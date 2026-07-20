"""Verifier tests for enforce-java-release-signature-trust.

The suite checks attestation_reports against the policy recomputed from the store
and the live artifact-metadata API, then reruns the agent-built worker on variant
H2 stores to confirm reports are derived by the program, not hand-written.
"""

from __future__ import annotations

from pathlib import Path

from helpers import (
    MAIN_DB_URL,
    REASON_EXPIRED,
    REASON_EXPOSURE,
    REASON_MISSING,
    REASON_NO_OPERATIVE,
    REASON_REVOKED,
    REASON_VERIFIED,
    api_healthy_status,
    build_variant_store,
    expected_reports_for_db,
    http_get_json,
    load_reports,
    load_store,
    run_attest_worker,
)

TESTS = Path(__file__).resolve().parent
VARIANT_CLEAN = TESTS / "variant_clean_seed.sql"
VARIANT_UNKNOWN = TESTS / "variant_unknown_seed.sql"


def test_api_serves_health() -> None:
    """The bundled metadata API answers /health before anything else runs."""
    assert api_healthy_status() == 200, "artifact-metadata API is not healthy"


def test_registry_fixture_matches_operative_evidence() -> None:
    """Every registry entry's canonical digest matches an evidence row for that
    artifact, so a fixture drift shows up here rather than as a wall of 404s."""
    store = load_store(MAIN_DB_URL)
    for artifact_id, rows in store["rows"].items():
        status, body = http_get_json(f"/artifacts/{artifact_id}")
        if status != 200:
            continue
        digests = {row["sha256_digest"] for row in rows}
        registry_digest = body.get("registry_digest", "")
        assert registry_digest not in digests, (
            f"{artifact_id}: registry_digest equals a canonical digest, which "
            "removes the trap that the registry digest must never be sent to /verify"
        )


def test_reports_cover_every_pending_artifact() -> None:
    """One report per queued artifact, no extras and no duplicates."""
    store = load_store(MAIN_DB_URL)
    reports = load_reports(MAIN_DB_URL)
    assert set(reports) == set(store["queued"]), (
        f"reported {sorted(reports)} for queued {sorted(store['queued'])}"
    )


def test_queue_is_not_consumed() -> None:
    """pending_attestations is an input, so the worker must leave every row."""
    store = load_store(MAIN_DB_URL)
    assert len(store["queued"]) == len(set(store["queued"])), "duplicate queue rows"
    assert store["queued"], "worker deleted rows from pending_attestations"


def test_shipped_reports_match_policy() -> None:
    """Every shipped verdict and reason_code matches the recomputed policy."""
    expected = expected_reports_for_db(MAIN_DB_URL)
    reports = load_reports(MAIN_DB_URL)
    mismatched = {
        artifact_id: (reports.get(artifact_id), report)
        for artifact_id, report in expected.items()
        if reports.get(artifact_id) != report
    }
    assert not mismatched, f"verdict mismatches (got, want): {mismatched}"


def test_operative_row_is_the_amended_one() -> None:
    """A standing amendment supersedes the row underneath it, so the later digest
    is the one that reaches /verify (A-2026-02, A-2026-03)."""
    store = load_store(MAIN_DB_URL)
    row = store["operative"]["art-beta"]
    assert row is not None and row["evidence_id"] == "ev-b2", (
        "art-beta's standing amendment should be operative"
    )
    assert expected_reports_for_db(MAIN_DB_URL)["art-beta"].reason_code == REASON_VERIFIED


def test_unauthorised_amendment_leaves_the_original_standing() -> None:
    """An amendment signed by a key that was not live is discarded and voids
    nothing, so the older row stays operative (A-2026-05)."""
    store = load_store(MAIN_DB_URL)
    row = store["operative"]["art-delta"]
    assert row is not None and row["evidence_id"] == "ev-d1", (
        "the discarded amendment must not void the row it names"
    )


def test_void_cascade_leaves_no_operative_row() -> None:
    """Voiding follows the chain past the row a single pass would stop at, so an
    artifact whose whole chain is void has no operative evidence (A-2026-03)."""
    store = load_store(MAIN_DB_URL)
    assert store["operative"]["art-gamma"] is None
    reports = load_reports(MAIN_DB_URL)
    assert reports["art-gamma"].reason_code == REASON_NO_OPERATIVE


def test_discarded_amendment_is_inert_in_the_cascade() -> None:
    """A discarded amendment's own pointer is never followed, so the row beneath
    it survives a chain that would otherwise void it (A-2026-05)."""
    store = load_store(MAIN_DB_URL)
    row = store["operative"]["art-pi"]
    assert row is not None and row["evidence_id"] == "ev-p1"
    reports = load_reports(MAIN_DB_URL)
    assert reports["art-pi"].reason_code == REASON_VERIFIED


def test_missing_and_no_operative_are_distinct() -> None:
    """An artifact with no rows and an artifact whose rows are all unusable are
    both quarantine but carry different reason codes (A-2026-04)."""
    reports = load_reports(MAIN_DB_URL)
    assert reports["art-lambda"].reason_code == REASON_MISSING
    assert reports["art-mu"].reason_code == REASON_NO_OPERATIVE
    assert reports["art-lambda"].verdict == reports["art-mu"].verdict == "quarantine"


