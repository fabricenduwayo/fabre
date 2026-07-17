"""Shared constants and pure helpers for the release-decision verifier.

The verifier re-derives the correct promotion decision from the two read-only
canonical sources the reconciliation step must reconcile:

* an H2 experiment database — authoritative for validation metrics,
  version-keyed feature-hash lineage, and calibration status, and
* the model-registry HTTP API — authoritative for the candidate set and
  identity.

Nothing here hardcodes a winning model id; the expected decision falls out of
whichever database the reconcile CLI is pointed at, evaluated against the
documented policy gates. The same machinery grades the shipped experiment store
and the verifier-built variant stores, which keeps a hardcoded manifest or a
fixture-tuned shortcut from passing.
"""

from __future__ import annotations

import csv
import glob
import json
import subprocess
import tempfile
import time
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path

# --- Pinned locations (stated in instruction.md / the policy bundle) --------
APP = Path("/app")
MANIFEST_PATH = APP / "build" / "release-decision.json"
SCHEMA_PATH = APP / "schemas" / "release-decision.schema.json"
API_BASE_URL = "http://localhost:8080"
HEALTH_URL = f"{API_BASE_URL}/health"
CANDIDATES_URL = f"{API_BASE_URL}/models/candidates"
MAIN_DB_URL = "jdbc:h2:file:/app/experiment-db/experiments"
RECONCILE_CLASSES = APP / "reconcile-model-release" / "classes"
MAIN_CLASS = "com.snorkel.registry.Main"
H2_JAR = APP / "lib" / "h2-2.2.224.jar"
TESTS_DIR = Path(__file__).resolve().parent

# Promotion-gate thresholds mirror the authored policy prose in
# environment/policy/promotion-policy.md (Gate 1); keep them in sync.
AUC_FLOOR = 0.80
ACCURACY_FLOOR = 0.75

# Exact reason codes defined by the promotion policy.
REASON_METRIC = "metric_threshold"
REASON_UNCALIBRATED = "uncalibrated"
REASON_LINEAGE = "lineage_mismatch"
REASON_MISSING = "missing_canonical_evidence"
REASON_TIEBREAK = "lost_tiebreak"

# Float tolerance for metric comparisons.
TOL = 1e-9


def find_h2_jar() -> str:
    """Locate the H2 driver jar (fixed image path, Maven-repo fallback)."""
    if H2_JAR.is_file():
        return str(H2_JAR)
    matches = glob.glob("/root/.m2/repository/com/h2database/h2/*/h2-*.jar")
    jars = [m for m in matches if not m.endswith(("-sources.jar", "-javadoc.jar"))]
    assert jars, "H2 driver jar not found in the image"
    return sorted(jars)[-1]


def reconcile_classpath() -> str:
    """Classpath for the agent-built reconcile-model-release Java CLI."""
    assert RECONCILE_CLASSES.is_dir(), (
        f"reconcile classes not found at {RECONCILE_CLASSES} — "
        "build /app/reconcile-model-release with build.sh"
    )
    return f"{RECONCILE_CLASSES}:/app/lib/*"


