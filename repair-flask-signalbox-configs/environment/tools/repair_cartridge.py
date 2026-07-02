#!/usr/bin/env python3
"""Broken cartridge repair helper — predates the bulletin tail; fix before use."""

from __future__ import annotations

import json
from itertools import product
from pathlib import Path

import duckdb
import yaml

CARTRIDGE = Path("/app/cartridge")
EVIDENCE = Path("/app/data/evidence.duckdb")
SEAL_TRACKS = {"t_sw1_c", "t_sw2_d", "t_sw3_f", "t_sw3_g"}


def load_rows() -> list[tuple]:
    conn = duckdb.connect(str(EVIDENCE), read_only=True)
    try:
        return conn.execute(
            "SELECT seq, bulletin, op, track_id, detail FROM route_lock_log ORDER BY seq"
        ).fetchall()
    finally:
        conn.close()


def load_corrections() -> dict[int, tuple[str, str]]:
    conn = duckdb.connect(str(EVIDENCE), read_only=True)
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


def parse_when(detail: str) -> dict[str, str]:
    if not detail:
        return {}
    try:
        obj = json.loads(detail)
    except json.JSONDecodeError:
        return {}
    if not isinstance(obj, dict):
        return {}
    when = obj.get("when")
    if isinstance(when, dict):
        return {k: str(v) for k, v in when.items()}
    return {k: str(v) for k, v in obj.items() if k in ("sw1", "sw2", "sw3")}


def naive_locks(rows: list[tuple], corrections: dict[int, tuple[str, str]]) -> dict[str, dict]:
    """Naive latest-row correlator — wrong for rescission, holds, and tail cascades."""
    state: dict[str, dict] = {}
    voided_bulletins: set[str] = set()
    for row in rows:
        seq, bulletin, op, track_id, detail = effective_row(row, corrections)
        if track_id not in SEAL_TRACKS:
            continue
        if op == "revoke":
            voided_bulletins.add(track_id if track_id.startswith("BUL-") else bulletin)
            continue
        if bulletin in voided_bulletins:
            continue
        if op in ("add", "amend", "replace"):
            when = parse_when(detail)
            if track_id in state and op == "amend":
                state[track_id].update(when)
            else:
                state[track_id] = when
        elif op in ("withdraw", "release"):
            state.pop(track_id, None)
    return state


def operative_goal(network: dict, locks: dict[str, dict]) -> str:
    stations = network["stations"]
    tracks = network["tracks"]
    switches = network["switches"]
    switch_ids = list(switches)
    positions = {sid: switches[sid]["positions"] for sid in switch_ids}
    candidates = []
    conn = duckdb.connect(str(EVIDENCE), read_only=True)
    try:
        arrivals = [
            row[0]
            for row in conn.execute(
                "SELECT station_id FROM arrival_candidates ORDER BY station_id"
            ).fetchall()
        ]
    finally:
        conn.close()
    for combo in product(*[positions[sid] for sid in switch_ids]):
        switch_map = dict(zip(switch_ids, combo, strict=True))
        if not reachable("A", arrivals, stations, tracks, locks, switch_map):
            continue
        for station in arrivals:
            if reachable("A", [station], stations, tracks, locks, switch_map):
                candidates.append(station)
    unique = sorted(set(candidates))
    if len(unique) != 1:
        return "F"
    return unique[0]


def reachable(
    start: str,
    goals: list[str],
    stations: dict,
    tracks: list[dict],
    locks: dict[str, dict],
    switch_map: dict[str, str],
) -> bool:
    seen = {start}
    stack = [start]
    while stack:
        node = stack.pop()
        if node in goals:
            return True
        for track in tracks:
            if track.get("from") != node:
                continue
            tid = track["id"]
            if tid in locks:
                when = locks[tid]
                if any(switch_map.get(sw) != pos for sw, pos in when.items()):
                    continue
            dest = track.get("to")
            if dest in stations or dest in switch_map:
                if dest not in seen:
                    seen.add(dest)
                    stack.append(dest)
    return False


def hint_map() -> dict[str, str]:
    conn = duckdb.connect(str(EVIDENCE), read_only=True)
    try:
        rows = conn.execute(
            "SELECT station_id, hint FROM hint_clues ORDER BY seq"
        ).fetchall()
    finally:
        conn.close()
    return {station: hint for station, hint in rows}


def shift_meta() -> dict[str, str]:
    conn = duckdb.connect(str(EVIDENCE), read_only=True)
    try:
        rows = conn.execute("SELECT key, value FROM shift_meta").fetchall()
    finally:
        conn.close()
    return {key: value for key, value in rows}


def main() -> None:
    network = yaml.safe_load((CARTRIDGE / "network.yaml").read_text(encoding="utf-8"))
    rows = load_rows()
    corrections = load_corrections()
    locks = naive_locks(rows, corrections)
    network["route_locks"] = [{"track": tid, "when": when} for tid, when in sorted(locks.items())]
    (CARTRIDGE / "network.yaml").write_text(
        yaml.safe_dump(network, sort_keys=False), encoding="utf-8"
    )
    goal = operative_goal(network, locks)
    meta = shift_meta()
    hints = hint_map()
    dispatch = {
        "shift": {
            "start_station": meta.get("start_station", "A"),
            "goal_station": goal,
            "train": meta.get("train", "orient-7"),
        },
        "hints": hints,
        "scoring": {"min_moves": 2},
        "validation": {"sw1": "south", "sw2": "north", "sw3": "north"},
    }
    lines = [
        "[shift]",
        f'start_station = "{dispatch["shift"]["start_station"]}"',
        f'goal_station = "{goal}"',
        f'train = "{dispatch["shift"]["train"]}"',
        "",
        "[hints]",
    ]
    for station, hint in sorted(hints.items()):
        lines.append(f'{station} = "{hint}"')
    lines.extend(["", "[scoring]", "min_moves = 2", "", "[validation]", 'sw1 = "south"', 'sw2 = "north"', 'sw3 = "north"'])
    (CARTRIDGE / "dispatch.toml").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"repair_cartridge: wrote {len(locks)} locks, goal={goal}")


if __name__ == "__main__":
    main()
