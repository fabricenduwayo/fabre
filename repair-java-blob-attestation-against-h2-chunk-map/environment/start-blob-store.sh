#!/usr/bin/env bash
# Launch the blob-store API on port 8080 if it is not already answering.
set -u

PORT="${BLOB_STORE_PORT:-8080}"

if curl -sf "http://localhost:${PORT}/health" >/dev/null 2>&1; then
    exit 0
fi

nohup java -cp "/app/blob-store/classes:/app/lib/*" \
    com.snorkel.store.StoreServer "${PORT}" \
    >/var/log/blob-store.log 2>&1 &

for _ in $(seq 1 30); do
    if curl -sf "http://localhost:${PORT}/health" >/dev/null 2>&1; then
        exit 0
    fi
    sleep 1
done

echo "blob-store did not become ready on port ${PORT}" >&2
exit 1
