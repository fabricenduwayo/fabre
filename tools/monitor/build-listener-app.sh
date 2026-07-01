#!/bin/bash
# Build SnorkelTerminusListener.app — FDA picker accepts .app, not python binaries.
set -euo pipefail

MONITOR_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$MONITOR_DIR/../.." && pwd)"
VENV="$MONITOR_DIR/.venv"
APP_DIR="$MONITOR_DIR/SnorkelTerminusListener.app"
MACOS_BIN="$APP_DIR/Contents/MacOS/SnorkelTerminusListener"
SUPPORT_DIR="$HOME/Library/Application Support/SnorkelTerminus"
SUPPORT_ENV="$SUPPORT_DIR/monitor.env"

if [[ ! -x "$VENV/bin/python" ]]; then
  echo "venv missing — run install-hourly-launchd.sh first" >&2
  exit 1
fi

PYTHON_REAL="$("$VENV/bin/python" -c 'import os, sys; print(os.path.realpath(sys.executable))')"

mkdir -p "$SUPPORT_DIR"
if [[ -f "$MONITOR_DIR/.env" ]]; then
  cp "$MONITOR_DIR/.env" "$SUPPORT_ENV"
  chmod 600 "$SUPPORT_ENV"
fi

mkdir -p "$APP_DIR/Contents/MacOS"

cat > "$APP_DIR/Contents/Info.plist" <<'PLIST'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>SnorkelTerminusListener</string>
    <key>CFBundleIdentifier</key>
    <string>com.snorkel.terminus-listener</string>
    <key>CFBundleName</key>
    <string>Snorkel Terminus Listener</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0</string>
    <key>LSUIElement</key>
    <true/>
    <key>LSBackgroundOnly</key>
    <true/>
</dict>
</plist>
PLIST

cat > "$MACOS_BIN" <<LAUNCHER
#!/bin/bash
cd /tmp 2>/dev/null || cd /

MONITOR_DIR="$MONITOR_DIR"
REPO_ROOT="$REPO_ROOT"
SUPPORT_ENV="$SUPPORT_ENV"
PYTHON_REAL="$PYTHON_REAL"

export REPO_ROOT MONITOR_DIR MONITOR_ENV_FILE="\$SUPPORT_ENV"
export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"
export SNORKEL_MSG_SOURCE=chatdb

if [[ -f "\$SUPPORT_ENV" ]]; then
  set -a
  # shellcheck disable=SC1091
  source "\$SUPPORT_ENV" || true
  set +a
fi

POLL_SEC="\${IMESSAGE_POLL_SEC:-20}"
while true; do
  if cp "\$HOME/Library/Messages/chat.db" "/tmp/snorkel-messages-chat.db" 2>/dev/null; then
    export SNORKEL_CHAT_DB="/tmp/snorkel-messages-chat.db"
  fi
  "\$PYTHON_REAL" "\$MONITOR_DIR/imessage_command_listener.py" --once || true
  sleep "\$POLL_SEC"
done
LAUNCHER

chmod +x "$MACOS_BIN"
echo "Built $APP_DIR"
echo "Env copy: $SUPPORT_ENV"
echo "Uses chat.db copy (SnorkelTerminusListener.app needs Full Disk Access + Automation → Messages"
