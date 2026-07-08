"""Turn platform feedback notes into a targeted fix brief for the Cursor agent."""

from __future__ import annotations

import re
from pathlib import Path


def _section_after(notes: str, heading: str) -> str:
    if heading not in notes:
        return ""
    return notes.split(heading, 1)[1].split("\n---", 1)[0].strip()


def triage_feedback(notes: str) -> dict[str, object]:
    """Extract structured blockers from stb feedback notes.txt."""
    out: dict[str, object] = {
        "difficulty_ok": bool(re.search(r"Difficulty:\s*✅", notes)),
        "difficulty_fail": None,
        "solvable_ok": bool(re.search(r"Status:\s*✅\s*Solvable", notes)),
        "solvable_fail": "Unsolvable" in notes or bool(re.search(r"Status:\s*❌", notes)),
        "instruction_sufficiency_fail": bool(
            re.search(r"Instruction Sufficiency:\s*❌", notes, re.IGNORECASE)
        ),
        "oracle_fail": bool(
            re.search(r"oracle:\s*0\.0%|oracle solution failed", notes, re.IGNORECASE)
        ),
        "quality_failures": [],
        "agent_performance": {},
        "autoeval_noise": "AutoEval execution failed" in notes,
    }

    diff_fail = re.search(r"Difficulty:\s*❌\s*(.+)", notes)
    if diff_fail:
        out["difficulty_fail"] = diff_fail.group(1).strip()

    qc = _section_after(notes, "Quality check summary")
    if qc:
        for match in re.finditer(r"❌\s*fail\s*-\s*([^:]+):\s*(.+?)(?=\n✅|\n➖|\n❌|\Z)", qc, re.DOTALL):
            out["quality_failures"].append(
                {"check": match.group(1).strip(), "detail": " ".join(match.group(2).split())[:800]}
            )

    perf = _section_after(notes, "Agent Performance:")
    if perf:
        for line in perf.splitlines():
            m = re.match(r"\s*•\s*([^:]+):\s*([\d.]+%)\s*\((\d+)/(\d+)", line)
            if m:
                out["agent_performance"][m.group(1).strip()] = {
                    "rate": m.group(2),
                    "passed": int(m.group(3)),
                    "total": int(m.group(4)),
                }

    analysis = _section_after(notes, "Analysis on Agent Failures:")
    if analysis and "FAIL" in analysis:
        out["failure_analysis"] = analysis[:2000]

    return out


def _languages_from_task(task_dir: Path) -> list[str]:
    toml = task_dir / "task.toml"
    if not toml.is_file():
        return []
    text = toml.read_text(encoding="utf-8")
    m = re.search(r'languages\s*=\s*\[([^\]]+)\]', text)
    if not m:
        return []
    return [x.strip().strip('"') for x in m.group(1).split(",") if x.strip()]


