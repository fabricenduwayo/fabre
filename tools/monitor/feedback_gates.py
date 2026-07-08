"""Parse platform feedback to decide if auto-fix should be skipped."""

from __future__ import annotations

import re


def eval_gates_green(notes: str) -> bool:
    """True when difficulty, solvability, sufficiency, and quality checks all pass.

    A NEEDS_REVISION bounce with green gates means the task content is fine —
    the remaining work is platform-field/UI edits (explanations, rubric) or
    AutoEval infra noise. The agent must not rewrite the task in that case.
    """
    if not notes.strip():
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


def is_green_autoeval_only_bounce(notes: str) -> bool:
    """True when eval is green except AutoEval boilerplate — do not auto-fix.

    Per docs/terminus-lessons-learned.md §0.1, "AutoEval execution failed" is
    usually noise when difficulty, instruction sufficiency, solvability, and
    quality checks are already passing.
    """
    has_autoeval_noise = (
        "AutoEval execution failed" in notes
        or "AutoEval Execution Summary" in notes
    )
    return has_autoeval_noise and eval_gates_green(notes)


def green_eval_skip_reason(notes: str) -> str | None:
    """Return a skip reason when the eval gates are green, else None.

    "manual_ui_fields_only": all content gates passed; anything left in the
    revision notes is a platform-field edit (explanations/rubric/paragraph
    style) the owner does in the UI — the agent must not touch the task.
    """
    if not eval_gates_green(notes):
        return None
    if is_green_autoeval_only_bounce(notes):
        return "green_autoeval_only"
    return "manual_ui_fields_only"


def skip_reason_label(notes: str) -> str:
    return green_eval_skip_reason(notes) or ""
