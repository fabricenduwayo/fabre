"""Parse platform feedback to decide if auto-fix should be skipped."""

from __future__ import annotations

import re


def is_green_autoeval_only_bounce(notes: str) -> bool:
    """True when eval is green except AutoEval boilerplate — do not auto-fix.

    Per docs/terminus-lessons-learned.md §0.1, "AutoEval execution failed" is
    usually noise when difficulty, instruction sufficiency, solvability, and
    quality checks are already passing.
    """
    if not notes.strip():
        return False

    has_autoeval_noise = (
        "AutoEval execution failed" in notes
        or "AutoEval Execution Summary" in notes
    )
    if not has_autoeval_noise:
        return False

    if re.search(r"Difficulty:\s*❌", notes):
        return False
    if not re.search(r"Difficulty:\s*✅", notes):
        return False

    if re.search(r"Instruction Sufficiency:\s*❌", notes, re.IGNORECASE):
        return False

    if re.search(r"Status:\s*❌", notes) or "Unsolvable" in notes:
        return False
    if not re.search(r"Status:\s*✅\s*Solvable", notes):
        return False

    if "Quality check summary" in notes:
        qc = notes.split("Quality check summary", 1)[1]
        if re.search(r"❌\s*fail", qc, re.IGNORECASE):
            return False
        if re.search(r"static checks:\s*FAIL", qc, re.IGNORECASE):
            return False

    if re.search(r"oracle:\s*0\.0%|oracle solution failed", notes, re.IGNORECASE):
        return False

    return True


def skip_reason_label(notes: str) -> str:
    if is_green_autoeval_only_bounce(notes):
        return "green_autoeval_only_bounce"
    return ""
