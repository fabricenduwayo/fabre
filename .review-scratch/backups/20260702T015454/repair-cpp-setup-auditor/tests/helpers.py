import json
import urllib.request

CPP_URL = "http://127.0.0.1:8080"

# Resolved policy: body of the Standard as amended by Appendix G.
EXEMPT_ACCOUNTS = {"svc_monitor", "svc_backup"}  # AC-EXEMPT + G-2026-03
SERVICE_UID_MAX = 499  # AC-EXEMPT ceiling lowered by G-2026-03

NOLOGIN_SHELLS = {  # AC-ACCT-SHELL base + G-2026-01
    "/usr/sbin/nologin",
    "/sbin/nologin",
    "/bin/false",
    "/usr/bin/false",
    "/usr/bin/git-shell",
    "/bin/sync",
}
LOCKED_TOKENS = {"", "!", "*", "!!", "*LK*"}  # AC-ACCT-LOCK + G-2026-01
REF_DAY = 20620  # AC-ACCT-LOCK + G-2026-16: account-expiry reference day
SSHD_KEYS = ("PermitRootLogin", "PasswordAuthentication", "KbdInteractiveAuthentication")
SSHD_ACCEPTED = {  # HD-SSHD-DROPIN + G-2026-04
    # G-2026-10: `without-password` is the deprecated spelling of
    # `prohibit-password` and is likewise accepted for PermitRootLogin.
    "PermitRootLogin": {"no", "prohibit-password", "without-password"},
    "PasswordAuthentication": {"no"},
    "KbdInteractiveAuthentication": {"no"},  # HD-SSHD-KBDINT + G-2026-06
}
# G-2026-06: ChallengeResponseAuthentication is the deprecated spelling of
# KbdInteractiveAuthentication; both names address the same effective setting.
SSHD_ALIASES = {"challengeresponseauthentication": "kbdinteractiveauthentication"}

# G-2026-17: the auditor evaluates drop-ins for a fixed audit connection context
# (connecting user `root` from source address 198.51.100.10) rather than ignoring
# Match blocks. Match blocks apply only when all their criteria match this context.
AUDIT_USER = "root"
AUDIT_ADDR = "198.51.100.10"

# G-2026-18: sudoers rules apply to this host only when their host field resolves
# to include the audit host (or ALL); rules scoped to other hosts are ignored.
AUDIT_HOST = "gw-lab-01"


# ---------------------------------------------------------------------------
# HTTP client
# ---------------------------------------------------------------------------
def _post(url, payload):
    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        url, data=data, headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode())


def cpp_audit(snapshot):
    return _post(CPP_URL + "/v1/setup/audit", snapshot)["patches"]


def canon(patches):
    return sorted(json.dumps(p, sort_keys=True) for p in patches)


# ---------------------------------------------------------------------------
# Reference implementation of the resolved Standard (hidden from the agent)
# ---------------------------------------------------------------------------
def _join_continuations(text):
    lines, pending = [], ""
    for raw in text.splitlines():
        if raw.endswith("\\"):
            pending += raw[:-1] + " "
        else:
            lines.append(pending + raw)
            pending = ""
    if pending:
        lines.append(pending)
    return lines


def parse_passwd(text):
    out = {}
    for line in text.splitlines():
        if not line.strip():
            continue
        parts = line.split(":")
        if len(parts) < 7:
            continue
        try:
            out[parts[0]] = {"uid": int(parts[2]), "gid": int(parts[3]), "shell": parts[6]}
        except ValueError:
            continue
    return out


def parse_shadow(text):
    out = {}
    for line in text.splitlines():
        if not line.strip():
            continue
        parts = line.split(":")
        out[parts[0]] = {
            "pw": parts[1] if len(parts) > 1 else "",
            "expire": parts[7] if len(parts) > 7 else "",
        }
    return out


