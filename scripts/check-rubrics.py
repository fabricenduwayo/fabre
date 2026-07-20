#!/usr/bin/env python3
"""Check rubric files against the Terminus Edition 2 rubric rules.

Usage:
    python3 scripts/check-rubrics.py [path ...]

With no arguments it checks .review-scratch/*-rubrics.txt. Exits non-zero if any
file fails. Rules come from .cursor/rules/terminus-rubrics.mdc.
"""

import glob
import os
import re
import sys

ALLOWED = {1, 2, 3, 5}
CRITERION = re.compile(r"^(Agent\b.*),\s*([+-]\d+)$")


def check(path):
    errors = []
    positive = 0
    negative = 0
    blocks = set()

    for lineno, raw in enumerate(open(path), 1):
        line = raw.strip()
        if not line:
            continue
        if line.startswith("# Rubric"):
            blocks.add(line)
            continue

        match = CRITERION.match(line)
        if not match:
            errors.append(f"L{lineno}: must start with 'Agent' and end with ', +/-N' -> {line[:60]!r}")
            continue

        score = match.group(2)
        value = int(score)
        if abs(value) not in ALLOWED:
            errors.append(f"L{lineno}: illegal score {score} (only +/-1, 2, 3, 5; 4 is forbidden)")
        if value > 0:
            if not score.startswith("+"):
                errors.append(f"L{lineno}: positive score needs an explicit '+' -> {score}")
            positive += value
        else:
            negative += 1

    if negative < 3:
        errors.append(f"only {negative} negative criteria (need at least 3)")

    count = len(blocks) or 1
    low, high = 10 * count, 40 * count
    if not low <= positive <= high:
        suffix = f" across {count} milestone blocks" if count > 1 else ""
        errors.append(f"positive total {positive} outside {low}-{high}{suffix}")

    return positive, negative, count, errors


def main(argv):
    paths = argv[1:] or sorted(glob.glob(".review-scratch/*-rubrics.txt"))
    if not paths:
        print("no rubric files found", file=sys.stderr)
        return 1

    failed = 0
    for path in paths:
        positive, negative, blocks, errors = check(path)
        status = "OK  " if not errors else "FAIL"
        print(f"[{status}] {os.path.basename(path):28} pos={positive:3} neg={negative} blocks={blocks}")
        for error in errors:
            print(f"         - {error}")
        failed += bool(errors)

    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
