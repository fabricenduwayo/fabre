#!/bin/bash
set -uo pipefail

# Verifier dependencies (pytest, pytest-json-ctrf, jsonschema) are preinstalled
# by environment/Dockerfile; nothing is installed or downloaded here.

mkdir -p /logs/verifier

PYTHONPATH=/tests python3 -m pytest --ctrf /logs/verifier/ctrf.json -p no:cacheprovider -rA /tests/test_outputs.py -q
rc=$?
if [ "$rc" -eq 0 ]; then
  echo 1 > /logs/verifier/reward.txt
else
  echo 0 > /logs/verifier/reward.txt
fi
