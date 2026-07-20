#!/bin/bash
set -uo pipefail

mkdir -p /logs/verifier

if [ "$PWD" = "/" ]; then
  echo "Error: No working directory set." >&2
  echo 0 > /logs/verifier/reward.txt
  exit 0
fi

# The instruction tells the agent the legacy jar will not be on the box at run
# time. Move it out of reach before the suite starts so that stays true.
if [ -f /opt/legacy/ledger-oracle.jar ]; then
  mv /opt/legacy/ledger-oracle.jar /tests/ledger-oracle.jar
fi

PYTHONPATH=/tests python3 -m pytest --ctrf /logs/verifier/ctrf.json -p no:cacheprovider -rA /tests/test_outputs.py -q
rc=$?
if [ "$rc" -eq 0 ]; then
  echo 1 > /logs/verifier/reward.txt
else
  echo 0 > /logs/verifier/reward.txt
fi
