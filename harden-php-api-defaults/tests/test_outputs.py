"""Behavioral verifier for the hardened, standard-reconciled HarborDesk API.

Two layers:
  * deterministic tests pin each individual control and Appendix G amendment;
  * a randomized property test replays many varied request lifecycles and checks
    every response and the resulting audit ledger against the hidden reference
    implementation of the resolved policy (helpers.simulate).

The reference (helpers.py) is mounted at verification time only; the agent must
derive the same behavior from the Standard.
"""

import random

import pytest

from helpers import (
    ALLOWED_ORIGINS,
    TOKEN_FILE,
    _State,
    audit_rows,
    audit_rows_with_origin,
    header_ci,
    make_sequence,
    read_secret,
    replay_request,
    request,
    reset_state,
    simulate,
)

RANDOM_CASES = 60
SEED = 91237  # fixed seed for reproducibility

ALLOWED = ALLOWED_ORIGINS[0]
ALLOWED2 = ALLOWED_ORIGINS[1]
JSON = {"Content-Type": "application/json"}


def _assert_response(exp, status, headers, raw, parsed):
    """Assert one captured response matches the reference expectation."""
    assert status == exp["status"], f"status {status} != {exp['status']}"

    # No internal disclosure, ever (EH-NO-DISCLOSE).
    assert header_ci(headers, "X-Debug-Mode") is None

    acao = header_ci(headers, "Access-Control-Allow-Origin")
    cred = header_ci(headers, "Access-Control-Allow-Credentials")
    if exp["cors"]:
        assert acao == exp["cors"]["Access-Control-Allow-Origin"]
        assert acao != "*"
        assert cred == "true"
        vary = header_ci(headers, "Vary")
        assert vary is not None and "origin" in vary.lower()
        if "Access-Control-Max-Age" in exp["cors"]:
            assert header_ci(headers, "Access-Control-Max-Age") == exp["cors"]["Access-Control-Max-Age"]
            assert header_ci(headers, "Access-Control-Allow-Methods") == exp["cors"]["Access-Control-Allow-Methods"]
            assert header_ci(headers, "Access-Control-Allow-Headers") == exp["cors"]["Access-Control-Allow-Headers"]
        else:
            # G-2026-11: preflight hints must not leak onto non-preflight responses.
            assert header_ci(headers, "Access-Control-Allow-Methods") is None
            assert header_ci(headers, "Access-Control-Allow-Headers") is None
            assert header_ci(headers, "Access-Control-Max-Age") is None
    else:
        assert acao is None, f"unexpected ACAO {acao!r}"
        assert cred is None, f"unexpected Allow-Credentials {cred!r}"

    body = exp["body"]
    if body == "ok":
        assert parsed == {"status": "ok"}
    elif body == "token":
        assert parsed and isinstance(parsed.get("token"), str) and parsed["token"]
    elif body == "error":
        assert parsed is not None and "trace" not in parsed
    elif body == "empty":
        assert raw == ""


# ---------------------------------------------------------------------------
# Deterministic scripted replay shared by the targeted tests.
# ---------------------------------------------------------------------------
@pytest.fixture(scope="session")
def scripted():
    """Reset state, replay a fixed sequence, and return captured responses."""
    reset_state()
    secret = read_secret()
    r = {}

    r["health_noauth"] = request("GET", "/health")
    r["boot_wrong"] = request("POST", "/admin/bootstrap", {**JSON, "X-Bootstrap-Secret": "nope"}, "{}")
    r["boot_nosecret"] = request("POST", "/admin/bootstrap", JSON, "{}")
    r["boot_malformed"] = request("POST", "/admin/bootstrap", {**JSON, "X-Bootstrap-Secret": secret}, "{bad json")
    r["boot_ok"] = request("POST", "/admin/bootstrap", {**JSON, "X-Bootstrap-Secret": secret}, "{}")

    status, _, _, body = r["boot_ok"]
    token = body["token"] if (status == 201 and body) else None
    r["token"] = token
    auth = {"Authorization": f"Bearer {token}"} if token else {}

    r["boot_repeat_ok"] = request("POST", "/admin/bootstrap", {**JSON, "X-Bootstrap-Secret": secret}, "{}")
    r["boot_repeat_wrong"] = request("POST", "/admin/bootstrap", {**JSON, "X-Bootstrap-Secret": "nope"}, "{}")
    r["health_ok"] = request("GET", "/health", auth)
    r["health_wrong"] = request("GET", "/health", {"Authorization": "Bearer bad"})
    r["cors_allowed"] = request("GET", "/health", {**auth, "Origin": ALLOWED})
    r["cors_allowed2"] = request("GET", "/health", {**auth, "Origin": ALLOWED2})
    r["cors_evil"] = request("GET", "/health", {**auth, "Origin": "https://evil.example"})
    r["cors_trailing_slash"] = request("GET", "/health", {**auth, "Origin": ALLOWED + "/"})
    r["preflight_allowed"] = request("OPTIONS", "/admin/bootstrap", {"Origin": ALLOWED})
    r["preflight_evil"] = request("OPTIONS", "/admin/bootstrap", {"Origin": "https://evil.example"})
    r["unknown"] = request("GET", "/nope")
    return r


