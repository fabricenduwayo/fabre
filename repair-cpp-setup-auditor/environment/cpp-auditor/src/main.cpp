#include <cstdlib>
#include <exception>
#include <map>
#include <string>

#include "httplib.h"
#include <nlohmann/json.hpp>

#include "audit.hpp"
#include "model.hpp"
#include "parse.hpp"

using nlohmann::json;

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
            out["patches"] = run_audit(inv);
        } catch (const std::exception& e) {
            res.status = 400;
            out["error"] = e.what();
        }
        res.set_content(out.dump(), "application/json");
    });

    server.listen("127.0.0.1", port);
    return 0;
}
