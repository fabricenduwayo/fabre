"""Behavioral verifier for the hardened HarborDesk API.

A single session fixture replays the request sequence once against the running
service; each test asserts an independent property of the responses, the token
file permissions, or the SQLite audit ledger. Tests are not order-dependent --
they all read from the shared replay result.
"""

import os
import stat

import pytest

from helpers import (
    ALLOWED_ORIGIN,
    TOKEN_FILE,
    count_decisions,
    header_ci,
    read_secret,
    request,
)

EVIL_ORIGIN = "https://evil.example"
JSON = {"Content-Type": "application/json"}


@pytest.fixture(scope="session")
def replay():
    """Replay the full request flow once and return every captured response."""
    secret = read_secret()
    results = {}

    results["boot_no_secret"] = request("POST", "/admin/bootstrap", JSON, "{}")
    results["boot_wrong_secret"] = request(
        "POST", "/admin/bootstrap", {**JSON, "X-Bootstrap-Secret": "nope"}, "{}"
    )
    results["boot_ok"] = request(
        "POST", "/admin/bootstrap", {**JSON, "X-Bootstrap-Secret": secret}, "{}"
    )
    results["boot_repeat"] = request(
        "POST", "/admin/bootstrap", {**JSON, "X-Bootstrap-Secret": secret}, "{}"
    )

    status, _, _, body = results["boot_ok"]
    token = body["token"] if (status == 201 and body) else None
    results["token"] = token
    auth = {"Authorization": f"Bearer {token}"} if token else {}

    results["health_noauth"] = request("GET", "/health")
    results["health_ok"] = request("GET", "/health", auth)
    results["cors_allowed"] = request("GET", "/health", {**auth, "Origin": ALLOWED_ORIGIN})
    results["cors_evil"] = request("GET", "/health", {**auth, "Origin": EVIL_ORIGIN})
    results["preflight"] = request("OPTIONS", "/admin/bootstrap", {"Origin": ALLOWED_ORIGIN})
    results["malformed"] = request(
        "POST", "/admin/bootstrap", {**JSON, "X-Bootstrap-Secret": secret}, "{bad json"
    )
    return results


def test_routing_health_reachable(replay):
    """The launcher serves the front controller, so /health is routed (not a 404)."""
    status, _, _, _ = replay["health_noauth"]
    assert status == 401


def test_bootstrap_requires_secret(replay):
    """Bootstrap is refused (no token minted) without, or with a wrong, secret."""
    for key in ("boot_no_secret", "boot_wrong_secret"):
        status, _, _, body = replay[key]
        assert status in (401, 403), f"{key} returned {status}"
        assert not (body and "token" in body), f"{key} leaked a token"


def test_bootstrap_succeeds_with_secret(replay):
    """A first bootstrap carrying the correct secret mints an admin token."""
    status, _, _, body = replay["boot_ok"]
    assert status == 201
    assert body and isinstance(body.get("token"), str) and body["token"]


def test_bootstrap_is_one_time(replay):
    """A second bootstrap is refused (no new token) once an admin token exists."""
    status, _, _, body = replay["boot_repeat"]
    assert status in (403, 409), f"repeat bootstrap returned {status}"
    assert not (body and "token" in body), "repeat bootstrap leaked a token"


def test_token_file_not_world_readable(replay):
    """The bootstrapped admin token is stored with 0600 permissions."""
    assert replay["token"] is not None
    mode = stat.S_IMODE(os.stat(TOKEN_FILE).st_mode)
    assert mode == 0o600, f"token file mode is {oct(mode)}"


def test_token_stored_non_recoverable(replay):
    """The token file must not hand back a reusable credential if it is read.

    We only assert the raw bearer token is not recoverable from the file; the
    storage format is left to the implementation (sha256, bcrypt, argon2, ...).
    That /health still accepts the raw token is covered separately, which proves
    the stored value is a verifiable derivation rather than the token itself.
    """
    token = replay["token"]
    assert token is not None
    with open(TOKEN_FILE, encoding="utf-8") as handle:
        stored = handle.read().strip()
    assert stored, "token file is empty"
    assert token not in stored, "raw token is recoverable from the token file"


def test_health_requires_valid_token(replay):
    """/health returns ok only when given the bootstrapped bearer token."""
    assert replay["health_noauth"][0] == 401
    status, _, _, body = replay["health_ok"]
    assert status == 200 and body == {"status": "ok"}


def test_cors_limited_to_internal_origin(replay):
    """The internal origin gets an exact credentialed grant; other origins none."""
    _, allowed, _, _ = replay["cors_allowed"]
    assert header_ci(allowed, "Access-Control-Allow-Origin") == ALLOWED_ORIGIN
    assert header_ci(allowed, "Access-Control-Allow-Credentials") == "true"

    _, evil, _, _ = replay["cors_evil"]
    acao = header_ci(evil, "Access-Control-Allow-Origin")
    assert acao != "*" and acao != EVIL_ORIGIN
    assert header_ci(evil, "Access-Control-Allow-Credentials") is None


def test_preflight_scoped_to_internal_origin(replay):
    """An OPTIONS preflight returns 204 with the internal-origin credentialed grant."""
    status, headers, _, _ = replay["preflight"]
    assert status == 204
    assert header_ci(headers, "Access-Control-Allow-Origin") == ALLOWED_ORIGIN
    assert header_ci(headers, "Access-Control-Allow-Credentials") == "true"


def test_no_debug_details_leak(replay):
    """Malformed input yields a generic 400 with no debug trace or debug header."""
    status, headers, _, body = replay["malformed"]
    assert status == 400
    assert body is not None and "trace" not in body
    assert header_ci(headers, "X-Debug-Mode") is None


def test_audit_ledger_records_decisions(replay):
    """Bootstrap and health decisions are persisted in the SQLite audit ledger."""
    assert count_decisions("bootstrap", "accepted") == 1
    assert count_decisions("bootstrap", "denied") >= 3
    assert count_decisions("health", "accepted") >= 1
    assert count_decisions("health", "denied") >= 1
