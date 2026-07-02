#!/usr/bin/env bash
set -euo pipefail
pkill -f 'dependency-audit-1.0.0.jar' >/dev/null 2>&1 || true
rm -rf /app/dependency-audit/data
mkdir -p /app/dependency-audit/data
nohup java -jar /app/dependency-audit/app.jar >/tmp/dependency-audit.log 2>&1 &
