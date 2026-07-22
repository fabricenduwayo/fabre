#!/usr/bin/env bash
set -uo pipefail
mkdir -p /logs/verifier
echo 0 > /logs/verifier/reward.txt

TEST_DIR="${TEST_DIR:-/tests}"
if [ ! -d "$TEST_DIR" ]; then
  echo "Error: missing test directory $TEST_DIR" >&2
  exit 0
fi

cd "$TEST_DIR" || exit 0
PYTHONSAFEPATH=1 python3 -m pytest --ctrf /logs/verifier/ctrf.json -p no:cacheprovider -rA test_outputs.py -q
rc=$?
if [ "$rc" -eq 0 ]; then
  echo 1 > /logs/verifier/reward.txt
else
  echo 0 > /logs/verifier/reward.txt
fi
