#!/usr/bin/env python3
"""Scratch harness — confirm lock traps produce unique operative/decoy arrivals."""

from __future__ import annotations

import json
from dataclasses import dataclass

# --- graph ---

STATIONS = {"A", "B", "C", "D", "E", "F", "G"}
ARRIVALS = {"D", "F", "G"}
SWITCHES = ("sw1", "sw2", "sw3")

TRACKS = [
    {"id": "t_a_sw1", "from": "A", "to": "sw1"},
    {"id": "t_sw1_b", "from": "sw1", "to": "B", "when": {"sw1": "north"}},
    {"id": "t_sw1_c", "from": "sw1", "to": "C", "when": {"sw1": "south"}},
    {"id": "t_b_sw2", "from": "B", "to": "sw2"},
    {"id": "t_sw2_d", "from": "sw2", "to": "D", "when": {"sw2": "north"}},
    {"id": "t_c_sw3", "from": "C", "to": "sw3"},
    {"id": "t_sw3_f", "from": "sw3", "to": "F", "when": {"sw3": "north"}},
    {"id": "t_sw3_g", "from": "sw3", "to": "G", "when": {"sw3": "south"}},
]

@dataclass(frozen=True)
class LogRow:
    seq: int
    bulletin: str
    op: str
    track: str
    detail: str


LOCK_LOG = [
    LogRow(1, "BUL-A", "add", "t_sw3_g", json.dumps({"sw3": "south"})),
    LogRow(2, "BUL-B", "revoke", "BUL-A", ""),
    LogRow(3, "BUL-C", "add", "t_sw3_f", json.dumps({"sw3": "north"})),
    LogRow(
        4,
        "BUL-C",
        "add",
        "t_sw1_c",
        json.dumps({"when": {"sw1": "north"}, "requires": ["t_sw3_f"]}),
    ),
    LogRow(5, "BUL-D", "withdraw", "t_sw3_f", ""),
    LogRow(6, "BUL-E", "revoke", "BUL-D", ""),
    LogRow(7, "BUL-F", "add", "t_sw2_d", json.dumps({"sw2": "north"})),
    LogRow(8, "BUL-G", "amend", "t_sw3_f", json.dumps({"sw1": "south"})),
    LogRow(9, "BUL-H", "revoke", "BUL-C", json.dumps(["t_sw3_f"])),
    LogRow(10, "BUL-I", "amend", "t_sw3_f", json.dumps({"sw3": "north"})),
    LogRow(11, "BUL-M", "amend", "t_sw2_d", json.dumps({"requires": ["t_sw1_c"]})),
    LogRow(12, "BUL-J", "add", "t_sw3_g", "A-G: sealed while sw3 holds south"),
    LogRow(13, "BUL-K", "add", "t_phantom", json.dumps({"sw9": "north"})),
    LogRow(14, "BUL-L", "withdraw", "t_never_added", ""),
]


def parse_detail(detail: str) -> tuple[dict[str, str], list[str] | None]:
    try:
        obj = json.loads(detail)
    except json.JSONDecodeError:
        return {}, None
    if not isinstance(obj, dict):
        return {}, None
    has_requires = "requires" in obj
    explicit_requires: list[str] | None = None
    if has_requires:
        raw_requires = obj.get("requires", [])
        if not isinstance(raw_requires, list):
            return {}, None
        explicit_requires = [req for req in raw_requires if isinstance(req, str)]
    if "when" in obj:
        when = obj.get("when", {})
    elif has_requires and set(obj) == {"requires"}:
        when = {}
    else:
        when = obj
    if not isinstance(when, dict):
        return {}, explicit_requires
    return when, explicit_requires


def parse_revoke_scope(detail: str) -> set[str] | None:
    if not detail.strip():
        return None
    try:
        obj = json.loads(detail)
    except json.JSONDecodeError:
        return None
    return set(obj) if isinstance(obj, list) else None


def compute_void_sets(rows: list[LogRow]) -> tuple[set[str], set[tuple[str, str]]]:
    voided: set[str] = set()
    partial: set[tuple[str, str]] = set()
    for row in rows:
        if row.op != "revoke":
            continue
        scope = parse_revoke_scope(row.detail)
        if scope is None:
            voided.add(row.track)
        else:
            for track_id in scope:
                partial.add((row.track, track_id))
    return voided, partial


