#!/bin/bash
# Rebuild environment/lib/blobstore-1.0.jar from the service source (author-only;
# tools/ is excluded from the task zip, the jar ships).
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
REPO="$(cd "$HERE/../.." && pwd)"
WORK="$(mktemp -d)"
javac --release 17 -cp "$REPO/environment/lib/*" -d "$WORK" \
    "$HERE"/src/com/snorkel/store/StoreServer.java
( cd "$WORK" && jar --create --file "$REPO/environment/lib/blobstore-1.0.jar" \
    --main-class com.snorkel.store.StoreServer com )
echo "built $REPO/environment/lib/blobstore-1.0.jar"
