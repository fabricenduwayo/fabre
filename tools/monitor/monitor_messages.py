"""Formatted Telegram / notification messages for monitor runs."""

from __future__ import annotations

from datetime import datetime, timezone

from monitor_health import health_report
from monitor_policy import auto_agent_enabled
from monitor_summary import summarize_issue_line

UTC = timezone.utc


def _ts() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%d %H:%M UTC")


def _state_counts(all_subs: list[dict]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for sub in all_subs:
        st = sub.get("assignment_state") or "?"
        counts[st] = counts.get(st, 0) + 1
    return counts


def build_run_report_message(
    *,
    all_subs: list[dict],
    fix_queue: list[dict],
    manual_ui: list[dict],
    skipped: list[dict],
    changes: list[str],
    fixed: int,
    oracle_skipped: list[tuple[str, str]],
    agent_blocked: str = "",
    dry_run: bool = False,
    errors: list[str] | None = None,
    remaining_queue: list[dict] | None = None,
    repo_root,
    state: dict,
) -> str:
    """One well-formatted message for the whole monitor run."""
    counts = _state_counts(all_subs)
    lines = [
        f"Snorkel Monitor — {_ts()}",
        "",
        "PLATFORM",
    ]
    for st in sorted(counts):
        lines.append(f"  {st}: {counts[st]}")

    needs_rev = [s for s in all_subs if s.get("assignment_state") == "NEEDS_REVISION"]
    if needs_rev:
        lines.extend(["", "NEEDS_REVISION TASKS"])
        queued_names = {i["folder_name"] for i in fix_queue}
        skipped_map = {
            (item.get("folder_name") or ""): item.get("reason", "?")
            for item in skipped
            if isinstance(item, dict)
        }
        notes_by_folder = {
            item["folder_name"]: item.get("feedback_notes") or ""
            for item in fix_queue + manual_ui
        }
        for sub in sorted(needs_rev, key=lambda s: (s.get("folder_name") or "")):
            folder = (sub.get("folder_name") or sub["submission_id"][:8]).strip()
            if folder in queued_names:
                marker = ">"
            elif folder in skipped_map:
                marker = "-"
            else:
                marker = " "
            lines.append(f"  {marker} {folder}")
            if folder in skipped_map:
                lines.append(f"      skipped: {skipped_map[folder]}")
            else:
                notes = notes_by_folder.get(folder, "")
                if notes:
                    lines.append(f"      {summarize_issue_line(notes)}")

    if skipped:
        lines.extend(["", "SKIPPED"])
        for item in skipped[:10]:
            if isinstance(item, dict):
                lines.append(
                    f"  - {item.get('folder_name', '?')}: {item.get('reason', '?')}"
                )

    if manual_ui:
        lines.extend(["", "FINISH IN UI (gates green — no code changes)"])
        for item in manual_ui[:8]:
            lines.append(f"  - {item.get('folder_name', '?')}")

    if fix_queue:
        lines.extend(["", f"FIX QUEUE ({len(fix_queue)})"])
        for idx, item in enumerate(fix_queue, 1):
            issue = summarize_issue_line(item.get("feedback_notes") or "")
            lines.append(f"  {idx}. {item['folder_name']}")
            lines.append(f"     {issue}")

    lines.extend(["", "THIS RUN"])
    if dry_run:
        lines.append(f"  Dry-run scan only (no Cursor agent). Queue: {len(fix_queue)} task(s)")
    else:
        lines.append(f"  Cursor fixes completed: {fixed} / {len(fix_queue)} queued")

    if oracle_skipped:
        lines.append("  Skipped (oracle precheck):")
        for folder, reason in oracle_skipped:
            lines.append(f"    - {folder}: {reason}")

    if agent_blocked:
        lines.append(f"  Agent not run: {agent_blocked}")
    elif not auto_agent_enabled() and fixed == 0 and fix_queue:
        lines.append("  Agent not run: AUTO_AGENT_FIX=0 (send `run` on Telegram)")

    if errors:
        lines.append("  Errors:")
        for err in errors[:5]:
            lines.append(f"    - {err}")

    if changes:
        lines.extend(["", "STATE CHANGES"])
        for change in changes[:8]:
            lines.append(f"  - {change}")

    lines.extend(["", "HEALTH"])
    for health_line in health_report(repo_root, state).splitlines():
        lines.append(f"  {health_line}")

    if remaining_queue:
        lines.extend(["", "NEXT"])
        lines.append(
            "  Remaining: "
            + ", ".join(i["folder_name"] for i in remaining_queue[:5])
        )
        if not auto_agent_enabled():
            lines.append("  Send `run` on Telegram to fix now")
    elif fix_queue and fixed < len(fix_queue) and not oracle_skipped:
        lines.extend(["", "NEXT"])
        lines.append(
            "  Remaining: "
            + ", ".join(i["folder_name"] for i in fix_queue[fixed:][:5])
        )
        if not auto_agent_enabled():
            lines.append("  Send `run` on Telegram to fix now")

    return "\n".join(lines)
