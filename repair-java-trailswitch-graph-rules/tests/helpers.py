"""Verifier helpers for the TrailSwitch graph puzzle repair task."""

from __future__ import annotations

import subprocess
import time
from pathlib import Path

import requests

API = "http://127.0.0.1:8080"
REPO_JAVA = Path(
    "/app/trailswitch/src/main/java/com/trailswitch/repo/GraphPathRepository.java"
)


def ensure_service() -> None:
    """Start PostgreSQL and TrailSwitch if the verifier runs before the agent."""
    subprocess.run(["bash", "/app/sql/init_db.sh"], check=True)
    try:
        resp = requests.get(f"{API}/health", timeout=2)
        if resp.json().get("status") == "ok":
            return
    except Exception:
        pass
    subprocess.run(["bash", "/app/trailswitch/start.sh"], check=True)
    deadline = time.time() + 30.0
    while time.time() < deadline:
        try:
            resp = requests.get(f"{API}/health", timeout=2)
            if resp.json().get("status") == "ok":
                return
        except Exception:
            pass
        time.sleep(0.25)
    raise RuntimeError("TrailSwitch service did not become ready")


def set_relay_state(state: str) -> None:
    """Set the yard_release relay latch in PostgreSQL."""
    subprocess.run(
        [
            "runuser",
            "-u",
            "postgres",
            "--",
            "psql",
            "-d",
            "trailswitch",
            "-c",
            f"UPDATE relay_latches SET relay_state = '{state}' "
            "WHERE relay_id = 'yard_release';",
        ],
        check=True,
    )


def plan(from_station: str, to_station: str, switches: dict[str, str]) -> dict:
    """Call POST /v1/plan and return the JSON body."""
    resp = requests.post(
        f"{API}/v1/plan",
        json={"from": from_station, "to": to_station, "switches": switches},
        timeout=5,
    )
    resp.raise_for_status()
    return resp.json()
