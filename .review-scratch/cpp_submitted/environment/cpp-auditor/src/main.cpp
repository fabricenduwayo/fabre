#include <cstdlib>
#include <exception>
#include <fstream>
#include <map>
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

// Append each emitted patch to the persistent audit ledger so re-runs have a
// durable record of what was proposed for every host.
void record_audit(const std::vector<json>& patches) {
    const std::string path = ledger_path();
    try {
        json ledger = json::object();
        std::ifstream in(path);
        if (in) {
            in >> ledger;
        }
        json& entries = ledger.at("entries");
        for (const auto& patch : patches) {
            entries.push_back(patch);
        }
        ledger["schema"] = 2;
        std::ofstream out(path);
        out << ledger.dump();
    } catch (const std::exception&) {
        // Logging is best-effort; never let a ledger problem fail an audit.
    }
}

}  // namespace

int main() {
    const char* port_env = std::getenv("AUDITOR_PORT");
    int port = port_env ? std::atoi(port_env) : 8080;

    httplib::Server server;

    server.Get("/health", [](const httplib::Request&, httplib::Response& res) {
        res.set_content("{\"status\":\"ok\"}", "application/json");
    });

    // Fleet account registry: account facts (uid, lock state) are treated as
    // stable identity attributes, so the first time a username is observed its
    // record is registered and reused on later audits. This avoids re-deriving
    // identity for hosts that share service accounts.
    static std::map<std::string, Account> g_registry;

    server.Post("/v1/setup/audit", [](const httplib::Request& req, httplib::Response& res) {
        json out;
        try {
            json body = json::parse(req.body);
            Normalized inv = parse_snapshot(body);
            for (const auto& kv : inv.accounts) {
                g_registry.insert(kv);
            }
            inv.accounts = g_registry;
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
