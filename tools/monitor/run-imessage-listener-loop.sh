#!/bin/bash
# Run iMessage listener in your login session. Requires Full Disk Access for your terminal app.
set -uo pipefail

MONITOR_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$MONITOR_DIR/../.." && pwd)"
VENV="$MONITOR_DIR/.venv"
SUPPORT_ENV="$HOME/Library/Application Support/SnorkelTerminus/monitor.env"
CHAT_SRC="$HOME/Library/Messages/chat.db"
CHAT_COPY="/tmp/snorkel-messages-chat.db"
WARNED=0

export REPO_ROOT MONITOR_DIR MONITOR_ENV_FILE="$SUPPORT_ENV"
export SNORKEL_MSG_SOURCE=chatdb
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

sync_chat_db() {
  if cp "$CHAT_SRC" "$CHAT_COPY" 2>/dev/null; then
    export SNORKEL_CHAT_DB="$CHAT_COPY"
    return 0
  fi
  unset SNORKEL_CHAT_DB
  if [[ "$WARNED" -eq 0 ]]; then
    WARNED=1
    echo ""
    echo "ERROR: cannot read $CHAT_SRC (Operation not permitted)"
    echo ""
    echo "Grant Full Disk Access to the app running this script:"
    echo "  System Settings → Privacy & Security → Full Disk Access"
    echo "  Add: /System/Applications/Utilities/Terminal.app"
    echo "  (or Cursor.app if you use the Cursor integrated terminal)"
    echo ""
    echo "Toggle ON, quit Terminal/Cursor fully, reopen, run this script again."
    echo ""
echo ""
echo "IMPORTANT: run only ONE listener (not both .app and run-imessage-listener-loop.sh)."
echo "  pkill -f SnorkelTerminusListener; pkill -f run-imessage-listener-loop"
echo ""
  fi
  return 1
}

POLL_SEC="${IMESSAGE_POLL_SEC:-20}"
echo "Terminus iMessage listener (terminal session). Poll every ${POLL_SEC}s. Ctrl+C to stop."

while true; do
  if sync_chat_db; then
    "$VENV/bin/python" "$MONITOR_DIR/imessage_command_listener.py" --once || true
  fi
  sleep "$POLL_SEC"
done
