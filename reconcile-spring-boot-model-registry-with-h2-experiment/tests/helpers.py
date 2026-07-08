"""Shared constants and pure helpers for the release-decision verifier.

The verifier re-derives the correct promotion decision from the two read-only
canonical sources the reconciliation step must reconcile:

* an H2 experiment database — authoritative for validation metrics,
  version-keyed feature-hash lineage, and calibration status, and
* the model-registry HTTP API — authoritative for the candidate set and
  identity.

Nothing here hardcodes a winning model id; the expected decision falls out of
whichever database the jar is pointed at, evaluated against the documented
policy gates. The same machinery grades the shipped experiment store and the
verifier-built variant stores, which keeps a hardcoded manifest or a
fixture-tuned jar from passing.
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
from pathlib import Path

# --- Pinned locations (stated in instruction.md / the policy bundle) --------
APP = Path("/app")
MANIFEST_PATH = APP / "build" / "release-decision.json"
SCHEMA_PATH = APP / "schemas" / "release-decision.schema.json"
API_BASE_URL = "http://localhost:8080"
HEALTH_URL = f"{API_BASE_URL}/health"
CANDIDATES_URL = f"{API_BASE_URL}/models/candidates"
MAIN_DB_URL = "jdbc:h2:file:/app/experiment-db/experiments"
STEP_JAR = APP / "reconcile-model-release" / "target" / "reconcile-model-release-0.1.0.jar"
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


def find_step_jar() -> str:
    """Locate the agent-built reconcile-model-release fat jar."""
    if STEP_JAR.is_file():
        return str(STEP_JAR)
    matches = glob.glob(str(STEP_JAR.parent / "reconcile-model-release*.jar"))
    jars = [m for m in matches if not m.endswith(("-sources.jar", "-javadoc.jar"))]
    assert jars, (
        f"reconcile-model-release jar not found at {STEP_JAR} — "
        "build it with: mvn -o -f /app/reconcile-model-release/pom.xml package"
    )
    return sorted(jars)[-1]


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


def run_step_jar(args: list[str], timeout: float = 180.0) -> subprocess.CompletedProcess:
    """Run the agent-built reconciliation jar from /app with the given args."""
    return subprocess.run(
        ["java", "-jar", find_step_jar(), *args],
        cwd=str(APP),
        capture_output=True,
        text=True,
        timeout=timeout,
    )


def load_evidence(db_url: str) -> dict:
    """Read the canonical promotion evidence out of an H2 experiment database."""
    metrics = {
        row["model_id"]: (float(row["auc"]), float(row["accuracy"]))
        for row in h2_select("SELECT model_id, auc, accuracy FROM validation_metrics", db_url)
    }
    lineage = {
        (row["model_id"], row["model_version"]): row["feature_hash"]
        for row in h2_select(
            "SELECT model_id, model_version, feature_hash FROM feature_hash_lineage", db_url
        )
    }
    calibrated = {
        row["model_id"]: row["calibrated"].strip().upper() in ("TRUE", "1", "T")
        for row in h2_select("SELECT model_id, calibrated FROM calibration_status", db_url)
    }
    assert metrics, f"no validation_metrics rows returned from {db_url}"
    return {"metrics": metrics, "lineage": lineage, "calibrated": calibrated}


def evaluate_candidate(candidate: dict, evidence: dict) -> list[str]:
    """Return the policy reason codes a candidate accrues (empty == qualifies).

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
        return [REASON_MISSING]

    reasons: list[str] = []
    auc, accuracy = metrics
    if auc < AUC_FLOOR or accuracy < ACCURACY_FLOOR:
        reasons.append(REASON_METRIC)
    if not calibrated:
        reasons.append(REASON_UNCALIBRATED)
    if candidate.get("featureHash") != lineage_hash:
        reasons.append(REASON_LINEAGE)
    return reasons


def expected_decision(candidates: list[dict], evidence: dict) -> dict:
    """Recompute the canonical decision for a candidate list and evidence set."""
    reasons = {c["id"]: evaluate_candidate(c, evidence) for c in candidates}
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
    return (manifest["promoted"], rejected, conflicts)


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
