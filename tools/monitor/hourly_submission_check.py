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
import hashlib
import json
import os
import subprocess
import sys
import textwrap
from datetime import datetime, timedelta, timezone
from pathlib import Path

UTC = timezone.utc

MONITOR_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(MONITOR_DIR))
REPO_ROOT = Path(os.environ.get("REPO_ROOT", MONITOR_DIR.parent.parent)).resolve()
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
    notify_all,
    parse_agent_report,
    write_run_report,
)
from feedback_gates import green_eval_skip_reason  # noqa: E402

PROJECT_ID = os.environ.get(
    "TERMINUS_PROJECT_ID", "bfe79c33-8ab0-4061-9849-08d3207c9927"
)
STATE_DIR = REPO_ROOT / ".review-scratch" / "monitor"
STATE_FILE = STATE_DIR / "state.json"
EXCLUSIONS_FILE = MONITOR_DIR / "review_exclusions.json"
TASKS_FILE = MONITOR_DIR / "tasks.json"
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


def load_env_file() -> None:
    env_path = MONITOR_DIR / ".env"
    if not env_path.exists():
        return
    for raw in env_path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip())


def load_state() -> dict:
    if not STATE_FILE.exists():
        return {"runs": {}, "last_check": None}
    return json.loads(STATE_FILE.read_text(encoding="utf-8"))


def save_state(state: dict) -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")


def load_tasks_map() -> dict:
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


