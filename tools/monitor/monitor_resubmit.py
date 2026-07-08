"""Run per-task resubmit scripts after cloud agent fixes."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def run_task_resubmit(
    folder: str,
    tasks_map: dict,
    repo_root: Path,
) -> tuple[bool, str]:
    """Execute the task's resubmit script from tasks.json."""
    meta = tasks_map.get(folder, {})
    script_rel = meta.get("resubmit_script")
    if not script_rel:
        return False, f"no resubmit_script for {folder} in tasks.json"

    script = repo_root / script_rel
    if not script.is_file():
        return False, f"resubmit script not found: {script}"

    cmd = [sys.executable, str(script)]
    arg = meta.get("resubmit_arg")
    if arg:
        cmd.append(str(arg))

    proc = subprocess.run(
        cmd,
        cwd=str(repo_root),
        capture_output=True,
        text=True,
        timeout=int(__import__("os").environ.get("RESUBMIT_TIMEOUT_SEC", "600")),
        check=False,
    )
    out = ((proc.stdout or "") + "\n" + (proc.stderr or "")).strip()
    if proc.returncode != 0:
        return False, out[-800:] if out else f"resubmit exited {proc.returncode}"
    return True, out[-400:] if out else "resubmit OK"
