"""HTTP driver and hidden resolved-policy model for HarborDesk."""

import json
import os
import sqlite3
import urllib.error
import urllib.request

BASE = "http://127.0.0.1:8080"
APP_DIR = "/app/harbordesk"
TOKEN_FILE = f"{APP_DIR}/data/admin_token"
TOKEN_LOCK_FILE = f"{APP_DIR}/data/admin_token.lock"
AUDIT_DB = f"{APP_DIR}/data/audit.db"
SECRET_FILE = f"{APP_DIR}/data/bootstrap_secret"
ORIGINS_FILE = f"{APP_DIR}/data/allowed_origins"
GENERATION_FILE = f"{APP_DIR}/data/credential_generation"
INITIAL_GENERATION = 41
PREDECESSOR_USES = 2

ALLOWED_ORIGINS = (
    "https://harbordesk.internal",
    "https://ops.harbordesk.internal",
)
DISALLOWED_ORIGINS = (
    "https://evil.example",
    "https://harbordesk.internal/",
    "http://harbordesk.internal",
    "https://harbordesk.internal:8443",
    "https://api.harbordesk.internal",
)
LEGACY_HISTORY = [
    (
        "2026-01-02T08:00:00+00:00",
        "health",
        "/health",
        "svc-legacy",
        "accepted",
        "legacy_history",
    ),
    (
        "2026-01-02T08:05:00+00:00",
        "bootstrap",
        "/admin/bootstrap",
        "svc-legacy",
        "denied",
        "legacy_history",
    ),
]


def read_secret():
    """Read the deployment bootstrap secret."""
    with open(SECRET_FILE, encoding="utf-8") as handle:
        return handle.read().strip()


def set_generation(value):
    """Publish a deployment credential generation."""
    with open(GENERATION_FILE, "w", encoding="ascii") as handle:
        handle.write(f"{value}\n")


def seed_legacy_ledger():
    """Replace audit_log with the seeded legacy actor layout."""
    conn = sqlite3.connect(AUDIT_DB, timeout=10)
    try:
        conn.execute("DROP TABLE IF EXISTS audit_log")
        conn.execute("DROP TABLE IF EXISTS audit_log_reconciled")
        conn.execute(
            "CREATE TABLE audit_log ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT, ts TEXT NOT NULL, "
            "event TEXT NOT NULL, route TEXT NOT NULL, actor TEXT NOT NULL, "
            "decision TEXT NOT NULL, reason TEXT)"
        )
        conn.executemany(
            "INSERT INTO audit_log (ts, event, route, actor, decision, reason) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            LEGACY_HISTORY,
        )
        conn.execute(
            "CREATE TABLE IF NOT EXISTS audit ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT, ts TEXT NOT NULL, "
            "event TEXT NOT NULL, route TEXT NOT NULL, origin TEXT, "
            "decision TEXT NOT NULL, reason TEXT)"
        )
        if conn.execute("SELECT COUNT(*) FROM audit").fetchone()[0] == 0:
            conn.execute(
                "INSERT INTO audit "
                "(ts, event, route, origin, decision, reason) VALUES "
                "('2026-01-01T00:00:00+00:00', 'decoy', '/legacy', "
                "NULL, 'accepted', 'decoy_seed')"
            )
        conn.commit()
    finally:
        conn.close()


def reset_state():
    """Reset credentials, generation, decoy input, and legacy ledger."""
    for path in (TOKEN_FILE, TOKEN_LOCK_FILE):
        try:
            os.remove(path)
        except FileNotFoundError:
            pass
    set_generation(INITIAL_GENERATION)
    with open(ORIGINS_FILE, "w", encoding="utf-8") as handle:
        handle.write("https://harbordesk.internal\n")
    seed_legacy_ledger()


def request(method, path, headers=None, body=None):
    """Issue one API request and capture success or HTTP error responses."""
    data = body.encode("utf-8") if isinstance(body, str) else body
    req = urllib.request.Request(BASE + path, data=data, method=method)
    for key, value in (headers or {}).items():
        req.add_header(key, value)
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            status = response.status
            response_headers = dict(response.headers.items())
            raw = response.read().decode("utf-8")
    except urllib.error.HTTPError as error:
        status = error.code
        response_headers = dict(error.headers.items())
        raw = error.read().decode("utf-8")
    parsed = None
    if raw:
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            pass
    return status, response_headers, raw, parsed


def header_ci(headers, name):
    """Return a response header using case-insensitive lookup."""
    target = name.lower()
    for key, value in headers.items():
        if key.lower() == target:
            return value
    return None


