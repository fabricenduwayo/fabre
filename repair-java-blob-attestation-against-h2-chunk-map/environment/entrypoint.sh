#!/usr/bin/env bash
# Container entrypoint: hand control to the requested command.
set -u
exec "$@"
