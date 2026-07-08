#!/usr/bin/env python3
"""Snorkel submission monitor (every 2 hours) — fix NEEDS_REVISION tasks via Cursor SDK.

Polls Terminus submissions, fetches platform feedback for items that need revision,
and triggers a local Composer 2.5 agent to fix + oracle + resubmit. Rules and docs
from .cursor/rules/ and docs/ are injected into every agent prompt.

Only NEEDS_REVISION tasks are ever touched. NEEDS_REVISION tasks whose eval gates
are already green (difficulty, solvability, instruction sufficiency, quality
checks) are never auto-fixed — those only need manual UI field edits
(explanations / rubric) and are reported in the status text instead.
"""

from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import os
import subprocess
import sys
import textwrap
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

UTC = timezone.utc

MONITOR_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(MONITOR_DIR))
STB_SITE = Path(
    os.environ.get(
        "STB_SITE",
        Path.home() / ".local/share/uv/tools/snorkelai-stb/lib/python3.13/site-packages",
    )
)
if STB_SITE.is_dir():
    sys.path.insert(0, str(STB_SITE))

from snorkelai_stb.submission_utils import (  # noqa: E402
    fetch_folder_names,
    get_submission_state,
    list_submission_ids,
)

from notifications import (  # noqa: E402
    git_diff_stat,
    parse_agent_report,
    write_run_report,
)
from feedback_gates import green_eval_skip_reason  # noqa: E402
from monitor_prompt import generate_fix_brief  # noqa: E402
from monitor_env import load_env_file  # noqa: E402
from monitor_exclusions import load_review_exclusions, sync_review_exclusions  # noqa: E402
from monitor_health import (  # noqa: E402
    docker_ready,
    git_dirty_task_folders,
    health_report,
    local_agent_ready,
)
from monitor_agent import (  # noqa: E402
    agent_runtime_label,
    assert_cursor_sdk_only,
    resolve_agent_runtime,
    resolve_cursor_model,
    run_agent,
)
from monitor_messages import build_run_report_message  # noqa: E402
from monitor_notify import notify_event  # noqa: E402
from monitor_oracle import should_skip_cursor_after_oracle  # noqa: E402
from monitor_policy import (  # noqa: E402
    auto_agent_enabled,
    can_run_agent_today,
    clear_skip_once,
    is_paused,
    mark_daily_summary_sent,
    pause_remaining_sec,
    record_daily_event,
    record_fix,
    skip_once_folders,
)
from monitor_summary import (  # noqa: E402
    build_daily_summary,
    should_send_daily_summary,
    state_change_alerts,
)
from monitor_state import (  # noqa: E402
    REPO_ROOT,
    STATE_DIR,
    STATE_FILE,
    TASKS_FILE,
    load_state,
    save_state,
)

from monitor_tasks import sync_tasks_json  # noqa: E402

PROJECT_ID = os.environ.get(
    "TERMINUS_PROJECT_ID", "bfe79c33-8ab0-4061-9849-08d3207c9927"
)
RULES_GLOBS = [
    REPO_ROOT / ".cursor" / "rules" / "terminus.mdc",
    REPO_ROOT / ".cursor" / "rules" / "final-check.mdc",
    REPO_ROOT / ".cursor" / "rules" / "terminus-submission-hardening.mdc",
]
DOCS_FILES = [
    REPO_ROOT / "docs" / "terminus-lessons-learned.md",
    REPO_ROOT / "docs" / "New submission requirements.txt",
]

FIX_STATES = {"NEEDS_REVISION"}
SKIP_STATES = {"EVALUATION_PENDING", "OFFERED", "ACCEPTED"}
MANUAL_REVIEW_STATE = "REVIEW_PENDING"


def log(msg: str) -> None:
    ts = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    line = f"[{ts}] {msg}"
    print(line, flush=True)
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    with (STATE_DIR / "monitor.log").open("a", encoding="utf-8") as fh:
        fh.write(line + "\n")


def load_tasks_map() -> dict:
    sync_tasks_json(REPO_ROOT, TASKS_FILE)
    if not TASKS_FILE.exists():
        return {}
    return json.loads(TASKS_FILE.read_text(encoding="utf-8"))