def test_backdated_compromise_denies_an_earlier_signature() -> None:
    """A key_compromise revocation reaches back to its effective instant, so a
    signature made after it is denied (A-2026-08, A-2026-09)."""
    reports = load_reports(MAIN_DB_URL)
    assert reports["art-epsilon"] == expected_reports_for_db(MAIN_DB_URL)["art-epsilon"]
    assert reports["art-epsilon"].reason_code == REASON_REVOKED


def test_non_compromise_revocation_does_not_backdate() -> None:
    """A revoke for any other reason takes effect when it occurred, and its
    effective_from is disregarded (A-2026-08)."""
    reports = load_reports(MAIN_DB_URL)
    assert reports["art-eta"].reason_code == REASON_VERIFIED, (
        "a cessation_of_operation revoke must not reach behind the signature"
    )


def test_expired_key_needs_a_covering_countersignature() -> None:
    """Signing outside the key's window is denied unless a timestamp authority
    whose own window covers that instant countersigned it (A-2026-10)."""
    reports = load_reports(MAIN_DB_URL)
    assert reports["art-theta"].reason_code == REASON_EXPIRED
    assert reports["art-iota"].reason_code == REASON_VERIFIED
    assert reports["art-omicron"].reason_code == REASON_EXPIRED, (
        "a countersignature whose window does not cover signed_at rescues nothing"
    )


def test_revocation_is_settled_before_expiry() -> None:
    """A countersignature extends validity but confers nothing against a
    revocation, so the revoked reason wins (A-2026-09 before A-2026-10)."""
    reports = load_reports(MAIN_DB_URL)
    assert reports["art-kappa"].reason_code == REASON_REVOKED


def test_channel_exposure_downgrades_a_clean_artifact() -> None:
    """Exposure is scoped from other artifacts' operative signers, so an artifact
    signed by a key that was never compromised is still downgraded (A-2026-11)."""
    store = load_store(MAIN_DB_URL)
    assert "edge" in store["exposure"], "the edge channel should be exposed"
    row = store["operative"]["art-xi"]
    assert row is not None and row["signer_key_id"] != "key-c", (
        "art-xi must be signed by a key that is not the compromised one"
    )
    reports = load_reports(MAIN_DB_URL)
    assert reports["art-xi"].reason_code == REASON_EXPOSURE
    assert reports["art-omega"].reason_code == REASON_EXPOSURE


def test_exposure_exemption_needs_a_strictly_earlier_signature() -> None:
    """The countersignature exemption requires signing strictly before the channel
    was exposed, so signing on that instant is not exempt (A-2026-11)."""
    store = load_store(MAIN_DB_URL)
    exposed_at = store["exposure"]["edge"]
    assert store["operative"]["art-xi"]["signed_at"] == exposed_at, (
        "art-xi should sign exactly on the exposure instant"
    )
    assert store["operative"]["art-zeta"]["signed_at"] < exposed_at
    reports = load_reports(MAIN_DB_URL)
    assert reports["art-zeta"].reason_code == REASON_VERIFIED
    assert reports["art-xi"].reason_code == REASON_EXPOSURE


def test_exposure_never_touches_a_denied_verdict() -> None:
    """The channel pass only downgrades trusted, so denied artifacts in an exposed
    channel keep their own reason (A-2026-11)."""
    store = load_store(MAIN_DB_URL)
    reports = load_reports(MAIN_DB_URL)
    for artifact_id, report in reports.items():
        channel = store["artifacts"][artifact_id]["channel_id"]
        if channel in store["exposure"] and report.verdict == "denied":
            assert report.reason_code != REASON_EXPOSURE


def _rerun_on_variant(seed: Path, name: str) -> tuple[dict, dict]:
    """Build a standalone variant store and rerun the agent's worker against it."""
    db_url = build_variant_store(seed, name)
    result = run_attest_worker(db_url)
    assert result.returncode == 0, f"worker failed on {seed.name}:\n{result.stderr}"
    return load_reports(db_url), expected_reports_for_db(db_url)


def test_worker_generalises_to_a_variant_store() -> None:
    """Repointed at a different store the worker derives that store's answer,
    which a hand-written manifest cannot do."""
    reports, expected = _rerun_on_variant(VARIANT_CLEAN, "clean")
    assert reports == expected, f"variant mismatch: got {reports}, want {expected}"


def test_worker_handles_an_artifact_the_registry_does_not_know() -> None:
    """An artifact absent from the registry is denied as unknown_artifact rather
    than trusted or crashed."""
    reports, expected = _rerun_on_variant(VARIANT_UNKNOWN, "unknown")
    assert reports == expected
    assert any(r.reason_code == "unknown_artifact" for r in reports.values())


def test_shipped_store_is_untouched_by_variant_runs() -> None:
    """Variant runs use their own database, so the shipped store still holds the
    agent's original manifest."""
    reports = load_reports(MAIN_DB_URL)
    assert reports == expected_reports_for_db(MAIN_DB_URL)
