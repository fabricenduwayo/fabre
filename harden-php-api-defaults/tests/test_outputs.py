"""Behavioral verifier for the amended HarborDesk API and credential lifecycle."""

import json
import os
import random
import sqlite3
import stat
from concurrent.futures import ThreadPoolExecutor

from helpers import (
    ALLOWED_ORIGINS,
    AUDIT_DB,
    INITIAL_GENERATION,
    ORIGINS_FILE,
    PREDECESSOR_USES,
    SECRET_FILE,
    TOKEN_FILE,
    State,
    audit_rows,
    bootstrap,
    header_ci,
    health,
    make_sequence,
    read_secret,
    replay,
    request,
    reset_state,
    set_generation,
    shadow_audit_rows,
    simulate,
)

ALLOWED = ALLOWED_ORIGINS[0]
ALLOWED_2 = ALLOWED_ORIGINS[1]
SEED = 73619
RANDOM_CASES = 45


def bootstrap_ok(secret=None, origin=None):
    """Mint a token and assert the stable bootstrap response shape."""
    response = bootstrap(secret or read_secret(), origin=origin)
    assert response[0] == 201
    assert response[3] and isinstance(response[3].get("token"), str)
    return response[3]["token"]


def activate_pending(current, pending):
    """Sponsor and confirm a staged successor from both allowed origins."""
    assert health(current, ALLOWED)[0] == 200
    first = health(pending, ALLOWED)
    assert health(current, ALLOWED_2)[0] == 200
    second = health(pending, ALLOWED_2)
    assert first[0] == second[0] == 200
    return first, second


def assert_cors(headers, origin=None, preflight=False):
    """Assert the resolved CORS grant for one response."""
    if origin in ALLOWED_ORIGINS:
        assert header_ci(headers, "Access-Control-Allow-Origin") == origin
        assert header_ci(headers, "Access-Control-Allow-Credentials") == "true"
        assert "origin" in header_ci(headers, "Vary").lower()
        if preflight:
            assert header_ci(headers, "Access-Control-Allow-Methods") == (
                "GET, POST, OPTIONS"
            )
            assert header_ci(headers, "Access-Control-Allow-Headers") == (
                "Authorization, Content-Type, X-Bootstrap-Secret"
            )
            assert header_ci(headers, "Access-Control-Max-Age") == "300"
        else:
            assert header_ci(headers, "Access-Control-Allow-Methods") is None
            assert header_ci(headers, "Access-Control-Allow-Headers") is None
            assert header_ci(headers, "Access-Control-Max-Age") is None
    else:
        assert header_ci(headers, "Access-Control-Allow-Origin") is None
        assert header_ci(headers, "Access-Control-Allow-Credentials") is None
        vary = header_ci(headers, "Vary")
        assert vary is None or "origin" not in vary.lower()
        assert header_ci(headers, "Access-Control-Allow-Methods") is None
        assert header_ci(headers, "Access-Control-Allow-Headers") is None
        assert header_ci(headers, "Access-Control-Max-Age") is None


def assert_expected(expected, actual):
    """Compare one real response with the resolved reference response."""
    status, headers, raw, parsed = actual
    assert status == expected["status"]
    assert header_ci(headers, "X-Debug-Mode") is None
    assert_cors(headers, expected["cors"].get("Access-Control-Allow-Origin"), status == 204)
    if expected["body"] == "empty":
        assert raw == ""
    elif expected["body"] == "ok":
        assert parsed == {"status": "ok"}
    elif expected["body"] == "token":
        assert parsed and isinstance(parsed.get("token"), str)
    else:
        assert parsed and set(parsed) == {"error"}


def test_options_preflight_creates_no_audit_row():
    """OPTIONS preflights are outside AU-LEDGER-SCOPE."""
    reset_state()
    bootstrap_ok()
    before = len(audit_rows())
    status, headers, raw, _ = request("OPTIONS", "/anything", {"Origin": ALLOWED_2})
    assert status == 204 and raw == ""
    assert_cors(headers, ALLOWED_2, preflight=True)
    assert len(audit_rows()) == before


