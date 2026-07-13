#!/bin/bash
# Milestone 3: add the decryptor to the milestone 2 pipeline and rebuild.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ ! -f /app/pipeline/classes/com/mariner/forensic/Main.class ]; then
    echo "pipeline not built; earlier milestones must run first" >&2
    exit 1
fi
cp "$SCRIPT_DIR/src/com/mariner/forensic/Main.java" \
    "$SCRIPT_DIR/src/com/mariner/forensic/MediaDecryptor.java" \
    /app/pipeline/src/com/mariner/forensic/
bash /app/pipeline/build.sh /app/pipeline
mkdir -p /app/out
java -cp "/app/pipeline/classes:/app/lib/*" com.mariner.forensic.Main decrypt
