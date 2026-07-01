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
        r
        for r in load_rulings()
        if r["incident"] == "INC-1" and r["ruling_seq"] <= 4
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
    assert official["alice"]["score"] == provisional["alice"]["score"] + 5
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
    provisional = {r["player"]: r for r in simulate_standings(load_ledger_rows())}
    official = {r["player"]: r for r in parse_transcript(OUTPUT.read_text())}
    assert official["dave"]["score"] == provisional["dave"]["score"] + 3
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
        if (r["incident"] != "INC-11" or r["ruling_seq"] < 15)
        and r["ruling_seq"] <= 41
    ]
    official = {
        r["player"]: r
        for r in reconcile_rulings(simulate_standings(load_ledger_rows()), without_amend)
    }
    assert official["bob"]["score"] == 13


def test_requires_incident_skips_rescinded_dependency():
    """A ruling requiring a rescinded incident must not change standings."""
    proc = run_worker()
    assert proc.returncode == 0, proc.stderr
    provisional = {r["player"]: r for r in simulate_standings(load_ledger_rows())}
    official = {r["player"]: r for r in parse_transcript(OUTPUT.read_text())}
    assert official["alice"]["score"] == provisional["alice"]["score"] + 5


def test_requires_incident_applies_when_dependency_active():
    """INC-11 stays deferred and restores bob to thirteen only while still deferred."""
    rulings = load_rulings()
    without_amend = [
        r
        for r in rulings
        if (r["incident"] != "INC-11" or r["ruling_seq"] < 15)
        and r["ruling_seq"] <= 41
    ]
    official = {
        r["player"]: r
        for r in reconcile_rulings(simulate_standings(load_ledger_rows()), without_amend)
    }
    assert official["bob"]["score"] == 13


def test_correct_delta_adjusts_tiebreak():
    """Dave's +2 correct_delta must rank him above carol on the official transcript."""
    proc = run_worker()
    assert proc.returncode == 0, proc.stderr
    official = {r["player"]: r for r in parse_transcript(OUTPUT.read_text())}
    assert official["dave"]["correct"] == 3
    assert official["carol"]["correct"] == 2
    assert official["dave"]["rank"] < official["carol"]["rank"]


def test_amend_omit_resets_correct_delta():
    """INC-13 amend without correct_delta must reset the incident delta to zero."""
    proc = run_worker()
    assert proc.returncode == 0, proc.stderr
    official = {r["player"]: r for r in parse_transcript(OUTPUT.read_text())}
    assert official["carol"]["correct"] == 2


def test_amend_omit_resets_delta():
    """INC-22 amend without delta must reset the incident score delta to zero."""
    proc = run_worker()
    assert proc.returncode == 0, proc.stderr
    official = {r["player"]: r for r in parse_transcript(OUTPUT.read_text())}
    assert official["carol"]["score"] == 15


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
        if (r["incident"] != "INC-11" or r["ruling_seq"] < 15)
        and r["ruling_seq"] <= 41
    ]
    official = {
        r["player"]: r
        for r in reconcile_rulings(simulate_standings(load_ledger_rows()), without_amend)
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
        {"ruling_seq": 3, "incident": "INC-X", "op": "rescind", "player": "alice", "delta": 0},
        {"ruling_seq": 4, "incident": "INC-Y", "op": "amend", "player": "alice", "delta": 7},
    ]
    official = reconcile_rulings(base, rulings)
    provisional_alice = next(r for r in base if r["player"] == "alice")
    alice = next(r for r in official if r["player"] == "alice")
    assert alice["score"] == provisional_alice["score"] + 7


def test_rescind_cascades_to_paired_incident():
    """Rescinding INC-25 must also void INC-26's alice -4 counter-adjustment (H-2026-12)."""
    proc = run_worker()
    assert proc.returncode == 0, proc.stderr
    provisional = {r["player"]: r for r in simulate_standings(load_ledger_rows())}
    official = {r["player"]: r for r in parse_transcript(OUTPUT.read_text())}
    assert official["alice"]["score"] == provisional["alice"]["score"] + 5
    assert official["carol"]["score"] == 15


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
    assert dave["score"] == 18


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
    provisional = {r["player"]: r for r in simulate_standings(load_ledger_rows())}
    official = {r["player"]: r for r in parse_transcript(OUTPUT.read_text())}
    assert official["dave"]["score"] == provisional["dave"]["score"] + 3
    assert official["alice"]["score"] == provisional["alice"]["score"] + 5


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
    assert official["alice"]["score"] == provisional["alice"]["score"] + 5


def test_amend_omit_retains_player():
    """INC-42 amend without player must still credit dave (H-2026-18)."""
    proc = run_worker()
    assert proc.returncode == 0, proc.stderr
    provisional = {r["player"]: r for r in simulate_standings(load_ledger_rows())}
    official = {r["player"]: r for r in parse_transcript(OUTPUT.read_text())}
    assert official["dave"]["score"] == provisional["dave"]["score"] + 3


def test_deferred_paired_snapshot_after_parent_rescind():
    """INC-46 must still apply after INC-45 rescind when snapshotted (H-2026-19)."""
    proc = run_worker()
    assert proc.returncode == 0, proc.stderr
    provisional = {r["player"]: r for r in simulate_standings(load_ledger_rows())}
    official = {r["player"]: r for r in parse_transcript(OUTPUT.read_text())}
    assert official["alice"]["score"] == provisional["alice"]["score"] + 5
    assert official["carol"]["score"] == 15


def test_amend_syncs_frozen_deferred_snapshot():
    """INC-46 amend retargeting to bob must apply snapshotted -6 to bob, not alice (H-2026-20)."""
    proc = run_worker()
    assert proc.returncode == 0, proc.stderr
    provisional = {r["player"]: r for r in simulate_standings(load_ledger_rows())}
    official = {r["player"]: r for r in parse_transcript(OUTPUT.read_text())}
    assert official["bob"]["score"] == 5
    assert official["alice"]["score"] == provisional["alice"]["score"] + 5


def test_supersede_clears_without_rescind_taint():
    """INC-50 supersedes INC-42 without ever-rescinded taint so INC-54 can still apply (H-2026-21)."""
    proc = run_worker()
    assert proc.returncode == 0, proc.stderr
    provisional = {r["player"]: r for r in simulate_standings(load_ledger_rows())}
    official = {r["player"]: r for r in parse_transcript(OUTPUT.read_text())}
    assert official["dave"]["score"] == provisional["dave"]["score"] + 3
    assert official["bob"]["score"] == 5


def test_supersede_blocks_dependency_at_record_time():
    """INC-53 must stay void because INC-42 was absent when it was recorded (H-2026-21)."""
    proc = run_worker()
    assert proc.returncode == 0, proc.stderr
    official = {r["player"]: r for r in parse_transcript(OUTPUT.read_text())}
    assert official["carol"]["score"] == 15


def test_demotion_clears_paired_frozen_snapshot():
    """Demoting INC-60 must drop snapshotted INC-61 so alice keeps the slimmer net (H-2026-22)."""
    proc = run_worker()
    assert proc.returncode == 0, proc.stderr
    provisional = {r["player"]: r for r in simulate_standings(load_ledger_rows())}
    official = {r["player"]: r for r in parse_transcript(OUTPUT.read_text())}
    assert official["alice"]["score"] == provisional["alice"]["score"] + 5
    assert official["carol"]["score"] == 15