def test_routing_health_reachable(scripted):
    """The launcher serves the front controller, so /health is routed (not 404)."""
    assert scripted["health_noauth"][0] == 401


def test_bootstrap_requires_secret(scripted):
    """Bootstrap is refused (no token) with a wrong or absent secret."""
    for key in ("boot_wrong", "boot_nosecret"):
        status, _, _, body = scripted[key]
        assert status == 403, f"{key} -> {status}"
        assert not (body and "token" in body)


def test_bootstrap_succeeds_with_secret(scripted):
    """A first bootstrap with the correct secret mints a token."""
    status, _, _, body = scripted["boot_ok"]
    assert status == 201
    assert body and isinstance(body.get("token"), str) and body["token"]


def test_bootstrap_already_bootstrapped_is_409(scripted):
    """G-2026-03: a repeat bootstrap is refused with 409 (not 403)."""
    status, _, _, body = scripted["boot_repeat_ok"]
    assert status == 409, f"repeat -> {status}"
    assert not (body and "token" in body)


def test_bootstrap_already_precedes_secret_check(scripted):
    """G-2026-05: an existing token yields 409 even with a wrong secret."""
    status, _, _, _ = scripted["boot_repeat_wrong"]
    assert status == 409, f"repeat-wrong-secret -> {status}"


def test_token_file_not_world_readable(scripted):
    """AC-TOKEN-STORE: the token file is mode 0600."""
    import os
    import stat

    assert scripted["token"] is not None
    mode = stat.S_IMODE(os.stat(TOKEN_FILE).st_mode)
    assert mode == 0o600, f"token file mode {oct(mode)}"


def test_token_stored_non_recoverable(scripted):
    """AC-TOKEN-STORE: the raw bearer token is not recoverable from the file."""
    token = scripted["token"]
    assert token is not None
    with open(TOKEN_FILE, encoding="utf-8") as fh:
        stored = fh.read().strip()
    assert stored and token not in stored


def test_cors_grant_follows_current_request(scripted):
    """CO-ORIGIN-ALLOW: each request's Origin header governs the credentialed grant."""
    token = scripted["token"]
    assert token is not None
    auth = {"Authorization": f"Bearer {token}"}

    _, headers_a, _, _ = request("GET", "/health", {**auth, "Origin": ALLOWED})
    assert header_ci(headers_a, "Access-Control-Allow-Origin") == ALLOWED

    _, headers_b, _, _ = request("GET", "/health", {**auth, "Origin": ALLOWED2})
    assert header_ci(headers_b, "Access-Control-Allow-Origin") == ALLOWED2

    _, headers_none, _, _ = request(
        "GET", "/health", {**auth, "Origin": "https://evil.example"}
    )
    assert header_ci(headers_none, "Access-Control-Allow-Origin") is None


def test_bootstrap_eligibility_follows_token_file(scripted):
    """AC-BOOTSTRAP: bootstrap eligibility follows the on-disk token file, not caches."""
    import os

    secret = read_secret()
    assert scripted["token"] is not None
    os.remove(TOKEN_FILE)

    status, _, _, body = request(
        "POST",
        "/admin/bootstrap",
        {**JSON, "X-Bootstrap-Secret": secret},
        "{}",
    )
    assert status == 201, f"expected fresh bootstrap after token removal, got {status}"
    assert body and body.get("token")


def test_health_requires_valid_token(scripted):
    """AC-HEALTH: ok only for the bootstrapped token; others refused."""
    assert scripted["health_noauth"][0] == 401
    assert scripted["health_wrong"][0] == 401
    status, _, _, body = scripted["health_ok"]
    assert status == 200 and body == {"status": "ok"}


