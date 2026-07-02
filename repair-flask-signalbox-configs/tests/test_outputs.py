"""Behavioral verifier for the repaired Signalbox cartridge and shift transcript.

Expected locks, operative goal, and switch lineup are recomputed from
/app/data/evidence.duckdb — there is no labeled operative answer row.
"""

import json
import random

import pytest

from helpers import (
    CARTRIDGE,
    DISPATCH_DB,
    OUTPUT,
    attempt_dispatch,
    compute_voided_seqs,
    decoy_arrivals,
    dispatch_success_count,
    effective_locks,
    effective_lock_state,
    effective_requires,
    hint_map,
    history_is_legal,
    load_network,
    lock_corrections,
    lock_log_rows,
    lock_map,
    normalized_locks,
    operative_profile,
    reset_referee,
    run_shift,
    switch_plans,
)

RANDOM_CASES = 60
RANDOM_SEED = 91237


@pytest.fixture(autouse=True)
def clean_referee():
    """Reset referee runtime state between tests."""
    reset_referee()
    yield
    reset_referee()


def test_cartridge_allows_session_start_and_wins():
    """Repaired cartridge must validate, dispatch, and end with won=True."""
    proc = run_shift()
    assert proc.returncode == 0, proc.stderr
    payload = json.loads(OUTPUT.read_text(encoding="utf-8"))
    assert payload["won"] is True


def test_transcript_reaches_operative_goal():
    """Transcript must end at the arrival uniquely reachable under resolved locks."""
    goal, _switches = operative_profile()
    proc = run_shift()
    assert proc.returncode == 0, proc.stderr
    payload = json.loads(OUTPUT.read_text(encoding="utf-8"))
    assert payload["goal"] == goal
    assert payload["history"][-1] == goal


def test_transcript_history_is_legal_under_reported_switches():
    """Visited stations must follow active unlocked edges under the transcript switches."""
    proc = run_shift()
    assert proc.returncode == 0, proc.stderr
    network = load_network()
    locks = lock_map()
    payload = json.loads(OUTPUT.read_text(encoding="utf-8"))
    assert history_is_legal(network, payload["history"], payload["switches"], locks)


def test_route_locks_match_resolved_bulletin_log():
    """network.yaml locks must equal the bulletin-resolved effective lock set."""
    proc = run_shift()
    assert proc.returncode == 0, proc.stderr
    network = load_network()
    assert normalized_locks(network.get("route_locks", [])) == normalized_locks(
        effective_locks(network)
    )


def test_route_locks_use_referee_schema():
    """Every route lock must be a {track, when:dict} object, not a station pair."""
    proc = run_shift()
    assert proc.returncode == 0, proc.stderr
    locks = load_network().get("route_locks", [])
    assert locks, "route_locks must not be empty"
    for lock in locks:
        assert isinstance(lock, dict)
        assert isinstance(lock.get("track"), str)
        assert isinstance(lock.get("when"), dict) and lock["when"]


def test_revoked_bulletin_does_not_keep_g_seal():
    """BUL-A g-seal must stay void after BUL-B revoke — keeping it blocks the operative path."""
    proc = run_shift()
    assert proc.returncode == 0, proc.stderr
    tracks = {lock.get("track") for lock in load_network().get("route_locks", [])}
    assert "t_sw3_g" not in tracks


def test_stamp_revoke_clears_g_seal():
    """Stamp revoke must void BUL-J g-seal rows so G stays reachable under resolved locks."""
    proc = run_shift()
    assert proc.returncode == 0, proc.stderr
    tracks = {lock.get("track") for lock in load_network().get("route_locks", [])}
    assert "t_sw3_g" not in tracks
    goal, _switches = operative_profile()
    assert goal == "G"


def test_hold_release_restores_f_lock():
    """Hold/release with hold_id BUL-D must restore t_sw3_f before amend churn continues."""
    proc = run_shift()
    assert proc.returncode == 0, proc.stderr
    locks = lock_map()
    assert locks.get("t_sw3_f") == {"sw3": "north", "sw1": "south"}


def test_replace_resets_junction_not_merge():
    """BUL-O replace must reset t_sw1_c north after BUL-N south replace, not merge positions."""
    proc = run_shift()
    assert proc.returncode == 0, proc.stderr
    locks = lock_map()
    assert locks.get("t_sw1_c") == {"sw1": "north"}


