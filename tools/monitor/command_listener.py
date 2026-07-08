#!/usr/bin/env python3
"""Poll Telegram and ntfy for monitor control commands (start / stop / status / run)."""

from __future__ import annotations

import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

MONITOR_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(MONITOR_DIR))

from command_parser import parse_command  # noqa: E402
from monitor_env import load_env_file  # noqa: E402
from ntfy_commands import fetch_ntfy_commands, ntfy_enabled, reply_ntfy  # noqa: E402
from telegram_commands import cmd_enabled as telegram_cmd_enabled  # noqa: E402
from telegram_commands import fetch_telegram_commands, reply_telegram  # noqa: E402
from terminus_control import REPO_ROOT, STATE_DIR, handle_command_text, log  # noqa: E402

LISTENER_STATE_FILE = STATE_DIR / "command-listener-state.json"


def load_listener_state() -> dict:
    if LISTENER_STATE_FILE.is_file():
        try:
            return json.loads(LISTENER_STATE_FILE.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            pass
    return {}


def save_listener_state(state: dict) -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    LISTENER_STATE_FILE.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")


def reply(text: str) -> None:
    telegram_ok = reply_telegram(text)
    ntfy_ok = reply_ntfy(text) if ntfy_enabled() else False
    if not telegram_ok and not ntfy_ok:
        log(
            "WARN: command reply failed — set TELEGRAM_BOT_TOKEN + TELEGRAM_CHAT_ID "
            "or NTFY_TOPIC in tools/monitor/.env"
        )


def _record_command(state: dict, command: str, result: str, source: str) -> dict:
    state["last_command"] = {
        "command": command,
        "at": datetime.now(timezone.utc).isoformat(),
        "reply": result[:200],
        "source": source,
    }
    save_listener_state(state)
    return state


def poll_telegram(state: dict) -> dict:
    if not telegram_cmd_enabled():
        return state
    offset = int(state.get("telegram_update_offset") or 0)
    try:
        messages, next_offset = fetch_telegram_commands(offset)
    except RuntimeError as exc:
        log(f"WARN: Telegram poll: {exc}")
        return state
    if next_offset > offset:
        state["telegram_update_offset"] = next_offset
        save_listener_state(state)
    for update_id, body in messages:
        if not parse_command(body):
            continue
        log(f"command from Telegram: {body[:80]} (update {update_id})")
        result = handle_command_text(body)
        reply(result)
        state = _record_command(state, body[:40], result, "telegram")
    return state


def poll_ntfy(state: dict) -> dict:
    if not ntfy_enabled():
        return state
    since = str(state.get("ntfy_since_id") or "10m")
    try:
        messages = fetch_ntfy_commands(since)
    except RuntimeError as exc:
        log(f"WARN: ntfy poll: {exc}")
        return state
    for mid, body in messages:
        if not parse_command(body):
            continue
        log(f"command from ntfy: {body[:80]} (id {mid})")
        result = handle_command_text(body)
        reply(result)
        state["ntfy_since_id"] = mid
        state = _record_command(state, body[:40], result, "ntfy")
    return state


def poll_once(state: dict) -> dict:
    state = poll_telegram(state)
    state = poll_ntfy(state)
    return state


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Telegram/ntfy command listener")
    parser.add_argument("--once", action="store_true", help="Single poll (launchd uses long-running mode)")
    args = parser.parse_args()

    load_env_file()
    STATE_DIR.mkdir(parents=True, exist_ok=True)

    poll_sec = int(os.environ.get("COMMAND_POLL_SEC", os.environ.get("IMESSAGE_POLL_SEC", "20")))
    if not args.once:
        log(f"command listener started (poll every {poll_sec}s)")
        log(f"repo: {REPO_ROOT}")
        if telegram_cmd_enabled():
            log("Telegram: send help for commands")
        if ntfy_enabled():
            log("ntfy commands: stop | start | status | run")
        if not telegram_cmd_enabled() and not ntfy_enabled():
            log("WARN: no command channel enabled — set Telegram or NTFY_TOPIC in .env")

    state = load_listener_state()

    def run_poll() -> None:
        nonlocal state
        try:
            state = poll_once(state)
        except Exception as exc:
            log(f"ERROR poll loop: {exc}")

    if args.once:
        run_poll()
        return 0

    while True:
        run_poll()
        time.sleep(poll_sec)


if __name__ == "__main__":
    raise SystemExit(main())
