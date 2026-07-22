#!/bin/bash
set -euo pipefail

PG_VERSION=15
PG_CLUSTER=main

if [ "$(id -u)" -eq 0 ]; then
    install -d -m 2775 -o postgres -g postgres /var/run/postgresql 2>/dev/null || true
fi

run_pg() {
    if [ "$(id -u)" -eq 0 ]; then
        "$@"
    else
        sudo -u postgres -- "$@"
    fi
}

if ! pg_isready -q 2>/dev/null; then
    run_pg pg_ctlcluster "${PG_VERSION}" "${PG_CLUSTER}" start
fi

TRIES=0
until pg_isready -q 2>/dev/null; do
    TRIES=$((TRIES + 1))
    if [ "$TRIES" -gt 150 ]; then
        echo "postgres did not become ready" >&2
        exit 1
    fi
    sleep 0.2
done