def parse_group(text):
    out = {}
    for line in text.splitlines():
        if not line.strip():
            continue
        parts = line.split(":")
        if len(parts) < 3:
            continue
        try:
            gid = int(parts[2])
        except ValueError:
            continue
        members = [m for m in (parts[3].split(",") if len(parts) > 3 else []) if m]
        out[parts[0]] = {"gid": gid, "members": members}
    return out


def is_disabled(name, accounts, shadow):
    ent = shadow.get(name)
    if ent is not None:
        h = ent["pw"]
        if h in LOCKED_TOKENS or h.startswith("!"):
            return True
        exp = ent["expire"]
        if exp:
            try:
                if 0 <= int(exp) < REF_DAY:  # G-2026-16: account expired
                    return True
            except ValueError:
                pass
    return accounts.get(name, {}).get("shell", "") in NOLOGIN_SHELLS


def effective_group_members(gname, groups, accounts):
    grp = groups.get(gname)
    if not grp:
        return set()
    members = set(grp["members"])
    for user, info in accounts.items():
        if info["gid"] == grp["gid"]:
            members.add(user)
    return members


def _grants_all_nopasswd(rest):
    """True iff sudoers tags make the ALL command set passwordless.

    G-2026-19 resolves command tags the way sudo does: NOPASSWD/PASSWD tags are
    sticky across comma-separated command entries until another tag appears.
    """
    command_part = rest.split("=", 1)[1] if "=" in rest else rest
    command_part = command_part.strip()
    if command_part.startswith("("):
        rp = command_part.find(")")
        if rp >= 0:
            command_part = command_part[rp + 1:].strip()

    tag = None
    for raw in command_part.split(","):
        segment = raw.strip()
        while True:
            upper = segment.upper()
            if upper.startswith("NOPASSWD"):
                after = segment[len("NOPASSWD"):].lstrip()
                if after.startswith(":"):
                    tag = "NOPASSWD"
                    segment = after[1:].strip()
                    continue
            if upper.startswith("PASSWD"):
                after = segment[len("PASSWD"):].lstrip()
                if after.startswith(":"):
                    tag = "PASSWD"
                    segment = after[1:].strip()
                    continue
            break
        if segment.split(None, 1)[0:1] == ["ALL"] and tag == "NOPASSWD":
            return True
    return False


def _runas_permits_root(rest):
    """True iff the rule's runas user list permits root (G-2026-15).

    The runas spec is the first parenthesized list after `=`; the user list is
    the part before any `:`. With no parentheses the rule defaults to root.
    """
    lp = rest.find("(")
    if lp < 0:
        return True
    rp = rest.find(")", lp)
    inside = rest[lp + 1:] if rp < 0 else rest[lp + 1:rp]
    users = inside.split(":", 1)[0]
    return any(t.strip() in ("root", "ALL") for t in users.split(","))


def _host_applies(host_str, host_aliases):
    """A spec's host field applies iff it resolves to include AUDIT_HOST (G-2026-18).

    The field is a comma-separated list of `ALL`, hostnames, or Host_Alias names,
    each optionally negated with `!`. Host_Alias names resolve recursively.
    """

    def matches(name, seen):
        if name == "ALL" or name == AUDIT_HOST:
            return True
        if name in host_aliases and name not in seen:
            seen = seen | {name}
            pos = neg = False
            for m in host_aliases[name]:
                m = m.strip()
                ng = m.startswith("!")
                hit = matches(m[1:] if ng else m, seen)
                if ng and hit:
                    neg = True
                elif not ng and hit:
                    pos = True
            return pos and not neg
        return False

    positive = False
    for tok in host_str.split(","):
        tok = tok.strip()
        if not tok:
            continue
        ng = tok.startswith("!")
        hit = matches(tok[1:] if ng else tok, set())
        if ng and hit:
            return False
        if not ng and hit:
            positive = True
    return positive


def _expand_sudoers_lines(text, sudoers_d):
    """Splice `@includedir`/`#includedir` files (sorted by name) inline (G-2026-09)."""
    out = []
    for line in _join_continuations(text):
        low = line.strip().lower()
        if low.startswith("@includedir") or low.startswith("#includedir"):
            for fname in sorted(sudoers_d):
                out.extend(_join_continuations(sudoers_d[fname]))
            continue
        out.append(line)
    return out


