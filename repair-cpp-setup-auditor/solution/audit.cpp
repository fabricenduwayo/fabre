#include "audit.hpp"

#include <algorithm>
#include <set>
#include <string>
#include <vector>

using nlohmann::json;

namespace {

const char* kSshdKeys[] = {"PermitRootLogin", "PasswordAuthentication",
                           "KbdInteractiveAuthentication"};

// AC-EXEMPT as amended by G-2026-03.
const std::set<std::string> kExemptAccounts = {"svc_monitor", "svc_backup"};
const long kServiceUidMax = 499;

std::string lower(std::string s) {
    std::transform(s.begin(), s.end(), s.begin(), ::tolower);
    return s;
}

// HD-SSHD-DROPIN as amended by G-2026-04: prohibit-password is accepted for
// PermitRootLogin only.
bool sshd_value_accepted(const std::string& key, const std::string& value) {
    std::string v = lower(value);
    if (v == "no") return true;
    // G-2026-10: `without-password` is the deprecated spelling of
    // `prohibit-password`; both are accepted for PermitRootLogin only.
    if (std::string(key) == "PermitRootLogin" &&
        (v == "prohibit-password" || v == "without-password")) {
        return true;
    }
    return false;
}

}  // namespace

std::vector<json> run_audit(const Normalized& inv) {
    std::vector<json> patches;

    auto disabled = [&](const std::string& user) {
        auto it = inv.accounts.find(user);
        return it != inv.accounts.end() && it->second.disabled;
    };
    auto exempt = [&](const std::string& user) {
        if (kExemptAccounts.count(user)) {
            return true;
        }
        auto it = inv.accounts.find(user);
        return it != inv.accounts.end() && it->second.uid <= kServiceUidMax;
    };

    for (const auto& user : inv.nopasswd_users) {
        if (!disabled(user) && !exempt(user)) {
            patches.push_back({{"action", "sudoers.require_password"}, {"target", user}});
        }
    }

    for (const auto& user : inv.users_with_keys) {
        if (disabled(user)) {
            patches.push_back({{"action", "ssh.revoke_keys"}, {"target", user}});
        }
    }

    for (const char* key : kSshdKeys) {
        auto it = inv.sshd.find(lower(key));
        bool ok = it != inv.sshd.end() && sshd_value_accepted(key, it->second);
        if (!ok) {
            patches.push_back({{"action", "systemd.set_dropin"},
                               {"unit", "sshd"},
                               {"key", key},
                               {"value", "no"}});
        }
    }

    return patches;
}
