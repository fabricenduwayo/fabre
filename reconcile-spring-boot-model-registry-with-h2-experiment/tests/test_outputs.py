"""Verifier tests for reconcile-spring-boot-model-registry-with-h2-experiment.

The suite grades the agent-produced /app/build/release-decision.json against
the canonical promotion decision recomputed from the live H2 experiment store
and the running registry API, then reruns the agent-built reconcile Java CLI — against the
shipped store and against verifier-built variant stores — to confirm the
decision is actually derived from live evidence by the program, not
hand-written or hardcoded.

Run via tests/test.sh, which writes /logs/verifier/reward.txt.
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import jsonschema

from helpers import (
    AUC_FLOOR,
    MANIFEST_PATH,
    REASON_METRIC,
    REASON_MISSING,
    REASON_UNCALIBRATED,
    SCHEMA_PATH,
    api_healthy,
    assert_manifest_matches_expected,
    evaluate_candidate,
    evaluate_candidate_with_waivers,
    expected_decision,
    load_evidence,
    run_reconcile_cli,
    semantic_decision,
)


def test_registry_api_serves_candidates(registry):
    """The provided registry API answers /health and reports candidate models."""
    assert api_healthy(), "registry API /health is not answering on port 8080"
    for candidate in registry:
        assert {"id", "name", "version", "metrics", "featureHash"} <= set(candidate)


def test_manifest_exists_and_is_valid_json():
    """The decision manifest exists at /app/build/release-decision.json and parses as JSON."""
    assert MANIFEST_PATH.is_file(), f"missing manifest at {MANIFEST_PATH}"
    # Raises json.JSONDecodeError (test fails) if the file is not valid JSON.
    json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def test_manifest_conforms_to_schema(manifest):
    """The manifest validates against schemas/release-decision.schema.json."""
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    # Raises jsonschema.ValidationError (test fails) on any schema violation.
    jsonschema.validate(instance=manifest, schema=schema)


def test_manifest_references_known_candidates(manifest, registry_by_id):
    """Promoted/rejected entries use registry candidate ids and never overlap."""
    promoted = manifest["promoted"]
    if promoted is not None:
        assert promoted in registry_by_id, (
            f"promoted {promoted!r} is not a registry candidate id"
        )
    rejected_ids = [entry["model"] for entry in manifest["rejected"]]
    for model_id in rejected_ids:
        assert model_id in registry_by_id, (
            f"rejected entry {model_id!r} is not a registry candidate id"
        )
    assert promoted not in rejected_ids, "the promoted model also appears in rejected"
    for conflict in manifest["conflicts"]:
        assert conflict["model"] in registry_by_id, (
            f"conflict references unknown model {conflict['model']!r}"
        )


def test_promoted_model_is_policy_safe(manifest, registry_by_id, evidence, expected):
    """The promoted model passes every policy gate against H2 canonical evidence."""
    promoted = manifest["promoted"]
    assert promoted == expected["promoted"], (
        f"promoted {promoted!r}; the policy makes {expected['promoted']!r} the safe choice"
    )
    assert promoted != "alpha", (
        "alpha must not win when the voided 0.87 validation run is treated as operative"
    )
    if promoted is not None:
        failures = evaluate_candidate(registry_by_id[promoted], evidence)
        assert failures == [], (
            f"promoted model {promoted} violates policy gate(s): {failures}"
        )


def test_rejected_models_carry_exact_reason_codes(manifest, registry, expected):
    """Every non-promoted candidate is rejected with exactly the policy's reason codes."""
    assert_manifest_matches_expected(manifest, registry, expected)


def test_uncalibrated_candidates_never_promoted(manifest, evidence, registry_by_id):
    """An uncalibrated candidate without a live matching waiver is rejected as such."""
    uncalibrated = {
        model_id
        for model_id in registry_by_id
        if evidence["calibrated"].get(model_id) is False
    }
    assert manifest["promoted"] not in uncalibrated, (
        f"promoted model {manifest['promoted']} is uncalibrated per calibration_status"
    )
    rejected = {entry["model"]: set(entry["reasons"]) for entry in manifest["rejected"]}
    for model_id in uncalibrated:
        assert model_id in rejected, f"uncalibrated model {model_id} is not rejected"
        assert REASON_UNCALIBRATED in rejected[model_id], (
            f"uncalibrated model {model_id} is missing the '{REASON_UNCALIBRATED}' reason"
        )


