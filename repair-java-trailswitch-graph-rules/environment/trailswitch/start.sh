#!/bin/bash
set -euo pipefail
bash /app/sql/init_db.sh
pkill -f '/app/trailswitch/app.jar' 2>/dev/null || true
nohup java -jar /app/trailswitch/app.jar >/tmp/trailswitch.log 2>&1 &
disown || true
