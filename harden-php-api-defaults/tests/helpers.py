"""Driver + hidden reference for the HarborDesk Edge API verifier.

The verifier talks to the API over HTTP (stdlib urllib, so no extra deps) and
reads the SQLite audit ledger directly. Ground truth lives here in ``tests/``
only; the agent never sees this file. The reference encodes the resolved policy
of the HarborDesk Edge API Hardening Standard (body controls + the authoritative
Appendix G amendments) and is the single source of truth the tests compare the
running API against.
"""

import json
import sqlite3
import urllib.error
import urllib.request

BASE = "http://127.0.0.1:8080"
APP_DIR = "/app/harbordesk"
TOKEN_FILE = f"{APP_DIR}/data/admin_token"
AUDIT_DB = f"{APP_DIR}/data/audit.db"
SECRET_FILE = f"{APP_DIR}/data/bootstrap_secret"

# ---------------------------------------------------------------------------
# Resolved policy (HEAS body as amended by Appendix G).
# ---------------------------------------------------------------------------
# CO-ORIGIN-ALLOW + G-2026-01: exact-match allowlist of two origins.
ALLOWED_ORIGINS = (
    "https://harbordesk.internal",
    "https://ops.harbordesk.internal",
)
# Origins that must receive NO cross-origin grant (incl. exact-match traps:
# trailing slash, differing scheme, differing port, subdomain).
DISALLOWED_ORIGINS = (
    "https://evil.example",
    "https://harbordesk.internal/",
    "http://harbordesk.internal",
    "https://harbordesk.internal:8443",
    "https://api.harbordesk.internal",
)
# CO-PREFLIGHT + G-2026-02: Max-Age lowered 600 -> 300.
PREFLIGHT_MAX_AGE = "300"
ALLOW_METHODS = "GET, POST, OPTIONS"
ALLOW_HEADERS = "Authorization, Content-Type, X-Bootstrap-Secret"

# Legacy ledger seed (schema 1: a non-null "actor" column, no "origin"), plus
# real historical rows the migration must preserve. Kept here so the test runner
# and inter-case resets stay in lockstep.
LEGACY_HISTORY = [
    ("2026-01-02T08:00:00+00:00", "health", "/health", "svc-legacy", "accepted", "legacy_history"),
    ("2026-01-02T08:05:00+00:00", "bootstrap", "/admin/bootstrap", "svc-legacy", "denied", "legacy_history"),
]


def read_secret():
    """Return the bootstrap secret the API expects, read from its data dir."""
    with open(SECRET_FILE, encoding="utf-8") as handle:
        return handle.read().strip()


def seed_legacy_ledger():
    """(Re)write the audit ledger in the legacy schema-1 layout with history.

    Used between randomized cases so the migration defect must be fixed in code
    (and re-applied) rather than worked around by deleting the database.
    """
    conn = sqlite3.connect(AUDIT_DB)
    try:
        conn.execute("DROP TABLE IF EXISTS audit_log")
        conn.execute("DROP TABLE IF EXISTS audit_log_legacy")
        conn.execute(
            "CREATE TABLE audit_log (id INTEGER PRIMARY KEY AUTOINCREMENT, "
            "ts TEXT NOT NULL, event TEXT NOT NULL, route TEXT NOT NULL, "
            "actor TEXT NOT NULL, decision TEXT NOT NULL, reason TEXT)"
        )
        conn.executemany(
            "INSERT INTO audit_log (ts, event, route, actor, decision, reason) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            LEGACY_HISTORY,
        )
        conn.commit()
    finally:
        conn.close()


def reset_state():
    """Clear the minted token and reseed the legacy ledger for a fresh case."""
    import os

    try:
        os.remove(TOKEN_FILE)
    except FileNotFoundError:
        pass
    seed_legacy_ledger()


def request(method, path, headers=None, body=None):
    """Issue one HTTP request and return (status, headers_dict, raw, parsed).

    Non-2xx responses are captured rather than raised so security responses
    (401/403/404/409) can be asserted on directly.
    """
    url = BASE + path
    data = body.encode("utf-8") if isinstance(body, str) else body
    req = urllib.request.Request(url, data=data, method=method)
    for key, value in (headers or {}).items():
        req.add_header(key, value)
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            status = resp.status
            resp_headers = {k: v for k, v in resp.headers.items()}
            raw = resp.read().decode("utf-8")
    except urllib.error.HTTPError as err:
        status = err.code
        resp_headers = {k: v for k, v in err.headers.items()}
        raw = err.read().decode("utf-8")
    parsed = None
    if raw:
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            parsed = None
    return status, resp_headers, raw, parsed


