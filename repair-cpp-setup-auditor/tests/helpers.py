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
        out[parts[0]] = parts[1] if len(parts) > 1 else ""
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
    h = shadow.get(name)
    if h is not None and (h in LOCKED_TOKENS or h.startswith("!")):
        return True
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
    """True iff the rule attaches NOPASSWD to the entire command set (ALL)."""
    i = 0
    while True:
        j = rest.find("NOPASSWD", i)
        if j < 0:
            return False
        k = j + len("NOPASSWD")
        while k < len(rest) and rest[k] in " \t":
            k += 1
        if k < len(rest) and rest[k] == ":":
            k += 1
            while k < len(rest) and rest[k] in " \t":
                k += 1
            if rest[k:k + 3] == "ALL" and (
                k + 3 == len(rest) or not rest[k + 3].isalnum()
            ):
                return True
        i = j + 1


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
    aliases, specs = {}, []
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
        # G-2026-05: a per-user/group `Defaults:<binder> !authenticate` line grants
        # passwordless sudo to that binder for the entire command set, overriding
        # the body rule that ignores Defaults lines.
        if s.startswith("Defaults:"):
            tail = s[len("Defaults:"):].strip()
            parts = tail.split(None, 1)
            if parts:
                binder = parts[0]
                flags = parts[1] if len(parts) > 1 else ""
                flag_tokens = [t.strip() for t in flags.replace(",", " ").split()]
                if "!authenticate" in flag_tokens:
                    specs.append((binder, "NOPASSWD: ALL"))
            continue
        head = s.split(None, 1)[0]
        if head in ("Host_Alias", "Runas_Alias", "Cmnd_Alias", "Defaults") or s.startswith("Defaults"):
            continue
        toks = s.split(None, 1)
        specs.append((toks[0], toks[1] if len(toks) > 1 else ""))

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
    for principal, rest in specs:
        grants = _grants_all_nopasswd(rest)
        is_neg, base = expand_token(principal, set())
        if is_neg:
            continue
        for u in base:
            state[u] = grants
    return {u for u, v in state.items() if v}


def _parse_keys(auth_map):
    out = set()
    for user, text in auth_map.items():
        for line in text.splitlines():
            s = line.strip()
            if s and not s.startswith("#"):
                out.add(user)
                break
    return out


def _parse_sshd(dropins):
    effective = {}
    in_global = True
    for fname in sorted(dropins):
        for line in dropins[fname].splitlines():
            s = line.strip()
            if not s or s.startswith("#"):
                continue
            toks = s.split()
            if toks[0].lower() == "match":
                # G-2026-08: `Match all` resumes global scope; other Match blocks
                # suspend evaluation until the next `Match all` or end of input.
                crit = toks[1].lower() if len(toks) > 1 else ""
                in_global = crit == "all"
                continue
            if not in_global:
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
    sshd_eff = _parse_sshd(files.get("sshd_config.d", {}))
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
        }

    passwd_lines, shadow_lines = [], []
    for user, m in meta.items():
        shell = rng.choice(NOLOGIN_CHOICES) if m["nologin"] else "/bin/bash"
        passwd_lines.append(f"{user}:x:{m['uid']}:{m['gid']}::/home/{user}:{shell}")
        pw = rng.choice(LOCK_CHOICES) if m["locked"] else VALID_HASH
        shadow_lines.append(f"{user}:{pw}:19000:0:99999:7:::")

    def supp(gid):
        cands = [u for u, m in meta.items() if m["gid"] != gid]
        k = rng.randint(0, min(2, len(cands)))
        return rng.sample(cands, k) if k else []

    group_lines = [
        f"wheel:x:{GID_WHEEL}:{','.join(supp(GID_WHEEL))}",
        f"developers:x:{GID_DEV}:{','.join(supp(GID_DEV))}",
        f"users:x:{GID_USERS}:",
    ]

    sudoers = ["Defaults env_reset", "# managed centrally", "%wheel ALL=(ALL) NOPASSWD: ALL"]
    if rng.random() < 0.6:
        victim = rng.choice(pool)
        sudoers.append(f"User_Alias OPS = %developers, !{victim}")
        sudoers.append("OPS ALL=(ALL) NOPASSWD: ALL")
    for user in pool:
        r = rng.random()
        if r < 0.18:
            sudoers.append(f"{user} ALL=(ALL) NOPASSWD: ALL")
        elif r < 0.34:
            # command-specific NOPASSWD: must NOT count (G-2026-02)
            sudoers.append(f"{user} ALL=(ALL) NOPASSWD: /usr/bin/systemctl restart lab")
        elif r < 0.44:
            sudoers.append(f"{user} ALL=(ALL) ALL")
    if rng.random() < 0.45:
        # Defaults-based passwordless grant (G-2026-05): body ignores Defaults,
        # amendment makes `!authenticate` grant NOPASSWD: ALL to the binder.
        sudoers.append(f"Defaults:{rng.choice(pool)} !authenticate")
    if rng.random() < 0.25:
        sudoers.append("Defaults:%developers !authenticate")
    # Last-word overrides (G-2026-07): a later spec supersedes earlier grants for
    # the same principal, so these distinguish last-match from accumulation.
    for user in pool:
        if rng.random() < 0.4:
            tail = "NOPASSWD: ALL" if rng.random() < 0.5 else "ALL"
            sudoers.append(f"{user} ALL=(ALL) {tail}")

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

    auth = {u: f"ssh-ed25519 AAAA{u} {u}@lab\n" for u in pool if rng.random() < 0.5}

    dropins = {"10-base.conf": f"PermitRootLogin {rng.choice(['yes', 'no', 'No', 'prohibit-password', 'without-password'])}\n"}
    if rng.random() < 0.5:
        dropins["20-extra.conf"] = f"PermitRootLogin {rng.choice(['yes', 'no'])}\n"
    if rng.random() < 0.6:
        dropins["30-auth.conf"] = f"PasswordAuthentication {rng.choice(['yes', 'no', 'YES'])}\n"
    if rng.random() < 0.7:
        kbd_name = rng.choice(["KbdInteractiveAuthentication", "ChallengeResponseAuthentication"])
        dropins["40-kbd.conf"] = f"{kbd_name} {rng.choice(['yes', 'no', 'No'])}\n"
    if rng.random() < 0.25:
        # Alias spelling earlier in filename order must win first (G-2026-06).
        dropins["05-kbd.conf"] = f"ChallengeResponseAuthentication {rng.choice(['yes', 'no'])}\n"
    if rng.random() < 0.4:
        dropins["90-match.conf"] = "Match User admin\nPasswordAuthentication yes\n"
    if rng.random() < 0.4:
        # A `Match all` reset (G-2026-08): the global line after it must count,
        # which a naive "stop at first Match" parser misses. Use a fresh key so
        # the first-occurrence rule does not pre-empt it.
        val = rng.choice(["yes", "no"])
        dropins["50-reset.conf"] = (
            "Match User deploy\nPermitRootLogin yes\n"
            f"Match all\nKbdInteractiveAuthentication {val}\n"
        )

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
