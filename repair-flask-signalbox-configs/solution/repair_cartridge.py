#!/usr/bin/env python3
"""Repair the Signalbox cartridge from evidence.duckdb.

Resolves the bulletin-keyed route-lock log (including partial revoke voiding, amend
merge, requires/unless_absent/unless_present cascades, hold/release corrections, stamp revoke, and
expires_after triggers), derives the unique operative arrival by reachability, and
rebuilds dispatch metadata.
"""

from __future__ import annotations

import json
from itertools import product
from pathlib import Path

import duckdb
import yaml

CARTRIDGE = Path("/app/cartridge")
EVIDENCE = Path("/app/data/evidence.duckdb")


def parse_hold_id(detail: str, bulletin: str) -> str:
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
    if not detail or not detail.strip():
        return None
    try:
        obj = json.loads(detail)
    except (json.JSONDecodeError, TypeError):
        return None
    if isinstance(obj, dict) and isinstance(obj.get("hold_id"), str):
        return obj["hold_id"]
    return None


def track_is_held(hold_stacks, track_id: str) -> bool:
    return bool(hold_stacks.get(track_id))


def apply_hold(state, hold_stacks, track_id: str, hold_id: str) -> None:
    saved = dict(state[track_id]) if track_id in state else None
    hold_stacks.setdefault(track_id, []).append((hold_id, saved))
    state.pop(track_id, None)


def apply_release(state, hold_stacks, track_id: str, required_hold_id: str | None) -> bool:
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
    state,
    rows,
    corrections,
    network,
    release_seq,
    restored_track,
    voided_seqs,
    hold_stacks,
    applied_bulletins,
):
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
    state,
    rows,
    corrections,
    network,
    release_seq,
    revokes,
    hold_stacks,
    voided_seqs,
    applied_bulletins,
):
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


def precondition_met(state, precondition: dict[str, dict]) -> bool:
    for track_id, required_when in precondition.items():
        entry = state.get(track_id)
        if not entry:
            return False
        current = entry.get("when", {})
        for switch_id, position in required_when.items():
            if current.get(switch_id) != position:
                return False
    return True


def apply_exclusive_with(state, exclusive_with: list[str]) -> None:
    for track_id in exclusive_with:
        state.pop(track_id, None)


def parse_detail(detail: str):
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


def parse_detail_flags(detail: str):
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


def _parse_match_map(raw):
    if not isinstance(raw, dict):
        return {}
    parsed = {}
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


def parse_detail_extras(detail: str):
    try:
        obj = json.loads(detail)
    except (json.JSONDecodeError, TypeError):
        return None, [], {}, {}, [], [], {}, {}, [], []
    if not isinstance(obj, dict):
        return None, [], {}, {}, [], [], {}, {}, [], []
    witness = obj.get("witness")
    witness_bulletin = witness if isinstance(witness, str) else None
    suppresses = []
    raw_suppresses = obj.get("suppresses", [])
    if isinstance(raw_suppresses, list):
        suppresses = [item for item in raw_suppresses if isinstance(item, str)]
    binds_requires = []
    raw_binds = obj.get("binds_requires", [])
    if isinstance(raw_binds, list):
        binds_requires = [item for item in raw_binds if isinstance(item, str)]
    unless_requires_changed = []
    raw_unless_changed = obj.get("unless_requires_changed", [])
    if isinstance(raw_unless_changed, list):
        unless_requires_changed = [
            item for item in raw_unless_changed if isinstance(item, str)
        ]
    requires_stable = []
    raw_stable = obj.get("requires_stable", [])
    if isinstance(raw_stable, list):
        requires_stable = [item for item in raw_stable if isinstance(item, str)]
    inherit_when_from = []
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


def parse_witness_active(detail: str) -> bool:
    try:
        obj = json.loads(detail)
    except (json.JSONDecodeError, TypeError):
        return False
    return isinstance(obj, dict) and bool(obj.get("witness_active"))


def bulletin_has_active_row(state, bulletin: str) -> bool:
    return any(entry.get("_bulletin") == bulletin for entry in state.values())


def witness_satisfied(witness, detail, applied_bulletins, state) -> bool:
    if not witness:
        return True
    if witness not in applied_bulletins:
        return False
    if parse_witness_active(detail):
        return bulletin_has_active_row(state, witness)
    return True


def unless_matches_active(state, unless_matches):
    for track_id, required_when in unless_matches.items():
        entry = state.get(track_id)
        if not entry:
            continue
        current = entry.get("when", {})
        if all(current.get(switch_id) == position for switch_id, position in required_when.items()):
            return True
    return False