def header_ci(headers, name):
    """Case-insensitive header lookup; returns None when the header is absent."""
    target = name.lower()
    for key, value in headers.items():
        if key.lower() == target:
            return value
    return None


def audit_rows():
    """Return all audit_log rows as dicts, ordered by id.

    Only columns common to every reasonable ledger shape are selected; the exact
    storage schema (extra columns, column order) is an implementation choice and
    must not be assumed here.
    """
    conn = sqlite3.connect(AUDIT_DB)
    conn.row_factory = sqlite3.Row
    try:
        cur = conn.execute(
            "SELECT id, ts, event, route, decision, reason FROM audit_log ORDER BY id"
        )
        return [dict(row) for row in cur.fetchall()]
    finally:
        conn.close()


def audit_origin_supported():
    """True if the ledger has an ``origin`` column (post-migration schema)."""
    conn = sqlite3.connect(AUDIT_DB)
    try:
        cols = [r[1] for r in conn.execute("PRAGMA table_info(audit_log)")]
    finally:
        conn.close()
    return "origin" in cols


def audit_rows_with_origin():
    """Return rows including origin (post-migration). Origin is None for history."""
    conn = sqlite3.connect(AUDIT_DB)
    conn.row_factory = sqlite3.Row
    try:
        cur = conn.execute(
            "SELECT id, event, route, origin, decision, reason FROM audit_log ORDER BY id"
        )
        return [dict(row) for row in cur.fetchall()]
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Reference simulator: resolved-policy expected outcome for one request.
# ---------------------------------------------------------------------------
class _State:
    """Tracks whether an administrative token currently exists."""

    def __init__(self):
        self.token_exists = False


def expected_cors(origin, preflight):
    """Expected cross-origin headers (CO-ORIGIN-ALLOW + CO-PREFLIGHT as amended)."""
    if origin in ALLOWED_ORIGINS:
        out = {
            "Access-Control-Allow-Origin": origin,
            "Access-Control-Allow-Credentials": "true",
            "Vary": "Origin",
        }
        if preflight:
            out["Access-Control-Allow-Methods"] = ALLOW_METHODS
            out["Access-Control-Allow-Headers"] = ALLOW_HEADERS
            out["Access-Control-Max-Age"] = PREFLIGHT_MAX_AGE
        return out
    return {}


def simulate(state, req):
    """Compute the expected outcome of one request against the resolved policy.

    ``req`` keys: method, path, origin (or None), secret in {None,"wrong","valid"},
    token in {None,"wrong","valid"}, body (raw str). Mutates ``state`` on a
    successful bootstrap. Returns a dict with: status, cors (expected header
    dict; {} means none), body ("ok"|"token"|"error"|"empty"), and audit (a
    (event, route, origin, decision, reason) tuple, or None if not audited).
    """
    method, path = req["method"], req["path"]
    origin = req.get("origin")
    preflight = method == "OPTIONS"
    cors = expected_cors(origin, preflight)

    if preflight:
        return {"status": 204, "cors": cors, "body": "empty", "audit": None}

    if path == "/health" and method == "GET":
        token = req.get("token")
        if token is None:
            return {"status": 401, "cors": cors, "body": "error",
                    "audit": ("health", "/health", origin, "denied", "missing_credentials")}
        if token == "valid" and state.token_exists:
            return {"status": 200, "cors": cors, "body": "ok",
                    "audit": ("health", "/health", origin, "accepted", None)}
        return {"status": 401, "cors": cors, "body": "error",
                "audit": ("health", "/health", origin, "denied", "invalid_token")}

    if path == "/admin/bootstrap" and method == "POST":
        body = req.get("body", "")
        if body and not _is_json(body):
            return {"status": 400, "cors": cors, "body": "error",
                    "audit": ("bootstrap", "/admin/bootstrap", origin, "denied", "malformed_request")}
        # G-2026-05: already-bootstrapped takes precedence over secret validation.
        if state.token_exists:
            return {"status": 409, "cors": cors, "body": "error",
                    "audit": ("bootstrap", "/admin/bootstrap", origin, "denied", "already_bootstrapped")}
        if req.get("secret") != "valid":
            return {"status": 403, "cors": cors, "body": "error",
                    "audit": ("bootstrap", "/admin/bootstrap", origin, "denied", "invalid_secret")}
        state.token_exists = True
        return {"status": 201, "cors": cors, "body": "token",
                "audit": ("bootstrap", "/admin/bootstrap", origin, "accepted", None)}

    return {"status": 404, "cors": cors, "body": "error", "audit": None}


