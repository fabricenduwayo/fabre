"""Daily summary, state-change alerts, finish-in-UI helper, explanation drafts."""

from __future__ import annotations

import re
from datetime import datetime, timezone

from feedback_gates import green_eval_skip_reason

UTC = timezone.utc

ACCEPTED_STATES = {"ACCEPTED"}
REVIEW_RETURN = {"NEEDS_REVISION"}


def extract_difficulty_line(notes: str) -> str | None:
    for line in notes.splitlines():
        text = line.strip()
        if "Difficulty:" in text and ("❌" in text or "TRIVIAL" in text or "EASY" in text):
            return text[:220]
    return None


def state_change_alerts(changes: list[str]) -> list[str]:
    alerts: list[str] = []
    for change in changes:
        if "-> ACCEPTED" in change:
            alerts.append(f"ACCEPTED: {change}")
        elif "REVIEW_PENDING -> NEEDS_REVISION" in change or "-> NEEDS_REVISION" in change:
            if "NEEDS_REVISION ->" not in change:
                alerts.append(f"Reviewer return: {change}")
    return alerts


def build_finish_ui_checklist(folder: str, notes: str) -> str:
    reason = green_eval_skip_reason(notes) or "eval gates green"
    lines = [
        f"Finish in UI — {folder}",
        f"Reason: {reason}",
        "",
        "Checklist:",
        "[ ] difficulty_explanation filled in platform UI",
        "[ ] solution_explanation filled in platform UI",
        "[ ] verification_explanation filled in platform UI",
        "[ ] rubric generated + edited (test_rubrics)",
        "[ ] checkbox_evaluate_rubrics = true",
        "[ ] ZIP re-uploaded if task files changed",
        "[ ] send to reviewer only after checks pass",
    ]
    diff = extract_difficulty_line(notes)
    if diff:
        lines.insert(3, f"Platform note: {diff}")
    return "\n".join(lines)


def draft_explanations(folder: str, notes: str, run_data: dict | None = None) -> str:
    """Short drafts for platform fields — paste into Snorkel UI."""
    issue = ""
    for line in notes.splitlines():
        if "Difficulty:" in line or "Instruction Sufficiency:" in line:
            issue = line.strip()[:200]
            break
    changes = ""
    if run_data:
        changes = str(
            run_data.get("agent_report", {}).get("changes_summary")
            or run_data.get("changes_summary")
            or ""
        )[:400]
    diff_explanation = (
        f"Task {folder} failed difficulty/solvability gates. "
        f"Platform feedback: {issue or 'see notes'}. "
        "Hardened with interacting logic rather than relabeling difficulty."
    )
    solution_explanation = (
        f"Read platform feedback, fixed root cause in {folder}, "
        "aligned instruction.md with tests, ran harbor oracle to 1.0, "
        "bumped platform-revision, resubmitted without send-to-reviewer."
    )
    if changes:
        solution_explanation += f" Changes: {changes}"
    verify_explanation = (
        "Verifier runs tests/test.sh → pytest test_outputs.py; "
        "oracle uses solution/solve.sh. Local harbor run matched platform static checks."
    )
    return "\n".join(
        [
            f"Draft explanations — {folder}",
            "",
            "difficulty_explanation:",
            diff_explanation,
            "",
            "solution_explanation:",
            solution_explanation,
            "",
            "verification_explanation:",
            verify_explanation,
        ]
    )


def build_daily_summary(state: dict) -> str:
    stats = state.get("daily_stats") or {}
    date = stats.get("date") or datetime.now(UTC).strftime("%Y-%m-%d")
    events: list[dict] = list(stats.get("events") or [])
    fixes = [e for e in events if e.get("type") == "fix"]
    errors = [e for e in events if e.get("type") == "error"]
    resubmits = [e for e in events if e.get("type") == "resubmitted"]
    accepted = [e for e in events if e.get("type") == "accepted"]
    lines = [
        f"Daily summary — {date}",
        f"Agent fixes: {len(fixes)} (cap {stats.get('fixes', len(fixes))} total today)",
        f"Agent minutes: {stats.get('agent_minutes', 0)}",
        f"Resubmitted: {len(resubmits)}",
        f"Accepted: {len(accepted)}",
        f"Errors: {len(errors)}",
    ]
    queue = state.get("last_queue", {}).get("fix_queue") or []
    manual = state.get("last_queue", {}).get("manual_ui") or []
    if queue:
        lines.append("Fix queue now: " + ", ".join(queue[:6]))
    if manual:
        lines.append("Finish in UI: " + ", ".join(manual[:6]))
    recent = events[-8:]
    if recent:
        lines.append("")
        lines.append("Recent:")
        for ev in recent:
            folder = ev.get("folder", ev.get("type", "?"))
            lines.append(f"  {ev.get('type')}: {folder}")
    return "\n".join(lines)


def should_send_daily_summary(state: dict, *, hour_utc: int | None = None) -> bool:
    """Send once per UTC day, default at NOTIFY_DAILY_SUMMARY_HOUR_UTC (23)."""
    target_hour = int(__import__("os").environ.get("NOTIFY_DAILY_SUMMARY_HOUR_UTC", "23"))
    hour = hour_utc if hour_utc is not None else datetime.now(UTC).hour
    today = datetime.now(UTC).strftime("%Y-%m-%d")
    if state.get("last_daily_summary_date") == today:
        return False
    return hour >= target_hour
