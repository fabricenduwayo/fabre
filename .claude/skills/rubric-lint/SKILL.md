---
name: rubric-lint
description: Lint a task rubric for CI format rules and semantic quality (reuses scripts/check-rubrics.py). Use before submitting or reviewing a Terminus task rubric to catch both the mechanical format failures the CI enforces and the semantic problems (test/meta references, negated phrasing, opposite trap, mis-scored severity, generic draft criteria) the script cannot see.
argument-hint: [task-folder]
---

# rubric-lint

Validate one task's rubric against the CI-enforced format rules AND the semantic quality rules the mechanical checker cannot see. Rules live in /Users/fabrice-mac-mini/Documents/snorkel-ai/.cursor/rules/terminus-rubrics.mdc and the reviewer bar in .cursor/rules/terminus-reviewer-checklist.mdc.

## Step 0 - resolve the target task folder (do this first, every run)

The target is one task folder at the repo root /Users/fabrice-mac-mini/Documents/snorkel-ai (kebab-case, contains task.toml). Milestone tasks contain steps/milestone_N/ subfolders and no root instruction.md.

1. If $ARGUMENTS is non-empty, treat it as the target folder name (or path). Use it.
2. If $ARGUMENTS is empty, list the candidate task folders - every directory at the repo root that contains a task.toml, EXCLUDING .review-scratch/, docs/, jobs/, scripts/, tools/, and .git/ - and ask the user which one with AskUserQuestion. If exactly one candidate exists you may confirm it instead of asking.
3. Confirm the chosen path exists and contains task.toml. If it does not, stop and tell the user exactly what you looked for. Never guess or run against the wrong folder.
4. Detect the task type: milestone if steps/milestone_N/ folders exist and there is no root instruction.md; otherwise non-milestone. Remember it - later steps branch on it.

Do not proceed past Step 0 until the target folder is resolved and confirmed.

## Step 1 - locate the rubric text

The rubric is a PLATFORM field (`test_rubrics`), never in the task ZIP or the task folder. The working copy lives in /Users/fabrice-mac-mini/Documents/snorkel-ai/.review-scratch/ as `<slug>-rubrics.txt`, where the slug is usually a shortened form of the folder name (folder `repair-java-blob-attestation-against-h2-chunk-map` -> `blob-attestation-rubrics.txt`; `reproduce-java-tls-waiver-findings` -> `tls-rubrics.txt`).

1. `ls /Users/fabrice-mac-mini/Documents/snorkel-ai/.review-scratch/*-rubrics.txt` and match a distinctive token from the folder name against the filenames.
2. Exactly one plausible match -> use it. Several plausible -> ask the user which. None -> ask the user to paste the rubric or give a path; write it to `.review-scratch/<slug>-rubrics.txt` so the linter can read it.
3. Read the matched file and report its full path before linting.

## Step 2 - run the mechanical linter (do not reimplement it)

Run:

    python3 /Users/fabrice-mac-mini/Documents/snorkel-ai/scripts/check-rubrics.py <rubric-path>

Report its output verbatim (OK/FAIL, pos/neg/blocks counts, and any per-line errors). It already enforces the following, so you do NOT re-check these by hand:

- every line starts with `Agent` and ends `, +/-N`
- scores are only +/- 1, 2, 3, 5 (4 is rejected)
- positive scores carry an explicit `+`
- at least 3 negative criteria total
- the summed positive total lands in 10-40; for M `# Rubric` blocks the range scales to M*10..M*40, but the script only tests the COMBINED total against that range - it does not check any single block's subtotal (see Step 3 rule 8)

If the script exits non-zero, those are hard CI failures - carry them into the final report as FAIL lines first.

## Step 3 - semantic pass (line by line, what the script cannot see)

Read the rubric line by line and flag each of these. Cite the offending line.

1. Test/pytest references: no mention of `/tests/`, `test.sh`, pytest, or reward.txt. Those run after the trace. Exception: the task itself is a testing task.
2. Meta-checks: no criterion about the agent reading `task.toml` or `instruction.md`. Those are passed automatically and are not engineering work.
3. Oracle/NOP: no mention of oracle or NOP runs (e.g. "oracle passes consistently").
4. Negated phrasing: criteria state the fact and let the sign judge. Flag negated sentences like `Agent does not access /app/secret/, +1`; the fix is `Agent accesses /app/secret/, -1`.
5. Opposite trap: no severe violation downgraded to a small positive, and no rewarding a basic expectation. Flag e.g. `Agent performs all operations in /app, +1`; the fix penalizes the violation: `Agent operates outside of /app, -5`.
6. Specific and binary: each criterion is a concrete, verifiable action with one yes/no answer. Flag vague ones like `Agent handles edge cases in logic, +2` or `Agent parses input correctly, +2`.
7. Severity mapping: score matches importance. Critical work (safety, core correctness, leaking secrets) is +/-5, major (reliability, verifying artifacts, error recovery) is +/-3, minor (inspection, hygiene, tool flags) is +/-1 to +/-2. Flag a critical action scored +/-1, or a trivial inspection scored +/-5.
8. Block structure (branch on Step 0 task type):
   - Milestone: one `# Rubric N` header per milestone; header count equal to `number_of_milestones` (from task.toml); each block carries >= 1 negative criterion; each block's own positive subtotal lands in 10-40. The mechanical linter sums ALL positives and checks only the combined total against N*10..N*40 - it does NOT verify per-block subtotals, per-block negatives, or header count. Verify all three by hand here.
   - Non-milestone: a flat list. A single `# Rubric 1` header is tolerated; flag any `# Rubric 2` or higher.
9. Generic draft residue: the platform generate step emits a synthetic draft. Flag criteria that read generic and untailored (could apply to any task, restate the instruction verbatim, or repeat boilerplate). They must be rewritten to name this task's real files, commands, and failure modes.
10. Perfect-score sanity: a perfect score should be rare on a frontier task. Note if the positives are so easy that the oracle-level work is under-weighted.

## Step 4 - report

Show a compact verdict, most severe first:

- One line per finding: `PASS`/`FAIL`/`NA`, the rule, and one line of evidence (quote the line and give its line number). Hard CI failures from Step 2 rank above semantic ones. Within semantic, order by reviewer severity: High (test/meta references, < 3 negatives, bad scores, vague criteria, block format) above Medium (per-milestone negative, severity mapping, negated phrasing, oracle/NOP) above Low (10-40 points). Report generic-draft residue (rule 9) and perfect-score sanity (rule 10) as Low notes unless they coincide with a High failure.
- Then a short prioritized fix list: the exact edits needed, each as the current line -> the replacement line.
- End with an overall `PASS` or `FAIL`. FAIL if any CI check failed or any High semantic criterion failed.

Do not edit the rubric file unless the user asks. The report is the deliverable.
