"""Digest notifications and event-aware notify wrapper."""

from __future__ import annotations

from monitor_policy import digest_mode, should_notify_event


class DigestCollector:
    """Collect lines during a monitor run; flush as one Telegram message."""

    def __init__(self) -> None:
        self._lines: list[str] = []

    def add(self, title: str, message: str = "", *, subtitle: str = "") -> None:
        parts = [title]
        if subtitle:
            parts.append(subtitle)
        if message:
            parts.append(message)
        self._lines.append("\n".join(parts))

    @property
    def lines(self) -> list[str]:
        return list(self._lines)

    def flush_text(self) -> str:
        return "\n\n---\n\n".join(self._lines)


_active: DigestCollector | None = None


def begin_digest() -> DigestCollector | None:
    global _active
    if not digest_mode():
        _active = None
        return None
    _active = DigestCollector()
    return _active


def get_digest() -> DigestCollector | None:
    return _active


def digest_add(title: str, message: str = "", *, subtitle: str = "") -> None:
    if _active is not None:
        _active.add(title, message, subtitle=subtitle)


def end_digest() -> str:
    global _active
    if _active is None:
        return ""
    text = _active.flush_text()
    _active = None
    return text


def notify_event(
    event: str,
    title: str,
    message: str = "",
    *,
    subtitle: str = "",
    slack: str | None = None,
    force: bool = False,
) -> None:
    """Route to digest buffer or immediate notify_all based on policy."""
    from notifications import notify_all

    if not force and not should_notify_event(event):
        return
    if _active is not None and event not in {"error", "fix_failed", "daily_summary"}:
        digest_add(title, message, subtitle=subtitle)
        return
    notify_all(title, message, subtitle=subtitle, slack=slack)