def audit_rows():
    """Read reconciled audit_log rows in id order."""
    conn = sqlite3.connect(AUDIT_DB, timeout=10)
    conn.row_factory = sqlite3.Row
    try:
        cursor = conn.execute(
            "SELECT id, event, route, origin, decision, reason "
            "FROM audit_log ORDER BY id"
        )
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()


def shadow_audit_rows():
    """Read rows from the decoy shadow audit table."""
    conn = sqlite3.connect(AUDIT_DB, timeout=10)
    conn.row_factory = sqlite3.Row
    try:
        cursor = conn.execute(
            "SELECT id, event, route, origin, decision, reason "
            "FROM audit ORDER BY id"
        )
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()


def bootstrap(secret=None, body="{}", origin=None):
    """Call bootstrap with optional secret and origin."""
    headers = {"Content-Type": "application/json"}
    if secret is not None:
        headers["X-Bootstrap-Secret"] = secret
    if origin is not None:
        headers["Origin"] = origin
    return request("POST", "/admin/bootstrap", headers, body)


def health(token=None, origin=None, authorization=None):
    """Call health with a token or explicit Authorization value."""
    headers = {}
    if authorization is not None:
        headers["Authorization"] = authorization
    elif token is not None:
        headers["Authorization"] = f"Bearer {token}"
    if origin is not None:
        headers["Origin"] = origin
    return request("GET", "/health", headers)


class State:
    """Resolved credential lifecycle state for randomized replay."""

    def __init__(self):
        self.target_generation = INITIAL_GENERATION
        self.stored_generation = None
        self.current = None
        self.previous = None
        self.previous_origins_remaining = set()
        self.pending_generation = None
        self.pending = None
        self.pending_origins = set()
        self.pending_sponsors = set()
        self.secret_revision = 0
        self.pending_secret_revision = None


def audited_origin(origin):
    """Resolve the ledger origin: allowlisted exact value or SQL NULL."""
    return origin if origin in ALLOWED_ORIGINS else None


def expected_cors(origin, preflight):
    """Resolve amended CORS headers for one request."""
    if origin not in ALLOWED_ORIGINS:
        return {}
    result = {
        "Access-Control-Allow-Origin": origin,
        "Access-Control-Allow-Credentials": "true",
        "Vary": "Origin",
    }
    if preflight:
        result.update(
            {
                "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
                "Access-Control-Allow-Headers": (
                    "Authorization, Content-Type, X-Bootstrap-Secret"
                ),
                "Access-Control-Max-Age": "300",
            }
        )
    return result


