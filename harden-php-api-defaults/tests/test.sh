#!/bin/bash
set -uo pipefail

mkdir -p /logs/verifier

APP=/app/harbordesk

# Start from a clean token and re-seed the production (legacy) audit ledger so
# the run is deterministic and the schema defect must be fixed in code, not by
# deleting the database file.
rm -f "$APP/data/admin_token" "$APP/data/audit.db"
sqlite3 "$APP/data/audit.db" \
    "CREATE TABLE audit_log (id INTEGER PRIMARY KEY AUTOINCREMENT, ts TEXT NOT NULL, event TEXT NOT NULL, route TEXT NOT NULL, actor TEXT NOT NULL, decision TEXT NOT NULL, reason TEXT);"

bash "$APP/start.sh" >/tmp/harbordesk.log 2>&1 &
SERVER_PID=$!
trap 'kill "$SERVER_PID" 2>/dev/null' EXIT

ready=0
for _ in $(seq 1 40); do
    if python3 -c "import urllib.request, urllib.error, sys
try:
    urllib.request.urlopen('http://127.0.0.1:8080/health', timeout=1)
except urllib.error.HTTPError:
    pass
except Exception:
    sys.exit(1)" >/dev/null 2>&1; then
        ready=1
        break
    fi
    sleep 0.5
done

if [ "$ready" -ne 1 ]; then
    echo "harbordesk failed to start" >&2
    cat /tmp/harbordesk.log >&2 || true
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
