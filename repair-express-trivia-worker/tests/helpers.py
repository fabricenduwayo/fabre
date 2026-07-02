"""Reference scoring helpers for Harbor trivia verifier tests."""

from __future__ import annotations

import csv
import json
import subprocess
import time
import urllib.error
import urllib.request
from pathlib import Path

MATCH_ID = "match-night-2026-03-15"
REF_API = "http://127.0.0.1:3000"
LEDGER = Path("/app/data/match_night.csv")
OUTPUT = Path("/app/output/scoreboard.txt")
WORKER = Path("/app/worker/replay.py")


def request_json(method: str, url: str, payload: dict | None = None, headers: dict | None = None):
    data = None
    hdrs = {}
    if payload is not None:
        hdrs["Content-Type"] = "application/json"
        data = json.dumps(payload).encode()
    if headers:
        hdrs.update(headers)
    req = urllib.request.Request(url, data=data, headers=hdrs, method=method)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            body = resp.read().decode()
            return resp.status, json.loads(body) if body else None
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode()
        try:
            parsed = json.loads(raw) if raw else None
        except json.JSONDecodeError:
            parsed = None
        return exc.code, parsed


def reset_referee() -> None:
    request_json("POST", f"{REF_API}/v1/reset")


def wait_for_referee(timeout_sec: float = 20.0) -> None:
    deadline = time.time() + timeout_sec
    while time.time() < deadline:
        try:
            status, body = request_json("GET", f"{REF_API}/health")
            if status == 200 and body and body.get("status") == "ok":
                return
        except Exception:
            pass
        time.sleep(0.25)
    raise RuntimeError("referee did not become ready")


def load_ledger_rows(path: Path = LEDGER) -> list[dict]:
    rows: list[dict] = []
    with path.open(newline="") as fh:
        reader = csv.DictReader(fh)
        for raw in reader:
            rows.append(
                {
                    "seq": int(raw["seq"]),
                    "ts": raw["ts"],
                    "kind": raw["kind"],
                    "question": raw["question"] or None,
                    "player": raw["player"] or None,
                    "payload": json.loads(raw["payload"] or "{}"),
                }
            )
    return rows


def simulate_standings(rows: list[dict]) -> list[dict]:
    """Pure-Python reference scorer matching the referee rules."""
    questions: dict[str, dict] = {}
    players: dict[str, dict] = {}

    def ensure_player(pid: str) -> dict:
        if pid not in players:
            players[pid] = {"score": 0, "correct": 0, "first_buzz_seq": None}
        return players[pid]

    def ensure_question(qid: str) -> dict:
        if qid not in questions:
            questions[qid] = {
                "open": False,
                "locked": False,
                "buzzer": None,
                "answered": False,
            }
        return questions[qid]

    for row in sorted(rows, key=lambda r: r["seq"]):
        kind = row["kind"]
        qid = row["question"]
        player = row["player"]
        payload = row["payload"]
        q = ensure_question(qid) if qid else None

        if kind == "open" and qid:
            q["open"] = True
            q["locked"] = False
        elif kind == "lock" and qid:
            q["open"] = False
            q["locked"] = True
        elif kind == "buzzer" and qid and player:
            if q["locked"] or not q["open"] or q["answered"]:
                continue
            if q["buzzer"]:
                continue
            q["buzzer"] = player
            stats = ensure_player(player)
            if stats["first_buzz_seq"] is None:
                stats["first_buzz_seq"] = row["seq"]
        elif kind == "answer" and qid and player:
            if q["locked"] or not q["open"] or q["answered"] or q["buzzer"] != player:
                continue
            q["answered"] = True
            stats = ensure_player(player)
            if payload.get("correct"):
                stats["score"] += 10
                stats["correct"] += 1
            else:
                stats["score"] -= 5
        elif kind == "penalty" and player:
            ensure_player(player)["score"] -= int(payload.get("points", 5))
        elif kind == "mod_override" and qid:
            action = payload.get("action")
            if action == "award" and player:
                ensure_player(player)["score"] += int(payload.get("points", 0))
            elif action == "deduct" and player:
                ensure_player(player)["score"] -= int(payload.get("points", 0))
            elif action == "void_buzzer":
                q["buzzer"] = None
            elif action == "reassign":
                if q["locked"] or not q["open"] or q["answered"]:
                    continue
                target = payload.get("player")
                q["buzzer"] = target
                stats = ensure_player(target)
                if stats["first_buzz_seq"] is None:
                    stats["first_buzz_seq"] = row["seq"]

    ordered = sorted(
        players.items(),
        key=lambda item: (
            -item[1]["score"],
            -item[1]["correct"],
            item[1]["first_buzz_seq"] if item[1]["first_buzz_seq"] is not None else 10**9,
            item[0],
        ),
    )
    standings = []
    for idx, (name, stats) in enumerate(ordered, start=1):
        standings.append(
            {
                "rank": idx,
                "player": name,
                "score": stats["score"],
                "correct": stats["correct"],
                "first_buzz_seq": stats["first_buzz_seq"],
            }
        )
    return standings


