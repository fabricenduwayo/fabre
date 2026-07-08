"""Local oracle pre-check — skip Cursor agent when harbor already passes."""

from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path


def harbor_bin() -> str:
    return os.environ.get(
        "HARBOR_BIN",
        str(Path.home() / ".local/share/uv/tools/snorkelai-stb/bin/harbor"),
    )


def oracle_reward(folder: str, *, repo_root: Path) -> float | None:
    """Run harbor oracle and parse reward, or None on failure/timeout."""
    if not os.environ.get("ORACLE_PRECHECK", "1").strip().lower() in {"1", "true", "yes"}:
        return None
    try:
        proc = subprocess.run(
            [harbor_bin(), "run", "-a", "oracle", "-p", folder],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            timeout=int(os.environ.get("ORACLE_PRECHECK_TIMEOUT_SEC", "900")),
            check=False,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None
    text = (proc.stdout or "") + "\n" + (proc.stderr or "")
    for pattern in (
        r"reward[:\s]+([01](?:\.\d+)?)",
        r"Reward:\s*([01](?:\.\d+)?)",
        r"reward\.txt.*?([01](?:\.\d+)?)",
    ):
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            try:
                return float(match.group(1))
            except ValueError:
                continue
    if proc.returncode == 0 and "1.0" in text:
        return 1.0
    return 0.0 if proc.returncode != 0 else None


def oracle_passes(folder: str, *, repo_root: Path) -> bool:
    reward = oracle_reward(folder, repo_root=repo_root)
    return reward is not None and reward >= 1.0