def test_cors_exact_allowlist(scripted):
    """CO-ORIGIN-ALLOW + G-2026-01: both internal origins get an exact grant."""
    for key, origin in (("cors_allowed", ALLOWED), ("cors_allowed2", ALLOWED2)):
        _, headers, _, _ = scripted[key]
        assert header_ci(headers, "Access-Control-Allow-Origin") == origin
        assert header_ci(headers, "Access-Control-Allow-Credentials") == "true"
        vary = header_ci(headers, "Vary")
        assert vary is not None and "origin" in vary.lower()
        assert header_ci(headers, "Access-Control-Allow-Methods") is None
        assert header_ci(headers, "Access-Control-Allow-Headers") is None


def test_cors_rejects_untrusted_and_inexact(scripted):
    """Disallowed origins and exact-match traps receive no grant."""
    for key in ("cors_evil", "cors_trailing_slash"):
        _, headers, _, _ = scripted[key]
        acao = header_ci(headers, "Access-Control-Allow-Origin")
        assert acao is None, f"{key} leaked ACAO {acao!r}"
        assert header_ci(headers, "Access-Control-Allow-Credentials") is None


def test_preflight_scoped_and_max_age(scripted):
    """CO-PREFLIGHT + G-2026-02: allowed preflight is 204 with Max-Age 300."""
    status, headers, _, _ = scripted["preflight_allowed"]
    assert status == 204
    assert header_ci(headers, "Access-Control-Allow-Origin") == ALLOWED
    assert header_ci(headers, "Access-Control-Max-Age") == "300"
    assert header_ci(headers, "Access-Control-Allow-Methods") == "GET, POST, OPTIONS"

    status, headers, _, _ = scripted["preflight_evil"]
    assert status == 204
    assert header_ci(headers, "Access-Control-Allow-Origin") is None
    assert header_ci(headers, "Access-Control-Max-Age") is None


def test_no_debug_details_leak(scripted):
    """EH-NO-DISCLOSE: malformed input is a generic 400, no trace/header."""
    status, headers, _, body = scripted["boot_malformed"]
    assert status == 400
    assert body is not None and "trace" not in body
    assert header_ci(headers, "X-Debug-Mode") is None


def test_health_missing_reason_renamed(scripted):
    """G-2026-04: a no-credential health denial is logged 'missing_credentials'."""
    rows = audit_rows()
    reasons = {r["reason"] for r in rows if r["event"] == "health" and r["decision"] == "denied"}
    assert "missing_credentials" in reasons
    assert "missing_token" not in reasons


def test_audit_history_preserved(scripted):
    """AU-LEDGER-SCOPE: legacy historical rows survive the schema migration."""
    rows = audit_rows()
    preserved = [r for r in rows if r["reason"] == "legacy_history"]
    assert len(preserved) == 2, f"expected 2 legacy rows, found {len(preserved)}"


def test_audit_records_origin(scripted):
    """G-2026-06: the migrated ledger records the request origin on rows."""
    rows = audit_rows_with_origin()
    matching = [r for r in rows if r.get("origin") == ALLOWED]
    assert matching, "no audited row recorded the allowed origin"


def test_randomized_lifecycles_match_reference():
    """Replay many randomized lifecycles; every response and ledger row must
    match the resolved-policy reference (helpers.simulate)."""
    rng = random.Random(SEED)
    secret = read_secret()

    for case in range(RANDOM_CASES):
        reset_state()
        state = _State()
        token = None
        expected_audit = []

        seq = make_sequence(rng)
        for i, req in enumerate(seq):
            exp = simulate(state, req)
            status, headers, raw, parsed = replay_request(req, secret, token)
            try:
                _assert_response(exp, status, headers, raw, parsed)
            except AssertionError as err:
                raise AssertionError(f"case {case} req {i} {req}: {err}") from err
            if exp["body"] == "token" and parsed:
                token = parsed["token"]
            if exp["audit"] is not None:
                expected_audit.append(exp["audit"])

        rows = audit_rows_with_origin()
        history = [r for r in rows if r["reason"] == "legacy_history"]
        assert len(history) == 2, f"case {case}: legacy history not preserved"

        audited = [r for r in rows if r["reason"] != "legacy_history"]
        assert len(audited) == len(expected_audit), (
            f"case {case}: {len(audited)} audited rows != {len(expected_audit)} expected"
        )
        for got, exp in zip(audited, expected_audit):
            ev, route, origin, decision, reason = exp
            assert got["event"] == ev and got["route"] == route, f"case {case}: {got} vs {exp}"
            assert got["decision"] == decision and got["reason"] == reason, f"case {case}: {got} vs {exp}"
            assert got["origin"] == origin, f"case {case}: origin {got['origin']!r} vs {origin!r}"
