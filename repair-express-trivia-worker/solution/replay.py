#!/usr/bin/env python3
"""Harbor trivia replay worker."""

from __future__ import annotations

import argparse
import csv
import json
import time
import urllib.error
import urllib.request
from pathlib import Path

MATCH_ID = "match-night-2026-03-15"


def request_json(
    method: str,
    url: str,
    payload: dict | None = None,
    headers: dict | None = None,
) -> tuple[int, dict | None]:
    data = None
    hdrs = {"Content-Type": "application/json"}
    if headers:
        hdrs.update(headers)
    if payload is not None:
        data = json.dumps(payload).encode()
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


def load_rows(path: Path) -> list[dict]:
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
    rows.sort(key=lambda r: r["seq"])
    return rows


def ingest_with_retry(base_url: str, row: dict) -> None:
    url = base_url.rstrip("/") + "/v1/ingest"
    key = f"match-night-{row['seq']}"
    delay = 0.05
    while True:
        status, body = request_json("POST", url, row, {"X-Idempotency-Key": key})
        if status in (200, 201):
            return
        if status == 503:
            time.sleep(delay)
            delay = min(delay * 2, 0.8)
            continue
        if status == 422:
            return
        if status == 409:
            raise RuntimeError(f"idempotency conflict at seq {row['seq']}: {body}")
        raise RuntimeError(f"ingest failed for seq {row['seq']}: {status} {body}")


def fetch_standings(base_url: str) -> list[dict]:
    status, body = request_json("GET", base_url.rstrip("/") + "/v1/standings")
    if status != 200 or not body:
        raise RuntimeError(f"standings fetch failed: {status}")
    return body["standings"]


def fetch_rulings(base_url: str) -> list[dict]:
    status, body = request_json("GET", base_url.rstrip("/") + "/v1/rulings")
    if status != 200 or not body:
        raise RuntimeError(f"rulings fetch failed: {status}")
    return body["rulings"]


def reconcile(standings: list[dict], rulings: list[dict]) -> list[dict]:
    """Apply the stewards' review (Appendix H) and re-rank with TR-TIEBREAK."""
    by_player = {row["player"]: dict(row) for row in standings}

    incidents: dict[str, dict] = {}
    deferred_order: list[str] = []
    ever_rescinded: set[str] = set()
    frozen_deferred: dict[str, dict] = {}

    for ruling in sorted(rulings, key=lambda r: r["ruling_seq"]):
        op = ruling["op"]
        incident = ruling["incident"]

        if op == "rescind":
            removed: set[str] = set()
            if incident in incidents:
                incidents.pop(incident)
                removed.add(incident)
                ever_rescinded.add(incident)
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
                    if inc not in frozen_deferred and inc in deferred_order:
                        deferred_order.remove(inc)
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

        supersedes = ruling.get("supersedes_incident")
        if supersedes and supersedes in incidents:
            removed = {supersedes}
            incidents.pop(supersedes, None)
            if supersedes in deferred_order:
                deferred_order.remove(supersedes)
            frozen_deferred.pop(supersedes, None)
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

        entry = {
            "player": player,
            "delta": delta,
            "correct_delta": correct_delta,
            "applies_after_floor": applies_after_floor,
            "requires_incident": requires,
            "paired_incident": paired_incident,
            "ruling_seq": ruling["ruling_seq"],
        }
        incidents[incident] = entry
        if applies_after_floor:
            if incident in deferred_order:
                deferred_order.remove(incident)
            deferred_order.append(incident)
            if paired_incident and paired_incident in incidents:
                frozen_deferred[incident] = dict(entry)
        else:
            frozen_deferred.pop(incident, None)
            if incident in deferred_order:
                deferred_order.remove(incident)
            for inc, snap in list(frozen_deferred.items()):
                if snap.get("paired_incident") == incident:
                    frozen_deferred.pop(inc, None)

        if op == "amend" and incident in frozen_deferred:
            frozen_deferred[incident] = dict(entry)

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

    def apply_adjustment(eff: dict) -> None:
        player = eff["player"]
        if player not in by_player:
            return
        by_player[player]["score"] += eff["delta"]
        by_player[player]["correct"] += eff["correct_delta"]

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
        apply_adjustment(eff)
        clamp_player(eff["player"])

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
        apply_adjustment(eff)
        player = eff["player"]
        if player in by_player:
            by_player[player]["score"] = max(0, by_player[player]["score"])
            by_player[player]["correct"] = max(0, by_player[player]["correct"])

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


def render_transcript(standings: list[dict], out: Path) -> None:
    lines = [
        f"STANDINGS {MATCH_ID}",
        "rank player score correct first_buzz_seq",
    ]
    for row in standings:
        fb = row["first_buzz_seq"]
        fb_text = str(fb) if fb is not None else "-"
        lines.append(
            f"{row['rank']} {row['player']} {row['score']} {row['correct']} {fb_text}"
        )
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ledger", required=True)
    parser.add_argument("--api", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    rows = load_rows(Path(args.ledger))
    for row in rows:
        ingest_with_retry(args.api, row)

    provisional = fetch_standings(args.api)
    rulings = fetch_rulings(args.api)
    official = reconcile(provisional, rulings)
    render_transcript(official, Path(args.output))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
