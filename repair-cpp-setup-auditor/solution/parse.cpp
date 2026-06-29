#include "parse.hpp"

#include <algorithm>
#include <cctype>
#include <functional>
#include <map>
#include <set>
#include <string>
#include <utility>
#include <vector>

using nlohmann::json;

namespace {

// AC-ACCT-SHELL base set extended by amendment G-2026-01.
const char* kNologin[] = {
    "/usr/sbin/nologin", "/sbin/nologin", "/bin/false", "/usr/bin/false",
    "/usr/bin/git-shell", "/bin/sync"};

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

struct ShadowEntry {
    std::string password;
    std::string expire;  // 8th field: account-expiry day (days since epoch)
};

std::map<std::string, ShadowEntry> parse_shadow(const std::string& text) {
    std::map<std::string, ShadowEntry> out;
    for (const auto& line : splitlines(text)) {
        if (trim(line).empty()) continue;
        auto parts = split(line, ':');
        ShadowEntry e;
        e.password = parts.size() > 1 ? parts[1] : "";
        e.expire = parts.size() > 7 ? parts[7] : "";
        out[parts[0]] = e;
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

// AC-ACCT-LOCK as amended by G-2026-01 (adds "*LK*") and G-2026-16 (account
// expiry: disabled when the shadow expire field is < the reference day).
const long kRefDay = 20620;

bool is_disabled(const std::string& name,
                 const std::map<std::string, RawAccount>& accounts,
                 const std::map<std::string, ShadowEntry>& shadow) {
    auto sit = shadow.find(name);
    if (sit != shadow.end()) {
        const std::string& h = sit->second.password;
        if (h.empty() || h == "!" || h == "*" || h == "!!" || h == "*LK*" ||
            h[0] == '!') {
            return true;
        }
        const std::string& exp = sit->second.expire;
        if (!exp.empty()) {
            try {
                long e = std::stol(exp);
                if (e >= 0 && e < kRefDay) return true;
            } catch (const std::exception&) {
            }
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

// AC-GROUP-EFFECTIVE: listed members plus primary-gid members.
std::set<std::string> effective_group_members(
    const std::string& gname,
    const std::map<std::string, RawGroup>& groups,
    const std::map<std::string, RawAccount>& accounts) {
    std::set<std::string> members;
    auto it = groups.find(gname);
    if (it == groups.end()) return members;
    for (const auto& m : it->second.members) members.insert(m);
    for (const auto& kv : accounts) {
        if (kv.second.gid == it->second.gid) members.insert(kv.first);
    }
    return members;
}

// AC-SUDO-NOPASSWD as amended by G-2026-02 and G-2026-19: only an ALL command
// set with an effective NOPASSWD tag counts. Sudo command tags are sticky across
// comma-separated command entries until another tag appears.
bool grants_all_nopasswd(const std::string& rest) {
    std::string commands = rest;
    size_t eq = commands.find('=');
    if (eq != std::string::npos) commands = commands.substr(eq + 1);
    commands = trim(commands);
    if (!commands.empty() && commands[0] == '(') {
        size_t rp = commands.find(')');
        if (rp != std::string::npos) commands = trim(commands.substr(rp + 1));
    }

    std::string tag;
    for (const auto& raw : split(commands, ',')) {
        std::string segment = trim(raw);
        while (true) {
            std::string upper = segment;
            std::transform(upper.begin(), upper.end(), upper.begin(), ::toupper);
            if (starts_with(upper, "NOPASSWD")) {
                std::string after = trim(segment.substr(8));
                if (!after.empty() && after[0] == ':') {
                    tag = "NOPASSWD";
                    segment = trim(after.substr(1));
                    continue;
                }
            }
            if (starts_with(upper, "PASSWD")) {
                std::string after = trim(segment.substr(6));
                if (!after.empty() && after[0] == ':') {
                    tag = "PASSWD";
                    segment = trim(after.substr(1));
                    continue;
                }
            }
            break;
        }
        auto words = ws_split(segment);
        if (!words.empty() && words[0] == "ALL" && tag == "NOPASSWD") {
            return true;
        }
    }
    return false;
}

// AC-SUDO-NOPASSWD as amended by G-2026-15: a NOPASSWD: ALL grant only counts
// when the rule permits running as root. The runas spec is the first
// parenthesized list after `=`; the user list is the part before any `:`. With
// no parentheses the rule defaults to root.
bool runas_permits_root(const std::string& rest) {
    size_t lp = rest.find('(');
    if (lp == std::string::npos) return true;
    size_t rp = rest.find(')', lp);
    std::string inside = rp == std::string::npos ? rest.substr(lp + 1)
                                                 : rest.substr(lp + 1, rp - lp - 1);
    size_t colon = inside.find(':');
    std::string users = colon == std::string::npos ? inside : inside.substr(0, colon);
    for (const auto& tok : split(users, ',')) {
        std::string t = trim(tok);
        if (t == "root" || t == "ALL") return true;
    }
    return false;
}

// AC-SUDO-NOPASSWD as amended by G-2026-18: a spec applies to this host only when
// its host field resolves to include the audit host (or ALL).
const char* kAuditHost = "gw-lab-01";

bool host_applies(const std::string& host_str,
                  const std::map<std::string, std::vector<std::string>>& host_aliases) {
    std::function<bool(const std::string&, std::set<std::string>)> matches =
        [&](const std::string& name, std::set<std::string> seen) -> bool {
        if (name == "ALL" || name == kAuditHost) return true;
        auto it = host_aliases.find(name);
        if (it != host_aliases.end() && !seen.count(name)) {
            seen.insert(name);
            bool pos = false, neg = false;
            for (const auto& m0 : it->second) {
                std::string m = trim(m0);
                bool ng = !m.empty() && m[0] == '!';
                bool hit = matches(ng ? m.substr(1) : m, seen);
                if (ng && hit) {
                    neg = true;
                } else if (!ng && hit) {
                    pos = true;
                }
            }
            return pos && !neg;
        }
        return false;
    };
    bool positive = false;
    for (const auto& tok0 : split(host_str, ',')) {
        std::string tok = trim(tok0);
        if (tok.empty()) continue;
        bool ng = tok[0] == '!';
        bool hit = matches(ng ? tok.substr(1) : tok, {});
        if (ng && hit) return false;
        if (!ng && hit) positive = true;
    }
    return positive;
}

struct SudoSpec {
    std::string principal;
    std::string rest;
    std::string host;
};

std::set<std::string> parse_sudoers(const std::string& text,
                                    const std::map<std::string, RawGroup>& groups,
                                    const std::map<std::string, RawAccount>& accounts,
                                    const json& sudoers_d) {
    std::map<std::string, std::vector<std::string>> aliases;
    std::map<std::string, std::vector<std::string>> host_aliases;
    std::vector<SudoSpec> specs;

    // G-2026-09: `@includedir`/`#includedir` splices /etc/sudoers.d files (sorted
    // by name) inline at the directive position so they share last-match ordering.
    std::vector<std::string> merged;
    for (const auto& line : join_continuations(text)) {
        std::string ls = lower(trim(line));
        if (starts_with(ls, "@includedir") || starts_with(ls, "#includedir")) {
            std::vector<std::string> dnames;
            for (auto it = sudoers_d.begin(); it != sudoers_d.end(); ++it) {
                dnames.push_back(it.key());
            }
            std::sort(dnames.begin(), dnames.end());
            for (const auto& dn : dnames) {
                for (const auto& dl :
                     join_continuations(sudoers_d.at(dn).get<std::string>())) {
                    merged.push_back(dl);
                }
            }
            continue;
        }
        merged.push_back(line);
    }

    for (const auto& line : merged) {
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
        if (starts_with(s, "Host_Alias ")) {
            std::string body = s.substr(std::string("Host_Alias ").size());
            auto eq = body.find('=');
            if (eq == std::string::npos) continue;
            std::string name = trim(body.substr(0, eq));
            std::vector<std::string> members;
            for (auto& m : split(body.substr(eq + 1), ',')) {
                std::string t = trim(m);
                if (!t.empty()) members.push_back(t);
            }
            host_aliases[name] = members;
            continue;
        }
        // G-2026-05: `Defaults:<binder> !authenticate` grants passwordless sudo
        // (NOPASSWD: ALL) to the bound user/group, overriding the body rule that
        // ignores Defaults lines. Defaults overrides are not host-scoped.
        if (starts_with(s, "Defaults:")) {
            std::string tail = trim(s.substr(std::string("Defaults:").size()));
            auto tparts = ws_split(tail);
            if (!tparts.empty()) {
                std::string binder = tparts[0];
                std::string flags =
                    tail.size() > binder.size() ? tail.substr(binder.size()) : "";
                bool noauth = false;
                std::string cur;
                for (char c : flags + " ") {
                    if (c == ' ' || c == '\t' || c == ',') {
                        if (cur == "!authenticate") noauth = true;
                        cur.clear();
                    } else {
                        cur.push_back(c);
                    }
                }
                if (noauth) specs.push_back({binder, "NOPASSWD: ALL", "ALL"});
            }
            continue;
        }
        auto toks = ws_split(s);
        std::string first = toks.empty() ? "" : toks[0];
        if (first == "Runas_Alias" || first == "Cmnd_Alias" ||
            first == "Defaults" || starts_with(s, "Defaults")) {
            continue;
        }
        std::string principal = toks[0];
        std::string rest = s.size() > principal.size()
                               ? s.substr(s.find(principal) + principal.size())
                               : "";
        // The host field is everything between the principal and the first `=`.
        auto eqp = rest.find('=');
        std::string host_field = eqp == std::string::npos ? rest : rest.substr(0, eqp);
        specs.push_back({principal, rest, host_field});
    }

    std::function<void(const std::string&, std::set<std::string>,
                       std::set<std::string>&, std::set<std::string>&)>
        expand_token;
    std::function<std::set<std::string>(const std::string&, std::set<std::string>)>
        expand_alias;

    expand_token = [&](const std::string& token, std::set<std::string> seen,
                       std::set<std::string>& pos, std::set<std::string>& neg) {
        bool is_neg = !token.empty() && token[0] == '!';
        std::string name = is_neg ? token.substr(1) : token;
        std::set<std::string> base;
        if (name == "ALL") {
            base = {};
        } else if (!name.empty() && name[0] == '%') {
            base = effective_group_members(name.substr(1), groups, accounts);
        } else if (aliases.count(name)) {
            base = expand_alias(name, seen);
        } else {
            base = {name};
        }
        if (is_neg) {
            neg.insert(base.begin(), base.end());
        } else {
            pos.insert(base.begin(), base.end());
        }
    };

    expand_alias = [&](const std::string& name,
                       std::set<std::string> seen) -> std::set<std::string> {
        if (seen.count(name)) return {};
        seen.insert(name);
        std::set<std::string> pos, neg;
        for (const auto& m : aliases[name]) {
            expand_token(m, seen, pos, neg);
        }
        std::set<std::string> result;
        for (const auto& u : pos) {
            if (!neg.count(u)) result.insert(u);
        }
        return result;
    };

    // G-2026-07: last-match-wins. The LAST spec naming a principal sets its
    // passwordless state (a later non-NOPASSWD:ALL grant revokes an earlier one).
    std::map<std::string, bool> state;
    for (const auto& spec : specs) {
        // G-2026-18: a spec scoped to other hosts does not apply here.
        if (!host_applies(spec.host, host_aliases)) continue;
        bool grants = grants_all_nopasswd(spec.rest) && runas_permits_root(spec.rest);
        std::set<std::string> pos, neg;
        expand_token(spec.principal, {}, pos, neg);
        for (const auto& u : pos) state[u] = grants;
    }
    std::set<std::string> passwordless;
    for (const auto& kv : state) {
        if (kv.second) passwordless.insert(kv.first);
    }
    return passwordless;
}

bool active_authorized_key_line(const std::string& line) {
    std::string s = trim(line);
    if (s.empty() || s[0] == '#' || s[0] == '@') return false;
    auto fields = ws_split(s);
    if (fields.empty()) return false;
    auto key_type = [](const std::string& v) {
        return starts_with(v, "ssh-") || starts_with(v, "ecdsa-") ||
               starts_with(v, "sk-ssh-") || starts_with(v, "sk-ecdsa-") ||
               starts_with(v, "rsa-sha2-");
    };
    if (key_type(fields[0])) return true;
    return fields.size() > 1 && key_type(fields[1]);
}

std::set<std::string> parse_keys(const json& auth_map) {
    std::set<std::string> out;
    for (auto it = auth_map.begin(); it != auth_map.end(); ++it) {
        for (const auto& line : splitlines(it.value().get<std::string>())) {
            if (active_authorized_key_line(line)) {
                out.insert(it.key());
                break;
            }
        }
    }
    return out;
}

// HD-SSHD context (G-2026-17): drop-ins are evaluated for a fixed audit
// connection — connecting user `root` from source address 198.51.100.10.
const char* kAuditUser = "root";
const char* kAuditAddr = "198.51.100.10";

long long ip_to_int(const std::string& s) {
    auto parts = split(s, '.');
    if (parts.size() != 4) return -1;
    long long v = 0;
    for (const auto& p : parts) {
        if (p.empty()) return -1;
        for (char c : p) {
            if (!std::isdigit(static_cast<unsigned char>(c))) return -1;
        }
        long n = std::stol(p);
        if (n < 0 || n > 255) return -1;
        v = (v << 8) | n;
    }
    return v;
}

// One Address criterion token: exact IPv4 or IPv4 CIDR range.
bool addr_matches_token(const std::string& token, const std::string& addr) {
    auto slash = token.find('/');
    if (slash != std::string::npos) {
        long long ni = ip_to_int(token.substr(0, slash));
        long long ai = ip_to_int(addr);
        std::string bits = token.substr(slash + 1);
        if (ni < 0 || ai < 0 || bits.empty()) return false;
        for (char c : bits) {
            if (!std::isdigit(static_cast<unsigned char>(c))) return false;
        }
        int prefix = std::stoi(bits);
        if (prefix < 0 || prefix > 32) return false;
        if (prefix == 0) return true;
        unsigned long mask = (0xFFFFFFFFUL << (32 - prefix)) & 0xFFFFFFFFUL;
        return (static_cast<unsigned long>(ni) & mask) ==
               (static_cast<unsigned long>(ai) & mask);
    }
    return token == addr;
}

// User criterion: comma list of patterns with `*` wildcard and `!` negation.
bool user_matches(const std::string& list, const std::string& user) {
    bool positive = false;
    for (const auto& raw : split(list, ',')) {
        std::string tok = trim(raw);
        if (tok.empty()) continue;
        bool neg = tok[0] == '!';
        std::string pat = neg ? tok.substr(1) : tok;
        bool hit = (pat == "*" || pat == user);
        if (neg && hit) return false;
        if (!neg && hit) positive = true;
    }
    return positive;
}

// A Match block applies iff every criterion matches the audit context.
bool match_block_active(const std::vector<std::string>& crit,
                        const std::set<std::string>& root_groups) {
    if (crit.size() == 1 && lower(crit[0]) == "all") return true;
    if (crit.empty()) return false;
    size_t i = 0;
    while (i < crit.size()) {
        std::string ctype = lower(crit[i]);
        if (i + 1 >= crit.size()) return false;
        std::string cval = crit[i + 1];
        i += 2;
        if (ctype == "user") {
            if (!user_matches(cval, kAuditUser)) return false;
        } else if (ctype == "group") {
            bool any = false;
            for (const auto& g : split(cval, ',')) {
                if (root_groups.count(trim(g))) { any = true; break; }
            }
            if (!any) return false;
        } else if (ctype == "address") {
            bool any = false;
            for (const auto& t : split(cval, ',')) {
                if (addr_matches_token(trim(t), kAuditAddr)) { any = true; break; }
            }
            if (!any) return false;
        } else {
            return false;  // unsupported criterion: block never applies
        }
    }
    return true;
}

// HD-SSHD-DROPIN as amended by G-2026-17: evaluate Match blocks against the
// audit context; global plus applicable-block lines, first occurrence wins.
std::map<std::string, std::string> parse_sshd(
    const json& dropins,
    const std::map<std::string, RawGroup>& groups,
    const std::map<std::string, RawAccount>& accounts) {
    std::set<std::string> root_groups;
    for (const auto& kv : groups) {
        auto m = effective_group_members(kv.first, groups, accounts);
        if (m.count(kAuditUser)) root_groups.insert(kv.first);
    }

    std::vector<std::string> names;
    for (auto it = dropins.begin(); it != dropins.end(); ++it) names.push_back(it.key());
    std::sort(names.begin(), names.end());

    std::map<std::string, std::string> effective;
    bool active = true;  // global scope is always active
    for (const auto& name : names) {
        for (const auto& line : splitlines(dropins.at(name).get<std::string>())) {
            std::string s = trim(line);
            if (s.empty() || s[0] == '#') continue;
            auto toks = ws_split(s);
            if (toks.empty()) continue;
            if (lower(toks[0]) == "match") {
                std::vector<std::string> crit(toks.begin() + 1, toks.end());
                active = match_block_active(crit, root_groups);
                continue;
            }
            if (!active) continue;
            if (toks.size() >= 2) {
                std::string key = lower(toks[0]);
                // G-2026-06: ChallengeResponseAuthentication is the deprecated
                // spelling of KbdInteractiveAuthentication; fold them together.
                if (key == "challengeresponseauthentication") {
                    key = "kbdinteractiveauthentication";
                }
                if (!effective.count(key)) effective[key] = toks[1];
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

    inv.nopasswd_users = parse_sudoers(get_str(files, "sudoers"), groups, raw_accounts,
                                       get_obj(files, "sudoers.d"));
    inv.users_with_keys = parse_keys(get_obj(files, "authorized_keys"));
    inv.sshd = parse_sshd(get_obj(files, "sshd_config.d"), groups, raw_accounts);

    return inv;
}
