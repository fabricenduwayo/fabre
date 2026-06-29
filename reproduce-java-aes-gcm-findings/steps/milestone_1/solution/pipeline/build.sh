#!/bin/bash
# Compile the Mariner forensic pipeline against the vendored jars in /app/lib.
set -euo pipefail
PIPE="${1:-/app/pipeline}"
mkdir -p "$PIPE/classes"
find "$PIPE/src" -name '*.java' > "$PIPE/sources.txt"
javac --release 17 -encoding UTF-8 -cp "/app/lib/*" -d "$PIPE/classes" @"$PIPE/sources.txt"
