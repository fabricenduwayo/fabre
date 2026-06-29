"""Canonical model for the Mariner AES-GCM forensic reproduction task.

Used only at authoring time by tools/gen_dataset.py and tools/gen_report.py.
Never copied into the task image.
"""

from __future__ import annotations

import datetime as _dt
import hashlib
from typing import Any

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

REVIEW_DATE = _dt.date(2026, 6, 1)
GIF_PATH = "/app/fixtures/evidence.gif"
JDBC_URL = "jdbc:sqlite:/app/data/forensic_audit.db"

# Explicit nonce overrides (documented in the report appendix).
NONCE_OVERRIDE_FRM003 = bytes.fromhex("A7C3E91B4D2F8065E1B9C0A3")
NONCE_OVERRIDE_FRM006 = bytes.fromhex("3F08D5621CA4790BEE17F2D8")
NONCE_OVERRIDE_FRM007 = bytes.fromhex("B4E19A7305C2D8F61E0A4B9C")
NONCE_OVERRIDE_FRM007_SUPERSEDED = bytes.fromhex("DEADBEEF0000000000000000")
NONCE_OVERRIDE_FRM008 = bytes.fromhex("C1D2E3F4029384758690A1B2C0")
NONCE_OVERRIDE_FRM008_SUPERSEDED = bytes.fromhex("FFFFFFFFFFFFFFFFFFFFFFFF")

FRAMES: list[dict[str, Any]] = [
    {
        "frame_id": "frm-001",
        "label": "alpha-channel",
        "gif_index": 0,
        "plaintext": b"EVIDENCE-ALPHA-CONFIRMED",
        "key_version": 2,
        "key_source": "latest_assigned",
        "nonce_source": "derived",
        "nonce_override": None,
    },
    {
        "frame_id": "frm-002",
        "label": "bravo-channel",
        "gif_index": 1,
        "plaintext": b"EVIDENCE-BRAVO-CONFIRMED",
        "key_version": 3,
        "key_source": "rotation_replacement",
        "nonce_source": "derived",
        "nonce_override": None,
    },
    {
        "frame_id": "frm-003",
        "label": "charlie-channel",
        "gif_index": 2,
        "plaintext": b"EVIDENCE-CHARLIE-CONFIRMED",
        "key_version": 2,
        "key_source": "latest_assigned",
        "nonce_source": "override",
        "nonce_override": NONCE_OVERRIDE_FRM003,
    },
    {
        # Two rotations: v1 -> v2 -> v4. The operative version is the LATEST
        # rotation's replacement (v4), not the first rotation (v2) and not a
        # later stale key_assigned row that restates v2.
        "frame_id": "frm-004",
        "label": "delta-channel",
        "gif_index": 4,
        "plaintext": b"EVIDENCE-DELTA-CONFIRMED",
        "key_version": 4,
        "key_source": "rotation_replacement",
        "nonce_source": "derived",
        "nonce_override": None,
    },
    {
        # Rotation to a LOWER version number (v3 -> v2). replacement_key_version
        # is operative regardless of magnitude; assuming versions only increase
        # picks v3.
        "frame_id": "frm-005",
        "label": "echo-channel",
        "gif_index": 5,
        "plaintext": b"EVIDENCE-ECHO-CONFIRMED",
        "key_version": 2,
        "key_source": "rotation_replacement",
        "nonce_source": "derived",
        "nonce_override": None,
    },
    {
        # Second report override (Appendix D lists two). A reader that only
        # transcribes the frm-003 override misses this one and derives a nonce.
        "frame_id": "frm-006",
        "label": "foxtrot-channel",
        "gif_index": 6,
        "plaintext": b"EVIDENCE-FOXTROT-CONFIRMED",
        "key_version": 2,
        "key_source": "latest_assigned",
        "nonce_source": "override",
        "nonce_override": NONCE_OVERRIDE_FRM006,
    },
    {
        # Nonce override registered only in SQLite — not listed in Appendix D.
        # correlate must walk nonce_override_registered audit rows, not only the
        # report's nonce_overrides map.
        "frame_id": "frm-007",
        "label": "golf-channel",
        "gif_index": 7,
        "plaintext": b"EVIDENCE-GOLF-CONFIRMED",
        "key_version": 2,
        "key_source": "latest_assigned",
        "nonce_source": "override",
        "nonce_override": NONCE_OVERRIDE_FRM007,
    },
    {
        # Two DB nonce registrations; only the latest recorded_at is operative.
        "frame_id": "frm-008",
        "label": "hotel-channel",
        "gif_index": 8,
        "plaintext": b"EVIDENCE-HOTEL-CONFIRMED",
        "key_version": 2,
        "key_source": "latest_assigned",
        "nonce_source": "override",
        "nonce_override": NONCE_OVERRIDE_FRM008,
    },
]

