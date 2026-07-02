#!/bin/bash
set -euo pipefail
cd /app/trailswitch
mvn -q -DskipTests package
cp target/trailswitch-1.0.0.jar /app/trailswitch/app.jar
