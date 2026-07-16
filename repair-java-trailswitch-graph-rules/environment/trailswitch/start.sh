#!/bin/bash
set -euo pipefail
bash /app/sql/init_db.sh

if pgrep -f '/app/trailswitch/app.jar' >/dev/null 2>&1; then
    pkill -f '/app/trailswitch/app.jar' 2>/dev/null || true
    for _ in $(seq 1 50); do
        if ! pgrep -f '/app/trailswitch/app.jar' >/dev/null 2>&1; then
            break
        fi
        sleep 0.1
    done
fi

nohup java -jar /app/trailswitch/app.jar >/tmp/trailswitch.log 2>&1 &
disown || true
