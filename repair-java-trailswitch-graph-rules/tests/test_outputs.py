"""Behavioral verifier for TrailSwitch referee contract compliance."""

import time

import pytest

from helpers import REPO_JAVA, ensure_service, plan, set_relay_state


@pytest.fixture(scope="module", autouse=True)
def service_ready():
    """Ensure TrailSwitch is running before policy checks."""
    ensure_service()


@pytest.fixture(autouse=True)
def reset_yard_release():
    """Reset the approach-release relay before and after each test."""
    set_relay_state("held")
    yield
    set_relay_state("held")


def test_health_endpoint():
    """TrailSwitch must expose GET /health with status ok."""
    import requests

    payload = requests.get("http://127.0.0.1:8080/health", timeout=3).json()
    assert payload.get("status") == "ok"


def test_plan_reaches_arrival_terminal():
    """Under south/south switches the depot can reach arrival via the junction."""
    result = plan("A", "E", {"sw1": "south", "sw2": "south"})
    assert result["reachable"] is True
    assert result["path"] == ["A", "C", "E"]
    assert result["cycle_guard"] is True


def test_held_relay_requires_release_cycle():
    """A held approach relay requires returning to C in a new relay state."""
    result = plan("C", "B", {"sw1": "south", "sw2": "north"})
    assert result["reachable"] is True
    assert result["path"] == ["C", "F", "C", "B"]


def test_release_cycle_opens_relayed_yard_route():
    """Crossing the release circuit opens the full relayed yard route."""
    result = plan("A", "E", {"sw1": "south", "sw2": "north"})
    assert result["reachable"] is True
    assert result["path"] == ["A", "C", "F", "C", "B", "D", "E"]
    assert result["cycle_guard"] is True


def test_database_relay_snapshot_changes_authorization():
    """A released database snapshot permits the yard route without the circuit."""
    set_relay_state("released")
    result = plan("A", "E", {"sw1": "south", "sw2": "north"})
    assert result["reachable"] is True
    assert result["path"] == ["A", "C", "B", "D", "E"]


def test_route_lock_blocks_staging_spur():
    """North/north switches cannot reach arrival when staging locks apply."""
    result = plan("A", "E", {"sw1": "north", "sw2": "north"})
    assert result["reachable"] is False
    assert result["path"] == []


def test_platform_lock_blocks_staging_when_sw2_north():
    """North/north cannot reach staging when a wildcard platform lock matches sw2."""
    result = plan("A", "D", {"sw1": "north", "sw2": "north"})
    assert result["reachable"] is False
    assert result["path"] == []


def test_clearance_beats_later_platform_lock():
    """South/north can reach staging when clearance opens the spur."""
    result = plan("A", "D", {"sw1": "south", "sw2": "north"})
    assert result["reachable"] is True
    assert result["path"] == ["A", "C", "F", "C", "B", "D"]


def test_lock_group_relay_blocks_arrival_leg():
    """North/north cannot depart staging toward arrival when relay locks apply."""
    result = plan("D", "E", {"sw1": "north", "sw2": "north"})
    assert result["reachable"] is False
    assert result["path"] == []


def test_initial_closure_blocks_inside_yard():
    """Starting inside the yard cannot bypass the held relay closure."""
    result = plan("D", "E", {"sw1": "south", "sw2": "north"})
    assert result["reachable"] is False
    assert result["path"] == []


def test_lock_group_relay_clears_when_spur_opens():
    """South/north can depart staging toward arrival when relayed locks clear."""
    set_relay_state("released")
    result = plan("D", "E", {"sw1": "south", "sw2": "north"})
    assert result["reachable"] is True
    assert result["path"] == ["D", "E"]


def test_spur_hold_relay_blocks_staging_departure():
    """South/south cannot depart staging toward arrival under the spur hold lineup."""
    result = plan("D", "E", {"sw1": "south", "sw2": "south"})
    assert result["reachable"] is False
    assert result["path"] == []


def test_scenic_spur_relay_open_after_clearance():
    """South/north can run B to E through staging after relayed locks clear."""
    set_relay_state("released")
    result = plan("B", "E", {"sw1": "south", "sw2": "north"})
    assert result["reachable"] is True
    assert result["path"] == ["B", "D", "E"]


def test_overlapping_lock_groups_relay_to_recirc():
    """Shared group edges must relay to a fixed point before path planning."""
    blocked = plan("E", "C", {"sw1": "south", "sw2": "south"})
    assert blocked["reachable"] is False
    assert blocked["path"] == []
    set_relay_state("released")
    open_line = plan("E", "C", {"sw1": "south", "sw2": "north"})
    assert open_line["reachable"] is True
    assert open_line["path"] == ["E", "C"]


def test_lock_positions_require_conjunction():
    """A route lock listing two switch positions requires both to match."""
    open_line = plan("A", "B", {"sw1": "north", "sw2": "north"})
    assert open_line["reachable"] is True
    assert open_line["path"] == ["A", "B"]
    blocked = plan("A", "B", {"sw1": "north", "sw2": "south"})
    assert blocked["reachable"] is False
    assert blocked["path"] == []


def test_cycle_guard_finishes_quickly():
    """Planning on the cyclic seed graph must finish without exhaustive re-enqueue loops."""
    start = time.time()
    result = plan("C", "E", {"sw1": "south", "sw2": "south"})
    elapsed = time.time() - start
    assert result["cycle_guard"] is True
    assert elapsed < 2.0


def test_sql_lookups_are_parameterized():
    """GraphPathRepository must not concatenate station ids into SQL strings."""
    source = REPO_JAVA.read_text(encoding="utf-8")
    assert "from_station = '" not in source
    assert "?" in source or "from_station = ?" in source
