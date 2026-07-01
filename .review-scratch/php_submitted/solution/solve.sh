#!/bin/bash
set -euo pipefail

APP=/app/harbordesk
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Harden HarborDesk from the staging defaults and fix the broken audit ledger:
# - config: turn off debug and plaintext bootstrap
# - http:   restrict CORS to the allowlisted internal origin (credentialed)
# - audit:  reconcile the legacy on-disk schema so audit writes stop failing
# - index:  require the bootstrap secret, make bootstrap one-time, store the
#           token as a digest and write it 0600
# - start:  serve every request through the front controller
cp "$HERE/config.php" "$APP/config.php"
cp "$HERE/http.php" "$APP/lib/http.php"
cp "$HERE/audit.php" "$APP/lib/audit.php"
cp "$HERE/index.php" "$APP/index.php"
cp "$HERE/start.sh" "$APP/start.sh"
chmod +x "$APP/start.sh"
