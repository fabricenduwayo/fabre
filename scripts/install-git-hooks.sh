#!/bin/bash
# Point this repo at .githooks/ so Co-authored-by: Cursor is stripped on every commit.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HOOKS="$REPO_ROOT/.githooks"

chmod +x "$HOOKS/prepare-commit-msg"
git -C "$REPO_ROOT" config core.hooksPath .githooks

echo "Installed git hooks: core.hooksPath=.githooks"
echo "Co-authored-by: Cursor lines will be removed from local commits."