def test_stale_pending_denied_when_generation_advances_again():
    """A generation advance fences an unfinished successor before replacement."""
    reset_state()
    current = bootstrap_ok()
    set_generation(INITIAL_GENERATION + 1)
    pending = bootstrap_ok()
    assert health(current, ALLOWED)[0] == 200
    assert health(pending, ALLOWED)[0] == 200
    set_generation(INITIAL_GENERATION + 2)
    assert health(pending, ALLOWED)[0] == 401
    assert health(pending, ALLOWED_2)[0] == 401
    assert health(current)[0] == 200
    assert bootstrap("wrong")[0] == 403
    replacement = bootstrap_ok()
    assert health(replacement, ALLOWED)[0] == 401
    assert health(current, ALLOWED)[0] == 200
    assert health(replacement, ALLOWED)[0] == 200


def test_cors_preflight_and_no_disclosure():
    """Amended CORS is request-scoped and errors disclose no debug details."""
    reset_state()
    token = bootstrap_ok()
    for origin in ALLOWED_ORIGINS:
        status, headers, _, body = health(token, origin)
        assert status == 200 and body == {"status": "ok"}
        assert_cors(headers, origin)

    _, evil_headers, _, _ = health(token, "https://evil.example")
    assert_cors(evil_headers, "https://evil.example")
    _, absent_headers, _, _ = health(token)
    assert_cors(absent_headers)

    status, headers, raw, _ = request(
        "OPTIONS", "/anything", {"Origin": ALLOWED_2}
    )
    assert status == 204 and raw == ""
    assert_cors(headers, ALLOWED_2, preflight=True)
    status, headers, raw, _ = request(
        "OPTIONS", "/anything", {"Origin": "https://evil.example"}
    )
    assert status == 204 and raw == ""
    assert_cors(headers, "https://evil.example", preflight=True)

    status, headers, _, body = bootstrap(read_secret(), body="{bad json")
    assert status == 400 and body == {"error": "bad request"}
    assert header_ci(headers, "X-Debug-Mode") is None
    assert "trace" not in body


def test_bootstrap_order_secret_normalization_and_repeat():
    """Bootstrap normalizes the live secret and checks active state before it."""
    reset_state()
    secret = read_secret()
    assert bootstrap("wrong")[0] == 403
    mixed = f"  {secret.swapcase()}  "
    token = bootstrap_ok(mixed)
    assert token
    assert bootstrap("wrong")[0] == 409
    rows = [row for row in audit_rows() if row["reason"] != "legacy_history"]
    assert [row["reason"] for row in rows] == [
        "invalid_secret",
        None,
        "already_bootstrapped",
    ]


def test_secret_and_generation_are_live_deployment_inputs():
    """Secret replacement and generation advance take effect without restart."""
    reset_state()
    original = read_secret()
    first = bootstrap_ok(original)
    replacement = "hd-rotated-secret-4B9a"
    with open(SECRET_FILE, "w", encoding="utf-8") as handle:
        handle.write(replacement + "\n")
    set_generation(INITIAL_GENERATION + 4)
    assert bootstrap(original)[0] == 403
    second = bootstrap_ok(replacement.swapcase())
    assert second != first
    assert health(second)[0] == 401
    assert health(first)[0] == 200
    activate_pending(first, second)
    assert health(second)[0] == 200
    with open(SECRET_FILE, "w", encoding="utf-8") as handle:
        handle.write(original + "\n")


def test_token_state_is_nonrecoverable_and_owner_only():
    """Persisted current and predecessor state contains no raw bearer token."""
    reset_state()
    first = bootstrap_ok()
    set_generation(INITIAL_GENERATION + 1)
    second = bootstrap_ok()
    with open(TOKEN_FILE, encoding="utf-8") as handle:
        stored = handle.read()
    assert first not in stored
    assert second not in stored
    assert read_secret() not in stored
    assert len(json.loads(stored)["pending_secret_digest"]) == 64
    assert stat.S_IMODE(os.stat(TOKEN_FILE).st_mode) == 0o600


def test_health_reasons_and_origin_audit():
    """Health classifies credentials and audits the allowlist-resolved origin."""
    reset_state()
    token = bootstrap_ok()
    assert health(authorization="Basic dXNlcjpwYXNz")[0] == 401
    assert health(authorization="Bearer ")[0] == 401
    assert health("wrong", ALLOWED)[0] == 401
    assert health(token, "https://evil.example")[0] == 200
    assert health(token, ALLOWED_2)[0] == 200
    rows = [
        row
        for row in audit_rows()
        if row["event"] == "health" and row["reason"] != "legacy_history"
    ]
    assert [(row["decision"], row["reason"]) for row in rows] == [
        ("denied", "missing_credentials"),
        ("denied", "missing_credentials"),
        ("denied", "invalid_token"),
        ("accepted", None),
        ("accepted", None),
    ]
    assert rows[0]["origin"] is None
    assert rows[2]["origin"] == ALLOWED
    assert rows[3]["origin"] is None
    assert rows[-1]["origin"] == ALLOWED_2


