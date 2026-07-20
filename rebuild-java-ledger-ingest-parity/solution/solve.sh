#!/bin/bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cp -R "${SCRIPT_DIR}/ingest/src/com/snorkel/ingest/." /app/ingest/src/com/snorkel/ingest/
bash /app/ingest/build.sh
