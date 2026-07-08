"""Parse remote control commands (Telegram / ntfy)."""

from __future__ import annotations

import re
from dataclasses import dataclass

COMMAND_ALIASES = {
    "startterminus": "start",
    "stopterminus": "stop",
    "statusterminus": "status",
    "runterminus": "run",
    "dryrunterminus": "dry-run",
    "queueterminus": "queue",
}


@dataclass(frozen=True)
class ParsedCommand:
    action: str
    args: list[str]


def _split_command(body: str) -> tuple[str, list[str]]:
    body = body.strip()
    if not body:
        return "", []
    parts = body.split()
    return parts[0].lower(), parts[1:]


def parse_command(body: str) -> ParsedCommand | None:
    if not body:
        return None
    lowered = body.lower().strip()
    compact = re.sub(r"[^a-z0-9]", "", lowered)

    for phrase, cmd in (
        ("start-terminus", "start"),
        ("stop-terminus", "stop"),
        ("status-terminus", "status"),
        ("run-terminus", "run"),
        ("dry-run-terminus", "dry-run"),
    ):
        if phrase.replace("-", "") in compact:
            return ParsedCommand(cmd, [])

    direct = COMMAND_ALIASES.get(compact)
    if direct:
        return ParsedCommand(direct, [])

    verb, args = _split_command(body)
    if verb in {
        "start",
        "stop",
        "status",
        "run",
        "dry-run",
        "dryrun",
        "queue",
        "docker",
        "resume",
        "summary",
        "help",
        "exclude",
        "unexclude",
        "reset",
        "skip",
        "ui",
        "draft",
        "health",
    }:
        if verb == "dryrun":
            verb = "dry-run"
        return ParsedCommand(verb, args)

    if verb == "pause":
        duration = " ".join(args) if args else ""
        return ParsedCommand("pause", [duration] if duration else [])

    if compact in {"status", "stop", "start", "run", "help", "queue", "docker", "resume", "summary"}:
        return ParsedCommand(compact, [])

    return None


def help_text() -> str:
    return """Commands:
status | queue | health | docker | summary
start | stop | resume
run [task-folder]
dry-run [task-folder]
pause 6h | pause 30m
exclude <task> | unexclude <task>
reset <task> | skip <task>
ui <task> | draft <task>
help"""