def test_legacy_ledger_reconciles_in_place_and_ignores_shadow():
    """Each audited write preserves legacy ids and appends only to audit_log."""
    reset_state()
    shadow_before = shadow_audit_rows()
    bootstrap_ok(origin=ALLOWED)
    rows = audit_rows()
    history = [row for row in rows if row["reason"] == "legacy_history"]
    assert {row["id"] for row in history} == {1, 2}
    assert all(row["origin"] is None for row in history)
    assert len(rows) == 3
    assert shadow_audit_rows() == shadow_before
    conn = sqlite3.connect(AUDIT_DB)
    try:
        columns = [row[1] for row in conn.execute("PRAGMA table_info(audit_log)")]
    finally:
        conn.close()
    assert "origin" in columns and "actor" not in columns


def test_ledger_reconciliation_repeats_after_live_reseed():
    """A legacy reseed during service life is migrated before the next write."""
    reset_state()
    bootstrap_ok()
    reset_state()
    bootstrap_ok()
    rows = audit_rows()
    assert {row["id"] for row in rows if row["reason"] == "legacy_history"} == {1, 2}
    assert len([row for row in rows if row["reason"] != "legacy_history"]) == 1


def test_generation_advance_requires_secret_before_cutover():
    """An advance opens rotation but does not bypass current secret validation."""
    reset_state()
    old = bootstrap_ok()
    set_generation(INITIAL_GENERATION + 3)
    assert bootstrap("wrong")[0] == 403
    assert health(old)[0] == 200
    new = bootstrap_ok()
    assert new != old
    assert health(new)[0] == 401
    assert health(old)[0] == 200
    activate_pending(old, new)
    assert health(new)[0] == 200


def test_pre_staging_sponsorship_does_not_authorize_confirmation():
    """Current-token origin visits count only after the successor is staged."""
    reset_state()
    current = bootstrap_ok()
    assert health(current, ALLOWED)[0] == 200
    assert health(current, ALLOWED_2)[0] == 200

    set_generation(INITIAL_GENERATION + 1)
    pending = bootstrap_ok()
    assert health(pending, ALLOWED)[0] == 401
    assert health(pending, ALLOWED_2)[0] == 401
    activate_pending(current, pending)
    assert health(pending)[0] == 200


def test_second_origin_requires_phase_fresh_sponsorship():
    """First confirmation voids earlier sponsorship for unconfirmed origins."""
    reset_state()
    current = bootstrap_ok()
    set_generation(INITIAL_GENERATION + 1)
    pending = bootstrap_ok()
    assert health(current, ALLOWED)[0] == 200
    assert health(current, ALLOWED_2)[0] == 200
    assert health(pending, ALLOWED)[0] == 200
    assert health(pending, ALLOWED_2)[0] == 401
    assert health(current, ALLOWED_2)[0] == 200
    assert health(pending, ALLOWED_2)[0] == 200
    assert health(pending)[0] == 200


def test_secret_rotation_clears_inflight_cutover_progress():
    """A live secret change clears confirmations and sponsorships under lock."""
    reset_state()
    original = read_secret()
    current = bootstrap_ok(original)
    set_generation(INITIAL_GENERATION + 1)
    pending = bootstrap_ok(original)
    assert health(current, ALLOWED)[0] == 200
    assert health(pending, ALLOWED)[0] == 200
    assert health(current, ALLOWED_2)[0] == 200

    rotated = "hd-cutover-rotated-7f19"
    try:
        with open(SECRET_FILE, "w", encoding="utf-8") as handle:
            handle.write(rotated + "\n")
        assert health(pending, ALLOWED_2)[0] == 401
        assert health(current, ALLOWED_2)[0] == 200
        assert health(pending, ALLOWED_2)[0] == 200
        assert health(pending)[0] == 401
        assert health(current, ALLOWED)[0] == 200
        assert health(pending, ALLOWED)[0] == 200
        assert health(pending)[0] == 200
    finally:
        with open(SECRET_FILE, "w", encoding="utf-8") as handle:
            handle.write(original + "\n")


