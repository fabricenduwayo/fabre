"""Behavioral verifier for the Harbor trivia replay worker."""

import csv
import json

import pytest

from helpers import (
    OUTPUT,
    REF_API,
    expected_standings,
    expected_transcript,
    format_transcript,
    load_ledger_rows,
    load_rulings,
    reconcile_rulings,
    request_json,
    reset_referee,
    run_worker,
    simulate_standings,
)


@pytest.fixture(autouse=True)
def clean_referee():
    """Reset referee state before each test."""
    reset_referee()
    yield
    reset_referee()


def parse_transcript(text: str) -> list[dict]:
    """Parse a STANDINGS transcript into ranked player rows."""
    lines = text.strip().splitlines()
    rows = []
    for line in lines[2:]:
        rank, player, score, correct, fb = line.split()
        rows.append(
            {
                "rank": int(rank),
                "player": player,
                "score": int(score),
                "correct": int(correct),
                "first_buzz_seq": None if fb == "-" else int(fb),
            }
        )
    return rows


def test_worker_replays_match_night_transcript():
    """Replay must emit the canonical official standings transcript."""
    proc = run_worker()
    assert proc.returncode == 0, proc.stderr
    assert OUTPUT.exists(), "worker did not write scoreboard transcript"
    assert OUTPUT.read_text() == expected_transcript()


def test_worker_uses_seq_order_not_timestamp():
    """Ledger rows with later timestamps but lower seq must not reorder ingest."""
    rows = load_ledger_rows()
    swapped = []
    for row in rows:
        copy = dict(row)
        if row["seq"] == 4:
            copy["ts"] = "2026-03-15T20:05:00Z"
        if row["seq"] == 5:
            copy["ts"] = "2026-03-15T20:00:04Z"
        swapped.append(copy)

    ledger_path = OUTPUT.parent / "swap_ledger.csv"
    with ledger_path.open("w", newline="") as fh:
        writer = csv.DictWriter(
            fh,
            fieldnames=["seq", "ts", "kind", "question", "player", "payload"],
        )
        writer.writeheader()
        for row in swapped:
            writer.writerow(
                {
                    "seq": row["seq"],
                    "ts": row["ts"],
                    "kind": row["kind"],
                    "question": row["question"] or "",
                    "player": row["player"] or "",
                    "payload": json.dumps(row["payload"]),
                }
            )

    proc = run_worker(ledger=ledger_path, output=OUTPUT.parent / "swap_out.txt")
    assert proc.returncode == 0, proc.stderr
    # alice must still win q1 buzzer (seq 4 before seq 5)
    status, body = request_json("GET", f"{REF_API}/v1/standings")
    assert status == 200
    alice = next(r for r in body["standings"] if r["player"] == "alice")
    assert alice["score"] == 30


def test_worker_retries_transient_503():
    """Rows whose seq is divisible by six must still be ingested after 503 retry."""
    proc = run_worker()
    assert proc.returncode == 0, proc.stderr
    status, body = request_json("GET", f"{REF_API}/v1/standings")
    assert status == 200
    dave = next(r for r in body["standings"] if r["player"] == "dave")
    assert dave["score"] == 15


def test_locked_question_rows_do_not_award_points():
    """Locked q2 buzzer/answer rows must not change standings (G-2026-03)."""
    proc = run_worker()
    assert proc.returncode == 0, proc.stderr
    status, body = request_json("GET", f"{REF_API}/v1/standings")
    assert status == 200
    dave = next(r for r in body["standings"] if r["player"] == "dave")
    assert dave["correct"] == 1
    assert dave["score"] == 15


def test_duplicate_buzzer_is_ignored_not_penalized():
    """Duplicate buzzer on q1 must not reduce bob below the reference score."""
    proc = run_worker()
    assert proc.returncode == 0, proc.stderr
    status, body = request_json("GET", f"{REF_API}/v1/standings")
    assert status == 200
    bob = next(r for r in body["standings"] if r["player"] == "bob")
    assert bob["score"] == -10


def test_transcript_matches_official_reference():
    """Final transcript must match the hidden official reference (with rulings)."""
    proc = run_worker()
    assert proc.returncode == 0, proc.stderr
    assert OUTPUT.read_text() == expected_transcript()


def test_transcript_is_official_not_provisional():
    """Output must reconcile the rulings, not echo provisional /v1/standings."""
    proc = run_worker()
    assert proc.returncode == 0, proc.stderr
    provisional = format_transcript(simulate_standings(load_ledger_rows()))
    assert OUTPUT.read_text() != provisional, "transcript ignored the stewards' review"


def test_amend_ruling_supersedes_earlier_issue():
    """carol's adjustment must use the amended +7 (INC-1), not the original +10."""
    proc = run_worker()
    assert proc.returncode == 0, proc.stderr
    provisional = {r["player"]: r for r in simulate_standings(load_ledger_rows())}
    inc1_only = [
        r for r in load_rulings() if r["incident"] == "INC-1" and r["ruling_seq"] <= 4
    ]
    carol_official = next(
        r
        for r in reconcile_rulings(simulate_standings(load_ledger_rows()), inc1_only)
        if r["player"] == "carol"
    )
    assert carol_official["score"] == provisional["carol"]["score"] + 7
    assert carol_official["score"] != provisional["carol"]["score"] + 10


