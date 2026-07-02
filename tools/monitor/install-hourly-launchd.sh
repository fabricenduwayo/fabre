#!/bin/bash
# Install hourly Snorkel submission monitor (launchd + Python venv + cursor-sdk).
set -euo pipefail

MONITOR_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$MONITOR_DIR/../.." && pwd)"
VENV="$MONITOR_DIR/.venv"
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

if [[ ! -f "$MONITOR_DIR/.env" ]]; then
  cp "$MONITOR_DIR/.env.example" "$MONITOR_DIR/.env"
  echo ""
  echo "!! Created $MONITOR_DIR/.env — add your CURSOR_API_KEY before the job will fix tasks."
  echo "   https://cursor.com/dashboard/integrations"
fi

mkdir -p "$REPO_ROOT/.review-scratch/monitor"
SUPPORT_DIR="$HOME/Library/Application Support/SnorkelTerminus"
SUPPORT_ENV="$SUPPORT_DIR/monitor.env"
mkdir -p "$SUPPORT_DIR"
if [[ -f "$MONITOR_DIR/.env" ]]; then
  cp "$MONITOR_DIR/.env" "$SUPPORT_ENV"
  chmod 600 "$SUPPORT_ENV"
fi

PYTHON_REAL="$("$VENV/bin/python" -c 'import os, sys; print(os.path.realpath(sys.executable))')"
VENV_SITE="$("$VENV/bin/python" -c 'import site; print(site.getsitepackages()[0])')"
"$VENV/bin/python" -c "import cursor_sdk" 2>/dev/null || {
  echo "cursor_sdk missing in venv — pip install -r $MONITOR_DIR/requirements.txt" >&2
  exit 1
}

# Render plist with absolute paths for this machine.
sed \
  -e "s|__REPO_ROOT__|$REPO_ROOT|g" \
  -e "s|__MONITOR_DIR__|$MONITOR_DIR|g" \
  -e "s|__PYTHON_REAL__|$PYTHON_REAL|g" \
  -e "s|__SUPPORT_ENV__|$SUPPORT_ENV|g" \
  -e "s|__HOME__|$HOME|g" \
  -e "s|__VENV__|$VENV|g" \
  -e "s|__VENV_SITE__|$VENV_SITE|g" \
  "$PLIST_SRC" > "$PLIST_DST"

echo "==> Installing launchd agent: $PLIST_DST"
launchctl bootout "gui/$(id -u)/com.snorkel.submission-monitor" 2>/dev/null || true
launchctl bootstrap "gui/$(id -u)" "$PLIST_DST"
launchctl enable "gui/$(id -u)/com.snorkel.submission-monitor"
launchctl kickstart -k "gui/$(id -u)/com.snorkel.submission-monitor"

echo ""
echo "Installed. Schedule: every 90 minutes + once at load."
echo "Logs: $REPO_ROOT/.review-scratch/monitor/monitor.log"
echo ""
echo "Manual test (no agent call):  $MONITOR_DIR/run-hourly.sh --dry-run"
echo "Manual test (live fix):       $MONITOR_DIR/run-hourly.sh"
echo "iMessage control (optional):  $MONITOR_DIR/install-imessage-control.sh"
echo ""
echo "IMPORTANT for unattended runs tomorrow:"
echo "  - Mac must be ON and you must be logged in (screen lock is OK; full logout is NOT)"
echo "  - Docker Desktop should be running (oracle needs it)"
echo "  - Fill CURSOR_API_KEY in tools/monitor/.env"
echo "  - stb auth must already be valid (you ran 'stb login' once)"