def test_failed_audit_append_cannot_publish_health_state():
    """Audit failure preserves sponsorship and predecessor allowances."""
    reset_state()
    current = bootstrap_ok()
    set_generation(INITIAL_GENERATION + 1)
    pending = bootstrap_ok()

    def set_failure_trigger(enabled):
        conn = sqlite3.connect(AUDIT_DB, timeout=10)
        try:
            conn.execute("DROP TRIGGER IF EXISTS fail_health_audit")
            if enabled:
                conn.execute(
                    "CREATE TRIGGER fail_health_audit "
                    "BEFORE INSERT ON audit_log WHEN NEW.event = 'health' "
                    "BEGIN SELECT RAISE(ABORT, 'blocked'); END"
                )
            conn.commit()
        finally:
            conn.close()

    set_failure_trigger(True)
    try:
        assert health(current, ALLOWED)[0] == 500
    finally:
        set_failure_trigger(False)
    assert health(pending, ALLOWED)[0] == 401
    assert health(current, ALLOWED)[0] == 200

    set_failure_trigger(True)
    try:
        assert health(pending, ALLOWED)[0] == 500
    finally:
        set_failure_trigger(False)
    assert health(current, ALLOWED_2)[0] == 200
    assert health(pending, ALLOWED)[0] == 200
    assert health(pending, ALLOWED_2)[0] == 401
    assert health(current, ALLOWED_2)[0] == 200

    set_failure_trigger(True)
    try:
        assert health(pending, ALLOWED_2)[0] == 500
    finally:
        set_failure_trigger(False)
    assert health(pending, ALLOWED_2)[0] == 200
    assert audit_rows()[-1]["reason"] == "cutover_activated"

    set_failure_trigger(True)
    try:
        assert health(current, ALLOWED)[0] == 500
    finally:
        set_failure_trigger(False)
    assert health(current, ALLOWED)[0] == 200
    assert health(current, ALLOWED)[0] == 401


def test_pending_successor_requires_two_distinct_allowed_origins():
    """Each origin needs incumbent sponsorship before it can confirm a successor."""
    reset_state()
    current = bootstrap_ok()
    set_generation(INITIAL_GENERATION + 1)
    pending = bootstrap_ok()

    assert health(pending)[0] == 401
    assert health(pending, "https://evil.example")[0] == 401
    assert health(pending, ALLOWED)[0] == 401
    assert health(current, ALLOWED)[0] == 200
    assert health(pending, ALLOWED)[0] == 200
    assert health(pending, ALLOWED)[0] == 200
    assert health(current)[0] == 200
    assert health(pending, ALLOWED_2)[0] == 401
    assert health(current, ALLOWED_2)[0] == 200
    assert health(pending, ALLOWED_2)[0] == 200
    assert health(pending)[0] == 200
    assert [
        health(current, ALLOWED)[0],
        health(current, ALLOWED)[0],
        health(current, ALLOWED_2)[0],
        health(current, ALLOWED_2)[0],
    ] == [200, 401, 200, 401]

    reasons = [
        row["reason"]
        for row in audit_rows()
        if row["event"] == "health" and row["reason"] != "legacy_history"
    ]
    assert reasons == [
        "invalid_token",
        "invalid_token",
        "invalid_token",
        None,
        "cutover_confirmation",
        "cutover_confirmation",
        None,
        "invalid_token",
        None,
        "cutover_activated",
        None,
        "predecessor_overlap",
        "invalid_token",
        "predecessor_overlap",
        "invalid_token",
    ]


def test_invalid_token_denial_revokes_same_origin_sponsorship():
    """An allowed-origin invalid token fences only that origin's sponsorship."""
    reset_state()
    current = bootstrap_ok()
    set_generation(INITIAL_GENERATION + 1)
    pending = bootstrap_ok()

    assert health(current, ALLOWED)[0] == 200
    assert health(current, ALLOWED_2)[0] == 200
    assert health("invalid-after-sponsorship", ALLOWED)[0] == 401
    assert health(pending, ALLOWED)[0] == 401
    assert health(pending, ALLOWED_2)[0] == 200
    assert health(current, ALLOWED)[0] == 200
    assert health(pending, ALLOWED)[0] == 200
    assert audit_rows()[-1]["reason"] == "cutover_activated"


