#!/bin/bash
# Oracle solution: implement the reconcile-model-release step, build it
# offline, and run it so the decision manifest is derived from the live
# registry API + H2 experiment store.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Registry normally starts from the container entrypoint. Give an in-flight boot
# a short grace period, then run the shared launcher (it waits on an existing
# process instead of spawning a duplicate on port 8080).
for _ in $(seq 1 60); do
    if curl -sf http://localhost:8080/health >/dev/null 2>&1; then
        break
    fi
    sleep 1
done
bash /app/start-registry.sh

if ! curl -sf http://localhost:8080/health >/dev/null 2>&1; then
    echo "registry API is not healthy before reconcile build; see /var/log/model-registry.log" >&2
    tail -n 40 /var/log/model-registry.log >&2 || true
    exit 1
fi

mkdir -p /app/build

# Complete the provided Maven skeleton with the reconciliation implementation.
cp "${SCRIPT_DIR}/App.java" \
    /app/reconcile-model-release/src/main/java/com/example/reconcile/App.java

# Build offline — every dependency was warmed into the local repo at image build.
mvn -o -B -q -f /app/reconcile-model-release/pom.xml package

# Derive the decision from the live sources and write the manifest.
java -jar /app/reconcile-model-release/target/reconcile-model-release-0.1.0.jar

cat /app/build/release-decision.json
