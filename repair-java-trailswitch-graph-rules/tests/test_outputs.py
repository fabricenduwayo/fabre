"""Behavioral verifier for TrailSwitch referee contract compliance."""

import time

import pytest

from helpers import REPO_JAVA, ensure_service, plan


@pytest.fixture(scope="module", autouse=True)
def service_ready():
    """Ensure TrailSwitch is running before policy checks."""
    ensure_service()


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


def test_clearance_rule_opens_scenic_spur():
    """A matching clear rule must unlock the spur before the direct junction leg is gated."""
    result = plan("A", "E", {"sw1": "south", "sw2": "north"})
    assert result["reachable"] is True
    assert result["path"] == ["A", "C", "B", "D", "E"]
    assert result["cycle_guard"] is True


def test_route_lock_blocks_staging_spur():
    """A non-matching early rule must not stop a later wildcard lock from blocking north/north."""
    result = plan("A", "E", {"sw1": "north", "sw2": "north"})
    assert result["reachable"] is False
    assert result["path"] == []


def test_platform_lock_blocks_staging_when_sw2_north():
    """A NULL lock_sw1 rule must still lock when the listed sw2 position matches."""
    result = plan("A", "D", {"sw1": "north", "sw2": "north"})
    assert result["reachable"] is False
    assert result["path"] == []


def test_clearance_beats_later_platform_lock():
    """A matching clear rule at lower priority must open the spur before the platform lock."""
    result = plan("A", "D", {"sw1": "south", "sw2": "north"})
    assert result["reachable"] is True
    assert result["path"] == ["A", "C", "B", "D"]


def test_lock_group_relay_blocks_arrival_leg():
    """A locked spur edge must relay the lock to its paired arrival leg in the yard group."""
    result = plan("D", "E", {"sw1": "north", "sw2": "north"})
    assert result["reachable"] is False
    assert result["path"] == []


def test_lock_group_relay_clears_when_spur_opens():
    """Clearance on the spur must keep the relayed arrival leg open for staging departures."""
    result = plan("D", "E", {"sw1": "south", "sw2": "north"})
    assert result["reachable"] is True
    assert result["path"] == ["D", "E"]


def test_spur_hold_relay_blocks_staging_departure():
    """A spur hold lock must relay to block staging departures even when switches match the hold."""
    result = plan("D", "E", {"sw1": "south", "sw2": "south"})
    assert result["reachable"] is False
    assert result["path"] == []


def test_scenic_spur_relay_open_after_clearance():
    """Clearance on the yard spur must relay-open the paired arrival leg for B to E runs."""
    result = plan("B", "E", {"sw1": "south", "sw2": "north"})
    assert result["reachable"] is True
    assert result["path"] == ["B", "D", "E"]


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


def test_lock_positions_require_conjunction():
    """A two-position lock must not fire when only one switch matches."""
    result = plan("A", "E", {"sw1": "south", "sw2": "south"})
    assert result["reachable"] is True
    assert result["path"] == ["A", "C", "E"]
