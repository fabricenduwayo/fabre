#include <cstdlib>
#include <exception>
#include <fstream>
#include <string>
#include <vector>

#include "httplib.h"
#include <nlohmann/json.hpp>

#include "audit.hpp"
#include "model.hpp"
#include "parse.hpp"

using nlohmann::json;

namespace {

std::string ledger_path() {
    const char* p = std::getenv("AUDITOR_LEDGER");
    return p ? std::string(p) : std::string("/app/cpp-auditor/state/ledger.json");
}

// Append each emitted patch to the persistent audit ledger. The on-disk file may
// still be in the legacy schema 1 layout (entries under the "audits" key); it is
// migrated in place to schema 2 ("entries") while preserving existing records.
void record_audit(const std::vector<json>& patches) {
    const std::string path = ledger_path();

    json ledger = json::object();
    {
        std::ifstream in(path);
        if (in) {
            try {
                in >> ledger;
            } catch (const std::exception&) {
                ledger = json::object();
            }
        }
    }
    if (!ledger.is_object()) ledger = json::object();

    int schema = ledger.value("schema", 0);
    json entries = json::array();
    if (schema < 2) {
        // Legacy schema: records were stored under "audits". Carry them forward.
        if (ledger.contains("audits") && ledger["audits"].is_array()) {
            entries = ledger["audits"];
        } else if (ledger.contains("entries") && ledger["entries"].is_array()) {
            entries = ledger["entries"];
        }
    } else if (ledger.contains("entries") && ledger["entries"].is_array()) {
        entries = ledger["entries"];
    }

    for (const auto& patch : patches) {
        entries.push_back(patch);
    }

    json out_ledger = json::object();
    out_ledger["schema"] = 2;
    out_ledger["entries"] = entries;

    std::ofstream out(path);
    out << out_ledger.dump();
}

}  // namespace

int main() {
    const char* port_env = std::getenv("AUDITOR_PORT");
    int port = port_env ? std::atoi(port_env) : 8080;

    httplib::Server server;

    server.Get("/health", [](const httplib::Request&, httplib::Response& res) {
        res.set_content("{\"status\":\"ok\"}", "application/json");
    });

    // Each audit depends only on the snapshot in its own request; the service
    // keeps no per-account state between requests.
    server.Post("/v1/setup/audit", [](const httplib::Request& req, httplib::Response& res) {
        json out;
        try {
            json body = json::parse(req.body);
            Normalized inv = parse_snapshot(body);
            std::vector<json> patches = run_audit(inv);
            record_audit(patches);
            out["patches"] = patches;
        } catch (const std::exception& e) {
            res.status = 400;
            out["error"] = e.what();
        }
        res.set_content(out.dump(), "application/json");
    });

    server.listen("127.0.0.1", port);
    return 0;
}
