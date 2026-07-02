#!/usr/bin/env python3
"""Broken Harbor trivia replay worker (staging default)."""

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
    rows.sort(key=lambda r: r["ts"])
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
    """Naive ruling replay — ignores Appendix H lifecycle controls."""
    by_player = {row["player"]: dict(row) for row in standings}

    for ruling in sorted(rulings, key=lambda r: r["ruling_seq"]):
        if ruling["op"] == "rescind":
            continue
        if ruling["op"] not in ("issue", "amend"):
            continue
        player = ruling.get("player")
        if not player or player not in by_player:
            continue
        by_player[player]["score"] += int(ruling.get("delta", 0))
        by_player[player]["correct"] += int(ruling.get("correct_delta", 0))

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
