#!/bin/bash
# Phone commands via ntfy (no Messages / Full Disk Access needed).
set -uo pipefail

MONITOR_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$MONITOR_DIR/../.." && pwd)"
VENV="$MONITOR_DIR/.venv"
SUPPORT_ENV="$HOME/Library/Application Support/SnorkelTerminus/monitor.env"

export REPO_ROOT MONITOR_DIR MONITOR_ENV_FILE="$SUPPORT_ENV"
export SNORKEL_MSG_SOURCE=none
export NTFY_CMD_ENABLE=1
export PATH="/opt/homebrew/bin:/usr/local/bin:$HOME/.local/bin:$PATH"

if [[ -f "$SUPPORT_ENV" ]]; then
  set -a
  # shellcheck disable=SC1091
  source "$SUPPORT_ENV"
  set +a
elif [[ -f "$MONITOR_DIR/.env" ]]; then
  set -a
  # shellcheck disable=SC1091
  source "$MONITOR_DIR/.env"
  set +a
fi

if [[ -z "${NTFY_CMD_TOPIC:-}" && -z "${NTFY_TOPIC:-}" ]]; then
  echo "Set NTFY_CMD_TOPIC in tools/monitor/.env (same topic you subscribe to on the ntfy iPhone app)." >&2
  exit 1
fi

POLL_SEC="${IMESSAGE_POLL_SEC:-20}"
TOPIC="${NTFY_CMD_TOPIC:-$NTFY_TOPIC}"
echo "Terminus ntfy listener on topic: $TOPIC"
echo "From phone (ntfy app): send message 'status', 'stop', 'start', or 'run'"
echo "Poll every ${POLL_SEC}s. Ctrl+C to stop."

while true; do
  "$VENV/bin/python" "$MONITOR_DIR/imessage_command_listener.py" --once || true
  sleep "$POLL_SEC"
done