def test_amend_retargets_incident_player():
    """INC-4 amend must move the +8 adjustment from bob to alice, not apply both."""
    proc = run_worker()
    assert proc.returncode == 0, proc.stderr
    provisional = {r["player"]: r for r in simulate_standings(load_ledger_rows())}
    official = {r["player"]: r for r in parse_transcript(OUTPUT.read_text())}
    assert official["alice"]["score"] == provisional["alice"]["score"] + 12
    assert official["bob"]["score"] == 5


def test_ruling_score_floor_clamps_at_zero():
    """Bob must hit zero after a primary penalty before later credit, then take deferred -6."""
    proc = run_worker()
    assert proc.returncode == 0, proc.stderr
    provisional = {r["player"]: r for r in simulate_standings(load_ledger_rows())}
    official = {r["player"]: r for r in parse_transcript(OUTPUT.read_text())}
    assert provisional["bob"]["score"] < 0
    assert official["bob"]["score"] == 5


def test_rescinded_rulings_have_no_effect():
    """Rescinded incidents (dave +20, bob -8) must not change provisional scores."""
    proc = run_worker()
    assert proc.returncode == 0, proc.stderr
    expected = {r["player"]: r for r in expected_standings()}
    official = {r["player"]: r for r in parse_transcript(OUTPUT.read_text())}
    assert official["dave"]["score"] == expected["dave"]["score"]
    assert official["bob"]["score"] == 5


def test_nonparticipant_ruling_is_void():
    """A ruling for a player who never appeared must not add them to standings."""
    proc = run_worker()
    assert proc.returncode == 0, proc.stderr
    players = {r["player"] for r in parse_transcript(OUTPUT.read_text())}
    ruling_players = {r["player"] for r in load_rulings() if "player" in r}
    match_players = {r["player"] for r in simulate_standings(load_ledger_rows())}
    for ghost in ruling_players - match_players:
        assert ghost not in players


def test_tiebreak_applies_after_adjustment():
    """Official standings must match the hidden reference after all rulings."""
    proc = run_worker()
    assert proc.returncode == 0, proc.stderr
    official = parse_transcript(OUTPUT.read_text())
    assert official == expected_standings()


def test_post_floor_credit_applies_after_primary_clamp():
    """Deferred rulings still run only after the primary zero clamp when left deferred."""
    rulings = load_rulings()
    without_amend = [
        r
        for r in rulings
        if (r["incident"] != "INC-11" or r["ruling_seq"] < 15) and r["ruling_seq"] <= 41
    ]
    official = {
        r["player"]: r
        for r in reconcile_rulings(
            simulate_standings(load_ledger_rows()), without_amend
        )
    }
    assert official["bob"]["score"] == 13


def test_requires_incident_skips_rescinded_dependency():
    """A ruling requiring a rescinded incident must not change standings."""
    proc = run_worker()
    assert proc.returncode == 0, proc.stderr
    provisional = {r["player"]: r for r in simulate_standings(load_ledger_rows())}
    official = {r["player"]: r for r in parse_transcript(OUTPUT.read_text())}
    assert official["alice"]["score"] == provisional["alice"]["score"] + 12


def test_requires_incident_applies_when_dependency_active():
    """INC-11 stays deferred and restores bob to thirteen only while still deferred."""
    rulings = load_rulings()
    without_amend = [
        r
        for r in rulings
        if (r["incident"] != "INC-11" or r["ruling_seq"] < 15) and r["ruling_seq"] <= 41
    ]
    official = {
        r["player"]: r
        for r in reconcile_rulings(
            simulate_standings(load_ledger_rows()), without_amend
        )
    }
    assert official["bob"]["score"] == 13


def test_correct_delta_adjusts_tiebreak():
    """correct_delta must break TR-TIEBREAK ties when scores are equal."""
    rows = simulate_standings(load_ledger_rows())
    rulings = [
        {
            "ruling_seq": 1,
            "incident": "INC-A",
            "op": "issue",
            "player": "carol",
            "delta": 7,
        },
        {
            "ruling_seq": 2,
            "incident": "INC-B",
            "op": "issue",
            "player": "dave",
            "delta": 0,
            "correct_delta": 2,
        },
    ]
    official = {r["player"]: r for r in reconcile_rulings(rows, rulings)}
    assert official["carol"]["score"] == official["dave"]["score"]
    assert official["dave"]["correct"] > official["carol"]["correct"]
    assert official["dave"]["rank"] < official["carol"]["rank"]


def test_amend_omit_resets_correct_delta():
    """INC-13 amend without correct_delta must reset the incident delta to zero."""
    rows = simulate_standings(load_ledger_rows())
    rulings = [
        {
            "ruling_seq": 1,
            "incident": "INC-13",
            "op": "issue",
            "player": "carol",
            "delta": 0,
            "correct_delta": 2,
        },
        {
            "ruling_seq": 2,
            "incident": "INC-13",
            "op": "amend",
            "player": "carol",
            "delta": -5,
        },
    ]
    baseline = {r["player"]: r for r in rows}
    official = {r["player"]: r for r in reconcile_rulings(rows, rulings)}
    assert official["carol"]["correct"] == baseline["carol"]["correct"]