def format_transcript(standings: list[dict], match_id: str = MATCH_ID) -> str:
    """Render the section 4 standings file from reference standings rows."""
    lines = [
        f"STANDINGS {match_id}",
        "rank player score correct first_buzz_seq",
    ]
    for row in standings:
        fb = row["first_buzz_seq"]
        fb_text = str(fb) if fb is not None else "-"
        lines.append(
            f"{row['rank']} {row['player']} {row['score']} {row['correct']} {fb_text}"
        )
    return "\n".join(lines) + "\n"


RULINGS_FILE = Path("/app/data/rulings.json")


def load_rulings(path: Path = RULINGS_FILE) -> list[dict]:
    """Read the stewards' review feed the referee serves at /v1/rulings."""
    data = json.loads(path.read_text())
    return data.get("rulings", [])


def reconcile_rulings(standings: list[dict], rulings: list[dict]) -> list[dict]:
    """Apply Appendix H reconciliation, then re-rank with TR-TIEBREAK."""
    by_player = {row["player"]: dict(row) for row in standings}

    incidents: dict[str, dict] = {}
    deferred_order: list[str] = []
    ever_rescinded: set[str] = set()
    frozen_deferred: dict[str, dict] = {}
    rescind_snapshot: dict[str, dict] = {}

    for ruling in sorted(rulings, key=lambda r: r["ruling_seq"]):
        op = ruling["op"]
        incident = ruling["incident"]

        if op == "rescind":
            removed: set[str] = set()
            if incident in incidents:
                rescind_snapshot[incident] = dict(incidents.pop(incident))
                removed.add(incident)
                ever_rescinded.add(incident)
                frozen_deferred.pop(incident, None)
                if incident in deferred_order:
                    deferred_order.remove(incident)
            while True:
                paired_remove = [
                    inc
                    for inc, ent in list(incidents.items())
                    if ent.get("paired_incident") in removed
                ]
                if not paired_remove:
                    break
                for inc in paired_remove:
                    incidents.pop(inc, None)
                    removed.add(inc)
                    rescind_snapshot.pop(inc, None)
                    if inc not in frozen_deferred and inc in deferred_order:
                        deferred_order.remove(inc)
            continue

        if op == "reinstate":
            if incident not in incidents and incident in rescind_snapshot:
                entry = dict(rescind_snapshot[incident])
                entry["ruling_seq"] = ruling["ruling_seq"]
                incidents[incident] = entry
                if entry["applies_after_floor"]:
                    if incident in deferred_order:
                        deferred_order.remove(incident)
                    deferred_order.append(incident)
            continue

        if op not in ("issue", "amend"):
            continue

        requires = ruling.get("requires_incident")
        if op == "amend" and "requires_incident" not in ruling:
            requires = None
        if requires and requires not in incidents:
            continue

        paired = ruling.get("paired_incident")
        if paired and paired not in incidents:
            continue

        mutex = ruling.get("mutex_incident")
        if op == "amend" and "mutex_incident" not in ruling:
            mutex = None
        if mutex and mutex in incidents:
            continue

        supersedes = ruling.get("supersedes_incident")
        if supersedes and supersedes in incidents:
            removed = {supersedes}
            incidents.pop(supersedes, None)
            if supersedes in deferred_order:
                deferred_order.remove(supersedes)
            frozen_deferred.pop(supersedes, None)
            rescind_snapshot.pop(supersedes, None)
            while True:
                paired_remove = [
                    inc
                    for inc, ent in list(incidents.items())
                    if ent.get("paired_incident") in removed
                ]
                if not paired_remove:
                    break
                for inc in paired_remove:
                    incidents.pop(inc, None)
                    removed.add(inc)
                    rescind_snapshot.pop(inc, None)
                    if inc not in frozen_deferred and inc in deferred_order:
                        deferred_order.remove(inc)

        prev = incidents.get(incident)
        if op == "amend" and "delta" not in ruling:
            delta = 0
        else:
            delta = int(ruling["delta"])

        if op == "amend" and "correct_delta" not in ruling:
            correct_delta = 0
        else:
            correct_delta = int(ruling.get("correct_delta", 0))

        if op == "amend" and "paired_incident" not in ruling:
            paired_incident = None
        elif paired is not None:
            paired_incident = paired
        elif prev is not None:
            paired_incident = prev.get("paired_incident")
        else:
            paired_incident = None

        if op == "amend" and "applies_after_floor" not in ruling:
            applies_after_floor = False
        else:
            applies_after_floor = bool(ruling.get("applies_after_floor", False))

        if op == "amend" and "player" not in ruling and prev is not None:
            player = prev["player"]
        else:
            player = ruling["player"]

        if op == "amend" and "score_ceiling" not in ruling:
            score_ceiling = None
        elif "score_ceiling" in ruling:
            score_ceiling = int(ruling["score_ceiling"])
        else:
            score_ceiling = None

        if op == "amend" and "max_score_after" not in ruling:
            max_score_after = None
        elif "max_score_after" in ruling:
            max_score_after = int(ruling["max_score_after"])
        else:
            max_score_after = None

        offset_player = ruling.get("offset_player")
        if op == "amend" and "offset_player" not in ruling:
            offset_player = None
        if offset_player and (
            offset_player not in by_player or offset_player == player
        ):
            continue

        offset_correct_player = ruling.get("offset_correct_player")
        if op == "amend" and "offset_correct_player" not in ruling:
            offset_correct_player = None
        if offset_correct_player and (
            offset_correct_player not in by_player
            or offset_correct_player == player
        ):
            continue

        if op == "amend" and "correct_ceiling" not in ruling:
            correct_ceiling = None
        elif "correct_ceiling" in ruling:
            correct_ceiling = int(ruling["correct_ceiling"])
        else:
            correct_ceiling = None

        if op == "amend" and "offset_min_score" not in ruling:
            offset_min_score = None
        elif "offset_min_score" in ruling:
            offset_min_score = int(ruling["offset_min_score"])
        else:
            offset_min_score = None

        entry = {
            "player": player,
            "delta": delta,
            "correct_delta": correct_delta,
            "applies_after_floor": applies_after_floor,
            "requires_incident": requires,
            "paired_incident": paired_incident,
            "score_ceiling": score_ceiling,
            "max_score_after": max_score_after,
            "offset_player": offset_player,
            "offset_correct_player": offset_correct_player,
            "correct_ceiling": correct_ceiling,
            "offset_min_score": offset_min_score,
            "ruling_seq": ruling["ruling_seq"],
        }
        incidents[incident] = entry
        if op == "amend" and incident in frozen_deferred and paired_incident:
            frozen_deferred[incident] = dict(entry)
        elif applies_after_floor:
            if incident in deferred_order:
                deferred_order.remove(incident)
            deferred_order.append(incident)
            if paired_incident and paired_incident in incidents:
                frozen_deferred[incident] = dict(entry)
            else:
                frozen_deferred.pop(incident, None)
        else:
            frozen_deferred.pop(incident, None)
            if incident in deferred_order:
                deferred_order.remove(incident)
            for inc, snap in list(frozen_deferred.items()):
                if snap.get("paired_incident") == incident:
                    frozen_deferred.pop(inc, None)

    def dependency_chain_active(requires: str | None) -> bool:
        """H-2026-14/H-2026-16: every requires_incident link must survive at replay end."""
        seen: set[str] = set()
        current = requires
        while current:
            if current in seen:
                return False
            seen.add(current)
            if current not in incidents or current in ever_rescinded:
                return False
            current = incidents[current].get("requires_incident")
        return True

    def apply_offset_transfer(offset: str, transfer: int) -> None:
        """H-2026-32: cap positive offset debits at the payer's current balance."""
        if offset not in by_player:
            return
        if transfer > 0:
            transfer = min(transfer, max(0, by_player[offset]["score"]))
        by_player[offset]["score"] -= transfer

    def apply_correct_offset_transfer(offset: str, transfer: int) -> int:
        """H-2026-39: cap positive correct debits; return the amount subtracted."""
        if offset not in by_player:
            return 0
        debit = transfer
        if debit > 0:
            debit = min(debit, max(0, by_player[offset]["correct"]))
        by_player[offset]["correct"] -= debit
        return debit

    def apply_primary(eff: dict) -> None:
        player = eff["player"]
        if player not in by_player:
            return
        before = by_player[player]["score"]
        by_player[player]["score"] += eff["delta"]
        correct_before = by_player[player]["correct"]
        by_player[player]["correct"] += eff["correct_delta"]
        correct_applied = by_player[player]["correct"] - correct_before
        applied = by_player[player]["score"] - before
        cap = eff.get("max_score_after")
        if cap is not None and by_player[player]["score"] > cap:
            by_player[player]["score"] = cap
            applied = cap - before
        offset = eff.get("offset_player")
        if offset and offset in by_player:
            score_before_floor = by_player[player]["score"]
            threshold = eff.get("offset_min_score")
            if threshold is not None and score_before_floor < threshold:
                transfer = applied // 2
            else:
                transfer = applied
            apply_offset_transfer(offset, transfer)
        offset_correct = eff.get("offset_correct_player")
        if offset_correct and offset_correct in by_player and correct_applied != 0:
            apply_correct_offset_transfer(offset_correct, correct_applied)

    def apply_deferred(eff: dict) -> None:
        player = eff["player"]
        if player not in by_player:
            return
        delta = eff["delta"]
        offset = eff.get("offset_player")
        ceiling = eff.get("score_ceiling")
        correct_ceiling = eff.get("correct_ceiling")
        offset_debit = 0
        if offset and offset in by_player:
            transfer = delta
            threshold = eff.get("offset_min_score")
            if threshold is not None and by_player[player]["score"] < threshold:
                transfer = delta // 2
            before_offset = by_player[offset]["score"]
            apply_offset_transfer(offset, transfer)
            offset_debit = before_offset - by_player[offset]["score"]
        if ceiling is not None:
            headroom = ceiling - by_player[player]["score"]
            score_applied = 0 if headroom <= 0 else min(delta, headroom)
        else:
            score_applied = delta
        by_player[player]["score"] += score_applied
        if (
            ceiling is not None
            and score_applied == 0
            and delta != 0
            and offset
            and offset_debit > 0
        ):
            by_player[offset]["score"] += offset_debit
        correct_before = by_player[player]["correct"]
        correct_delta = eff["correct_delta"]
        score_blocked_correct = False
        if ceiling is not None and correct_ceiling is not None and score_applied == 0:
            correct_delta = 0
            score_blocked_correct = True
        elif correct_ceiling is not None:
            headroom = correct_ceiling - by_player[player]["correct"]
            correct_delta = 0 if headroom <= 0 else min(correct_delta, headroom)
        by_player[player]["correct"] += correct_delta
        correct_applied = by_player[player]["correct"] - correct_before
        offset_correct = eff.get("offset_correct_player")
        correct_offset_debit = 0
        if offset_correct and offset_correct in by_player and correct_applied != 0:
            correct_offset_debit = apply_correct_offset_transfer(
                offset_correct, correct_applied
            )
        if score_blocked_correct and offset_correct and correct_offset_debit > 0:
            by_player[offset_correct]["correct"] += correct_offset_debit

    def clamp_scores() -> None:
        for row in by_player.values():
            row["score"] = max(0, row["score"])
            row["correct"] = max(0, row["correct"])

    def clamp_player(player: str) -> None:
        if player in by_player:
            by_player[player]["score"] = max(0, by_player[player]["score"])
            by_player[player]["correct"] = max(0, by_player[player]["correct"])

    primaries = sorted(
        (
            eff
            for eff in incidents.values()
            if not eff["applies_after_floor"]
            and dependency_chain_active(eff.get("requires_incident"))
            and (
                not eff.get("paired_incident")
                or eff["paired_incident"] not in ever_rescinded
            )
        ),
        key=lambda eff: eff["ruling_seq"],
    )
    for eff in primaries:
        apply_primary(eff)
        clamp_player(eff["player"])
        offset = eff.get("offset_player")
        if offset:
            clamp_player(offset)
        offset_correct = eff.get("offset_correct_player")
        if offset_correct:
            clamp_player(offset_correct)

    clamp_scores()

    for incident in sorted(
        set(deferred_order) | set(frozen_deferred.keys()),
        key=lambda inc: (
            frozen_deferred[inc]["ruling_seq"]
            if inc in frozen_deferred
            else incidents[inc]["ruling_seq"]
        ),
    ):
        eff = frozen_deferred.get(incident) or incidents.get(incident)
        if not eff:
            continue
        apply_deferred(eff)
        player = eff["player"]
        if player in by_player:
            by_player[player]["score"] = max(0, by_player[player]["score"])
            by_player[player]["correct"] = max(0, by_player[player]["correct"])
        offset = eff.get("offset_player")
        if offset:
            clamp_player(offset)
        offset_correct = eff.get("offset_correct_player")
        if offset_correct:
            clamp_player(offset_correct)

    ordered = sorted(
        by_player.values(),
        key=lambda r: (
            -r["score"],
            -r["correct"],
            r["first_buzz_seq"] if r["first_buzz_seq"] is not None else 10**9,
            r["player"],
        ),
    )
    for idx, row in enumerate(ordered, start=1):
        row["rank"] = idx
    return ordered


def expected_standings(rows: list[dict] | None = None) -> list[dict]:
    """Official standings: provisional reference reconciled with the rulings feed."""
    ledger = rows if rows is not None else load_ledger_rows()
    return reconcile_rulings(simulate_standings(ledger), load_rulings())


def expected_transcript(rows: list[dict] | None = None) -> str:
    """Build the canonical official transcript from the hidden reference."""
    return format_transcript(expected_standings(rows))


def run_worker(ledger: Path = LEDGER, output: Path = OUTPUT) -> subprocess.CompletedProcess:
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists():
        output.unlink()
    return subprocess.run(
        [
            "python3",
            str(WORKER),
            "--ledger",
            str(ledger),
            "--api",
            REF_API,
            "--output",
            str(output),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