# Decoy frame embedded in the GIF but out of forensic scope.
DECOY_FRAME = {
    "frame_id": "frm-099",
    "label": "decoy-padding",
    "gif_index": 3,
    "plaintext": b"NOT-IN-SCOPE-DECOY",
    "key_version": 1,
}


def key_material(version: int) -> bytes:
    """Deterministic 256-bit AES key for a vault key version."""
    return hashlib.sha256(f"mariner-aes-key-v{version}".encode()).digest()


def derived_nonce(frame_id: str, key_version: int) -> bytes:
    """Default nonce: first 12 bytes of SHA-256(frame_id:key_version)."""
    digest = hashlib.sha256(f"{frame_id}:{key_version}".encode()).digest()
    return digest[:12]


def operative_nonce(frame: dict[str, Any]) -> bytes:
    if frame.get("nonce_override") is not None:
        return frame["nonce_override"]
    return derived_nonce(frame["frame_id"], frame["key_version"])


def encrypt_payload(frame_id: str, plaintext: bytes, key_version: int, nonce: bytes) -> bytes:
    """AES-256-GCM ciphertext || tag, with frame_id as AAD."""
    return AESGCM(key_material(key_version)).encrypt(nonce, plaintext, frame_id.encode())


def plaintext_sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def build_audit_events() -> list[dict[str, Any]]:
    """SQLite audit rows, oldest first within each frame group."""
    rows: list[dict[str, Any]] = []

    # frm-001: single assignment.
    rows.append({
        "frame_id": "frm-001",
        "event_type": "key_assigned",
        "key_version": 2,
        "replacement_key_version": None,
        "nonce_override_hex": None,
        "recorded_at": "2026-05-10 09:00:00",
    })

    # frm-002: assigned v1, then rotated to v3. A naive latest-assigned-only
    # reader that ignores rotation semantics picks v1.
    rows.append({
        "frame_id": "frm-002",
        "event_type": "key_assigned",
        "key_version": 1,
        "replacement_key_version": None,
        "nonce_override_hex": None,
        "recorded_at": "2026-05-04 08:15:00",
    })
    rows.append({
        "frame_id": "frm-002",
        "event_type": "key_rotated",
        "key_version": 1,
        "replacement_key_version": 3,
        "nonce_override_hex": None,
        "recorded_at": "2026-05-18 14:30:00",
    })
    # Stale reassignment that must NOT win over the rotation replacement.
    rows.append({
        "frame_id": "frm-002",
        "event_type": "key_assigned",
        "key_version": 2,
        "replacement_key_version": None,
        "nonce_override_hex": None,
        "recorded_at": "2026-05-20 11:00:00",
    })

    # frm-003: assignment plus a DB nonce override that mirrors the report.
    rows.append({
        "frame_id": "frm-003",
        "event_type": "key_assigned",
        "key_version": 2,
        "replacement_key_version": None,
        "nonce_override_hex": None,
        "recorded_at": "2026-05-12 10:00:00",
    })
    rows.append({
        "frame_id": "frm-003",
        "event_type": "nonce_override_registered",
        "key_version": 2,
        "replacement_key_version": None,
        "nonce_override_hex": NONCE_OVERRIDE_FRM003.hex().upper(),
        "recorded_at": "2026-05-22 16:45:00",
    })

    # frm-004: assigned v1, rotated v1->v2, rotated again v2->v4, then a stale
    # reassignment of v2. The operative version is the latest rotation's
    # replacement (v4).
    rows.append({
        "frame_id": "frm-004",
        "event_type": "key_assigned",
        "key_version": 1,
        "replacement_key_version": None,
        "nonce_override_hex": None,
        "recorded_at": "2026-05-02 09:00:00",
    })
    rows.append({
        "frame_id": "frm-004",
        "event_type": "key_rotated",
        "key_version": 1,
        "replacement_key_version": 2,
        "nonce_override_hex": None,
        "recorded_at": "2026-05-09 10:00:00",
    })
    rows.append({
        "frame_id": "frm-004",
        "event_type": "key_rotated",
        "key_version": 2,
        "replacement_key_version": 4,
        "nonce_override_hex": None,
        "recorded_at": "2026-05-21 11:00:00",
    })
    rows.append({
        "frame_id": "frm-004",
        "event_type": "key_assigned",
        "key_version": 2,
        "replacement_key_version": None,
        "nonce_override_hex": None,
        "recorded_at": "2026-05-25 12:00:00",
    })

    # frm-005: assigned v3, rotated down to v2. Rotation replacement wins even
    # though the version number decreases.
    rows.append({
        "frame_id": "frm-005",
        "event_type": "key_assigned",
        "key_version": 3,
        "replacement_key_version": None,
        "nonce_override_hex": None,
        "recorded_at": "2026-05-06 09:00:00",
    })
    rows.append({
        "frame_id": "frm-005",
        "event_type": "key_rotated",
        "key_version": 3,
        "replacement_key_version": 2,
        "nonce_override_hex": None,
        "recorded_at": "2026-05-19 14:00:00",
    })

    # frm-006: single assignment; nonce comes from the report override (Appendix D).
    rows.append({
        "frame_id": "frm-006",
        "event_type": "key_assigned",
        "key_version": 2,
        "replacement_key_version": None,
        "nonce_override_hex": None,
        "recorded_at": "2026-05-08 09:00:00",
    })

    # frm-007: assignment plus DB-only nonce override (no Appendix D entry).
    # An earlier superseded registration must not win over the later one.
    rows.append({
        "frame_id": "frm-007",
        "event_type": "key_assigned",
        "key_version": 2,
        "replacement_key_version": None,
        "nonce_override_hex": None,
        "recorded_at": "2026-05-11 10:00:00",
    })
    rows.append({
        "frame_id": "frm-007",
        "event_type": "nonce_override_registered",
        "key_version": 2,
        "replacement_key_version": None,
        "nonce_override_hex": NONCE_OVERRIDE_FRM007_SUPERSEDED.hex().upper(),
        "recorded_at": "2026-05-20 14:00:00",
    })
    rows.append({
        "frame_id": "frm-007",
        "event_type": "nonce_override_registered",
        "key_version": 2,
        "replacement_key_version": None,
        "nonce_override_hex": NONCE_OVERRIDE_FRM007.hex().upper(),
        "recorded_at": "2026-05-23 15:30:00",
    })

    # frm-008: assignment plus two nonce registrations; latest wins.
    rows.append({
        "frame_id": "frm-008",
        "event_type": "key_assigned",
        "key_version": 2,
        "replacement_key_version": None,
        "nonce_override_hex": None,
        "recorded_at": "2026-05-13 09:00:00",
    })
    rows.append({
        "frame_id": "frm-008",
        "event_type": "nonce_override_registered",
        "key_version": 2,
        "replacement_key_version": None,
        "nonce_override_hex": NONCE_OVERRIDE_FRM008_SUPERSEDED.hex().upper(),
        "recorded_at": "2026-05-21 10:00:00",
    })
    rows.append({
        "frame_id": "frm-008",
        "event_type": "nonce_override_registered",
        "key_version": 2,
        "replacement_key_version": None,
        "nonce_override_hex": NONCE_OVERRIDE_FRM008.hex().upper(),
        "recorded_at": "2026-05-24 16:00:00",
    })

    return rows


