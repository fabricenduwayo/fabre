#!/bin/bash
# Build every vendor artifact version against the wire API it was written for
# and install it into the local Maven repository with its pom (so transitive
# dependency declarations survive).
set -euo pipefail

VENDOR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORK=/tmp/vendor-build
rm -rf "$WORK"
mkdir -p "$WORK"

build() {
    local artifact="$1" version="$2" cp="${3:-}"
    local src="$VENDOR/$artifact/$version/src"
    local out="$WORK/$artifact-$version"
    mkdir -p "$out"
    if [ -n "$cp" ]; then
        javac -cp "$cp" -d "$out" $(find "$src" -name '*.java')
    else
        javac -d "$out" $(find "$src" -name '*.java')
    fi
    jar cf "$WORK/$artifact-$version.jar" -C "$out" .
    mvn -B -q install:install-file \
        -Dfile="$WORK/$artifact-$version.jar" \
        -DpomFile="$VENDOR/$artifact/$version/pom.xml"
}

build wire-format 2.1.0
build wire-format 2.3.0
build wire-format 3.0.0

build telemetry-client 1.2.0 "$WORK/wire-format-2.1.0"
build telemetry-client 1.4.1 "$WORK/wire-format-2.1.0"

build format-legacy 0.9.0 "$WORK/wire-format-2.1.0"
build format-legacy 1.1.0 "$WORK/wire-format-3.0.0"

rm -rf "$WORK"
