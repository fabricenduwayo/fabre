"""Load monitor configuration from tools/monitor/.env only."""

from __future__ import annotations

import os
from pathlib import Path

MONITOR_DIR = Path(__file__).resolve().parent
DEFAULT_ENV_FILE = MONITOR_DIR / ".env"


def load_env_file() -> Path | None:
    """Load key=value pairs from the monitor .env file (first match wins)."""
    override = os.environ.get("MONITOR_ENV_FILE", "").strip()
    candidates = [Path(override)] if override else []
    candidates.append(DEFAULT_ENV_FILE)
    for env_path in candidates:
        if not env_path.is_file():
            continue
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            os.environ.setdefault(key.strip(), value.strip())
        return env_path
    return None