def run_h2_script(db_url: str, script_path: Path) -> None:
    """Execute a SQL script against an H2 database via the RunScript tool."""
    result = subprocess.run(
        [
            "java", "-cp", find_h2_jar(), "org.h2.tools.RunScript",
            "-url", db_url, "-user", "sa", "-script", str(script_path),
        ],
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, (
        f"H2 RunScript failed for {script_path}:\n{result.stdout}\n{result.stderr}"
    )


def h2_select(sql: str, db_url: str = MAIN_DB_URL) -> list[dict[str, str]]:
    """Run a read-only SELECT against an H2 database, returning rows as dicts.

    Uses H2's CSVWRITE via the driver jar so the pure-Python verifier can read
    the Java-native database file without a JDBC binding. Column keys are
    lower-cased for stable access regardless of H2's identifier casing.
    """
    read_url = db_url if "IFEXISTS" in db_url else f"{db_url};IFEXISTS=TRUE"
    safe_sql = sql.replace("'", "''")
    with tempfile.TemporaryDirectory() as tmp:
        out_csv = Path(tmp) / "out.csv"
        script = Path(tmp) / "query.sql"
        script.write_text(
            f"CALL CSVWRITE('{out_csv}', '{safe_sql}');\n", encoding="utf-8"
        )
        result = subprocess.run(
            [
                "java", "-cp", find_h2_jar(), "org.h2.tools.RunScript",
                "-url", read_url, "-user", "sa", "-script", str(script),
            ],
            capture_output=True,
            text=True,
            timeout=120,
        )
        assert result.returncode == 0, (
            f"H2 query failed for {sql!r}:\n{result.stdout}\n{result.stderr}"
        )
        with out_csv.open(newline="", encoding="utf-8") as handle:
            return [
                {key.lower(): value for key, value in row.items()}
                for row in csv.DictReader(handle)
            ]


def http_get_json(url: str, timeout: float = 5.0):
    """GET a URL and parse the JSON body."""
    with urllib.request.urlopen(url, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def api_healthy() -> bool:
    """True when the registry API answers its health endpoint."""
    try:
        return http_get_json(HEALTH_URL).get("status") == "UP"
    except (urllib.error.URLError, OSError, ValueError):
        return False


def wait_for_api(seconds: float) -> bool:
    """Poll the health endpoint for up to ``seconds``; True once it answers."""
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        if api_healthy():
            return True
        time.sleep(1)
    return api_healthy()


def run_reconcile_cli(args: list[str], timeout: float = 240.0) -> subprocess.CompletedProcess:
    """Run the agent-built reconcile-model-release Java CLI from /app."""
    return subprocess.run(
        ["java", "-cp", reconcile_classpath(), MAIN_CLASS, *args],
        cwd=str(APP),
        capture_output=True,
        text=True,
        timeout=timeout,
    )


LATEST_COMPLETED_METRICS_SQL = """
SELECT run_id, model_id, captured_at, status, auc, accuracy, supersedes_run_id
FROM validation_runs
"""


def operative_metrics(db_url: str) -> dict[str, tuple[float, float, str, str]]:
    """Pick Gate 1 metrics per model using A-2026-04, A-2026-05, and A-2026-08."""
    runs = h2_select(LATEST_COMPLETED_METRICS_SQL, db_url)
    supersedes_by_run = {
        row["run_id"]: row.get("supersedes_run_id", "").strip()
        for row in runs
        if row.get("supersedes_run_id", "").strip()
    }
    voided = {
        row["supersedes_run_id"].strip()
        for row in runs
        if row.get("supersedes_run_id", "").strip()
    }
    changed = True
    while changed:
        changed = False
        for run_id, supersedes in supersedes_by_run.items():
            if run_id in voided and supersedes and supersedes not in voided:
                voided.add(supersedes)
                changed = True
    latest_by_model: dict[str, dict[str, str]] = {}
    for row in runs:
        if row["status"] != "completed":
            continue
        if row["run_id"] in voided:
            continue
        model_id = row["model_id"]
        captured_at = row["captured_at"]
        current = latest_by_model.get(model_id)
        if current is None or captured_at > current["captured_at"]:
            latest_by_model[model_id] = row
    return {
        model_id: (float(row["auc"]), float(row["accuracy"]), row["captured_at"], row["run_id"])
        for model_id, row in latest_by_model.items()
    }


def parse_timestamp(value: str) -> datetime:
    """Parse an H2 timestamp into an orderable Python value."""
    return datetime.fromisoformat(value.strip().replace("Z", "+00:00"))


def active_waivers(db_url: str) -> list[dict]:
    """Evaluate the A-2026-06 waiver event lifecycle as of decision_at."""
    contexts = h2_select("SELECT context_id, decision_at FROM release_context", db_url)
    assert len(contexts) == 1, "release_context must contain exactly one decision"
    decision_at = parse_timestamp(contexts[0]["decision_at"])
    waivers = {
        row["waiver_id"]: row
        for row in h2_select(
            """
            SELECT waiver_id, model_id, model_version, reason_code,
                   valid_from, valid_until, replaces_waiver_id, anchors_run_id
            FROM promotion_waivers
            """,
            db_url,
        )
    }
    events = {
        row["event_id"]: row
        for row in h2_select(
            """
            SELECT event_id, waiver_id, event_type, occurred_at, paired_event_id
            FROM waiver_events
            """,
            db_url,
        )
        if parse_timestamp(row["occurred_at"]) <= decision_at
    }

    valid_events: list[dict] = []
    for event in events.values():
        waiver = waivers[event["waiver_id"]]
        paired_id = event.get("paired_event_id", "").strip()
        if not paired_id:
            if event["event_type"] == "revoke" or not waiver.get(
                "replaces_waiver_id", ""
            ).strip():
                valid_events.append(event)
            continue
        mate = events.get(paired_id)
        if mate is None or mate.get("paired_event_id", "").strip() != event["event_id"]:
            continue
        if event["occurred_at"] != mate["occurred_at"]:
            continue
        pair = {event["event_type"]: event, mate["event_type"]: mate}
        if set(pair) != {"grant", "revoke"}:
            continue
        successor = waivers[pair["grant"]["waiver_id"]]
        predecessor = waivers[pair["revoke"]["waiver_id"]]
        if successor.get("replaces_waiver_id", "").strip() != predecessor["waiver_id"]:
            continue
        if any(
            successor[key] != predecessor[key]
            for key in ("model_id", "model_version", "reason_code")
        ):
            continue
        successor_anchor = successor.get("anchors_run_id", "").strip()
        predecessor_anchor = predecessor.get("anchors_run_id", "").strip()
        if successor_anchor != predecessor_anchor:
            continue
        valid_events.append(event)

    latest: dict[str, dict] = {}
    for event in valid_events:
        current = latest.get(event["waiver_id"])
        key = (parse_timestamp(event["occurred_at"]), event["event_id"])
        if current is None or key > (
            parse_timestamp(current["occurred_at"]),
            current["event_id"],
        ):
            latest[event["waiver_id"]] = event

    result: list[dict] = []
    for waiver_id, event in latest.items():
        waiver = waivers[waiver_id]
        if event["event_type"] != "grant":
            continue
        if (
            parse_timestamp(waiver["valid_from"])
            <= decision_at
            < parse_timestamp(waiver["valid_until"])
        ):
            result.append(
                {
                    **waiver,
                    "grant_at": parse_timestamp(event["occurred_at"]),
                    "grant_event_id": event["event_id"],
                }
            )
    return result


def approval_quorum(db_url: str, active_waivers: list[dict]) -> set[str]:
    """Return active waiver ids satisfying A-2026-11's current-grant quorum."""
    contexts = h2_select("SELECT context_id, decision_at FROM release_context", db_url)
    assert len(contexts) == 1, "release_context must contain exactly one decision"
    decision_at = parse_timestamp(contexts[0]["decision_at"])
    active_by_id = {waiver["waiver_id"]: waiver for waiver in active_waivers}

    latest: dict[tuple[str, str, str], dict[str, str]] = {}
    for event in h2_select(
        """
        SELECT event_id, waiver_id, reviewer_id, reviewer_role,
               event_type, occurred_at
        FROM waiver_approval_events
        """,
        db_url,
    ):
        waiver = active_by_id.get(event["waiver_id"])
        if waiver is None:
            continue
        event_key = (parse_timestamp(event["occurred_at"]), event["event_id"])
        grant_key = (waiver["grant_at"], waiver["grant_event_id"])
        if event_key <= grant_key or event_key[0] > decision_at:
            continue
        key = (event["waiver_id"], event["reviewer_id"], event["reviewer_role"])
        current = latest.get(key)
        if current is None or event_key > (
            parse_timestamp(current["occurred_at"]),
            current["event_id"],
        ):
            latest[key] = event

    reviewers: dict[str, dict[str, set[str]]] = {}
    for event in latest.values():
        if event["event_type"] != "approve":
            continue
        roles = reviewers.setdefault(event["waiver_id"], {})
        roles.setdefault(event["reviewer_role"], set()).add(event["reviewer_id"])

    approved: set[str] = set()
    for waiver_id, roles in reviewers.items():
        risk = roles.get("risk", set())
        owners = roles.get("model_owner", set())
        if any(risk_reviewer != owner_reviewer for risk_reviewer in risk for owner_reviewer in owners):
            approved.add(waiver_id)
    return approved


def effective_calibration(db_url: str) -> dict[str, bool]:
    """Replay A-2026-07 calibration_events through release_context.decision_at."""
    contexts = h2_select("SELECT context_id, decision_at FROM release_context", db_url)
    assert len(contexts) == 1, "release_context must contain exactly one decision"
    decision_at = parse_timestamp(contexts[0]["decision_at"])

    snapshot = {
        row["model_id"]: row["calibrated"].strip().upper() in ("TRUE", "1", "T")
        for row in h2_select("SELECT model_id, calibrated FROM calibration_status", db_url)
    }
    events_by_model: dict[str, list[dict[str, str]]] = {}
    for row in h2_select(
        "SELECT event_id, model_id, event_type, occurred_at FROM calibration_events",
        db_url,
    ):
        if parse_timestamp(row["occurred_at"]) > decision_at:
            continue
        events_by_model.setdefault(row["model_id"], []).append(row)

    calibrated: dict[str, bool] = {}
    for model_id, flag in snapshot.items():
        effective = flag
        ordered = sorted(
            events_by_model.get(model_id, []),
            key=lambda row: (parse_timestamp(row["occurred_at"]), row["event_id"]),
        )
        for event in ordered:
            effective = event["event_type"] == "calibrate"
        calibrated[model_id] = effective
    return calibrated


def load_evidence(db_url: str) -> dict:
    """Read the canonical promotion evidence out of an H2 experiment database."""
    metrics = operative_metrics(db_url)
    lineage = {
        (row["model_id"], row["model_version"]): row["feature_hash"]
        for row in h2_select(
            "SELECT model_id, model_version, feature_hash FROM feature_hash_lineage", db_url
        )
    }
    calibrated = effective_calibration(db_url)
    assert metrics, f"no validation_metrics rows returned from {db_url}"
    metric_values = {
        model_id: (values[0], values[1]) for model_id, values in metrics.items()
    }
    metric_captured_at = {
        model_id: values[2] for model_id, values in metrics.items()
    }
    operative_run_ids = {
        model_id: values[3] for model_id, values in metrics.items()
    }
    waivers = active_waivers(db_url)
    return {
        "metrics": metric_values,
        "metric_captured_at": metric_captured_at,
        "operative_run_ids": operative_run_ids,
        "lineage": lineage,
        "calibrated": calibrated,
        "active_waivers": waivers,
        "approved_waiver_ids": approval_quorum(db_url, waivers),
    }


def evaluate_candidate_with_waivers(
    candidate: dict, evidence: dict
) -> tuple[list[str], list[tuple[str, str, str, str]]]:
    """Return effective reasons and selected suppressing governance waivers.

    Mirrors the promotion policy: incomplete canonical evidence fails closed
    with ``missing_canonical_evidence`` and skips gate evaluation; otherwise
    every failing gate contributes its exact reason code.
    """
    model_id = candidate["id"]
    version = candidate["version"]
    metrics = evidence["metrics"].get(model_id)
    calibrated = evidence["calibrated"].get(model_id)
    lineage_hash = evidence["lineage"].get((model_id, version))
    if metrics is None or calibrated is None or lineage_hash is None:
        return [REASON_MISSING], []

    reasons: list[str] = []
    auc, accuracy = metrics
    if auc < AUC_FLOOR or accuracy < ACCURACY_FLOOR:
        reasons.append(REASON_METRIC)
    if not calibrated:
        reasons.append(REASON_UNCALIBRATED)
    if candidate.get("featureHash") != lineage_hash:
        reasons.append(REASON_LINEAGE)

    remaining: list[str] = []
    applied: list[tuple[str, str, str, str]] = []
    operative_at = evidence.get("metric_captured_at", {}).get(model_id)
    operative_run_id = evidence.get("operative_run_ids", {}).get(model_id)
    for reason in reasons:
        matching = []
        for waiver in evidence["active_waivers"]:
            if (
                waiver["model_id"] != model_id
                or waiver["model_version"] != version
                or waiver["reason_code"] != reason
                or waiver["waiver_id"] not in evidence["approved_waiver_ids"]
            ):
                continue
            anchor = waiver.get("anchors_run_id", "").strip() or None
            if anchor is not None:
                if operative_run_id != anchor:
                    continue
                timing_source = operative_at
            else:
                timing_source = operative_at
            operative_timestamp = (
                parse_timestamp(timing_source) if timing_source is not None else None
            )
            if operative_timestamp is not None and waiver["grant_at"] >= operative_timestamp:
                continue
            matching.append(waiver)
        if not matching:
            remaining.append(reason)
            continue
        selected = max(
            matching, key=lambda waiver: (waiver["grant_at"], waiver["waiver_id"])
        )
        applied.append((selected["waiver_id"], model_id, version, reason))
    return remaining, applied


def evaluate_candidate(candidate: dict, evidence: dict) -> list[str]:
    """Return effective policy reason codes after governance waivers."""
    return evaluate_candidate_with_waivers(candidate, evidence)[0]


def expected_decision(candidates: list[dict], evidence: dict) -> dict:
    """Recompute the canonical decision for a candidate list and evidence set."""
    evaluated = {
        c["id"]: evaluate_candidate_with_waivers(c, evidence) for c in candidates
    }
    reasons = {mid: result[0] for mid, result in evaluated.items()}
    applied_waivers = {
        waiver for result in evaluated.values() for waiver in result[1]
    }
    qualifiers = [mid for mid, fails in reasons.items() if not fails]
    ranked = sorted(qualifiers, key=lambda mid: (-evidence["metrics"][mid][0], mid))
    promoted = ranked[0] if ranked else None
    for mid in qualifiers:
        if mid != promoted:
            reasons[mid].append(REASON_TIEBREAK)

    conflicts: dict[tuple[str, str], tuple] = {}
    for candidate in candidates:
        mid = candidate["id"]
        db_metrics = evidence["metrics"].get(mid)
        if db_metrics is not None:
            api_auc = float(candidate["metrics"]["auc"])
            api_accuracy = float(candidate["metrics"]["accuracy"])
            if abs(api_auc - db_metrics[0]) > TOL:
                conflicts[(mid, "auc")] = (api_auc, db_metrics[0])
            if abs(api_accuracy - db_metrics[1]) > TOL:
                conflicts[(mid, "accuracy")] = (api_accuracy, db_metrics[1])
        db_hash = evidence["lineage"].get((mid, candidate["version"]))
        if db_hash is not None and candidate.get("featureHash") != db_hash:
            conflicts[(mid, "featurehash")] = (candidate["featureHash"], db_hash)

    return {
        "promoted": promoted,
        "reasons": {mid: frozenset(codes) for mid, codes in reasons.items()},
        "rejected": {mid for mid in reasons if mid != promoted},
        "applied_waivers": applied_waivers,
        "conflicts": conflicts,
    }


def norm_field(name: str) -> str:
    """Normalize a conflict field label so naming variants compare equal.

    e.g. "feature_hash", "featureHash", "feature-hash" -> "featurehash".
    """
    return "".join(ch for ch in name.lower() if ch.isalnum())


def semantic_decision(manifest: dict) -> tuple:
    """Reduce a manifest to an order-insensitive, comparable structure."""
    rejected = {
        entry["model"]: frozenset(entry["reasons"]) for entry in manifest["rejected"]
    }
    conflicts = {}
    for conflict in manifest["conflicts"]:
        field = norm_field(conflict["field"])
        if field in ("auc", "accuracy"):
            values = (round(float(conflict["api_value"]), 9), round(float(conflict["db_value"]), 9))
        else:
            values = (str(conflict["api_value"]), str(conflict["db_value"]))
        conflicts[(conflict["model"], field)] = (*values, conflict["canonical_source"])
    applied = {
        (
            row["waiver_id"],
            row["model"],
            row["model_version"],
            row["reason"],
        )
        for row in manifest["applied_waivers"]
    }
    return (manifest["promoted"], rejected, applied, conflicts)


def assert_manifest_matches_expected(manifest: dict, candidates: list[dict], expected: dict) -> None:
    """Assert a manifest encodes exactly the recomputed canonical decision."""
    assert manifest["promoted"] == expected["promoted"], (
        f"promoted {manifest['promoted']!r}; the policy makes {expected['promoted']!r} the safe choice"
    )

    rejected_reasons: dict[str, frozenset] = {}
    for entry in manifest["rejected"]:
        assert entry["model"] not in rejected_reasons, (
            f"model {entry['model']!r} appears twice in rejected"
        )
        rejected_reasons[entry["model"]] = frozenset(entry["reasons"])
    assert set(rejected_reasons) == expected["rejected"], (
        f"rejected set {sorted(rejected_reasons)} != expected {sorted(expected['rejected'])}"
    )
    for mid, codes in rejected_reasons.items():
        assert codes == expected["reasons"][mid], (
            f"reason codes for {mid}: manifest {sorted(codes)} != policy {sorted(expected['reasons'][mid])}"
        )

    applied = [
        (
            row["waiver_id"],
            row["model"],
            row["model_version"],
            row["reason"],
        )
        for row in manifest["applied_waivers"]
    ]
    assert len(applied) == len(set(applied)), "an applied waiver is reported twice"
    assert set(applied) == expected["applied_waivers"], (
        f"applied waivers {sorted(applied)} != expected "
        f"{sorted(expected['applied_waivers'])}"
    )

    reported: dict[tuple[str, str], tuple] = {}
    for conflict in manifest["conflicts"]:
        key = (conflict["model"], norm_field(conflict["field"]))
        assert key not in reported, f"conflict {key} reported twice"
        assert conflict["canonical_source"] == "h2", (
            f"conflict {key} must record canonical_source 'h2'"
        )
        reported[key] = (conflict["api_value"], conflict["db_value"])
    assert set(reported) == set(expected["conflicts"]), (
        f"conflict set mismatch: manifest {sorted(reported)} != expected {sorted(expected['conflicts'])}"
    )
    for key, (api_value, db_value) in expected["conflicts"].items():
        got_api, got_db = reported[key]
        if key[1] in ("auc", "accuracy"):
            assert abs(float(got_api) - api_value) <= TOL, (
                f"conflict {key}: api_value {got_api!r} != registry value {api_value!r}"
            )
            assert abs(float(got_db) - db_value) <= TOL, (
                f"conflict {key}: db_value {got_db!r} != H2 canonical value {db_value!r}"
            )
        else:
            assert str(got_api) == api_value, (
                f"conflict {key}: api_value {got_api!r} != registry hash {api_value!r}"
            )
            assert str(got_db) == db_value, (
                f"conflict {key}: db_value {got_db!r} != H2 canonical hash {db_value!r}"
            )