def row_voided(
    bulletin: str,
    track_id: str,
    voided: set[str],
    partial: set[tuple[str, str]],
) -> bool:
    return bulletin in voided or (bulletin, track_id) in partial


def row_valid(track: str, when: dict[str, str], known_tracks: set[str]) -> bool:
    if track not in known_tracks or not when:
        return False
    return all(sw in SWITCHES and pos in ("north", "south") for sw, pos in when.items())


def apply_requires_fixpoint(state: dict[str, dict]) -> None:
    changed = True
    while changed:
        changed = False
        for track_id, entry in list(state.items()):
            for req in entry.get("requires", []):
                if req not in state:
                    del state[track_id]
                    changed = True
                    break


def effective_locks(rows: list[LogRow], *, full_bul_c_revoke: bool) -> dict[str, dict]:
    known_tracks = {t["id"] for t in TRACKS}
    voided, partial = compute_void_sets(rows)
    if full_bul_c_revoke:
        voided.add("BUL-C")
    state: dict[str, dict] = {}
    for row in rows:
        if row.op == "revoke":
            continue
        if row_voided(row.bulletin, row.track, voided, partial):
            continue
        if row.op in ("add", "amend"):
            when, explicit_requires = parse_detail(row.detail)
            if row.op == "add":
                if not row_valid(row.track, when, known_tracks):
                    continue
                state[row.track] = {
                    "when": dict(when),
                    "requires": list(explicit_requires or []),
                }
            else:
                prev = state.get(row.track, {"when": {}, "requires": []})
                if when:
                    if not row_valid(row.track, when, known_tracks):
                        continue
                    merged_when = {**prev["when"], **when}
                elif prev["when"]:
                    merged_when = dict(prev["when"])
                else:
                    continue
                if explicit_requires is not None:
                    merged_requires = list(explicit_requires)
                else:
                    merged_requires = list(prev["requires"])
                state[row.track] = {"when": merged_when, "requires": merged_requires}
        elif row.op == "withdraw":
            state.pop(row.track, None)
    apply_requires_fixpoint(state)
    return {track: entry["when"] for track, entry in state.items()}


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


def neighbors(station: str, switches: dict[str, str], locks: dict[str, dict]) -> list[str]:
    outs: list[str] = []
    for track in TRACKS:
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
            for track2 in TRACKS:
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
    return [n for n in resolved if not n.startswith("sw")]


def find_path(start: str, goal: str, switches: dict[str, str], locks: dict[str, dict]) -> list[str] | None:
    queue = [(start, [start])]
    seen = {start}
    while queue:
        node, path = queue.pop(0)
        if node == goal:
            return path
        for nxt in neighbors(node, switches, locks):
            if nxt in seen:
                continue
            seen.add(nxt)
            queue.append((nxt, path + [nxt]))
    return None


def reachable_arrivals(locks: dict[str, dict]) -> dict[str, list[dict[str, str]]]:
    found: dict[str, list[dict[str, str]]] = {a: [] for a in sorted(ARRIVALS)}
    for bits in range(2 ** len(SWITCHES)):
        switches = {
            sw: ("south" if (bits >> i) & 1 else "north")
            for i, sw in enumerate(SWITCHES)
        }
        for arrival in ARRIVALS:
            if find_path("A", arrival, switches, locks):
                found[arrival].append(switches)
    return found


def main() -> None:
    correct = effective_locks(LOCK_LOG, full_bul_c_revoke=False)
    naive_full = effective_locks(LOCK_LOG, full_bul_c_revoke=True)
    naive_ignore_revokes = effective_locks(
        [r for r in LOCK_LOG if r.op != "revoke"], full_bul_c_revoke=False
    )
    print("correct locks:", correct)
    print("naive full BUL-C revoke:", naive_full)
    print("naive ignore revokes:", naive_ignore_revokes)
    c = reachable_arrivals(correct)
    n = reachable_arrivals(naive_full)
    print("correct reachability:", {k: len(v) for k, v in c.items()})
    print("naive reachability:", {k: len(v) for k, v in n.items()})
    assert correct["t_sw3_f"] == {"sw3": "north", "sw1": "south"}, correct
    assert correct["t_sw1_c"] == {"sw1": "north"}, correct
    assert c["G"] and not c["D"] and not c["F"], c
    assert naive_ignore_revokes["t_sw3_g"] == {"sw3": "south"}
    assert "t_sw1_c" not in naive_full
    print("OK: cascade trap validates")


if __name__ == "__main__":
    main()
