#!/bin/bash
# Quick health check for phone command listeners.
set -uo pipefail

MONITOR_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CHAT_SRC="$HOME/Library/Messages/chat.db"

echo "=== Terminus listener diagnose ==="

if cp "$CHAT_SRC" /tmp/snorkel-diag-chat.db 2>/dev/null; then
  echo "OK  Mac can read Messages database (Full Disk Access works in this terminal)"
  "$MONITOR_DIR/.venv/bin/python" - <<'PY'
import sqlite3
from pathlib import Path
conn = sqlite3.connect("file:/tmp/snorkel-diag-chat.db?mode=ro", uri=True)
max_id = conn.execute("SELECT MAX(ROWID) FROM message").fetchone()[0]
print(f"    Latest message ROWID on Mac: {max_id}")
PY
else
  echo "FAIL Mac cannot read Messages database from this terminal"
  echo "     Add Terminal.app (or Cursor.app) to Full Disk Access, or use ntfy instead:"
  echo "     ./run-ntfy-listener-loop.sh"
fi

if [[ -f "$MONITOR_DIR/.env" ]]; then
  # shellcheck disable=SC1091
  source "$MONITOR_DIR/.env"
fi
if [[ -n "${NTFY_CMD_TOPIC:-}${NTFY_TOPIC:-}" ]]; then
  echo "OK  ntfy topic configured: ${NTFY_CMD_TOPIC:-$NTFY_TOPIC}"
else
  echo "—   ntfy not configured (optional — reliable phone control without iMessage sync)"
fi

echo ""
pgrep -fl "run-imessage-listener|run-ntfy-listener|SnorkelTerminusListener" || echo "No listener process running"
echo ""
echo "iPhone texts only work if they appear in Messages.app ON THIS MAC."
echo "Open Messages on the Mac — if your phone texts are not there, iMessage sync is the issue."
echo ""
echo "Reliable option: ntfy app on iPhone → ./run-ntfy-listener-loop.sh"
