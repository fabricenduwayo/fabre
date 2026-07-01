#!/bin/bash
# Wrapper for launchd / manual runs. Sources .env, activates venv, runs monitor.
set -euo pipefail

MONITOR_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$MONITOR_DIR/../.." && pwd)"
VENV="$MONITOR_DIR/.venv"
LOG_DIR="$REPO_ROOT/.review-scratch/monitor"

mkdir -p "$LOG_DIR"

if [[ -f "$MONITOR_DIR/.env" ]]; then
  set -a
  # shellcheck disable=SC1091
  source "$MONITOR_DIR/.env"
  set +a
fi

export REPO_ROOT
export PATH="/opt/homebrew/bin:/usr/local/bin:$HOME/.local/bin:$PATH"

if [[ ! -x "$VENV/bin/python" ]]; then
  echo "Monitor venv missing. Run: $MONITOR_DIR/install-hourly-launchd.sh" >&2
  exit 1
fi

# Keep machine awake for the agent run (display may sleep; system stays up).
exec caffeinate -imsu "$VENV/bin/python" "$MONITOR_DIR/hourly_submission_check.py" "$@"