def read_context_bundle() -> str:
    parts: list[str] = []
    for path in RULES_GLOBS + DOCS_FILES:
        if path.exists():
            parts.append(f"### {path.relative_to(REPO_ROOT)}\n\n{path.read_text(encoding='utf-8')}")
    if not parts:
        raise RuntimeError("No rules/docs files found — cannot run unattended fixes")
    return "\n\n---\n\n".join(parts)


def fetch_feedback_notes(submission_id: str) -> str:
    stb = os.environ.get(
        "STB_BIN",
        str(Path.home() / ".local/share/uv/tools/snorkelai-stb/bin/stb"),
    )
    proc = subprocess.run(
        [stb, "submissions", "feedback", submission_id],
        capture_output=True,
        text=True,
        timeout=180,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(
            f"stb feedback failed ({proc.returncode}): {proc.stderr or proc.stdout}"
        )
    out_dir: Path | None = None
    for line in (proc.stdout + proc.stderr).splitlines():
        if "Feedback written to" in line:
            out_dir = Path(line.split("Feedback written to", 1)[1].strip())
            break
    if out_dir and (out_dir / "notes.txt").exists():
        return (out_dir / "notes.txt").read_text(encoding="utf-8")
    raise RuntimeError(f"could not read feedback notes for {submission_id}")


def feedback_hash(notes: str) -> str:
    return hashlib.sha256(notes.encode()).hexdigest()[:16]


def is_excluded(sid: str, folder: str, exclusions: dict[str, dict]) -> str | None:
    if sid in exclusions:
        return exclusions[sid].get("reason", "excluded")
    return None


def fix_cooldown_seconds() -> int:
    return int(os.environ.get("FIX_COOLDOWN_SEC", "3600"))


def max_attempts_per_feedback() -> int:
    """How many agent attempts to allow on the same unchanged feedback."""
    return int(os.environ.get("MAX_ATTEMPTS_PER_FEEDBACK", "2"))


def cooldown_active(state: dict) -> bool:
    until = state.get("next_fix_allowed_after")
    if not until:
        return False
    try:
        deadline = datetime.fromisoformat(until.replace("Z", "+00:00"))
    except ValueError:
        return False
    return datetime.now(UTC) < deadline


def set_fix_cooldown(state: dict) -> None:
    state["next_fix_allowed_after"] = (
        datetime.now(UTC) + timedelta(seconds=fix_cooldown_seconds())
    ).isoformat()


def cooldown_remaining_sec(state: dict) -> int:
    until = state.get("next_fix_allowed_after")
    if not until:
        return 0
    try:
        deadline = datetime.fromisoformat(until.replace("Z", "+00:00"))
    except ValueError:
        return 0
    return max(0, int((deadline - datetime.now(UTC)).total_seconds()))


def list_submission_queue(
    exclusions: dict[str, dict],
    state: dict,
    subs: list[dict],
    *,
    dry_run: bool,
) -> tuple[list[dict], list[dict], list[dict]]:
    """Return (fix_queue, manual_ui, skipped) after filters and feedback gates.

    manual_ui: NEEDS_REVISION tasks whose eval gates are all green — the task
    content must not be changed; the owner finishes explanations/rubric in the UI.
    """
    fix_queue: list[dict] = []
    manual_ui: list[dict] = []
    skipped: list[dict] = []
    skip_once = skip_once_folders(state)

    for sub in subs:
        sid = sub["submission_id"]
        state_name = sub.get("assignment_state") or get_submission_state(PROJECT_ID, sid)
        folder = (sub.get("folder_name") or "").strip()
        sub["assignment_state"] = state_name

        if state_name in SKIP_STATES:
            log(f"skip {sid[:8]}… state={state_name} folder={folder or '?'}")
            continue
        if state_name == MANUAL_REVIEW_STATE:
            log(f"skip {sid[:8]}… state=REVIEW_PENDING folder={folder or '?'}")
            continue
        if state_name not in FIX_STATES:
            log(f"skip {sid[:8]}… unhandled state={state_name}")
            continue

        ex_reason = is_excluded(sid, folder, exclusions)
        if ex_reason:
            log(f"skip {sid[:8]}… excluded ({ex_reason}) folder={folder or '?'}")
            skipped.append({"submission_id": sid, "folder_name": folder, "reason": ex_reason})
            continue

        if not folder:
            log(f"skip {sid[:8]}… NEEDS_REVISION but no folder name")
            continue
        task_dir = REPO_ROOT / folder
        if not task_dir.is_dir():
            log(f"skip {sid[:8]}… folder missing on disk: {folder}")
            continue

        if folder in skip_once:
            log(f"skip {folder} — skip-once (Telegram skip command)")
            skipped.append({"submission_id": sid, "folder_name": folder, "reason": "skip_once"})
            continue

        try:
            notes = fetch_feedback_notes(sid)
        except Exception as exc:
            log(f"skip {sid[:8]}… feedback fetch failed: {exc}")
            skipped.append({"submission_id": sid, "folder_name": folder, "reason": f"feedback_error: {exc}"})
            continue

        green_reason = green_eval_skip_reason(notes)
        if green_reason:
            log(f"skip {folder} — eval gates green ({green_reason}); UI fields only")
            manual_ui.append(
                {"submission_id": sid, "folder_name": folder, "reason": green_reason}
            )
            skipped.append(
                {"submission_id": sid, "folder_name": folder, "reason": green_reason}
            )
            continue

        fhash = feedback_hash(notes)
        prev = state.get("runs", {}).get(sid, {})
        if (
            not dry_run
            and prev.get("feedback_hash") == fhash
            and prev.get("status") == "agent_finished"
        ):
            log(f"skip {folder} — already fixed this feedback ({fhash})")
            skipped.append({"submission_id": sid, "folder_name": folder, "reason": "already_fixed"})
            continue
        attempts = int(prev.get("attempts", 0)) if prev.get("feedback_hash") == fhash else 0
        if not dry_run and attempts >= max_attempts_per_feedback():
            log(f"skip {folder} — attempt cap reached ({attempts}) on feedback {fhash}")
            skipped.append({"submission_id": sid, "folder_name": folder, "reason": "attempt_cap"})
            continue

        fix_queue.append(
            {
                "submission_id": sid,
                "folder_name": folder,
                "task_dir": task_dir,
                "state": state_name,
                "feedback_notes": notes,
                "feedback_hash": fhash,
                "attempts": attempts,
            }
        )

    fix_queue.sort(key=lambda item: item["folder_name"])
    return fix_queue, manual_ui, skipped


def build_agent_prompt(item: dict, notes: str, tasks_map: dict) -> str:
    folder = item["folder_name"]
    sid = item["submission_id"]
    meta = tasks_map.get(folder, {})
    resubmit = meta.get("resubmit_script")
    resubmit_arg = meta.get("resubmit_arg")
    resubmit_cmd = ""
    if resubmit:
        script = REPO_ROOT / resubmit
        if resubmit_arg:
            resubmit_cmd = f"python3 {script} {resubmit_arg}"
        else:
            resubmit_cmd = f"python3 {script}"
    else:
        resubmit_cmd = (
            "build ZIP + explanations + rubric and call stb create_submission "
            "with --no-send-to-reviewer (see docs/terminus-lessons-learned.md)"
        )

    rules = read_context_bundle()
    brief = generate_fix_brief(folder, notes, task_dir=item["task_dir"])
    return textwrap.dedent(
        f"""\
        Fix this Terminus/Harbor submission task based on platform feedback.

        You MUST follow every rule in the mandatory context below. Do not relabel
        difficulty to pass gates — harden with real interacting logic. Do not send
        to reviewer. Only work on this one task folder.

        ## Mandatory rules and docs (obey all of these)
        {rules}

        ## Task under repair
        - Submission ID: {sid}
        - Task folder: {item['task_dir']}
        - Folder name: {folder}
        - Assignment state: NEEDS_REVISION

        ## Platform feedback (triage using docs/terminus-lessons-learned.md §0)
        {notes}

        {brief}

        ## Required workflow
        1. Read the feedback. Ignore "AutoEval execution failed" boilerplate unless
           the build log shows a real oracle/static-check failure.
        2. Fix the root cause in `{item['task_dir']}`.
        3. Align instruction.md with tests (instruction sufficiency).
        4. For python in languages[], difficulty must be HARD (worst model ≤20%).
        5. Run: harbor run -a oracle -p {folder}
           until reward is 1.0. Docker must be used for oracle.
        6. Bump `# platform-revision:` in environment/Dockerfile before resubmit.
        7. Resubmit in one call (ZIP + explanations + rubric, no send-to-reviewer):
           {resubmit_cmd}
        8. Confirm assignment moves to EVALUATION_PENDING after resubmit.

        ## Required final report (for monitor notifications)
        End your last message with a fenced JSON block exactly like this:

        ```json
        {{
          "changes_summary": "one paragraph: files touched and what you fixed",
          "oracle_reward": "1.0 or failed",
          "resubmit_static_checks": "PASS or FAIL",
          "resubmit_sent": true,
          "platform_state_after": "EVALUATION_PENDING or unchanged"
        }}
        ```
        """
    )


def cleanup_cursor_bridges() -> None:
    """Stop orphaned cursor-sdk-bridge processes from finished local agent runs."""
    pattern = f"cursor-sdk-bridge.js.*{REPO_ROOT}"
    subprocess.run(["pkill", "-f", pattern], capture_output=True, check=False)


def run_cursor_agent(prompt: str, *, dry_run: bool) -> tuple[str, str]:
    """Run a fix via Cursor SDK (cloud default — no macOS popup)."""
    if dry_run:
        preview = STATE_DIR / "last-prompt-preview.txt"
        preview.write_text(prompt, encoding="utf-8")
        log(f"prompt preview written to {preview}")
    return run_agent(prompt, repo_root=REPO_ROOT, dry_run=dry_run, log_fn=log)


def summarize_feedback_issue(notes: str) -> str:
    """Pull a short issue line from platform feedback for notifications."""
    for line in notes.splitlines():
        text = line.strip()
        if "Difficulty:" in text and "❌" in text:
            return text[:200]
        if "Instruction Sufficiency:" in text and "FAIL" in text:
            return text[:200]
        if text.startswith("Difficulty:"):
            return text[:200]
    for line in notes.splitlines():
        if "Summary (difficulty check)" in line:
            continue
        if line.strip().startswith("•"):
            return line.strip()[:200]
    return "see platform feedback in monitor log"


def process_one(item: dict, state: dict, tasks_map: dict, *, dry_run: bool) -> tuple[bool, str]:
    sid = item["submission_id"]
    folder = item["folder_name"]
    notes = item.get("feedback_notes") or fetch_feedback_notes(sid)
    fhash = item.get("feedback_hash") or feedback_hash(notes)
    issue = summarize_feedback_issue(notes)

    if not dry_run:
        skip_oracle, skip_reason = should_skip_cursor_after_oracle(
            notes, folder, repo_root=REPO_ROOT
        )
        if skip_oracle:
            log(f"skip {folder} — {skip_reason} (saved Cursor tokens)")
            record_daily_event(state, "oracle_skip", folder=folder)
            save_state(state)
            return False, skip_reason

    log(f"fixing {folder} ({sid[:8]}…) — {issue}")
    notify_event(
        "fix_started",
        "Snorkel monitor: fix started",
        f"Composer is fixing {folder}.\nIssue: {issue}",
        subtitle=folder,
    )

    prompt = build_agent_prompt(item, notes, tasks_map)
    log(f"triggering Composer fix for {folder}")
    agent_start = time.monotonic()
    cloud_runtime = resolve_agent_runtime() == "cloud"
    try:
        status, summary = run_cursor_agent(prompt, dry_run=dry_run)
    except Exception as exc:
        notify_event(
            "fix_failed",
            "Snorkel monitor: fix failed",
            f"{folder}: {exc}",
            subtitle="agent error",
            force=True,
        )
        record_daily_event(state, "error", folder=folder, detail=str(exc)[:200])
        raise
    agent_minutes = (time.monotonic() - agent_start) / 60.0

    parsed = parse_agent_report(summary)
    if cloud_runtime and not dry_run:
        from monitor_git import pull_latest
        from monitor_oracle import oracle_reward
        from monitor_resubmit import run_task_resubmit

        pulled, pull_msg = pull_latest(REPO_ROOT)
        log(f"git pull after cloud agent: {pull_msg}")
        if not pulled:
            raise RuntimeError(f"git pull failed after cloud agent: {pull_msg}")

        reward = oracle_reward(folder, repo_root=REPO_ROOT)
        log(f"oracle after cloud pull: {reward}")
        if reward is not None:
            parsed["oracle_reward"] = str(reward)
        if reward is not None and reward >= 1.0:
            ok, resubmit_msg = run_task_resubmit(folder, tasks_map, REPO_ROOT)
            log(f"resubmit after cloud fix: {resubmit_msg}")
            if ok:
                parsed["resubmit_sent"] = True
                parsed["resubmit_static_checks"] = parsed.get("resubmit_static_checks", "PASS")
            else:
                parsed["resubmit_sent"] = False
                parsed["resubmit_static_checks"] = "FAIL"
                raise RuntimeError(f"resubmit failed: {resubmit_msg}")
        elif reward is not None:
            raise RuntimeError(f"oracle failed after cloud fix (reward={reward})")

    diff_stat = git_diff_stat(REPO_ROOT, folder) if not dry_run else "(dry run)"
    new_state = ""
    if not dry_run:
        try:
            new_state = get_submission_state(PROJECT_ID, sid)
        except Exception as exc:
            new_state = f"unknown ({exc})"

    changes = parsed.get("changes_summary") or "(agent did not return changes_summary)"
    oracle = parsed.get("oracle_reward", "?")
    static = parsed.get("resubmit_static_checks", "?")
    resubmitted = parsed.get("resubmit_sent", new_state == "EVALUATION_PENDING")

    report = {
        "folder_name": folder,
        "submission_id": sid,
        "feedback_hash": fhash,
        "issue": issue,
        "agent_status": status,
        "agent_report": parsed,
        "git_diff_stat": diff_stat,
        "platform_state_after": new_state or parsed.get("platform_state_after", ""),
        "dry_run": dry_run,
        "finished_at": datetime.now(UTC).isoformat(),
    }
    report_path = write_run_report(STATE_DIR, report)

    if dry_run:
        notify_event(
            "dry_run",
            "Snorkel monitor: dry run",
            f"Would fix {folder}. Prompt saved.",
            subtitle=folder,
        )
    elif resubmitted or new_state == "EVALUATION_PENDING":
        notify_event(
            "resubmitted",
            "Snorkel monitor: resubmitted",
            (
                f"{folder} → {new_state or 'EVALUATION_PENDING'}\n"
                f"Oracle: {oracle} | Static: {static}\n"
                f"Changes: {changes[:180]}"
            ),
            subtitle="resubmit OK",
        )
        record_daily_event(state, "resubmitted", folder=folder)
        from monitor_git import commit_and_push_repo

        committed, git_msg = commit_and_push_repo(REPO_ROOT, folder, changes)
        if committed:
            log(f"git: committed and pushed — {git_msg}")
        elif git_msg != "nothing to commit":
            log(f"git: {git_msg}")
    else:
        notify_event(
            "fix_finished",
            "Snorkel monitor: fix finished",
            (
                f"{folder} — agent done but verify resubmit.\n"
                f"State: {new_state or 'unchanged'} | Oracle: {oracle}\n"
                f"Changes: {changes[:180]}"
            ),
            subtitle="review needed",
        )

    if not dry_run:
        record_fix(state, folder, agent_minutes=agent_minutes)

    state.setdefault("runs", {})[sid] = {
        "folder_name": folder,
        "feedback_hash": fhash,
        "attempts": int(item.get("attempts", 0)) + 1,
        "status": "agent_finished" if not dry_run else "dry_run",
        "agent_status": status,
        "agent_summary": summary,
        "agent_report": parsed,
        "git_diff_stat": diff_stat,
        "platform_state_after": new_state,
        "issue": issue,
        "report_path": str(report_path),
        "last_run": datetime.now(UTC).isoformat(),
    }
    save_state(state)
    log(f"done {folder} agent_status={status} state_after={new_state}")
    return True, ""


def detect_state_changes(state: dict, all_subs: list[dict]) -> list[str]:
    """Compare platform states to the previous run and return change lines."""
    previous: dict[str, str] = dict(state.get("last_states") or {})
    current: dict[str, str] = {}
    changes: list[str] = []
    for sub in all_subs:
        sid = sub["submission_id"]
        name = (sub.get("folder_name") or sid[:8]).strip() or sid[:8]
        st = sub.get("assignment_state") or "?"
        current[sid] = st
        old = previous.get(sid)
        if old and old != st:
            changes.append(f"{name}: {old} -> {st}")
        elif not old and previous:
            changes.append(f"{name}: new submission ({st})")
    state["last_states"] = current
    return changes


def build_status_text(
    all_subs: list[dict],
    fix_queue: list[dict],
    manual_ui: list[dict],
    changes: list[str],
) -> str:
    """Log-friendly status summary (Telegram uses build_run_report_message)."""
    counts: dict[str, int] = {}
    for sub in all_subs:
        counts[sub.get("assignment_state") or "?"] = (
            counts.get(sub.get("assignment_state") or "?", 0) + 1
        )
    lines = [
        "States: " + ", ".join(f"{k}={v}" for k, v in sorted(counts.items())),
    ]
    if changes:
        lines.append("Changed since last run:")
        lines.extend(f"  {c}" for c in changes[:6])
    if fix_queue:
        lines.append(
            "Fix queue: " + ", ".join(i["folder_name"] for i in fix_queue[:8])
        )
    else:
        lines.append("Fix queue: none")
    if manual_ui:
        lines.append(
            "Finish in UI: " + ", ".join(i["folder_name"] for i in manual_ui[:5])
        )
    return "\n".join(lines)


_run_report: dict | None = None


def _init_run_report() -> dict:
    global _run_report
    _run_report = {
        "all_subs": [],
        "fix_queue": [],
        "manual_ui": [],
        "skipped": [],
        "changes": [],
        "fixed": 0,
        "oracle_skipped": [],
        "agent_blocked": "",
        "errors": [],
    }
    return _run_report


def _update_run_report(**kwargs) -> None:
    if _run_report is not None:
        _run_report.update(kwargs)


def _acquire_run_lock() -> object | None:
    """Prevent overlapping hourly runs (e.g. RunAtLoad + manual kickstart)."""
    lock_path = STATE_DIR / ".hourly.lock"
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    fh = lock_path.open("w", encoding="utf-8")
    try:
        fcntl.flock(fh.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        fh.close()
        return None
    fh.write(f"{os.getpid()}\n")
    fh.flush()
    return fh


def _finish_run(state: dict) -> None:
    """Daily summary, run report, git warning, clear skip-once."""
    dirty = git_dirty_task_folders(REPO_ROOT)
    warn_at = int(os.environ.get("GIT_WARN_MIN_FOLDERS", "3"))
    if len(dirty) >= warn_at:
        notify_event(
            "git_warning",
            "Snorkel monitor: git hygiene",
            f"{len(dirty)} task folders have uncommitted changes:\n"
            + ", ".join(dirty[:8]),
            force=True,
        )
    if should_send_daily_summary(state):
        summary = build_daily_summary(state)
        notify_event(
            "daily_summary",
            "Snorkel daily summary",
            summary,
            force=True,
        )
        mark_daily_summary_sent(state)
    if _run_report is not None:
        from notifications import notify_all

        report = build_run_report_message(
            repo_root=REPO_ROOT,
            state=state,
            **_run_report,
        )
        notify_all("Snorkel Monitor", report)
    if state.get("skip_once_folders"):
        clear_skip_once(state)
    save_state(state)


def main() -> int:
    parser = argparse.ArgumentParser(description="Snorkel submission monitor (every 90 minutes)")
    parser.add_argument("--dry-run", action="store_true", help="Check only; do not call Cursor")
    parser.add_argument(
        "--max-fixes",
        type=int,
        default=int(os.environ.get("MAX_FIXES_PER_RUN", "8")),
        help="Max agent runs per invocation (remainder waits for the next 90-minute run)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Ignore fix cooldown (still respects exclusions and green-gate skip)",
    )
    parser.add_argument(
        "--folder",
        type=str,
        default="",
        help="Only consider this task folder name",
    )
    args = parser.parse_args()
    if args.force:
        force_cap = int(os.environ.get("MAX_FIXES_PER_FORCE_RUN", "8"))
        scheduled_cap = int(os.environ.get("MAX_FIXES_PER_RUN", "8"))
        if args.max_fixes <= scheduled_cap:
            args.max_fixes = max(args.max_fixes, force_cap)

    load_env_file()
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    lock = _acquire_run_lock()
    if lock is None:
        log("SKIP — another hourly run is already in progress")
        return 0

    _init_run_report()
    state = load_state()
    state["last_check"] = datetime.now(UTC).isoformat()
    save_state(state)

    if is_paused(state):
        remain = pause_remaining_sec(state)
        log(f"paused — {remain}s remaining")
        _update_run_report(agent_blocked=f"paused ({remain // 60}m left)")
        notify_event(
            "paused",
            "Snorkel monitor: paused",
            f"No fixes until pause ends ({remain // 60}m left).\nSend resume on Telegram.",
            force=True,
        )
        _finish_run(state)
        return 0

    log("=== 90-minute submission check start ===")
    docker_ok = docker_ready()
    if not docker_ok:
        log("WARN: Docker not reachable — agent fixes deferred (oracle needs Docker)")

    try:
        all_subs = list_submission_ids(project_id=PROJECT_ID)
        fetch_folder_names(all_subs, fetch_all=True)
        exclusions = sync_review_exclusions(all_subs, log_fn=log)
        fix_queue, manual_ui, skipped = list_submission_queue(
            exclusions, state, all_subs, dry_run=args.dry_run
        )
        if args.folder.strip():
            needle = args.folder.strip().lower()
            fix_queue = [
                i
                for i in fix_queue
                if i["folder_name"].lower() == needle or needle in i["folder_name"].lower()
            ]
    except Exception as exc:
        log(f"ERROR listing submissions: {exc}")
        _update_run_report(errors=[f"list submissions: {exc}"])
        notify_event(
            "error",
            "Snorkel monitor: error",
            f"Could not list submissions: {exc}",
            subtitle="90-min check",
            force=True,
        )
        _finish_run(state)
        return 1

    changes = detect_state_changes(state, all_subs)
    for change in changes:
        log(f"state change: {change}")
    for alert in state_change_alerts(changes):
        notify_event("state_alert", "Snorkel monitor: state change", alert, force=True)
        if "ACCEPTED" in alert:
            record_daily_event(state, "accepted", folder=alert.split(":")[-1].strip())

    _update_run_report(
        all_subs=all_subs,
        fix_queue=fix_queue,
        manual_ui=manual_ui,
        skipped=skipped,
        changes=changes,
    )

    state["last_queue"] = {
        "fix_queue": [i["folder_name"] for i in fix_queue],
        "manual_ui": [i["folder_name"] for i in manual_ui],
        "skipped": skipped,
        "checked_at": datetime.now(UTC).isoformat(),
    }
    save_state(state)

    status_text = build_status_text(all_subs, fix_queue, manual_ui, changes)
    status_text += "\n\n" + health_report(REPO_ROOT, state)
    log("status:\n" + status_text)

    if not fix_queue:
        log("no auto-fix candidates after exclusions and feedback gates")
        if skipped:
            log(f"skipped {len(skipped)} item(s) — see state.last_queue")
        _finish_run(state)
        return 0

    log(f"fix queue ({len(fix_queue)}): {', '.join(i['folder_name'] for i in fix_queue)}")
    if skipped:
        log(f"skipped {len(skipped)} — exclusions / green gates / already fixed")

    if not docker_ok and not args.dry_run:
        _update_run_report(agent_blocked="Docker not reachable")
        notify_event(
            "waiting_docker",
            "Snorkel monitor: waiting for Docker",
            f"{len(fix_queue)} task(s) need fixes but Docker is down. "
            "Start Docker Desktop; will retry next run.",
            subtitle="blocked",
            force=True,
        )
        _finish_run(state)
        return 0

    if cooldown_active(state) and not args.force and not args.dry_run:
        remain = cooldown_remaining_sec(state)
        nxt = fix_queue[0]["folder_name"]
        log(f"cooldown active ({remain}s left) — next up: {nxt}")
        _update_run_report(agent_blocked=f"cooldown ({remain // 60}m left)")
        notify_event(
            "queued",
            "Snorkel monitor: queued",
            f"Next fix in {remain // 60}m: {nxt}\nQueue: {', '.join(i['folder_name'] for i in fix_queue[:4])}",
            subtitle="cooldown",
        )
        _finish_run(state)
        return 0

    agent_ok, cap_reason = can_run_agent_today(state)
    if not agent_ok and not args.dry_run:
        log(f"daily cap: {cap_reason}")
        _update_run_report(agent_blocked=cap_reason)
        notify_event(
            "error",
            "Snorkel monitor: daily cap",
            cap_reason,
            force=True,
        )
        _finish_run(state)
        return 0

    if (
        not auto_agent_enabled()
        and not args.force
        and not args.folder.strip()
        and not args.dry_run
    ):
        log("AUTO_AGENT_FIX=0 — scan only (Telegram: run or run <task> to use Cursor)")
        _update_run_report(agent_blocked="AUTO_AGENT_FIX=0 (scan only)")
        _finish_run(state)
        return 0

    tasks_map = load_tasks_map()
    try:
        composer_model = assert_cursor_sdk_only()
    except RuntimeError as exc:
        log(f"ERROR: {exc}")
        _update_run_report(agent_blocked=str(exc), errors=[str(exc)])
        notify_event(
            "error",
            "Snorkel monitor: config error",
            str(exc),
            force=True,
        )
        _finish_run(state)
        return 1
    log(f"Cursor agent runtime: {agent_runtime_label()} model={composer_model}")
    if resolve_agent_runtime() == "local":
        ready, cursor_reason = local_agent_ready()
        if not ready and not args.dry_run:
            log(f"Cursor preflight: {cursor_reason}")
            _update_run_report(agent_blocked=cursor_reason)
            notify_event(
                "error",
                "Snorkel monitor: Cursor not ready",
                cursor_reason,
                force=True,
            )
            _finish_run(state)
            return 0

    fixed = 0
    oracle_skipped: list[tuple[str, str]] = []
    run_errors: list[str] = []
    for item in fix_queue:
        if fixed >= args.max_fixes:
            log(f"reached max fixes per run ({args.max_fixes}) — remainder waits for next run")
            break
        try:
            did_fix, skip_reason = process_one(item, state, tasks_map, dry_run=args.dry_run)
            if skip_reason:
                oracle_skipped.append((item["folder_name"], skip_reason))
            elif did_fix:
                fixed += 1
        except Exception as exc:
            log(f"ERROR on {item['folder_name']}: {exc}")
            run_errors.append(f"{item['folder_name']}: {exc}")
            notify_event(
                "error",
                "Snorkel monitor: error",
                f"{item['folder_name']}: {exc}",
                subtitle="90-min check",
                force=True,
            )
            sid = item["submission_id"]
            state.setdefault("runs", {})[sid] = {
                "folder_name": item["folder_name"],
                "feedback_hash": item.get("feedback_hash", ""),
                "attempts": int(item.get("attempts", 0)) + 1,
                "status": "error",
                "error": str(exc),
                "last_run": datetime.now(UTC).isoformat(),
            }
            save_state(state)
    if fixed and not args.dry_run:
        set_fix_cooldown(state)
        save_state(state)

    if fix_queue and fixed < len(fix_queue):
        nxt = fix_queue[fixed]["folder_name"] if fixed < len(fix_queue) else ""
        if nxt:
            log(f"next queued task on next run: {nxt}")

    log(f"=== done — triggered {fixed} fix(es) ===")
    processed = fixed + len(oracle_skipped) + len(run_errors)
    remaining_queue = fix_queue[processed:] if processed < len(fix_queue) else []
    _update_run_report(
        fixed=fixed,
        oracle_skipped=oracle_skipped,
        errors=run_errors,
        remaining_queue=remaining_queue,
    )
    _finish_run(state)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