def _is_json(raw):
    try:
        json.loads(raw)
        return True
    except (json.JSONDecodeError, ValueError):
        return False


# ---------------------------------------------------------------------------
# Randomized request-sequence generator.
# ---------------------------------------------------------------------------
def _rand_origin(rng):
    """Pick an origin: allowed, disallowed, or none."""
    roll = rng.random()
    if roll < 0.45:
        return rng.choice(ALLOWED_ORIGINS)
    if roll < 0.85:
        return rng.choice(DISALLOWED_ORIGINS)
    return None


def make_sequence(rng):
    """Build one randomized request lifecycle.

    Phase 1 (pre-bootstrap): varied unauthenticated/failed requests.
    Then a successful bootstrap, then optional repeat attempts.
    Phase 2 (post-bootstrap): varied authenticated requests and preflights.
    """
    seq = []

    pre_choices = [
        {"method": "GET", "path": "/health", "token": None},
        {"method": "GET", "path": "/health", "token": "wrong"},
        {"method": "POST", "path": "/admin/bootstrap", "secret": "wrong", "body": "{}"},
        {"method": "POST", "path": "/admin/bootstrap", "secret": None, "body": "{}"},
        {"method": "POST", "path": "/admin/bootstrap", "secret": "valid", "body": "{bad json"},
        {"method": "OPTIONS", "path": "/admin/bootstrap"},
        {"method": "GET", "path": "/nope"},
    ]
    for _ in range(rng.randint(2, 5)):
        item = dict(rng.choice(pre_choices))
        item["origin"] = _rand_origin(rng)
        seq.append(item)

    # The one successful bootstrap.
    seq.append({"method": "POST", "path": "/admin/bootstrap", "secret": "valid",
                "body": "{}", "origin": _rand_origin(rng)})

    # Optional repeat attempts (must be refused with 409 regardless of secret).
    for _ in range(rng.randint(0, 2)):
        seq.append({"method": "POST", "path": "/admin/bootstrap",
                    "secret": rng.choice(["valid", "wrong", None]),
                    "body": "{}", "origin": _rand_origin(rng)})

    post_choices = [
        {"method": "GET", "path": "/health", "token": "valid"},
        {"method": "GET", "path": "/health", "token": "wrong"},
        {"method": "GET", "path": "/health", "token": None},
        {"method": "OPTIONS", "path": "/health"},
        {"method": "OPTIONS", "path": "/admin/bootstrap"},
        {"method": "GET", "path": "/unknown"},
    ]
    for _ in range(rng.randint(3, 7)):
        item = dict(rng.choice(post_choices))
        item["origin"] = _rand_origin(rng)
        seq.append(item)

    return seq


def replay_request(req, secret, token):
    """Translate a symbolic request into headers and issue it.

    ``secret``/``token`` provide the real credential values substituted for the
    symbolic "valid" markers.
    """
    headers = {}
    if req.get("origin") is not None:
        headers["Origin"] = req["origin"]

    if req["path"] == "/admin/bootstrap" and req["method"] == "POST":
        headers["Content-Type"] = "application/json"
        sec = req.get("secret")
        if sec == "valid":
            headers["X-Bootstrap-Secret"] = secret
        elif sec == "wrong":
            headers["X-Bootstrap-Secret"] = "nope-" + secret[:4]
        body = req.get("body", "{}")
        return request("POST", "/admin/bootstrap", headers, body)

    if req["path"] == "/health" or req["path"].startswith("/"):
        tok = req.get("token")
        if tok == "valid" and token is not None:
            headers["Authorization"] = f"Bearer {token}"
        elif tok == "wrong":
            headers["Authorization"] = "Bearer not-a-real-token"
        return request(req["method"], req["path"], headers, None)

    return request(req["method"], req["path"], headers, None)
