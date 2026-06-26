"""Helpers for driving the HarborDesk API and inspecting its audit ledger.

The verifier talks to the API over HTTP (stdlib urllib, so no extra deps and no
``curl`` in the test layer) and reads the SQLite audit database directly. Ground
truth lives here in ``tests/`` only; the agent never sees this file.
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
ALLOWED_ORIGIN = "https://harbordesk.internal"


def read_secret():
    """Return the bootstrap secret the API expects, read from its data dir."""
    with open(SECRET_FILE, encoding="utf-8") as handle:
        return handle.read().strip()


def request(method, path, headers=None, body=None):
    """Issue one HTTP request and return (status, headers_dict, parsed_body).

    Non-2xx responses are captured rather than raised so security responses
    (401/403/404) can be asserted on directly.
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
    """Return all audit_log rows as a list of dicts, ordered by id."""
    conn = sqlite3.connect(AUDIT_DB)
    conn.row_factory = sqlite3.Row
    try:
        cur = conn.execute(
            "SELECT id, event, route, origin, decision, reason FROM audit_log ORDER BY id"
        )
        return [dict(row) for row in cur.fetchall()]
    finally:
        conn.close()


def count_decisions(event, decision):
    """Count audit rows for a given event/decision pair via SQL."""
    conn = sqlite3.connect(AUDIT_DB)
    try:
        cur = conn.execute(
            "SELECT COUNT(*) FROM audit_log WHERE event = ? AND decision = ?",
            (event, decision),
        )
        return cur.fetchone()[0]
    finally:
        conn.close()