def _parse_sudoers(text, groups, accounts, sudoers_d=None):
    aliases, host_aliases, specs = {}, {}, []
    for line in _expand_sudoers_lines(text, sudoers_d or {}):
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        if s.startswith("User_Alias "):
            body = s[len("User_Alias "):]
            if "=" not in body:
                continue
            name, rhs = body.split("=", 1)
            aliases[name.strip()] = [m.strip() for m in rhs.split(",") if m.strip()]
            continue
        if s.startswith("Host_Alias "):
            body = s[len("Host_Alias "):]
            if "=" not in body:
                continue
            name, rhs = body.split("=", 1)
            host_aliases[name.strip()] = [m.strip() for m in rhs.split(",") if m.strip()]
            continue
        # G-2026-05: a per-user/group `Defaults:<binder> !authenticate` line grants
        # passwordless sudo to that binder for the entire command set, overriding
        # the body rule that ignores Defaults lines. Defaults overrides are not
        # host-scoped, so they apply on every host (host field "ALL").
        if s.startswith("Defaults:"):
            tail = s[len("Defaults:"):].strip()
            parts = tail.split(None, 1)
            if parts:
                binder = parts[0]
                flags = parts[1] if len(parts) > 1 else ""
                flag_tokens = [t.strip() for t in flags.replace(",", " ").split()]
                if "!authenticate" in flag_tokens:
                    specs.append((binder, "NOPASSWD: ALL", "ALL"))
            continue
        head = s.split(None, 1)[0]
        if head in ("Runas_Alias", "Cmnd_Alias", "Defaults") or s.startswith("Defaults"):
            continue
        toks = s.split(None, 1)
        rest = toks[1] if len(toks) > 1 else ""
        # The host field is everything between the principal and the first `=`.
        host_field = rest.split("=", 1)[0]
        specs.append((toks[0], rest, host_field))

    def expand_token(token, seen):
        neg = token.startswith("!")
        name = token[1:] if neg else token
        if name == "ALL":
            base = set()
        elif name.startswith("%"):
            base = effective_group_members(name[1:], groups, accounts)
        elif name in aliases:
            base = expand_alias(name, seen)
        else:
            base = {name}
        return neg, base

    def expand_alias(name, seen):
        if name in seen:
            return set()
        seen = seen | {name}
        pos, neg = set(), set()
        for member in aliases[name]:
            is_neg, base = expand_token(member, seen)
            (neg if is_neg else pos).update(base)
        return pos - neg

    # G-2026-07: last-match-wins. Process specs (and Defaults overrides) in file
    # order; the LAST spec naming a principal sets its passwordless state.
    state = {}
    for principal, rest, host_field in specs:
        # G-2026-18: a spec scoped to other hosts does not apply here and so does
        # not participate in last-match for its principal.
        if not _host_applies(host_field, host_aliases):
            continue
        grants = _grants_all_nopasswd(rest) and _runas_permits_root(rest)
        is_neg, base = expand_token(principal, set())
        if is_neg:
            continue
        for u in base:
            state[u] = grants
    return {u for u, v in state.items() if v}


def _active_authorized_key_line(line):
    """Return whether a line contains a usable authorized_keys key record.

    G-2026-20: comments, blank lines, marker-style revoked lines, and options
    without a following key do not count as keys to revoke.
    """
    s = line.strip()
    if not s or s.startswith("#") or s.startswith("@"):
        return False
    fields = s.split()
    if not fields:
        return False
    key_types = ("ssh-", "ecdsa-", "sk-ssh-", "sk-ecdsa-", "rsa-sha2-")
    if fields[0].startswith(key_types):
        return True
    return len(fields) > 1 and fields[1].startswith(key_types)


def _parse_keys(auth_map):
    out = set()
    for user, text in auth_map.items():
        for line in text.splitlines():
            if _active_authorized_key_line(line):
                out.add(user)
                break
    return out


