#!/bin/bash
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

cp "$HERE/parent-pom.xml" /app/project/pom.xml
cp "$HERE/cli-pom.xml" /app/project/meter-cli/pom.xml

cd /app/project
mvn -B -o clean verify
