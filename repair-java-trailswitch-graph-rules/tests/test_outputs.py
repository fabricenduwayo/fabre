"""Behavioral verifier for TrailSwitch referee contract compliance."""

import pytest

from helpers import (
    REPO_JAVA,
    add_probe_edge_f_to_j,
    ensure_service,
    plan,
    remove_probe_edge_f_to_j,
    reset_relays,
    restore_checkpoint_freshness_window,
    run_sql,
    set_relay_state,
    tighten_checkpoint_freshness_window,
)


@pytest.fixture(scope="module", autouse=True)
def service_ready():
    """Ensure TrailSwitch is running before policy checks."""
    ensure_service()


@pytest.fixture(autouse=True)
def reset_relay_latches():
    """Reset relay latches before and after each test."""
    reset_relays()
    yield
    reset_relays()


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
    set_relay_state("yard_release", "released")
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


def test_premature_yard_exit_blocked_without_circuit():
    """Released latch alone cannot open staging departure without a qualifying visit."""
    set_relay_state("yard_release", "released")
    result = plan("D", "E", {"sw1": "south", "sw2": "north"})
    assert result["reachable"] is False
    assert result["path"] == []


def test_lock_group_relay_clears_when_spur_opens():
    """South/north can depart staging toward arrival after a qualifying yard visit."""
    set_relay_state("yard_release", "released")
    result = plan("B", "E", {"sw1": "south", "sw2": "north"})
    assert result["reachable"] is True
    assert result["path"] == ["B", "D", "E"]


def test_yard_spur_requires_release_circuit_from_north_yard():
    """North yard cannot reach arrival without the scenic circuit while the yard relay is held."""
    result = plan("B", "E", {"sw1": "south", "sw2": "north"})
    assert result["reachable"] is False
    assert result["path"] == []


def test_spur_hold_relay_blocks_staging_departure():
    """South/south cannot depart staging toward arrival under the spur hold lineup."""
    result = plan("D", "E", {"sw1": "south", "sw2": "south"})
    assert result["reachable"] is False
    assert result["path"] == []


def test_scenic_spur_relay_open_after_clearance():
    """South/north can run B to E through staging after relayed locks clear."""
    set_relay_state("yard_release", "released")
    result = plan("B", "E", {"sw1": "south", "sw2": "north"})
    assert result["reachable"] is True
    assert result["path"] == ["B", "D", "E"]


def test_overlapping_lock_groups_relay_to_recirc():
    """Shared group edges must relay to a fixed point before path planning."""
    blocked = plan("E", "C", {"sw1": "south", "sw2": "south"})
    assert blocked["reachable"] is False
    assert blocked["path"] == []
    set_relay_state("yard_release", "released")
    open_line = plan("E", "C", {"sw1": "south", "sw2": "north"})
    assert open_line["reachable"] is True
    assert open_line["path"] == ["E", "C"]


def test_armed_recirc_group_inactive_when_relay_released():
    """Recirc lock groups disarm once the yard release relay is posted."""
    set_relay_state("yard_release", "released")
    result = plan("E", "C", {"sw1": "south", "sw2": "south"})
    assert result["reachable"] is True
    assert result["path"] == ["E", "C"]


def test_conditional_spur_transition_requires_posted_release():
    """The spur seal opens only after the yard release relay is posted on entry."""
    result = plan("A", "D", {"sw1": "south", "sw2": "north"})
    assert result["reachable"] is True
    assert result["path"] == ["A", "C", "F", "C", "B", "D"]


def test_ordered_release_sequence_rejects_shortcut_history():
    """An out-of-order F-to-C visit must not satisfy the C-F-C release circuit."""
    result = plan("G", "E", {"sw1": "south", "sw2": "north"})
    assert result["reachable"] is True
    assert result["path"] == ["G", "F", "C", "F", "C", "B", "D", "E"]
    assert result["cycle_guard"] is True


def test_equal_length_routes_use_first_differing_edge_id():
    """Equal-length authorized paths choose the lower first edge id."""
    set_relay_state("yard_release", "released")
    result = plan("H", "B", {"sw1": "north", "sw2": "north"})
    assert result["reachable"] is True
    assert result["path"] == ["H", "A", "B"]
    assert result["cycle_guard"] is True


