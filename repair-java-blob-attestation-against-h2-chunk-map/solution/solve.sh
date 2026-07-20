#!/bin/bash
# Oracle solution: drop the finished auditor over the scaffold, build it, and run
# it so the attestation report is derived from the store the auditor is pointed at.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET="/app/attest-objects"
SRC="${SCRIPT_DIR}/attest-objects/src"

mkdir -p /app/build "${TARGET}/src/com/snorkel/attest"
cp -R "${SRC}/com/snorkel/attest/." "${TARGET}/src/com/snorkel/attest/"
bash "${TARGET}/build.sh"

java -cp "${TARGET}/classes:/app/lib/*" com.snorkel.attest.Main

cat /app/build/attestation-report.json
