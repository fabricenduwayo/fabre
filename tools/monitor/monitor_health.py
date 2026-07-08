"""Health checks: Docker, stb, bridge orphans, git hygiene, Cursor preflight."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


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


def stb_ok() -> tuple[bool, str]:
    stb = os.environ.get(
        "STB_BIN",
        str(Path.home() / ".local/share/uv/tools/snorkelai-stb/bin/stb"),
    )
    if not Path(stb).is_file():
        return False, "stb binary not found"
    try:
        proc = subprocess.run(
            [stb, "--help"],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired) as exc:
        return False, str(exc)
    if proc.returncode != 0:
        return False, "stb --help failed"
    return True, "installed"


def cursor_app_running() -> bool:
    """True when the Cursor desktop app process is running (macOS local SDK bridge)."""
    if sys.platform != "darwin":
        return True
    try:
        proc = subprocess.run(
            ["pgrep", "-x", "Cursor"],
            capture_output=True,
            text=True,
            check=False,
        )
        return proc.returncode == 0
    except FileNotFoundError:
        return False


def local_agent_ready() -> tuple[bool, str]:
    """Fast preflight before cursor_sdk local bridge (avoids long ReadTimeout hangs)."""
    if os.environ.get("REQUIRE_CURSOR_OPEN", "1").strip().lower() in {
        "0",
        "false",
        "no",
        "off",
    }:
        return True, ""
    if cursor_app_running():
        return True, ""
    return False, (
        "Cursor is not running. Open Cursor.app before agent fixes. "
        "Scheduled scans do not need Cursor (set AUTO_AGENT_FIX=0)."
    )


def bridge_orphan_count(repo_root: Path) -> int:
    pattern = f"cursor-sdk-bridge.js.*{repo_root}"
    try:
        proc = subprocess.run(
            ["pgrep", "-f", pattern],
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError:
        return 0
    if proc.returncode != 0:
        return 0
    return len([line for line in proc.stdout.splitlines() if line.strip()])


def git_dirty_task_folders(repo_root: Path) -> list[str]:
    proc = subprocess.run(
        ["git", "-C", str(repo_root), "status", "--short"],
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        return []
    folders: set[str] = set()
    for line in proc.stdout.splitlines():
        line = line.strip()
        if not line or line.startswith("??"):
            parts = line.split()
            if len(parts) >= 2:
                path = parts[-1].split("/")[0]
                if (repo_root / path / "task.toml").is_file():
                    folders.add(path)
            continue
        parts = line.split()
        if not parts:
            continue
        path = parts[-1].split("/")[0]
        if (repo_root / path / "task.toml").is_file():
            folders.add(path)
    return sorted(folders)


def health_report(repo_root: Path, state: dict | None = None) -> str:
    docker = "up" if docker_ready() else "DOWN"
    stb_status, stb_detail = stb_ok()
    bridges = bridge_orphan_count(repo_root)
    dirty = git_dirty_task_folders(repo_root)
    cursor = "running" if cursor_app_running() else "NOT RUNNING"
    auto_fix = os.environ.get("AUTO_AGENT_FIX", "0").strip()
    lines = [
        f"Docker: {docker}",
        f"stb: {'ok' if stb_status else 'FAIL'} ({stb_detail})",
        f"Cursor app: {cursor}",
        f"AUTO_AGENT_FIX: {auto_fix}",
        f"cursor-sdk bridges: {bridges} orphan(s)",
    ]
    if state:
        from monitor_policy import is_paused, pause_remaining_sec

        if is_paused(state):
            lines.append(f"paused: {pause_remaining_sec(state) // 60}m remaining")
        else:
            lines.append("paused: no")
    if dirty:
        lines.append(f"uncommitted task folders ({len(dirty)}): {', '.join(dirty[:5])}")
    else:
        lines.append("git: task folders clean")
    return "\n".join(lines)
