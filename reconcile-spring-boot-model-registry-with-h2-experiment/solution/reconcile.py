#!/usr/bin/env python3
"""Derive the release-decision manifest from live registry API + H2 evidence."""

from __future__ import annotations

import argparse
import csv
import json
import re
import subprocess
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path

DEFAULT_DB_URL = "jdbc:h2:file:/app/experiment-db/experiments"
DEFAULT_OUTPUT = "/app/build/release-decision.json"
POLICY_PATH = Path("/app/policy/promotion-policy.md")
SCHEMA_PATH = Path("/app/schemas/release-decision.schema.json")
CANDIDATES_URL = "http://localhost:8080/models/candidates"
H2_JAR = Path("/app/lib/h2-2.2.224.jar")

REASON_METRIC = "metric_threshold"
REASON_UNCALIBRATED = "uncalibrated"
REASON_LINEAGE = "lineage_mismatch"
REASON_MISSING = "missing_canonical_evidence"
REASON_TIEBREAK = "lost_tiebreak"
TOL = 1e-9


def policy_floor(policy: str, metric_label: str) -> float:
    pattern = re.compile(
        rf"\|\s*{re.escape(metric_label)}\s*\|\s*must be greater than or equal to\s*([0-9.]+)"
    )
    match = pattern.search(policy)
    if not match:
        raise RuntimeError(f"promotion policy does not state the {metric_label} floor")
    return float(match.group(1))


def h2_select(sql: str, db_url: str) -> list[dict[str, str]]:
    read_url = db_url if "IFEXISTS" in db_url else f"{db_url};IFEXISTS=TRUE"
    safe_sql = sql.replace("'", "''")
    with tempfile.TemporaryDirectory() as tmp:
        out_csv = Path(tmp) / "out.csv"
        script = Path(tmp) / "query.sql"
        script.write_text(f"CALL CSVWRITE('{out_csv}', '{safe_sql}');\n", encoding="utf-8")
        result = subprocess.run(
            [
                "java",
                "-cp",
                str(H2_JAR),
                "org.h2.tools.RunScript",
                "-url",
                read_url,
                "-user",
                "sa",
                "-script",
                str(script),
            ],
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
        )
        if result.returncode != 0:
            raise RuntimeError(
                f"H2 query failed for {sql!r}:\n{result.stdout}\n{result.stderr}"
            )
        with out_csv.open(newline="", encoding="utf-8") as handle:
            return [
                {key.lower(): value for key, value in row.items()}
                for row in csv.DictReader(handle)
            ]


def fetch_candidates() -> list[dict]:
    last_error: Exception | None = None
    for _ in range(120):
        try:
            with urllib.request.urlopen(CANDIDATES_URL, timeout=10) as response:
                body = json.loads(response.read().decode("utf-8"))
            if isinstance(body, list):
                return body
            last_error = RuntimeError(f"unexpected candidates payload: {type(body)}")
        except (urllib.error.URLError, OSError, ValueError, json.JSONDecodeError) as exc:
            last_error = exc
        time.sleep(1)
    raise RuntimeError("registry API never served /models/candidates") from last_error


def load_evidence(db_url: str) -> dict:
    latest_completed_sql = """
        SELECT vr.model_id, vr.auc, vr.accuracy
        FROM validation_runs vr
        INNER JOIN (
            SELECT model_id, MAX(captured_at) AS max_captured
            FROM validation_runs
            WHERE status = 'completed'
            GROUP BY model_id
        ) latest
            ON vr.model_id = latest.model_id
           AND vr.captured_at = latest.max_captured
        WHERE vr.status = 'completed'
    """
    metrics = {
        row["model_id"]: (float(row["auc"]), float(row["accuracy"]))
        for row in h2_select(latest_completed_sql, db_url)
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
    return {"metrics": metrics, "lineage": lineage, "calibrated": calibrated}


def build_manifest(candidates: list[dict], evidence: dict, auc_floor: float, accuracy_floor: float) -> dict:
    reasons: dict[str, list[str]] = {}
    conflicts: list[dict] = []

    for candidate in candidates:
        model_id = candidate["id"]
        version = candidate["version"]
        registry_hash = candidate["featureHash"]
        api_auc = float(candidate["metrics"]["auc"])
        api_accuracy = float(candidate["metrics"]["accuracy"])

        metrics = evidence["metrics"].get(model_id)
        calibrated_flag = evidence["calibrated"].get(model_id)
        canonical_hash = evidence["lineage"].get((model_id, version))

        if metrics is not None:
            db_auc, db_accuracy = metrics
            if abs(api_auc - db_auc) > TOL:
                conflicts.append(
                    {
                        "model": model_id,
                        "field": "auc",
                        "api_value": api_auc,
                        "db_value": db_auc,
                        "canonical_source": "h2",
                    }
                )
            if abs(api_accuracy - db_accuracy) > TOL:
                conflicts.append(
                    {
                        "model": model_id,
                        "field": "accuracy",
                        "api_value": api_accuracy,
                        "db_value": db_accuracy,
                        "canonical_source": "h2",
                    }
                )
        if canonical_hash is not None and canonical_hash != registry_hash:
            conflicts.append(
                {
                    "model": model_id,
                    "field": "feature_hash",
                    "api_value": registry_hash,
                    "db_value": canonical_hash,
                    "canonical_source": "h2",
                }
            )

        fails: list[str] = []
        if metrics is None or calibrated_flag is None or canonical_hash is None:
            fails.append(REASON_MISSING)
        else:
            db_auc, db_accuracy = metrics
            if db_auc < auc_floor or db_accuracy < accuracy_floor:
                fails.append(REASON_METRIC)
            if not calibrated_flag:
                fails.append(REASON_UNCALIBRATED)
            if canonical_hash != registry_hash:
                fails.append(REASON_LINEAGE)
        reasons[model_id] = fails

    qualifiers = [mid for mid, fails in reasons.items() if not fails]
    ranked = sorted(qualifiers, key=lambda mid: (-evidence["metrics"][mid][0], mid))
    promoted = ranked[0] if ranked else None
    for model_id in qualifiers:
        if model_id != promoted:
            reasons[model_id].append(REASON_TIEBREAK)

    rejected = []
    for model_id in sorted(reasons):
        if model_id == promoted:
            continue
        rejected.append({"model": model_id, "reasons": reasons[model_id]})

    conflicts.sort(key=lambda row: (row["model"], row["field"]))
    manifest = {
        "promoted": promoted,
        "rejected": rejected,
        "conflicts": conflicts,
    }
    return manifest


def validate_manifest(manifest: dict) -> None:
    import jsonschema

    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    jsonschema.validate(instance=manifest, schema=schema)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Reconcile model release evidence.")
    parser.add_argument("jdbc_url", nargs="?", default=DEFAULT_DB_URL)
    parser.add_argument("output_path", nargs="?", default=DEFAULT_OUTPUT)
    args = parser.parse_args(argv)

    policy = POLICY_PATH.read_text(encoding="utf-8")
    auc_floor = policy_floor(policy, "AUC")
    accuracy_floor = policy_floor(policy, "Accuracy")

    candidates = fetch_candidates()
    evidence = load_evidence(args.jdbc_url)
    manifest = build_manifest(candidates, evidence, auc_floor, accuracy_floor)
    validate_manifest(manifest)

    output_path = Path(args.output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(manifest, indent=2) + "\n",
        encoding="utf-8",
    )
    print(
        f"release decision written to {output_path} "
        f"(promoted={manifest['promoted']!r})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
