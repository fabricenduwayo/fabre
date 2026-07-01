#!/usr/bin/env python3
"""Drive a winning Signalbox shift and write the transcript."""

from __future__ import annotations

import json
import tomllib
import urllib.error
import urllib.request
from pathlib import Path

API = "http://127.0.0.1:5000"
OUTPUT = Path("/app/output/transcript.json")
DISPATCH = Path("/app/cartridge/dispatch.toml")


def call(method: str, path: str, payload: dict | None = None) -> dict:
    data = None
    headers = {}
    if payload is not None:
        data = json.dumps(payload).encode()
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(API + path, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as exc:
        body = exc.read().decode()
        raise RuntimeError(f"{method} {path} -> {exc.code}: {body}") from exc


def load_plan() -> tuple[str, dict[str, str]]:
    dispatch = tomllib.loads(DISPATCH.read_text(encoding="utf-8"))
    goal = dispatch["shift"]["goal_station"]
    switches = dict(dispatch.get("validation", {}))
    return goal, switches


def main() -> None:
    goal, switches = load_plan()
    call("POST", "/v1/reset")
    call("POST", "/v1/session/start")
    for switch_id, position in sorted(switches.items()):
        call("POST", f"/v1/switch/{switch_id}", {"position": position})
    call("POST", "/v1/dispatch", {"to": goal})
    transcript = call("GET", "/v1/transcript")
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(transcript, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
