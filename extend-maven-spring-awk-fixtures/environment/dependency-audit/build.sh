#!/usr/bin/env bash
set -euo pipefail
cd /app/dependency-audit
mvn -q test package
cp target/dependency-audit-1.0.0.jar /app/dependency-audit/app.jar