def _ip_to_int(s):
    parts = s.split(".")
    if len(parts) != 4:
        return None
    try:
        nums = [int(p) for p in parts]
    except ValueError:
        return None
    if any(n < 0 or n > 255 for n in nums):
        return None
    return (nums[0] << 24) | (nums[1] << 16) | (nums[2] << 8) | nums[3]


def _addr_matches_token(token, addr):
    """One Address criterion token: exact IPv4 or IPv4 CIDR (G-2026-17)."""
    if "/" in token:
        net, _, bits = token.partition("/")
        ni = _ip_to_int(net)
        ai = _ip_to_int(addr)
        try:
            prefix = int(bits)
        except ValueError:
            return False
        if ni is None or ai is None or not (0 <= prefix <= 32):
            return False
        if prefix == 0:
            return True
        mask = (0xFFFFFFFF << (32 - prefix)) & 0xFFFFFFFF
        return (ni & mask) == (ai & mask)
    return token == addr


def _user_matches(pattern_list, user):
    """User criterion: comma list of patterns with `*` wildcard and `!` negation."""
    positive = False
    for tok in pattern_list.split(","):
        tok = tok.strip()
        if not tok:
            continue
        neg = tok.startswith("!")
        pat = tok[1:] if neg else tok
        hit = pat == "*" or pat == user
        if neg and hit:
            return False
        if not neg and hit:
            positive = True
    return positive


def _match_block_active(crit_tokens, root_groups):
    """A Match block applies iff every criterion matches the audit context."""
    if len(crit_tokens) == 1 and crit_tokens[0].lower() == "all":
        return True
    i = 0
    if not crit_tokens:
        return False
    while i < len(crit_tokens):
        ctype = crit_tokens[i].lower()
        if i + 1 >= len(crit_tokens):
            return False
        cval = crit_tokens[i + 1]
        i += 2
        if ctype == "user":
            if not _user_matches(cval, AUDIT_USER):
                return False
        elif ctype == "group":
            if not any(g.strip() in root_groups for g in cval.split(",")):
                return False
        elif ctype == "address":
            if not any(_addr_matches_token(t.strip(), AUDIT_ADDR) for t in cval.split(",")):
                return False
        else:
            return False  # unsupported criterion: block never applies
    return True


def _parse_sshd(dropins, groups, accounts):
    # G-2026-17: a Match block scoped to Group matches when root is an effective
    # member of the named group (per AC-GROUP-EFFECTIVE).
    root_groups = {
        gname
        for gname in groups
        if AUDIT_USER in effective_group_members(gname, groups, accounts)
    }
    effective = {}
    active = True  # global scope is always active
    for fname in sorted(dropins):
        for line in dropins[fname].splitlines():
            s = line.strip()
            if not s or s.startswith("#"):
                continue
            toks = s.split()
            if toks[0].lower() == "match":
                active = _match_block_active(toks[1:], root_groups)
                continue
            if not active:
                continue
            if len(toks) >= 2:
                key = toks[0].lower()
                key = SSHD_ALIASES.get(key, key)
                if key not in effective:
                    effective[key] = toks[1]
    return effective


def normalize(snapshot):
    files = snapshot["files"]
    raw = parse_passwd(files.get("passwd", ""))
    shadow = parse_shadow(files.get("shadow", ""))
    groups = parse_group(files.get("group", ""))
    accounts = {
        name: {"uid": info["uid"], "disabled": is_disabled(name, raw, shadow)}
        for name, info in raw.items()
    }
    sshd_eff = _parse_sshd(files.get("sshd_config.d", {}), groups, raw)
    return {
        "accounts": accounts,
        "sudo_nopasswd_users": sorted(
            _parse_sudoers(files.get("sudoers", ""), groups, raw, files.get("sudoers.d", {}))
        ),
        "users_with_keys": sorted(_parse_keys(files.get("authorized_keys", {}))),
        "sshd": {k: sshd_eff.get(k.lower()) for k in SSHD_KEYS},
    }


