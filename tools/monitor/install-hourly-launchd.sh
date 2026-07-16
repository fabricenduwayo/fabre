#!/bin/bash
# Install hourly Snorkel submission monitor (launchd + Python venv + cursor-sdk).
set -euo pipefail

MONITOR_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$MONITOR_DIR/../.." && pwd)"
VENV="$MONITOR_DIR/.venv"
ENV_FILE="$MONITOR_DIR/.env"
PLIST_SRC="$MONITOR_DIR/com.snorkel.submission-monitor.plist"
PLIST_DST="$HOME/Library/LaunchAgents/com.snorkel.submission-monitor.plist"
PYTHON="${PYTHON:-$HOME/.local/share/uv/python/cpython-3.13-macos-aarch64-none/bin/python3.13}"

echo "==> Snorkel submission monitor installer"
echo "    repo: $REPO_ROOT"

if [[ ! -x "$PYTHON" ]]; then
  echo "Python 3.13 not found at $PYTHON" >&2
  echo "Install with: uv python install 3.13" >&2
  exit 1
fi

echo "==> Creating venv at $VENV"
"$PYTHON" -m venv "$VENV"
"$VENV/bin/pip" install --upgrade pip
"$VENV/bin/pip" install -r "$MONITOR_DIR/requirements.txt"

chmod +x "$MONITOR_DIR/run-hourly.sh"
chmod +x "$MONITOR_DIR/hourly_submission_check.py"
chmod +x "$MONITOR_DIR/terminus-control.sh"
chmod +x "$MONITOR_DIR/stop-all.sh"
chmod +x "$MONITOR_DIR/status-all.sh"

if [[ ! -f "$ENV_FILE" ]]; then
  cp "$MONITOR_DIR/.env.example" "$ENV_FILE"
  echo ""
  echo "!! Created $ENV_FILE — add CURSOR_API_KEY and Telegram settings before fixes run."
  echo "   https://cursor.com/dashboard/integrations"
fi

mkdir -p "$REPO_ROOT/.review-scratch/monitor"

PYTHON_REAL="$("$VENV/bin/python" -c 'import os, sys; print(os.path.realpath(sys.executable))')"
VENV_SITE="$("$VENV/bin/python" -c 'import site; print(site.getsitepackages()[0])')"
"$VENV/bin/python" -c "import cursor_sdk" 2>/dev/null || {
  echo "cursor_sdk missing in venv — pip install -r $MONITOR_DIR/requirements.txt" >&2
  exit 1
}
"$VENV/bin/python" -c "
import sys
sys.path.insert(0, '$MONITOR_DIR')
from monitor_agent import resolve_cursor_model
print('Cursor model:', resolve_cursor_model())
" 2>/dev/null || {
  echo "monitor_agent model check failed — fix CURSOR_COMPOSER_MODEL / MONITOR_MODEL in .env" >&2
  exit 1
}

sed \
  -e "s|__REPO_ROOT__|$REPO_ROOT|g" \
  -e "s|__MONITOR_DIR__|$MONITOR_DIR|g" \
  -e "s|__MONITOR_ENV__|$ENV_FILE|g" \
  -e "s|__PYTHON_REAL__|$PYTHON_REAL|g" \
  -e "s|__HOME__|$HOME|g" \
  -e "s|__VENV__|$VENV|g" \
  -e "s|__VENV_SITE__|$VENV_SITE|g" \
  "$PLIST_SRC" > "$PLIST_DST"

echo "==> Installing launchd agent: $PLIST_DST"
launchctl bootout "gui/$(id -u)/com.snorkel.submission-monitor" 2>/dev/null || true
launchctl bootstrap "gui/$(id -u)" "$PLIST_DST"
launchctl enable "gui/$(id -u)/com.snorkel.submission-monitor"
# RunAtLoad=true already starts one run — do not kickstart again (was causing duplicate Telegram alerts).

echo ""
echo "Installed. Schedule: every 90 minutes + once at load."
echo "Config: $ENV_FILE"
echo "Logs: $REPO_ROOT/.review-scratch/monitor/monitor.log"
echo ""
echo "Manual test (no agent):  $MONITOR_DIR/run-hourly.sh --dry-run"
echo "Manual test (live fix):  $MONITOR_DIR/run-hourly.sh"
echo "Remote commands (opt):   $MONITOR_DIR/install-command-listener.sh"
echo ""
echo "For unattended agent fixes (optional):"
echo "  - AUTO_AGENT_FIX=1 in $ENV_FILE"
echo "  - Cursor.app open and logged in"
echo "  - Allow macOS privacy prompt once (python ↔ Cursor)"
echo "  - Docker Desktop running"
echo ""
echo "Recommended (no privacy prompts on schedule):"
echo "  - AUTO_AGENT_FIX=0  NOTIFY_MACOS=0  — scan + Telegram only"
echo "  - Send 'run' on Telegram when you want a fix"
