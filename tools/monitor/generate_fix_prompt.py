#!/usr/bin/env python3
"""Fetch platform feedback and write a Cursor-ready fix prompt for one task."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

MONITOR_DIR = Path(__file__).resolve().parent
REPO_ROOT = MONITOR_DIR.parent.parent
sys.path.insert(0, str(MONITOR_DIR))

from snorkelai_stb.submission_utils import fetch_folder_names, list_submission_ids  # noqa: E402

from hourly_submission_check import (  # noqa: E402
    PROJECT_ID,
    build_agent_prompt,
    fetch_feedback_notes,
    load_tasks_map,
)
from monitor_prompt import generate_fix_brief, triage_feedback  # noqa: E402
from monitor_env import load_env_file  # noqa: E402
from monitor_tasks import find_submission_for_folder, sync_tasks_json  # noqa: E402
from monitor_state import REPO_ROOT, TASKS_FILE  # noqa: E402


def _subs_with_folders() -> list[dict]:
    subs = list_submission_ids(project_id=PROJECT_ID)
    fetch_folder_names(subs, fetch_all=True)
    return subs


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate a fix prompt from platform feedback")
    parser.add_argument("folder", help="Task folder name, e.g. harden-php-api-defaults")
    parser.add_argument(
        "--out",
        type=Path,
        default=None,
        help="Write prompt here (default: .review-scratch/prompts/<folder>.txt)",
    )
    parser.add_argument("--brief-only", action="store_true", help="Print triage brief only")
    args = parser.parse_args()

    load_env_file()
    sync_tasks_json(REPO_ROOT, TASKS_FILE)
    sub = find_submission_for_folder(_subs_with_folders(), args.folder)
    if not sub:
        print(f"no NEEDS_REVISION submission for folder {args.folder!r}", file=sys.stderr)
        return 1

    sid = sub["submission_id"]
    notes = fetch_feedback_notes(sid)
    task_dir = REPO_ROOT / args.folder
    brief = generate_fix_brief(args.folder, notes, task_dir=task_dir)

    if args.brief_only:
        print(brief)
        triage = triage_feedback(notes)
        print("\n--- triage json ---")
        import json

        print(json.dumps(triage, indent=2, default=str))
        return 0

    tasks_map = load_tasks_map()
    item = {
        "submission_id": sid,
        "folder_name": args.folder,
        "task_dir": task_dir,
    }
    prompt = build_agent_prompt(item, notes, tasks_map)
    # Inject brief after platform feedback section
    prompt = prompt.replace(
        f"## Platform feedback (triage using docs/terminus-lessons-learned.md §0)\n        {notes}",
        f"## Platform feedback (triage using docs/terminus-lessons-learned.md §0)\n        {notes}\n\n        {brief}",
    )

    out = args.out or REPO_ROOT / ".review-scratch" / "prompts" / f"{args.folder}.txt"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(prompt, encoding="utf-8")
    print(f"wrote {out} ({len(prompt)} chars)")
    print(f"submission: {sid}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