def test_amend_omit_resets_delta():
    """INC-22 amend without delta must reset the incident score delta to zero."""
    proc = run_worker()
    assert proc.returncode == 0, proc.stderr
    expected = {r["player"]: r for r in expected_standings()}
    official = {r["player"]: r for r in parse_transcript(OUTPUT.read_text())}
    assert official["carol"]["score"] == expected["carol"]["score"]


def test_primary_requires_active_at_replay_end():
    """INC-21 must not apply after INC-5 is rescinded even though it was valid when recorded."""
    proc = run_worker()
    assert proc.returncode == 0, proc.stderr
    official = {r["player"]: r for r in parse_transcript(OUTPUT.read_text())}
    assert official["bob"]["score"] == 5


def test_deferred_requires_snapshot_after_dependency_rescind():
    """INC-11 keeps deferred eligibility when still deferred after INC-5 is rescinded."""
    rulings = load_rulings()
    without_amend = [
        r
        for r in rulings
        if (r["incident"] != "INC-11" or r["ruling_seq"] < 15) and r["ruling_seq"] <= 41
    ]
    official = {
        r["player"]: r
        for r in reconcile_rulings(
            simulate_standings(load_ledger_rows()), without_amend
        )
    }
    assert official["bob"]["score"] == 13


def test_correct_count_floor_clamps_at_zero():
    """Negative provisional scores must clamp to zero before any surviving post-floor credit."""
    proc = run_worker()
    assert proc.returncode == 0, proc.stderr
    provisional = {r["player"]: r for r in simulate_standings(load_ledger_rows())}
    official = {r["player"]: r for r in parse_transcript(OUTPUT.read_text())}
    assert provisional["bob"]["score"] < 0
    assert official["bob"]["score"] == 5


def test_sequential_primary_floor_checkpoint():
    """Primary rulings must clamp between each ruling_seq step (H-2026-09), not only at the end."""
    proc = run_worker()
    assert proc.returncode == 0, proc.stderr
    provisional = {r["player"]: r for r in simulate_standings(load_ledger_rows())}
    official = {r["player"]: r for r in parse_transcript(OUTPUT.read_text())}
    # Batch primary apply would leave bob at zero; sequential checkpoints yield eight.
    assert provisional["bob"]["score"] < 0
    assert official["bob"]["score"] == 5
    assert official["bob"]["score"] != 0


def test_ingest_body_includes_all_ledger_fields():
    """Ingest POST bodies must carry the full ledger row, including ts and null keys."""
    proc = run_worker()
    assert proc.returncode == 0, proc.stderr
    rows = load_ledger_rows()
    open_row = next(r for r in rows if r["kind"] == "open" and r["question"] == "q1")
    status, body = request_json(
        "POST",
        f"{REF_API}/v1/ingest",
        open_row,
        {"X-Idempotency-Key": f"match-night-{open_row['seq']}"},
    )
    assert status == 200
    assert body and body.get("status") == "duplicate"
    stripped = {k: v for k, v in open_row.items() if k != "ts"}
    status, body = request_json(
        "POST",
        f"{REF_API}/v1/ingest",
        stripped,
        {"X-Idempotency-Key": f"match-night-{open_row['seq']}"},
    )
    assert status == 409


def test_worker_sends_idempotency_keys():
    """Re-running ingest for seq 1 with the same key must be a duplicate, not 400."""
    proc = run_worker()
    assert proc.returncode == 0, proc.stderr
    rows = load_ledger_rows()
    row = rows[0]
    status, body = request_json(
        "POST",
        f"{REF_API}/v1/ingest",
        row,
        {"X-Idempotency-Key": f"match-night-{row['seq']}"},
    )
    assert status == 200
    assert body and body.get("status") == "duplicate"


def test_amend_omit_resets_applies_after_floor():
    """INC-11 amend demotes to primary so INC-5 rescind voids it at replay end (H-2026-13)."""
    proc = run_worker()
    assert proc.returncode == 0, proc.stderr
    official = {r["player"]: r for r in parse_transcript(OUTPUT.read_text())}
    assert official["bob"]["score"] == 5


def test_amend_omit_clears_requires_incident():
    """An amend omitting requires_incident must survive a later dependency rescind."""
    base = simulate_standings(load_ledger_rows())
    rulings = [
        {
            "ruling_seq": 1,
            "incident": "INC-X",
            "op": "issue",
            "player": "alice",
            "delta": 0,
            "correct_delta": 0,
        },
        {
            "ruling_seq": 2,
            "incident": "INC-Y",
            "op": "issue",
            "player": "alice",
            "delta": 7,
            "requires_incident": "INC-X",
        },
        {
            "ruling_seq": 3,
            "incident": "INC-X",
            "op": "rescind",
            "player": "alice",
            "delta": 0,
        },
        {
            "ruling_seq": 4,
            "incident": "INC-Y",
            "op": "amend",
            "player": "alice",
            "delta": 7,
        },
    ]
    official = reconcile_rulings(base, rulings)
    provisional_alice = next(r for r in base if r["player"] == "alice")
    alice = next(r for r in official if r["player"] == "alice")
    assert alice["score"] == provisional_alice["score"] + 7


