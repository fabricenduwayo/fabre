#include <cstdlib>
#include <exception>
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

    // Each audit must depend only on the snapshot in its own request; the
    // service keeps no cross-request state.
    server.Post("/v1/setup/audit", [](const httplib::Request& req, httplib::Response& res) {
        json out;
        try {
            json body = json::parse(req.body);
            Normalized inv = parse_snapshot(body);
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
