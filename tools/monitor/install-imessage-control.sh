#!/bin/bash
# Install iMessage command listener (start-terminus / stop-terminus via text).
set -euo pipefail

MONITOR_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$MONITOR_DIR/../.." && pwd)"
PLIST_SRC="$MONITOR_DIR/com.snorkel.terminus-imessage-control.plist"
PLIST_DST="$HOME/Library/LaunchAgents/com.snorkel.terminus-imessage-control.plist"
VENV="$MONITOR_DIR/.venv"

echo "==> Snorkel iMessage control installer"
echo "    repo: $REPO_ROOT"

if [[ ! -x "$VENV/bin/python" ]]; then
  echo "Run install-hourly-launchd.sh first (creates venv)." >&2
  exit 1
fi

chmod +x "$MONITOR_DIR/build-listener-app.sh"
chmod +x "$MONITOR_DIR/run-imessage-listener.sh"
chmod +x "$MONITOR_DIR/terminus-control.sh"
chmod +x "$MONITOR_DIR/imessage_command_listener.py"
chmod +x "$MONITOR_DIR/terminus_control.py"

mkdir -p "$REPO_ROOT/.review-scratch/monitor"

"$MONITOR_DIR/build-listener-app.sh"
LISTENER_APP="$MONITOR_DIR/SnorkelTerminusListener.app"

sed \
  -e "s|__REPO_ROOT__|$REPO_ROOT|g" \
  -e "s|__MONITOR_DIR__|$MONITOR_DIR|g" \
  -e "s|__HOME__|$HOME|g" \
  -e "s|__LISTENER_APP__|$LISTENER_APP|g" \
  "$PLIST_SRC" > "$PLIST_DST"

echo "==> Installing launchd listener: $PLIST_DST"
launchctl bootout "gui/$(id -u)/com.snorkel.terminus-imessage-control" 2>/dev/null || true
launchctl bootstrap "gui/$(id -u)" "$PLIST_DST"
launchctl enable "gui/$(id -u)/com.snorkel.terminus-imessage-control"
launchctl kickstart -k "gui/$(id -u)/com.snorkel.terminus-imessage-control"

echo ""
echo "Installed. The listener stays running and watches for iMessage commands."
echo ""
echo "From your iPhone (same Apple ID / iMessage as this Mac), text yourself:"
echo "  start-terminus   — enable hourly monitor + run now"
echo "  stop-terminus    — disable hourly monitor"
echo "  status-terminus  — reply with running/stopped + queue"
echo "  run-terminus     — one fix cycle now (monitor can be stopped)"
echo ""
echo "REQUIRED permissions:"
echo "  1) Full Disk Access → SnorkelTerminusListener.app (read Messages)"
echo "  2) Automation → SnorkelTerminusListener → Messages (send replies)"
echo "  Then: launchctl kickstart -k gui/\$(id -u)/com.snorkel.terminus-imessage-control"
echo ""
echo "Also ensure Messages is signed in and NOTIFY_IMESSAGE=1 + IMESSAGE_TO in .env"
echo ""
echo "For iMessage REPLIES also grant Automation:"
echo "  System Settings → Privacy & Security → Automation"
echo "  Allow SnorkelTerminusListener (or osascript) to control Messages"
echo ""
echo "Manual CLI (no iMessage): $MONITOR_DIR/terminus-control.sh status"
echo "Logs: $REPO_ROOT/.review-scratch/monitor/control.log"
