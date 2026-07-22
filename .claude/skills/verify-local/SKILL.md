---
name: Verify local
description: Run the local oracle/NOP reward gate the sanctioned way before every submit or resubmit - oracle must land reward 1.0 and NOP must land reward 0.0, with a dummy key, per-milestone for milestone tasks. Use this before any stb submit/resubmit, after any task edit, or whenever you need to prove a task is reward-trustworthy locally.
argument-hint: [task-folder]
---

# verify-local

Run the local Harbor reward gate for one task and report a clear PASS/FAIL. Oracle must land reward 1.0, NOP must land reward 0.0. Nothing here submits or sends to a reviewer.

## Step 0 - resolve the target task folder (do this first, every run)

The target is one task folder at the repo root /Users/fabrice-mac-mini/Documents/snorkel-ai (kebab-case, contains task.toml). Milestone tasks contain steps/milestone_N/ subfolders and no root instruction.md.

1. If $ARGUMENTS is non-empty, treat it as the target folder name (or path). Use it.
2. If $ARGUMENTS is empty, list the candidate task folders - every directory at the repo root that contains a task.toml, EXCLUDING .review-scratch/, docs/, jobs/, scripts/, tools/, and .git/ - and ask the user which one with AskUserQuestion. If exactly one candidate exists you may confirm it instead of asking.
3. Confirm the chosen path exists and contains task.toml. If it does not, stop and tell the user exactly what you looked for. Never guess or run against the wrong folder.
4. Detect the task type: milestone if steps/milestone_N/ folders exist and there is no root instruction.md; otherwise non-milestone. Remember it - later steps branch on it.

Do not proceed past Step 0 until the target folder is resolved and confirmed.

## Step 1 - set the dummy key

Run:

```bash
export ANTHROPIC_API_KEY=dummy
```

Never substitute a personal key. A key already in the environment, shell profile, or macOS Keychain is not permission to use it (see /Users/fabrice-mac-mini/Documents/snorkel-ai/.cursor/rules/personal-api-key-consent.mdc). Local Harbor verifier runs are deterministic and do not need a billable key. Never print, echo, or log a key.

## Step 2 - warn that this is slow

These runs build and start Docker containers and can take several minutes each (oracle + NOP = two full builds/runs; milestone tasks run every milestone). Tell the user this before you start so a long-running command is expected, not a hang.

## Step 3 - run the gate

Run oracle first, then NOP. Both in the same terminal session where ANTHROPIC_API_KEY=dummy is exported.

### Non-milestone task

```bash
harbor run -a oracle -p <task-folder>   # must land reward 1.0
harbor run -a nop -p <task-folder>      # must land reward 0.0
```

Read the reward Harbor reports at the end of each run (1.0 = pass, 0.0 = fail). If the printed summary is ambiguous, read /logs/verifier/reward.txt inside that run - the verifier writes `1` (pass) or `0` (fail) there.

### Milestone task

Run the same gate for the milestone task; every steps/milestone_N must have its oracle pass and its NOP fail.

```bash
harbor run -a oracle -p <task-folder>   # every milestone_N must land reward 1.0
harbor run -a nop -p <task-folder>      # every milestone_N must land reward 0.0
```

Confirm the per-milestone reward for each milestone_N in the output - do not accept a single top-line number as proof all milestones passed. If you need to isolate one milestone, check `harbor run --help` for a step/milestone selector; do not guess a flag.

## Step 4 - if the gate does not hold, stop

The gate holds only when oracle is 1.0 and NOP is 0.0 (per milestone for milestone tasks). If either is wrong, the task is not reward-trustworthy:

- Oracle not 1.0: the sanctioned solution does not pass its own tests. Surface the exact failing command or test from the run output (the pytest failure line, the failing build/step). Do not resubmit.
- NOP not 0.0: the tests pass with no work done, so they are trivially satisfied. Surface which tests still passed under NOP.

Show the failing log excerpt, not just the number. Then stop with a clear verdict - do not paper over it or retry blindly.

## Step 5 - report

Show a compact verdict, most severe first, then a short fix list.

- One line per run: `ORACLE PASS - reward 1.0` / `NOP PASS - reward 0.0` (NOP "passing" the gate means it correctly failed the tests). Use FAIL with a one-line evidence excerpt when a run lands the wrong value, NA if a run could not execute.
- For milestone tasks, one line per milestone_N for oracle and for NOP.
- End with an overall verdict: PASS only if oracle is 1.0 and NOP is 0.0 everywhere; otherwise FAIL.
- If FAIL, list the prioritized fixes (most blocking first): the failing test/command to fix, then resubmit only after the gate is green again. Remember to bump the `# platform-revision:` comment in environment/Dockerfile on any resubmit so the platform does not serve a cached build.
