#!/bin/bash
set -uo pipefail

if [ "$PWD" = "/" ]; then
    echo "Error: No working directory set." >&2
    exit 1
fi

mkdir -p /logs/verifier

cmake -S /app/cpp-auditor -B /app/cpp-auditor/build >/tmp/cmake_configure.log 2>&1
cmake --build /app/cpp-auditor/build -j 2 >/tmp/cmake_build.log 2>&1
if [ $? -ne 0 ]; then
    echo "C++ build failed" >&2
    tail -n 40 /tmp/cmake_build.log >&2
    echo 0 > /logs/verifier/reward.txt
    exit 0
fi

# Reset the audit ledger to its legacy schema-1 state so the auditor must
# reconcile it at runtime; removing the file in a solution is not sufficient.
mkdir -p /app/cpp-auditor/state
printf '%s' '{"schema": 1, "audits": [{"action": "audit.bootstrap", "target": "legacy-seed"}]}' \
    > /app/cpp-auditor/state/ledger.json

AUDITOR_PORT=8080 /app/cpp-auditor/build/setup_auditor &
CPP_PID=$!
trap 'kill "$CPP_PID" 2>/dev/null' EXIT

ready=0
for _ in $(seq 1 40); do
    if python3 -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8080/health', timeout=1)" >/dev/null 2>&1; then
        ready=1
        break
    fi
    sleep 0.5
done

if [ "$ready" -ne 1 ]; then
    echo "auditor failed to start" >&2
    echo 0 > /logs/verifier/reward.txt
    exit 0
fi

PYTHONPATH=/tests python3 -m pytest --ctrf /logs/verifier/ctrf.json -p no:cacheprovider -rA /tests/test_outputs.py -q
rc=$?
if [ "$rc" -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi
