#!/usr/bin/env bash
set -uo pipefail
mkdir -p /logs/verifier
TEST_DIR="${TEST_DIR:-/tests}"
PYTHONPATH="$TEST_DIR" python3 -m pytest --ctrf /logs/verifier/ctrf.json -p no:cacheprovider -rA "$TEST_DIR/test_outputs.py" -q
rc=$?
if [ "$rc" -eq 0 ]; then
  echo 1 > /logs/verifier/reward.txt
else
  echo 0 > /logs/verifier/reward.txt
fi