def _lock_entry(
    when,
    requires,
    unless_absent,
    unless_present,
    unless_held=None,
    requires_match=None,
    unless_matches=None,
    binds_requires=None,
    unless_requires_changed=None,
    requires_when=None,
    unless_requires_when=None,
    requires_stable=None,
    inherit_when_from=None,
    base_when=None,
    requires_snapshots=None,
    stable_snapshots=None,
):
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


def capture_requires_snapshots(state, unless_requires_changed):
    snapshots = {}
    for watched in unless_requires_changed:
        if watched in state:
            snapshots[watched] = tuple(sorted(effective_requires(state[watched], state)))
    return snapshots


def merged_inherited_when(state, base_when, inherit_when_from):
    merged = dict(base_when)
    for source in inherit_when_from:
        if source not in state:
            return None
        merged.update(state[source].get("when", {}))
    return merged


def recompute_inherited_when(state):
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


def capture_stable_snapshots(state, requires_stable):
    snapshots = {}
    for watched in requires_stable:
        if watched in state:
            entry = state[watched]
            snapshots[watched] = (
                tuple(sorted(effective_requires(entry, state))),
                tuple(sorted(entry.get("when", {}).items())),
            )
    return snapshots


def attach_requires_snapshots(state, track_id, detail):
    entry = state.get(track_id)
    if not entry:
        return
    _witness, _suppresses, _requires_match, _unless_matches, _binds, unless_changed, _requires_when, _unless_rw, _requires_stable, _inherit = (
        parse_detail_extras(detail)
    )
    merged = (
        unless_changed if unless_changed else list(entry.get("unless_requires_changed", []))
    )
    if not merged:
        return
    entry["unless_requires_changed"] = merged
    entry["requires_snapshots"] = capture_requires_snapshots(state, merged)


def attach_stable_snapshots(state, track_id, detail):
    entry = state.get(track_id)
    if not entry:
        return
    *_, requires_stable, _inherit = parse_detail_extras(detail)
    merged = requires_stable if requires_stable else list(entry.get("requires_stable", []))
    if not merged:
        return
    entry["requires_stable"] = merged
    entry["stable_snapshots"] = capture_stable_snapshots(state, merged)


def effective_requires(entry, state):
    merged = list(entry.get("requires", []))
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


def requires_when_satisfied(entry, state):
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


def unless_requires_when_active(entry, state):
    unless_requires_when = entry.get("unless_requires_when", {})
    for track_id, needed in unless_requires_when.items():
        watched = state.get(track_id)
        if not watched:
            continue
        current = watched.get("when", {})
        if not all(current.get(switch_id) == position for switch_id, position in needed.items()):
            return True
    return False


def parse_revoke_scope(detail: str, track_id: str) -> tuple[str, str, set[str] | None]:
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


def compute_revoke_events(rows, corrections):
    events = []
    for row in rows:
        seq, bulletin, op, track_id, detail = effective_row(row, corrections)
        if op != "revoke":
            continue
        kind, target, scope = parse_revoke_scope(detail, track_id)
        events.append((seq, kind, target, scope))
    return events


def effective_row(row, corrections):
    seq, bulletin, op, track_id, detail = row
    if seq in corrections:
        op, detail = corrections[seq]
    return seq, bulletin, op, track_id, detail


def row_voided(row_seq, bulletin, track_id, anchor_bulletin, expires_after, row_stamp, revokes, voided_seqs=None):
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


def row_valid(track_id, when, known_tracks, switches):
    if track_id not in known_tracks:
        return False
    if not when:
        return False
    return all(sw in switches and pos in ("north", "south") for sw, pos in when.items())


def compute_voided_seqs(rows, corrections):
    revokes = compute_revoke_events(rows, corrections)
    voided = set()
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
            _coupling, _decouple, _defer, supersedes = parse_detail_flags(detail)
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
            coupling_ids = set()
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
                coupled_seq, _cb, _cop, _ct, coupled_detail = effective_row(coupled, corrections)
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
            _witness, suppresses, _requires_match, _unless_matches, _binds, _unless_changed, _requires_when, _unless_rw, _requires_stable, _inherit = parse_detail_extras(detail)
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


def apply_unless_held_cascade(state, hold_stacks):
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


