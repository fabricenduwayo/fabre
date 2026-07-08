"""Poll ntfy.sh for phone commands (status / stop / start / run)."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request


def ntfy_cmd_topic() -> str:
    return os.environ.get("NTFY_CMD_TOPIC", os.environ.get("NTFY_TOPIC", "")).strip()


def ntfy_enabled() -> bool:
    return bool(ntfy_cmd_topic()) and os.environ.get("NTFY_CMD_ENABLE", "1").strip().lower() in {
        "1",
        "true",
        "yes",
    }


def fetch_ntfy_commands(since_id: str) -> list[tuple[str, str]]:
    """Return (message_id, command_text) from ntfy topic since since_id."""
    topic = ntfy_cmd_topic()
    if not topic:
        return []
    server = os.environ.get("NTFY_SERVER", "https://ntfy.sh").strip().rstrip("/")
    since = since_id or "1m"
    url = f"{server}/{topic}/json?poll=1&since={since}"
    req = urllib.request.Request(url, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=35) as resp:
            body = resp.read().decode("utf-8", errors="replace")
    except (urllib.error.URLError, TimeoutError) as exc:
        raise RuntimeError(f"ntfy poll failed: {exc}") from exc

    out: list[tuple[str, str]] = []
    for line in body.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if event.get("event") != "message":
            continue
        mid = str(event.get("id", ""))
        msg = str(event.get("message", "")).strip()
        if mid and msg:
            out.append((mid, msg))
    return out


def reply_ntfy(text: str) -> bool:
    topic = ntfy_cmd_topic()
    if not topic:
        return False
    server = os.environ.get("NTFY_SERVER", "https://ntfy.sh").strip().rstrip("/")
    url = f"{server}/{topic}"
    body = f"Terminus: {text}"[:3800].encode()
    req = urllib.request.Request(
        url,
        data=body,
        headers={"Title": "Terminus", "Tags": "snorkel"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return 200 <= resp.status < 300
    except (urllib.error.URLError, TimeoutError):
        return False
