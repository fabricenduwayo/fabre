---
name: Draft explanation fields
description: Draft the three platform explanation fields (difficulty, solution, verification) in Fabrice's voice, grounded in the real shipped task, and authorship-scan them. Use before any submit/resubmit so no submission goes out with blank or stale explanations. Reads the task's instruction, tests, and solution to get real test/milestone counts and what the tests actually drive, writes the drafts to <task>/.submission-explanations.txt, then runs the authorship scans. Works for both milestone and non-milestone tasks.
argument-hint: [task-folder]
---

Draft the three platform explanation fields so a submission never goes out blank or stale. The fields are `difficulty_explanation`, `solution_explanation`, `verification_explanation`. They must read as Fabrice wrote them and match the task actually shipped. You draft them; Fabrice reviews and approves.

## Step 0 - resolve the target task folder (do this first, every run)

The target is one task folder at the repo root /Users/fabrice-mac-mini/Documents/snorkel-ai (kebab-case, contains task.toml). Milestone tasks contain steps/milestone_N/ subfolders and no root instruction.md.

1. If $ARGUMENTS is non-empty, treat it as the target folder name (or path). Use it.
2. If $ARGUMENTS is empty, list the candidate task folders - every directory at the repo root that contains a task.toml, EXCLUDING .review-scratch/, docs/, jobs/, scripts/, tools/, and .git/ - and ask the user which one with AskUserQuestion. If exactly one candidate exists you may confirm it instead of asking.
3. Confirm the chosen path exists and contains task.toml. If it does not, stop and tell the user exactly what you looked for. Never guess or run against the wrong folder.
4. Detect the task type: milestone if steps/milestone_N/ folders exist and there is no root instruction.md; otherwise non-milestone. Remember it - later steps branch on it.

Do not proceed past Step 0 until the target folder is resolved and confirmed.

## Step 1 - ground in the shipped task (get real numbers)

Read the actual files. Do not draft from memory or from the task name. Below, `<task>` is the resolved absolute path from Step 0.

Non-milestone:
- Read `<task>/instruction.md` - requirements, and any counts the narrative states (amendments, revisions, corpus size, control IDs).
- Read `<task>/task.toml` - `difficulty`, `languages`, `category`, `number_of_milestones` (0 here).
- Read `<task>/tests/test_outputs.py` and `<task>/tests/helpers.py` - what the tests exercise.
- Read `<task>/solution/` (the sources and `solve.sh`) - the reference approach and key insight.

Milestone:
- Read every `<task>/steps/milestone_N/instruction.md`.
- Read `<task>/task.toml` - `number_of_milestones` must equal the count of `steps/milestone_*` dirs.
- Read every `<task>/steps/milestone_N/tests/test_*.py`.
- Read every `<task>/steps/milestone_N/solution/` (`solve.sh` and any staged sources).

Pull the real numbers with these (substitute the real path for `<task>`):
- Test count (non-milestone): `rg -c '^\s*def test_' <task>/tests/test_outputs.py`
- Test count per milestone: `rg -c '^\s*def test_' <task>/steps/milestone_*/tests/test_*.py`
- Randomized / parametrized cases: `rg -n 'parametrize|range\(|random|seed' <task>/tests/test_outputs.py` (or the milestone test files)
- Does pytest drive the real artifact, or only helpers? `rg -n 'subprocess|Popen|check_output|requests\.|http|sqlite3|Main|_run_stage' <task>/tests/test_outputs.py` (or the milestone test files). If the primary tests only call `helpers.*` and never execute the agent's program, say that honestly - do not claim they drive a live service.
- Milestone count: `ls -d <task>/steps/milestone_* 2>/dev/null | wc -l` and compare to `number_of_milestones`.

Before drafting, skim 2-3 existing `<other-task>/.submission-explanations.txt` files (e.g. `harden-php-api-defaults`, `reproduce-java-aes-gcm-findings`) for voice. Terse, concrete, engineer tone - that is the reference, not general good technical writing.

## Step 2 - draft the three fields

Each field is one paragraph, about 4-6 sentences, in Fabrice's own words. ASCII hyphen `-` only, never `—` or `–`. No AI smell (furthermore, additionally, it is worth noting, leverage, robust, seamless, comprehensive, delve into). Short direct sentences a working engineer would write. No bullet lists inside a field.

- `difficulty_explanation` - why the task is hard for an AGENT, not just a human. Point at the interacting state or reasoning the agent has to do (lifecycle pairing, cross-file/timeline reconciliation, sticky semantics), not a list of edge cases. Do not restate the instruction.
- `solution_explanation` - the high-level approach and the key insight behind it. NOT a step-by-step command walkthrough. Say what the oracle does at the level of "reads X, resolves Y through Z, joins to W", not "run this then that".
- `verification_explanation` - what the tests actually drive (the real service / CLI / compiled stage / DB, not source inspection), the real test count from Step 1, and how expected values are derived or replayed (hidden fixtures, a reference state machine, a forced failure injection). For milestone tasks, give one or two sentences per milestone on what its verifier reruns and checks.

## Step 3 - consistency and staleness pass

The three fields must agree with each other and with the shipped task.

- Counts match reality: the test count in `verification_explanation`, and the milestone count referenced anywhere, match Step 1. Non-milestone: milestone count is NA.
- No stale wording: do not call a trimmed corpus "long", do not cite an amendment/revision count the current files no longer have, do not name a stage or control the task dropped. Cross-check every number and adjective against the files you read.
- `verification_explanation` describes tests driving the real artifact only if Step 1 showed they do.

## Step 4 - save the local copy

Write the drafts to `<task>/.submission-explanations.txt` with the Write tool. Use this exact three-section shape (matches the existing convention so /safe-resubmit can pick the fields up):

```
DIFFICULTY

<paragraph>

SOLUTION

<paragraph>

VERIFICATION

<paragraph>
```

## Step 5 - authorship scans

Run the scans against the saved file. If an `/authorship-scan` skill is available you may hand off to it and paste its output instead; otherwise run these inline (substitute the real path for `<task>`) - each must return nothing:

```bash
rg -n $'—|–' <task>/.submission-explanations.txt
rg -in 'furthermore|it is worth noting|in conclusion|additionally|moreover|delve into|leverag|game changer' <task>/.submission-explanations.txt
rg -in 'really|deliverable|as follows|the following|ensure that|in order to|note that|utilize|robust|seamless|comprehensive' <task>/.submission-explanations.txt
rg -no '[`\w]+, [`\w]+ (and|or) ' <task>/.submission-explanations.txt
rg -n 'DRAFT|HUMAN REVIEW REQUIRED|NEEDS HUMAN REVIEW|Co-authored-by|Generated by' <task>/.submission-explanations.txt
```

Paste the raw output. Any hit is a FAIL - fix the wording in the file and re-run until all five are clean. Do not claim the drafts pass the authorship check without pasting a clean run.

## Step 6 - report

Show a compact verdict, most severe first, then a short prioritized fix list:

```
authorship scans   PASS/FAIL/NA - clean / <hit>
consistency        PASS/FAIL/NA - N tests, M milestones match the files
verification draft PASS/FAIL/NA - drives real <service/CLI/DB>, count N
difficulty draft   PASS/FAIL/NA - agent-facing reason, not edge-case spam
solution draft     PASS/FAIL/NA - approach + insight, no command walkthrough
saved file         PASS/FAIL/NA - <task>/.submission-explanations.txt
```

Milestone count is NA on non-milestone tasks. Then note: these three fields feed the single combined `create_submission` payload that /safe-resubmit assembles alongside the ZIP and rubrics. Do not push them to the platform here.
