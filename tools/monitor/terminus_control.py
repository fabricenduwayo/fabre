#!/usr/bin/env python3
"""Start/stop/status and Telegram command dispatch for the submission monitor."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from command_parser import ParsedCommand, help_text, parse_command
from monitor_env import DEFAULT_ENV_FILE, load_env_file
from monitor_exclusions import exclude_submission, load_review_exclusions, unexclude_submission
from monitor_health import docker_ready, health_report
from monitor_policy import (
    clear_pause,
    clear_skip_once,
    parse_pause_duration,
    set_pause,
)
from monitor_state import REPO_ROOT, STATE_DIR, load_state, save_state
from monitor_summary import build_daily_summary, build_finish_ui_checklist, draft_explanations
from monitor_tasks import find_submission_for_folder, resolve_folder_name, sync_tasks_json

MONITOR_DIR = Path(__file__).resolve().parent
MONITOR_LABEL = "com.snorkel.submission-monitor"
LISTENER_LABEL = "com.snorkel.terminus-command-listener"
PLIST_NAME = f"{MONITOR_LABEL}.plist"
LISTENER_PLIST_NAME = f"{LISTENER_LABEL}.plist"
TASKS_FILE = MONITOR_DIR / "tasks.json"
PROJECT_ID = os.environ.get(
    "TERMINUS_PROJECT_ID", "bfe79c33-8ab0-4061-9849-08d3207c9927"
)


def _uid() -> int:
    return os.getuid()


def _gui_domain() -> str:
    return f"gui/{_uid()}"


def monitor_plist_path() -> Path:
    return Path.home() / "Library" / "LaunchAgents" / PLIST_NAME


def log(msg: str) -> None:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    line = f"[{ts}] [terminus-control] {msg}"
    print(line, flush=True)
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    with (STATE_DIR / "control.log").open("a", encoding="utf-8") as fh:
        fh.write(line + "\n")


def _launchctl(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["launchctl", *args],
        capture_output=True,
        text=True,
        check=False,
    )


def is_monitor_loaded() -> bool:
    target = f"{_gui_domain()}/{MONITOR_LABEL}"
    return _launchctl("print", target).returncode == 0


def is_listener_loaded() -> bool:
    target = f"{_gui_domain()}/{LISTENER_LABEL}"
    return _launchctl("print", target).returncode == 0


def start_monitor(*, kickstart: bool = False) -> tuple[bool, str]:
    plist = monitor_plist_path()
    if not plist.is_file():
        return False, f"plist missing — run install-hourly-launchd.sh first ({plist})"

    domain = _gui_domain()
    target = f"{domain}/{MONITOR_LABEL}"

    if is_monitor_loaded():
        if kickstart:
            _launchctl("kickstart", "-k", target)
        return True, "monitor already loaded (90-minute schedule)"

    proc = _launchctl("bootstrap", domain, str(plist))
    if proc.returncode != 0 and "already bootstrapped" not in (proc.stderr or "").lower():
        return False, (proc.stderr or proc.stdout or "bootstrap failed").strip()

    _launchctl("enable", target)
    return True, "monitor started (90-minute schedule; scans only unless AUTO_AGENT_FIX=1)"


def stop_monitor() -> tuple[bool, str]:
    if not is_monitor_loaded():
        return True, "monitor already stopped"

    proc = _launchctl("bootout", _gui_domain(), MONITOR_LABEL)
    if proc.returncode != 0:
        return False, (proc.stderr or proc.stdout or "bootout failed").strip()
    return True, "monitor stopped (no more scheduled runs)"


def _launchctl_job_detail(label: str) -> dict[str, str]:
    target = f"{_gui_domain()}/{label}"
    proc = _launchctl("print", target)
    if proc.returncode != 0:
        return {"loaded": "no", "state": "stopped", "last_exit": ""}
    text = proc.stdout or ""
    detail = {"loaded": "yes", "state": "unknown", "last_exit": "", "active": ""}
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("state ="):
            detail["state"] = line.split("=", 1)[1].strip()
        if line.startswith("last exit code ="):
            detail["last_exit"] = line.split("=", 1)[1].strip()
        if line.startswith("active count ="):
            detail["active"] = line.split("=", 1)[1].strip()
    return detail


def monitor_status_line() -> str:
    detail = _launchctl_job_detail(MONITOR_LABEL)
    if detail["loaded"] == "no":
        return "hourly monitor: stopped (not installed)"
    last_exit = detail.get("last_exit", "")
    if last_exit and last_exit not in {"0", ""}:
        return f"hourly monitor: BROKEN (last exit {last_exit})"
    if detail.get("active") == "1":
        return "hourly monitor: running now"
    return "hourly monitor: scheduled (every 90 minutes)"


def listener_status_line() -> str:
    detail = _launchctl_job_detail(LISTENER_LABEL)
    if detail["loaded"] == "no":
        return "remote commands: stopped"
    if detail.get("active") == "1":
        return "remote commands: running"
    return "remote commands: installed"


def _fetch_subs() -> list[dict]:
    stb_site = Path(
        os.environ.get(
            "STB_SITE",
            Path.home() / ".local/share/uv/tools/snorkelai-stb/lib/python3.13/site-packages",
        )
    )
    if stb_site.is_dir() and str(stb_site) not in sys.path:
        sys.path.insert(0, str(stb_site))
    from snorkelai_stb.submission_utils import fetch_folder_names, list_submission_ids

    subs = list_submission_ids(project_id=PROJECT_ID)
    fetch_folder_names(subs, fetch_all=True)
    return subs


def _folder_notes(folder: str) -> tuple[str | None, str]:
    subs = _fetch_subs()
    sub = find_submission_for_folder(subs, folder)
    if not sub:
        return None, f"no submission for folder {folder}"
    sid = sub["submission_id"]
    stb = os.environ.get(
        "STB_BIN",
        str(Path.home() / ".local/share/uv/tools/snorkelai-stb/bin/stb"),
    )
    proc = subprocess.run(
        [stb, "submissions", "feedback", sid],
        capture_output=True,
        text=True,
        timeout=180,
        check=False,
    )
    if proc.returncode != 0:
        return sid, f"feedback fetch failed: {(proc.stderr or proc.stdout)[:200]}"
    out_dir: Path | None = None
    for line in (proc.stdout + proc.stderr).splitlines():
        if "Feedback written to" in line:
            out_dir = Path(line.split("Feedback written to", 1)[1].strip())
            break
    if out_dir and (out_dir / "notes.txt").exists():
        return sid, (out_dir / "notes.txt").read_text(encoding="utf-8")
    return sid, "could not read feedback notes"


def run_monitor_now(
    *,
    dry_run: bool = False,
    force: bool = False,
    folder: str | None = None,
) -> tuple[bool, str]:
    python = MONITOR_DIR / ".venv" / "bin" / "python"
    script = MONITOR_DIR / "hourly_submission_check.py"
    if not python.is_file() or not script.is_file():
        return False, "monitor scripts missing — run install-hourly-launchd.sh"

    load_env_file()
    env = os.environ.copy()
    env["REPO_ROOT"] = str(REPO_ROOT)
    if DEFAULT_ENV_FILE.is_file():
        env["MONITOR_ENV_FILE"] = str(DEFAULT_ENV_FILE)
    venv_site = MONITOR_DIR / ".venv" / "lib"
    for site_pkg in venv_site.glob("python*/site-packages"):
        env["PYTHONPATH"] = str(site_pkg)
        break

    args = [str(python), str(script)]
    if dry_run:
        args.append("--dry-run")
    if force:
        args.append("--force")
        force_cap = os.environ.get("MAX_FIXES_PER_FORCE_RUN", "8")
        args.extend(["--max-fixes", force_cap])
    if folder:
        args.extend(["--folder", folder])

    proc = subprocess.run(
        args,
        cwd=str(REPO_ROOT),
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    combined = "\n".join(filter(None, [proc.stdout, proc.stderr])).strip()
    tail = combined.splitlines()[-1] if combined else f"exit {proc.returncode}"
    if proc.returncode != 0:
        return False, tail[:400]
    return True, tail[:400]


def status_text() -> str:
    state = load_state()
    from monitor_policy import is_paused, pause_remaining_sec

    lines = [
        monitor_status_line(),
        listener_status_line(),
        health_report(REPO_ROOT, state),
    ]
    if is_paused(state):
        lines.append(f"paused: {pause_remaining_sec(state) // 60}m remaining")
    queue = state.get("last_queue", {}).get("fix_queue") or []
    manual = state.get("last_queue", {}).get("manual_ui") or []
    if queue:
        lines.append("fix queue: " + ", ".join(queue[:5]))
    if manual:
        lines.append("finish in UI: " + ", ".join(manual[:5]))
    lines.append(f"AUTO_AGENT_FIX={os.environ.get('AUTO_AGENT_FIX', '1')}")
    return "\n".join(lines)


def queue_text() -> str:
    state = load_state()
    q = state.get("last_queue", {}) or {}
    lines = ["Fix queue: " + (", ".join(q.get("fix_queue") or []) or "none")]
    manual = q.get("manual_ui") or []
    if manual:
        lines.append("Finish in UI: " + ", ".join(manual))
    skipped = q.get("skipped") or []
    if skipped:
        lines.append(f"Skipped ({len(skipped)}):")
        for item in skipped[:6]:
            if isinstance(item, dict):
                lines.append(f"  {item.get('folder_name','?')}: {item.get('reason','?')}")
    return "\n".join(lines)


def handle_parsed_command(cmd: ParsedCommand, *, dry_run: bool = False) -> str:
    action = cmd.action
    args = cmd.args
    state = load_state()

    if action == "help":
        return help_text()
    if action == "start":
        ok, msg = start_monitor()
        return f"{'OK' if ok else 'FAIL'}: {msg}"
    if action == "stop":
        ok, msg = stop_monitor()
        return f"{'OK' if ok else 'FAIL'}: {msg}"
    if action == "resume":
        clear_pause(state)
        save_state(state)
        return "OK: pause cleared"
    if action == "pause":
        duration = " ".join(args) if args else os.environ.get("DEFAULT_PAUSE", "6h")
        seconds = parse_pause_duration(duration)
        if not seconds:
            return "FAIL: use pause 6h or pause 30m"
        msg = set_pause(state, seconds)
        save_state(state)
        return f"OK: {msg}"
    if action == "status":
        return status_text()
    if action == "queue":
        return queue_text()
    if action == "docker":
        return "Docker: up" if docker_ready() else "Docker: DOWN — start Docker Desktop"
    if action == "health":
        return health_report(REPO_ROOT, state)
    if action == "summary":
        return build_daily_summary(state)
    if action == "dry-run":
        folder = args[0] if args else None
        ok, msg = run_monitor_now(dry_run=True, force=True, folder=folder)
        return f"{'OK' if ok else 'FAIL'}: {msg}"
    if action == "prompt":
        folder = args[0] if args else None
        if not folder:
            return "FAIL: prompt needs a task folder name"
        folder = resolve_folder_name(folder, _fetch_subs(), REPO_ROOT) or folder
        script = MONITOR_DIR / "generate_fix_prompt.py"
        python = MONITOR_DIR / ".venv" / "bin" / "python"
        if not python.is_file():
            python = Path(sys.executable)
        proc = subprocess.run(
            [str(python), str(script), folder],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            check=False,
        )
        if proc.returncode != 0:
            return f"FAIL: {(proc.stderr or proc.stdout or 'prompt failed')[:300]}"
        return (proc.stdout or "prompt written").strip()[:400]
    if action == "run":
        folder = args[0] if args else None
        ok, msg = run_monitor_now(dry_run=dry_run, force=True, folder=folder)
        return f"{'OK' if ok else 'FAIL'}: {msg}"

    if action in {"exclude", "unexclude", "reset", "skip", "ui", "draft"} and not args:
        return f"FAIL: {action} needs a task folder name"

    subs = _fetch_subs() if action in {"exclude", "unexclude", "reset", "skip", "ui", "draft"} else []

    if action == "exclude":
        folder = resolve_folder_name(args[0], subs, REPO_ROOT)
        if not folder:
            return f"FAIL: unknown folder {args[0]}"
        sub = find_submission_for_folder(subs, folder)
        if not sub:
            return f"FAIL: no submission for {folder}"
        exclude_submission(sub["submission_id"], folder, reason="manual")
        return f"OK: excluded {folder}"
    if action == "unexclude":
        folder = resolve_folder_name(args[0], subs, REPO_ROOT)
        if not folder:
            return f"FAIL: unknown folder {args[0]}"
        sub = find_submission_for_folder(subs, folder)
        if not sub:
            return f"FAIL: no submission for {folder}"
        if unexclude_submission(sub["submission_id"]):
            return f"OK: unexcluded {folder}"
        return f"OK: {folder} was not excluded"
    if action == "reset":
        folder = resolve_folder_name(args[0], subs, REPO_ROOT)
        if not folder:
            return f"FAIL: unknown folder {args[0]}"
        sub = find_submission_for_folder(subs, folder)
        if not sub:
            return f"FAIL: no submission for {folder}"
        runs = state.get("runs", {})
        if sub["submission_id"] in runs:
            del runs[sub["submission_id"]]
            save_state(state)
            return f"OK: reset state for {folder}"
        return f"OK: no state entry for {folder}"
    if action == "skip":
        folder = resolve_folder_name(args[0], subs, REPO_ROOT)
        if not folder:
            return f"FAIL: unknown folder {args[0]}"
        from monitor_policy import add_skip_once

        add_skip_once(state, folder)
        save_state(state)
        return f"OK: skip {folder} for next scheduled run"
    if action == "ui":
        folder = resolve_folder_name(args[0], subs, REPO_ROOT)
        if not folder:
            return f"FAIL: unknown folder {args[0]}"
        _sid, notes = _folder_notes(folder)
        if notes.startswith("feedback") or notes.startswith("no submission"):
            return f"FAIL: {notes}"
        return build_finish_ui_checklist(folder, notes)
    if action == "draft":
        folder = resolve_folder_name(args[0], subs, REPO_ROOT)
        if not folder:
            return f"FAIL: unknown folder {args[0]}"
        sub = find_submission_for_folder(subs, folder)
        run_data = state.get("runs", {}).get(sub["submission_id"], {}) if sub else {}
        _sid, notes = _folder_notes(folder)
        if notes.startswith("feedback") or notes.startswith("no submission"):
            return f"FAIL: {notes}"
        return draft_explanations(folder, notes, run_data)

    return f"unknown command '{action}' — send help"


def handle_command_text(body: str, *, dry_run: bool = False) -> str:
    parsed = parse_command(body)
    if not parsed:
        return help_text()
    return handle_parsed_command(parsed, dry_run=dry_run)


def main() -> int:
    load_env_file()
    sync_tasks_json(REPO_ROOT, TASKS_FILE)
    import argparse

    parser = argparse.ArgumentParser(description="Control Snorkel submission monitor")
    parser.add_argument("action", choices=["start", "stop", "status", "run"])
    parser.add_argument("--dry-run", action="store_true", help="For run: scan only, no agent")
    args = parser.parse_args()

    if args.action == "start":
        ok, msg = start_monitor()
        log(msg)
        print(msg)
        return 0 if ok else 1
    if args.action == "stop":
        ok, msg = stop_monitor()
        log(msg)
        print(msg)
        return 0 if ok else 1
    if args.action == "status":
        print(status_text())
        return 0
    if args.action == "run":
        ok, msg = run_monitor_now(dry_run=args.dry_run, force=True)
        log(msg)
        print(msg)
        return 0 if ok else 1
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
