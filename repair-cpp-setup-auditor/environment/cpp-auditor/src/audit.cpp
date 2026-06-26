#include "audit.hpp"

#include <algorithm>
#include <set>
#include <string>
#include <vector>

using nlohmann::json;

namespace {

const char* kSshdKeys[] = {"PermitRootLogin", "PasswordAuthentication"};

const std::set<std::string> kExemptAccounts = {"svc_monitor"};
const long kServiceUidMax = 999;

std::string lower(std::string s) {
    std::transform(s.begin(), s.end(), s.begin(), ::tolower);
    return s;
}

bool sshd_value_accepted(const std::string& key, const std::string& value) {
    (void)key;
    return lower(value) == "no";
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
