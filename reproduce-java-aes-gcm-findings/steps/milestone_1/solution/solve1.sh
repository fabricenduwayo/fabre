#!/bin/bash
# Milestone 1: install and build the pipeline, then extract report rules.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

rm -rf /app/pipeline
mkdir -p /app/pipeline/src/com/mariner/forensic
cp "$SCRIPT_DIR/pipeline/build.sh" /app/pipeline/build.sh
cp "$SCRIPT_DIR/pipeline/src/com/mariner/forensic/Main.java" \
    "$SCRIPT_DIR/pipeline/src/com/mariner/forensic/Json.java" \
    "$SCRIPT_DIR/pipeline/src/com/mariner/forensic/RuleExtractor.java" \
    /app/pipeline/src/com/mariner/forensic/
chmod +x /app/pipeline/build.sh
bash /app/pipeline/build.sh /app/pipeline

mkdir -p /app/out
java -cp "/app/pipeline/classes:/app/lib/*" com.mariner.forensic.Main rules
