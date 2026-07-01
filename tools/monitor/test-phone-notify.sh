#!/bin/bash
# Send test notifications to every channel enabled in tools/monitor/.env
set -euo pipefail
MONITOR_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [[ -f "$MONITOR_DIR/.env" ]]; then
  set -a
  # shellcheck disable=SC1091
  source "$MONITOR_DIR/.env"
  set +a
fi
export PYTHONPATH="$MONITOR_DIR"
export MONITOR_DIR
"$MONITOR_DIR/.venv/bin/python" - <<'PY'
import os
import sys
sys.path.insert(0, os.environ.get("MONITOR_DIR", "."))
from notifications import notify_all, notify_imessage, notify_ntfy, notify_macos

title = "Snorkel monitor test"
msg = "If you see this on your phone, phone notifications work."

notify_macos(title, msg, subtitle="Mac only")
notify_all(title, msg, subtitle="all channels")
print("macOS:", os.environ.get("NOTIFY_MACOS", "1"))
print("iMessage:", os.environ.get("NOTIFY_IMESSAGE", "0"), "→", os.environ.get("IMESSAGE_TO", "(unset)"))
print("ntfy:", os.environ.get("NOTIFY_NTFY", "0"), "→", os.environ.get("NTFY_TOPIC", "(unset)"))
PY
