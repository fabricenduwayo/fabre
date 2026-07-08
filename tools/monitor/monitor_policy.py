"""Pause, quiet hours, digest mode, cost guards, and per-run skip list."""

from __future__ import annotations

import os
import re
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

UTC = timezone.utc


def _env_bool(flag: str, default: str = "0") -> bool:
    return os.environ.get(flag, default).strip().lower() in {"1", "true", "yes", "on"}


def auto_agent_enabled() -> bool:
    """When false, scheduled runs scan/notify only — no Cursor agent unless you `run`."""
    return _env_bool("AUTO_AGENT_FIX", "0")


def digest_mode() -> bool:
    return _env_bool("NOTIFY_DIGEST", "1")


def priority_notify_only() -> bool:
    """Skip routine status pings; still send errors and resubmits."""
    return _env_bool("NOTIFY_PRIORITY_ONLY", "0")


def max_fixes_per_day() -> int:
    return int(os.environ.get("MAX_FIXES_PER_DAY", "12"))


def max_agent_minutes_per_day() -> int:
    return int(os.environ.get("MAX_AGENT_MINUTES_PER_DAY", "180"))


def local_tz() -> ZoneInfo:
    name = os.environ.get("MONITOR_TZ", "America/Chicago").strip()
    try:
        return ZoneInfo(name)
    except Exception:
        return ZoneInfo("UTC")


def is_quiet_hours() -> bool:
    if not _env_bool("NOTIFY_QUIET_HOURS", "0"):
        return False
    start = int(os.environ.get("NOTIFY_QUIET_START_HOUR", "23"))
    end = int(os.environ.get("NOTIFY_QUIET_END_HOUR", "7"))
    hour = datetime.now(local_tz()).hour
    if start <= end:
        return start <= hour < end
    return hour >= start or hour < end


def should_send_notification(event: str) -> bool:
    """Return False during quiet hours unless high priority."""
    if not is_quiet_hours():
        return True
    return event in {
        "error",
        "fix_failed",
        "daily_summary",
        "state_alert",
        "difficulty_alert",
        "git_warning",
    }


def is_priority_event(event: str) -> bool:
    return event in {
        "error",
        "fix_failed",
        "resubmitted",
        "waiting_docker",
        "daily_summary",
        "state_alert",
        "difficulty_alert",
        "git_warning",
        "run_complete",
    }


def should_notify_event(event: str) -> bool:
    if priority_notify_only() and not is_priority_event(event):
        return False
    return should_send_notification(event)


def parse_pause_duration(text: str) -> int | None:
    """Parse '6h', '30m', '2 hours', '90 minutes' into seconds."""
    text = text.strip().lower()
    if not text:
        return None
    m = re.fullmatch(r"(\d+)\s*(h|hr|hrs|hour|hours|m|min|mins|minute|minutes)", text)
    if not m:
        return None
    value = int(m.group(1))
    unit = m.group(2)
    if unit.startswith("h"):
        return value * 3600
    return value * 60


def is_paused(state: dict) -> bool:
    until = state.get("paused_until")
    if not until:
        return False
    try:
        deadline = datetime.fromisoformat(until.replace("Z", "+00:00"))
    except ValueError:
        return False
    return datetime.now(UTC) < deadline


def pause_remaining_sec(state: dict) -> int:
    until = state.get("paused_until")
    if not until:
        return 0
    try:
        deadline = datetime.fromisoformat(until.replace("Z", "+00:00"))
    except ValueError:
        return 0
    return max(0, int((deadline - datetime.now(UTC)).total_seconds()))


def set_pause(state: dict, seconds: int) -> str:
    until = datetime.now(UTC) + timedelta(seconds=seconds)
    state["paused_until"] = until.isoformat()
    if seconds >= 3600:
        label = f"{seconds // 3600}h"
    else:
        label = f"{seconds // 60}m"
    return f"paused until {until.isoformat()} ({label})"


def clear_pause(state: dict) -> None:
    state.pop("paused_until", None)


def skip_once_folders(state: dict) -> set[str]:
    return set(state.get("skip_once_folders") or [])


def add_skip_once(state: dict, folder: str) -> None:
    folders = skip_once_folders(state)
    folders.add(folder)
    state["skip_once_folders"] = sorted(folders)


def clear_skip_once(state: dict, folder: str | None = None) -> None:
    if folder is None:
        state.pop("skip_once_folders", None)
        return
    folders = skip_once_folders(state)
    folders.discard(folder)
    state["skip_once_folders"] = sorted(folders)


def _today_key() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%d")


def daily_stats(state: dict) -> dict:
    stats = dict(state.get("daily_stats") or {})
    key = _today_key()
    if stats.get("date") != key:
        return {
            "date": key,
            "fixes": 0,
            "agent_minutes": 0,
            "events": [],
        }
    return stats


def save_daily_stats(state: dict, stats: dict) -> None:
    state["daily_stats"] = stats


def can_run_agent_today(state: dict) -> tuple[bool, str]:
    stats = daily_stats(state)
    if stats["fixes"] >= max_fixes_per_day():
        return False, f"daily fix cap ({max_fixes_per_day()}) reached"
    if stats["agent_minutes"] >= max_agent_minutes_per_day():
        return False, f"daily agent minute cap ({max_agent_minutes_per_day()}m) reached"
    return True, ""


def record_fix(state: dict, folder: str, *, agent_minutes: float = 0) -> None:
    stats = daily_stats(state)
    stats["fixes"] = int(stats.get("fixes", 0)) + 1
    stats["agent_minutes"] = round(float(stats.get("agent_minutes", 0)) + agent_minutes, 1)
    events: list[dict] = list(stats.get("events") or [])
    events.append(
        {
            "at": datetime.now(UTC).isoformat(),
            "type": "fix",
            "folder": folder,
            "agent_minutes": agent_minutes,
        }
    )
    stats["events"] = events[-200:]
    save_daily_stats(state, stats)


def record_daily_event(state: dict, event_type: str, **fields: str) -> None:
    stats = daily_stats(state)
    events: list[dict] = list(stats.get("events") or [])
    events.append({"at": datetime.now(UTC).isoformat(), "type": event_type, **fields})
    stats["events"] = events[-200:]
    save_daily_stats(state, stats)


def last_summary_date(state: dict) -> str | None:
    return state.get("last_daily_summary_date")


def mark_daily_summary_sent(state: dict) -> None:
    state["last_daily_summary_date"] = _today_key()
