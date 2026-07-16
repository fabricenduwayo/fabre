#!/bin/bash
set -euo pipefail

APP=/app/harbordesk
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Harden HarborDesk from the staging defaults and fix the broken audit ledger.
cp "$HERE/config.php" "$APP/config.php"
cp "$HERE/http.php" "$APP/lib/http.php"
cp "$HERE/audit.php" "$APP/lib/audit.php"
cp "$HERE/index.php" "$APP/index.php"
cp "$HERE/start.sh" "$APP/start.sh"
chmod +x "$APP/start.sh"

# Restart the long-lived PHP server so the patched sources are what /v1 traffic hits.
pkill -f 'php -S 127.0.0.1:8080' 2>/dev/null || true
nohup bash "$APP/start.sh" >/tmp/harbordesk-oracle.log 2>&1 &

ready=0
for _ in $(seq 1 40); do
    if curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:8080/health | grep -qE '^(401|200)$'; then
        ready=1
        break
    fi
    sleep 0.25
done

if [ "$ready" -ne 1 ]; then
    echo "harbordesk failed to restart after oracle patch" >&2
    cat /tmp/harbordesk-oracle.log >&2 || true
    exit 1
fi
