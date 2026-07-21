#!/bin/bash
set -uo pipefail
# Intentionally omit -e so pytest failures still reach the canonical reward block.

mkdir -p /logs/verifier

if [ "$PWD" = "/" ]; then
  echo "Error: No working directory set." >&2
  echo 0 > /logs/verifier/reward.txt
  exit 0
fi

# The reference attestor was the agent's to reverse-engineer, not to shell out
# to. Move it out of the way so parity has to come from the agent's own control.
rm -rf /app/ref

# Grade the agent's own source: recompile it so a dropped-in classes directory
# cannot stand in for a real reimplementation. A build failure fails closed.
if [ -d /app/attest-objects/src ]; then
  rm -rf /app/attest-objects/classes
  if ! bash /app/attest-objects/build.sh >/tmp/agent-build.log 2>&1; then
    echo "agent build failed:" >&2
    cat /tmp/agent-build.log >&2
    echo 0 > /logs/verifier/reward.txt
    exit 0
  fi
fi

PYTHONPATH=/tests python3 -m pytest --ctrf /logs/verifier/ctrf.json -p no:cacheprovider -rA /tests/test_outputs.py -q
rc=$?
if [ "$rc" -eq 0 ]; then
  echo 1 > /logs/verifier/reward.txt
else
  echo 0 > /logs/verifier/reward.txt
fi
