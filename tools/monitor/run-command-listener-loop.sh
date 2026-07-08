#!/bin/bash
# Run Telegram/ntfy command listener in foreground (no launchd).
set -uo pipefail

MONITOR_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$MONITOR_DIR/../.." && pwd)"
VENV="$MONITOR_DIR/.venv"

export REPO_ROOT MONITOR_DIR
export PATH="/opt/homebrew/bin:/usr/local/bin:$HOME/.local/bin:$PATH"

if [[ -f "$MONITOR_DIR/.env" ]]; then
  set -a
  # shellcheck disable=SC1091
  source "$MONITOR_DIR/.env"
  set +a
fi

if [[ ! -x "$VENV/bin/python" ]]; then
  echo "Run install-hourly-launchd.sh first." >&2
  exit 1
fi

POLL_SEC="${COMMAND_POLL_SEC:-20}"
echo "Terminus command listener (foreground). Poll every ${POLL_SEC}s. Ctrl+C to stop."
echo "Commands: stop | start | status | run"

exec "$VENV/bin/python" "$MONITOR_DIR/command_listener.py"
