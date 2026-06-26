#include "parse.hpp"

#include <algorithm>
#include <functional>
#include <map>
#include <set>
#include <string>
#include <utility>
#include <vector>

using nlohmann::json;

namespace {

const char* kNologin[] = {
    "/usr/sbin/nologin", "/sbin/nologin", "/bin/false", "/usr/bin/false"};

struct RawAccount {
    long uid = 0;
    long gid = 0;
    std::string shell;
};

struct RawGroup {
    long gid = 0;
    std::vector<std::string> members;
};

std::vector<std::string> splitlines(const std::string& text) {
    std::vector<std::string> out;
    std::string cur;
    for (char c : text) {
        if (c == '\n') {
            out.push_back(cur);
            cur.clear();
        } else if (c != '\r') {
            cur.push_back(c);
        }
    }
    out.push_back(cur);
    return out;
}

std::string trim(const std::string& s) {
    size_t a = s.find_first_not_of(" \t");
    if (a == std::string::npos) return "";
    size_t b = s.find_last_not_of(" \t");
    return s.substr(a, b - a + 1);
}

std::vector<std::string> split(const std::string& s, char delim) {
    std::vector<std::string> out;
    std::string cur;
    for (char c : s) {
        if (c == delim) {
            out.push_back(cur);
            cur.clear();
        } else {
            cur.push_back(c);
        }
    }
    out.push_back(cur);
    return out;
}

std::vector<std::string> ws_split(const std::string& s) {
    std::vector<std::string> out;
    std::string cur;
    for (char c : s) {
        if (c == ' ' || c == '\t') {
            if (!cur.empty()) {
                out.push_back(cur);
                cur.clear();
            }
        } else {
            cur.push_back(c);
        }
    }
    if (!cur.empty()) out.push_back(cur);
    return out;
}

std::string lower(std::string s) {
    std::transform(s.begin(), s.end(), s.begin(), ::tolower);
    return s;
}

bool starts_with(const std::string& s, const std::string& p) {
    return s.size() >= p.size() && s.compare(0, p.size(), p) == 0;
}

std::vector<std::string> join_continuations(const std::string& text) {
    std::vector<std::string> out;
    std::string pending;
    for (const auto& raw : splitlines(text)) {
        if (!raw.empty() && raw.back() == '\\') {
            pending += raw.substr(0, raw.size() - 1) + " ";
        } else {
            out.push_back(pending + raw);
            pending.clear();
        }
    }
    if (!pending.empty()) out.push_back(pending);
    return out;
}

std::map<std::string, RawAccount> parse_passwd(const std::string& text) {
    std::map<std::string, RawAccount> accounts;
    for (const auto& line : splitlines(text)) {
        if (trim(line).empty()) continue;
        auto parts = split(line, ':');
        if (parts.size() < 7) continue;
        try {
            RawAccount acc;
            acc.uid = std::stol(parts[2]);
            acc.gid = std::stol(parts[3]);
            acc.shell = parts[6];
            accounts[parts[0]] = acc;
        } catch (const std::exception&) {
            continue;
        }
    }
    return accounts;
}

std::map<std::string, std::string> parse_shadow(const std::string& text) {
    std::map<std::string, std::string> out;
    for (const auto& line : splitlines(text)) {
        if (trim(line).empty()) continue;
        auto parts = split(line, ':');
        out[parts[0]] = parts.size() > 1 ? parts[1] : "";
    }
    return out;
}

std::map<std::string, RawGroup> parse_group(const std::string& text) {
    std::map<std::string, RawGroup> out;
    for (const auto& line : splitlines(text)) {
        if (trim(line).empty()) continue;
        auto parts = split(line, ':');
        if (parts.size() < 3) continue;
        try {
            RawGroup g;
            g.gid = std::stol(parts[2]);
            if (parts.size() > 3) {
                for (const auto& m : split(parts[3], ',')) {
                    if (!m.empty()) g.members.push_back(m);
                }
            }
            out[parts[0]] = g;
        } catch (const std::exception&) {
            continue;
        }
    }
    return out;
}

bool is_disabled(const std::string& name,
                 const std::map<std::string, RawAccount>& accounts,
                 const std::map<std::string, std::string>& shadow) {
    auto sit = shadow.find(name);
    if (sit != shadow.end()) {
        const std::string& h = sit->second;
        if (h.empty() || h == "!" || h == "*" || h == "!!" || h[0] == '!') {
            return true;
        }
    }
    auto ait = accounts.find(name);
    if (ait != accounts.end()) {
        for (const char* sh : kNologin) {
            if (ait->second.shell == sh) return true;
        }
    }
    return false;
}

std::set<std::string> effective_group_members(
    const std::string& gname,
    const std::map<std::string, RawGroup>& groups,
    const std::map<std::string, RawAccount>& accounts) {
    std::set<std::string> members;
    auto it = groups.find(gname);
    if (it == groups.end()) return members;
    for (const auto& m : it->second.members) members.insert(m);
    return members;
}

bool has_nopasswd(const std::string& rest) {
    return rest.find("NOPASSWD") != std::string::npos;
}

std::set<std::string> parse_sudoers(const std::string& text,
                                    const std::map<std::string, RawGroup>& groups,
                                    const std::map<std::string, RawAccount>& accounts) {
    std::map<std::string, std::vector<std::string>> aliases;
    std::vector<std::pair<std::string, std::string>> specs;

    for (const auto& line : join_continuations(text)) {
        std::string s = trim(line);
        if (s.empty() || s[0] == '#') continue;
        if (starts_with(s, "User_Alias ")) {
            std::string body = s.substr(std::string("User_Alias ").size());
            auto eq = body.find('=');
            if (eq == std::string::npos) continue;
            std::string name = trim(body.substr(0, eq));
            std::vector<std::string> members;
            for (auto& m : split(body.substr(eq + 1), ',')) {
                std::string t = trim(m);
                if (!t.empty()) members.push_back(t);
            }
            aliases[name] = members;
            continue;
        }
        auto toks = ws_split(s);
        std::string first = toks.empty() ? "" : toks[0];
        if (first == "Host_Alias" || first == "Runas_Alias" ||
            first == "Cmnd_Alias" || first == "Defaults" ||
            starts_with(s, "Defaults")) {
            continue;
        }
        std::string principal = toks[0];
        std::string rest = s.size() > principal.size()
                               ? s.substr(s.find(principal) + principal.size())
                               : "";
        specs.push_back({principal, rest});
    }

    std::function<std::set<std::string>(const std::string&, std::set<std::string>)>
        expand_alias;

    auto expand_token = [&](const std::string& token,
                            std::set<std::string> seen) -> std::set<std::string> {
        std::string name = token;
        if (!name.empty() && name[0] == '!') name = name.substr(1);
        if (name == "ALL") return {};
        if (!name.empty() && name[0] == '%') {
            return effective_group_members(name.substr(1), groups, accounts);
        }
        if (aliases.count(name)) {
            return expand_alias(name, seen);
        }
        return {name};
    };

    expand_alias = [&](const std::string& name,
                       std::set<std::string> seen) -> std::set<std::string> {
        if (seen.count(name)) return {};
        seen.insert(name);
        std::set<std::string> result;
        for (const auto& m : aliases[name]) {
            auto base = expand_token(m, seen);
            result.insert(base.begin(), base.end());
        }
        return result;
    };

    std::set<std::string> passwordless;
    for (const auto& spec : specs) {
        if (!has_nopasswd(spec.second)) continue;
        auto base = expand_token(spec.first, {});
        passwordless.insert(base.begin(), base.end());
    }
    return passwordless;
}

std::set<std::string> parse_keys(const json& auth_map) {
    std::set<std::string> out;
    for (auto it = auth_map.begin(); it != auth_map.end(); ++it) {
        for (const auto& line : splitlines(it.value().get<std::string>())) {
            std::string s = trim(line);
            if (!s.empty() && s[0] != '#') {
                out.insert(it.key());
                break;
            }
        }
    }
    return out;
}

std::map<std::string, std::string> parse_sshd(const json& dropins) {
    std::vector<std::string> names;
    for (auto it = dropins.begin(); it != dropins.end(); ++it) names.push_back(it.key());
    std::sort(names.begin(), names.end());

    std::map<std::string, std::string> effective;
    for (const auto& name : names) {
        for (const auto& line : splitlines(dropins.at(name).get<std::string>())) {
            std::string s = trim(line);
            if (s.empty() || s[0] == '#') continue;
            auto toks = ws_split(s);
            if (toks.empty()) continue;
            if (toks.size() >= 2) {
                effective[lower(toks[0])] = toks[1];
            }
        }
    }
    return effective;
}

std::string get_str(const json& files, const char* key) {
    if (files.contains(key) && files.at(key).is_string()) {
        return files.at(key).get<std::string>();
    }
    return "";
}

json get_obj(const json& files, const char* key) {
    if (files.contains(key) && files.at(key).is_object()) {
        return files.at(key);
    }
    return json::object();
}

}  // namespace

Normalized parse_snapshot(const json& body) {
    Normalized inv;
    json files = body.contains("files") ? body.at("files") : json::object();

    auto raw_accounts = parse_passwd(get_str(files, "passwd"));
    auto shadow = parse_shadow(get_str(files, "shadow"));
    auto groups = parse_group(get_str(files, "group"));

    for (const auto& kv : raw_accounts) {
        Account acc;
        acc.uid = kv.second.uid;
        acc.disabled = is_disabled(kv.first, raw_accounts, shadow);
        inv.accounts[kv.first] = acc;
    }

    inv.nopasswd_users = parse_sudoers(get_str(files, "sudoers"), groups, raw_accounts);
    inv.users_with_keys = parse_keys(get_obj(files, "authorized_keys"));
    inv.sshd = parse_sshd(get_obj(files, "sshd_config.d"));

    return inv;
}