def test_rescind_cascades_to_paired_incident():
    """Rescinding INC-25 must also void INC-26's alice -4 counter-adjustment (H-2026-12)."""
    proc = run_worker()
    assert proc.returncode == 0, proc.stderr
    expected = {r["player"]: r for r in expected_standings()}
    provisional = {r["player"]: r for r in simulate_standings(load_ledger_rows())}
    official = {r["player"]: r for r in parse_transcript(OUTPUT.read_text())}
    assert official["alice"]["score"] == provisional["alice"]["score"] + 12
    assert official["carol"]["score"] == expected["carol"]["score"]


def test_paired_incident_void_when_parent_missing():
    """INC-26 must not apply when its paired_incident parent was never active."""
    rulings = load_rulings()
    orphan = {
        "ruling_seq": 99,
        "incident": "INC-99",
        "op": "issue",
        "player": "dave",
        "delta": -50,
        "paired_incident": "INC-MISSING",
        "issued_at": "2026-03-15T22:00:00Z",
    }
    official = reconcile_rulings(
        simulate_standings(load_ledger_rows()),
        rulings + [orphan],
    )
    dave = next(r for r in official if r["player"] == "dave")
    expected_dave = next(r for r in expected_standings() if r["player"] == "dave")
    assert dave["score"] == expected_dave["score"]


def test_transitive_requires_incident_void_at_replay_end():
    """INC-30 must not apply when INC-29's chain reaches rescinded INC-5 (H-2026-14)."""
    proc = run_worker()
    assert proc.returncode == 0, proc.stderr
    official = {r["player"]: r for r in parse_transcript(OUTPUT.read_text())}
    assert official["bob"]["score"] == 5


def test_transitive_paired_incident_cascade_on_rescind():
    """Rescinding INC-31 must also void INC-33 paired through INC-32 (H-2026-15)."""
    proc = run_worker()
    assert proc.returncode == 0, proc.stderr
    expected = {r["player"]: r for r in expected_standings()}
    provisional = {r["player"]: r for r in simulate_standings(load_ledger_rows())}
    official = {r["player"]: r for r in parse_transcript(OUTPUT.read_text())}
    assert official["dave"]["score"] == expected["dave"]["score"]
    assert official["alice"]["score"] == provisional["alice"]["score"] + 12


def test_reissued_incident_does_not_restore_dependency():
    """INC-34 must stay void even though INC-5 is re-issued after rescind (H-2026-16)."""
    proc = run_worker()
    assert proc.returncode == 0, proc.stderr
    official = {r["player"]: r for r in parse_transcript(OUTPUT.read_text())}
    assert official["bob"]["score"] == 5


def test_transcript_ends_with_trailing_newline():
    """The scoreboard file must end with a newline after the last player row."""
    proc = run_worker()
    assert proc.returncode == 0, proc.stderr
    text = OUTPUT.read_text()
    assert text.endswith("\n"), "scoreboard must end with a trailing newline"
    assert not text.endswith("\n\n"), "scoreboard must not have a blank trailing line"


