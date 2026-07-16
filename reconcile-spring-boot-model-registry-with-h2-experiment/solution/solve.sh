#!/bin/bash
# Oracle solution: implement the reconcile-model-release Java CLI and run it so
# the decision manifest is derived from the live registry API + H2 store.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET="/app/reconcile-model-release"
SRC="${SCRIPT_DIR}/reconcile-model-release/src"

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

mkdir -p /app/build "${TARGET}/src/com/snorkel/registry"
cp -R "${SRC}/com/snorkel/registry/." "${TARGET}/src/com/snorkel/registry/"
bash "${TARGET}/build.sh"

java -cp "${TARGET}/classes:/app/lib/*" com.snorkel.registry.Main

cat /app/build/release-decision.json