def test_missing_evidence_candidates_fail_closed(manifest, evidence, registry_by_id):
    """Candidates without complete H2 evidence are rejected as missing_canonical_evidence."""
    incomplete = {
        model_id
        for model_id, candidate in registry_by_id.items()
        if evaluate_candidate(candidate, evidence) == [REASON_MISSING]
    }
    rejected = {entry["model"]: set(entry["reasons"]) for entry in manifest["rejected"]}
    assert manifest["promoted"] not in incomplete, (
        "a candidate without canonical evidence was promoted"
    )
    for model_id in incomplete:
        assert model_id in rejected, (
            f"candidate {model_id} has no canonical evidence but is not rejected"
        )
        assert rejected[model_id] == {REASON_MISSING}, (
            f"candidate {model_id} must be rejected with exactly '{REASON_MISSING}'"
        )


def test_conflicts_use_h2_as_canonical_source(manifest):
    """Every recorded conflict names H2 as the canonical source for its field."""
    for conflict in manifest["conflicts"]:
        assert conflict["canonical_source"] == "h2", (
            f"conflict on {conflict['model']}/{conflict['field']} must record "
            "canonical_source 'h2'"
        )


def test_shipped_decision_uses_h2_metrics_not_registry_overstatement(
    manifest, registry_by_id, evidence, expected
):
    """Gate 1 must use operative H2 validation runs, not registry-reported metrics."""
    beta = registry_by_id["beta"]
    registry_auc = float(beta["metrics"]["auc"])
    h2_auc = evidence["metrics"]["beta"][0]
    assert registry_auc >= 0.94, "registry feed should overstate beta for this trap"
    assert h2_auc < AUC_FLOOR, "H2 canonical beta AUC should fail the metric floor"
    assert expected["promoted"] == "omega", (
        "omega wins once delta's replayed calibration voids its qualification"
    )
    assert manifest["promoted"] == "omega", (
        "promoted model must follow H2 metrics, not registry-reported values"
    )
    rejected = {entry["model"]: set(entry["reasons"]) for entry in manifest["rejected"]}
    assert rejected["beta"] == {"lost_tiebreak"}, (
        "beta's canonical metric failure is waived, then its canonical H2 AUC loses tie-break"
    )
    assert any(
        row["model"] == "beta" and row["reason"] == REASON_METRIC
        for row in manifest["applied_waivers"]
    )


def test_gate1_uses_latest_completed_validation_run(evidence, expected):
    """A-2026-04/05/08: Gate 1 ignores non-completed rows and transitive voids."""
    alpha_auc = evidence["metrics"]["alpha"][0]
    assert alpha_auc == 0.83, (
        "alpha must use the surviving completed run after transitive voiding, not the "
        "voided 0.87 row or the recursively voided 0.75 row"
    )
    beta_auc = evidence["metrics"]["beta"][0]
    assert beta_auc == 0.74, (
        "beta must use the latest completed run even when an older completed run passed"
    )
    assert expected["promoted"] == "omega"


def test_gate1_transitive_void_preserves_later_survivor(evidence, expected):
    """A-2026-08: voiding a superseding run also voids runs it superseded."""
    assert evidence["metrics"]["alpha"] == (0.83, 0.78), (
        "alpha operative metrics must come from alpha-run-3 after alpha-run-2 and "
        "alpha-run-1 are voided transitively"
    )
    assert expected["promoted"] == "omega", (
        "promoting alpha would mean the voided high-water 0.87 run was used instead"
    )


def test_calibration_events_override_stale_snapshot(manifest, evidence, expected):
    """A-2026-07: delta's calibration_status snapshot is stale after event replay."""
    assert evidence["calibrated"]["delta"] is False, (
        "delta must be uncalibrated after replaying calibration_events"
    )
    assert expected["promoted"] == "omega"
    assert manifest["promoted"] == "omega"
    rejected = {entry["model"]: set(entry["reasons"]) for entry in manifest["rejected"]}
    assert REASON_UNCALIBRATED in rejected["delta"], (
        "delta must be rejected as uncalibrated despite the stale snapshot row"
    )


def test_gate1_voids_superseded_completed_run(evidence, expected):
    """A-2026-05/08: supersession voiding falls back to the next surviving completed run."""
    assert evidence["metrics"]["alpha"] == (0.83, 0.78), (
        "alpha operative metrics must come from alpha-run-3 after void propagation"
    )
    assert expected["promoted"] == "omega", (
        "with alpha losing the tie-break, omega is the sole qualifier once delta is uncalibrated"
    )


def test_omega_same_timestamp_calibration_replay(evidence, expected):
    """A-2026-09: same-timestamp calibration events tie-break by event_id order."""
    assert evidence["calibrated"]["omega"] is True, (
        "omega must stay calibrated when omega-cal-a then omega-cal-z replay at the "
        "same occurred_at"
    )
    assert expected["promoted"] == "omega"


