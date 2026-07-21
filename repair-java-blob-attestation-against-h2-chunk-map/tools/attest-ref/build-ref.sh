#!/bin/bash
# Build environment/ref/attest-ref.jar, the reference attestor the agent matches.
# It is the same logic the solution implements, compiled with debug info stripped
# and shipped as a jar; the agent probes it to work out how the store attests and
# reimplements it. Author-only: tools/ is excluded from the task zip.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
REPO="$(cd "$HERE/../.." && pwd)"
WORK="$(mktemp -d)"
find "$REPO/solution/attest-objects/src" -name '*.java' > "$WORK/src.txt"
javac -g:none --release 17 -cp "$REPO/environment/lib/*" -d "$WORK/classes" @"$WORK/src.txt"
( cd "$WORK/classes" && jar --create --file "$REPO/environment/ref/attest-ref.jar" \
    --main-class com.snorkel.attest.Main com )
echo "built $REPO/environment/ref/attest-ref.jar"
