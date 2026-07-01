#!/bin/bash
set -euo pipefail
cd /app/referee
exec /usr/bin/node src/server.js
