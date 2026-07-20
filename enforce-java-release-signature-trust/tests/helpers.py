"""Shared helpers for the release attestation verifier.

The expected manifest is recomputed here from the H2 store and the live metadata
API, so nothing depends on a hardcoded winner. Point it at a different store and it
derives that store's answer.
"""

from __future__ import annotations

import json
import os
import subprocess
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

# ATTEST_APP_ROOT lets the author run this suite outside the container; the
# verifier always runs against /app.
APP = Path(os.environ.get("ATTEST_APP_ROOT", "/app"))
MAIN_DB_URL = f"jdbc:h2:file:{APP}/attestation-db/attestation"
API_BASE = "http://localhost:8080"
H2_JAR = APP / "lib" / "h2-2.2.224.jar"
WORKER_CLASSES = APP / "attest-worker" / "classes"

ATTESTED = "attested"
COMPROMISE = "key_compromise"

REASON_VERIFIED = "verified"
REASON_REVOKED = "revoked_signer"
REASON_EXPIRED = "expired_key_signature"
REASON_EXPOSURE = "channel_exposure"
REASON_MISSING = "missing_evidence"
REASON_NO_OPERATIVE = "no_operative_evidence"


@dataclass(frozen=True)
class ReportRow:
    verdict: str
    reason_code: str
    operative_evidence_id: str | None = None


def find_h2_jar() -> str:
    if H2_JAR.is_file():
        return str(H2_JAR)
    matches = sorted((APP / "lib").glob("h2-*.jar"))
    if not matches:
        raise AssertionError("no H2 jar under /app/lib")
    return str(matches[0])


def worker_classpath() -> str:
    return f"{WORKER_CLASSES}:{APP / 'lib'}/*"


def ensure_api_ready() -> None:
    subprocess.run(["bash", str(APP / "start-api.sh")], check=True, timeout=360)


def api_healthy_status() -> int:
    status, _ = http_get_json("/health")
    return status


def build_variant_store(seed_path: Path, name: str) -> str:
    """Build a standalone H2 store from the shipped schema plus a variant seed.

    Variant runs get their own database so they never mutate the shipped store,
    which keeps the suite order independent.
    """
    target = Path("/tmp") / f"variant-{name}"
    for stale in Path("/tmp").glob(f"variant-{name}.*"):
        stale.unlink()
    db_url = f"jdbc:h2:file:{target}"
    run_h2_script(db_url, APP / "attestation-db" / "schema.sql")
    run_h2_script(db_url, seed_path)
    return db_url


def run_h2_script(db_url: str, script_path: Path) -> None:
    result = subprocess.run(
        [
            "java", "-cp", find_h2_jar(), "org.h2.tools.RunScript",
            "-url", db_url, "-user", "sa", "-script", str(script_path),
        ],
        capture_output=True, text=True, timeout=180,
    )
    assert result.returncode == 0, (
        f"H2 RunScript failed for {script_path}:\n{result.stdout}\n{result.stderr}"
    )


def h2_rows(db_url: str, columns: list[str], table: str, tail: str = "") -> list[list[str]]:
    """RunScript separates columns with a space and timestamps contain spaces, so
    concatenate with an explicit delimiter and read back a single column."""
    expr = " || '~' || ".join(f"COALESCE(CAST({c} AS VARCHAR), 'NULL')" for c in columns)
    script = Path("/tmp/_verifier_query.sql")
    script.write_text(f"SELECT {expr} FROM {table} {tail};\n")
    result = subprocess.run(
        [
            "java", "-cp", find_h2_jar(), "org.h2.tools.RunScript",
            "-url", db_url, "-user", "sa", "-script", str(script), "-showResults",
        ],
        capture_output=True, text=True, timeout=180,
    )
    assert result.returncode == 0, f"H2 query failed:\n{result.stdout}\n{result.stderr}"
    return [
        line[4:].split("~") for line in result.stdout.splitlines() if line.startswith("--> ")
    ]


def _ts(value: str) -> datetime | None:
    value = value.strip()
    if not value or value.lower() == "null":
        return None
    return datetime.strptime(value.split(".")[0], "%Y-%m-%d %H:%M:%S")


def _nul(value: str) -> str | None:
    value = value.strip()
    return None if not value or value.lower() == "null" else value


def effective_instant(event: dict) -> datetime:
    """A-2026-08. effective_from counts only for a key_compromise revoke."""
    if event["event_type"] == "revoke" and event["reason"] == COMPROMISE:
        return event["effective_from"] or event["occurred_at"]
    return event["occurred_at"]


def revoked_at(events: list[dict], instant: datetime) -> bool:
    """A-2026-07. Replay the log; the latest event at or before instant wins."""
    seen = [e for e in events if effective_instant(e) <= instant]
    if not seen:
        return False
    seen.sort(key=lambda e: (effective_instant(e), e["event_id"]))
    return seen[-1]["event_type"] == "revoke"