def _exempt(user, accounts):
    if user in EXEMPT_ACCOUNTS:
        return True
    return user in accounts and accounts[user]["uid"] <= SERVICE_UID_MAX


def expected_patches(snapshot):
    inv = normalize(snapshot)
    accounts = inv["accounts"]
    patches = []
    for user in inv["sudo_nopasswd_users"]:
        disabled = accounts.get(user, {}).get("disabled", False)
        if not disabled and not _exempt(user, accounts):
            patches.append({"action": "sudoers.require_password", "target": user})
    for user in inv["users_with_keys"]:
        if accounts.get(user, {}).get("disabled", False):
            patches.append({"action": "ssh.revoke_keys", "target": user})
    for key in SSHD_KEYS:
        value = inv["sshd"][key]
        if value is None or value.lower() not in SSHD_ACCEPTED[key]:
            patches.append(
                {"action": "systemd.set_dropin", "unit": "sshd", "key": key, "value": "no"}
            )
    return patches


# ---------------------------------------------------------------------------
# Randomized snapshot generator (exercises every amended clause)
# ---------------------------------------------------------------------------
GID_WHEEL = 10
GID_DEV = 1002
GID_USERS = 100
VALID_HASH = "$6$rounds=5000$abcdefgh$" + "x" * 40
LOCK_CHOICES = ["!", "*", "!!", "*LK*", "!" + VALID_HASH]
NOLOGIN_CHOICES = ["/usr/sbin/nologin", "/usr/bin/git-shell", "/bin/sync"]