def simulate(state, operation):
    """Resolve one symbolic operation and mutate lifecycle state."""
    if operation["kind"] == "advance":
        state.target_generation += operation.get("amount", 1)
        return None
    if operation["kind"] == "rotate_secret":
        state.secret_revision += 1
        return None

    method = operation["method"]
    path = operation["path"]
    origin = operation.get("origin")
    cors = expected_cors(origin, method == "OPTIONS")
    if method == "OPTIONS":
        return {"status": 204, "body": "empty", "cors": cors, "audit": None}

    if path == "/health" and method == "GET":
        credential = operation.get("credential")
        if credential is None or credential == "malformed":
            return {
                "status": 401,
                "body": "error",
                "cors": cors,
                "audit": (
                    "health",
                    path,
                    audited_origin(origin),
                    "denied",
                    "missing_credentials",
                ),
            }
        if (
            state.pending is not None
            and state.pending_secret_revision != state.secret_revision
        ):
            state.pending_sponsors = set()
            state.pending_origins = set()
            state.pending_secret_revision = state.secret_revision
        accepted = False
        via_predecessor = False
        reason = None
        if credential == state.current:
            accepted = True
            if (
                state.pending is not None
                and state.target_generation == state.pending_generation
                and origin in ALLOWED_ORIGINS
            ):
                state.pending_sponsors.add(origin)
        elif (
            credential == state.previous
            and origin in state.previous_origins_remaining
        ):
            accepted = True
            via_predecessor = True
            state.previous_origins_remaining.remove(origin)
        elif credential == state.pending and origin in ALLOWED_ORIGINS:
            if (
                state.pending_generation is not None
                and state.target_generation > state.pending_generation
            ):
                accepted = False
                reason = "invalid_token"
            elif origin not in state.pending_sponsors:
                accepted = False
                reason = "invalid_token"
            else:
                accepted = True
                new_confirmation = origin not in state.pending_origins
                state.pending_origins.add(origin)
                if new_confirmation and len(state.pending_origins) == 1:
                    state.pending_sponsors.intersection_update(state.pending_origins)
                if state.pending_origins == set(ALLOWED_ORIGINS):
                    state.previous = state.current
                    state.previous_origins_remaining = set(ALLOWED_ORIGINS)
                    state.current = state.pending
                    state.stored_generation = state.pending_generation
                    state.pending = None
                    state.pending_generation = None
                    state.pending_origins = set()
                    state.pending_sponsors = set()
                    state.pending_secret_revision = None
                    reason = "cutover_activated"
                else:
                    reason = "cutover_confirmation"
        if accepted:
            if via_predecessor:
                reason = "predecessor_overlap"
        elif reason is None:
            reason = "invalid_token"
        if (
            not accepted
            and reason == "invalid_token"
            and state.pending is not None
            and origin in ALLOWED_ORIGINS
        ):
            state.pending_sponsors.discard(origin)
        return {
            "status": 200 if accepted else 401,
            "body": "ok" if accepted else "error",
            "cors": cors,
            "audit": (
                "health",
                path,
                audited_origin(origin),
                "accepted" if accepted else "denied",
                reason,
            ),
        }

    if path == "/admin/bootstrap" and method == "POST":
        body = operation.get("body", "{}")
        if body and not _is_json(body):
            return {
                "status": 400,
                "body": "error",
                "cors": cors,
                "audit": (
                    "bootstrap",
                    path,
                    audited_origin(origin),
                    "denied",
                    "malformed_request",
                ),
            }
        highest_generation = (
            state.pending_generation
            if state.pending_generation is not None
            else state.stored_generation
        )
        if highest_generation is not None and state.target_generation <= highest_generation:
            return {
                "status": 409,
                "body": "error",
                "cors": cors,
                "audit": (
                    "bootstrap",
                    path,
                    audited_origin(origin),
                    "denied",
                    "already_bootstrapped",
                ),
            }
        if operation.get("secret") != "valid":
            return {
                "status": 403,
                "body": "error",
                "cors": cors,
                "audit": (
                    "bootstrap",
                    path,
                    audited_origin(origin),
                    "denied",
                    "invalid_secret",
                ),
            }
        label = operation["mint"]
        if state.current is None:
            state.current = label
            state.stored_generation = state.target_generation
        else:
            state.pending = label
            state.pending_generation = state.target_generation
            state.pending_origins = set()
            state.pending_sponsors = set()
            state.pending_secret_revision = state.secret_revision
        return {
            "status": 201,
            "body": "token",
            "cors": cors,
            "audit": ("bootstrap", path, audited_origin(origin), "accepted", None),
        }

    return {"status": 404, "body": "error", "cors": cors, "audit": None}


def replay(operation, secret, tokens):
    """Execute one symbolic operation against the real API."""
    if operation["kind"] == "advance":
        set_generation(operation["generation"])
        return None
    if operation["kind"] == "rotate_secret":
        with open(SECRET_FILE, "w", encoding="utf-8") as handle:
            handle.write(operation["value"] + "\n")
        return None
    headers = {}
    origin = operation.get("origin")
    if origin is not None:
        headers["Origin"] = origin
    if operation["path"] == "/admin/bootstrap" and operation["method"] == "POST":
        headers["Content-Type"] = "application/json"
        if operation.get("secret") == "valid":
            headers["X-Bootstrap-Secret"] = read_secret()
        elif operation.get("secret") == "wrong":
            headers["X-Bootstrap-Secret"] = "wrong-" + secret[:5]
        return request("POST", "/admin/bootstrap", headers, operation.get("body", "{}"))
    credential = operation.get("credential")
    if credential == "malformed":
        headers["Authorization"] = "Basic not-bearer"
    elif credential == "wrong":
        headers["Authorization"] = "Bearer not-a-real-token"
    elif credential in tokens:
        headers["Authorization"] = f"Bearer {tokens[credential]}"
    return request(operation["method"], operation["path"], headers)


