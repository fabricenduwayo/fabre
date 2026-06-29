#!/bin/bash
# Milestone 1: install and build the pipeline, then extract report rules.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

rm -rf /app/pipeline
cp -r "$SCRIPT_DIR/pipeline" /app/pipeline
bash /app/pipeline/build.sh /app/pipeline

mkdir -p /app/out
java -cp "/app/pipeline/classes:/app/lib/*" com.mariner.forensic.Main rules