def test_shipped_waiver_lifecycle(manifest, evidence, expected):
    """A-2026-06/10/11: suppression needs timing and latest-grant approval quorum."""
    active_ids = {waiver["waiver_id"] for waiver in evidence["active_waivers"]}
    assert "delta-lineage-new" in active_ids
    assert "delta-lineage-alt" in active_ids
    assert "delta-lineage-old" not in active_ids
    assert "beta-metric-new" not in active_ids, (
        "beta's non-simultaneous replacement transaction must be ignored"
    )
    assert "gamma-calibration" not in active_ids, (
        "gamma's later ordinary revoke must deactivate its grant"
    )
    assert "alpha-metric-future" not in active_ids, (
        "events after release_context.decision_at must not count"
    )
    assert "beta-metric-quorum" in evidence["approved_waiver_ids"]
    assert "beta-metric-noquorum" not in evidence["approved_waiver_ids"], (
        "one reviewer carrying both role labels must not satisfy approval quorum"
    )
    assert expected["applied_waivers"] == {
        ("beta-metric-quorum", "beta", "0.9.1", "metric_threshold")
    }, "the older fully approved beta waiver must survive the newer under-approved grant"
    reported = {
        (row["waiver_id"], row["model"], row["model_version"], row["reason"])
        for row in manifest["applied_waivers"]
    }
    assert reported == expected["applied_waivers"]
    rejected = {entry["model"]: set(entry["reasons"]) for entry in manifest["rejected"]}
    assert rejected["beta"] == {"lost_tiebreak"}, (
        "beta's metric failure is suppressed, but its lower H2 AUC still loses tie-break"
    )


def test_shipped_waiver_quorum_replays_ties_and_distinct_reviewers(evidence):
    """A-2026-11 replays approval ties and requires distinct risk/owner reviewers."""
    assert evidence["approved_waiver_ids"] == {"beta-metric-quorum"}, (
        "only the waiver with a final owner approval and a distinct risk reviewer qualifies"
    )


def test_manifest_only_registry_candidates(manifest, registry_by_id):
    """Only registry candidates may appear in promoted, rejected, or conflicts."""
    registry_ids = set(registry_by_id)
    if manifest["promoted"] is not None:
        assert manifest["promoted"] in registry_ids
    for entry in manifest["rejected"]:
        assert entry["model"] in registry_ids
    for conflict in manifest["conflicts"]:
        assert conflict["model"] in registry_ids
    assert "zeta" not in registry_ids, "zeta is H2-only bait and must stay out of the manifest"


def test_cli_regenerates_manifest_from_live_evidence(manifest, registry, expected):
    """Rerunning the reconcile CLI reproduces the manifest, with args and with defaults."""
    with tempfile.TemporaryDirectory() as tmp:
        out_path = Path(tmp) / "regenerated.json"
        result = run_reconcile_cli(
            ["jdbc:h2:file:/app/experiment-db/experiments", str(out_path)]
        )
        assert result.returncode == 0, (
            f"reconcile CLI failed with explicit args:\n{result.stdout}\n{result.stderr}"
        )
        assert out_path.is_file(), "CLI did not write to the output path argument"
        regenerated = json.loads(out_path.read_text(encoding="utf-8"))
        assert semantic_decision(regenerated) == semantic_decision(manifest), (
            "manifest regenerated by the CLI disagrees with the submitted manifest"
        )

    original_bytes = MANIFEST_PATH.read_bytes()
    try:
        MANIFEST_PATH.unlink()
        result = run_reconcile_cli([])
        assert result.returncode == 0, (
            f"reconcile CLI failed with default args:\n{result.stdout}\n{result.stderr}"
        )
        assert MANIFEST_PATH.is_file(), (
            "CLI did not write the default manifest path /app/build/release-decision.json"
        )
        regenerated = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        assert semantic_decision(regenerated) == semantic_decision(
            json.loads(original_bytes.decode("utf-8"))
        ), "manifest regenerated with defaults disagrees with the submitted manifest"
    finally:
        MANIFEST_PATH.write_bytes(original_bytes)