def docker_ready() -> bool:
    try:
        proc = subprocess.run(
            ["docker", "info"],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
        return proc.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


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


def sync_review_exclusions(all_subs: list[dict]) -> dict[str, dict]:
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
            log(f"excluded {sid[:8]}… ({folder or '?'}) — REVIEW_PENDING manual review")
    if changed:
        save_review_exclusions(exclusions)
    return exclusions


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


def run_cursor_agent(prompt: str, *, dry_run: bool) -> tuple[str, str]:
    model = os.environ.get("MONITOR_MODEL", "composer-2.5")
    if dry_run:
        log(f"DRY RUN — would call Agent.prompt model={model} cwd={REPO_ROOT}")
        preview = STATE_DIR / "last-prompt-preview.txt"
        preview.write_text(prompt, encoding="utf-8")
        log(f"prompt preview written to {preview}")
        return "dry_run", "skipped"

    api_key = os.environ.get("CURSOR_API_KEY", "").strip()
    if not api_key or api_key.startswith("cursor_your"):
        raise RuntimeError(
            "CURSOR_API_KEY not set — copy tools/monitor/.env.example to tools/monitor/.env"
        )

    from cursor_sdk import Agent, AgentOptions, CursorAgentError, LocalAgentOptions

    try:
        result = Agent.prompt(
            prompt,
            AgentOptions(
                api_key=api_key,
                model=model,
                local=LocalAgentOptions(cwd=str(REPO_ROOT)),
            ),
        )
    except CursorAgentError as exc:
        raise RuntimeError(f"Cursor agent startup failed: {exc.message}") from exc

    if result.status == "error":
        raise RuntimeError(f"Cursor agent run failed: {getattr(result, 'result', '')}")
    return str(result.status), str(getattr(result, "result", ""))[:4000]


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


def process_one(item: dict, state: dict, tasks_map: dict, *, dry_run: bool) -> bool:
    sid = item["submission_id"]
    folder = item["folder_name"]
    notes = item.get("feedback_notes") or fetch_feedback_notes(sid)
    fhash = item.get("feedback_hash") or feedback_hash(notes)
    issue = summarize_feedback_issue(notes)
    log(f"fixing {folder} ({sid[:8]}…) — {issue}")
    notify_all(
        "Snorkel monitor: fix started",
        f"Composer is fixing {folder}.\nIssue: {issue}",
        subtitle=folder,
        slack=f":hammer_and_wrench: *Fix started* — `{folder}`\nIssue: {issue}",
    )

    prompt = build_agent_prompt(item, notes, tasks_map)
    log(f"triggering Composer fix for {folder}")
    try:
        status, summary = run_cursor_agent(prompt, dry_run=dry_run)
    except Exception as exc:
        notify_all(
            "Snorkel monitor: fix failed",
            f"{folder}: {exc}",
            subtitle="agent error",
            slack=f":x: *Fix failed* — `{folder}`\n{exc}",
        )
        raise

    diff_stat = git_diff_stat(REPO_ROOT, folder) if not dry_run else "(dry run)"
    parsed = parse_agent_report(summary)
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
        notify_all(
            "Snorkel monitor: dry run",
            f"Would fix {folder}. Prompt saved.",
            subtitle=folder,
        )
    elif resubmitted or new_state == "EVALUATION_PENDING":
        notify_all(
            "Snorkel monitor: resubmitted",
            (
                f"{folder} → {new_state or 'EVALUATION_PENDING'}\n"
                f"Oracle: {oracle} | Static: {static}\n"
                f"Changes: {changes[:180]}"
            ),
            subtitle="resubmit OK",
            slack=(
                f":white_check_mark: *Resubmitted* — `{folder}`\n"
                f"State: `{new_state}` | Oracle: `{oracle}` | Checks: `{static}`\n"
                f"Changes: {changes}\n"
                f"Diff:\n```\n{diff_stat[:1500]}\n```"
            ),
        )
    else:
        notify_all(
            "Snorkel monitor: fix finished",
            (
                f"{folder} — agent done but verify resubmit.\n"
                f"State: {new_state or 'unchanged'} | Oracle: {oracle}\n"
                f"Changes: {changes[:180]}"
            ),
            subtitle="review needed",
            slack=(
                f":warning: *Fix finished — verify* `{folder}`\n"
                f"State: `{new_state}` | Oracle: `{oracle}` | Checks: `{static}`\n"
                f"Changes: {changes}"
            ),
        )

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
    return True


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
    """Human status message sent at the start of every run."""
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
            "Will auto-fix now: " + ", ".join(i["folder_name"] for i in fix_queue[:5])
        )
    else:
        lines.append("Will auto-fix now: none")
    if manual_ui:
        lines.append(
            "Green — finish in UI (explanations/rubric only, task untouched): "
            + ", ".join(i["folder_name"] for i in manual_ui[:5])
        )
    return "\n".join(lines)


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
    args = parser.parse_args()

    load_env_file()
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    state = load_state()
    state["last_check"] = datetime.now(UTC).isoformat()
    save_state(state)

    log("=== 90-minute submission check start ===")
    docker_ok = docker_ready()
    if not docker_ok:
        log("WARN: Docker not reachable — agent fixes deferred (oracle needs Docker)")

    try:
        all_subs = list_submission_ids(project_id=PROJECT_ID)
        fetch_folder_names(all_subs, fetch_all=True)
        exclusions = sync_review_exclusions(all_subs)
        fix_queue, manual_ui, skipped = list_submission_queue(
            exclusions, state, all_subs, dry_run=args.dry_run
        )
    except Exception as exc:
        log(f"ERROR listing submissions: {exc}")
        notify_all(
            "Snorkel monitor: error",
            f"Could not list submissions: {exc}",
            subtitle="90-min check",
        )
        return 1

    changes = detect_state_changes(state, all_subs)
    for change in changes:
        log(f"state change: {change}")

    state["last_queue"] = {
        "fix_queue": [i["folder_name"] for i in fix_queue],
        "manual_ui": [i["folder_name"] for i in manual_ui],
        "skipped": skipped,
        "checked_at": datetime.now(UTC).isoformat(),
    }
    save_state(state)

    # Status text before any work starts — every run, even when idle.
    status_text = build_status_text(all_subs, fix_queue, manual_ui, changes)
    log("status:\n" + status_text)
    notify_all(
        "Snorkel monitor: status",
        status_text,
        subtitle="90-min check",
    )

    if not fix_queue:
        log("no auto-fix candidates after exclusions and feedback gates")
        if skipped:
            log(f"skipped {len(skipped)} item(s) — see state.last_queue")
        return 0

    log(f"fix queue ({len(fix_queue)}): {', '.join(i['folder_name'] for i in fix_queue)}")
    if skipped:
        log(f"skipped {len(skipped)} — exclusions / green gates / already fixed")

    if not docker_ok and not args.dry_run:
        notify_all(
            "Snorkel monitor: waiting for Docker",
            f"{len(fix_queue)} task(s) need fixes but Docker is down. "
            "Start Docker Desktop; will retry in 2h.",
            subtitle="blocked",
        )
        return 0

    if cooldown_active(state) and not args.force and not args.dry_run:
        remain = cooldown_remaining_sec(state)
        nxt = fix_queue[0]["folder_name"]
        log(f"cooldown active ({remain}s left) — next up: {nxt}")
        notify_all(
            "Snorkel monitor: queued",
            f"Next fix in {remain // 60}m: {nxt}\nQueue: {', '.join(i['folder_name'] for i in fix_queue[:4])}",
            subtitle="cooldown",
        )
        return 0

    tasks_map = load_tasks_map()
    fixed = 0
    for item in fix_queue:
        if fixed >= args.max_fixes:
            log(f"reached max fixes per run ({args.max_fixes}) — remainder waits for next run")
            break
        try:
            if process_one(item, state, tasks_map, dry_run=args.dry_run):
                fixed += 1
        except Exception as exc:
            log(f"ERROR on {item['folder_name']}: {exc}")
            notify_all(
                "Snorkel monitor: error",
                f"{item['folder_name']}: {exc}",
                subtitle="90-min check",
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
    notify_all(
        "Snorkel monitor: run complete",
        f"Fixed {fixed} of {len(fix_queue)} queued task(s). Next check in 90m.",
        subtitle="90-min check",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