def live_at(key: dict, events: list[dict], instant: datetime) -> bool:
    """A-2026-06. Not revoked, and inside the half-open validity window."""
    if revoked_at(events, instant):
        return False
    return key["not_before"] <= instant < key["not_after"]


def operative_row(rows: list[dict], keys: dict, events: dict) -> dict | None:
    """A-2026-01 through A-2026-05, in the order the amendments impose."""
    discarded = set()
    for row in rows:
        if row["supersedes_evidence_id"] is None:
            continue
        amender = row["amendment_key_id"]
        if amender is None or not live_at(
            keys[amender], events.get(amender, []), row["recorded_at"]
        ):
            discarded.add(row["evidence_id"])

    void: set[str] = set()
    standing = [
        r
        for r in rows
        if r["supersedes_evidence_id"] is not None and r["evidence_id"] not in discarded
    ]
    if standing:
        standing.sort(key=lambda r: (r["recorded_at"], r["evidence_id"]))
        void.add(standing[-1]["supersedes_evidence_id"])
        by_id = {r["evidence_id"]: r for r in rows}
        growing = True
        while growing:
            growing = False
            for evidence_id in list(void):
                row = by_id.get(evidence_id)
                # A-2026-05: a discarded amendment is inert in the cascade.
                if row is None or evidence_id in discarded:
                    continue
                target = row["supersedes_evidence_id"]
                if target and target not in void:
                    void.add(target)
                    growing = True

    candidates = [
        r
        for r in rows
        if r["status"] == ATTESTED
        and r["evidence_id"] not in void
        and r["evidence_id"] not in discarded
    ]
    if not candidates:
        return None
    candidates.sort(key=lambda r: (r["recorded_at"], r["evidence_id"]))
    return candidates[-1]


def countersigned(row: dict, tsas: dict) -> bool:
    """A-2026-10. The named authority's window has to cover signed_at."""
    tsa = tsas.get(row["tsa_id"]) if row["tsa_id"] else None
    if not tsa:
        return False
    return tsa["valid_from"] <= row["signed_at"] < tsa["valid_until"]


def signer_defect(row: dict, keys: dict, events: dict, tsas: dict) -> str | None:
    """A-2026-09 then A-2026-10."""
    if revoked_at(events.get(row["signer_key_id"], []), row["signed_at"]):
        return REASON_REVOKED
    key = keys[row["signer_key_id"]]
    if key["not_before"] <= row["signed_at"] < key["not_after"]:
        return None
    if countersigned(row, tsas):
        return None
    return REASON_EXPIRED


def exposed_channels(artifacts: dict, operative: dict, events: dict) -> dict[str, datetime]:
    """A-2026-11. Earliest compromise instant per channel, from operative signers."""
    exposure: dict[str, datetime] = {}
    for key_id, key_events in events.items():
        for event in key_events:
            if event["event_type"] != "revoke" or event["reason"] != COMPROMISE:
                continue
            instant = effective_instant(event)
            for artifact_id, row in operative.items():
                if row is None or row["signer_key_id"] != key_id:
                    continue
                channel = artifacts[artifact_id]["channel_id"]
                if channel not in exposure or instant < exposure[channel]:
                    exposure[channel] = instant
    return exposure


def load_store(db_url: str) -> dict:
    """Read every table the policy touches and resolve the operative rows."""
    keys = {
        r[0]: {"key_id": r[0], "not_before": _ts(r[1]), "not_after": _ts(r[2])}
        for r in h2_rows(db_url, ["key_id", "not_before", "not_after"], "signing_keys")
    }
    events: dict[str, list[dict]] = {}
    for r in h2_rows(
        db_url,
        ["event_id", "key_id", "event_type", "reason", "occurred_at", "effective_from"],
        "key_lifecycle_events",
    ):
        events.setdefault(r[1], []).append(
            {
                "event_id": r[0], "key_id": r[1], "event_type": r[2],
                "reason": _nul(r[3]), "occurred_at": _ts(r[4]), "effective_from": _ts(r[5]),
            }
        )
    tsas = {
        r[0]: {"valid_from": _ts(r[1]), "valid_until": _ts(r[2])}
        for r in h2_rows(db_url, ["tsa_id", "valid_from", "valid_until"], "timestamp_authorities")
    }
    artifacts = {
        r[0]: {"artifact_id": r[0], "channel_id": r[1], "version": r[2]}
        for r in h2_rows(db_url, ["artifact_id", "channel_id", "version"], "artifacts")
    }
    rows: dict[str, list[dict]] = {a: [] for a in artifacts}
    for r in h2_rows(
        db_url,
        ["evidence_id", "artifact_id", "sha256_digest", "signer_key_id", "signed_at",
         "recorded_at", "status", "supersedes_evidence_id", "amendment_key_id", "tsa_id"],
        "artifact_evidence",
    ):
        rows[r[1]].append(
            {
                "evidence_id": r[0], "artifact_id": r[1], "sha256_digest": r[2],
                "signer_key_id": r[3], "signed_at": _ts(r[4]), "recorded_at": _ts(r[5]),
                "status": r[6], "supersedes_evidence_id": _nul(r[7]),
                "amendment_key_id": _nul(r[8]), "tsa_id": _nul(r[9]),
            }
        )
    queued = [
        r[0]
        for r in h2_rows(db_url, ["artifact_id"], "pending_attestations", "ORDER BY enqueued_at")
    ]
    operative = {a: operative_row(rows[a], keys, events) for a in artifacts}
    return {
        "keys": keys, "events": events, "tsas": tsas, "artifacts": artifacts,
        "rows": rows, "queued": queued, "operative": operative,
        "exposure": exposed_channels(artifacts, operative, events),
    }