def test_nested_hold_skips_replace_until_matched_release():
    """Nested holds must skip BUL-V south replace until signal-test and yard-check release."""
    proc = run_shift()
    assert proc.returncode == 0, proc.stderr
    locks = lock_map()
    assert locks.get("t_sw1_c") == {"sw1": "north"}


def test_partial_revoke_keeps_junction_lock():
    """BUL-H partial revoke must drop only BUL-C's t_sw3_f row, not the junction seal."""
    proc = run_shift()
    assert proc.returncode == 0, proc.stderr
    locks = lock_map()
    assert locks.get("t_sw1_c") == {"sw1": "north"}


def test_amend_merges_switch_conditions():
    """Amend rows must merge when maps so t_sw3_f needs both sw3 north and sw1 south."""
    proc = run_shift()
    assert proc.returncode == 0, proc.stderr
    locks = lock_map()
    assert locks.get("t_sw3_f") == {"sw3": "north", "sw1": "south"}


def test_amend_without_add_initializes_lock():
    """Amend rows must seed a track lock when no surviving add remains for that track."""
    proc = run_shift()
    assert proc.returncode == 0, proc.stderr
    locks = lock_map()
    assert locks.get("t_sw3_f") == {"sw3": "north", "sw1": "south"}


def test_requires_only_amend_attaches_dependency():
    """Requires-only amend rows must replace requires without changing the when map."""
    proc = run_shift()
    assert proc.returncode == 0, proc.stderr
    locks = effective_locks()
    d_lock = next(item for item in locks if item["track"] == "t_sw2_d")
    assert d_lock["when"] == {"sw2": "north"}
    assert lock_map(locks).get("t_sw1_c") == {"sw1": "north"}


def test_anchored_amend_voided_by_partial_revoke():
    """Amend rows anchored to a revoked bulletin must not survive partial revoke on that track."""
    proc = run_shift()
    assert proc.returncode == 0, proc.stderr
    locks = lock_map()
    assert locks.get("t_sw3_f") == {"sw3": "north", "sw1": "south"}


def test_unless_absent_drops_junction_when_d_seal_lands():
    """unless_absent must drop t_sw1_c once t_sw2_d lands until the junction is re-added."""
    proc = run_shift()
    assert proc.returncode == 0, proc.stderr
    locks = lock_map()
    assert locks.get("t_sw1_c") == {"sw1": "north"}
    assert locks.get("t_sw2_d") == {"sw2": "north"}


def test_expires_after_partial_revoke_requires_junction_readd():
    """expires_after must void surviving BUL-C junction rows when BUL-C is partially revoked."""
    proc = run_shift()
    assert proc.returncode == 0, proc.stderr
    locks = effective_locks()
    junction = next(item for item in locks if item["track"] == "t_sw1_c")
    assert junction["when"] == {"sw1": "north"}
    assert lock_map(locks).get("t_sw3_f") == {"sw3": "north", "sw1": "south"}


def test_decoy_arrivals_are_blocked_under_every_switch_lineup():
    """Each non-operative candidate must stay unreachable for all switch lineups."""
    proc = run_shift()
    assert proc.returncode == 0, proc.stderr
    network = load_network()
    for arrival in decoy_arrivals():
        for switches in switch_plans(network):
            status, body = attempt_dispatch(switches, arrival)
            assert status == 409, (
                f"decoy arrival {arrival} reachable under {switches}: {status} {body}"
            )


def test_dispatch_log_records_success():
    """Referee must record a successful dispatch in dispatch.duckdb."""
    proc = run_shift()
    assert proc.returncode == 0, proc.stderr
    assert DISPATCH_DB.exists()
    assert dispatch_success_count() >= 1


def test_dispatch_toml_goal_and_hints_match_evidence():
    """dispatch.toml goal/hints must match the derived operative goal and hint clues."""
    proc = run_shift()
    assert proc.returncode == 0, proc.stderr
    goal, _switches = operative_profile()
    dispatch_text = (CARTRIDGE / "dispatch.toml").read_text(encoding="utf-8")
    assert f'goal_station = "{goal}"' in dispatch_text
    for hint in hint_map().values():
        assert hint in dispatch_text


