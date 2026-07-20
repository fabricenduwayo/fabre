#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET="/app/attest-worker"
SRC="${SCRIPT_DIR}/attest-worker/src"

for _ in $(seq 1 90); do
    if curl -sf http://localhost:8080/health >/dev/null 2>&1; then
        break
    fi
    sleep 1
done
bash /app/start-api.sh

if ! curl -sf http://localhost:8080/health >/dev/null 2>&1; then
    echo "artifact-metadata API is not healthy before attestation run" >&2
    tail -n 40 /var/log/artifact-api.log >&2 || true
    exit 1
fi

mkdir -p "${TARGET}/src/com/snorkel/attest"
cp -R "${SRC}/com/snorkel/attest/." "${TARGET}/src/com/snorkel/attest/"
bash "${TARGET}/build.sh"

java -cp "${TARGET}/classes:/app/lib/*" com.snorkel.attest.Main
