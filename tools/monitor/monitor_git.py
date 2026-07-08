"""Git commit/push after successful monitor fixes."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path


def _enabled() -> bool:
    return os.environ.get("AUTO_GIT_COMMIT", "1").strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }


def commit_and_push_repo(repo_root: Path, folder: str, summary: str) -> tuple[bool, str]:
    """Stage all repo changes, commit, and push after a successful fix."""
    if not _enabled():
        return False, "AUTO_GIT_COMMIT=0"

    status = subprocess.run(
        ["git", "-C", str(repo_root), "status", "--porcelain"],
        capture_output=True,
        text=True,
        check=False,
    )
    if status.returncode != 0:
        return False, status.stderr.strip() or "git status failed"
    if not status.stdout.strip():
        return False, "nothing to commit"

    add = subprocess.run(
        ["git", "-C", str(repo_root), "add", "-A"],
        capture_output=True,
        text=True,
        check=False,
    )
    if add.returncode != 0:
        return False, add.stderr.strip() or "git add failed"

    short = " ".join(summary.split())[:120] if summary else "monitor fix"
    message = f"terminus: {folder} — {short}"
    commit = subprocess.run(
        ["git", "-C", str(repo_root), "commit", "-m", message],
        capture_output=True,
        text=True,
        check=False,
    )
    if commit.returncode != 0:
        return False, commit.stderr.strip() or "git commit failed"

    push = subprocess.run(
        ["git", "-C", str(repo_root), "push"],
        capture_output=True,
        text=True,
        check=False,
    )
    if push.returncode != 0:
        return False, f"committed but push failed: {push.stderr.strip() or push.stdout.strip()}"

    return True, message
