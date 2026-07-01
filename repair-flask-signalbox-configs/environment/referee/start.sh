#!/bin/bash
set -euo pipefail
cd /app/referee
exec python3 app.py
