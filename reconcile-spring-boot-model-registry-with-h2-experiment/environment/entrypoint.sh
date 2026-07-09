#!/usr/bin/env bash
# Container entrypoint: bring up the registry API, wait for readiness, then hand
# control to the requested command.
set -u

registry_ready() {
    bash /app/start-registry.sh
}

if ! registry_ready; then
    echo "model-registry API not ready on first attempt; retrying once" >&2
    sleep 5
    if ! registry_ready; then
        echo "WARNING: model-registry API is not up" >&2
    fi
fi

exec "$@"
