#!/bin/bash
set -euo pipefail

SRC=/app/cpp-auditor/src
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Bring the auditor into compliance with the current Standard (body + Appendix G):
# - parser: primary-group membership, locked-account detection incl. *LK* and the
#   extended non-interactive shell set, sudoers negation/last-match, NOPASSWD-on-ALL,
#   Defaults !authenticate, #includedir resolution, and sshd drop-in precedence with
#   Match-block handling (incl. Match all) and the KbdInteractive alias.
cp "$HERE/parse.cpp" "$SRC/parse.cpp"
# - rules: lowered service-account uid ceiling, extended exempt roster, and the
#   prohibit-password/without-password allowance for PermitRootLogin.
cp "$HERE/audit.cpp" "$SRC/audit.cpp"
# - handler: restore per-request isolation (the shipped service caches account
#   facts in a process-wide registry, so audits drift across hosts) and fix the
#   audit ledger, which silently stopped writing because the on-disk file is in
#   the legacy schema-1 layout; migrate it to schema 2 and keep appending.
cp "$HERE/main.cpp" "$SRC/main.cpp"

cmake -S /app/cpp-auditor -B /app/cpp-auditor/build
cmake --build /app/cpp-auditor/build -j 2
