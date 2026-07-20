#!/bin/bash
set -euo pipefail
ROOT="${1:-/app/attest-worker}"
mkdir -p "${ROOT}/classes"
find "${ROOT}/src" -name '*.java' > "${ROOT}/sources.txt"
javac --release 17 -encoding UTF-8 -cp "/app/lib/*" -d "${ROOT}/classes" @"${ROOT}/sources.txt"
