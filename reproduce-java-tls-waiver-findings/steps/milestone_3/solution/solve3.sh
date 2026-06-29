#!/bin/bash
# Milestone 3: validate the config against its schemas and emit final findings.
set -euo pipefail
if [ ! -f /app/pipeline/classes/com/mariner/audit/Main.class ]; then
    echo "pipeline not built; milestone 1 must run first" >&2
    exit 1
fi
mkdir -p /app/out
java -cp "/app/pipeline/classes:/app/lib/*" com.mariner.audit.Main validate
