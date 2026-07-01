#!/usr/bin/env python3
"""Start/stop/status for the Snorkel submission monitor (launchd)."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

MONITOR_DIR = Path(__file__).resolve().parent
REPO_ROOT = Path(os.environ.get("REPO_ROOT", MONITOR_DIR.parent.parent)).resolve()
STATE_DIR = REPO_ROOT / ".review-scratch" / "monitor"
MONITOR_LABEL = "com.snorkel.submission-monitor"
LISTENER_LABEL = "com.snorkel.terminus-imessage-control"
PLIST_NAME = f"{MONITOR_LABEL}.plist"


def _uid() -> int:
    return os.getuid()


def _gui_domain() -> str:
    return f"gui/{_uid()}"


def monitor_plist_path() -> Path:
    return Path.home() / "Library" / "LaunchAgents" / PLIST_NAME


def run_hourly_script() -> Path:
    return MONITOR_DIR / "run-hourly.sh"


def load_env_file() -> None:
    candidates: list[Path] = []
    override = os.environ.get("MONITOR_ENV_FILE", "").strip()
    if override:
        candidates.append(Path(override))
    candidates.append(Path.home() / "Library/Application Support/SnorkelTerminus/monitor.env")
    candidates.append(MONITOR_DIR / ".env")
    for env_path in candidates:
        if not env_path.is_file():
            continue
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            os.environ.setdefault(key.strip(), value.strip())
        return


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
    proc = _launchctl("print", target)
    return proc.returncode == 0


def is_listener_loaded() -> bool:
    target = f"{_gui_domain()}/{LISTENER_LABEL}"
    proc = _launchctl("print", target)
    return proc.returncode == 0


def start_monitor(*, kickstart: bool = True) -> tuple[bool, str]:
    plist = monitor_plist_path()
    if not plist.is_file():
        return False, f"plist missing — run install-hourly-launchd.sh first ({plist})"

    domain = _gui_domain()
    target = f"{domain}/{MONITOR_LABEL}"

    if is_monitor_loaded():
        if kickstart:
            _launchctl("kickstart", "-k", target)
        return True, "monitor already running (re-kicked)"

    proc = _launchctl("bootstrap", domain, str(plist))
    if proc.returncode != 0 and "already bootstrapped" not in (proc.stderr or "").lower():
        return False, (proc.stderr or proc.stdout or "bootstrap failed").strip()

    _launchctl("enable", target)
    if kickstart:
        _launchctl("kickstart", "-k", target)
    return True, "monitor started (hourly schedule active)"


def stop_monitor() -> tuple[bool, str]:
    if not is_monitor_loaded():
        return True, "monitor already stopped"

    proc = _launchctl("bootout", _gui_domain(), MONITOR_LABEL)
    if proc.returncode != 0:
        return False, (proc.stderr or proc.stdout or "bootout failed").strip()
    return True, "monitor stopped (no more hourly runs)"


def _cooldown_summary() -> str:
    state_file = STATE_DIR / "state.json"
    if not state_file.is_file():
        return "no prior runs"
    try:
        state = json.loads(state_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return "state unreadable"
    until = state.get("next_fix_allowed_after")
    queue = state.get("last_queue", {}).get("fix_queue") or []
    parts = []
    if until:
        parts.append(f"next fix after {until}")
    if queue:
        parts.append(f"queue: {', '.join(queue[:3])}")
    return " | ".join(parts) if parts else "idle queue"


def _launchctl_job_detail() -> dict[str, str]:
    target = f"{_gui_domain()}/{MONITOR_LABEL}"
    proc = _launchctl("print", target)
    if proc.returncode != 0:
        return {"loaded": "no", "state": "stopped", "last_exit": ""}
    text = proc.stdout or ""
    state = "unknown"
    last_exit = ""
    active = ""
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("state ="):
            state = line.split("=", 1)[1].strip()
        if line.startswith("last exit code ="):
            last_exit = line.split("=", 1)[1].strip()
        if line.startswith("active count ="):
            active = line.split("=", 1)[1].strip()
    return {"loaded": "yes", "state": state, "last_exit": last_exit, "active": active}


def monitor_status_line() -> str:
    detail = _launchctl_job_detail()
    if detail["loaded"] == "no":
        return "hourly Cursor fix: stopped (not installed)"
    last_exit = detail.get("last_exit", "")
    if last_exit and last_exit not in {"0", ""}:
        return f"hourly Cursor fix: BROKEN (last exit {last_exit}) — run install-hourly-launchd.sh"
    if detail.get("active") == "1":
        return "hourly Cursor fix: running now"
    return "hourly Cursor fix: scheduled (every hour)"


def run_monitor_now(*, dry_run: bool = False, force: bool = False) -> tuple[bool, str]:
    python = MONITOR_DIR / ".venv" / "bin" / "python"
    script = MONITOR_DIR / "hourly_submission_check.py"
    if not python.is_file() or not script.is_file():
        return False, "monitor scripts missing — run install-hourly-launchd.sh"

    load_env_file()
    env = os.environ.copy()
    env["REPO_ROOT"] = str(REPO_ROOT)
    support_env = Path.home() / "Library/Application Support/SnorkelTerminus/monitor.env"
    if support_env.is_file():
        env["MONITOR_ENV_FILE"] = str(support_env)
    venv_site = MONITOR_DIR / ".venv" / "lib"
    for site_pkg in venv_site.glob("python*/site-packages"):
        env["PYTHONPATH"] = str(site_pkg)
        break

    args = [str(python), str(script)]
    if dry_run:
        args.append("--dry-run")
    if force:
        args.append("--force")

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
        return False, tail[:300]
    return True, tail[:300]


def status_text() -> str:
    listener = "running" if is_listener_loaded() else "stopped"
    return (
        f"{monitor_status_line()}\n"
        f"iMessage listener: {listener}\n"
        f"{_cooldown_summary()}\n"
        f"Text 'run' to trigger one Cursor fix now"
    )


def handle_command(command: str, *, dry_run: bool = False) -> str:
    """Execute a control command and return a short reply for iMessage."""
    cmd = command.strip().lower()
    if cmd == "start":
        ok, msg = start_monitor()
        run_ok, run_msg = run_monitor_now(force=True)
        lines = [f"{'OK' if ok else 'FAIL'}: {msg}"]
        lines.append(f"{'OK' if run_ok else 'FAIL'}: kick fix — {run_msg}")
        return "\n".join(lines)
    if cmd == "stop":
        ok, msg = stop_monitor()
        return f"{'OK' if ok else 'FAIL'}: {msg}"
    if cmd == "status":
        return status_text()
    if cmd == "run":
        ok, msg = run_monitor_now(dry_run=dry_run, force=True)
        prefix = "OK" if ok else "FAIL"
        return f"{prefix}: one-shot run — {msg}"
    return f"unknown command '{command}' — try start-terminus, stop-terminus, status-terminus, run-terminus"


def main() -> int:
    load_env_file()
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
        text = status_text()
        print(text)
        return 0
    if args.action == "run":
        ok, msg = run_monitor_now(dry_run=args.dry_run)
        log(msg)
        print(msg)
        return 0 if ok else 1
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
