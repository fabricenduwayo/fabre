"""Notification helpers for the submission monitor.

Channels: macOS banners, Telegram, ntfy push, Slack.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from telegram_commands import send_telegram

UTC = timezone.utc


def _enabled(flag: str, default: str = "1") -> bool:
    return os.environ.get(flag, default).strip().lower() in {"1", "true", "yes", "on"}


def _escape_applescript(text: str) -> str:
    return text.replace("\\", "\\\\").replace('"', '\\"')


def notify_macos(title: str, message: str, *, subtitle: str = "") -> bool:
    """Show a native macOS notification via osascript (can trigger TCC prompts).

    Disabled by default — use Telegram/ntfy instead to avoid macOS privacy dialogs.
    """
    if not _enabled("NOTIFY_MACOS", "0"):
        return False
    title_e = _escape_applescript(title[:120])
    msg_e = _escape_applescript(message[:250])
    if subtitle:
        script = (
            f'display notification "{msg_e}" with title "{title_e}" '
            f'subtitle "{_escape_applescript(subtitle[:120])}"'
        )
    else:
        script = f'display notification "{msg_e}" with title "{title_e}"'
    proc = subprocess.run(["osascript", "-e", script], capture_output=True, check=False)
    return proc.returncode == 0


def notify_slack(text: str) -> bool:
    """Post a message to Slack via incoming webhook (optional)."""
    webhook = os.environ.get("SLACK_WEBHOOK_URL", "").strip()
    if not webhook or not _enabled("NOTIFY_SLACK", "0"):
        return False
    payload = json.dumps({"text": text}).encode()
    req = urllib.request.Request(
        webhook,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return 200 <= resp.status < 300
    except (urllib.error.URLError, TimeoutError):
        return False


def notify_telegram(title: str, message: str) -> bool:
    """Send a Telegram message to TELEGRAM_CHAT_ID."""
    if not _enabled("NOTIFY_TELEGRAM", "0"):
        return False
    if message:
        body = message if not title or message.startswith(title) else f"{title}\n{message}"
    else:
        body = title
    return send_telegram(body[:4096])


def notify_ntfy(title: str, message: str) -> bool:
    """Push to phone via ntfy.sh (install the ntfy app and subscribe to NTFY_TOPIC)."""
    topic = os.environ.get("NTFY_TOPIC", "").strip()
    if not topic or not _enabled("NOTIFY_NTFY", "0"):
        return False
    server = os.environ.get("NTFY_SERVER", "https://ntfy.sh").strip().rstrip("/")
    url = f"{server}/{topic}"
    body = f"{title}\n{message}"[:3800].encode()
    headers = {
        "Title": title[:200],
        "Priority": os.environ.get("NTFY_PRIORITY", "default"),
        "Tags": "snorkel,robot",
    }
    req = urllib.request.Request(url, data=body, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return 200 <= resp.status < 300
    except (urllib.error.URLError, TimeoutError):
        return False


def notify_all(
    title: str,
    message: str,
    *,
    subtitle: str = "",
    slack: str | None = None,
    phone: str | None = None,
) -> None:
    notify_macos(title, message, subtitle=subtitle)

    phone_text = phone
    if not phone_text:
        parts = [title]
        if subtitle:
            parts.append(subtitle)
        if message:
            parts.append(message)
        phone_text = "\n".join(parts)

    notify_telegram(title, phone_text)
    notify_ntfy(title, phone_text)

    if slack:
        notify_slack(slack)
    elif _enabled("NOTIFY_SLACK", "0"):
        body = f"*{title}*"
        if subtitle:
            body += f"\n_{subtitle}_"
        body += f"\n{message}"
        notify_slack(body)


def parse_agent_report(text: str) -> dict:
    """Extract MONITOR_REPORT_JSON from agent output if present."""
    if not text:
        return {}
    match = re.search(r"```json\s*(\{.*?\})\s*```", text, re.DOTALL | re.IGNORECASE)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass
    match = re.search(
        r'\{[^{}]*"changes_summary"[^{}]*\}',
        text,
        re.DOTALL,
    )
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass
    return {}


def git_diff_stat(repo_root: Path, folder_name: str) -> str:
    """Summarize uncommitted changes in a task folder."""
    task = repo_root / folder_name
    if not task.is_dir():
        return "(task folder not found)"
    proc = subprocess.run(
        ["git", "-C", str(repo_root), "diff", "--stat", "--", folder_name],
        capture_output=True,
        text=True,
        check=False,
    )
    stat = proc.stdout.strip()
    if stat:
        return stat[:800]
    proc = subprocess.run(
        ["git", "-C", str(repo_root), "status", "--short", "--", folder_name],
        capture_output=True,
        text=True,
        check=False,
    )
    status = proc.stdout.strip()
    return status[:800] if status else "(no git diff detected)"


def write_run_report(state_dir: Path, report: dict) -> Path:
    state_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    path = state_dir / f"run-report-{ts}.json"
    path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    latest = state_dir / "last-run-report.json"
    latest.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return path
