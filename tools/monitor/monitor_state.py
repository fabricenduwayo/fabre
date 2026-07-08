#!/usr/bin/env python3
"""Shared monitor state paths and load/save."""

from __future__ import annotations

import json
import os
from pathlib import Path

MONITOR_DIR = Path(__file__).resolve().parent
REPO_ROOT = Path(os.environ.get("REPO_ROOT", MONITOR_DIR.parent.parent)).resolve()
STATE_DIR = REPO_ROOT / ".review-scratch" / "monitor"
STATE_FILE = STATE_DIR / "state.json"
EXCLUSIONS_FILE = MONITOR_DIR / "review_exclusions.json"
TASKS_FILE = MONITOR_DIR / "tasks.json"


def load_state() -> dict:
    if not STATE_FILE.exists():
        return {"runs": {}, "last_check": None}
    return json.loads(STATE_FILE.read_text(encoding="utf-8"))


def save_state(state: dict) -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
