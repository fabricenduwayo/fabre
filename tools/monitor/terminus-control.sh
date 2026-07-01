#!/bin/bash
# Manual start/stop/status without iMessage.
set -euo pipefail

MONITOR_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$MONITOR_DIR/../.." && pwd)"
VENV="$MONITOR_DIR/.venv"

if [[ -f "$MONITOR_DIR/.env" ]]; then
  set -a
  # shellcheck disable=SC1091
  source "$MONITOR_DIR/.env"
  set +a
fi

export REPO_ROOT

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 {start|stop|status|run} [--dry-run]" >&2
  exit 1
fi

exec "$VENV/bin/python" "$MONITOR_DIR/terminus_control.py" "$@"
