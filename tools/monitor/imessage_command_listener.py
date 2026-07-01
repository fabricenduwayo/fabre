#!/usr/bin/env python3
"""Poll iMessage for control commands (start-terminus, stop-terminus, etc.).

Reads ~/Library/Messages/chat.db (read-only). Requires Full Disk Access for the
Python binary or run-imessage-listener.sh in System Settings → Privacy.
"""

from __future__ import annotations

import json
import os
import re
import sqlite3
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

MONITOR_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(MONITOR_DIR))

from messages_applescript import fetch_recent_messages_lines  # noqa: E402
from notifications import notify_imessage  # noqa: E402
from ntfy_commands import fetch_ntfy_commands, ntfy_enabled, reply_ntfy  # noqa: E402
from terminus_control import (  # noqa: E402
    REPO_ROOT,
    STATE_DIR,
    handle_command,
    load_env_file,
    log,
)

LISTENER_STATE_FILE = STATE_DIR / "imessage-listener-state.json"
CHAT_DB = Path.home() / "Library" / "Messages" / "chat.db"
CHAT_DB_COPY = Path("/tmp/snorkel-messages-chat.db")

COMMAND_ALIASES = {
    "startterminus": "start",
    "stopterminus": "stop",
    "statusterminus": "status",
    "runterminus": "run",
}


TYPEDSTREAM_NOISE = frozenset({
    "nsvalue",
    "nsobject",
    "nsstring",
    "nsdictionary",
    "nsnumber",
    "nsattributedstring",
    "streamtyped",
    "kimmessagepartattributename",
    "bterminus",
})


def _is_bot_reply_text(text: str) -> bool:
    lowered = text.lower()
    return (
        lowered.startswith("terminus:")
        or "terminus monitor" in lowered
        or "imessage listener" in lowered
        or "queue:" in lowered
        or "repair-express" in lowered
    )


def decode_message_text(text: str | None, attributed_body: bytes | None) -> str:
    if text and text.strip():
        body = text.strip()
        return "" if _is_bot_reply_text(body) else body
    if not attributed_body:
        return ""
    raw = attributed_body.decode("utf-8", errors="ignore")
    for alias in COMMAND_ALIASES:
        phrase = alias.replace("terminus", "-terminus")
        if phrase.replace("-", "") in re.sub(r"[^a-z0-9]", "", raw.lower()):
            return phrase

    words: list[str] = []
    for token in re.findall(r"[a-zA-Z][a-zA-Z0-9\-]{2,}", raw):
        wl = token.lower()
        if wl in TYPEDSTREAM_NOISE or wl.startswith("ns") or "kimmessage" in wl:
            continue
        words.append(token)

    if not words:
        return ""

    joined = " ".join(words).lower()
    if _is_bot_reply_text(joined):
        return ""

    lower_words = [w.lower() for w in words]
    for cmd in ("status", "start", "stop", "run"):
        if cmd in lower_words:
            return cmd
    for cmd, phrase in (
        ("status", "status-terminus"),
        ("start", "start-terminus"),
        ("stop", "stop-terminus"),
        ("run", "run-terminus"),
    ):
        if cmd in lower_words and "terminus" in lower_words:
            return phrase

    return words[0].lower()


def parse_command(body: str) -> str | None:
    if not body:
        return None
    lowered = body.lower().strip()
    compact = re.sub(r"[^a-z0-9]", "", lowered)
    if compact in {"status", "stop", "start", "run"}:
        return compact
    direct = COMMAND_ALIASES.get(compact)
    if direct:
        return direct
    for phrase, cmd in (
        ("start-terminus", "start"),
        ("stop-terminus", "stop"),
        ("status-terminus", "status"),
        ("run-terminus", "run"),
    ):
        if phrase.replace("-", "") in compact:
            return cmd
    return None


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


def init_last_rowid(conn: sqlite3.Connection) -> int:
    row = conn.execute("SELECT COALESCE(MAX(ROWID), 0) FROM message").fetchone()
    return int(row[0])


def fetch_new_messages(
    conn: sqlite3.Connection, after_rowid: int
) -> tuple[list[tuple[int, str]], int]:
    """Return ([(rowid, command), ...], max_rowid_scanned).

    Texts from your iPhone often sync as is_from_me=0 on the Mac.
    Always advance past bot replies and non-command rows.
    """
    rows = conn.execute(
        """
        SELECT ROWID, text, attributedBody, is_from_me
        FROM message
        WHERE ROWID > ?
        ORDER BY ROWID ASC
        LIMIT 30
        """,
        (after_rowid,),
    ).fetchall()

    out: list[tuple[int, str]] = []
    max_rowid = after_rowid
    for rowid, text, body, _is_from_me in rows:
        max_rowid = max(max_rowid, int(rowid))
        body_text = decode_message_text(text, body)
        cmd = parse_command(body_text)
        if cmd:
            out.append((int(rowid), cmd))
    return out, max_rowid


def open_chat_db() -> sqlite3.Connection:
    override = os.environ.get("SNORKEL_CHAT_DB", "").strip()
    if override:
        db_path = Path(override)
    elif CHAT_DB_COPY.is_file():
        db_path = CHAT_DB_COPY
    else:
        db_path = CHAT_DB
    if not db_path.is_file():
        raise FileNotFoundError(f"Messages database not found: {db_path}")
    uri = f"file:{db_path}?mode=ro"
    return sqlite3.connect(uri, uri=True, timeout=2.0)


