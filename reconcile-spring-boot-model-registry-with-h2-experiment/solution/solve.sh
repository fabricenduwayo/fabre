#!/bin/bash
# Oracle solution: implement the reconcile-model-release step, build it
# offline, and run it so the decision manifest is derived from the live
# registry API + H2 experiment store.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Make sure the provided registry API is serving (it normally starts on boot).
bash /app/start-registry.sh

# Complete the provided Maven skeleton with the reconciliation implementation.
cp "${SCRIPT_DIR}/App.java" \
    /app/reconcile-model-release/src/main/java/com/example/reconcile/App.java

# Build offline — every dependency was warmed into the local repo at image build.
mvn -o -B -q -f /app/reconcile-model-release/pom.xml package

# Derive the decision from the live sources and write the manifest.
java -jar /app/reconcile-model-release/target/reconcile-model-release-0.1.0.jar

cat /app/build/release-decision.json
