#!/usr/bin/env bash
set -euo pipefail
cp /solution/flatten-deps.awk /app/dependency-audit/tools/flatten-deps.awk
cp /solution/pom.xml /app/dependency-audit/pom.xml
chmod +x /app/dependency-audit/tools/flatten-deps.awk
bash /app/dependency-audit/build.sh
bash /app/dependency-audit/start.sh
curl -sf http://127.0.0.1:8080/health | grep -q ok