def test_cli_generalizes_without_predecessor_revival(registry, variant_a_db_url):
    """Revoking a replacement does not revive its predecessor in a variant store."""
    variant_expected = expected_decision(registry, load_evidence(variant_a_db_url))
    with tempfile.TemporaryDirectory() as tmp:
        out_path = Path(tmp) / "variant-a.json"
        result = run_reconcile_cli([variant_a_db_url, str(out_path)])
        assert result.returncode == 0, (
            f"reconcile CLI failed against the variant store:\n{result.stdout}\n{result.stderr}"
        )
        assert out_path.is_file(), "CLI did not write the variant manifest"
        variant_manifest = json.loads(out_path.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    jsonschema.validate(instance=variant_manifest, schema=schema)
    assert_manifest_matches_expected(variant_manifest, registry, variant_expected)


def test_cli_generalizes_with_malformed_replacement(registry, variant_b_db_url):
    """Stale pre-regrant approvals and a malformed replacement pair are ignored."""
    variant_expected = expected_decision(registry, load_evidence(variant_b_db_url))
    with tempfile.TemporaryDirectory() as tmp:
        out_path = Path(tmp) / "variant-b.json"
        result = run_reconcile_cli([variant_b_db_url, str(out_path)])
        assert result.returncode == 0, (
            f"reconcile CLI failed against the variant store:\n{result.stdout}\n{result.stderr}"
        )
        assert out_path.is_file(), "CLI did not write the variant manifest"
        variant_manifest = json.loads(out_path.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    jsonschema.validate(instance=variant_manifest, schema=schema)
    assert_manifest_matches_expected(variant_manifest, registry, variant_expected)
    assert variant_manifest["promoted"] == "omega"
    rejected = {
        entry["model"]: set(entry["reasons"])
        for entry in variant_manifest["rejected"]
    }
    assert "uncalibrated" in rejected["gamma"], (
        "gamma's approvals predate its latest grant epoch and cannot approve the regrant"
    )
    assert not any(
        row["waiver_id"] == "gamma-calibration"
        for row in variant_manifest["applied_waivers"]
    )


def test_cli_reports_partial_waiver_under_dual_failure(registry, variant_c_db_url):
    """A suppressing waiver is reported even when another gate failure still rejects."""
    variant_expected = expected_decision(registry, load_evidence(variant_c_db_url))
    with tempfile.TemporaryDirectory() as tmp:
        out_path = Path(tmp) / "variant-c.json"
        result = run_reconcile_cli([variant_c_db_url, str(out_path)])
        assert result.returncode == 0, (
            f"reconcile CLI failed against the variant store:\n{result.stdout}\n{result.stderr}"
        )
        variant_manifest = json.loads(out_path.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    jsonschema.validate(instance=variant_manifest, schema=schema)
    assert_manifest_matches_expected(variant_manifest, registry, variant_expected)
    rejected = {entry["model"]: set(entry["reasons"]) for entry in variant_manifest["rejected"]}
    assert rejected["omega"] == {"lineage_mismatch"}, (
        "omega must stay rejected for lineage after its metric waiver suppresses only that gate"
    )
    reported = {
        (row["waiver_id"], row["model"], row["model_version"], row["reason"])
        for row in variant_manifest["applied_waivers"]
    }
    assert ("omega-metric", "omega", "1.4.2", "metric_threshold") in reported


def test_anchored_waiver_voided_run_fails_closed(registry_by_id, variant_d_db_url):
    """A waiver anchored to a voided validation run cannot suppress metric failures."""
    evidence = load_evidence(variant_d_db_url)
    assert evidence["operative_run_ids"]["beta"] == "beta-run-3"
    _, applied = evaluate_candidate_with_waivers(registry_by_id["beta"], evidence)
    reported = {row[0] for row in applied}
    assert "beta-metric-anchored-stale" not in reported
    assert "beta-metric-anchored-live" not in reported
    assert "beta-metric-anchored-ok" in reported


def test_cli_generalizes_operative_run_anchoring(registry, variant_d_db_url):
    """Voided anchors, timing, quorum, and replacement integrity compose on live JDBC."""
    variant_expected = expected_decision(registry, load_evidence(variant_d_db_url))
    with tempfile.TemporaryDirectory() as tmp:
        out_path = Path(tmp) / "variant-d.json"
        result = run_reconcile_cli([variant_d_db_url, str(out_path)])
        assert result.returncode == 0, (
            f"reconcile CLI failed against the variant store:\n{result.stdout}\n{result.stderr}"
        )
        variant_manifest = json.loads(out_path.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    jsonschema.validate(instance=variant_manifest, schema=schema)
    assert_manifest_matches_expected(variant_manifest, registry, variant_expected)
    assert variant_manifest["promoted"] == "omega"
    reported = {
        (row["waiver_id"], row["model"], row["model_version"], row["reason"])
        for row in variant_manifest["applied_waivers"]
    }
    assert reported == {("beta-metric-anchored-ok", "beta", "0.9.1", "metric_threshold")}
    rejected = {
        entry["model"]: set(entry["reasons"])
        for entry in variant_manifest["rejected"]
    }
    assert "lost_tiebreak" in rejected["beta"]
    assert "uncalibrated" in rejected["gamma"]


def test_role_epochs_invalidate_stale_reviewer_authority(registry_by_id, variant_e_db_url):
    """A-2026-13: revoked reviewer authority voids newer waiver approvals."""
    evidence = load_evidence(variant_e_db_url)
    assert "beta-metric-new" not in evidence["approved_waiver_ids"], (
        "risk reviewer authority ended before decision time"
    )
    assert "beta-metric-quorum" in evidence["approved_waiver_ids"]
    _, applied = evaluate_candidate_with_waivers(registry_by_id["beta"], evidence)
    reported = {row[0] for row in applied}
    assert reported == {"beta-metric-quorum"}


def test_gamma_withdrawal_breaks_quorum_after_regrant(registry_by_id, variant_e_db_url):
    """A-2026-11/13: post-quorum risk withdrawal leaves gamma uncalibrated."""
    evidence = load_evidence(variant_e_db_url)
    assert "gamma-calibration" not in evidence["approved_waiver_ids"]
    assert evaluate_candidate(registry_by_id["gamma"], evidence) == [REASON_UNCALIBRATED]


def test_variant_d_requires_operative_run_anchoring(registry_by_id, variant_d_db_url):
    """Pre-A-2026-12 anchoring scope ignores anchor run model_id mismatches."""
    evidence = load_evidence(variant_d_db_url)
    anchored_ok = next(
        waiver
        for waiver in evidence["active_waivers"]
        if waiver["waiver_id"] == "beta-metric-anchored-ok"
    )
    anchor_run = anchored_ok["anchors_run_id"].strip()
    poisoned = dict(evidence)
    poisoned["run_model_ids"] = dict(evidence["run_model_ids"])
    poisoned["run_model_ids"][anchor_run] = "gamma"
    _, applied_full = evaluate_candidate_with_waivers(registry_by_id["beta"], evidence)
    _, applied_poisoned = evaluate_candidate_with_waivers(registry_by_id["beta"], poisoned)
    _, applied_legacy = evaluate_candidate_with_waivers(
        registry_by_id["beta"],
        poisoned,
        enforce_metric_anchoring=False,
    )
    full_ids = {row[0] for row in applied_full}
    poisoned_ids = {row[0] for row in applied_poisoned}
    legacy_ids = {row[0] for row in applied_legacy}
    assert full_ids == {"beta-metric-anchored-ok"}
    assert "beta-metric-anchored-ok" not in poisoned_ids
    assert "beta-metric-anchored-ok" in legacy_ids


def test_variant_e_requires_role_epochs(registry_by_id, variant_e_db_url):
    """Ignoring reviewer-role epochs incorrectly approves a newer under-authority waiver."""
    evidence = load_evidence(variant_e_db_url, enforce_role_epochs=False)
    assert "beta-metric-new" in evidence["approved_waiver_ids"]
    _, applied = evaluate_candidate_with_waivers(registry_by_id["beta"], evidence)
    assert {row[0] for row in applied} == {"beta-metric-new"}


def test_cli_generalizes_reviewer_role_epochs(registry, variant_e_db_url):
    """Role revoke/reassign, withdrawal, and waiver fallback compose on live JDBC."""
    variant_expected = expected_decision(registry, load_evidence(variant_e_db_url))
    with tempfile.TemporaryDirectory() as tmp:
        out_path = Path(tmp) / "variant-e.json"
        result = run_reconcile_cli([variant_e_db_url, str(out_path)])
        assert result.returncode == 0, (
            f"reconcile CLI failed against the variant store:\n{result.stdout}\n{result.stderr}"
        )
        variant_manifest = json.loads(out_path.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    jsonschema.validate(instance=variant_manifest, schema=schema)
    assert_manifest_matches_expected(variant_manifest, registry, variant_expected)
    assert variant_manifest["promoted"] == "omega"
    reported = {
        (row["waiver_id"], row["model"], row["model_version"], row["reason"])
        for row in variant_manifest["applied_waivers"]
    }
    assert reported == {("beta-metric-quorum", "beta", "0.9.1", "metric_threshold")}
    rejected = {
        entry["model"]: set(entry["reasons"])
        for entry in variant_manifest["rejected"]
    }
    assert "lost_tiebreak" in rejected["beta"]
    assert "uncalibrated" in rejected["gamma"]
