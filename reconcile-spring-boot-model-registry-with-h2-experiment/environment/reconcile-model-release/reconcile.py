#!/usr/bin/env python3
"""Reconcile registry API evidence with the H2 experiment store."""

from __future__ import annotations

import sys

DEFAULT_DB_URL = "jdbc:h2:file:/app/experiment-db/experiments"
DEFAULT_OUTPUT = "/app/build/release-decision.json"


def main() -> int:
  print("reconcile-model-release: not yet implemented", file=sys.stderr)
  return 0


if __name__ == "__main__":
  raise SystemExit(main())
