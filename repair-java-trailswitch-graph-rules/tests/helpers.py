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


def set_relay_state(relay_id: str, state: str) -> None:
    """Set a relay latch state in PostgreSQL."""
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
            f"WHERE relay_id = '{relay_id}';",
        ],
        check=True,
    )


def reset_relays() -> None:
    """Restore seeded relay latch defaults."""
    set_relay_state("yard_release", "held")
    set_relay_state("spur_seal", "sealed")


def plan(from_station: str, to_station: str, switches: dict[str, str]) -> dict:
    """Call POST /v1/plan and return the JSON body."""
    resp = requests.post(
        f"{API}/v1/plan",
        json={"from": from_station, "to": to_station, "switches": switches},
        timeout=5,
    )
    resp.raise_for_status()
    return resp.json()


def run_sql(sql: str) -> None:
    """Execute verifier-owned SQL against the live TrailSwitch database."""
    subprocess.run(
        ["runuser", "-u", "postgres", "--", "psql", "-d", "trailswitch", "-c", sql],
        check=True,
    )


def add_probe_edge_f_to_j() -> None:
    """Insert a verifier-owned F-to-J probe edge and clearance rule."""
    run_sql(
        "INSERT INTO edges (edge_id, from_station, to_station, requires_sw1, requires_sw2) "
        "VALUES ('e_f_j_probe', 'F', 'J', 'south', 'north') "
        "ON CONFLICT (edge_id) DO NOTHING;"
    )
    run_sql(
        "INSERT INTO route_rules ("
        "rule_id, edge_id, rule_priority, lock_sw1, lock_sw2, rule_action, "
        "match_relay_id, match_relay_state, count_relay_id, "
        "min_transition_count, max_transition_count, requires_visited_station, "
        "requires_completed_sequence"
        ") VALUES ("
        "'r_fj_probe_clear', 'e_f_j_probe', 2, 'south', 'north', 'clear', "
        "NULL, NULL, NULL, NULL, NULL, NULL, 'approach_release'"
        ") ON CONFLICT (rule_id) DO NOTHING;"
    )


def remove_probe_edge_f_to_j() -> None:
    """Remove the verifier-owned F-to-J probe fixtures."""
    run_sql("DELETE FROM route_rules WHERE rule_id = 'r_fj_probe_clear';")
    run_sql("DELETE FROM edges WHERE edge_id = 'e_f_j_probe';")


def tighten_checkpoint_freshness_window() -> None:
    """Tighten arrival_return freshness so a stale grant cannot clear the checkpoint."""
    run_sql(
        "UPDATE route_rule_sequence_requirements "
        "SET max_transitions_since = 0 "
        "WHERE rule_id = 'r_cj_recirc_clear' AND sequence_id = 'arrival_return';"
    )


def restore_checkpoint_freshness_window() -> None:
    """Restore the seeded arrival_return freshness window."""
    run_sql(
        "UPDATE route_rule_sequence_requirements "
        "SET max_transitions_since = 1 "
        "WHERE rule_id = 'r_cj_recirc_clear' AND sequence_id = 'arrival_return';"
    )

