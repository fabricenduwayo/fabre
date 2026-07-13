#!/bin/bash
set -uo pipefail

if [ "$PWD" = "/" ]; then
    echo "Error: No working directory set." >&2
    exit 1
fi

mkdir -p /logs/verifier

APP=/app/harbordesk

# Start from a clean token and re-seed the production (legacy) audit ledger with
# its historical rows, so the run is deterministic and the schema defect must be
# fixed in code (preserving history), not by deleting the database file. The
# randomized tests re-seed per case via the same legacy layout.
rm -f "$APP/data/admin_token"
rm -f "$APP/data/audit.db"
printf 'https://harbordesk.internal\n' > "$APP/data/allowed_origins"
sqlite3 "$APP/data/audit.db" \
    "CREATE TABLE audit_log (id INTEGER PRIMARY KEY AUTOINCREMENT, ts TEXT NOT NULL, event TEXT NOT NULL, route TEXT NOT NULL, actor TEXT NOT NULL, decision TEXT NOT NULL, reason TEXT); INSERT INTO audit_log (ts, event, route, actor, decision, reason) VALUES ('2026-01-02T08:00:00+00:00', 'health', '/health', 'svc-legacy', 'accepted', 'legacy_history'); INSERT INTO audit_log (ts, event, route, actor, decision, reason) VALUES ('2026-01-02T08:05:00+00:00', 'bootstrap', '/admin/bootstrap', 'svc-legacy', 'denied', 'legacy_history');"

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
