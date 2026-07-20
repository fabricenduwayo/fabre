"""Verifier tests for repair-java-release-attestation-worker.

The suite checks attestation_reports against the policy using the live
artifact-metadata API and reruns the agent-built worker on variant H2 stores
to confirm reports are derived by the program, not hand-written.
"""

from __future__ import annotations

from pathlib import Path

from helpers import (
    MAIN_DB_URL,
    REASON_BAD_SIG,
    REASON_REVOKED,
    REASON_UNKNOWN,
    REASON_VERIFIED,
    REASON_VERIFY_DEGRADED,
    VERDICT_DENIED,
    VERDICT_QUARANTINE,
    VERDICT_TRUSTED,
    api_healthy,
    clone_main_database,
    expected_reports_for_db,
    http_get_json,
    http_post_verify,
    load_evidence,
    load_reports,
    run_attest_worker,
    run_h2_script,
)

TESTS_DIR = Path(__file__).resolve().parent


def test_api_serves_health() -> None:
    """The bundled artifact-metadata API answers /health on port 8080."""
    assert api_healthy(), "artifact-metadata API /health is not answering"


def test_reports_cover_every_pending_artifact(pending_ids, shipped_reports) -> None:
    """Every pending artifact has exactly one attestation report."""
    assert set(shipped_reports) == set(pending_ids), (
        f"reports {sorted(shipped_reports)} do not match pending {sorted(pending_ids)}"
    )


def test_shipped_reports_match_policy(expected_shipped, shipped_reports) -> None:
    """Shipped reports match the policy table for each pending artifact."""
    for artifact_id, expected in expected_shipped.items():
        actual = shipped_reports[artifact_id]
        assert actual.verdict == expected.verdict, (
            f"{artifact_id}: verdict {actual.verdict!r}, expected {expected.verdict!r}"
        )
        assert actual.reason_code == expected.reason_code, (
            f"{artifact_id}: reason {actual.reason_code!r}, "
            f"expected {expected.reason_code!r}"
        )


def test_trusted_artifact_verified(shipped_reports) -> None:
    """art-alpha passes detached-signature verify with the H2 digest."""
    row = shipped_reports["art-alpha"]
    assert row.verdict == VERDICT_TRUSTED
    assert row.reason_code == REASON_VERIFIED


def test_beta_trusted_when_verify_uses_h2_digest(shipped_reports) -> None:
    """art-beta is trusted when verify uses the H2 digest despite a stale registry_digest."""
    row = shipped_reports["art-beta"]
    assert row.verdict == VERDICT_TRUSTED
    assert row.reason_code == REASON_VERIFIED


def test_revoked_signer_denied_before_verify(shipped_reports) -> None:
    """art-gamma is denied from H2 revocation without trusting registry metadata."""
    row = shipped_reports["art-gamma"]
    assert row.verdict == VERDICT_DENIED
    assert row.reason_code == REASON_REVOKED


def test_bad_signature_denied(shipped_reports) -> None:
    """art-delta is denied when POST /verify rejects the detached signature."""
    row = shipped_reports["art-delta"]
    assert row.verdict == VERDICT_DENIED
    assert row.reason_code == REASON_BAD_SIG


def test_verify_degraded_quarantines(shipped_reports) -> None:
    """art-epsilon is quarantined when POST /verify returns 503."""
    row = shipped_reports["art-epsilon"]
    assert row.verdict == VERDICT_QUARANTINE
    assert row.reason_code == REASON_VERIFY_DEGRADED


def test_worker_reruns_on_unknown_artifact_variant() -> None:
    """The worker denies unknown artifacts when rerun against a fresh pending row."""
    db_url = clone_main_database()
    run_h2_script(db_url, TESTS_DIR / "variant_unknown_seed.sql")
    result = run_attest_worker(db_url)
    assert result.returncode == 0, result.stderr
    expected = expected_reports_for_db(db_url)
    reports = load_reports(db_url)
    assert reports["art-probe"].verdict == VERDICT_DENIED
    assert reports["art-probe"].reason_code == REASON_UNKNOWN
    assert reports["art-probe"].verdict == expected["art-probe"].verdict


def test_worker_reruns_on_live_variant() -> None:
    """The worker trusts a variant artifact when H2 digest and verify both succeed."""
    db_url = clone_main_database()
    run_h2_script(db_url, TESTS_DIR / "variant_live_seed.sql")
    result = run_attest_worker(db_url)
    assert result.returncode == 0, result.stderr
    reports = load_reports(db_url)
    assert reports["art-live"].verdict == VERDICT_TRUSTED
    assert reports["art-live"].reason_code == REASON_VERIFIED


def test_registry_digest_alone_is_insufficient() -> None:
    """POST /verify with only the registry digest does not satisfy art-beta policy."""
    evidence = load_evidence(MAIN_DB_URL)["art-beta"]
    status, body = http_get_json("/artifacts/art-beta")
    assert status == 200
    registry_digest = body["registry_digest"]
    assert registry_digest != evidence["sha256_digest"]
    verify_status = http_post_verify(
        "art-beta",
        registry_digest,
        body["detached_signature"],
    )
    assert verify_status == 409