def http_get_json(path: str) -> tuple[int, dict]:
    request = urllib.request.Request(API_BASE + path, method="GET")
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            return response.status, json.loads(response.read().decode())
    except urllib.error.HTTPError as exc:
        return exc.code, {}


def http_post_verify(artifact_id: str, digest: str, signature: str) -> int:
    payload = json.dumps(
        {"artifact_id": artifact_id, "digest": digest, "detached_signature": signature}
    ).encode()
    request = urllib.request.Request(
        API_BASE + "/verify", data=payload, method="POST",
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            return response.status
    except urllib.error.HTTPError as exc:
        return exc.code


def api_stage(artifact_id: str, digest: str) -> ReportRow:
    """Ask the live API what happens for this artifact and canonical digest."""
    status, body = http_get_json(f"/artifacts/{artifact_id}")
    if status == 404:
        return ReportRow("denied", "unknown_artifact")
    if status == 503:
        return ReportRow("quarantine", "registry_degraded")
    if status != 200:
        return ReportRow("quarantine", "registry_error")
    verify = http_post_verify(artifact_id, digest, body.get("detached_signature", ""))
    return {
        200: ReportRow("trusted", REASON_VERIFIED),
        400: ReportRow("denied", "bad_signature"),
        404: ReportRow("denied", "unknown_artifact"),
        409: ReportRow("denied", "digest_mismatch"),
        503: ReportRow("quarantine", "verify_degraded"),
    }.get(verify, ReportRow("quarantine", "verify_error"))


def expected_reports_for_db(db_url: str) -> dict[str, ReportRow]:
    """Recompute the policy-correct manifest for whatever store this points at."""
    store = load_store(db_url)
    expected: dict[str, ReportRow] = {}
    for artifact_id in store["queued"]:
        if not store["rows"][artifact_id]:
            expected[artifact_id] = ReportRow("quarantine", REASON_MISSING, None)
            continue
        row = store["operative"][artifact_id]
        if row is None:
            expected[artifact_id] = ReportRow("quarantine", REASON_NO_OPERATIVE, None)
            continue
        defect = signer_defect(row, store["keys"], store["events"], store["tsas"])
        if defect:
            expected[artifact_id] = ReportRow("denied", defect, row["evidence_id"])
            continue
        staged = api_stage(artifact_id, row["sha256_digest"])
        expected[artifact_id] = ReportRow(
            staged.verdict, staged.reason_code, row["evidence_id"]
        )

    for artifact_id, report in list(expected.items()):
        if report.verdict != "trusted":
            continue
        channel = store["artifacts"][artifact_id]["channel_id"]
        exposed_at = store["exposure"].get(channel)
        if exposed_at is None:
            continue
        row = store["operative"][artifact_id]
        if not (countersigned(row, store["tsas"]) and row["signed_at"] < exposed_at):
            expected[artifact_id] = ReportRow(
                "quarantine", REASON_EXPOSURE, row["evidence_id"]
            )
    return expected


def load_pending_artifact_ids(db_url: str = MAIN_DB_URL) -> list[str]:
    return [
        r[0]
        for r in h2_rows(db_url, ["artifact_id"], "pending_attestations", "ORDER BY enqueued_at")
    ]


def load_reports(db_url: str = MAIN_DB_URL) -> dict[str, ReportRow]:
    return {
        r[0]: ReportRow(r[1], r[2], _nul(r[3]))
        for r in h2_rows(
            db_url,
            ["artifact_id", "verdict", "reason_code", "operative_evidence_id"],
            "attestation_reports",
        )
    }


def run_attest_worker(db_url: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["java", "-cp", worker_classpath(), "com.snorkel.attest.Main", db_url],
        capture_output=True, text=True, timeout=300,
    )
