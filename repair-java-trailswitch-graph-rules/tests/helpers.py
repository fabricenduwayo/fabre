"""Verifier helpers for the TrailSwitch graph puzzle repair task."""

from __future__ import annotations

import subprocess
import time

import requests

API = "http://127.0.0.1:8080"


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


def add_quoted_station_probe() -> None:
    """Insert a live graph edge whose station id contains an apostrophe."""
    run_sql(
        "INSERT INTO stations (station_id, label) VALUES ('Q''1', 'Quoted Probe') "
        "ON CONFLICT (station_id) DO NOTHING;"
    )
    run_sql(
        "INSERT INTO edges (edge_id, from_station, to_station, requires_sw1, requires_sw2) "
        "VALUES ('e_quote_probe', 'Q''1', 'A', NULL, NULL) "
        "ON CONFLICT (edge_id) DO NOTHING;"
    )


def remove_quoted_station_probe() -> None:
    """Remove the quoted-station live graph probe."""
    run_sql("DELETE FROM edges WHERE edge_id = 'e_quote_probe';")
    run_sql("DELETE FROM stations WHERE station_id = 'Q''1';")


def disable_release_transition_progress_guard() -> None:
    """Make the yard release transition accept zero shortcut progress."""
    run_sql(
        "UPDATE edge_relay_transitions "
        "SET requires_sequence_id = 'approach_release', requires_sequence_progress = 0 "
        "WHERE edge_id = 'e_f_c' AND relay_id = 'yard_release';"
    )


def restore_release_transition_progress_guard() -> None:
    """Restore the seeded approach-progress guard on yard release."""
    run_sql(
        "UPDATE edge_relay_transitions "
        "SET requires_sequence_id = 'approach_release', requires_sequence_progress = 1 "
        "WHERE edge_id = 'e_f_c' AND relay_id = 'yard_release';"
    )


def disable_spur_transition_grant_guard() -> None:
    """Make the C-to-F spur transition ignore the arrival grant."""
    run_sql(
        "UPDATE edge_relay_transitions "
        "SET requires_sequence_id = NULL, requires_sequence_progress = NULL "
        "WHERE edge_id = 'e_c_f' AND relay_id = 'spur_seal';"
    )


def restore_spur_transition_grant_guard() -> None:
    """Restore the arrival-grant guard on the C-to-F spur transition."""
    run_sql(
        "UPDATE edge_relay_transitions "
        "SET requires_sequence_id = 'arrival_return', requires_sequence_progress = NULL "
        "WHERE edge_id = 'e_c_f' AND relay_id = 'spur_seal';"
    )


def remove_yard_reset_transition() -> None:
    """Remove the E-to-C yard reset transition from the live graph."""
    run_sql(
        "DELETE FROM edge_relay_transitions "
        "WHERE edge_id = 'e_e_c' AND relay_id = 'yard_release';"
    )


def restore_yard_reset_transition() -> None:
    """Restore the seeded E-to-C yard reset transition."""
    run_sql(
        "INSERT INTO edge_relay_transitions ("
        "edge_id, transition_order, relay_id, from_state, to_state, "
        "requires_relay_id, requires_relay_state, "
        "requires_sequence_id, requires_sequence_progress"
        ") VALUES ("
        "'e_e_c', 1, 'yard_release', 'released', 'held', "
        "NULL, NULL, NULL, NULL"
        ") ON CONFLICT (edge_id, transition_order, relay_id) DO NOTHING;"
    )


def tighten_departure_transition_window() -> None:
    """Require zero yard transitions for the visit-based departure clearance."""
    run_sql(
        "UPDATE route_rules SET min_transition_count = 0, max_transition_count = 0 "
        "WHERE rule_id = 'r_de_visit_clear';"
    )


def restore_departure_transition_window() -> None:
    """Restore the seeded one-transition departure clearance window."""
    run_sql(
        "UPDATE route_rules SET min_transition_count = 1, max_transition_count = 1 "
        "WHERE rule_id = 'r_de_visit_clear';"
    )


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

