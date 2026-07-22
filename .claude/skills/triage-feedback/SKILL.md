---
name: Triage submission feedback
description: Read stb/LLMaJ submission feedback, skip the boilerplate, and classify the bounce into the three known cliffs with the fix. Use after a Snorkel/Harbor submission bounces or shows "AutoEval execution failed" and you need to name the real blocker instead of re-diagnosing the wrapper message.
argument-hint: [task-folder]
---

# Triage submission feedback

Advisory skill. It reads the eval feedback for one task, names the real blocker,
and hands back the one concrete next action. It does NOT edit the task, the ZIP,
or the submission.

## Step 0 - resolve the target task folder (do this first, every run)

The target is one task folder at the repo root /Users/fabrice-mac-mini/Documents/snorkel-ai (kebab-case, contains task.toml). Milestone tasks contain steps/milestone_N/ subfolders and no root instruction.md.

1. If $ARGUMENTS is non-empty, treat it as the target folder name (or path). Use it.
2. If $ARGUMENTS is empty, list the candidate task folders - every directory at the repo root that contains a task.toml, EXCLUDING .review-scratch/, docs/, jobs/, scripts/, tools/, and .git/ - and ask the user which one with AskUserQuestion. If exactly one candidate exists you may confirm it instead of asking.
3. Confirm the chosen path exists and contains task.toml. If it does not, stop and tell the user exactly what you looked for. Never guess or run against the wrong folder.
4. Detect the task type: milestone if steps/milestone_N/ folders exist and there is no root instruction.md; otherwise non-milestone. Remember it - later steps branch on it.

Do not proceed past Step 0 until the target folder is resolved and confirmed.

## Step 1 - ignore the wrapper line

The `revision_notes` line "AutoEval execution failed" (or "build FAILED") is
usually boilerplate for a submission that never reached a human reviewer. It is
not the diagnosis. Skip it.

- Do NOT ask Terminus Bot to explain "AutoEval Failure". The bot is literal and
  chases the wrapper message instead of the real LLMaJ summary.
- If the user only has the wrapper line so far, that is expected - go to Step 2
  to pull the real signal.

## Step 2 - get the real signal

The real reason lives in one of these, in order of preference:

1. The right side of the Web UI submission summary (difficulty, solvability,
   instruction sufficiency, per-test breakdown).
2. `stb submissions feedback` -> the Summary / LLMaJ section.
3. The difficulty-check artifact downloaded from the summary window - its job
   log names the exact failing command, file, or test.

If you can reach `stb` / the artifact, read it. If you cannot (no creds, no
access from here), stop and ask the user to paste one of:

- the Summary / LLMaJ text from the Web UI, or
- the difficulty-check artifact / job log.

Do not classify from the wrapper line alone. Wait for the real text.

## Step 3 - classify into one of the three cliffs

Match the summary to exactly one cliff. Key on the concrete evidence, not the
wrapper.

### Cliff 1 - oracle solution failed on the platform

- Evidence: reference oracle not 100% on the platform; difficulty-check build
  FAILED; a named failing command/file/test in the artifact log.
- Read: local `harbor run -a oracle` green is necessary but NOT sufficient -
  platform Docker/env drift, unpinned deps, or slow apt mirrors can still fail
  the oracle.
- Next action: download the difficulty-check artifact, read the exact failing
  command/file/test, fix it, re-run the oracle locally to green, then bump the
  ZIP (`# platform-revision: 2026-07-21-rN` in `environment/Dockerfile`) and
  resubmit. The platform may serve a cached build if the ZIP bytes do not change.

### Cliff 2 - difficulty TRIVIAL or EASY

- Evidence: `Difficulty: EASY` / `TRIVIAL - Requires at least MEDIUM`.
- Read: the diversity gate accepts MEDIUM or HARD only. Worst-model pass rate
  > 60% bounces as EASY/TRIVIAL. If `task.toml` `languages` includes `python`,
  the bar is HARD (best or worst pass rate <= 20% under the OR rule). Check the
  target's `task.toml` `languages` to know which bar applies - and flag if
  `python` is listed only because of the pytest verifier (that falsely triggers
  the HARD gate; the verifier does not count).
- Next action: harden with real interacting logic/state (waiver lifecycle keyed
  by id, sticky command-tag semantics, cross-request state). Do NOT relabel
  `task.toml` and do NOT pile on trivial edge cases - both are reviewer red
  flags and neither raises real difficulty.

### Cliff 3 - solvability (some tests not passed by any agent run)

- Evidence: `Unsolvable` / "some tests not passed by any agent run". Look at the
  per-test breakdown to split the two causes:
  - KILLER TEST: one or more tests passed by 0/10 agent runs. Root cause is a
    spec gap in `instruction.md` (requirement tested but not stated) or an
    over-strict / hidden-path test. Instruction sufficiency FAIL usually shows
    up here.
  - VERIFIER TIMEOUT: tests are passable but the verifier ran out of budget on
    5+ of 10 attempts (>= 6/10 must finish within budget).
- Next action (killer test): name the missing requirement in `instruction.md`
  (or the doc it points at) without giving the solution, or relax the over-strict
  test / accept reasonable output paths. Do not strip a tested requirement to
  chase difficulty.
- Next action (verifier timeout): trim the budget hogs - heavy image builds or
  one milestone soaking the agent budget, any installs in `test.sh` (forbidden
  anyway), and cold pip/cargo/uv dependency chains in the agent path.

## Step 4 - report

Give a compact verdict, most severe first, then the single next action.

- CLIFF: 1, 2, or 3 (with its name).
- EVIDENCE: the one line from the Summary / LLMaJ / artifact you keyed on.
- NEXT ACTION: one concrete step (the matching bullet above), specific to this
  task.

If the evidence genuinely fits none of the three cliffs, say so plainly and
quote the summary line you could not classify - do not force a fit. This skill
is advisory: report the diagnosis and stop. It does not edit the task.
