---
name: safe-resubmit
description: Safely prepare and perform a NEEDS_REVISION resubmit as one combined ZIP-plus-fields payload, with all guardrails, without sending to a reviewer. Use before every Terminus resubmit so you never lock the assignment with blank fields or overwrite an edited rubric. Runs the pre-flight gate, busts the platform cache, assembles the single combined create_submission, then stops before any reviewer send.
argument-hint: [task-folder]
---

# safe-resubmit

Encode the submission state machine so a resubmit never locks the assignment or overwrites the rubric. This skill prepares and performs the combined update. It never sends to a reviewer on its own. Source rules: `.cursor/rules/terminus-submission-hardening.mdc`, `.cursor/rules/terminus-rubrics.mdc`, `docs/terminus-lessons-learned.md` sections 1.1-1.6 (especially 1.3, 1.3a).

## Step 0 - resolve the target task folder (do this first, every run)

The target is one task folder at the repo root /Users/fabrice-mac-mini/Documents/snorkel-ai (kebab-case, contains task.toml).

1. If $ARGUMENTS is non-empty, treat it as the target folder name (or path). Use it.
2. If $ARGUMENTS is empty, list the candidate task folders - every directory at the repo root that contains a task.toml, EXCLUDING .review-scratch/, docs/, jobs/, scripts/, tools/, and .git/ - and ask the user which one with AskUserQuestion. If exactly one candidate exists you may confirm it instead of asking.
3. Confirm the chosen path exists and contains task.toml. If it does not, stop and tell the user exactly what you looked for. Never guess or run against the wrong folder.
4. Detect the task type. The canonical signal is `number_of_milestones` in `<task>/task.toml`: `> 0` means milestone, `0` (or absent) means non-milestone. Milestone tasks also carry `steps/milestone_N/` folders and no root `instruction.md`; non-milestone tasks have a root `instruction.md`. Remember the type - later steps branch on it.

Do not proceed past Step 0 until the target folder is resolved and confirmed.

## Step 1 - precondition: assignment must be NEEDS_REVISION

Do this before any revision work. Editing a locked assignment wastes the pass and needs an admin to unlock.

1. Read the submission id from `<task>/.snorkel_config` (`submission_id: <uuid>`).
2. Confirm the assignment state is `NEEDS_REVISION`. Read it from the portal assignment page (authoritative for state). In the terminal, the documented `stb submissions feedback` surfaces the submission summary, and the repo's `.review-scratch/resubmit_*.py` scripts resolve the assignment through the `snorkelai_stb` SDK (`get_assignment_id_for_submission`, `get_existing_submission_payload`). If you cannot confirm the state is `NEEDS_REVISION`, stop and ask - do not guess.
3. If the state is `REVIEW_PENDING` or `EVALUATION_PENDING`, STOP. Those are locked. There is no self-service recall from `REVIEW_PENDING` - only an admin returns it to `NEEDS_REVISION`. Report the state and stop; do not touch the ZIP or any field.

Never run any create/update against a task that is not `NEEDS_REVISION`.

## Step 2 - pre-flight gate (all four must pass)

Run these first. Do not proceed if any fails. Prefer the sibling skills; if a sibling is not present, run the fallback and report it.

1. Oracle green + NOP fails locally - run `/verify-local <task>`. Fallback: `export ANTHROPIC_API_KEY=dummy` then `harbor run -a oracle -p <task>` (expect reward 1.0) and `harbor run -a nop -p <task>` (expect reward 0.0). Never use Fabrice's personal API key (see `.cursor/rules/personal-api-key-consent.mdc`).
2. Authorship scans clean - run `/authorship-scan <task>`. No AI-smell, no em/en dashes, Fabrice's tone across instruction.md, README, submission notes, commit messages.
3. Rubric valid - run `/rubric-lint <task>`. Fallback: `python3 /Users/fabrice-mac-mini/Documents/snorkel-ai/scripts/check-rubrics.py <rubric-file>`. Rubric shape must match the task type from Step 0: non-milestone is a flat list with >= 3 negative criteria; milestone is one `# Rubric N` block per milestone, each with >= 1 negative and a 10-40 positive total.
4. All three explanation fields drafted - run `/draft-explanations <task>`. Confirm `difficulty_explanation`, `solution_explanation`, `verification_explanation` are all written (roughly one paragraph, 4-6 sentences each), consistent with the shipped task, and saved locally (e.g. `<task>/.submission-explanations.txt`). Reviewers reject blank ones.

