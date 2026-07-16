#!/bin/bash
# Oracle solution: implement the reconcile-model-release script and run it so
# the decision manifest is derived from the live registry API + H2 store.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

for _ in $(seq 1 90); do
    if curl -sf http://localhost:8080/health >/dev/null 2>&1; then
        break
    fi
    sleep 1
done
bash /app/start-registry.sh

if ! curl -sf http://localhost:8080/health >/dev/null 2>&1; then
    echo "registry API is not healthy before reconcile; see /var/log/model-registry.log" >&2
    tail -n 40 /var/log/model-registry.log >&2 || true
    exit 1
fi

mkdir -p /app/build

cp "${SCRIPT_DIR}/reconcile.py" /app/reconcile-model-release/reconcile.py
chmod +x /app/reconcile-model-release/reconcile.py

python3 /app/reconcile-model-release/reconcile.py

cat /app/build/release-decision.json
