"""Verifier tests for reconcile-spring-boot-model-registry-with-h2-experiment.

The suite grades the agent-produced /app/build/release-decision.json against
the canonical promotion decision recomputed from the live H2 experiment store
and the running registry API, then reruns the agent-built reconcile script — against the
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
    expected_decision,
    load_evidence,
    run_reconcile_script,
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
    assert expected["promoted"] == "delta", (
        "delta's governed lineage waiver should make it the canonical-AUC winner"
    )
    assert manifest["promoted"] == "delta", (
        "promoted model must follow H2 metrics, not registry-reported values"
    )
    rejected = {entry["model"]: set(entry["reasons"]) for entry in manifest["rejected"]}
    assert REASON_METRIC in rejected["beta"]


def test_gate1_uses_latest_completed_validation_run(evidence, expected):
    """A-2026-04/05: Gate 1 ignores non-completed rows and voided completed rows."""
    alpha_auc = evidence["metrics"]["alpha"][0]
    assert alpha_auc == 0.75, (
        "alpha must use the latest non-voided completed validation run, not the "
        "voided 0.87 row or a later superseded row"
    )
    beta_auc = evidence["metrics"]["beta"][0]
    assert beta_auc == 0.74, (
        "beta must use the latest completed run even when an older completed run passed"
    )
    assert expected["promoted"] == "delta"


def test_gate1_voids_superseded_completed_run(evidence, expected):
    """A-2026-05: a superseding row voids its target run before operative selection."""
    assert evidence["metrics"]["alpha"] == (0.75, 0.70), (
        "alpha operative metrics must fall back after alpha-run-2 is voided"
    )
    assert expected["promoted"] == "delta", (
        "with alpha failing Gate 1, delta's valid waiver makes it the safe winner"
    )


def test_shipped_waiver_lifecycle(manifest, evidence, expected):
    """A-2026-06 applies only delta's latest valid replacement grant."""
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
    expected_applied = {
        ("delta-lineage-new", "delta", "1.0.3", "lineage_mismatch")
    }
    assert expected["applied_waivers"] == expected_applied
    reported = {
        (row["waiver_id"], row["model"], row["model_version"], row["reason"])
        for row in manifest["applied_waivers"]
    }
    assert reported == expected_applied, (
        "only the latest grant that actually suppresses delta's raw failure is reportable"
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


def test_script_regenerates_manifest_from_live_evidence(manifest, registry, expected):
    """Rerunning the reconcile script reproduces the manifest, with args and with defaults."""
    with tempfile.TemporaryDirectory() as tmp:
        out_path = Path(tmp) / "regenerated.json"
        result = run_reconcile_script(
            ["jdbc:h2:file:/app/experiment-db/experiments", str(out_path)]
        )
        assert result.returncode == 0, (
            f"reconcile script failed with explicit args:\n{result.stdout}\n{result.stderr}"
        )
        assert out_path.is_file(), "script did not write to the output path argument"
        regenerated = json.loads(out_path.read_text(encoding="utf-8"))
        assert semantic_decision(regenerated) == semantic_decision(manifest), (
            "manifest regenerated by the script disagrees with the submitted manifest"
        )

    original_bytes = MANIFEST_PATH.read_bytes()
    try:
        MANIFEST_PATH.unlink()
        result = run_reconcile_script([])
        assert result.returncode == 0, (
            f"reconcile script failed with default args:\n{result.stdout}\n{result.stderr}"
        )
        assert MANIFEST_PATH.is_file(), (
            "script did not write the default manifest path /app/build/release-decision.json"
        )
        regenerated = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        assert semantic_decision(regenerated) == semantic_decision(
            json.loads(original_bytes.decode("utf-8"))
        ), "manifest regenerated with defaults disagrees with the submitted manifest"
    finally:
        MANIFEST_PATH.write_bytes(original_bytes)


def test_script_generalizes_without_predecessor_revival(registry, variant_a_db_url):
    """Revoking a replacement does not revive its predecessor in a variant store."""
    variant_expected = expected_decision(registry, load_evidence(variant_a_db_url))
    with tempfile.TemporaryDirectory() as tmp:
        out_path = Path(tmp) / "variant-a.json"
        result = run_reconcile_script([variant_a_db_url, str(out_path)])
        assert result.returncode == 0, (
            f"reconcile script failed against the variant store:\n{result.stdout}\n{result.stderr}"
        )
        assert out_path.is_file(), "script did not write the variant manifest"
        variant_manifest = json.loads(out_path.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    jsonschema.validate(instance=variant_manifest, schema=schema)
    assert_manifest_matches_expected(variant_manifest, registry, variant_expected)


def test_script_generalizes_with_malformed_replacement(registry, variant_b_db_url):
    """A valid simple grant applies while a malformed replacement pair is ignored."""
    variant_expected = expected_decision(registry, load_evidence(variant_b_db_url))
    with tempfile.TemporaryDirectory() as tmp:
        out_path = Path(tmp) / "variant-b.json"
        result = run_reconcile_script([variant_b_db_url, str(out_path)])
        assert result.returncode == 0, (
            f"reconcile script failed against the variant store:\n{result.stdout}\n{result.stderr}"
        )
        assert out_path.is_file(), "script did not write the variant manifest"
        variant_manifest = json.loads(out_path.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    jsonschema.validate(instance=variant_manifest, schema=schema)
    assert_manifest_matches_expected(variant_manifest, registry, variant_expected)
