#!/bin/bash
# Stop all Snorkel monitor processes and unload launchd jobs.
set -euo pipefail

MONITOR_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$MONITOR_DIR/../.." && pwd)"
GUI="gui/$(id -u)"

echo "==> Stopping Snorkel monitor processes"

pkill -f 'cursor-sdk-bridge.js.*snorkel-ai' 2>/dev/null || true
pkill -f 'hourly_submission_check.py' 2>/dev/null || true
pkill -f 'command_listener.py' 2>/dev/null || true
pkill -f 'imessage_command_listener.py' 2>/dev/null || true
pkill -f 'run-hourly.sh' 2>/dev/null || true
pkill -f 'run-command-listener' 2>/dev/null || true
pkill -f 'run-imessage-listener' 2>/dev/null || true
pkill -f 'SnorkelTerminusListener' 2>/dev/null || true
pkill -f 'caffeinate.*hourly_submission_check' 2>/dev/null || true

sleep 1
pkill -9 -f 'cursor-sdk-bridge.js.*snorkel-ai' 2>/dev/null || true
pkill -9 -f 'hourly_submission_check.py' 2>/dev/null || true
pkill -9 -f 'command_listener.py' 2>/dev/null || true

echo "==> Unloading launchd jobs"
launchctl bootout "$GUI/com.snorkel.submission-monitor" 2>/dev/null || true
launchctl bootout "$GUI/com.snorkel.terminus-command-listener" 2>/dev/null || true
launchctl bootout "$GUI/com.snorkel.terminus-imessage-control" 2>/dev/null || true

echo ""
echo "Done. Remaining processes:"
pgrep -fl 'cursor-sdk-bridge|hourly_submission|command_listener|SnorkelTerminus' 2>/dev/null || echo "  (none)"
echo ""
echo "Re-enable:"
echo "  $MONITOR_DIR/install-hourly-launchd.sh"
echo "  $MONITOR_DIR/install-command-listener.sh   # optional remote commands"
