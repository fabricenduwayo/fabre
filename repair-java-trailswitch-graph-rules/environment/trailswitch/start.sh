#!/bin/bash
set -euo pipefail
bash /app/sql/init_db.sh
pkill -f 'trailswitch-1.0.0.jar' 2>/dev/null || true
nohup java -jar /app/trailswitch/app.jar >/tmp/trailswitch.log 2>&1 &
disown || true
