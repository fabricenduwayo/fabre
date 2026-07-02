#!/usr/bin/env bash
set -euo pipefail
pkill -f '/app/dependency-audit/app.jar' >/dev/null 2>&1 || true
for _ in $(seq 1 40); do
  if ! pgrep -f '/app/dependency-audit/app.jar' >/dev/null 2>&1; then
    break
  fi
  sleep 0.25
done
rm -rf /app/dependency-audit/data
mkdir -p /app/dependency-audit/data
nohup java -jar /app/dependency-audit/app.jar >/tmp/dependency-audit.log 2>&1 &