def test_higher_generation_replaces_only_unfinished_successor():
    """A replacement clears old sponsorship and confirmation state."""
    reset_state()
    current = bootstrap_ok()
    set_generation(INITIAL_GENERATION + 1)
    abandoned = bootstrap_ok()
    assert health(abandoned, ALLOWED)[0] == 401
    assert health(current, ALLOWED)[0] == 200
    assert health(abandoned, ALLOWED)[0] == 200

    set_generation(INITIAL_GENERATION + 2)
    assert bootstrap("wrong")[0] == 403
    successor = bootstrap_ok()
    assert health(abandoned, ALLOWED_2)[0] == 401
    assert health(current)[0] == 200
    assert health(successor, ALLOWED)[0] == 401
    assert health(current, ALLOWED)[0] == 200
    assert health(successor, ALLOWED)[0] == 200
    assert health(current, ALLOWED_2)[0] == 200
    assert health(successor, ALLOWED_2)[0] == 200
    assert [
        health(current, ALLOWED)[0],
        health(current, ALLOWED)[0],
        health(current, ALLOWED_2)[0],
        health(current, ALLOWED_2)[0],
    ] == [200, 401, 200, 401]


def test_pending_activation_is_atomic_across_workers():
    """Concurrent confirmations perform one activation and one predecessor handoff."""
    reset_state()
    current = bootstrap_ok()
    set_generation(INITIAL_GENERATION + 1)
    pending = bootstrap_ok()
    assert health(current, ALLOWED)[0] == 200
    assert health(current, ALLOWED_2)[0] == 200
    assert health(pending, ALLOWED)[0] == 200
    assert health(pending, ALLOWED_2)[0] == 401
    assert health(current, ALLOWED_2)[0] == 200
    before = len(audit_rows())

    origins = [ALLOWED_2] * 12
    with ThreadPoolExecutor(max_workers=12) as pool:
        statuses = list(pool.map(lambda origin: health(pending, origin)[0], origins))
    assert statuses == [200] * len(origins)

    rows = [
        row
        for row in audit_rows()[before:]
        if row["event"] == "health"
    ]
    reasons = [row["reason"] for row in rows]
    assert reasons.count("cutover_activated") == 1
    assert set(reasons) <= {None, "cutover_activated"}
    assert [
        health(current, ALLOWED)[0],
        health(current, ALLOWED)[0],
        health(current, ALLOWED_2)[0],
        health(current, ALLOWED_2)[0],
    ] == [200, 401, 200, 401]


def test_predecessor_overlap_is_partitioned_by_allowed_origin():
    """Predecessor overlap grants one atomic acceptance per allowed origin."""
    reset_state()
    old = bootstrap_ok()
    set_generation(INITIAL_GENERATION + 1)
    current = bootstrap_ok()
    assert health(current)[0] == 401
    activate_pending(old, current)
    assert health(current)[0] == 200
    assert health(old)[0] == 401
    assert health(old, "https://evil.example")[0] == 401
    assert health(old, ALLOWED)[0] == 200
    assert health(old, ALLOWED)[0] == 401
    assert health(current)[0] == 200
    assert health(old, ALLOWED_2)[0] == 200
    assert health(old, ALLOWED_2)[0] == 401
    assert health(current)[0] == 200
    reasons = [
        (row["decision"], row["reason"])
        for row in audit_rows()
        if row["event"] == "health" and row["reason"] != "legacy_history"
    ]
    assert reasons == [
        ("denied", "invalid_token"),
        ("accepted", None),
        ("accepted", "cutover_confirmation"),
        ("accepted", None),
        ("accepted", "cutover_activated"),
        ("accepted", None),
        ("denied", "invalid_token"),
        ("denied", "invalid_token"),
        ("accepted", "predecessor_overlap"),
        ("denied", "invalid_token"),
        ("accepted", None),
        ("accepted", "predecessor_overlap"),
        ("denied", "invalid_token"),
        ("accepted", None),
    ]


def test_invalid_health_does_not_consume_predecessor_overlap():
    """Untrusted requests leave both origin-partitioned allowances intact."""
    reset_state()
    old = bootstrap_ok()
    set_generation(INITIAL_GENERATION + 1)
    pending = bootstrap_ok()
    activate_pending(old, pending)
    for _ in range(4):
        assert health("wrong")[0] == 401
        assert health()[0] == 401
    assert health(old)[0] == 401
    assert health(old, "https://evil.example")[0] == 401
    assert [
        health(old, ALLOWED)[0],
        health(old, ALLOWED_2)[0],
        health(old, ALLOWED)[0],
        health(old, ALLOWED_2)[0],
    ] == [200, 200, 401, 401]


