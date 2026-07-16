#!/usr/bin/env python3
"""Diagnose Cursor cloud agent config — prints error details, never secrets."""
from __future__ import annotations

import os
import sys
from pathlib import Path

MONITOR_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(MONITOR_DIR))

from monitor_env import load_env_file
from monitor_agent import (
    resolve_github_branch,
    resolve_github_repo_url,
    resolve_github_starting_ref,
    resolve_cursor_model,
)
from monitor_state import REPO_ROOT

load_env_file()

api_key = os.environ.get("CURSOR_API_KEY", "")
if not api_key or api_key.startswith("cursor_your"):
    print("FAIL: CURSOR_API_KEY missing in tools/monitor/.env")
    sys.exit(1)

repo_url = resolve_github_repo_url(REPO_ROOT)
branch = resolve_github_branch(REPO_ROOT)
starting_ref = resolve_github_starting_ref(REPO_ROOT)
model = resolve_cursor_model()

print("config:")
print(f"  repo_url: {repo_url}")
print(f"  branch: {branch}")
print(f"  starting_ref: {starting_ref[:12]}… ({len(starting_ref)} chars)")
print(f"  model: {model}")
print(f"  api_key_prefix: {api_key[:8]}…")

from cursor_sdk import Agent, AgentOptions, CloudAgentOptions, CloudRepository, CursorAgentError

variants = [
    ("commit_sha + work_on_branch", starting_ref, True),
    ("branch_name + work_on_branch", branch, True),
    ("branch_name only", branch, False),
    ("main + work_on_branch", "main", True),
]

for label, ref, work_on_branch in variants:
    print(f"\n--- try: {label} (ref={ref!r}) ---")
    try:
        result = Agent.prompt(
            "Reply with exactly: pong",
            AgentOptions(
                api_key=api_key,
                model=model,
                cloud=CloudAgentOptions(
                    repos=[CloudRepository(url=repo_url, starting_ref=ref)],
                    work_on_current_branch=work_on_branch,
                    auto_create_pr=False,
                ),
            ),
        )
        print(f"OK status={result.status} result={str(getattr(result, 'result', ''))[:200]}")
        sys.exit(0)
    except CursorAgentError as exc:
        print(f"CursorAgentError:")
        print(f"  message: {exc.message}")
        for attr in ("status_code", "error_type", "details", "body", "response"):
            if hasattr(exc, attr):
                val = getattr(exc, attr)
                if val:
                    print(f"  {attr}: {val}")
        # dump all public attrs
        for k, v in vars(exc).items():
            if k != "message" and v:
                print(f"  {k}: {v}")

print("\nAll variants failed.")
sys.exit(1)
