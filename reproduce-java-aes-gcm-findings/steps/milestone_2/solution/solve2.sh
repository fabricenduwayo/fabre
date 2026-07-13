#!/bin/bash
# Milestone 2: add the correlator to the milestone 1 pipeline and rebuild.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ ! -f /app/pipeline/classes/com/mariner/forensic/Main.class ]; then
    echo "pipeline not built; milestone 1 must run first" >&2
    exit 1
fi
cp "$SCRIPT_DIR/src/com/mariner/forensic/Main.java" \
    "$SCRIPT_DIR/src/com/mariner/forensic/AuditCorrelator.java" \
    /app/pipeline/src/com/mariner/forensic/
bash /app/pipeline/build.sh /app/pipeline
mkdir -p /app/out
java -cp "/app/pipeline/classes:/app/lib/*" com.mariner.forensic.Main correlate