def generate_fix_brief(
    folder: str,
    notes: str,
    *,
    task_dir: Path | None = None,
) -> str:
    """Produce task-specific fix instructions from triaged feedback."""
    triage = triage_feedback(notes)
    langs = _languages_from_task(task_dir) if task_dir else []
    lines: list[str] = ["## Triage (from platform feedback)"]

    if triage.get("autoeval_noise"):
        lines.append(
            "- AutoEval build-failed line present — ignore unless oracle/static checks "
            "or a real build log failure is also reported (see terminus-lessons-learned §0)."
        )

    if triage.get("oracle_fail"):
        lines.append(
            "- **BLOCKER: platform oracle failed** — reproduce with "
            f"`harbor run -a oracle -p {folder}` locally; fix env/solution/timeouts; "
            "bump `# platform-revision:` before resubmit."
        )

    if triage.get("difficulty_fail"):
        fail = triage["difficulty_fail"]
        lines.append(f"- **BLOCKER: difficulty** — {fail}")
        if "python" in langs and "HARD" in str(fail).upper():
            lines.append(
                "  - Python in languages[] → measured gate is **HARD** (worst model ≤20%). "
                "Harden with interacting logic/state; do NOT relabel task.toml only."
            )
        elif "MEDIUM" in str(fail).upper() or "TRIVIAL" in str(fail).upper():
            lines.append(
                "  - Need **MEDIUM** (worst model ≤60%). Remove hand-holding from "
                "instruction.md; break env subtly; avoid cheat-sheets in seed/SQL."
            )

    if triage.get("instruction_sufficiency_fail"):
        lines.append(
            "- **BLOCKER: instruction sufficiency** — name every tested requirement in "
            "instruction.md (control IDs / amendment IDs OK; no solution hints). "
            "Keep instructions short and human-sounding."
        )

    for qf in triage.get("quality_failures") or []:
        check = qf["check"]
        detail = qf["detail"]
        lines.append(f"- **Quality fail: {check}** — {detail[:400]}")
        if check == "behavior_in_task_description":
            lines.append(
                "  - Fix: signpost amended controls in instruction.md; everything tested "
                "must be stated or clearly implied there."
            )

    if triage.get("solvable_fail"):
        lines.append(
            "- **BLOCKER: solvability** — find killer tests (0/N agent passes); fix spec "
            "gap in instruction.md OR over-strict test; do not strip real difficulty."
        )

    perf = triage.get("agent_performance") or {}
    if perf and not triage.get("difficulty_ok"):
        rates = [v["rate"] for v in perf.values() if isinstance(v, dict)]
        if rates and all(r.startswith("100") for r in rates):
            lines.append(
                "- Both frontier models at 100% — task is too easy; env must stay broken "
                "on non-obvious bugs."
            )

    # Task-specific hints from known patterns
    if folder == "harden-php-api-defaults":
        lines.extend(
            [
                "",
                "## PHP-specific fix plan",
                "- Difficulty MEDIUM is already passing — **do not** re-add a full control "
                "checklist that makes the task TRIVIAL again.",
                "- Add **control-name signposting** only: CO-ORIGIN-ALLOW (incl. Vary), "
                "CO-PREFLIGHT (G-2026-11), AC-BOOTSTRAP (G-2026-03/05/15/16), AC-HEALTH "
                "(G-2026-04), AC-TOKEN-STORE (G-2026-12 digest), AU-LEDGER-SCOPE (G-2026-06), "
                "EH-NO-DISCLOSE.",
                "- Keep 'reconcile full standard' framing; no status-code literals as hints.",
            ]
        )
    elif folder == "repair-express-trivia-worker":
        lines.extend(
            [
                "",
                "## Trivia-specific fix plan",
                "- Python task → must be **HARD** (≤20% worst model).",
                "- Latest eval: 100%/100% TRIVIAL — re-harden without undoing solvability "
                "(H-2026-34 delta=0 at ceiling must stay documented).",
                "- Tests must drive `/app/worker/replay.py`, not only helpers.",
            ]
        )
    elif folder == "repair-java-trailswitch-graph-rules":
        lines.extend(
            [
                "",
                "## Trailswitch-specific fix plan",
                "- Need MEDIUM (≤60%); latest eval 100%/100% TRIVIAL.",
                "- Contract already has ascending rule_priority — re-break env Java "
                "(SwitchRuleHandler clear/lock, lock-group relay) without cheat-sheets.",
                "- category must stay `games` (debugging blocked on platform).",
            ]
        )
    elif folder == "reproduce-java-aes-gcm-findings":
        lines.extend(
            [
                "",
                "## AES-specific fix plan",
                "- Platform oracle failed — verify all three milestones locally.",
                "- If oracle green locally, bump platform-revision and check image size/timeouts.",
                "- Broken scaffold bugs must require real repair, not stub-from-scratch.",
            ]
        )

    lines.append("")
    lines.append("## Do not")
    lines.append("- Send to reviewer.")
    lines.append("- Commit unless the user asked (monitor runs may commit per project rules).")
    lines.append("- Relabel difficulty without measured pass-rate change.")

    return "\n".join(lines)
