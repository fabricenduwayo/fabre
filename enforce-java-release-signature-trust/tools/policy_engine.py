"""Reference derivation of the signing trust policy.

Used at authoring time to generate the registry fixture and to cross-check the
oracle. The verifier carries its own copy in tests/helpers.py.
"""

from __future__ import annotations

from datetime import datetime

ATTESTED = "attested"
COMPROMISE = "key_compromise"


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


def signer_defect(row: dict, keys: dict, events: dict, tsas: dict) -> str | None:
    """A-2026-09 then A-2026-10. Returns a reason_code or None."""
    key_id = row["signer_key_id"]
    if revoked_at(events.get(key_id, []), row["signed_at"]):
        return "revoked_signer"
    key = keys[key_id]
    if key["not_before"] <= row["signed_at"] < key["not_after"]:
        return None
    tsa = tsas.get(row["tsa_id"]) if row["tsa_id"] else None
    if tsa and tsa["valid_from"] <= row["signed_at"] < tsa["valid_until"]:
        return None
    return "expired_key_signature"


def exposed_channels(
    artifacts: dict, operative: dict, keys: dict, events: dict
) -> dict[str, datetime]:
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


def exposure_exempt(row: dict, tsas: dict, exposed_at: datetime) -> bool:
    """A-2026-11 final paragraph. Countersignature plus strictly earlier signing."""
    tsa = tsas.get(row["tsa_id"]) if row["tsa_id"] else None
    if not tsa:
        return False
    covers = tsa["valid_from"] <= row["signed_at"] < tsa["valid_until"]
    return covers and row["signed_at"] < exposed_at