def test_sequence_grant_voids_when_yard_returns_to_initial():
    """Recirculation through arrival must re-earn release-sequence clearance."""
    result = plan("A", "J", {"sw1": "south", "sw2": "north"})
    assert result["reachable"] is True
    assert result["path"] == ["A", "C", "F", "C", "B", "D", "E", "C", "F", "C", "J"]
    assert result["cycle_guard"] is True


def test_transition_count_window_blocks_stale_yard_release():
    """Departure clearance requires exactly one yard transition after re-approach."""
    result = plan("A", "J", {"sw1": "south", "sw2": "north"})
    assert result["reachable"] is True
    assert result["path"].count("D") == 1
    assert result["path"].count("E") == 1


def test_lock_positions_require_conjunction():
    """A route lock listing two switch positions requires both to match."""
    open_line = plan("A", "B", {"sw1": "north", "sw2": "north"})
    assert open_line["reachable"] is True
    assert open_line["path"] == ["A", "B"]
    blocked = plan("A", "B", {"sw1": "north", "sw2": "south"})
    assert blocked["reachable"] is False
    assert blocked["path"] == []


def test_cycle_guard_terminates_cyclic_search():
    """Planning on the cyclic seed graph must finish through state deduplication."""
    result = plan("C", "E", {"sw1": "south", "sw2": "south"})
    assert result["cycle_guard"] is True


def test_sql_lookups_are_parameterized():
    """GraphPathRepository must not concatenate station ids into SQL strings."""
    source = REPO_JAVA.read_text(encoding="utf-8")
    assert "from_station = '" not in source
    assert "?" in source or "from_station = ?" in source


def test_checkpoint_requires_dual_sequence_grants():
    """Recirc checkpoint clearance needs re-earned approach and fresh arrival grants."""
    result = plan("A", "J", {"sw1": "south", "sw2": "north"})
    assert result["reachable"] is True
    assert result["path"] == [
        "A",
        "C",
        "F",
        "C",
        "B",
        "D",
        "E",
        "C",
        "F",
        "C",
        "J",
    ]


def test_arrival_grant_survives_same_traversal_reset_epoch():
    """A grant issued after a relay reset epoch advance on the same edge stays valid."""
    result = plan("A", "J", {"sw1": "south", "sw2": "north"})
    assert result["reachable"] is True
    assert result["path"] == [
        "A",
        "C",
        "F",
        "C",
        "B",
        "D",
        "E",
        "C",
        "F",
        "C",
        "J",
    ]


def test_restarting_first_step_preserves_existing_grant():
    """Crossing the first release step again must not discard an existing grant."""
    add_probe_edge_f_to_j()
    try:
        earned = plan("C", "B", {"sw1": "south", "sw2": "north"})
        assert earned["path"] == ["C", "F", "C", "B"]
        restarted = plan("C", "F", {"sw1": "south", "sw2": "north"})
        assert restarted["reachable"] is True
        assert restarted["path"] == ["C", "F"]
        shortcut = plan("F", "J", {"sw1": "south", "sw2": "north"})
        assert shortcut["reachable"] is True
        assert shortcut["path"] == ["F", "J"]
    finally:
        remove_probe_edge_f_to_j()


def test_live_freshness_window_blocks_stale_arrival_grant():
    """Tightening a sequence freshness window in PostgreSQL must change authorization."""
    tighten_checkpoint_freshness_window()
    try:
        blocked = plan("A", "J", {"sw1": "south", "sw2": "north"})
        assert blocked["reachable"] is False
        assert blocked["path"] == []
    finally:
        restore_checkpoint_freshness_window()


def test_dual_sequence_requirement_blocks_without_arrival_grant():
    """Checkpoint clearance fails when only the approach grant is present after recirc."""
    run_sql("DELETE FROM release_sequences WHERE sequence_id = 'arrival_return';")
    try:
        blocked = plan("A", "J", {"sw1": "south", "sw2": "north"})
        assert blocked["reachable"] is False
        assert blocked["path"] == []
    finally:
        run_sql(
            "INSERT INTO release_sequences (sequence_id, step_order, edge_id) VALUES "
            "('arrival_return', 1, 'e_b_d'), "
            "('arrival_return', 2, 'e_d_e'), "
            "('arrival_return', 3, 'e_e_c');"
        )
