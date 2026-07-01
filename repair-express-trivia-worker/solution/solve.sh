#!/bin/bash
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cp "$HERE/replay.py" /app/worker/replay.py
chmod +x /app/worker/replay.py
