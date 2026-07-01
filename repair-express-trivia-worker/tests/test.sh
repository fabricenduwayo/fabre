#!/bin/bash
set -uo pipefail

if [ "$PWD" = "/" ]; then
    echo "Error: No working directory set." >&2
    exit 1
fi

mkdir -p /logs/verifier /app/output

pkill -f 'node src/server.js' 2>/dev/null || true
sleep 0.2

nohup /app/referee/start.sh >/tmp/referee.log 2>&1 &
SERVER_PID=$!
disown "$SERVER_PID" 2>/dev/null || true
trap 'kill "$SERVER_PID" 2>/dev/null; pkill -f "node src/server.js" 2>/dev/null || true' EXIT

ready=0
for _ in $(seq 1 80); do
    if python3 -c "import urllib.request, json, sys
try:
    r = urllib.request.urlopen('http://127.0.0.1:3000/health', timeout=2)
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
    echo "referee failed to start" >&2
    cat /tmp/referee.log >&2 || true
    echo 0 > /logs/verifier/reward.txt
    exit 0
fi

PYTHONPATH=/tests python3 -m pytest --ctrf /logs/verifier/ctrf.json -p no:cacheprovider -rA /tests/test_outputs.py -q
rc=$?
if [ "$rc" -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi
