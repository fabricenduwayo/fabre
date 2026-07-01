#!/bin/bash
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

cp "$HERE/play_shift.py" /app/tools/play_shift.py
python3 "$HERE/repair_cartridge.py"

pkill -f '/app/referee/app.py' 2>/dev/null || true
pkill -f 'python3 app.py' 2>/dev/null || true
sleep 0.2

nohup bash /app/referee/start.sh >/tmp/oracle-referee.log 2>&1 &
REF_PID=$!
disown "$REF_PID" 2>/dev/null || true
trap 'kill "$REF_PID" 2>/dev/null; pkill -f "/app/referee/app.py" 2>/dev/null || true' EXIT

ready=0
for _ in $(seq 1 80); do
    if python3 -c "import urllib.request, json, sys
try:
    r = urllib.request.urlopen('http://127.0.0.1:5000/health', timeout=2)
    d = json.loads(r.read().decode())
    sys.exit(0 if d.get('status') == 'ok' else 1)
except Exception:
    sys.exit(1)" >/dev/null 2>&1; then
        ready=1
        break
    fi
    sleep 0.5
done

if [ "$ready" -ne 1 ]; then
    echo "signalbox referee failed to start" >&2
    cat /tmp/oracle-referee.log >&2 || true
    exit 1
fi

python3 /app/tools/play_shift.py
