#!/bin/bash
# Milestone 3: verify GIF media decryption (pipeline built in m1).
set -euo pipefail
if [ ! -f /app/pipeline/classes/com/mariner/forensic/Main.class ]; then
    echo "pipeline not built; milestone 1 must run first" >&2
    exit 1
fi
mkdir -p /app/out
java -cp "/app/pipeline/classes:/app/lib/*" com.mariner.forensic.Main decrypt
