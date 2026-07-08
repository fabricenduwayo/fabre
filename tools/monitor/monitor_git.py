"""Git pull, commit, and push for the submission monitor."""

from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path

from monitor_agent import resolve_github_branch, resolve_github_repo_url

GIT_AUTHOR_NAME = os.environ.get("GIT_AUTHOR_NAME", "Fabrice Nduwayo")
GIT_AUTHOR_EMAIL = os.environ.get("GIT_AUTHOR_EMAIL", "fabrice.nduwayo12@gmail.com")


def _enabled() -> bool:
    return os.environ.get("AUTO_GIT_COMMIT", "1").strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }


def _github_token() -> str:
    return os.environ.get("GITHUB_TOKEN", "").strip()


def _auth_repo_url(https_url: str, token: str) -> str:
    if not token:
        return https_url
    if re.match(r"https://x-access-token:[^@]+@", https_url):
        return https_url
    return https_url.replace("https://", f"https://x-access-token:{token}@", 1)


def _git_commit_env() -> list[str]:
    return [
        "-c",
        f"user.name={GIT_AUTHOR_NAME}",
        "-c",
        f"user.email={GIT_AUTHOR_EMAIL}",
    ]


def pull_latest(repo_root: Path, *, branch: str | None = None) -> tuple[bool, str]:
    """Pull latest from GitHub after a cloud agent push."""
    branch = branch or resolve_github_branch(repo_root)
    token = _github_token()
    if token:
        url = _auth_repo_url(resolve_github_repo_url(repo_root) + ".git", token)
        proc = subprocess.run(
            ["git", "-C", str(repo_root), "pull", "--rebase", url, branch],
            capture_output=True,
            text=True,
            check=False,
        )
    else:
        proc = subprocess.run(
            ["git", "-C", str(repo_root), "pull", "--rebase", "origin", branch],
            capture_output=True,
            text=True,
            check=False,
        )
    out = ((proc.stdout or "") + "\n" + (proc.stderr or "")).strip()
    if proc.returncode != 0:
        return False, out[-800:] if out else "git pull failed"
    return True, out[-400:] if out else "pulled"


def push_repo(repo_root: Path, *, branch: str | None = None) -> tuple[bool, str]:
    """Push to GitHub using GITHUB_TOKEN when set."""
    branch = branch or resolve_github_branch(repo_root)
    token = _github_token()
    if token:
        url = _auth_repo_url(resolve_github_repo_url(repo_root) + ".git", token)
        proc = subprocess.run(
            ["git", "-C", str(repo_root), "push", url, f"HEAD:{branch}"],
            capture_output=True,
            text=True,
            check=False,
        )
    else:
        proc = subprocess.run(
            ["git", "-C", str(repo_root), "push", "origin", branch],
            capture_output=True,
            text=True,
            check=False,
        )
    out = ((proc.stdout or "") + "\n" + (proc.stderr or "")).strip()
    if proc.returncode != 0:
        return False, out[-800:] if out else "git push failed"
    return True, out[-200:] if out else "pushed"


def commit_and_push_repo(repo_root: Path, folder: str, summary: str) -> tuple[bool, str]:
    """Stage all repo changes, commit (single author), and push."""
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
        ["git", "-C", str(repo_root), *_git_commit_env(), "commit", "-m", message],
        capture_output=True,
        text=True,
        check=False,
    )
    if commit.returncode != 0:
        return False, commit.stderr.strip() or "git commit failed"

    pushed, push_msg = push_repo(repo_root)
    if not pushed:
        return False, f"committed but push failed: {push_msg}"
    return True, message
