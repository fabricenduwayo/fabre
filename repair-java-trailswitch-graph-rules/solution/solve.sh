#!/bin/bash
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEST=/app/trailswitch/src/main/java/com/trailswitch

cp "$HERE/GraphPathRepository.java" "$DEST/repo/GraphPathRepository.java"
cp "$HERE/RelayTransition.java" "$DEST/model/RelayTransition.java"
cp "$HERE/SwitchRuleHandler.java" "$DEST/service/SwitchRuleHandler.java"
cp "$HERE/PathPlanner.java" "$DEST/service/PathPlanner.java"

bash /app/trailswitch/build.sh
bash /app/trailswitch/start.sh

ready=0
for _ in $(seq 1 60); do
    if curl -sf http://127.0.0.1:8080/health >/dev/null 2>&1; then
        ready=1
        break
    fi
    sleep 0.5
done
if [ "$ready" -ne 1 ]; then
    echo "TrailSwitch failed to start" >&2
    cat /tmp/trailswitch.log >&2 || true
    exit 1
fi