def test_later_cutover_replaces_unspent_predecessor():
    """A second cutover discards the older predecessor and resets overlap."""
    reset_state()
    oldest = bootstrap_ok()
    set_generation(INITIAL_GENERATION + 1)
    middle = bootstrap_ok()
    activate_pending(oldest, middle)
    assert health(oldest, ALLOWED)[0] == 200
    set_generation(INITIAL_GENERATION + 8)
    newest = bootstrap_ok()
    assert health(middle)[0] == 200
    activate_pending(middle, newest)
    assert health(oldest, ALLOWED_2)[0] == 401
    assert [
        health(middle, ALLOWED)[0],
        health(middle, ALLOWED_2)[0],
        health(middle, ALLOWED)[0],
        health(middle, ALLOWED_2)[0],
    ] == [200, 200, 401, 401]
    assert health(newest)[0] == 200


def test_predecessor_budget_is_atomic_across_workers():
    """Concurrent predecessor calls collectively receive exactly two accepts."""
    reset_state()
    old = bootstrap_ok()
    set_generation(INITIAL_GENERATION + 1)
    pending = bootstrap_ok()
    activate_pending(old, pending)
    before = len(audit_rows())
    origins = [ALLOWED] * 5 + [ALLOWED_2] * 5
    with ThreadPoolExecutor(max_workers=10) as pool:
        statuses = list(pool.map(lambda origin: health(old, origin)[0], origins))
    assert statuses.count(200) == PREDECESSOR_USES
    assert statuses.count(401) == 10 - PREDECESSOR_USES
    lifecycle_rows = [
        row
        for row in audit_rows()[before:]
        if row["event"] == "health"
    ]
    accepted = [row for row in lifecycle_rows if row["decision"] == "accepted"]
    assert len(accepted) == 2
    assert all(row["reason"] == "predecessor_overlap" for row in accepted)
    assert len(lifecycle_rows) == 10


def test_corrupt_existing_state_blocks_bootstrap_and_health():
    """Malformed state hard-blocks bootstrap before generation and secret checks."""
    reset_state()
    with open(TOKEN_FILE, "w", encoding="utf-8") as handle:
        handle.write("not-valid-credential-state\n")
    os.chmod(TOKEN_FILE, 0o600)
    set_generation(INITIAL_GENERATION + 100)
    assert bootstrap("wrong")[0] == 409
    assert bootstrap(read_secret())[0] == 409
    assert health("anything")[0] == 401


def test_decoy_origin_file_never_changes_policy():
    """The legacy origins input cannot add grants or remove amended origins."""
    reset_state()
    with open(ORIGINS_FILE, "w", encoding="utf-8") as handle:
        handle.write("https://evil.example\n")
    token = bootstrap_ok()
    assert_cors(health(token, ALLOWED_2)[1], ALLOWED_2)
    assert_cors(health(token, "https://evil.example")[1], "https://evil.example")


def test_randomized_lifecycles_match_resolved_policy():
    """Varied cutovers match the hidden response and ledger state machine."""
    rng = random.Random(SEED)
    secret = read_secret()
    for case in range(RANDOM_CASES):
        reset_state()
        state = State()
        tokens = {}
        expected_audit = []
        for index, operation in enumerate(make_sequence(rng)):
            expected = simulate(state, operation)
            if operation["kind"] in {"advance", "rotate_secret"}:
                replay(operation, secret, tokens)
                continue
            actual = replay(operation, secret, tokens)
            try:
                assert_expected(expected, actual)
            except AssertionError as error:
                raise AssertionError(
                    f"case {case} operation {index} {operation}: {error}"
                ) from error
            if expected["body"] == "token":
                tokens[operation["mint"]] = actual[3]["token"]
            if expected["audit"] is not None:
                expected_audit.append(expected["audit"])

        rows = audit_rows()
        history = [row for row in rows if row["reason"] == "legacy_history"]
        assert len(history) == 2
        actual_audit = [row for row in rows if row["reason"] != "legacy_history"]
        assert len(actual_audit) == len(expected_audit), f"case {case}"
        for row, expected_row in zip(actual_audit, expected_audit):
            event, route, origin, decision, reason = expected_row
            assert (
                row["event"],
                row["route"],
                row["origin"],
                row["decision"],
                row["reason"],
            ) == (event, route, origin, decision, reason)
