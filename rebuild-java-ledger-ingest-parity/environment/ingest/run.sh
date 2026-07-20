#!/bin/bash
set -euo pipefail
CORPUS="${1:?usage: run.sh <corpus-dir> <jdbc-url> <summary-json>}"
JDBC="${2:?}"
SUMMARY="${3:?}"
java -cp "/app/ingest/classes:/app/lib/*" com.snorkel.ingest.Main "$CORPUS" "$JDBC" "$SUMMARY"
