"""Trace a store through the policy engine and print the verdicts.

Authoring aid. Reads H2 directly so it stays honest about what the database holds
rather than what the seed file looks like.

  python3 tools/trace_seed.py jdbc:h2:file:/path/to/attestation
"""

from __future__ import annotations

import subprocess
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from policy_engine import (  # noqa: E402
    exposed_channels,
    exposure_exempt,
    operative_row,
    signer_defect,
)

TASK = Path(__file__).resolve().parent.parent
H2_JAR = TASK / "environment" / "lib" / "h2-2.2.224.jar"

# Outcomes fixed by the API fixture rather than by the database.
API_STAGE = {
    "art-alpha": ("denied", "bad_signature"),
    "art-nu": ("quarantine", "verify_degraded"),
}


def ts(value: str) -> datetime | None:
    value = value.strip()
    if not value or value.lower() == "null":
        return None
    return datetime.strptime(value.split(".")[0], "%Y-%m-%d %H:%M:%S")


def nul(value: str) -> str | None:
    value = value.strip()
    return None if not value or value.lower() == "null" else value


def query(db_url: str, columns: list[str], table: str, tail: str = "") -> list[list[str]]:
    """RunScript separates columns with a space and timestamps contain spaces, so
    concatenate with an explicit delimiter and read back a single column."""
    expr = " || '~' || ".join(f"COALESCE(CAST({c} AS VARCHAR), 'NULL')" for c in columns)
    script = Path("/tmp/_trace.sql")
    script.write_text(f"SELECT {expr} FROM {table} {tail};\n")
    out = subprocess.run(
        [
            "java", "-cp", str(H2_JAR), "org.h2.tools.RunScript",
            "-url", db_url, "-user", "sa", "-script", str(script), "-showResults",
        ],
        capture_output=True, text=True, check=True,
    ).stdout
    return [line[4:].split("~") for line in out.splitlines() if line.startswith("--> ")]


def load_store(db_url: str) -> dict:
    keys = {
        r[0]: {"key_id": r[0], "not_before": ts(r[1]), "not_after": ts(r[2])}
        for r in query(db_url, ["key_id", "not_before", "not_after"], "signing_keys")
    }
    events: dict[str, list[dict]] = {}
    for r in query(
        db_url,
        ["event_id", "key_id", "event_type", "reason", "occurred_at", "effective_from"],
        "key_lifecycle_events",
    ):
        events.setdefault(r[1], []).append(
            {
                "event_id": r[0], "key_id": r[1], "event_type": r[2],
                "reason": nul(r[3]), "occurred_at": ts(r[4]), "effective_from": ts(r[5]),
            }
        )
    tsas = {
        r[0]: {"valid_from": ts(r[1]), "valid_until": ts(r[2])}
        for r in query(db_url, ["tsa_id", "valid_from", "valid_until"], "timestamp_authorities")
    }
    artifacts = {
        r[0]: {"artifact_id": r[0], "channel_id": r[1], "version": r[2]}
        for r in query(db_url, ["artifact_id", "channel_id", "version"], "artifacts")
    }
    rows: dict[str, list[dict]] = {a: [] for a in artifacts}
    for r in query(
        db_url,
        ["evidence_id", "artifact_id", "sha256_digest", "signer_key_id", "signed_at",
         "recorded_at", "status", "supersedes_evidence_id", "amendment_key_id", "tsa_id"],
        "artifact_evidence",
    ):
        rows[r[1]].append(
            {
                "evidence_id": r[0], "artifact_id": r[1], "sha256_digest": r[2],
                "signer_key_id": r[3], "signed_at": ts(r[4]), "recorded_at": ts(r[5]),
                "status": r[6], "supersedes_evidence_id": nul(r[7]),
                "amendment_key_id": nul(r[8]), "tsa_id": nul(r[9]),
            }
        )
    queued = [
        r[0]
        for r in query(db_url, ["artifact_id"], "pending_attestations", "ORDER BY enqueued_at")
    ]
    operative = {a: operative_row(rows[a], keys, events) for a in artifacts}
    exposure = exposed_channels(artifacts, operative, keys, events)
    return {
        "keys": keys, "events": events, "tsas": tsas, "artifacts": artifacts,
        "rows": rows, "queued": queued, "operative": operative, "exposure": exposure,
    }


def verdicts_for(store: dict, api_stage: dict | None = None) -> dict[str, tuple[str, str]]:
    api_stage = API_STAGE if api_stage is None else api_stage
    out: dict[str, tuple[str, str]] = {}
    for artifact_id in store["queued"]:
        if not store["rows"][artifact_id]:
            out[artifact_id] = ("quarantine", "missing_evidence")
            continue
        row = store["operative"][artifact_id]
        if row is None:
            out[artifact_id] = ("quarantine", "no_operative_evidence")
            continue
        defect = signer_defect(row, store["keys"], store["events"], store["tsas"])
        if defect:
            out[artifact_id] = ("denied", defect)
            continue
        out[artifact_id] = api_stage.get(artifact_id, ("trusted", "verified"))

    for artifact_id, (verdict, _) in list(out.items()):
        if verdict != "trusted":
            continue
        channel = store["artifacts"][artifact_id]["channel_id"]
        if channel not in store["exposure"]:
            continue
        row = store["operative"][artifact_id]
        if not exposure_exempt(row, store["tsas"], store["exposure"][channel]):
            out[artifact_id] = ("quarantine", "channel_exposure")
    return out


def main(db_url: str) -> int:
    store = load_store(db_url)
    out = verdicts_for(store)
    print(f"exposed channels: { {c: str(t) for c, t in store['exposure'].items()} }\n")
    for artifact_id in store["queued"]:
        row = store["operative"][artifact_id]
        verdict, reason = out[artifact_id]
        operative = row["evidence_id"] if row else "NONE"
        print(f"  {artifact_id:13s} {verdict:11s} {reason:25s} operative={operative}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1] if len(sys.argv) > 1 else "jdbc:h2:file:/tmp/attestation"))