def make_sequence(rng):
    """Build a lifecycle with two or three credential generations."""
    sequence = []

    def origin():
        return _random_origin(rng)

    sequence.extend(
        [
            {
                "kind": "request",
                "method": "GET",
                "path": "/health",
                "credential": rng.choice([None, "wrong", "malformed"]),
                "origin": origin(),
            },
            {
                "kind": "request",
                "method": "POST",
                "path": "/admin/bootstrap",
                "secret": "wrong",
                "body": "{}",
                "origin": origin(),
            },
            {
                "kind": "request",
                "method": "POST",
                "path": "/admin/bootstrap",
                "secret": "valid",
                "body": "{}",
                "mint": "g0",
                "origin": origin(),
            },
        ]
    )
    labels = ["g0"]
    generation = INITIAL_GENERATION
    rotations = rng.randint(1, 2)
    for number in range(1, rotations + 1):
        for _ in range(rng.randint(1, 3)):
            sequence.append(
                {
                    "kind": "request",
                    "method": rng.choice(["GET", "OPTIONS"]),
                    "path": rng.choice(["/health", "/admin/bootstrap", "/unknown"]),
                    "credential": rng.choice(labels + ["wrong", "malformed", None]),
                    "origin": origin(),
                }
            )
        amount = rng.randint(1, 3)
        generation += amount
        sequence.append(
            {"kind": "advance", "amount": amount, "generation": generation}
        )
        sequence.append(
            {
                "kind": "request",
                "method": "POST",
                "path": "/admin/bootstrap",
                "secret": "wrong",
                "body": "{}",
                "origin": origin(),
            }
        )
        label = f"g{number}"
        sequence.append(
            {
                "kind": "request",
                "method": "POST",
                "path": "/admin/bootstrap",
                "secret": "valid",
                "body": "{}",
                "mint": label,
                "origin": origin(),
            }
        )
        current_label = labels[-1]
        sequence.extend(
            [
                {
                    "kind": "request",
                    "method": "GET",
                    "path": "/health",
                    "credential": current_label,
                    "origin": ALLOWED_ORIGINS[0],
                },
                {
                    "kind": "request",
                    "method": "GET",
                    "path": "/health",
                    "credential": current_label,
                    "origin": ALLOWED_ORIGINS[1],
                },
                {
                    "kind": "request",
                    "method": "GET",
                    "path": "/health",
                    "credential": label,
                    "origin": ALLOWED_ORIGINS[0],
                },
                {
                    "kind": "request",
                    "method": "GET",
                    "path": "/health",
                    "credential": label,
                    "origin": ALLOWED_ORIGINS[1],
                },
            ]
        )
        if rng.random() < 0.5:
            sequence.extend(
                [
                    {
                        "kind": "rotate_secret",
                        "value": f"hd-random-secret-{number}-{rng.randrange(1_000_000)}",
                    },
                    {
                        "kind": "request",
                        "method": "GET",
                        "path": "/health",
                        "credential": label,
                        "origin": ALLOWED_ORIGINS[1],
                    },
                    {
                        "kind": "request",
                        "method": "GET",
                        "path": "/health",
                        "credential": current_label,
                        "origin": ALLOWED_ORIGINS[1],
                    },
                    {
                        "kind": "request",
                        "method": "GET",
                        "path": "/health",
                        "credential": label,
                        "origin": ALLOWED_ORIGINS[1],
                    },
                    {
                        "kind": "request",
                        "method": "GET",
                        "path": "/health",
                        "credential": current_label,
                        "origin": ALLOWED_ORIGINS[0],
                    },
                    {
                        "kind": "request",
                        "method": "GET",
                        "path": "/health",
                        "credential": label,
                        "origin": ALLOWED_ORIGINS[0],
                    },
                ]
            )
        else:
            sequence.extend(
                [
                    {
                        "kind": "request",
                        "method": "GET",
                        "path": "/health",
                        "credential": current_label,
                        "origin": ALLOWED_ORIGINS[1],
                    },
                    {
                        "kind": "request",
                        "method": "GET",
                        "path": "/health",
                        "credential": label,
                        "origin": ALLOWED_ORIGINS[1],
                    },
                ]
            )
        labels.append(label)
        for _ in range(rng.randint(4, 8)):
            sequence.append(
                {
                    "kind": "request",
                    "method": "GET",
                    "path": rng.choice(["/health", "/unknown"]),
                    "credential": rng.choice(labels + ["wrong", "malformed", None]),
                    "origin": origin(),
                }
            )
    return sequence


def _random_origin(rng):
    roll = rng.random()
    if roll < 0.45:
        return rng.choice(ALLOWED_ORIGINS)
    if roll < 0.85:
        return rng.choice(DISALLOWED_ORIGINS)
    return None


def _is_json(raw):
    try:
        json.loads(raw)
        return True
    except (json.JSONDecodeError, ValueError):
        return False
