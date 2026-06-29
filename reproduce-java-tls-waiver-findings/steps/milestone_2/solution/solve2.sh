#!/bin/bash
# Milestone 2: join the captured probe evidence from H2 (pipeline built in m1).
set -euo pipefail
if [ ! -f /app/pipeline/classes/com/mariner/audit/Main.class ]; then
    echo "pipeline not built; milestone 1 must run first" >&2
    exit 1
fi
mkdir -p /app/out
java -cp "/app/pipeline/classes:/app/lib/*" com.mariner.audit.Main join
