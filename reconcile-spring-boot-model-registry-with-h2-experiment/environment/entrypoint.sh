#!/usr/bin/env bash
# Container entrypoint: bring up the registry API, wait for readiness, then hand
# control to the requested command.
set -u

if ! bash /app/start-registry.sh; then
    echo "WARNING: model-registry API is not up" >&2
fi

exec "$@"
