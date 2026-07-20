#!/bin/bash
# Compile attest-objects against the vendored jars in /app/lib.
set -euo pipefail
ROOT="${1:-/app/attest-objects}"
mkdir -p "${ROOT}/classes"
find "${ROOT}/src" -name '*.java' > "${ROOT}/sources.txt"
javac --release 17 -encoding UTF-8 -cp "/app/lib/*" -d "${ROOT}/classes" @"${ROOT}/sources.txt"
