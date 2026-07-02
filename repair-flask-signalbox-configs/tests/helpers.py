"""Verifier helpers for the Signalbox cartridge repair task.

Expected locks, operative goal, and switch lineup are derived from evidence.duckdb
and the cartridge topology — there is no labeled operative answer row.
"""

from __future__ import annotations

import json
import sqlite3
import subprocess
import time
import urllib.error
import urllib.request
from itertools import product
from pathlib import Path

import duckdb
import yaml

API = "http://127.0.0.1:5000"
EVIDENCE_DB = Path("/app/data/evidence.duckdb")
DISPATCH_DB = Path("/app/data/dispatch.duckdb")
OUTPUT = Path("/app/output/transcript.json")
CARTRIDGE = Path("/app/cartridge")
PLAY = Path("/app/tools/play_shift.py")


def request_json(method: str, path: str, payload: dict | None = None):
    data = None
    headers = {}
    if payload is not None:
        data = json.dumps(payload).encode()
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(API + path, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            body = resp.read().decode()
            return resp.status, json.loads(body) if body else None
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode()
        try:
            parsed = json.loads(raw) if raw else None
        except json.JSONDecodeError:
            parsed = None
        return exc.code, parsed


def wait_for_referee(timeout_sec: float = 20.0) -> None:
    deadline = time.time() + timeout_sec
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(f"{API}/health", timeout=2) as resp:
                if json.loads(resp.read().decode()).get("status") == "ok":
                    return
        except Exception:
            pass
        time.sleep(0.25)
    raise RuntimeError("signalbox referee did not become ready")


def reset_referee() -> None:
    last_error: Exception | None = None
    for _ in range(8):
        try:
            req = urllib.request.Request(f"{API}/v1/reset", method="POST", data=b"")
            urllib.request.urlopen(req, timeout=5).read()
            return
        except Exception as exc:
            last_error = exc
            time.sleep(0.25)
    raise RuntimeError(f"signalbox referee reset failed: {last_error}") from last_error


def load_network() -> dict:
    with (CARTRIDGE / "network.yaml").open(encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def _evidence() -> duckdb.DuckDBPyConnection:
    return duckdb.connect(str(EVIDENCE_DB), read_only=True)


def lock_log_rows() -> list[tuple]:
    conn = _evidence()
    try:
        return conn.execute(
            "SELECT seq, bulletin, op, track_id, detail FROM route_lock_log ORDER BY seq"
        ).fetchall()
    finally:
        conn.close()


def lock_corrections() -> dict[int, tuple[str, str]]:
    conn = _evidence()
    try:
        rows = conn.execute(
            "SELECT seq, effective_op, effective_detail FROM lock_corrections ORDER BY seq"
        ).fetchall()
    finally:
        conn.close()
    return {int(seq): (op, detail) for seq, op, detail in rows}


def effective_row(row: tuple, corrections: dict[int, tuple[str, str]]) -> tuple:
    seq, bulletin, op, track_id, detail = row
    if seq in corrections:
        op, detail = corrections[seq]
    return seq, bulletin, op, track_id, detail


def arrival_candidates() -> list[str]:
    conn = _evidence()
    try:
        return [
            row[0]
            for row in conn.execute(
                "SELECT station_id FROM arrival_candidates ORDER BY station_id"
            ).fetchall()
        ]
    finally:
        conn.close()


def hint_map() -> dict[str, str]:
    conn = _evidence()
    try:
        rows = conn.execute(
            "SELECT station_id, hint FROM hint_clues ORDER BY seq"
        ).fetchall()
    finally:
        conn.close()
    return {station: hint for station, hint in rows}


def parse_hold_id(detail: str, bulletin: str) -> str:
    """Return hold_id from detail JSON or default to the bulletin id."""
    if not detail or not detail.strip():
        return bulletin
    try:
        obj = json.loads(detail)
    except (json.JSONDecodeError, TypeError):
        return bulletin
    if isinstance(obj, dict) and isinstance(obj.get("hold_id"), str):
        return obj["hold_id"]
    return bulletin


def parse_release_hold_id(detail: str) -> str | None:
    """Return required hold_id for release, or None when detail is empty."""
    if not detail or not detail.strip():
        return None
    try:
        obj = json.loads(detail)
    except (json.JSONDecodeError, TypeError):
        return None
    if isinstance(obj, dict) and isinstance(obj.get("hold_id"), str):
        return obj["hold_id"]
    return None


def track_is_held(hold_stacks: dict[str, list[tuple[str, dict | None]]], track_id: str) -> bool:
    return bool(hold_stacks.get(track_id))


def apply_hold(
    state: dict[str, dict],
    hold_stacks: dict[str, list[tuple[str, dict | None]]],
    track_id: str,
    hold_id: str,
) -> None:
    saved = dict(state[track_id]) if track_id in state else None
    hold_stacks.setdefault(track_id, []).append((hold_id, saved))
    state.pop(track_id, None)


def apply_release(
    state: dict[str, dict],
    hold_stacks: dict[str, list[tuple[str, dict | None]]],
    track_id: str,
    required_hold_id: str | None,
) -> bool:
    stack = hold_stacks.get(track_id)
    if not stack:
        return False
    top_hold_id, saved = stack[-1]
    if required_hold_id is not None and top_hold_id != required_hold_id:
        return False
    stack.pop()
    if not stack:
        hold_stacks.pop(track_id, None)
    if saved is None:
        state.pop(track_id, None)
    else:
        state[track_id] = saved
    return True


def restore_dependent_locks(
    state: dict[str, dict],
    rows: list[tuple],
    corrections: dict[int, tuple[str, str]],
    network: dict,
    release_seq: int,
    restored_track: str,
    voided_seqs: set[int],
    hold_stacks: dict[str, list[tuple[str, dict | None]]],
    applied_bulletins: set[str],
) -> None:
    """Re-apply surviving rows that require a track just released from hold."""
    known_tracks = {track["id"] for track in network["tracks"]}
    switch_ids = set(network["switches"])
    revokes = compute_revoke_events(rows, corrections)
    for row in rows:
        seq, bulletin, op, track_id, detail = effective_row(row, corrections)
        if seq >= release_seq:
            continue
        when, explicit_requires, anchor_bulletin, unless_absent, unless_present, unless_held, expires_after, row_stamp, precondition, exclusive_with = (
            parse_detail(detail)
        )
        witness, _suppresses, requires_match, unless_matches, binds_requires, _unless_changed, requires_when, unless_requires_when, _requires_stable, _inherit = parse_detail_extras(
            detail
        )
        if op not in ("add", "amend", "replace"):
            continue
        requires = list(explicit_requires or [])
        if restored_track not in requires and restored_track not in binds_requires:
            continue
        if witness and not witness_satisfied(witness, detail, applied_bulletins, state):
            continue
        if unless_held and any(
            track_is_held(hold_stacks, held_track) for held_track in unless_held
        ):
            continue
        if precondition and not precondition_met(state, precondition):
            continue
        if requires_match and not precondition_met(state, requires_match):
            continue
        if unless_matches and unless_matches_active(state, unless_matches):
            continue
        if row_voided(
            seq,
            bulletin,
            track_id,
            anchor_bulletin,
            expires_after,
            row_stamp,
            revokes,
            voided_seqs,
        ):
            continue
        if track_is_held(hold_stacks, track_id):
            continue
        if op in ("add", "replace"):
            if not row_valid(track_id, when, known_tracks, switch_ids):
                continue
            restore_op = "amend" if op == "add" and track_id in state else op
            if restore_op == "replace":
                state[track_id] = _lock_entry(
                    when,
                    requires,
                    unless_absent,
                    unless_present,
                    unless_held,
                    requires_match,
                    unless_matches,
                    binds_requires,
                    requires_when=requires_when,
                    unless_requires_when=unless_requires_when,
                )
            else:
                apply_lock_row(
                    state, restore_op, track_id, detail, known_tracks, switch_ids
                )
                attach_requires_snapshots(state, track_id, detail)
                attach_stable_snapshots(state, track_id, detail)
        else:
            prev = state.get(track_id, _lock_entry({}, [], [], []))
            if when:
                if not row_valid(track_id, when, known_tracks, switch_ids):
                    continue
                merged_when = {**prev["when"], **when}
            elif prev["when"]:
                merged_when = dict(prev["when"])
            else:
                continue
            state[track_id] = _lock_entry(
                merged_when,
                requires,
                unless_absent if unless_absent else list(prev["unless_absent"]),
                unless_present if unless_present else list(prev["unless_present"]),
                unless_held if unless_held else list(prev.get("unless_held", [])),
                requires_match if requires_match else dict(prev.get("requires_match", {})),
                unless_matches if unless_matches else dict(prev.get("unless_matches", {})),
                binds_requires if binds_requires else list(prev.get("binds_requires", [])),
                requires_when=requires_when if requires_when else dict(prev.get("requires_when", {})),
                unless_requires_when=unless_requires_when
                if unless_requires_when
                else dict(prev.get("unless_requires_when", {})),
            )
            attach_requires_snapshots(state, track_id, detail)
            attach_stable_snapshots(state, track_id, detail)
        apply_exclusive_with(state, exclusive_with)
        apply_fixpoints(state)


def reapply_unless_present_rows(
    state: dict[str, dict],
    rows: list[tuple],
    corrections: dict[int, tuple[str, str]],
    network: dict,
    release_seq: int,
    revokes: list[tuple[int, str, str, set[str] | None]],
    hold_stacks: dict[str, list[tuple[str, dict | None]]],
    voided_seqs: set[int],
    applied_bulletins: set[str],
) -> None:
    """Re-apply earlier unless_present rows once a release restores their conditions."""
    known_tracks = {track["id"] for track in network["tracks"]}
    switch_ids = set(network["switches"])
    for row in rows:
        seq, bulletin, op, track_id, detail = effective_row(row, corrections)
        if seq >= release_seq:
            continue
        (
            when,
            explicit_requires,
            anchor_bulletin,
            unless_absent,
            unless_present,
            unless_held,
            expires_after,
            row_stamp,
            precondition,
            exclusive_with,
        ) = parse_detail(detail)
        witness, _suppresses, requires_match, unless_matches, binds_requires, _unless_changed, requires_when, unless_requires_when, _requires_stable, _inherit = parse_detail_extras(
            detail
        )
        if not unless_present or op not in ("add", "amend", "replace"):
            continue
        if witness and not witness_satisfied(witness, detail, applied_bulletins, state):
            continue
        if unless_held and any(
            track_is_held(hold_stacks, held_track) for held_track in unless_held
        ):
            continue
        if precondition and not precondition_met(state, precondition):
            continue
        if requires_match and not precondition_met(state, requires_match):
            continue
        if unless_matches and unless_matches_active(state, unless_matches):
            continue
        if row_voided(
            seq,
            bulletin,
            track_id,
            anchor_bulletin,
            expires_after,
            row_stamp,
            revokes,
            voided_seqs,
        ):
            continue
        if track_is_held(hold_stacks, track_id):
            continue
        if not all(present in state for present in unless_present):
            continue
        if op in ("add", "replace"):
            if not row_valid(track_id, when, known_tracks, switch_ids):
                continue
            state[track_id] = _lock_entry(
                when,
                list(explicit_requires or []),
                unless_absent,
                unless_present,
                unless_held,
                requires_match,
                unless_matches,
                binds_requires,
                requires_when=requires_when,
                unless_requires_when=unless_requires_when,
            )
        else:
            prev = state.get(track_id, _lock_entry({}, [], [], []))
            if when:
                if not row_valid(track_id, when, known_tracks, switch_ids):
                    continue
                merged_when = {**prev["when"], **when}
            elif prev["when"]:
                merged_when = dict(prev["when"])
            else:
                continue
            merged_requires = (
                list(explicit_requires)
                if explicit_requires is not None
                else list(prev["requires"])
            )
            merged_unless_absent = (
                unless_absent if unless_absent else list(prev["unless_absent"])
            )
            merged_unless_present = (
                unless_present if unless_present else list(prev["unless_present"])
            )
            merged_unless_held = unless_held if unless_held else list(prev.get("unless_held", []))
            merged_requires_match = (
                requires_match if requires_match else dict(prev.get("requires_match", {}))
            )
            merged_unless_matches = (
                unless_matches if unless_matches else dict(prev.get("unless_matches", {}))
            )
            merged_binds_requires = (
                binds_requires if binds_requires else list(prev.get("binds_requires", []))
            )
            merged_requires_when = (
                requires_when if requires_when else dict(prev.get("requires_when", {}))
            )
            merged_unless_requires_when = (
                unless_requires_when
                if unless_requires_when
                else dict(prev.get("unless_requires_when", {}))
            )
            state[track_id] = _lock_entry(
                merged_when,
                merged_requires,
                merged_unless_absent,
                merged_unless_present,
                merged_unless_held,
                merged_requires_match,
                merged_unless_matches,
                merged_binds_requires,
                requires_when=merged_requires_when,
                unless_requires_when=merged_unless_requires_when,
            )
        attach_requires_snapshots(state, track_id, detail)
        attach_stable_snapshots(state, track_id, detail)
        apply_exclusive_with(state, exclusive_with)
        apply_fixpoints(state)


def parse_detail_flags(detail: str) -> tuple[str | None, bool, str | None, str | None]:
    """Return coupling id, decouple flag, defer_until bulletin, and supersedes bulletin."""
    try:
        obj = json.loads(detail)
    except (json.JSONDecodeError, TypeError):
        return None, False, None, None
    if not isinstance(obj, dict):
        return None, False, None, None
    coupling = obj.get("coupling")
    coupling_id = coupling if isinstance(coupling, str) else None
    decouple = obj.get("decouple") is True
    defer_until = obj.get("defer_until")
    defer_bulletin = defer_until if isinstance(defer_until, str) else None
    supersedes = obj.get("supersedes")
    supersedes_bulletin = supersedes if isinstance(supersedes, str) else None
    return coupling_id, decouple, defer_bulletin, supersedes_bulletin


def _parse_match_map(raw: object) -> dict[str, dict[str, str]]:
    """Parse track-id keyed partial when maps from detail JSON."""
    if not isinstance(raw, dict):
        return {}
    parsed: dict[str, dict[str, str]] = {}
    for track_id, when in raw.items():
        if not isinstance(track_id, str) or not isinstance(when, dict):
            continue
        positions = {
            switch_id: position
            for switch_id, position in when.items()
            if isinstance(switch_id, str) and position in ("north", "south")
        }
        if positions:
            parsed[track_id] = positions
    return parsed


def parse_detail_extras(
    detail: str,
) -> tuple[
    str | None,
    list[str],
    dict[str, dict[str, str]],
    dict[str, dict[str, str]],
    list[str],
    list[str],
    dict[str, dict[str, str]],
    dict[str, dict[str, str]],
]:
    """Return witness, suppresses, requires_match, unless_matches, binds_requires, unless_requires_changed, requires_when, unless_requires_when."""
    try:
        obj = json.loads(detail)
    except (json.JSONDecodeError, TypeError):
        return None, [], {}, {}, [], [], {}, {}, [], []
    if not isinstance(obj, dict):
        return None, [], {}, {}, [], [], {}, {}, [], []
    witness = obj.get("witness")
    witness_bulletin = witness if isinstance(witness, str) else None
    suppresses: list[str] = []
    raw_suppresses = obj.get("suppresses", [])
    if isinstance(raw_suppresses, list):
        suppresses = [item for item in raw_suppresses if isinstance(item, str)]
    binds_requires: list[str] = []
    raw_binds = obj.get("binds_requires", [])
    if isinstance(raw_binds, list):
        binds_requires = [item for item in raw_binds if isinstance(item, str)]
    unless_requires_changed: list[str] = []
    raw_unless_changed = obj.get("unless_requires_changed", [])
    if isinstance(raw_unless_changed, list):
        unless_requires_changed = [
            item for item in raw_unless_changed if isinstance(item, str)
        ]
    requires_stable: list[str] = []
    raw_stable = obj.get("requires_stable", [])
    if isinstance(raw_stable, list):
        requires_stable = [item for item in raw_stable if isinstance(item, str)]
    inherit_when_from: list[str] = []
    raw_inherit = obj.get("inherit_when_from", [])
    if isinstance(raw_inherit, list):
        inherit_when_from = [item for item in raw_inherit if isinstance(item, str)]
    return (
        witness_bulletin,
        suppresses,
        _parse_match_map(obj.get("requires_match", {})),
        _parse_match_map(obj.get("unless_matches", {})),
        binds_requires,
        unless_requires_changed,
        _parse_match_map(obj.get("requires_when", {})),
        _parse_match_map(obj.get("unless_requires_when", {})),
        requires_stable,
        inherit_when_from,
    )


def unless_matches_active(
    state: dict[str, dict], unless_matches: dict[str, dict[str, str]]
) -> bool:
    """True when any listed track is locked with every listed switch position."""
    for track_id, required_when in unless_matches.items():
        entry = state.get(track_id)
        if not entry:
            continue
        current = entry.get("when", {})
        if all(current.get(switch_id) == position for switch_id, position in required_when.items()):
            return True
    return False


def parse_witness_active(detail: str) -> bool:
    """True when detail requests the witness bulletin still own a track lock."""
    try:
        obj = json.loads(detail)
    except (json.JSONDecodeError, TypeError):
        return False
    return isinstance(obj, dict) and bool(obj.get("witness_active"))


def bulletin_has_active_row(state: dict[str, dict], bulletin: str) -> bool:
    """True when the bulletin still owns at least one surviving track lock."""
    return any(entry.get("_bulletin") == bulletin for entry in state.values())


def witness_satisfied(
    witness: str | None,
    detail: str,
    applied_bulletins: set[str],
    state: dict[str, dict],
) -> bool:
    """Apply witness and optional witness_active gates."""
    if not witness:
        return True
    if witness not in applied_bulletins:
        return False
    if parse_witness_active(detail):
        return bulletin_has_active_row(state, witness)
    return True


def _lock_entry(
    when: dict[str, str],
    requires: list[str],
    unless_absent: list[str],
    unless_present: list[str],
    unless_held: list[str] | None = None,
    requires_match: dict[str, dict[str, str]] | None = None,
    unless_matches: dict[str, dict[str, str]] | None = None,
    binds_requires: list[str] | None = None,
    unless_requires_changed: list[str] | None = None,
    requires_when: dict[str, dict[str, str]] | None = None,
    unless_requires_when: dict[str, dict[str, str]] | None = None,
    requires_stable: list[str] | None = None,
    inherit_when_from: list[str] | None = None,
    base_when: dict[str, str] | None = None,
    requires_snapshots: dict[str, tuple[str, ...]] | None = None,
    stable_snapshots: dict[str, tuple[tuple[str, ...], tuple[tuple[str, str], ...]]] | None = None,
) -> dict:
    return {
        "when": dict(when),
        "requires": list(requires),
        "unless_absent": list(unless_absent),
        "unless_present": list(unless_present),
        "unless_held": list(unless_held or []),
        "requires_match": dict(requires_match or {}),
        "unless_matches": dict(unless_matches or {}),
        "binds_requires": list(binds_requires or []),
        "unless_requires_changed": list(unless_requires_changed or []),
        "requires_when": dict(requires_when or {}),
        "unless_requires_when": dict(unless_requires_when or {}),
        "requires_stable": list(requires_stable or []),
        "inherit_when_from": list(inherit_when_from or []),
        "base_when": dict(base_when or {}),
        "requires_snapshots": dict(requires_snapshots or {}),
        "stable_snapshots": dict(stable_snapshots or {}),
    }


def capture_requires_snapshots(
    state: dict[str, dict], unless_requires_changed: list[str]
) -> dict[str, tuple[str, ...]]:
    """Snapshot effective requires for unless_requires_changed watches at apply time."""
    snapshots: dict[str, tuple[str, ...]] = {}
    for watched in unless_requires_changed:
        if watched in state:
            snapshots[watched] = tuple(sorted(effective_requires(state[watched], state)))
    return snapshots


def merged_inherited_when(
    state: dict[str, dict], base_when: dict[str, str], inherit_when_from: list[str]
) -> dict[str, str] | None:
    merged = dict(base_when)
    for source in inherit_when_from:
        if source not in state:
            return None
        merged.update(state[source].get("when", {}))
    return merged


def recompute_inherited_when(state: dict[str, dict]) -> bool:
    changed = False
    for track_id, entry in list(state.items()):
        sources = entry.get("inherit_when_from", [])
        if not sources:
            continue
        for source in sources:
            if source not in state:
                del state[track_id]
                changed = True
                break
        else:
            merged = merged_inherited_when(state, entry.get("base_when", {}), sources)
            if merged is None:
                del state[track_id]
                changed = True
            elif merged != entry.get("when"):
                entry["when"] = merged
                changed = True
    return changed


def capture_stable_snapshots(
    state: dict[str, dict], requires_stable: list[str]
) -> dict[str, tuple[tuple[str, ...], tuple[tuple[str, str], ...]]]:
    snapshots: dict[str, tuple[tuple[str, ...], tuple[tuple[str, str], ...]]] = {}
    for watched in requires_stable:
        if watched in state:
            entry = state[watched]
            snapshots[watched] = (
                tuple(sorted(effective_requires(entry, state))),
                tuple(sorted(entry.get("when", {}).items())),
            )
    return snapshots


def effective_requires(entry: dict[str, dict], state: dict[str, dict]) -> list[str]:
    """Union explicit requires with binds_requires track ids and their requires."""
    merged: list[str] = list(entry.get("requires", []))
    seen = set(merged)
    for bound in entry.get("binds_requires", []):
        if bound in state:
            if bound not in seen:
                merged.append(bound)
                seen.add(bound)
            for req in state[bound].get("requires", []):
                if req not in seen:
                    merged.append(req)
                    seen.add(req)
    return merged


def requires_when_satisfied(entry: dict[str, dict], state: dict[str, dict]) -> bool:
    """True when every effective requires entry meets requires_when positional gates."""
    requires_when = entry.get("requires_when", {})
    for req in effective_requires(entry, state):
        if req not in state:
            return False
        needed = requires_when.get(req)
        if not needed:
            continue
        current = state[req].get("when", {})
        if not all(current.get(switch_id) == position for switch_id, position in needed.items()):
            return False
    return True


def unless_requires_when_active(
    entry: dict[str, dict], state: dict[str, dict]
) -> bool:
    """True when a listed track is locked but its when-map misses a listed position."""
    unless_requires_when = entry.get("unless_requires_when", {})
    for track_id, needed in unless_requires_when.items():
        watched = state.get(track_id)
        if not watched:
            continue
        current = watched.get("when", {})
        if not all(current.get(switch_id) == position for switch_id, position in needed.items()):
            return True
    return False


def precondition_met(state: dict[str, dict], precondition: dict[str, dict]) -> bool:
    """True when every listed track is locked with matching when positions."""
    for track_id, required_when in precondition.items():
        entry = state.get(track_id)
        if not entry:
            return False
        current = entry.get("when", {})
        for switch_id, position in required_when.items():
            if current.get(switch_id) != position:
                return False
    return True


def apply_exclusive_with(state: dict[str, dict], exclusive_with: list[str]) -> None:
    """Drop listed tracks after a row successfully applies."""
    for track_id in exclusive_with:
        state.pop(track_id, None)


def parse_detail(
    detail: str,
) -> tuple[
    dict[str, str],
    list[str] | None,
    str | None,
    list[str],
    list[str],
    list[str],
    str | None,
    str | None,
    dict[str, dict[str, str]],
    list[str],
]:
    """Split detail into when, requires, anchor, unless lists, expires, stamp, precondition, exclusive_with."""
    try:
        obj = json.loads(detail)
    except (json.JSONDecodeError, TypeError):
        return {}, None, None, [], [], [], None, None, {}, []
    if not isinstance(obj, dict):
        return {}, None, None, [], [], [], None, None, {}, []
    anchor = obj.get("anchor")
    anchor_bulletin = anchor if isinstance(anchor, str) else None
    stamp = obj.get("stamp")
    row_stamp = stamp if isinstance(stamp, str) else None
    expires_after = obj.get("expires_after")
    expires_bulletin = expires_after if isinstance(expires_after, str) else None
    unless_absent: list[str] = []
    raw_unless = obj.get("unless_absent", [])
    if isinstance(raw_unless, list):
        unless_absent = [item for item in raw_unless if isinstance(item, str)]
    unless_present: list[str] = []
    raw_present = obj.get("unless_present", [])
    if isinstance(raw_present, list):
        unless_present = [item for item in raw_present if isinstance(item, str)]
    unless_held: list[str] = []
    raw_held = obj.get("unless_held", [])
    if isinstance(raw_held, list):
        unless_held = [item for item in raw_held if isinstance(item, str)]
    precondition: dict[str, dict[str, str]] = {}
    raw_precondition = obj.get("precondition", {})
    if isinstance(raw_precondition, dict):
        for track_id, when in raw_precondition.items():
            if not isinstance(track_id, str) or not isinstance(when, dict):
                continue
            parsed_when = {
                switch_id: position
                for switch_id, position in when.items()
                if isinstance(switch_id, str) and position in ("north", "south")
            }
            if parsed_when:
                precondition[track_id] = parsed_when
    exclusive_with: list[str] = []
    raw_exclusive = obj.get("exclusive_with", [])
    if isinstance(raw_exclusive, list):
        exclusive_with = [item for item in raw_exclusive if isinstance(item, str)]
    raw_base_when = obj.get("base_when")
    parsed_base_when: dict[str, str] | None = None
    if isinstance(raw_base_when, dict):
        parsed_base_when = {
            switch_id: position
            for switch_id, position in raw_base_when.items()
            if isinstance(switch_id, str) and position in ("north", "south")
        }
    obj = {
        key: value
        for key, value in obj.items()
        if key
        not in (
            "anchor",
            "stamp",
            "expires_after",
            "unless_absent",
            "unless_present",
            "unless_held",
            "coupling",
            "decouple",
            "defer_until",
            "supersedes",
            "precondition",
            "exclusive_with",
            "witness",
            "suppresses",
            "requires_match",
            "unless_matches",
            "binds_requires",
            "unless_requires_changed",
            "requires_when",
            "unless_requires_when",
            "requires_stable",
            "inherit_when_from",
            "base_when",
        )
    }
    has_requires = "requires" in obj
    explicit_requires: list[str] | None = None
    if has_requires:
        raw_requires = obj.get("requires", [])
        if not isinstance(raw_requires, list):
            return {}, None, anchor_bulletin, unless_absent, unless_present, unless_held, expires_bulletin, row_stamp, precondition, exclusive_with
        explicit_requires = [req for req in raw_requires if isinstance(req, str)]
    if "when" in obj:
        when = obj.get("when", {})
    elif parsed_base_when is not None:
        when = parsed_base_when
    elif has_requires and set(obj) == {"requires"}:
        when = {}
    else:
        when = {key: value for key, value in obj.items() if key != "requires"}
    if not isinstance(when, dict):
        return {}, explicit_requires, anchor_bulletin, unless_absent, unless_present, unless_held, expires_bulletin, row_stamp, precondition, exclusive_with
    return when, explicit_requires, anchor_bulletin, unless_absent, unless_present, unless_held, expires_bulletin, row_stamp, precondition, exclusive_with


def parse_revoke_scope(detail: str, track_id: str) -> tuple[str, str, set[str] | None]:
    """Return revoke kind, target bulletin or stamp, and optional scoped tracks."""
    if track_id == "_stamp":
        try:
            obj = json.loads(detail)
        except (json.JSONDecodeError, TypeError):
            return "stamp", "", None
        if isinstance(obj, dict) and isinstance(obj.get("stamp"), str):
            return "stamp", obj["stamp"], None
        return "stamp", "", None
    if not detail or not detail.strip():
        return "bulletin", track_id, None
    try:
        obj = json.loads(detail)
    except (json.JSONDecodeError, TypeError):
        return "bulletin", track_id, None
    if isinstance(obj, list):
        return "bulletin", track_id, {item for item in obj if isinstance(item, str)}
    return "bulletin", track_id, None


def compute_revoke_events(
    rows: list[tuple], corrections: dict[int, tuple[str, str]]
) -> list[tuple[int, str, str, set[str] | None]]:
    """Return revoke events as (seq, kind, target, scoped_tracks_or_none)."""
    events: list[tuple[int, str, str, set[str] | None]] = []
    for row in rows:
        seq, _bulletin, op, track_id, detail = effective_row(row, corrections)
        if op != "revoke":
            continue
        kind, target, scope = parse_revoke_scope(detail, track_id)
        events.append((seq, kind, target, scope))
    return events


def row_voided(
    row_seq: int,
    bulletin: str,
    track_id: str,
    anchor_bulletin: str | None,
    expires_after: str | None,
    row_stamp: str | None,
    revokes: list[tuple[int, str, str, set[str] | None]],
    voided_seqs: set[int] | None = None,
) -> bool:
    """True when a later revoke, expires_after trigger, or cascade voids this row."""
    if voided_seqs is not None and row_seq in voided_seqs:
        return True
    linked = {bulletin}
    if anchor_bulletin:
        linked.add(anchor_bulletin)
    for revoke_seq, kind, target, scope in revokes:
        if revoke_seq <= row_seq:
            continue
        if kind == "stamp" and row_stamp and target == row_stamp:
            return True
        if kind != "bulletin":
            continue
        if expires_after and target == expires_after:
            return True
        if target not in linked:
            continue
        if scope is None:
            return True
        if track_id in scope:
            return True
    return False


def row_valid(
    track_id: str,
    when: dict[str, str],
    known_tracks: set[str],
    switches: set[str],
) -> bool:
    if track_id not in known_tracks:
        return False
    if not when:
        return False
    return all(sw in switches and pos in ("north", "south") for sw, pos in when.items())


def compute_voided_seqs(
    rows: list[tuple], corrections: dict[int, tuple[str, str]]
) -> set[int]:
    """Collect row seq values voided by revoke, supersede, and coupling cascades."""
    revokes = compute_revoke_events(rows, corrections)
    voided: set[int] = set()

    for row in rows:
        seq, bulletin, _op, track_id, detail = effective_row(row, corrections)
        _when, _req, anchor, _ua, _up, _uh, expires_after, row_stamp, _pre, _ex = parse_detail(detail)
        if row_voided(seq, bulletin, track_id, anchor, expires_after, row_stamp, revokes):
            voided.add(seq)

    changed = True
    while changed:
        changed = False
        for row in rows:
            seq, _bulletin, _op, _track_id, detail = effective_row(row, corrections)
            if seq in voided:
                continue
            _coupling, _decouple, _defer_until, supersedes = parse_detail_flags(detail)
            if not supersedes:
                continue
            for prior in rows:
                prior_seq, prior_bulletin, _pop, _pt, _pd = effective_row(prior, corrections)
                if prior_seq >= seq or prior_seq in voided:
                    continue
                if prior_bulletin == supersedes:
                    voided.add(prior_seq)
                    changed = True

    changed = True
    while changed:
        changed = False
        for row in rows:
            seq, _bulletin, op, track_id, detail = effective_row(row, corrections)
            if op != "revoke":
                continue
            kind, target, scope = parse_revoke_scope(detail, track_id)
            if kind != "bulletin" or scope is not None:
                continue
            coupling_ids: set[str] = set()
            for linked in rows:
                linked_seq, linked_bulletin, _lop, _lt, linked_detail = effective_row(
                    linked, corrections
                )
                if linked_seq >= seq:
                    continue
                if linked_bulletin != target:
                    continue
                coupling, decouple, _defer, _sup = parse_detail_flags(linked_detail)
                if coupling and not decouple:
                    coupling_ids.add(coupling)
            if not coupling_ids:
                continue
            for coupled in rows:
                coupled_seq, _cb, _cop, _ct, coupled_detail = effective_row(
                    coupled, corrections
                )
                if coupled_seq >= seq or coupled_seq in voided:
                    continue
                coupling, decouple, _defer, _sup = parse_detail_flags(coupled_detail)
                if coupling and not decouple and coupling in coupling_ids:
                    voided.add(coupled_seq)
                    changed = True

    changed = True
    while changed:
        changed = False
        for row in rows:
            seq, _bulletin, _op, _track_id, detail = effective_row(row, corrections)
            if seq in voided:
                continue
            _witness, suppresses, _requires_match, _unless_matches, _binds, _unless_changed, _requires_when, _unless_rw, _requires_stable, _inherit = parse_detail_extras(
                detail
            )
            if not suppresses:
                continue
            suppressed = set(suppresses)
            for prior in rows:
                prior_seq, prior_bulletin, _pop, _pt, _pd = effective_row(prior, corrections)
                if prior_seq >= seq or prior_seq in voided:
                    continue
                if prior_bulletin in suppressed:
                    voided.add(prior_seq)
                    changed = True

    return voided


def apply_unless_held_cascade(
    state: dict[str, dict],
    hold_stacks: dict[str, list[tuple[str, dict | None]]],
) -> None:
    """Drop surviving locks whose unless_held names a currently held track."""
    changed = True
    while changed:
        changed = False
        for track_id, entry in list(state.items()):
            for held_track in entry.get("unless_held", []):
                if track_is_held(hold_stacks, held_track):
                    del state[track_id]
                    changed = True
                    break
        if changed:
            apply_fixpoints(state)


def apply_lock_row(
    state: dict[str, dict],
    op: str,
    track_id: str,
    detail: str,
    known_tracks: set[str],
    switch_ids: set[str],
) -> None:
    """Apply one surviving add/amend/replace/withdraw row to lock state."""
    when, explicit_requires, _anchor, unless_absent, unless_present, unless_held, _exp, _stamp, _pre, _ex = (
        parse_detail(detail)
    )
    (
        _witness,
        _suppresses,
        requires_match,
        unless_matches,
        binds_requires,
        unless_changed,
        requires_when,
        unless_requires_when,
        requires_stable,
        inherit_when_from,
    ) = parse_detail_extras(detail)

    def store_lock(
        final_when,
        base_when,
        active_inherit,
        requires,
        unless_absent_list,
        unless_present_list,
        unless_held_list,
        prev=None,
    ):
        prev = prev or _lock_entry({}, [], [], [])
        state[track_id] = _lock_entry(
            final_when,
            requires,
            unless_absent_list,
            unless_present_list,
            unless_held_list,
            requires_match if requires_match else dict(prev.get("requires_match", {})),
            unless_matches if unless_matches else dict(prev.get("unless_matches", {})),
            binds_requires if binds_requires else list(prev.get("binds_requires", [])),
            unless_requires_changed=unless_changed
            if unless_changed
            else list(prev.get("unless_requires_changed", [])),
            requires_when=requires_when if requires_when else dict(prev.get("requires_when", {})),
            unless_requires_when=unless_requires_when
            if unless_requires_when
            else dict(prev.get("unless_requires_when", {})),
            requires_stable=requires_stable if requires_stable else list(prev.get("requires_stable", [])),
            inherit_when_from=active_inherit,
            base_when=base_when if active_inherit else {},
            requires_snapshots=dict(prev.get("requires_snapshots", {})),
            stable_snapshots=dict(prev.get("stable_snapshots", {})),
        )

    if op in ("add", "replace"):
        base_when = dict(when)
        active_inherit = list(inherit_when_from)
        final_when = (
            merged_inherited_when(state, base_when, active_inherit)
            if active_inherit
            else base_when
        )
        if final_when is None or not row_valid(track_id, final_when, known_tracks, switch_ids):
            return
        store_lock(
            final_when,
            base_when,
            active_inherit,
            list(explicit_requires or []),
            unless_absent,
            unless_present,
            unless_held,
        )
    elif op == "amend":
        prev = state.get(track_id, _lock_entry({}, [], [], []))
        if when:
            if not row_valid(track_id, when, known_tracks, switch_ids):
                return
            base_when = {**prev["when"], **when}
        elif prev["when"]:
            base_when = dict(prev["when"])
        else:
            return
        active_inherit = inherit_when_from if inherit_when_from else list(prev.get("inherit_when_from", []))
        final_when = (
            merged_inherited_when(state, base_when, active_inherit)
            if active_inherit
            else base_when
        )
        if final_when is None or not row_valid(track_id, final_when, known_tracks, switch_ids):
            return
        merged_requires = (
            list(explicit_requires) if explicit_requires is not None else list(prev["requires"])
        )
        merged_unless_absent = unless_absent if unless_absent else list(prev["unless_absent"])
        merged_unless_present = unless_present if unless_present else list(prev["unless_present"])
        merged_unless_held = unless_held if unless_held else list(prev.get("unless_held", []))
        store_lock(
            final_when,
            base_when,
            active_inherit,
            merged_requires,
            merged_unless_absent,
            merged_unless_present,
            merged_unless_held,
            prev=prev,
        )
    elif op == "withdraw":
        state.pop(track_id, None)


def apply_fixpoints(state: dict[str, dict]) -> None:
    changed = True
    while changed:
        changed = False
        if recompute_inherited_when(state):
            changed = True
            continue
        for track_id, entry in list(state.items()):
            if not requires_when_satisfied(entry, state):
                del state[track_id]
                changed = True
                break
        for track_id, entry in list(state.items()):
            requires_match = entry.get("requires_match", {})
            if requires_match and not precondition_met(state, requires_match):
                del state[track_id]
                changed = True
                break
        for track_id, entry in list(state.items()):
            unless_matches = entry.get("unless_matches", {})
            if unless_matches and unless_matches_active(state, unless_matches):
                del state[track_id]
                changed = True
                break
        for track_id, entry in list(state.items()):
            if unless_requires_when_active(entry, state):
                del state[track_id]
                changed = True
                break
        for track_id, entry in list(state.items()):
            for absent in entry.get("unless_absent", []):
                if absent in state:
                    del state[track_id]
                    changed = True
                    break
        for track_id, entry in list(state.items()):
            for present in entry.get("unless_present", []):
                if present not in state:
                    del state[track_id]
                    changed = True
                    break
        for track_id, entry in list(state.items()):
            snapshots = entry.get("requires_snapshots", {})
            if not snapshots:
                continue
            for watched, snap in snapshots.items():
                if watched not in state:
                    continue
                current = tuple(sorted(effective_requires(state[watched], state)))
                if current != snap:
                    del state[track_id]
                    changed = True
                    break
            if changed:
                break
        for track_id, entry in list(state.items()):
            snapshots = entry.get("stable_snapshots", {})
            if not snapshots:
                continue
            for watched, snap in snapshots.items():
                if watched not in state:
                    del state[track_id]
                    changed = True
                    break
                watched_entry = state[watched]
                current = (
                    tuple(sorted(effective_requires(watched_entry, state))),
                    tuple(sorted(watched_entry.get("when", {}).items())),
                )
                if current != snap:
                    del state[track_id]
                    changed = True
                    break
            if changed:
                break


def attach_requires_snapshots(state: dict[str, dict], track_id: str, detail: str) -> None:
    """Record unless_requires_changed snapshots after a row successfully applies."""
    entry = state.get(track_id)
    if not entry:
        return
    _witness, _suppresses, _requires_match, _unless_matches, _binds, unless_changed, _requires_when, _unless_rw, _requires_stable, _inherit = (
        parse_detail_extras(detail)
    )
    merged = (
        unless_changed
        if unless_changed
        else list(entry.get("unless_requires_changed", []))
    )
    if not merged:
        return
    entry["unless_requires_changed"] = merged
    entry["requires_snapshots"] = capture_requires_snapshots(state, merged)


def attach_stable_snapshots(state: dict[str, dict], track_id: str, detail: str) -> None:
    """Record requires_stable snapshots after a row successfully applies."""
    entry = state.get(track_id)
    if not entry:
        return
    *_, requires_stable, _inherit = parse_detail_extras(detail)
    merged = requires_stable if requires_stable else list(entry.get("requires_stable", []))
    if not merged:
        return
    entry["requires_stable"] = merged
    entry["stable_snapshots"] = capture_stable_snapshots(state, merged)


def _fold_without_hold_release(
    rows: list[tuple],
    corrections: dict[int, tuple[str, str]],
    network: dict,
    upto_seq: int,
) -> dict[str, dict]:
    known_tracks = {track["id"] for track in network["tracks"]}
    switch_ids = set(network["switches"])
    subset = [row for row in rows if row[0] < upto_seq]
    revokes = compute_revoke_events(subset, corrections)
    voided_seqs = compute_voided_seqs(subset, corrections)
    state: dict[str, dict] = {}
    for row in subset:
        seq, bulletin, op, track_id, detail = effective_row(row, corrections)
        when, explicit_requires, anchor_bulletin, unless_absent, unless_present, unless_held, expires_after, row_stamp, _pre, _ex = (
            parse_detail(detail)
        )
        if op == "revoke" or row_voided(
            seq,
            bulletin,
            track_id,
            anchor_bulletin,
            expires_after,
            row_stamp,
            revokes,
            voided_seqs,
        ):
            continue
        if op in ("hold", "release", "withdraw"):
            if op == "withdraw":
                state.pop(track_id, None)
            continue
        if op in ("add", "amend", "replace"):
            if op in ("add", "replace"):
                if not row_valid(track_id, when, known_tracks, switch_ids):
                    continue
                state[track_id] = {
                    "when": dict(when),
                    "requires": list(explicit_requires or []),
                    "unless_absent": list(unless_absent),
                    "unless_present": list(unless_present),
                }
            else:
                prev = state.get(
                    track_id,
                    {"when": {}, "requires": [], "unless_absent": [], "unless_present": []},
                )
                if when:
                    if not row_valid(track_id, when, known_tracks, switch_ids):
                        continue
                    merged_when = {**prev["when"], **when}
                elif prev["when"]:
                    merged_when = dict(prev["when"])
                else:
                    continue
                merged_requires = (
                    list(explicit_requires)
                    if explicit_requires is not None
                    else list(prev["requires"])
                )
                merged_unless_absent = (
                    unless_absent if unless_absent else list(prev["unless_absent"])
                )
                merged_unless_present = (
                    unless_present if unless_present else list(prev["unless_present"])
                )
                state[track_id] = {
                    "when": merged_when,
                    "requires": merged_requires,
                    "unless_absent": merged_unless_absent,
                    "unless_present": merged_unless_present,
                }
        apply_fixpoints(state)
    apply_fixpoints(state)
    return state


def _resolve_lock_state(
    network: dict,
    rows: list[tuple],
    corrections: dict[int, tuple[str, str]],
) -> dict[str, dict]:
    """Fold the bulletin log into the internal lock-state map."""
    from collections import defaultdict

    known_tracks = {track["id"] for track in network["tracks"]}
    switch_ids = set(network["switches"])
    revokes = compute_revoke_events(rows, corrections)
    voided_seqs = compute_voided_seqs(rows, corrections)
    state: dict[str, dict] = {}
    hold_stacks: dict[str, list[tuple[str, dict | None]]] = {}
    pending: dict[str, list[tuple]] = defaultdict(list)
    applied_bulletins: set[str] = set()

    def row_is_voided(seq: int, bulletin: str, track_id: str, detail: str) -> bool:
        _when, _req, anchor, _ua, _up, _uh, expires_after, row_stamp, _pre, _ex = parse_detail(detail)
        return row_voided(
            seq,
            bulletin,
            track_id,
            anchor,
            expires_after,
            row_stamp,
            revokes,
            voided_seqs,
        )

    def process_row(row: tuple) -> None:
        seq, bulletin, op, track_id, detail = effective_row(row, corrections)
        if op == "revoke" or row_is_voided(seq, bulletin, track_id, detail):
            return
        if op == "hold":
            apply_hold(state, hold_stacks, track_id, parse_hold_id(detail, bulletin))
            apply_unless_held_cascade(state, hold_stacks)
        elif op == "release":
            if apply_release(state, hold_stacks, track_id, parse_release_hold_id(detail)):
                restore_dependent_locks(
                    state,
                    rows,
                    corrections,
                    network,
                    seq,
                    track_id,
                    voided_seqs,
                    hold_stacks,
                    applied_bulletins,
                )
                reapply_unless_present_rows(
                    state,
                    rows,
                    corrections,
                    network,
                    seq,
                    revokes,
                    hold_stacks,
                    voided_seqs,
                    applied_bulletins,
                )
        elif track_is_held(hold_stacks, track_id):
            return
        elif op in ("add", "amend", "replace", "withdraw"):
            when, explicit_requires, _anchor, unless_absent, unless_present, unless_held, _exp, _stamp, precondition, exclusive_with = (
                parse_detail(detail)
            )
            witness, _suppresses, requires_match, unless_matches, _binds, _unless_changed, _requires_when, _unless_rw, _requires_stable, _inherit = (
                parse_detail_extras(detail)
            )
            if witness and not witness_satisfied(witness, detail, applied_bulletins, state):
                return
            if unless_held and any(
                track_is_held(hold_stacks, held_track) for held_track in unless_held
            ):
                return
            if precondition and not precondition_met(state, precondition):
                return
            if requires_match and not precondition_met(state, requires_match):
                return
            if unless_matches and unless_matches_active(state, unless_matches):
                return
            before = json.dumps(state.get(track_id)) if track_id in state else None
            apply_lock_row(state, op, track_id, detail, known_tracks, switch_ids)
            apply_exclusive_with(state, exclusive_with)
            after = json.dumps(state.get(track_id)) if track_id in state else None
            if op == "withdraw" or before != after:
                applied_bulletins.add(bulletin)
                if track_id in state:
                    state[track_id]["_bulletin"] = bulletin
                    attach_requires_snapshots(state, track_id, detail)
                    attach_stable_snapshots(state, track_id, detail)
        apply_fixpoints(state)

    def flush_deferred(trigger_bulletin: str) -> None:
        deferred = sorted(pending.pop(trigger_bulletin, []), key=lambda item: item[0])
        for deferred_row in deferred:
            process_row(deferred_row)

    for row in rows:
        _seq, bulletin, _op, _track_id, detail = effective_row(row, corrections)
        _coupling, _decouple, defer_until, _supersedes = parse_detail_flags(detail)
        if defer_until:
            pending[defer_until].append(row)
            continue
        process_row(row)
        flush_deferred(bulletin)

    apply_fixpoints(state)
    return state


def effective_lock_state(
    network: dict | None = None, rows: list[tuple] | None = None
) -> dict[str, dict]:
    """Return the resolved lock map including requires metadata."""
    network = network or load_network()
    rows = rows if rows is not None else lock_log_rows()
    corrections = lock_corrections()
    return _resolve_lock_state(network, rows, corrections)


def effective_locks(network: dict | None = None, rows: list[tuple] | None = None) -> list[dict]:
    """Resolve the bulletin log into the operative route-lock set."""
    network = network or load_network()
    rows = rows if rows is not None else lock_log_rows()
    corrections = lock_corrections()
    state = _resolve_lock_state(network, rows, corrections)
    return [{"track": track, "when": state[track]["when"]} for track in sorted(state)]


def lock_map(locks: list[dict] | None = None) -> dict[str, dict]:
    locks = locks if locks is not None else effective_locks()
    return {lock["track"]: lock["when"] for lock in locks}


def track_locked(locks: dict[str, dict], track_id: str, switches: dict[str, str]) -> bool:
    when = locks.get(track_id)
    if not when:
        return False
    return all(switches.get(sw) == pos for sw, pos in when.items())


def active_edge(track: dict, switches: dict[str, str]) -> bool:
    when = track.get("when")
    if not when:
        return True
    return all(switches.get(sw) == pos for sw, pos in when.items())


def neighbors(network: dict, station: str, switches: dict[str, str], locks: dict[str, dict]) -> list[str]:
    outs: list[str] = []
    for track in network["tracks"]:
        if track_locked(locks, track["id"], switches):
            continue
        if not active_edge(track, switches):
            continue
        src, dst = track["from"], track["to"]
        if src == station and dst not in outs:
            outs.append(dst)
        elif dst == station and src not in outs:
            outs.append(src)
    resolved: list[str] = []
    for node in outs:
        if node.startswith("sw"):
            for track2 in network["tracks"]:
                if track_locked(locks, track2["id"], switches):
                    continue
                if not active_edge(track2, switches):
                    continue
                if track2["from"] == node:
                    resolved.append(track2["to"])
                elif track2["to"] == node:
                    resolved.append(track2["from"])
        else:
            resolved.append(node)
    return [node for node in resolved if not node.startswith("sw")]


def find_path(
    network: dict,
    start: str,
    goal: str,
    switches: dict[str, str],
    locks: dict[str, dict],
) -> list[str] | None:
    queue = [(start, [start])]
    seen = {start}
    while queue:
        node, path = queue.pop(0)
        if node == goal:
            return path
        for nxt in neighbors(network, node, switches, locks):
            if nxt in seen:
                continue
            seen.add(nxt)
            queue.append((nxt, path + [nxt]))
    return None


def switch_plans(network: dict) -> list[dict[str, str]]:
    switch_ids = sorted(network["switches"])
    positions = ("north", "south")
    return [
        dict(zip(switch_ids, combo, strict=True))
        for combo in product(positions, repeat=len(switch_ids))
    ]


def operative_profile() -> tuple[str, dict[str, str]]:
    """Return the unique operative goal and one switch lineup that reaches it."""
    network = load_network()
    locks = lock_map(effective_locks(network))
    candidates = arrival_candidates()
    reachable: dict[str, list[dict[str, str]]] = {station: [] for station in candidates}
    for switches in switch_plans(network):
        for station in candidates:
            if find_path(network, "A", station, switches, locks):
                reachable[station].append(switches)
    winners = [station for station, plans in reachable.items() if plans]
    if len(winners) != 1:
        raise RuntimeError(f"evidence model is ambiguous: {reachable}")
    goal = winners[0]
    return goal, reachable[goal][0]


def decoy_arrivals() -> list[str]:
    goal, _switches = operative_profile()
    return [station for station in arrival_candidates() if station != goal]


def normalized_locks(locks: list[dict]) -> set[tuple]:
    out = set()
    for lock in locks:
        when = lock.get("when", {})
        out.add((lock.get("track"), tuple(sorted(when.items()))))
    return out


def history_is_legal(
    network: dict,
    history: list[str],
    switches: dict[str, str],
    locks: dict[str, dict],
) -> bool:
    if not history or history[0] != "A":
        return False
    for left, right in zip(history, history[1:], strict=False):
        if right not in neighbors(network, left, switches, locks):
            return False
    return True


def run_shift() -> subprocess.CompletedProcess:
    if OUTPUT.exists():
        OUTPUT.unlink()
    if DISPATCH_DB.exists():
        DISPATCH_DB.unlink()
    return subprocess.run(
        ["python3", str(PLAY)],
        capture_output=True,
        text=True,
        check=False,
    )


def attempt_dispatch(switches: dict, target: str) -> tuple[int, dict | None]:
    """Open a fresh session, apply switches, and try to dispatch to target."""
    reset_referee()
    status, _ = request_json("POST", "/v1/session/start")
    if status != 200:
        return status, None
    for switch_id, position in sorted(switches.items()):
        request_json("POST", f"/v1/switch/{switch_id}", {"position": position})
    return request_json("POST", "/v1/dispatch", {"to": target})


def dispatch_success_count() -> int:
    conn = sqlite3.connect(DISPATCH_DB)
    try:
        cur = conn.execute("SELECT COUNT(*) FROM dispatch_log WHERE outcome = 'ok'")
        return int(cur.fetchone()[0])
    finally:
        conn.close()