def apply_lock_row(state, op, track_id, detail, known_tracks, switch_ids):
    when, explicit_requires, _anchor, unless_absent, unless_present, unless_held, _exp, _stamp, _pre, _ex = parse_detail(
        detail
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

    def store_lock(final_when, base_when, active_inherit, requires, unless_absent_list, unless_present_list, unless_held_list, prev=None):
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


def apply_fixpoints(state):
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


def fold_without_hold_release(rows, corrections, network, upto_seq):
    known_tracks = {track["id"] for track in network["tracks"]}
    switch_ids = set(network["switches"])
    subset = [row for row in rows if row[0] < upto_seq]
    revokes = compute_revoke_events(subset, corrections)
    state = {}
    for row in subset:
        seq, bulletin, op, track_id, detail = effective_row(row, corrections)
        when, explicit_requires, anchor_bulletin, unless_absent, unless_present, unless_held, expires_after, row_stamp, _pre, _ex = (
            parse_detail(detail)
        )
        if op == "revoke" or row_voided(
            seq, bulletin, track_id, anchor_bulletin, expires_after, row_stamp, revokes
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


def effective_locks(network: dict, rows: list[tuple], corrections: dict[int, tuple[str, str]]) -> list[dict]:
    from collections import defaultdict

    known_tracks = {track["id"] for track in network["tracks"]}
    switch_ids = set(network["switches"])
    revokes = compute_revoke_events(rows, corrections)
    voided_seqs = compute_voided_seqs(rows, corrections)
    state = {}
    hold_stacks = {}
    pending = defaultdict(list)
    applied_bulletins = set()

    def row_is_voided(seq, bulletin, track_id, detail):
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

    def process_row(row):
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
            _when, _req, _anchor, _ua, _up, unless_held, _exp, _stamp, precondition, exclusive_with = parse_detail(
                detail
            )
            witness, _suppresses, requires_match, unless_matches, _binds, _unless_changed, _requires_when, _unless_rw, _requires_stable, _inherit = parse_detail_extras(detail)
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

    def flush_deferred(trigger_bulletin):
        deferred = sorted(pending.pop(trigger_bulletin, []), key=lambda item: item[0])
        for deferred_row in deferred:
            process_row(deferred_row)

    for row in rows:
        _seq, bulletin, _op, _track_id, detail = effective_row(row, corrections)
        _coupling, _decouple, defer_until, _sup = parse_detail_flags(detail)
        if defer_until:
            pending[defer_until].append(row)
            continue
        process_row(row)
        flush_deferred(bulletin)

    apply_fixpoints(state)
    return [{"track": track, "when": state[track]["when"]} for track in sorted(state)]


def lock_map(locks: list[dict]) -> dict[str, dict]:
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


def find_path(network, start, goal, switches, locks):
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


def operative_plan(network: dict, locks: dict[str, dict], candidates: list[str]) -> tuple[str, dict[str, str]]:
    reachable: dict[str, list[dict[str, str]]] = {station: [] for station in candidates}
    for switches in switch_plans(network):
        for station in candidates:
            if find_path(network, "A", station, switches, locks):
                reachable[station].append(switches)
    winners = [station for station, plans in reachable.items() if plans]
    if len(winners) != 1:
        raise RuntimeError(f"expected one operative arrival, got {reachable}")
    goal = winners[0]
    return goal, reachable[goal][0]


def hint_map(conn: duckdb.DuckDBPyConnection) -> dict[str, str]:
    rows = conn.execute(
        "SELECT station_id, hint FROM hint_clues ORDER BY seq"
    ).fetchall()
    return {station: hint for station, hint in rows}


def main() -> None:
    network_path = CARTRIDGE / "network.yaml"
    network = yaml.safe_load(network_path.read_text(encoding="utf-8"))

    conn = duckdb.connect(str(EVIDENCE), read_only=True)
    rows = conn.execute(
        "SELECT seq, bulletin, op, track_id, detail FROM route_lock_log ORDER BY seq"
    ).fetchall()
    corrections = {
        int(seq): (op, detail)
        for seq, op, detail in conn.execute(
            "SELECT seq, effective_op, effective_detail FROM lock_corrections ORDER BY seq"
        ).fetchall()
    }
    candidates = [
        row[0]
        for row in conn.execute(
            "SELECT station_id FROM arrival_candidates ORDER BY station_id"
        ).fetchall()
    ]
    train = conn.execute(
        "SELECT value FROM shift_meta WHERE key = 'train'"
    ).fetchone()[0]
    hints = hint_map(conn)
    conn.close()

    locks = effective_locks(network, rows, corrections)
    network["route_locks"] = locks
    network_path.write_text(yaml.safe_dump(network, sort_keys=False), encoding="utf-8")

    goal, switches = operative_plan(network, lock_map(locks), candidates)

    lines = [
        "[shift]",
        'start_station = "A"',
        f'goal_station = "{goal}"',
        f'train = "{train}"',
        "",
        "[hints]",
    ]
    for key in sorted(hints):
        lines.append(f'{key} = "{hints[key]}"')
    lines += ["", "[scoring]", "min_moves = 2", "", "[validation]"]
    for sw in sorted(switches):
        lines.append(f'{sw} = "{switches[sw]}"')
    (CARTRIDGE / "dispatch.toml").write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