def rules_expected() -> dict[str, Any]:
    return {
        "review_date": REVIEW_DATE.isoformat(),
        "key_selection_precedence": [
            "rotation_replacement",
            "latest_key_assigned",
        ],
        "nonce_selection_precedence": [
            "report_override",
            "derived_sha256_prefix",
        ],
        "derived_nonce_rule": "SHA-256(frame_id + ':' + key_version), first 12 bytes",
        "nonce_overrides": {
            "frm-003": NONCE_OVERRIDE_FRM003.hex().upper(),
            "frm-006": NONCE_OVERRIDE_FRM006.hex().upper(),
        },
    }


def resolve_key_version(frame_id: str, events: list[dict[str, Any]]) -> tuple[int, str]:
    """Pick operative key version from audit timeline + exception precedence."""
    frame_events = [e for e in events if e["frame_id"] == frame_id]
    rotations = [e for e in frame_events if e["event_type"] == "key_rotated"]
    if rotations:
        latest = max(rotations, key=lambda e: e["recorded_at"])
        return latest["replacement_key_version"], "rotation_replacement"
    assigned = [e for e in frame_events if e["event_type"] == "key_assigned"]
    latest = max(assigned, key=lambda e: e["recorded_at"])
    return latest["key_version"], "latest_assigned"