def test_unless_present_reapplies_after_hold_release():
    """unless_present rows must re-apply in seq order once a matching release restores them."""
    network = load_network()
    rows = lock_log_rows()
    prefix = [row for row in rows if row[0] <= 28]
    locks = lock_map(effective_locks(network, prefix))
    assert locks.get("t_sw1_c") == {"sw1": "south"}


def test_coupling_full_revoke_clears_yard_link_rows():
    """Full revoke on a coupled bulletin must void every earlier yard-link row."""
    rows = lock_log_rows()
    prefix = [row for row in rows if row[0] <= 30]
    locks = lock_map(effective_locks(rows=prefix))
    assert "t_sw2_d" not in locks


def test_decouple_add_restores_d_seal_after_coupling_revoke():
    """Decoupled yard-link add after coupling revoke must restore t_sw2_d."""
    rows = lock_log_rows()
    prefix = [row for row in rows if row[0] <= 31]
    locks = lock_map(effective_locks(rows=prefix))
    assert locks.get("t_sw2_d") == {"sw2": "north"}


def test_deferred_requires_amend_after_release():
    """defer_until rows must apply after the trigger release finishes restoring holds."""
    rows = lock_log_rows()
    prefix = [row for row in rows if row[0] <= 34]
    state = effective_lock_state(rows=prefix)
    assert state["t_sw1_c"]["requires"] == ["t_sw3_f", "t_sw2_d"]


def test_supersedes_voids_earlier_bulletin_rows():
    """supersedes must void lower-seq rows from the named bulletin before the row applies."""
    voided = compute_voided_seqs(lock_log_rows(), lock_corrections())
    assert 29 in voided
    assert 7 in voided
    assert 11 in voided
    assert 18 in voided


def test_supersedes_replace_resets_deferred_requires():
    """Final superseding replace must reset junction requires after deferred amend."""
    state = effective_lock_state()
    assert state["t_sw1_c"]["requires"] == ["t_sw3_f"]


def test_exclusive_with_clears_stale_d_seal():
    """exclusive_with on the final junction replace must drop stale t_sw2_d rows."""
    rows = lock_log_rows()
    prefix = [row for row in rows if row[0] <= 35]
    locks = lock_map(effective_locks(rows=prefix))
    assert "t_sw2_d" not in locks


def test_precondition_skips_mismatched_amend():
    """precondition must skip BUL-AK when t_sw1_c is north instead of the required south."""
    rows = lock_log_rows()
    prefix = [row for row in rows if row[0] <= 36]
    locks = lock_map(effective_locks(rows=prefix))
    assert locks.get("t_sw2_d") != {"sw2": "south"}


def test_d_seal_restored_after_exclusive_with():
    """BUL-AL must re-add t_sw2_d after exclusive_with clears the stale yard-link row."""
    proc = run_shift()
    assert proc.returncode == 0, proc.stderr
    locks = lock_map()
    assert locks.get("t_sw2_d") == {"sw2": "north"}


def test_witness_skips_unapplied_bulletin():
    """witness must skip BUL-AM south amend when BUL-AK never successfully applied."""
    rows = lock_log_rows()
    prefix = [row for row in rows if row[0] <= 38]
    locks = lock_map(effective_locks(rows=prefix))
    assert locks.get("t_sw2_d") == {"sw2": "north"}


def test_unless_matches_blocks_south_d_seal_amend():
    """unless_matches must skip BUL-AN south amend while t_sw3_f still carries sw1 south."""
    rows = lock_log_rows()
    prefix = [row for row in rows if row[0] <= 39]
    locks = lock_map(effective_locks(rows=prefix))
    assert locks.get("t_sw2_d") == {"sw2": "north"}


def test_witness_amend_refreshes_d_seal_requires():
    """BUL-AO witness amend must attach junction and f-seal dependencies on t_sw2_d."""
    state = effective_lock_state()
    assert effective_requires(state["t_sw2_d"], state) == ["t_sw3_f", "t_sw1_c"]
    assert state["t_sw2_d"]["binds_requires"] == ["t_sw1_c"]


