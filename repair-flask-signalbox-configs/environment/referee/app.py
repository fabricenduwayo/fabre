"""Signalbox Flask referee API."""

from __future__ import annotations

import json
import sqlite3
import tomllib
from pathlib import Path

import yaml
from flask import Flask, jsonify, request

APP = Flask(__name__)

CARTRIDGE_DIR = Path("/app/cartridge")
DISPATCH_DB = Path("/app/data/dispatch.duckdb")

SESSION: dict | None = None
SWITCHES: dict[str, str] = {}


def load_network() -> dict:
    with (CARTRIDGE_DIR / "network.yaml").open(encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def load_dispatch() -> dict:
    with (CARTRIDGE_DIR / "dispatch.toml").open("rb") as fh:
        return tomllib.load(fh)


def dispatch_db() -> sqlite3.Connection:
    DISPATCH_DB.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DISPATCH_DB)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS dispatch_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            train TEXT,
            from_station TEXT,
            to_station TEXT,
            switch_state TEXT,
            outcome TEXT
        )
        """
    )
    return conn


def reset_runtime() -> None:
    global SESSION, SWITCHES
    SESSION = None
    SWITCHES = {}
    if DISPATCH_DB.exists():
        DISPATCH_DB.unlink()


def track_locked(network: dict, track_id: str) -> bool:
    for lock in network.get("route_locks", []):
        if lock.get("track") != track_id:
            continue
        when = lock.get("when", {})
        if all(SWITCHES.get(sw) == pos for sw, pos in when.items()):
            return True
    return False


def active_edge(network: dict, track: dict) -> bool:
    when = track.get("when")
    if not when:
        return True
    return all(SWITCHES.get(sw) == pos for sw, pos in when.items())


def neighbors(network: dict, station: str) -> list[str]:
    outs: list[str] = []
    for track in network["tracks"]:
        if track_locked(network, track["id"]):
            continue
        if not active_edge(network, track):
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
                if track_locked(network, track2["id"]):
                    continue
                if not active_edge(network, track2):
                    continue
                if track2["from"] == node:
                    resolved.append(track2["to"])
                elif track2["to"] == node:
                    resolved.append(track2["from"])
        else:
            resolved.append(node)
    return [n for n in resolved if not n.startswith("sw")]


def find_path(network: dict, start: str, goal: str) -> list[str] | None:
    queue = [(start, [start])]
    seen = {start}
    while queue:
        node, path = queue.pop(0)
        if node == goal:
            return path
        for nxt in neighbors(network, node):
            if nxt in seen:
                continue
            seen.add(nxt)
            queue.append((nxt, path + [nxt]))
    return None


def validate_cartridge() -> list[str]:
    errors: list[str] = []
    network = load_network()
    dispatch = load_dispatch()
    goal = dispatch["shift"]["goal_station"]
    start = dispatch["shift"]["start_station"]
    validation = dispatch.get("validation", {})
    SWITCHES.clear()
    for sw, cfg in network["switches"].items():
        SWITCHES[sw] = validation.get(sw, cfg["default"])
    if find_path(network, start, goal) is None:
        errors.append(f"no path from {start} to {goal} with validation switches")
    SWITCHES.clear()
    return errors


@APP.get("/health")
def health():
    return jsonify({"status": "ok", "service": "signalbox-referee"})


@APP.post("/v1/reset")
def reset():
    reset_runtime()
    return jsonify({"status": "reset"})


@APP.post("/v1/session/start")
def start_session():
    global SESSION
    errors = validate_cartridge()
    if errors:
        return jsonify({"error": "invalid_cartridge", "details": errors}), 422
    network = load_network()
    dispatch = load_dispatch()
    SESSION = {
        "train": dispatch["shift"]["train"],
        "position": dispatch["shift"]["start_station"],
        "goal": dispatch["shift"]["goal_station"],
        "moves": 0,
        "history": [dispatch["shift"]["start_station"]],
    }
    SWITCHES.clear()
    for sw, cfg in network["switches"].items():
        SWITCHES[sw] = cfg["default"]
    return jsonify({"session": SESSION, "switches": SWITCHES})


@APP.get("/v1/network")
def network_view():
    return jsonify({"network": load_network(), "switches": SWITCHES})


@APP.post("/v1/switch/<switch_id>")
def set_switch(switch_id: str):
    if SESSION is None:
        return jsonify({"error": "no_session"}), 400
    network = load_network()
    if switch_id not in network["switches"]:
        return jsonify({"error": "unknown_switch"}), 404
    body = request.get_json(silent=True) or {}
    position = body.get("position")
    if position not in network["switches"][switch_id]["positions"]:
        return jsonify({"error": "invalid_position"}), 422
    SWITCHES[switch_id] = position
    return jsonify({"switches": SWITCHES})


@APP.post("/v1/dispatch")
def dispatch_train():
    if SESSION is None:
        return jsonify({"error": "no_session"}), 400
    network = load_network()
    dispatch = load_dispatch()
    body = request.get_json(silent=True) or {}
    target = body.get("to") or dispatch["shift"]["goal_station"]
    train = body.get("train") or SESSION["train"]
    start = SESSION["position"]
    path = find_path(network, start, target)
    outcome = "ok" if path else "blocked"
    conn = dispatch_db()
    conn.execute(
        "INSERT INTO dispatch_log (train, from_station, to_station, switch_state, outcome) "
        "VALUES (?, ?, ?, ?, ?)",
        [train, start, target, json.dumps(SWITCHES), outcome],
    )
    conn.commit()
    conn.close()
    if not path:
        return jsonify({"error": "blocked", "switches": SWITCHES}), 409
    SESSION["position"] = target
    SESSION["moves"] += 1
    SESSION["history"].extend(path[1:])
    won = target == SESSION["goal"]
    return jsonify(
        {
            "train": train,
            "path": path,
            "position": SESSION["position"],
            "moves": SESSION["moves"],
            "won": won,
            "switches": SWITCHES,
        }
    )


@APP.get("/v1/transcript")
def transcript():
    if SESSION is None:
        return jsonify({"error": "no_session"}), 400
    dispatch = load_dispatch()
    payload = {
        "train": SESSION["train"],
        "start": dispatch["shift"]["start_station"],
        "goal": dispatch["shift"]["goal_station"],
        "history": SESSION["history"],
        "moves": SESSION["moves"],
        "won": SESSION["position"] == SESSION["goal"],
        "switches": SWITCHES,
    }
    return jsonify(payload)


if __name__ == "__main__":
    reset_runtime()
    APP.run(host="127.0.0.1", port=5000, threaded=True)
