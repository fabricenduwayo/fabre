#!/bin/bash
# Show Snorkel monitor status (launchd, processes, queue).
set -euo pipefail

MONITOR_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV="$MONITOR_DIR/.venv"

if [[ -f "$MONITOR_DIR/.env" ]]; then
  set -a
  # shellcheck disable=SC1091
  source "$MONITOR_DIR/.env"
  set +a
fi
export REPO_ROOT="$(cd "$MONITOR_DIR/../.." && pwd)"

echo "==> Launchd"
launchctl list 2>/dev/null | grep snorkel || echo "  (no snorkel jobs loaded)"

echo ""
echo "==> Processes"
pgrep -fl 'hourly_submission_check|command_listener|cursor-sdk-bridge.*snorkel-ai|caffeinate.*hourly' 2>/dev/null || echo "  (none)"

echo ""
if [[ -x "$VENV/bin/python" ]]; then
  echo "==> Control status"
  "$VENV/bin/python" "$MONITOR_DIR/terminus_control.py" status
else
  echo "venv missing — run install-hourly-launchd.sh"
fi
