"""Trace the shipped seed through the policy engine and print the 17 verdicts.

Authoring aid. Reads the H2 store directly so it stays honest about what the
database actually holds rather than what the seed file looks like.
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
    """RunScript separates columns with a space, and timestamps contain spaces,
    so concatenate with an explicit delimiter and read back one column."""
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


def main(db_url: str) -> int:
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
        r[0]: {"artifact_id": r[0], "channel_id": r[1]}
        for r in query(db_url, ["artifact_id", "channel_id"], "artifacts")
    }
    rows_by_artifact: dict[str, list[dict]] = {a: [] for a in artifacts}
    for r in query(
        db_url,
        ["evidence_id", "artifact_id", "sha256_digest", "signer_key_id", "signed_at",
         "recorded_at", "status", "supersedes_evidence_id", "amendment_key_id", "tsa_id"],
        "artifact_evidence",
    ):
        rows_by_artifact[r[1]].append(
            {
                "evidence_id": r[0], "artifact_id": r[1], "sha256_digest": r[2],
                "signer_key_id": r[3], "signed_at": ts(r[4]), "recorded_at": ts(r[5]),
                "status": r[6], "supersedes_evidence_id": nul(r[7]),
                "amendment_key_id": nul(r[8]), "tsa_id": nul(r[9]),
            }
        )
    queued = [r[0] for r in query(
        db_url, ["artifact_id"], "pending_attestations", "ORDER BY enqueued_at")]

    operative = {a: operative_row(rows_by_artifact[a], keys, events) for a in artifacts}
    exposure = exposed_channels(artifacts, operative, keys, events)

    verdicts: dict[str, tuple[str, str]] = {}
    for artifact_id in queued:
        rows = rows_by_artifact[artifact_id]
        if not rows:
            verdicts[artifact_id] = ("quarantine", "missing_evidence")
            continue
        row = operative[artifact_id]
        if row is None:
            verdicts[artifact_id] = ("quarantine", "no_operative_evidence")
            continue
        defect = signer_defect(row, keys, events, tsas)
        if defect:
            verdicts[artifact_id] = ("denied", defect)
            continue
        verdicts[artifact_id] = API_STAGE.get(artifact_id, ("trusted", "verified"))

    for artifact_id in queued:
        verdict, reason = verdicts[artifact_id]
        if verdict != "trusted":
            continue
        channel = artifacts[artifact_id]["channel_id"]
        if channel not in exposure:
            continue
        row = operative[artifact_id]
        if not exposure_exempt(row, tsas, exposure[channel]):
            verdicts[artifact_id] = ("quarantine", "channel_exposure")

    print(f"exposed channels: { {c: str(t) for c, t in exposure.items()} }\n")
    for artifact_id in queued:
        row = operative[artifact_id]
        verdict, reason = verdicts[artifact_id]
        print(f"  {artifact_id:13s} {verdict:11s} {reason:25s} operative={row['evidence_id'] if row else 'NONE'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1] if len(sys.argv) > 1 else "jdbc:h2:file:/tmp/attestation"))
