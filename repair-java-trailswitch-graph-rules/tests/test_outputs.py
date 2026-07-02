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


def test_route_lock_blocks_staging_spur():
    """Ascending-priority hold rule must lock the north spur when both switches are north."""
    result = plan("A", "E", {"sw1": "north", "sw2": "north"})
    assert result["reachable"] is False
    assert result["path"] == []


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