def make_snapshot(rng):
    users = [f"user{i}" for i in range(rng.randint(4, 7))]
    pool = list(users)
    if rng.random() < 0.6:
        pool.append("svc_monitor")
    if rng.random() < 0.6:
        pool.append("svc_backup")
    if rng.random() < 0.6:
        pool.append("svc_low")

    next_high = 1000
    next_mid = 500  # in (499, 999]: exempt only under the un-amended ceiling
    meta = {}
    for user in pool:
        if user == "svc_low":
            uid = rng.randint(100, 499)
        elif rng.random() < 0.35:
            uid = next_mid
            next_mid += 1
        else:
            uid = next_high
            next_high += 1
        roll = rng.random()
        gid = GID_WHEEL if roll < 0.3 else (GID_DEV if roll < 0.5 else GID_USERS)
        meta[user] = {
            "uid": uid,
            "gid": gid,
            "nologin": rng.random() < 0.2,
            "locked": rng.random() < 0.3,
            "expired": rng.random() < 0.15,
            "future_expire": rng.random() < 0.15,
        }

    passwd_lines, shadow_lines = [], []
    for user, m in meta.items():
        shell = rng.choice(NOLOGIN_CHOICES) if m["nologin"] else "/bin/bash"
        passwd_lines.append(f"{user}:x:{m['uid']}:{m['gid']}::/home/{user}:{shell}")
        pw = rng.choice(LOCK_CHOICES) if m["locked"] else VALID_HASH
        # G-2026-16: an expiry day < REF_DAY disables; >= REF_DAY does not.
        if m["expired"]:
            expire = str(rng.randint(18000, REF_DAY - 1))
        elif m["future_expire"]:
            expire = str(rng.randint(REF_DAY, REF_DAY + 3000))
        else:
            expire = ""
        shadow_lines.append(f"{user}:{pw}:19000:0:99999:7::{expire}:")

    # root participates so that `Match Group` (G-2026-17) can resolve against its
    # effective group membership; root (uid 0) is exempt from sudo remediation.
    passwd_lines.append("root:x:0:0::/root:/bin/bash")
    shadow_lines.append(f"root:{VALID_HASH}:19000:0:99999:7:::")

    def supp(gid):
        cands = [u for u, m in meta.items() if m["gid"] != gid]
        k = rng.randint(0, min(2, len(cands)))
        return rng.sample(cands, k) if k else []

    wheel_members = supp(GID_WHEEL)
    dev_members = supp(GID_DEV)
    if rng.random() < 0.4:
        wheel_members.append("root")
    if rng.random() < 0.3:
        dev_members.append("root")
    group_lines = [
        "root:x:0:",
        f"wheel:x:{GID_WHEEL}:{','.join(wheel_members)}",
        f"developers:x:{GID_DEV}:{','.join(dev_members)}",
        f"users:x:{GID_USERS}:",
    ]

    sudoers = ["Defaults env_reset", "# managed centrally", "%wheel ALL=(ALL) NOPASSWD: ALL"]

    # G-2026-18: host scoping. A rule applies on this host only when its host field
    # resolves to include AUDIT_HOST (gw-lab-01) or ALL; otherwise it is ignored.
    if rng.random() < 0.4:
        if rng.random() < 0.5:
            sudoers.append("Host_Alias LABHOSTS = gw-lab-01, bastion-1")
        else:
            sudoers.append("Host_Alias LABHOSTS = db-prod-07, db-prod-08")

    def host_field():
        r = rng.random()
        if r < 0.5:
            return "ALL"
        if r < 0.72:
            return "gw-lab-01"
        if r < 0.9:
            return rng.choice(["db-prod-07", "edge-09"])  # non-matching
        return "LABHOSTS"

    if rng.random() < 0.6:
        victim = rng.choice(pool)
        sudoers.append(f"User_Alias OPS = %developers, !{victim}")
        sudoers.append("OPS ALL=(ALL) NOPASSWD: ALL")
    for user in pool:
        r = rng.random()
        if r < 0.18:
            sudoers.append(f"{user} {host_field()}=(ALL) NOPASSWD: ALL")
        elif r < 0.34:
            # command-specific NOPASSWD: must NOT count (G-2026-02)
            sudoers.append(f"{user} {host_field()}=(ALL) NOPASSWD: /usr/bin/systemctl restart lab")
        elif r < 0.44:
            sudoers.append(f"{user} {host_field()}=(ALL) ALL")
        elif r < 0.54:
            # non-root runas NOPASSWD: ALL must NOT count (G-2026-15)
            sudoers.append(f"{user} {host_field()}=({rng.choice(['www-data', 'deploy'])}) NOPASSWD: ALL")
        elif r < 0.64:
            # G-2026-19: command tags are sticky, so NOPASSWD on a specific
            # command also applies to a later ALL unless PASSWD resets it.
            sudoers.append(f"{user} {host_field()}=(ALL) NOPASSWD: /usr/bin/id, ALL")
        elif r < 0.72:
            sudoers.append(f"{user} {host_field()}=(ALL) NOPASSWD: /usr/bin/id, PASSWD: ALL")
    if rng.random() < 0.45:
        # Defaults-based passwordless grant (G-2026-05): body ignores Defaults,
        # amendment makes `!authenticate` grant NOPASSWD: ALL to the binder.
        sudoers.append(f"Defaults:{rng.choice(pool)} !authenticate")
    if rng.random() < 0.25:
        sudoers.append("Defaults:%developers !authenticate")
    # Last-word overrides (G-2026-07): a later spec supersedes earlier grants for
    # the same principal, so these distinguish last-match from accumulation. A
    # trailing non-root runas NOPASSWD line (G-2026-15) also revokes.
    for user in pool:
        if rng.random() < 0.4:
            roll = rng.random()
            if roll < 0.4:
                sudoers.append(f"{user} {host_field()}=(ALL) NOPASSWD: ALL")
            elif roll < 0.7:
                sudoers.append(f"{user} {host_field()}=(ALL) ALL")
            else:
                sudoers.append(f"{user} {host_field()}=(www-data) NOPASSWD: ALL")

    # Drop-in includes (G-2026-09): `#includedir` splices /etc/sudoers.d files
    # (sorted) at the directive position, participating in last-match ordering.
    sudoers_d = {}
    if rng.random() < 0.55:
        sudoers.append(rng.choice(["@includedir /etc/sudoers.d", "#includedir /etc/sudoers.d"]))
        u1 = rng.choice(pool)
        sudoers_d["10-team"] = f"{u1} ALL=(ALL) {'NOPASSWD: ALL' if rng.random() < 0.5 else 'ALL'}\n"
        if rng.random() < 0.6:
            u2 = rng.choice(pool)
            sudoers_d["20-ops"] = f"{u2} ALL=(ALL) {'NOPASSWD: ALL' if rng.random() < 0.5 else 'ALL'}\n"
        if rng.random() < 0.5:
            # A spec after the include is the true last word for that principal.
            u3 = rng.choice(pool)
            sudoers.append(f"{u3} ALL=(ALL) {'NOPASSWD: ALL' if rng.random() < 0.5 else 'ALL'}")

    auth = {}
    for u in pool:
        r = rng.random()
        if r < 0.35:
            auth[u] = f"ssh-ed25519 AAAA{u} {u}@lab\n"
        elif r < 0.5:
            auth[u] = f'from="198.51.100.0/24",no-pty ssh-ed25519 AAAA{u} {u}@lab\n'
        elif r < 0.6:
            auth[u] = f"# rotated out\n@revoked ssh-ed25519 AAAA{u} {u}@lab\n"

    # sshd drop-ins exercise the context evaluation of G-2026-17: Match blocks
    # apply only when their User/Group/Address criteria match the audit context
    # (root @ 198.51.100.10). Keywords placed only inside a block become effective
    # iff the block applies; first occurrence in concatenated order wins.
    KW = [
        "PermitRootLogin",
        "PasswordAuthentication",
        "KbdInteractiveAuthentication",
        "ChallengeResponseAuthentication",
    ]
    KWVALS = {
        "PermitRootLogin": ["yes", "no", "No", "prohibit-password", "without-password"],
        "PasswordAuthentication": ["yes", "no", "YES"],
        "KbdInteractiveAuthentication": ["yes", "no", "No"],
        "ChallengeResponseAuthentication": ["yes", "no"],
    }

    def random_match_criteria():
        t = rng.random()
        if t < 0.18:
            return "all"
        if t < 0.42:
            return "User " + rng.choice(
                ["root", "root,deploy", "*", "admin", "!root", "*,!root", "deploy,admin"]
            )
        if t < 0.64:
            return "Address " + rng.choice(
                ["198.51.100.10", "198.51.100.0/24", "198.51.0.0/16", "0.0.0.0/0",
                 "10.0.0.0/8", "203.0.113.5", "198.51.101.0/24"]
            )
        if t < 0.84:
            return "Group " + rng.choice(["root", "wheel", "developers", "users"])
        return (
            "User " + rng.choice(["root", "*", "admin"])
            + " Address " + rng.choice(["198.51.100.0/24", "10.0.0.0/8"])
        )

    def kwline():
        kw = rng.choice(KW)
        return f"{kw} {rng.choice(KWVALS[kw])}\n"

    dropins = {}
    idx = 10
    if rng.random() < 0.75:
        dropins[f"{idx:02d}-base.conf"] = f"PermitRootLogin {rng.choice(KWVALS['PermitRootLogin'])}\n"
        idx += 10
    for _ in range(rng.randint(2, 4)):
        name = f"{idx:02d}-frag.conf"
        idx += 10
        if rng.random() < 0.4:
            dropins[name] = kwline()
        else:
            body = f"Match {random_match_criteria()}\n{kwline()}"
            if rng.random() < 0.5:
                body += kwline()
            if rng.random() < 0.4:
                body += f"Match all\n{kwline()}"
            dropins[name] = body

    files = {
        "passwd": "\n".join(passwd_lines) + "\n",
        "shadow": "\n".join(shadow_lines) + "\n",
        "group": "\n".join(group_lines) + "\n",
        "sudoers": "\n".join(sudoers) + "\n",
        "authorized_keys": auth,
        "sshd_config.d": dropins,
    }
    if sudoers_d:
        files["sudoers.d"] = sudoers_d
    return {"files": files}


def load_fixture(name):
    with open("/app/fixtures/" + name) as fh:
        return json.load(fh)
