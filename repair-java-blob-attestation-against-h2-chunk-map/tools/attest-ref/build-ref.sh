#!/bin/bash
# Build the native reference attestor for both linux arches into environment/ref/.
# Author-only: tools/ is excluded from the task zip; the binaries ship.
set -euo pipefail
export PATH="/opt/homebrew/bin:$PATH"
HERE="$(cd "$(dirname "$0")" && pwd)"
REPO="$(cd "$HERE/../.." && pwd)"
mkdir -p "$REPO/environment/ref"
cd "$HERE"
GOOS=linux GOARCH=arm64 go build -trimpath -ldflags="-s -w" -o "$REPO/environment/ref/attest-ref-aarch64" .
GOOS=linux GOARCH=amd64 go build -trimpath -ldflags="-s -w" -o "$REPO/environment/ref/attest-ref-x86_64" .
cat > "$REPO/environment/ref/attest-ref" <<'WRAP'
#!/bin/sh
exec "$(dirname "$0")/attest-ref-$(uname -m)" "$@"
WRAP
chmod +x "$REPO/environment/ref/attest-ref"
echo "built native reference for aarch64 + x86_64"
