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
NONCE_OVERRIDE_FRM008 = bytes.fromhex("C1D2E3F4029384758690A1B2")
NONCE_OVERRIDE_FRM008_SUPERSEDED = bytes.fromhex("FFFFFFFFFFFFFFFFFFFFFFFF")
NONCE_OVERRIDE_FRM008_REVOKED = bytes.fromhex("AABBCCDDEEFF001122334455")
NONCE_OVERRIDE_FRM013_SURVIVOR = bytes.fromhex("112233445566778899AABBCC")
NONCE_OVERRIDE_FRM013_REVOKED = bytes.fromhex("FFEEDDCCBBAA998877665544")
NONCE_OVERRIDE_FRM010 = bytes.fromhex("0A1B2C3D4E5F60718293A4B5")
NONCE_OVERRIDE_FRM010_DB = bytes.fromhex("FEEDFACECAFE000000000001")
NONCE_OVERRIDE_FRM012 = bytes.fromhex("D0E1F2A3B4C5D6E7F8091A2B")
NONCE_OVERRIDE_FRM006_SUPERSEDED = bytes.fromhex("0102030405060708090A0B0C")
NONCE_OVERRIDE_FRM014 = bytes.fromhex("ABCDEF0123456789ABCDEF01")
NONCE_OVERRIDE_FRM014_STALE_V2 = bytes.fromhex("000102030405060708090A0B")
NONCE_OVERRIDE_FRM014_LATE_STALE = bytes.fromhex("998877665544332211009988")
NONCE_OVERRIDE_FRM015 = bytes.fromhex("13579BDF2468ACE024681ACE")
NONCE_FRM016_EARLY = bytes.fromhex("AABBCCDDEEFF001122334455")
NONCE_FRM016_TO_AMEND = bytes.fromhex("112233445566778899AABBCC")
NONCE_FRM016_RESULT = bytes.fromhex("33445566778899AABBCCDDEE")
NONCE_FRM017_AAA = bytes.fromhex("5566778899AABBCCDDEEFF00")
NONCE_FRM017_BBB = bytes.fromhex("66778899AABBCCDDEEFF0011")
NONCE_FRM017_CCC = bytes.fromhex("778899AABBCCDDEEFF001122")
NONCE_FRM020_AAA = bytes.fromhex("A1B2C3D4E5F60718293A4B5C")
NONCE_FRM020_BBB = bytes.fromhex("B2C3D4E5F60718293A4B5C6D")
NONCE_FRM020_CCC = bytes.fromhex("C3D4E5F60718293A4B5C6D7E")
NONCE_FRM020_DDD = bytes.fromhex("D4E5F60718293A4B5C6D7E8F")
NONCE_OVERRIDE_FRM022 = bytes.fromhex("E1F2A3B4C5D67890ABCDEF01")
NONCE_OVERRIDE_FRM022_DB = bytes.fromhex("FACEFACEFACEFACEFACEFACE")
NONCE_FRM023_AAA = bytes.fromhex("1A2B3C4D5E6F708192A3B4C5")
NONCE_FRM023_BBB = bytes.fromhex("2B3C4D5E6F708192A3B4C5D6")
NONCE_FRM023_CCC = bytes.fromhex("3C4D5E6F708192A3B4C5D6E7")
NONCE_FRM024_V2 = bytes.fromhex("4D5E6F708192A3B4C5D6E7F8")
NONCE_FRM024_EEE = bytes.fromhex("5E6F708192A3B4C5D6E7F809")
NONCE_FRM024_FFF = bytes.fromhex("6F708192A3B4C5D6E7F8091A")
NONCE_FRM024_GGG = bytes.fromhex("708192A3B4C5D6E7F8091A2B")

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
    {
        # Single rotation to a high version (v2 -> v5) with a later stale
        # key_assigned v3. Operative version is v5, not v3.
        "frame_id": "frm-009",
        "label": "india-channel",
        "gif_index": 9,
        "plaintext": b"EVIDENCE-INDIA-CONFIRMED",
        "key_version": 5,
        "key_source": "rotation_replacement",
        "nonce_source": "derived",
        "nonce_override": None,
    },
    {
        # Appendix D names an override; SQLite also has a later
        # nonce_override_registered row with a different value. Report
        # precedence wins — taking the latest DB registration alone fails.
        "frame_id": "frm-010",
        "label": "juliet-channel",
        "gif_index": 10,
        "plaintext": b"EVIDENCE-JULIET-CONFIRMED",
        "key_version": 2,
        "key_source": "latest_assigned",
        "nonce_source": "override",
        "nonce_override": NONCE_OVERRIDE_FRM010,
    },
    {
        # Three rotations ending v2->v4, then a stale high-version assign.
        # Operative key is v4 from the latest rotation, not v6 from max
        # replacement or the stale reassignment.
        "frame_id": "frm-011",
        "label": "kilo-channel",
        "gif_index": 11,
        "plaintext": b"EVIDENCE-KILO-CONFIRMED",
        "key_version": 4,
        "key_source": "rotation_replacement",
        "nonce_source": "derived",
        "nonce_override": None,
    },
    {
        # DB nonce override registered for v2, then key_rotated v2->v4.
        # The override binds to key_version at registration; after rotation
        # the operative key is v4 so derived nonce wins — taking the DB row
        # alone decrypts with the wrong nonce.
        "frame_id": "frm-012",
        "label": "lima-channel",
        "gif_index": 12,
        "plaintext": b"EVIDENCE-LIMA-CONFIRMED",
        "key_version": 4,
        "key_source": "rotation_replacement",
        "nonce_source": "derived",
        "nonce_override": None,
    },
    {
        # A later DB registration was revoked; rotation then voids the survivor
        # because both registrations bind to v2 while the operative key is v4.
        "frame_id": "frm-013",
        "label": "mike-channel",
        "gif_index": 13,
        "plaintext": b"EVIDENCE-MIKE-CONFIRMED",
        "key_version": 4,
        "key_source": "rotation_replacement",
        "nonce_source": "derived",
        "nonce_override": None,
    },
    {
        # DB nonce registered for v2, rotated to v4, then re-registered for v4.
        # A later v2 registration after rotation must not beat the v4 match.
        "frame_id": "frm-014",
        "label": "november-channel",
        "gif_index": 14,
        "plaintext": b"EVIDENCE-NOVEMBER-CONFIRMED",
        "key_version": 4,
        "key_source": "rotation_replacement",
        "nonce_source": "override",
        "nonce_override": NONCE_OVERRIDE_FRM014,
    },
    {
        # Appendix D override survives key rotation — nonce stays fixed while
        # the operative key version moves to the rotation replacement.
        "frame_id": "frm-015",
        "label": "oscar-channel",
        "gif_index": 15,
        "plaintext": b"EVIDENCE-OSCAR-CONFIRMED",
        "key_version": 4,
        "key_source": "rotation_replacement",
        "nonce_source": "override",
        "nonce_override": NONCE_OVERRIDE_FRM015,
    },
    {
        # DB-only: a later registration is amended away; the amendment result
        # is operative, not the pre-amend registration bytes.
        "frame_id": "frm-016",
        "label": "papa-channel",
        "gif_index": 16,
        "plaintext": b"EVIDENCE-PAPA-CONFIRMED",
        "key_version": 2,
        "key_source": "latest_assigned",
        "nonce_source": "override",
        "nonce_override": NONCE_FRM016_RESULT,
    },
    {
        # Post-rotation DB path: amendment voids a registration, then the same
        # nonce bytes are registered again — the re-registration wins over the
        # amendment result. A stale v2 row after rotation must not beat the match.
        "frame_id": "frm-017",
        "label": "quebec-channel",
        "gif_index": 17,
        "plaintext": b"EVIDENCE-QUEBEC-CONFIRMED",
        "key_version": 4,
        "key_source": "rotation_replacement",
        "nonce_source": "override",
        "nonce_override": NONCE_FRM017_BBB,
    },
    {
        # A later key_assigned row is voided by key_assignment_rescinded before
        # key selection runs — taking the latest assign without filtering rescissions
        # picks v6 instead of v2.
        "frame_id": "frm-018",
        "label": "sierra-channel",
        "gif_index": 18,
        "plaintext": b"EVIDENCE-SIERRA-CONFIRMED",
        "key_version": 2,
        "key_source": "latest_assigned",
        "nonce_source": "derived",
        "nonce_override": None,
    },
    {
        # Chained rotations v1->v3 then v3->v5; the second hop is rescinded so the
        # operative version is v3 from the surviving first hop, not v5.
        "frame_id": "frm-019",
        "label": "tango-channel",
        "gif_index": 19,
        "plaintext": b"EVIDENCE-TANGO-CONFIRMED",
        "key_version": 3,
        "key_source": "rotation_replacement",
        "nonce_source": "derived",
        "nonce_override": None,
    },
    {
        # Two sequential nonce_override_amended events; only the final amendment
        # result is operative, not the intermediate registration bytes.
        "frame_id": "frm-020",
        "label": "uniform-channel",
        "gif_index": 20,
        "plaintext": b"EVIDENCE-UNIFORM-CONFIRMED",
        "key_version": 2,
        "key_source": "latest_assigned",
        "nonce_source": "override",
        "nonce_override": NONCE_FRM020_DDD,
    },
    {
        # Every key_rotated row is rescinded — must fall back to latest_key_assigned
        # after filtering key_assignment_rescinded, not treat voided rotations as operative.
        "frame_id": "frm-021",
        "label": "victor-channel",
        "gif_index": 21,
        "plaintext": b"EVIDENCE-VICTOR-CONFIRMED",
        "key_version": 2,
        "key_source": "latest_assigned",
        "nonce_source": "derived",
        "nonce_override": None,
    },
    {
        # Fifth Appendix D override — readers that stop after four report entries miss this.
        "frame_id": "frm-022",
        "label": "whiskey-channel",
        "gif_index": 22,
        "plaintext": b"EVIDENCE-WHISKEY-CONFIRMED",
        "key_version": 4,
        "key_source": "rotation_replacement",
        "nonce_source": "override",
        "nonce_override": NONCE_OVERRIDE_FRM022,
    },
    {
        # DB-only: register A, replace A->B, rescind replacement (restore A),
        # replace A->C — operative nonce is C, not B or the first registration.
        "frame_id": "frm-023",
        "label": "xray-channel",
        "gif_index": 23,
        "plaintext": b"EVIDENCE-XRAY-CONFIRMED",
        "key_version": 2,
        "key_source": "latest_assigned",
        "nonce_source": "override",
        "nonce_override": NONCE_FRM023_CCC,
    },
    {
        # Rotation voids a replacement-scoped override; operative key v5 with a
        # fresh v5 registration — keeping the v4 replacement bytes fails decrypt.
        "frame_id": "frm-024",
        "label": "yankee-channel",
        "gif_index": 24,
        "plaintext": b"EVIDENCE-YANKEE-CONFIRMED",
        "key_version": 5,
        "key_source": "rotation_replacement",
        "nonce_source": "override",
        "nonce_override": NONCE_FRM024_GGG,
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
    rows.append({
        "frame_id": "frm-008",
        "event_type": "nonce_override_registered",
        "key_version": 2,
        "replacement_key_version": None,
        "nonce_override_hex": NONCE_OVERRIDE_FRM008_REVOKED.hex().upper(),
        "recorded_at": "2026-05-26 18:00:00",
    })
    rows.append({
        "frame_id": "frm-008",
        "event_type": "nonce_override_revoked",
        "key_version": 2,
        "replacement_key_version": None,
        "nonce_override_hex": NONCE_OVERRIDE_FRM008_REVOKED.hex().upper(),
        "recorded_at": "2026-05-27 09:00:00",
    })

    # frm-009: assigned v2, rotated v2->v5, a later v2->v4 correction rotation that
    # is rescinded, then stale reassignment of v3. A reader that takes the latest
    # key_rotated without filtering rescissions picks v4; the operative version is
    # v5 from the surviving v2->v5 rotation.
    rows.append({
        "frame_id": "frm-009",
        "event_type": "key_assigned",
        "key_version": 2,
        "replacement_key_version": None,
        "nonce_override_hex": None,
        "recorded_at": "2026-05-07 08:00:00",
    })
    rows.append({
        "frame_id": "frm-009",
        "event_type": "key_rotated",
        "key_version": 2,
        "replacement_key_version": 5,
        "nonce_override_hex": None,
        "recorded_at": "2026-05-17 12:00:00",
    })
    rows.append({
        "frame_id": "frm-009",
        "event_type": "key_rotated",
        "key_version": 2,
        "replacement_key_version": 4,
        "nonce_override_hex": None,
        "recorded_at": "2026-05-20 10:00:00",
    })
    rows.append({
        "frame_id": "frm-009",
        "event_type": "key_rotation_rescinded",
        "key_version": 2,
        "replacement_key_version": 4,
        "nonce_override_hex": None,
        "recorded_at": "2026-05-21 11:00:00",
    })
    rows.append({
        "frame_id": "frm-009",
        "event_type": "key_assigned",
        "key_version": 3,
        "replacement_key_version": None,
        "nonce_override_hex": None,
        "recorded_at": "2026-05-26 09:00:00",
    })

    # frm-010: report override in Appendix D plus a later DB registration that
    # must not supersede the report value.
    rows.append({
        "frame_id": "frm-010",
        "event_type": "key_assigned",
        "key_version": 2,
        "replacement_key_version": None,
        "nonce_override_hex": None,
        "recorded_at": "2026-05-14 08:00:00",
    })
    rows.append({
        "frame_id": "frm-010",
        "event_type": "nonce_override_registered",
        "key_version": 2,
        "replacement_key_version": None,
        "nonce_override_hex": NONCE_OVERRIDE_FRM010_DB.hex().upper(),
        "recorded_at": "2026-05-27 17:00:00",
    })

    # frm-011: v1 -> v6 -> v2 -> v4, then stale assign v6.
    rows.append({
        "frame_id": "frm-011",
        "event_type": "key_assigned",
        "key_version": 1,
        "replacement_key_version": None,
        "nonce_override_hex": None,
        "recorded_at": "2026-05-01 08:00:00",
    })
    rows.append({
        "frame_id": "frm-011",
        "event_type": "key_rotated",
        "key_version": 1,
        "replacement_key_version": 6,
        "nonce_override_hex": None,
        "recorded_at": "2026-05-08 10:00:00",
    })
    rows.append({
        "frame_id": "frm-011",
        "event_type": "key_rotated",
        "key_version": 6,
        "replacement_key_version": 2,
        "nonce_override_hex": None,
        "recorded_at": "2026-05-15 11:00:00",
    })
    rows.append({
        "frame_id": "frm-011",
        "event_type": "key_rotated",
        "key_version": 2,
        "replacement_key_version": 4,
        "nonce_override_hex": None,
        "recorded_at": "2026-05-22 14:00:00",
    })
    rows.append({
        "frame_id": "frm-011",
        "event_type": "key_assigned",
        "key_version": 6,
        "replacement_key_version": None,
        "nonce_override_hex": None,
        "recorded_at": "2026-05-28 09:00:00",
    })

    # frm-012: nonce override registered for v2, then rotated v2->v4. The DB
    # override must be ignored once the operative key version differs.
    rows.append({
        "frame_id": "frm-012",
        "event_type": "key_assigned",
        "key_version": 2,
        "replacement_key_version": None,
        "nonce_override_hex": None,
        "recorded_at": "2026-05-09 09:00:00",
    })
    rows.append({
        "frame_id": "frm-012",
        "event_type": "nonce_override_registered",
        "key_version": 2,
        "replacement_key_version": None,
        "nonce_override_hex": NONCE_OVERRIDE_FRM012.hex().upper(),
        "recorded_at": "2026-05-18 10:00:00",
    })
    rows.append({
        "frame_id": "frm-012",
        "event_type": "key_rotated",
        "key_version": 2,
        "replacement_key_version": 4,
        "nonce_override_hex": None,
        "recorded_at": "2026-05-24 14:00:00",
    })

    # frm-013: survivor registration, later registration revoked, then rotation.
    rows.append({
        "frame_id": "frm-013",
        "event_type": "key_assigned",
        "key_version": 2,
        "replacement_key_version": None,
        "nonce_override_hex": None,
        "recorded_at": "2026-05-10 08:00:00",
    })
    rows.append({
        "frame_id": "frm-013",
        "event_type": "nonce_override_registered",
        "key_version": 2,
        "replacement_key_version": None,
        "nonce_override_hex": NONCE_OVERRIDE_FRM013_SURVIVOR.hex().upper(),
        "recorded_at": "2026-05-15 10:00:00",
    })
    rows.append({
        "frame_id": "frm-013",
        "event_type": "nonce_override_registered",
        "key_version": 2,
        "replacement_key_version": None,
        "nonce_override_hex": NONCE_OVERRIDE_FRM013_REVOKED.hex().upper(),
        "recorded_at": "2026-05-20 14:00:00",
    })
    rows.append({
        "frame_id": "frm-013",
        "event_type": "nonce_override_revoked",
        "key_version": 2,
        "replacement_key_version": None,
        "nonce_override_hex": NONCE_OVERRIDE_FRM013_REVOKED.hex().upper(),
        "recorded_at": "2026-05-22 11:00:00",
    })
    rows.append({
        "frame_id": "frm-013",
        "event_type": "key_rotated",
        "key_version": 2,
        "replacement_key_version": 4,
        "nonce_override_hex": None,
        "recorded_at": "2026-05-25 16:00:00",
    })

    # frm-014: v2 override, rotate v2->v4, stale v2 re-register, then v4 register.
    rows.append({
        "frame_id": "frm-014",
        "event_type": "key_assigned",
        "key_version": 2,
        "replacement_key_version": None,
        "nonce_override_hex": None,
        "recorded_at": "2026-05-10 09:00:00",
    })
    rows.append({
        "frame_id": "frm-014",
        "event_type": "nonce_override_registered",
        "key_version": 2,
        "replacement_key_version": None,
        "nonce_override_hex": NONCE_OVERRIDE_FRM014_STALE_V2.hex().upper(),
        "recorded_at": "2026-05-12 10:00:00",
    })
    rows.append({
        "frame_id": "frm-014",
        "event_type": "key_rotated",
        "key_version": 2,
        "replacement_key_version": 4,
        "nonce_override_hex": None,
        "recorded_at": "2026-05-18 14:00:00",
    })
    rows.append({
        "frame_id": "frm-014",
        "event_type": "nonce_override_registered",
        "key_version": 2,
        "replacement_key_version": None,
        "nonce_override_hex": NONCE_OVERRIDE_FRM014_LATE_STALE.hex().upper(),
        "recorded_at": "2026-05-20 11:00:00",
    })
    rows.append({
        "frame_id": "frm-014",
        "event_type": "nonce_override_registered",
        "key_version": 4,
        "replacement_key_version": None,
        "nonce_override_hex": NONCE_OVERRIDE_FRM014.hex().upper(),
        "recorded_at": "2026-05-22 16:00:00",
    })

    # frm-015: report override; rotate v2->v4; report nonce still operative.
    rows.append({
        "frame_id": "frm-015",
        "event_type": "key_assigned",
        "key_version": 2,
        "replacement_key_version": None,
        "nonce_override_hex": None,
        "supersedes_nonce_hex": None,
        "recorded_at": "2026-05-08 08:00:00",
    })
    rows.append({
        "frame_id": "frm-015",
        "event_type": "key_rotated",
        "key_version": 2,
        "replacement_key_version": 4,
        "nonce_override_hex": None,
        "supersedes_nonce_hex": None,
        "recorded_at": "2026-05-16 12:00:00",
    })

    # frm-016: two registrations then an amendment voiding the latest reg.
    rows.append({
        "frame_id": "frm-016",
        "event_type": "key_assigned",
        "key_version": 2,
        "replacement_key_version": None,
        "nonce_override_hex": None,
        "supersedes_nonce_hex": None,
        "recorded_at": "2026-05-09 09:00:00",
    })
    rows.append({
        "frame_id": "frm-016",
        "event_type": "nonce_override_registered",
        "key_version": 2,
        "replacement_key_version": None,
        "nonce_override_hex": NONCE_FRM016_EARLY.hex().upper(),
        "supersedes_nonce_hex": None,
        "recorded_at": "2026-05-14 10:00:00",
    })
    rows.append({
        "frame_id": "frm-016",
        "event_type": "nonce_override_registered",
        "key_version": 2,
        "replacement_key_version": None,
        "nonce_override_hex": NONCE_FRM016_TO_AMEND.hex().upper(),
        "supersedes_nonce_hex": None,
        "recorded_at": "2026-05-18 11:00:00",
    })
    rows.append({
        "frame_id": "frm-016",
        "event_type": "nonce_override_amended",
        "key_version": 2,
        "replacement_key_version": None,
        "nonce_override_hex": NONCE_FRM016_RESULT.hex().upper(),
        "supersedes_nonce_hex": NONCE_FRM016_TO_AMEND.hex().upper(),
        "recorded_at": "2026-05-22 15:00:00",
    })

    # frm-017: rotate first, then DB registrations with amend + re-register.
    rows.append({
        "frame_id": "frm-017",
        "event_type": "key_assigned",
        "key_version": 2,
        "replacement_key_version": None,
        "nonce_override_hex": None,
        "supersedes_nonce_hex": None,
        "recorded_at": "2026-05-07 08:00:00",
    })
    rows.append({
        "frame_id": "frm-017",
        "event_type": "key_rotated",
        "key_version": 2,
        "replacement_key_version": 4,
        "nonce_override_hex": None,
        "supersedes_nonce_hex": None,
        "recorded_at": "2026-05-15 12:00:00",
    })
    rows.append({
        "frame_id": "frm-017",
        "event_type": "nonce_override_registered",
        "key_version": 4,
        "replacement_key_version": None,
        "nonce_override_hex": NONCE_FRM017_AAA.hex().upper(),
        "supersedes_nonce_hex": None,
        "recorded_at": "2026-05-19 10:00:00",
    })
    rows.append({
        "frame_id": "frm-017",
        "event_type": "nonce_override_registered",
        "key_version": 4,
        "replacement_key_version": None,
        "nonce_override_hex": NONCE_FRM017_BBB.hex().upper(),
        "supersedes_nonce_hex": None,
        "recorded_at": "2026-05-21 14:00:00",
    })
    rows.append({
        "frame_id": "frm-017",
        "event_type": "nonce_override_amended",
        "key_version": 4,
        "replacement_key_version": None,
        "nonce_override_hex": NONCE_FRM017_CCC.hex().upper(),
        "supersedes_nonce_hex": NONCE_FRM017_BBB.hex().upper(),
        "recorded_at": "2026-05-23 16:00:00",
    })
    rows.append({
        "frame_id": "frm-017",
        "event_type": "nonce_override_registered",
        "key_version": 4,
        "replacement_key_version": None,
        "nonce_override_hex": NONCE_FRM017_BBB.hex().upper(),
        "supersedes_nonce_hex": None,
        "recorded_at": "2026-05-25 18:00:00",
    })
    rows.append({
        "frame_id": "frm-017",
        "event_type": "nonce_override_registered",
        "key_version": 2,
        "replacement_key_version": None,
        "nonce_override_hex": NONCE_FRM017_AAA.hex().upper(),
        "supersedes_nonce_hex": None,
        "recorded_at": "2026-05-26 09:00:00",
    })

    # frm-018: assigned v2, assigned v6, rescinded v6 — operative assign is v2.
    rows.append({
        "frame_id": "frm-018",
        "event_type": "key_assigned",
        "key_version": 2,
        "replacement_key_version": None,
        "nonce_override_hex": None,
        "supersedes_nonce_hex": None,
        "recorded_at": "2026-05-08 08:00:00",
    })
    rows.append({
        "frame_id": "frm-018",
        "event_type": "key_assigned",
        "key_version": 6,
        "replacement_key_version": None,
        "nonce_override_hex": None,
        "supersedes_nonce_hex": None,
        "recorded_at": "2026-05-20 14:00:00",
    })
    rows.append({
        "frame_id": "frm-018",
        "event_type": "key_assignment_rescinded",
        "key_version": 6,
        "replacement_key_version": None,
        "nonce_override_hex": None,
        "supersedes_nonce_hex": None,
        "recorded_at": "2026-05-22 16:00:00",
    })

    # frm-019: v1->v3 then v3->v5 with the second hop rescinded.
    rows.append({
        "frame_id": "frm-019",
        "event_type": "key_assigned",
        "key_version": 1,
        "replacement_key_version": None,
        "nonce_override_hex": None,
        "supersedes_nonce_hex": None,
        "recorded_at": "2026-05-05 08:00:00",
    })
    rows.append({
        "frame_id": "frm-019",
        "event_type": "key_rotated",
        "key_version": 1,
        "replacement_key_version": 3,
        "nonce_override_hex": None,
        "supersedes_nonce_hex": None,
        "recorded_at": "2026-05-12 10:00:00",
    })
    rows.append({
        "frame_id": "frm-019",
        "event_type": "key_rotated",
        "key_version": 3,
        "replacement_key_version": 5,
        "nonce_override_hex": None,
        "supersedes_nonce_hex": None,
        "recorded_at": "2026-05-18 14:00:00",
    })
    rows.append({
        "frame_id": "frm-019",
        "event_type": "key_rotation_rescinded",
        "key_version": 3,
        "replacement_key_version": 5,
        "nonce_override_hex": None,
        "supersedes_nonce_hex": None,
        "recorded_at": "2026-05-19 15:00:00",
    })

    # frm-020: two sequential amendments after two registrations.
    rows.append({
        "frame_id": "frm-020",
        "event_type": "key_assigned",
        "key_version": 2,
        "replacement_key_version": None,
        "nonce_override_hex": None,
        "supersedes_nonce_hex": None,
        "recorded_at": "2026-05-09 09:00:00",
    })
    rows.append({
        "frame_id": "frm-020",
        "event_type": "nonce_override_registered",
        "key_version": 2,
        "replacement_key_version": None,
        "nonce_override_hex": NONCE_FRM020_AAA.hex().upper(),
        "supersedes_nonce_hex": None,
        "recorded_at": "2026-05-14 10:00:00",
    })
    rows.append({
        "frame_id": "frm-020",
        "event_type": "nonce_override_registered",
        "key_version": 2,
        "replacement_key_version": None,
        "nonce_override_hex": NONCE_FRM020_BBB.hex().upper(),
        "supersedes_nonce_hex": None,
        "recorded_at": "2026-05-16 11:00:00",
    })
    rows.append({
        "frame_id": "frm-020",
        "event_type": "nonce_override_amended",
        "key_version": 2,
        "replacement_key_version": None,
        "nonce_override_hex": NONCE_FRM020_CCC.hex().upper(),
        "supersedes_nonce_hex": NONCE_FRM020_BBB.hex().upper(),
        "recorded_at": "2026-05-20 14:00:00",
    })
    rows.append({
        "frame_id": "frm-020",
        "event_type": "nonce_override_amended",
        "key_version": 2,
        "replacement_key_version": None,
        "nonce_override_hex": NONCE_FRM020_DDD.hex().upper(),
        "supersedes_nonce_hex": NONCE_FRM020_CCC.hex().upper(),
        "recorded_at": "2026-05-24 16:00:00",
    })

    # frm-021: every rotation rescinded — assignment fallback after rescission filtering.
    rows.append({
        "frame_id": "frm-021",
        "event_type": "key_assigned",
        "key_version": 2,
        "replacement_key_version": None,
        "nonce_override_hex": None,
        "supersedes_nonce_hex": None,
        "recorded_at": "2026-05-08 08:00:00",
    })
    rows.append({
        "frame_id": "frm-021",
        "event_type": "key_rotated",
        "key_version": 2,
        "replacement_key_version": 4,
        "nonce_override_hex": None,
        "supersedes_nonce_hex": None,
        "recorded_at": "2026-05-15 12:00:00",
    })
    rows.append({
        "frame_id": "frm-021",
        "event_type": "key_rotation_rescinded",
        "key_version": 2,
        "replacement_key_version": 4,
        "nonce_override_hex": None,
        "supersedes_nonce_hex": None,
        "recorded_at": "2026-05-16 13:00:00",
    })
    rows.append({
        "frame_id": "frm-021",
        "event_type": "key_assigned",
        "key_version": 6,
        "replacement_key_version": None,
        "nonce_override_hex": None,
        "supersedes_nonce_hex": None,
        "recorded_at": "2026-05-20 14:00:00",
    })
    rows.append({
        "frame_id": "frm-021",
        "event_type": "key_assignment_rescinded",
        "key_version": 6,
        "replacement_key_version": None,
        "nonce_override_hex": None,
        "supersedes_nonce_hex": None,
        "recorded_at": "2026-05-22 16:00:00",
    })
    rows.append({
        "frame_id": "frm-021",
        "event_type": "key_rotated",
        "key_version": 2,
        "replacement_key_version": 5,
        "nonce_override_hex": None,
        "supersedes_nonce_hex": None,
        "recorded_at": "2026-05-24 10:00:00",
    })
    rows.append({
        "frame_id": "frm-021",
        "event_type": "key_rotation_rescinded",
        "key_version": 2,
        "replacement_key_version": 5,
        "nonce_override_hex": None,
        "supersedes_nonce_hex": None,
        "recorded_at": "2026-05-25 11:00:00",
    })

    # frm-022: Appendix D override plus later DB registration and rotation.
    rows.append({
        "frame_id": "frm-022",
        "event_type": "key_assigned",
        "key_version": 2,
        "replacement_key_version": None,
        "nonce_override_hex": None,
        "supersedes_nonce_hex": None,
        "recorded_at": "2026-05-08 08:00:00",
    })
    rows.append({
        "frame_id": "frm-022",
        "event_type": "nonce_override_registered",
        "key_version": 2,
        "replacement_key_version": None,
        "nonce_override_hex": NONCE_OVERRIDE_FRM022_DB.hex().upper(),
        "supersedes_nonce_hex": None,
        "recorded_at": "2026-05-18 10:00:00",
    })
    rows.append({
        "frame_id": "frm-022",
        "event_type": "key_rotated",
        "key_version": 2,
        "replacement_key_version": 4,
        "nonce_override_hex": None,
        "supersedes_nonce_hex": None,
        "recorded_at": "2026-05-20 12:00:00",
    })

    # frm-023: replacement rescinded then replaced again — final bytes are C.
    rows.append({
        "frame_id": "frm-023",
        "event_type": "key_assigned",
        "key_version": 2,
        "replacement_key_version": None,
        "nonce_override_hex": None,
        "supersedes_nonce_hex": None,
        "recorded_at": "2026-05-08 08:00:00",
    })
    rows.append({
        "frame_id": "frm-023",
        "event_type": "nonce_override_registered",
        "key_version": 2,
        "replacement_key_version": None,
        "nonce_override_hex": NONCE_FRM023_AAA.hex().upper(),
        "supersedes_nonce_hex": None,
        "recorded_at": "2026-05-10 10:00:00",
    })
    rows.append({
        "frame_id": "frm-023",
        "event_type": "nonce_override_replaced",
        "key_version": 2,
        "replacement_key_version": None,
        "nonce_override_hex": NONCE_FRM023_BBB.hex().upper(),
        "supersedes_nonce_hex": NONCE_FRM023_AAA.hex().upper(),
        "recorded_at": "2026-05-14 12:00:00",
    })
    rows.append({
        "frame_id": "frm-023",
        "event_type": "nonce_override_replacement_rescinded",
        "key_version": 2,
        "replacement_key_version": None,
        "nonce_override_hex": NONCE_FRM023_AAA.hex().upper(),
        "supersedes_nonce_hex": NONCE_FRM023_BBB.hex().upper(),
        "recorded_at": "2026-05-18 14:00:00",
    })
    rows.append({
        "frame_id": "frm-023",
        "event_type": "nonce_override_replaced",
        "key_version": 2,
        "replacement_key_version": None,
        "nonce_override_hex": NONCE_FRM023_CCC.hex().upper(),
        "supersedes_nonce_hex": NONCE_FRM023_AAA.hex().upper(),
        "recorded_at": "2026-05-22 16:00:00",
    })

    # frm-024: v2 override, rotate to v4, replace v4 override, rotate to v5, v5 override.
    rows.append({
        "frame_id": "frm-024",
        "event_type": "key_assigned",
        "key_version": 2,
        "replacement_key_version": None,
        "nonce_override_hex": None,
        "supersedes_nonce_hex": None,
        "recorded_at": "2026-05-05 08:00:00",
    })
    rows.append({
        "frame_id": "frm-024",
        "event_type": "nonce_override_registered",
        "key_version": 2,
        "replacement_key_version": None,
        "nonce_override_hex": NONCE_FRM024_V2.hex().upper(),
        "supersedes_nonce_hex": None,
        "recorded_at": "2026-05-08 09:00:00",
    })
    rows.append({
        "frame_id": "frm-024",
        "event_type": "key_rotated",
        "key_version": 2,
        "replacement_key_version": 4,
        "nonce_override_hex": None,
        "supersedes_nonce_hex": None,
        "recorded_at": "2026-05-12 10:00:00",
    })
    rows.append({
        "frame_id": "frm-024",
        "event_type": "nonce_override_registered",
        "key_version": 4,
        "replacement_key_version": None,
        "nonce_override_hex": NONCE_FRM024_EEE.hex().upper(),
        "supersedes_nonce_hex": None,
        "recorded_at": "2026-05-15 11:00:00",
    })
    rows.append({
        "frame_id": "frm-024",
        "event_type": "nonce_override_replaced",
        "key_version": 4,
        "replacement_key_version": None,
        "nonce_override_hex": NONCE_FRM024_FFF.hex().upper(),
        "supersedes_nonce_hex": NONCE_FRM024_EEE.hex().upper(),
        "recorded_at": "2026-05-18 13:00:00",
    })
    rows.append({
        "frame_id": "frm-024",
        "event_type": "key_rotated",
        "key_version": 4,
        "replacement_key_version": 5,
        "nonce_override_hex": None,
        "supersedes_nonce_hex": None,
        "recorded_at": "2026-05-20 14:00:00",
    })
    rows.append({
        "frame_id": "frm-024",
        "event_type": "nonce_override_registered",
        "key_version": 5,
        "replacement_key_version": None,
        "nonce_override_hex": NONCE_FRM024_GGG.hex().upper(),
        "supersedes_nonce_hex": None,
        "recorded_at": "2026-05-22 16:00:00",
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
            "db_override",
            "derived_sha256_prefix",
        ],
        "derived_nonce_rule": "SHA-256(frame_id + ':' + key_version), first 12 bytes",
        "nonce_overrides": {
            "frm-003": NONCE_OVERRIDE_FRM003.hex().upper(),
            "frm-006": NONCE_OVERRIDE_FRM006.hex().upper(),
            "frm-010": NONCE_OVERRIDE_FRM010.hex().upper(),
            "frm-015": NONCE_OVERRIDE_FRM015.hex().upper(),
            "frm-022": NONCE_OVERRIDE_FRM022.hex().upper(),
        },
    }


def rescinded_assignment_versions(
    frame_id: str, events: list[dict[str, Any]]
) -> set[int]:
    """key_version values voided by key_assignment_rescinded for this frame."""
    return {
        e["key_version"]
        for e in events
        if e["frame_id"] == frame_id
        and e["event_type"] == "key_assignment_rescinded"
        and e["key_version"] is not None
    }


def rescinded_rotation_pairs(
    frame_id: str, events: list[dict[str, Any]]
) -> set[tuple[int, int]]:
    """Rotation (key_version, replacement_key_version) pairs voided by rescission."""
    pairs: set[tuple[int, int]] = set()
    for event in events:
        if (
            event["frame_id"] == frame_id
            and event["event_type"] == "key_rotation_rescinded"
            and event["key_version"] is not None
            and event["replacement_key_version"] is not None
        ):
            pairs.add((event["key_version"], event["replacement_key_version"]))
    return pairs


def resolve_key_version(frame_id: str, events: list[dict[str, Any]]) -> tuple[int, str]:
    """Pick operative key version from audit timeline + exception precedence."""
    frame_events = [e for e in events if e["frame_id"] == frame_id]
    voided = rescinded_rotation_pairs(frame_id, events)
    rotations = [
        e for e in frame_events
        if e["event_type"] == "key_rotated"
        and (e["key_version"], e["replacement_key_version"]) not in voided
    ]
    if rotations:
        latest = max(rotations, key=lambda e: e["recorded_at"])
        return latest["replacement_key_version"], "rotation_replacement"
    voided_assignments = rescinded_assignment_versions(frame_id, events)
    assigned = [
        e for e in frame_events
        if e["event_type"] == "key_assigned"
        and e["key_version"] not in voided_assignments
    ]
    latest = max(assigned, key=lambda e: e["recorded_at"])
    return latest["key_version"], "latest_assigned"


def revoked_nonce_hex(frame_id: str, events: list[dict[str, Any]]) -> set[str]:
    """Nonce override bytes voided by nonce_override_revoked for this frame."""
    return {
        e["nonce_override_hex"]
        for e in events
        if e["frame_id"] == frame_id
        and e["event_type"] == "nonce_override_revoked"
        and e["nonce_override_hex"]
    }


def db_override_candidates(
    frame_id: str, events: list[dict[str, Any]]
) -> list[tuple[str, str, int | None]]:
    """Eligible DB nonce rows after revocation and amendment processing."""
    frame_events = sorted(
        (e for e in events if e["frame_id"] == frame_id),
        key=lambda e: e["recorded_at"],
    )
    revoked = revoked_nonce_hex(frame_id, events)
    candidates: list[tuple[str, str, int | None]] = []

    for event in frame_events:
        event_type = event["event_type"]
        if event_type == "nonce_override_revoked":
            continue
        if event_type == "nonce_override_registered":
            hx = event["nonce_override_hex"]
            if hx and hx not in revoked:
                candidates.append((event["recorded_at"], hx, event["key_version"]))
        elif event_type == "nonce_override_amended":
            supersedes = event.get("supersedes_nonce_hex")
            hx = event["nonce_override_hex"]
            if supersedes:
                candidates = [c for c in candidates if c[1] != supersedes]
            if hx and hx not in revoked:
                candidates.append((event["recorded_at"], hx, event["key_version"]))
        elif event_type == "nonce_override_replaced":
            supersedes = event.get("supersedes_nonce_hex")
            hx = event["nonce_override_hex"]
            if supersedes:
                candidates = [c for c in candidates if c[1] != supersedes]
            if hx and hx not in revoked:
                candidates.append((event["recorded_at"], hx, event["key_version"]))
        elif event_type == "nonce_override_replacement_rescinded":
            voided = event.get("supersedes_nonce_hex")
            restored = event.get("nonce_override_hex")
            if voided:
                candidates = [c for c in candidates if c[1] != voided]
            if restored and restored not in revoked:
                candidates.append((event["recorded_at"], restored, event["key_version"]))

    return [c for c in candidates if c[1] not in revoked]


def resolve_nonce(
    frame_id: str,
    key_version: int,
    rules: dict[str, Any],
    events: list[dict[str, Any]],
) -> tuple[bytes, str]:
    overrides = rules.get("nonce_overrides", {})
    if frame_id in overrides:
        return bytes.fromhex(overrides[frame_id]), "override"
    candidates = db_override_candidates(frame_id, events)
    matching = [c for c in candidates if c[2] == key_version]
    if matching:
        latest = max(matching, key=lambda c: c[0])
        return bytes.fromhex(latest[1]), "override"
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