def test_suppresses_voids_before_witness_amend():
    """suppresses on BUL-AO must void the skipped BUL-AK row before dependency refresh."""
    voided = compute_voided_seqs(lock_log_rows(), lock_corrections())
    assert 36 in voided


def test_witness_blocks_south_junction_replace():
    """witness must skip BUL-AP south replace when BUL-AK never successfully applied."""
    rows = lock_log_rows()
    prefix = [row for row in rows if row[0] <= 41]
    locks = lock_map(effective_locks(rows=prefix))
    assert locks.get("t_sw1_c") == {"sw1": "north"}


def test_unless_held_skips_cross_track_amend_during_hold():
    """unless_held must skip BUL-AR south amend while final-gate hold keeps t_sw1_c held."""
    rows = lock_log_rows()
    prefix = [row for row in rows if row[0] <= 43]
    locks = lock_map(effective_locks(rows=prefix))
    assert locks.get("t_sw2_d") != {"sw2": "south"}


def test_final_gate_release_reapplies_unless_present_south():
    """final-gate release must re-apply unless_present south replace before BUL-AT north reset."""
    rows = lock_log_rows()
    prefix = [row for row in rows if row[0] <= 44]
    locks = lock_map(effective_locks(rows=prefix))
    assert locks.get("t_sw1_c") == {"sw1": "south"}


def test_final_gate_north_reset_restores_operative_junction():
    """BUL-AT replace must reset t_sw1_c north after unless_present reapply on final-gate release."""
    proc = run_shift()
    assert proc.returncode == 0, proc.stderr
    locks = lock_map()
    assert locks.get("t_sw1_c") == {"sw1": "north"}
    assert locks.get("t_sw2_d") == {"sw2": "north"}
    state = effective_lock_state()
    assert state["t_sw1_c"]["requires"] == ["t_sw3_f"]
    assert effective_requires(state["t_sw2_d"], state) == ["t_sw3_f", "t_sw1_c"]


def test_witness_skips_bul_au_south_amend():
    """BUL-AU south amend must skip because BUL-AK never successfully applied."""
    rows = lock_log_rows()
    prefix = [row for row in rows if row[0] <= 45]
    locks = lock_map(effective_locks(rows=prefix))
    assert locks.get("t_sw2_d") != {"sw2": "south"}
    assert "t_sw2_d" not in locks


def test_binds_requires_tracks_junction_requires():
    """binds_requires must union junction requires during cascade fixpoints."""
    rows = lock_log_rows()
    prefix = [row for row in rows if row[0] <= 35]
    state = effective_lock_state(rows=prefix)
    assert "t_sw2_d" not in state
    full = effective_lock_state()
    assert full["t_sw2_d"]["binds_requires"] == ["t_sw1_c"]
    assert effective_requires(full["t_sw2_d"], full) == ["t_sw3_f", "t_sw1_c"]


def test_witness_binds_amend_preserves_when_map():
    """Witness binds_requires amend must keep the surviving d-seal when positions."""
    state = effective_lock_state()
    assert state["t_sw2_d"]["when"] == {"sw2": "north"}
    assert state["t_sw2_d"]["binds_requires"] == ["t_sw1_c"]


def test_unless_requires_changed_drops_yard_link_after_gate_release():
    """unless_requires_changed must drop t_sw2_d once unless_present reapply clears junction requires."""
    rows = lock_log_rows()
    prefix = [row for row in rows if row[0] <= 45]
    locks = lock_map(effective_locks(rows=prefix))
    assert "t_sw2_d" not in locks


def test_unless_requires_changed_recovery_readds_yard_link():
    """BUL-AV must re-add t_sw2_d after unless_requires_changed drop and final junction reset."""
    proc = run_shift()
    assert proc.returncode == 0, proc.stderr
    locks = lock_map()
    assert locks.get("t_sw2_d") == {"sw2": "north"}
    state = effective_lock_state()
    assert effective_requires(state["t_sw2_d"], state) == ["t_sw3_f", "t_sw1_c"]


def test_requires_when_drops_yard_link_without_merged_f_seal_when():
    """requires_when must gate yard link on t_sw3_f merged when positions, not presence alone."""
    rows = lock_log_rows()
    prefix = [row for row in rows if row[0] <= 48]
    locks = lock_map(effective_locks(rows=prefix))
    assert locks.get("t_sw3_f") == {"sw3": "north", "sw1": "south"}
    assert locks.get("t_sw2_d") == {"sw2": "north", "sw1": "south", "sw3": "north"}


