#!/usr/bin/env bash
# Container entrypoint: bring the blob-store API up, then hand control to the
# requested command. The API is a convenience for experimenting against the
# store; the auditor reads the database directly and does not depend on it.
set -u

if ! bash /app/start-blob-store.sh; then
    echo "WARNING: blob-store API is not up" >&2
fi

exec "$@"
