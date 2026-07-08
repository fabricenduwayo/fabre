#!/usr/bin/env bash
# Container entrypoint: bring up the registry API in the background, then hand
# control to the requested command. A failed API start is reported but does not
# kill the container, so a shell is still available for debugging.
set -u

bash /app/start-registry.sh || echo "WARNING: model-registry API is not up" >&2

exec "$@"