def test_requires_when_tail_refreshes_yard_link_positions():
    """BUL-AY must keep yard link metadata keyed on merged f-seal and north junction when maps."""
    proc = run_shift()
    assert proc.returncode == 0, proc.stderr
    state = effective_lock_state()
    assert state["t_sw2_d"]["requires_when"]["t_sw3_f"] == {"sw1": "south", "sw3": "north"}
    assert state["t_sw2_d"]["requires_when"]["t_sw1_c"] == {"sw1": "north"}
    assert state["t_sw1_c"]["requires_when"]["t_sw3_f"] == {"sw1": "south"}
    assert effective_requires(state["t_sw2_d"], state) == ["t_sw3_f", "t_sw1_c"]


def test_requires_stable_drops_yard_link_on_junction_when_change():
    """requires_stable must drop t_sw2_d when t_sw1_c when-map changes without requires tuple change."""
    rows = lock_log_rows()
    prefix = [row for row in rows if row[0] <= 44]
    locks = lock_map(effective_locks(rows=prefix))
    assert "t_sw2_d" not in locks


def test_lock_corrections_override_release_hold_id():
    """lock_corrections must override BUL-W release hold_id from yard-check to signal-test."""
    corrections = lock_corrections()
    assert corrections[22][1] == '{"hold_id": "signal-test"}'
    rows = lock_log_rows()
    prefix = [row for row in rows if row[0] <= 24]
    locks = lock_map(effective_locks(rows=prefix))
    assert locks.get("t_sw1_c") == {"sw1": "north"}


def test_inherit_when_from_composes_yard_link_during_tail():
    """BUL-AV through BUL-AZ must inherit merged junction and f-seal when maps on t_sw2_d."""
    rows = lock_log_rows()
    prefix = [row for row in rows if row[0] <= 51]
    locks = lock_map(effective_locks(rows=prefix))
    assert locks.get("t_sw2_d") == {"sw2": "north", "sw1": "south", "sw3": "north"}


def test_inherit_when_from_recomputes_before_final_replace():
    """inherit_when_from must keep t_sw2_d composed through BUL-AY before BUL-BA collapses export."""
    rows = lock_log_rows()
    prefix = [row for row in rows if row[0] <= 50]
    locks = lock_map(effective_locks(rows=prefix))
    assert locks.get("t_sw2_d") == {"sw2": "north", "sw1": "south", "sw3": "north"}


def test_static_replace_clears_inherited_when_for_export():
    """BUL-BA replace must collapse inherited when back to the static sw2 north export."""
    proc = run_shift()
    assert proc.returncode == 0, proc.stderr
    locks = lock_map()
    assert locks.get("t_sw2_d") == {"sw2": "north"}
    state = effective_lock_state()
    assert not state["t_sw2_d"].get("inherit_when_from")


def test_witness_active_skips_retired_bulletin():
    """BUL-BB g-seal must skip when BUL-AL no longer owns a surviving track lock."""
    state = effective_lock_state()
    assert "t_sw3_g" not in state
    locks = lock_map()
    assert "t_sw3_g" not in locks


def test_transcript_has_required_fields():
    """Transcript JSON must expose the documented GET /v1/transcript fields."""
    proc = run_shift()
    assert proc.returncode == 0, proc.stderr
    payload = json.loads(OUTPUT.read_text(encoding="utf-8"))
    for field in ("train", "start", "goal", "history", "moves", "won", "switches"):
        assert field in payload, f"missing transcript field {field}"


def test_property_random_prefixes_resolve_deterministically():
    """Random route_lock_log prefixes must fold to stable lock sets on repeated resolution."""
    network = load_network()
    rows = lock_log_rows()
    rng = random.Random(RANDOM_SEED)
    for _ in range(RANDOM_CASES):
        end = rng.randint(1, len(rows))
        prefix = rows[:end]
        first = normalized_locks(effective_locks(network, prefix))
        second = normalized_locks(effective_locks(network, prefix))
        assert first == second
