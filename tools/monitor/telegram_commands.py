"""Telegram Bot API helpers for monitor notifications and remote commands."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request


def _enabled(flag: str, default: str = "1") -> bool:
    return os.environ.get(flag, default).strip().lower() in {"1", "true", "yes", "on"}


def bot_token() -> str:
    return os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()


def chat_id() -> str:
    return os.environ.get("TELEGRAM_CHAT_ID", "").strip()


def notify_enabled() -> bool:
    return bool(bot_token() and chat_id()) and _enabled("NOTIFY_TELEGRAM", "0")


def cmd_enabled() -> bool:
    return notify_enabled() and _enabled("TELEGRAM_CMD_ENABLE", "1")


def _api_url(method: str) -> str:
    return f"https://api.telegram.org/bot{bot_token()}/{method}"


def _post_json(method: str, payload: dict) -> dict:
    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        _api_url(method),
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = json.loads(resp.read().decode("utf-8", errors="replace"))
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"Telegram API {method} failed: {exc}") from exc
    if not body.get("ok"):
        raise RuntimeError(f"Telegram API {method} error: {body.get('description', body)}")
    return body


def send_telegram(text: str, *, parse_mode: str | None = None) -> bool:
    if not notify_enabled():
        return False
    payload: dict = {
        "chat_id": chat_id(),
        "text": text[:4096],
        "disable_web_page_preview": True,
    }
    if parse_mode:
        payload["parse_mode"] = parse_mode
    try:
        _post_json("sendMessage", payload)
        return True
    except RuntimeError:
        return False


def reply_telegram(text: str) -> bool:
    return send_telegram(f"Terminus: {text}"[:4096])


def _allowed_user_ids() -> set[str]:
    raw = os.environ.get("TELEGRAM_ALLOWED_USER_IDS", "").strip()
    if not raw:
        return set()
    return {part.strip() for part in raw.split(",") if part.strip()}


def fetch_telegram_commands(offset: int) -> tuple[list[tuple[int, str]], int]:
    """Return ([(update_id, command_text), ...], next_offset)."""
    if not cmd_enabled():
        return [], offset
    params = urllib.parse.urlencode(
        {
            "timeout": "0",
            "offset": str(offset) if offset else "",
            "allowed_updates": json.dumps(["message"]),
        }
    )
    url = f"{_api_url('getUpdates')}?{params}"
    req = urllib.request.Request(url, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=35) as resp:
            body = json.loads(resp.read().decode("utf-8", errors="replace"))
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"Telegram getUpdates failed: {exc}") from exc

    if not body.get("ok"):
        raise RuntimeError(f"Telegram getUpdates error: {body.get('description', body)}")

    allowed_users = _allowed_user_ids()
    target_chat = chat_id()
    out: list[tuple[int, str]] = []
    next_offset = offset
    for update in body.get("result") or []:
        update_id = int(update.get("update_id", 0))
        next_offset = max(next_offset, update_id + 1)
        message = update.get("message") or {}
        msg_chat = str((message.get("chat") or {}).get("id", ""))
        if msg_chat != target_chat:
            continue
        user = message.get("from") or {}
        user_id = str(user.get("id", ""))
        if allowed_users and user_id not in allowed_users:
            continue
        text = str(message.get("text") or "").strip()
        if text:
            out.append((update_id, text))
    return out, next_offset