def resolve_nonce(
    frame_id: str,
    key_version: int,
    rules: dict[str, Any],
    events: list[dict[str, Any]],
) -> tuple[bytes, str]:
  overrides = rules.get("nonce_overrides", {})
  if frame_id in overrides:
      return bytes.fromhex(overrides[frame_id]), "override"
  frame_events = [
      e for e in events
      if e["frame_id"] == frame_id and e["event_type"] == "nonce_override_registered"
  ]
  if frame_events:
      latest = max(frame_events, key=lambda e: e["recorded_at"])
      return bytes.fromhex(latest["nonce_override_hex"]), "override"
  return derived_nonce(frame_id, key_version), "derived"


def correlation_expected() -> list[dict[str, Any]]:
    events = build_audit_events()
    rules = rules_expected()
    out: list[dict[str, Any]] = []
    for frame in FRAMES:
        kv, key_source = resolve_key_version(frame["frame_id"], events)
        nonce, nonce_source = resolve_nonce(frame["frame_id"], kv, rules, events)
        out.append({
            "frame_id": frame["frame_id"],
            "label": frame["label"],
            "gif_index": frame["gif_index"],
            "key_version": kv,
            "key_source": key_source,
            "nonce_hex": nonce.hex().upper(),
            "nonce_source": nonce_source,
        })
    return out


def findings_expected() -> list[dict[str, Any]]:
    events = build_audit_events()
    rules = rules_expected()
    out: list[dict[str, Any]] = []
    for frame in FRAMES:
        kv, key_source = resolve_key_version(frame["frame_id"], events)
        nonce, nonce_source = resolve_nonce(frame["frame_id"], kv, rules, events)
        pt = frame["plaintext"]
        try:
            AESGCM(key_material(kv)).decrypt(nonce, encrypt_payload(
                frame["frame_id"], pt, kv, nonce
            ), frame["frame_id"].encode())
            auth_ok = True
            reason = "authenticated"
        except Exception:
            auth_ok = False
            reason = "auth_failed"
        out.append({
            "frame_id": frame["frame_id"],
            "label": frame["label"],
            "gif_index": frame["gif_index"],
            "key_version": kv,
            "key_source": key_source,
            "nonce_hex": nonce.hex().upper(),
            "nonce_source": nonce_source,
            "auth_ok": auth_ok,
            "plaintext_sha256": plaintext_sha256(pt),
            "reason_code": reason,
        })
    return out


def aggregate_counts() -> dict[str, int]:
    counts = {"authenticated": 0, "auth_failed": 0}
    for f in findings_expected():
        if f["auth_ok"]:
            counts["authenticated"] += 1
        else:
            counts["auth_failed"] += 1
    return counts


if __name__ == "__main__":
    import json

    print("frames:", len(FRAMES))
    print("aggregate:", aggregate_counts())
    print("correlation sample:", json.dumps(correlation_expected()[1], indent=2))