If any check fails, stop and report the failure. Do not resubmit on a red gate.

## Step 3 - bust the platform cache

Re-uploading identical ZIP bytes can serve a cached build and mask your fix. Bump the cache-bust comment in `<task>/environment/Dockerfile`:

```
# platform-revision: 2026-07-21-rN
```

Use today's date (2026-07-21). Increment `rN` (r1, r2, ...) each resubmit on the same day. Leave the canonical base image line above it untouched:

```
FROM public.ecr.aws/docker/library/python:3.13-slim-bookworm@sha256:01f42367a0a94ad4bc17111776fd66e3500c1d87c15bbd6055b7371d39c124fb
```

Do not bump the base digest to a "newer" public one - it fails AutoEval with `manifest verification failed`.

## Step 4 - assemble ONE combined payload

Assemble a single `create_submission` payload that carries the ZIP and every platform field together:

- `upload_a_zip_file` - the bumped ZIP built from `<task>/`
- `difficulty_explanation`
- `solution_explanation`
- `verification_explanation`
- `test_rubrics` - the validated rubric text from Step 2 (flat list, or `# Rubric N` blocks for milestone)
- `checkbox_evaluate_rubrics` - UNTICKED (see Step 5)

Rules for the payload:

- NEVER push the platform fields before the ZIP. A payload-only (fields-only) create_submission flips the assignment to `EVALUATION_PENDING` and locks it; the follow-up ZIP upload then returns 403 and needs an admin to unlock (lessons-learned 1.3, 1.3a).
- The `stb submissions update` CLI merges only the ZIP - it carries none of the platform fields. So the combined action is one of:
  - the single UI submission form: attach the bumped ZIP, paste all three explanations and `test_rubrics`, set the rubric checkbox unticked, submit once; or
  - the stb Python API `create_submission` with `upload_a_zip_file` plus all five fields in one call.
- Do not run the CLI `update` and then try to fill fields afterward - the update triggers evaluation and locks the task with the fields still blank.

## Step 5 - rubric checkbox nuance

`checkbox_evaluate_rubrics` is the generate toggle. If it is left ticked when you send, it can OVERWRITE the rubric you edited with a fresh synthetic draft.

- This skill carries an already-edited, validated rubric in `test_rubrics`. Keep `checkbox_evaluate_rubrics` UNTICKED so your edits survive.
- Only tick it if no rubric has ever been generated and you deliberately want the platform to draft one - that is a separate generate pass, not this resubmit.
- Untick it before the final send to reviewer, always.

## Step 6 - perform the combined update, no reviewer send

Perform the single combined action from Step 4 with reviewer sending OFF. Only two paths carry the ZIP and all platform fields in one action - do NOT reach for the CLI `stb submissions update` here, it merges the ZIP alone and would lock the task with the fields still blank:

- UI path: submit the one form - attach the bumped ZIP, paste the three explanations and `test_rubrics`, leave `checkbox_evaluate_rubrics` unticked, submit once. Do not click send-to-reviewer.
- API path: one `create_submission` call carrying `upload_a_zip_file` plus all five fields, with `checkbox_send_to_reviewer = None` (the no-send equivalent). This mirrors the repo's `.review-scratch/resubmit_*.py` scripts; adapt one for the target task rather than writing a fresh flow.

Default every submit to no-send-to-reviewer. The documented `stb submissions update` / submit flow defaults to send-on, so the opt-out is mandatory. Sending to a reviewer is a separate, final step the user explicitly approves - do NOT do it automatically, and do not send "just to see what happens" (there is no recall from `REVIEW_PENDING`).

Never use Fabrice's personal API key for any of this without explicit per-run authorization for that run.

## Step 7 - report and stop

Stop here and wait for the user. Do not send to a reviewer.

Report in this order:

1. Pre-flight checklist - one line per gate, most severe FAIL first: `PASS/FAIL/NA - <check> - <one line of evidence>`. Cover state precondition (Step 1), oracle+NOP, authorship, rubric, explanations, cache-bust.
2. The exact single-payload plan - the five platform fields plus the ZIP, the checkbox state (unticked), the task type (milestone / non-milestone), and the exact command or UI action you will run to submit as ONE combined create_submission with no reviewer send.
3. A short prioritized fix list if any gate is red.

If every gate is green, state that the combined update is ready and ask the user to confirm before you run it. After the update lands, remind the user that sending to the reviewer is a separate step they must explicitly approve.
