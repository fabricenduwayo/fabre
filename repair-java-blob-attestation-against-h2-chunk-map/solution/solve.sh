#!/bin/bash
# Oracle solution: drop the finished Auditor over the scaffold's stub, build, and
# run it so the attestation report is derived from the store the auditor is
# pointed at. Main.java is unchanged scaffolding, so only Auditor.java is copied.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET="/app/attest-objects"
SRC="${SCRIPT_DIR}/attest-objects/src"

mkdir -p /app/build
cp "${SRC}/com/snorkel/attest/Auditor.java" \
   "${TARGET}/src/com/snorkel/attest/Auditor.java"
bash "${TARGET}/build.sh"

java -cp "${TARGET}/classes:/app/lib/*" com.snorkel.attest.Main

cat /app/build/attestation-report.json