def reply(text: str) -> None:
    imessage_ok = notify_imessage(f"Terminus: {text}"[:900])
    ntfy_ok = reply_ntfy(text) if ntfy_enabled() else False
    if not imessage_ok and not ntfy_ok:
        log(
            "WARN: reply failed — iMessage needs Automation; "
            "or set NTFY_CMD_TOPIC in .env and use ntfy app"
        )


def fetch_new_commands_applescript(seen_ids: set[str]) -> list[tuple[str, str]]:
    """Return (message_id, command) for new outgoing command messages."""
    out: list[tuple[str, str]] = []
    try:
        messages = fetch_recent_messages_lines()
    except RuntimeError as exc:
        log(f"WARN: AppleScript Messages read failed: {exc}")
        return out
    for mid, body in messages:
        if mid in seen_ids:
            continue
        cmd = parse_command(body)
        if cmd:
            out.append((mid, cmd))
    out.sort(key=lambda x: x[0])
    return out


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
        command = parse_command(body)
        if not command:
            continue
        log(f"command from ntfy: {command} (id {mid})")
        result = handle_command(command)
        reply(result)
        state["ntfy_since_id"] = mid
        state["last_command"] = {
            "command": command,
            "at": datetime.now(timezone.utc).isoformat(),
            "reply": result[:200],
            "source": "ntfy",
        }
        save_listener_state(state)
    return state


def poll_once(state: dict) -> dict:
    state = poll_ntfy(state)

    use_applescript = os.environ.get("SNORKEL_MSG_SOURCE", "chatdb").strip().lower() == "applescript"
    if os.environ.get("SNORKEL_MSG_SOURCE", "").strip().lower() == "none":
        return state
    if use_applescript:
        seen = set(state.get("seen_message_ids") or [])
        if state.get("initialized") is not True:
            try:
                for mid, _body in fetch_recent_messages_lines():
                    seen.add(mid)
            except RuntimeError as exc:
                log(f"WARN: AppleScript init failed: {exc}")
                return state
            state["initialized"] = True
            state["seen_message_ids"] = sorted(seen)[-500:]
            log(f"listener ready (AppleScript) — ignoring {len(seen)} existing messages")
            save_listener_state(state)
            return state

        for mid, command in fetch_new_commands_applescript(seen):
            log(f"command from iMessage: {command} (id {mid})")
            result = handle_command(command)
            reply(result)
            seen.add(mid)
            state["seen_message_ids"] = sorted(seen)[-500:]
            state["last_command"] = {
                "command": command,
                "at": datetime.now(timezone.utc).isoformat(),
                "reply": result[:200],
            }
            save_listener_state(state)
        return state

    try:
        conn = open_chat_db()
    except sqlite3.OperationalError as exc:
        if "authorization denied" in str(exc).lower() or "unable to open" in str(exc).lower():
            log(
                "WARN: cannot read chat.db — ensure SnorkelTerminusListener.app "
                "has Full Disk Access and restart the listener"
            )
        else:
            log(f"WARN: chat.db error: {exc}")
        return state
    except FileNotFoundError as exc:
        log(f"WARN: {exc}")
        return state

    try:
        last_rowid = int(state.get("last_rowid", 0))
        if state.get("initialized") is not True:
            last_rowid = init_last_rowid(conn)
            state["initialized"] = True
            state["last_rowid"] = last_rowid
            log(f"listener ready — ignoring history up to message ROWID {last_rowid}")
            save_listener_state(state)
            return state

        commands, max_rowid = fetch_new_messages(conn, last_rowid)
        if max_rowid > last_rowid:
            state["last_rowid"] = max_rowid
            save_listener_state(state)

        cooldown = int(os.environ.get("IMESSAGE_CMD_COOLDOWN_SEC", "8"))
        last_cmd = state.get("last_command") or {}
        last_cmd_at = last_cmd.get("at", "")

        for rowid, command in commands:
            if last_cmd.get("command") == command and last_cmd_at:
                try:
                    prev = datetime.fromisoformat(last_cmd_at.replace("Z", "+00:00"))
                    if (datetime.now(timezone.utc) - prev).total_seconds() < cooldown:
                        log(f"skip duplicate {command} (ROWID {rowid}) — cooldown {cooldown}s")
                        continue
                except ValueError:
                    pass
            log(f"command from iMessage: {command} (ROWID {rowid})")
            result = handle_command(command)
            reply(result)
            state["last_rowid"] = rowid
            state["last_command"] = {
                "command": command,
                "at": datetime.now(timezone.utc).isoformat(),
                "reply": result[:200],
            }
            save_listener_state(state)
            last_cmd = state["last_command"]
            last_cmd_at = last_cmd["at"]
    finally:
        conn.close()

    return state


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="iMessage command listener")
    parser.add_argument("--once", action="store_true", help="Single poll (used by .app wrapper)")
    args = parser.parse_args()

    load_env_file()
    STATE_DIR.mkdir(parents=True, exist_ok=True)

    poll_sec = int(os.environ.get("IMESSAGE_POLL_SEC", "20"))
    if not args.once:
        log(f"iMessage command listener started (poll every {poll_sec}s)")
        log(f"repo: {REPO_ROOT}")
        log("text yourself: status | stop | start | run  (run = Cursor fix now)")

        if not os.environ.get("IMESSAGE_TO", "").strip():
            log("WARN: IMESSAGE_TO not set in .env — replies will not send")

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
