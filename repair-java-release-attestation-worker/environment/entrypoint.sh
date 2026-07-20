#!/usr/bin/env bash
set -u

if ! bash /app/start-api.sh; then
    echo "artifact-metadata API not ready on first attempt; retrying once" >&2
    sleep 5
    if ! bash /app/start-api.sh; then
        echo "WARNING: artifact-metadata API is not up" >&2
    fi
fi

exec "$@"
