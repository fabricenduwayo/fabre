#!/bin/bash
# Install Telegram/ntfy remote command listener (optional).
set -euo pipefail

MONITOR_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$MONITOR_DIR/../.." && pwd)"
VENV="$MONITOR_DIR/.venv"
ENV_FILE="$MONITOR_DIR/.env"
PLIST_SRC="$MONITOR_DIR/com.snorkel.terminus-command-listener.plist"
PLIST_DST="$HOME/Library/LaunchAgents/com.snorkel.terminus-command-listener.plist"

echo "==> Snorkel command listener installer"
echo "    repo: $REPO_ROOT"

if [[ ! -x "$VENV/bin/python" ]]; then
  echo "Run install-hourly-launchd.sh first (creates venv)." >&2
  exit 1
fi

chmod +x "$MONITOR_DIR/command_listener.py"

mkdir -p "$REPO_ROOT/.review-scratch/monitor"

PYTHON_REAL="$("$VENV/bin/python" -c 'import os, sys; print(os.path.realpath(sys.executable))')"
VENV_SITE="$("$VENV/bin/python" -c 'import site; print(site.getsitepackages()[0])')"

sed \
  -e "s|__REPO_ROOT__|$REPO_ROOT|g" \
  -e "s|__MONITOR_DIR__|$MONITOR_DIR|g" \
  -e "s|__MONITOR_ENV__|$ENV_FILE|g" \
  -e "s|__PYTHON_REAL__|$PYTHON_REAL|g" \
  -e "s|__HOME__|$HOME|g" \
  -e "s|__VENV__|$VENV|g" \
  -e "s|__VENV_SITE__|$VENV_SITE|g" \
  "$PLIST_SRC" > "$PLIST_DST"

# Remove legacy iMessage listener if present.
launchctl bootout "gui/$(id -u)/com.snorkel.terminus-imessage-control" 2>/dev/null || true
rm -f "$HOME/Library/LaunchAgents/com.snorkel.terminus-imessage-control.plist"

echo "==> Installing launchd listener: $PLIST_DST"
launchctl bootout "gui/$(id -u)/com.snorkel.terminus-command-listener" 2>/dev/null || true
launchctl bootstrap "gui/$(id -u)" "$PLIST_DST"
launchctl enable "gui/$(id -u)/com.snorkel.terminus-command-listener"
# RunAtLoad=true already starts the listener — avoid double start on install.

echo ""
echo "Installed. Polls Telegram and/or ntfy for: stop | start | status | run"
echo "Config: $ENV_FILE"
echo "Logs: $REPO_ROOT/.review-scratch/monitor/command-listener-stderr.log"
echo ""
echo "Telegram setup:"
echo "  1) Message @BotFather → /newbot → copy token to TELEGRAM_BOT_TOKEN"
echo "  2) Message your bot /start"
echo "  3) curl https://api.telegram.org/bot<TOKEN>/getUpdates → copy chat id to TELEGRAM_CHAT_ID"
echo "  4) Set NOTIFY_TELEGRAM=1 and TELEGRAM_CMD_ENABLE=1 in $ENV_FILE"
