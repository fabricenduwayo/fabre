"""Review exclusion list helpers."""

from __future__ import annotations

import json
from datetime import datetime, timezone

from monitor_state import EXCLUSIONS_FILE

UTC = timezone.utc


def load_review_exclusions() -> dict[str, dict]:
    if not EXCLUSIONS_FILE.exists():
        return {}
    data = json.loads(EXCLUSIONS_FILE.read_text(encoding="utf-8"))
    return dict(data.get("submission_ids") or {})


def save_review_exclusions(exclusions: dict[str, dict]) -> None:
    payload = {
        "_comment": (
            "Submissions excluded from auto-fix. REVIEW_PENDING tasks are added "
            "automatically. Delete an entry to re-enable auto-fix after manual review."
        ),
        "submission_ids": exclusions,
    }
    EXCLUSIONS_FILE.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def exclude_submission(sid: str, folder: str, reason: str = "manual") -> None:
    exclusions = load_review_exclusions()
    exclusions[sid] = {
        "folder_name": folder,
        "reason": reason,
        "added_at": datetime.now(UTC).isoformat(),
    }
    save_review_exclusions(exclusions)


def unexclude_submission(sid: str) -> bool:
    exclusions = load_review_exclusions()
    if sid not in exclusions:
        return False
    del exclusions[sid]
    save_review_exclusions(exclusions)
    return True


MANUAL_REVIEW_STATE = "REVIEW_PENDING"


def sync_review_exclusions(all_subs: list[dict], log_fn=None) -> dict[str, dict]:
    """Persist REVIEW_PENDING tasks so they stay excluded if bounced to NEEDS_REVISION."""
    exclusions = load_review_exclusions()
    changed = False
    now = datetime.now(UTC).isoformat()
    for sub in all_subs:
        sid = sub["submission_id"]
        state = sub.get("assignment_state", "")
        folder = (sub.get("folder_name") or "").strip()
        if state != MANUAL_REVIEW_STATE:
            continue
        if sid not in exclusions:
            exclusions[sid] = {
                "folder_name": folder,
                "reason": "REVIEW_PENDING",
                "added_at": now,
            }
            changed = True
            if log_fn:
                log_fn(f"excluded {sid[:8]}… ({folder or '?'}) — REVIEW_PENDING manual review")
    if changed:
        save_review_exclusions(exclusions)
    return exclusions