def test_ingest_uses_default_json_serialization():
    """Ingest bodies must use default json.dumps spacing so byte-exact replay succeeds."""
    import urllib.error
    import urllib.request

    proc = run_worker()
    assert proc.returncode == 0, proc.stderr
    rows = load_ledger_rows()
    row = next(r for r in rows if r["kind"] == "open" and r["question"] == "q1")
    compact = json.dumps(row, separators=(",", ":"), sort_keys=True).encode()
    req = urllib.request.Request(
        f"{REF_API}/v1/ingest",
        data=compact,
        headers={
            "Content-Type": "application/json",
            "X-Idempotency-Key": f"match-night-{row['seq']}",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            status = resp.status
    except urllib.error.HTTPError as exc:
        status = exc.code
    assert status == 409, "compact re-serialization must not match the stored body"


def test_reissued_paired_parent_does_not_restore_paired_ruling():
    """INC-41 stays void after INC-40 is re-issued post-rescind (H-2026-17)."""
    proc = run_worker()
    assert proc.returncode == 0, proc.stderr
    provisional = {r["player"]: r for r in simulate_standings(load_ledger_rows())}
    official = {r["player"]: r for r in parse_transcript(OUTPUT.read_text())}
    assert official["alice"]["score"] == provisional["alice"]["score"] + 12


def test_amend_omit_retains_player():
    """INC-42 amend without player must still credit dave (H-2026-18)."""
    proc = run_worker()
    assert proc.returncode == 0, proc.stderr
    expected = {r["player"]: r for r in expected_standings()}
    {r["player"]: r for r in simulate_standings(load_ledger_rows())}
    official = {r["player"]: r for r in parse_transcript(OUTPUT.read_text())}
    assert official["dave"]["score"] == expected["dave"]["score"]


def test_deferred_paired_snapshot_after_parent_rescind():
    """INC-46 must still apply after INC-45 rescind when snapshotted (H-2026-19)."""
    proc = run_worker()
    assert proc.returncode == 0, proc.stderr
    expected = {r["player"]: r for r in expected_standings()}
    provisional = {r["player"]: r for r in simulate_standings(load_ledger_rows())}
    official = {r["player"]: r for r in parse_transcript(OUTPUT.read_text())}
    assert official["alice"]["score"] == provisional["alice"]["score"] + 12
    assert official["carol"]["score"] == expected["carol"]["score"]


def test_amend_syncs_frozen_deferred_snapshot():
    """INC-46 amend retargeting to bob must apply snapshotted -6 to bob, not alice (H-2026-20)."""
    proc = run_worker()
    assert proc.returncode == 0, proc.stderr
    provisional = {r["player"]: r for r in simulate_standings(load_ledger_rows())}
    official = {r["player"]: r for r in parse_transcript(OUTPUT.read_text())}
    assert official["bob"]["score"] == 5
    assert official["alice"]["score"] == provisional["alice"]["score"] + 12


def test_supersede_clears_without_rescind_taint():
    """INC-50 supersedes INC-42 without ever-rescinded taint so INC-54 can still apply (H-2026-21)."""
    proc = run_worker()
    assert proc.returncode == 0, proc.stderr
    expected = {r["player"]: r for r in expected_standings()}
    {r["player"]: r for r in simulate_standings(load_ledger_rows())}
    official = {r["player"]: r for r in parse_transcript(OUTPUT.read_text())}
    assert official["dave"]["score"] == expected["dave"]["score"]
    assert official["bob"]["score"] == 5


def test_supersede_blocks_dependency_at_record_time():
    """INC-53 must stay void because INC-42 was absent when it was recorded (H-2026-21)."""
    proc = run_worker()
    assert proc.returncode == 0, proc.stderr
    expected = {r["player"]: r for r in expected_standings()}
    official = {r["player"]: r for r in parse_transcript(OUTPUT.read_text())}
    assert official["carol"]["score"] == expected["carol"]["score"]


def test_demotion_clears_paired_frozen_snapshot():
    """Demoting INC-60 must drop snapshotted INC-61 so alice keeps the slimmer net (H-2026-22)."""
    proc = run_worker()
    assert proc.returncode == 0, proc.stderr
    expected = {r["player"]: r for r in expected_standings()}
    provisional = {r["player"]: r for r in simulate_standings(load_ledger_rows())}
    official = {r["player"]: r for r in parse_transcript(OUTPUT.read_text())}
    assert official["alice"]["score"] == provisional["alice"]["score"] + 12
    assert official["carol"]["score"] == expected["carol"]["score"]


def test_deferred_score_ceiling_clamps_partial_delta():
    """INC-62 must add only +1 to dave because score_ceiling 19 caps the deferred +5 (H-2026-23)."""
    proc = run_worker()
    assert proc.returncode == 0, proc.stderr
    expected = {r["player"]: r for r in expected_standings()}
    {r["player"]: r for r in simulate_standings(load_ledger_rows())}
    official = {r["player"]: r for r in parse_transcript(OUTPUT.read_text())}
    assert official["dave"]["score"] == expected["dave"]["score"]


def test_mutex_incident_void_when_parent_active():
    """INC-63 must stay void while INC-34 is active in the map at record time (H-2026-24)."""
    proc = run_worker()
    assert proc.returncode == 0, proc.stderr
    official = {r["player"]: r for r in parse_transcript(OUTPUT.read_text())}
    assert official["bob"]["score"] == 5


def test_reinstate_restores_most_recent_rescind_snapshot():
    """INC-75 reinstate must restore the +2 second-lifetime entry, not the +8 first one (H-2026-25)."""
    proc = run_worker()
    assert proc.returncode == 0, proc.stderr
    provisional = {r["player"]: r for r in simulate_standings(load_ledger_rows())}
    official = {r["player"]: r for r in parse_transcript(OUTPUT.read_text())}
    assert official["alice"]["score"] == provisional["alice"]["score"] + 12
    assert official["alice"]["score"] != provisional["alice"]["score"] + 13


def test_reinstate_does_not_clear_dependency_taint():
    """INC-70 reinstate applies its own +2 but INC-72 requiring it stays void (H-2026-25)."""
    proc = run_worker()
    assert proc.returncode == 0, proc.stderr
    expected = {r["player"]: r for r in expected_standings()}
    {r["player"]: r for r in simulate_standings(load_ledger_rows())}
    official = {r["player"]: r for r in parse_transcript(OUTPUT.read_text())}
    assert official["carol"]["score"] == expected["carol"]["score"]
    assert official["dave"]["score"] == expected["dave"]["score"]


def test_reinstate_noop_after_paired_cascade_removal():
    """INC-74 reinstate must be a no-op because it was cleared by the paired cascade (H-2026-25)."""
    proc = run_worker()
    assert proc.returncode == 0, proc.stderr
    official = {r["player"]: r for r in parse_transcript(OUTPUT.read_text())}
    assert official["bob"]["score"] == 5


def test_reinstate_noop_after_supersede():
    """INC-76 reinstate must be a no-op because supersede deleted its rescind snapshot (H-2026-25)."""
    proc = run_worker()
    assert proc.returncode == 0, proc.stderr
    official = {r["player"]: r for r in parse_transcript(OUTPUT.read_text())}
    assert official["bob"]["score"] == 5


def test_reinstated_deferred_rejoins_post_floor_pass():
    """INC-78 reinstate must rejoin the deferred pass and add carol's +1 after the clamp (H-2026-26)."""
    proc = run_worker()
    assert proc.returncode == 0, proc.stderr
    expected = {r["player"]: r for r in expected_standings()}
    official = {r["player"]: r for r in parse_transcript(OUTPUT.read_text())}
    assert official["carol"]["score"] == expected["carol"]["score"]


def test_direct_rescind_drops_frozen_deferred_snapshot():
    """Directly rescinding snapshotted INC-80 must drop its -5, unlike a paired-cascade removal (H-2026-19)."""
    proc = run_worker()
    assert proc.returncode == 0, proc.stderr
    provisional = {r["player"]: r for r in simulate_standings(load_ledger_rows())}
    official = {r["player"]: r for r in parse_transcript(OUTPUT.read_text())}
    assert official["alice"]["score"] == provisional["alice"]["score"] + 12


def test_reinstate_does_not_restore_cascade_removed_paired():
    """Reinstating INC-81 must not resurrect INC-82, which fell to the paired cascade (H-2026-25)."""
    proc = run_worker()
    assert proc.returncode == 0, proc.stderr
    expected = {r["player"]: r for r in expected_standings()}
    official = {r["player"]: r for r in parse_transcript(OUTPUT.read_text())}
    assert official["carol"]["score"] == expected["carol"]["score"]


def test_primary_max_score_after_caps_applied_delta():
    """max_score_after must discard primary score excess above the cap (H-2026-27)."""
    rows = simulate_standings(load_ledger_rows())
    provisional = {r["player"]: r for r in rows}
    rulings = [
        {
            "ruling_seq": 1,
            "incident": "INC-A",
            "op": "issue",
            "player": "carol",
            "delta": 9,
        },
        {
            "ruling_seq": 2,
            "incident": "INC-90",
            "op": "issue",
            "player": "carol",
            "delta": 10,
            "max_score_after": 20,
        },
    ]
    official = {r["player"]: r for r in reconcile_rulings(rows, rulings)}
    assert official["carol"]["score"] == provisional["carol"]["score"] + 12
    assert official["carol"]["score"] == 20


def test_offset_player_transfers_applied_score_change():
    """offset_player must subtract the applied delta after max_score_after, not the nominal delta (H-2026-28)."""
    rows = simulate_standings(load_ledger_rows())
    provisional = {r["player"]: r for r in rows}
    rulings = [
        {
            "ruling_seq": 1,
            "incident": "INC-X",
            "op": "issue",
            "player": "alice",
            "delta": 20,
            "max_score_after": 35,
            "offset_player": "bob",
        }
    ]
    official = {r["player"]: r for r in reconcile_rulings(rows, rulings)}
    assert official["alice"]["score"] == provisional["alice"]["score"] + 5
    assert official["bob"]["score"] == 0


def test_deferred_correct_ceiling_clamps_partial_correct_delta():
    """INC-92 must add only +1 correct to dave because correct_ceiling 4 caps the +3 (H-2026-29)."""
    proc = run_worker()
    assert proc.returncode == 0, proc.stderr
    without_inc92 = [r for r in load_rulings() if r["incident"] != "INC-92"]
    baseline = {
        r["player"]: r
        for r in reconcile_rulings(
            simulate_standings(load_ledger_rows()), without_inc92
        )
    }
    official = {r["player"]: r for r in parse_transcript(OUTPUT.read_text())}
    assert official["dave"]["correct"] == baseline["dave"]["correct"]


def test_offset_player_void_when_target_not_in_standings():
    """A ruling whose offset_player never appeared in provisional standings must stay void (H-2026-28)."""
    rows = simulate_standings(load_ledger_rows())
    provisional = {r["player"]: r for r in rows}
    rulings = [
        {
            "ruling_seq": 1,
            "incident": "INC-X",
            "op": "issue",
            "player": "alice",
            "delta": 5,
            "offset_player": "zoe",
        }
    ]
    official = {r["player"]: r for r in reconcile_rulings(rows, rulings)}
    assert official["alice"]["score"] == provisional["alice"]["score"]
    assert "zoe" not in official


def test_deferred_offset_runs_before_score_ceiling():
    """INC-94 must pull the full nominal delta from dave before trimming carol to score_ceiling 24 (H-2026-30)."""
    proc = run_worker()
    assert proc.returncode == 0, proc.stderr
    expected = {r["player"]: r for r in expected_standings()}
    without_inc94 = [r for r in load_rulings() if r["incident"] != "INC-94"]
    baseline = {
        r["player"]: r
        for r in reconcile_rulings(
            simulate_standings(load_ledger_rows()), without_inc94
        )
    }
    official = {r["player"]: r for r in parse_transcript(OUTPUT.read_text())}
    assert official["carol"]["score"] == expected["carol"]["score"]
    assert official["dave"]["score"] == baseline["dave"]["score"] - 6
    assert official["dave"]["score"] == expected["dave"]["score"]


def test_offset_solvency_caps_primary_transfer():
    """Primary offset must not debit more than offset_player's current score (H-2026-32)."""
    rows = simulate_standings(load_ledger_rows())
    provisional = {r["player"]: r for r in rows}
    rulings = [
        {
            "ruling_seq": 1,
            "incident": "INC-X",
            "op": "issue",
            "player": "alice",
            "delta": 10,
            "offset_player": "bob",
        }
    ]
    official = {r["player"]: r for r in reconcile_rulings(rows, rulings)}
    assert official["alice"]["score"] == provisional["alice"]["score"] + 10
    assert official["bob"]["score"] == 0


def test_deferred_offset_without_score_ceiling():
    """Deferred offset_player must run even when score_ceiling is omitted (H-2026-33)."""
    rows = simulate_standings(load_ledger_rows())
    {r["player"]: r for r in rows}
    rulings = [
        {
            "ruling_seq": 1,
            "incident": "INC-X",
            "op": "issue",
            "player": "bob",
            "delta": 5,
            "offset_player": "alice",
            "applies_after_floor": True,
        }
    ]
    official = {r["player"]: r for r in reconcile_rulings(rows, rulings)}
    assert official["bob"]["score"] == 5
    assert official["alice"]["score"] == 25


def test_offset_min_score_halves_primary_transfer():
    """Primary offset must transfer only half the applied delta when the beneficiary sits below offset_min_score (H-2026-31)."""
    rows = simulate_standings(load_ledger_rows())
    provisional = {r["player"]: r for r in rows}
    rulings = [
        {
            "ruling_seq": 1,
            "incident": "INC-X",
            "op": "issue",
            "player": "carol",
            "delta": 2,
            "offset_player": "dave",
            "offset_min_score": 24,
        }
    ]
    official = {r["player"]: r for r in reconcile_rulings(rows, rulings)}
    assert official["carol"]["score"] == provisional["carol"]["score"] + 2
    assert official["dave"]["score"] == provisional["dave"]["score"] - 1


def test_dual_ceiling_blocked_score_zeroes_correct_credit():
    """When score_ceiling blocks all score credit, correct_delta must stay 0 even if correct_ceiling has headroom (H-2026-34)."""
    rows = simulate_standings(load_ledger_rows())
    provisional = {r["player"]: r for r in rows}
    rulings = [
        {
            "ruling_seq": 1,
            "incident": "INC-A",
            "op": "issue",
            "player": "carol",
            "delta": 16,
            "applies_after_floor": True,
        },
        {
            "ruling_seq": 2,
            "incident": "INC-B",
            "op": "issue",
            "player": "carol",
            "delta": 0,
            "correct_delta": 1,
            "applies_after_floor": True,
            "score_ceiling": 24,
            "correct_ceiling": 4,
        },
    ]
    official = {r["player"]: r for r in reconcile_rulings(rows, rulings)}
    assert official["carol"]["score"] == 24
    assert official["carol"]["correct"] == provisional["carol"]["correct"]


def test_deferred_offset_min_score_halves_offset_debit():
    """Deferred offset must debit only half the nominal delta when the beneficiary is below offset_min_score (H-2026-35)."""
    proc = run_worker()
    assert proc.returncode == 0, proc.stderr
    without_inc102 = [r for r in load_rulings() if r["incident"] != "INC-102"]
    baseline = {
        r["player"]: r
        for r in reconcile_rulings(
            simulate_standings(load_ledger_rows()), without_inc102
        )
    }
    official = {r["player"]: r for r in parse_transcript(OUTPUT.read_text())}
    assert official["carol"]["score"] == 30
    assert official["dave"]["score"] == baseline["dave"]["score"] - 3
    assert official["dave"]["score"] == 10


def test_frozen_snapshot_syncs_offset_min_score_on_amend():
    """Amend must refresh offset_min_score on a frozen deferred snapshot after the paired parent is rescinded (H-2026-36)."""
    rows = simulate_standings(load_ledger_rows())
    provisional = {r["player"]: r for r in rows}
    rulings = [
        {
            "ruling_seq": 1,
            "incident": "INC-P",
            "op": "issue",
            "player": "carol",
            "delta": 0,
            "applies_after_floor": True,
        },
        {
            "ruling_seq": 2,
            "incident": "INC-C",
            "op": "issue",
            "player": "carol",
            "delta": 6,
            "offset_player": "dave",
            "offset_min_score": 30,
            "applies_after_floor": True,
            "paired_incident": "INC-P",
        },
        {
            "ruling_seq": 3,
            "incident": "INC-C",
            "op": "amend",
            "player": "carol",
            "delta": 6,
            "offset_player": "dave",
            "offset_min_score": 5,
            "applies_after_floor": True,
            "paired_incident": "INC-P",
        },
        {"ruling_seq": 4, "incident": "INC-P", "op": "rescind", "delta": 0},
    ]
    official = {r["player"]: r for r in reconcile_rulings(rows, rulings)}
    assert official["carol"]["score"] == provisional["carol"]["score"] + 6
    assert official["dave"]["score"] == provisional["dave"]["score"] - 6


def test_inc101_blocked_correct_credit_in_full_replay():
    """INC-101 must not raise carol's correct count when her score is already at score_ceiling 24 (H-2026-34)."""
    rows = simulate_standings(load_ledger_rows())
    rulings = load_rulings() + [
        {
            "ruling_seq": 999,
            "incident": "INC-101",
            "op": "issue",
            "player": "carol",
            "delta": 0,
            "correct_delta": 1,
            "applies_after_floor": True,
            "score_ceiling": 24,
            "correct_ceiling": 4,
            "issued_at": "2026-03-15T22:22:25Z",
        }
    ]
    baseline = {
        r["player"]: r
        for r in reconcile_rulings(simulate_standings(load_ledger_rows()), load_rulings())
    }
    official = {r["player"]: r for r in reconcile_rulings(rows, rulings)}
    assert official["carol"]["correct"] == baseline["carol"]["correct"]
    assert official["carol"]["score"] == baseline["carol"]["score"]


def test_deferred_offset_refund_when_ceiling_blocks_score():
    """Deferred offset must refund when score_ceiling blocks all score credit (H-2026-37)."""
    rows = simulate_standings(load_ledger_rows())
    provisional = {r["player"]: r for r in rows}
    rulings = [
        {
            "ruling_seq": 1,
            "incident": "INC-A",
            "op": "issue",
            "player": "carol",
            "delta": 16,
            "applies_after_floor": True,
        },
        {
            "ruling_seq": 2,
            "incident": "INC-B",
            "op": "issue",
            "player": "carol",
            "delta": 5,
            "offset_player": "dave",
            "applies_after_floor": True,
            "score_ceiling": 24,
        },
    ]
    official = {r["player"]: r for r in reconcile_rulings(rows, rulings)}
    assert official["carol"]["score"] == 24
    assert official["dave"]["score"] == provisional["dave"]["score"]


def test_offset_correct_player_transfers_applied_correct_change():
    """offset_correct_player must subtract the applied correct_delta from the named player (H-2026-38)."""
    rows = simulate_standings(load_ledger_rows())
    provisional = {r["player"]: r for r in rows}
    rulings = [
        {
            "ruling_seq": 1,
            "incident": "INC-X",
            "op": "issue",
            "player": "dave",
            "delta": 0,
            "correct_delta": 2,
            "offset_correct_player": "alice",
        }
    ]
    official = {r["player"]: r for r in reconcile_rulings(rows, rulings)}
    assert official["dave"]["correct"] == provisional["dave"]["correct"] + 2
    assert official["alice"]["correct"] == provisional["alice"]["correct"] - 2


def test_correct_offset_solvency_caps_debit():
    """Correct offset must not debit more than offset_correct_player's current correct count (H-2026-39)."""
    rows = simulate_standings(load_ledger_rows())
    provisional = {r["player"]: r for r in rows}
    rulings = [
        {
            "ruling_seq": 1,
            "incident": "INC-X",
            "op": "issue",
            "player": "dave",
            "delta": 0,
            "correct_delta": 3,
            "offset_correct_player": "bob",
        }
    ]
    official = {r["player"]: r for r in reconcile_rulings(rows, rulings)}
    assert official["dave"]["correct"] == provisional["dave"]["correct"] + 3
    assert official["bob"]["correct"] == 0


def test_inc103_refunds_dave_offset_in_full_replay():
    """INC-103 must not debit dave when carol is already above score_ceiling 24 (H-2026-37)."""
    proc = run_worker()
    assert proc.returncode == 0, proc.stderr
    without = [r for r in load_rulings() if r["incident"] != "INC-103"]
    baseline = {
        r["player"]: r
        for r in reconcile_rulings(simulate_standings(load_ledger_rows()), without)
    }
    official = {r["player"]: r for r in parse_transcript(OUTPUT.read_text())}
    assert official["dave"]["score"] == baseline["dave"]["score"]
    assert official["carol"]["score"] == 30


def test_inc104_transfers_correct_from_alice_in_full_replay():
    """INC-104 must debit alice's correct count; net dave gain is +1 because INC-92 ceiling blocks later credit (H-2026-38)."""
    proc = run_worker()
    assert proc.returncode == 0, proc.stderr
    without = [r for r in load_rulings() if r["incident"] != "INC-104"]
    baseline = {
        r["player"]: r
        for r in reconcile_rulings(simulate_standings(load_ledger_rows()), without)
    }
    official = {r["player"]: r for r in parse_transcript(OUTPUT.read_text())}
    assert official["alice"]["correct"] == baseline["alice"]["correct"] - 2
    assert official["dave"]["correct"] == baseline["dave"]["correct"] + 1


def test_blocked_correct_leaves_offset_correct_untouched():
    """Dual-ceiling blocked score must leave offset_correct_player unchanged (H-2026-34/H-2026-40)."""
    rows = simulate_standings(load_ledger_rows())
    provisional = {r["player"]: r for r in rows}
    rulings = [
        {
            "ruling_seq": 1,
            "incident": "INC-A",
            "op": "issue",
            "player": "carol",
            "delta": 16,
            "applies_after_floor": True,
        },
        {
            "ruling_seq": 2,
            "incident": "INC-B",
            "op": "issue",
            "player": "carol",
            "delta": 0,
            "correct_delta": 1,
            "offset_correct_player": "alice",
            "applies_after_floor": True,
            "score_ceiling": 24,
            "correct_ceiling": 4,
        },
    ]
    official = {r["player"]: r for r in reconcile_rulings(rows, rulings)}
    assert official["carol"]["score"] == 24
    assert official["carol"]["correct"] == provisional["carol"]["correct"]
    assert official["alice"]["correct"] == provisional["alice"]["correct"]
