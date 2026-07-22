---
name: task-review
description: Grade one Terminus task folder against the full Terminal Bench Edition 2 reviewer checklist before submission - be the reviewer before the reviewer so nothing bounces on a checklist item. Walks Instruction prompt, Environment, Oracle solution, Verifiers, Rubrics, Task structure, Task metadata, and Milestone rules, folds in the difficulty and category_classifier gates, and prints a severity-grouped PASS/FAIL/NA verdict with a prioritized fix list. Read-only - reports findings and stops. Use before any stb submit/resubmit, or whenever asked to review or grade a task against the reviewer checklist.
argument-hint: [task-folder]
---

# Task review - grade against the TB2 reviewer checklist

Grade the resolved task folder against every section of the reviewer checklist
(`.cursor/rules/terminus-reviewer-checklist.mdc`), plus the two live gates. Judge each
criterion against the task's real files, never from memory. Report and stop; do not edit.

## Step 0 - resolve the target task folder (do this first, every run)

The target is one task folder at the repo root /Users/fabrice-mac-mini/Documents/snorkel-ai (kebab-case, contains task.toml). Milestone tasks contain steps/milestone_N/ subfolders and no root instruction.md.

1. If $ARGUMENTS is non-empty, treat it as the target folder name (or path). Use it.
2. If $ARGUMENTS is empty, list the candidate task folders - every directory at the repo root that contains a task.toml, EXCLUDING .review-scratch/, docs/, jobs/, scripts/, tools/, and .git/ - and ask the user which one with AskUserQuestion. If exactly one candidate exists you may confirm it instead of asking.
3. Confirm the chosen path exists and contains task.toml. If it does not, stop and tell the user exactly what you looked for. Never guess or run against the wrong folder.
4. Detect the task type: milestone if steps/milestone_N/ folders exist and there is no root instruction.md; otherwise non-milestone. Remember it - later steps branch on it.

Do not proceed past Step 0 until the target folder is resolved and confirmed.

## Step 1 - read the task's real files

Read before you grade. Do not judge any criterion from memory.

- Always: `task.toml`, `environment/Dockerfile` (or `environment/docker-compose.yaml`),
  `environment/.dockerignore`, and any `environment/` docs, fixtures, and scaffold.
- Non-milestone: `instruction.md`, `solution/solve.sh` (+ any source it copies),
  `tests/test.sh`, `tests/test_outputs.py`, `tests/helpers.py` if present.
- Milestone: each `steps/milestone_N/instruction.md`, `steps/milestone_N/solution/solve.sh`
  + `solveN.sh`, `steps/milestone_N/tests/test.sh` + `test_mN.py`. Confirm there is no
  root-level `instruction.md`, `tests/`, `solution/`, or `milestone_x.md`.

## Step 2 - walk every checklist section

Judge each criterion against the files you read. Mark PASS / FAIL / NA and hold one line of
file-cited evidence for each. Do not skip a section.

### Instruction prompt (grade instruction.md, or each steps/*/instruction.md)
- [High] Concise: one sentence to three paragraphs, human-sounding, no emojis, little markdown,
  no long multi-requirement checklists.
- [High] Well specified: goal is clear; not hard mainly from a pile of edge cases.
- [High] Interesting/useful to some group of developers.
- [High] No solution hints: requirements yes, stepwise instructions or hints no.
- [High] Environment carries no hidden instructions/hints (no file, comment, README, config,
  script, or TODO that walks the solution) - cross-check the `environment/` files you read.
- [High] Spec/doc files realistic: define what, not a step-by-step guide; do not move the
  prompt's logic out of instruction.md to dodge the length limit; read like real eng docs.
- [High] Unique vs TB2, TB3, Terminus Edition 1 (different initial state/instructions or output).
- [High] Absolute paths for every path referenced.
- [Medium] No canary string in instruction.md.
- [Medium] No task name as a leftover first-line comment.

### Environment (grade environment/Dockerfile, compose, .dockerignore, deps)
- [High] No web content at build time other than package deps; no `curl ... | bash` remote
  setup scripts; everything else stored locally.
- [High] `allow_internet` matches actual need: false unless current/external info or an
  unbundleable resource is genuinely required.
- [High] Dependencies pinned (packages; apt excluded). Downloaded binaries pinned by version + sha256.
- [High] No context from outside `environment/` (no compose `context: ../`).
- [High] No solution or ground truth in the environment (oracle lives in solution/, verify data in tests/).
- [High] No dangerous Docker ops: no `--privileged`, no SYS_ADMIN/NET_ADMIN/SYS_MODULE, no docker.sock mount.
- [High] No conflicting volume mounts (reserved: /logs/artifacts/, /logs/verifier/, /tests/, /solution/). Prefer none.
- [High] No AI-framework scaffolding filenames (CLAUDE.md, skills.md, and similar) in the env.
- [High] Every base image digest-pinned with `@sha256:` (every FROM, any pulled compose `image:`).
- [High] Base image canonical or justified. The pinned
  `public.ecr.aws/docker/library/python:3.13-slim-bookworm@sha256:01f42367a0a94ad4bc17111776fd66e3500c1d87c15bbd6055b7371d39c124fb`
  is sanctioned even for non-Python tasks (install the real runtime via apt on top).
  Non-canonical needs a credible written justification; reject one a canonical image already covers.
- [High] Build context small: `environment/` <= 100 MiB total, no single file > 50 MiB (measure it).
- [High] tmux and asciinema installed (agent runtime needs both or all runs fail).
- [Medium] Apt clean and reproducible: one `apt-get update && install --no-install-recommends ... && rm -rf /var/lib/apt/lists/*` per stage, no `apt-get upgrade`.
- [Medium] `.dockerignore` present on any non-trivial env (.git, __pycache__/, *.pyc, node_modules/, .env, solution/, tests/).
- [Low] Avoid heredocs in the Dockerfile.
- [High] codebase_applicability: for build-from-scratch tasks the env ships a minimal non-solution
  scaffold (real .py/.java/.js), not only config/schemas/jars/fixtures. Env with no source code
  fails `is_real_code_base=False` and holds the task in NEEDS_REVISION alone.

### Oracle solution (grade solution/solve.sh and what it builds)
- [High] Passes consistently, never flaky (no randomization, no latency-dependent behavior).
- [High] Internet use matches allow_internet: with false, downloads nothing; all deps preinstalled.
- [High] Reflects instruction.md: solves every stated requirement, real implementation not a hardcoded answer.

### Verifiers (grade tests/test.sh and test_outputs.py / test_mN.py)
- [High] Cannot exit before a reward is assigned; test.sh writes reward.txt on success and
  failure. The `if ... fi` reward block is the canonical end - do NOT flag a missing trailing
  `exit`, and adding `exit $?` after `fi` fails check_test_sh. Confirm `rc=$?` sits immediately
  before the `if` with nothing between, and nothing follows `fi`. Canonical block:
  `PYTHONPATH=/tests python3 -m pytest --ctrf /logs/verifier/ctrf.json -p no:cacheprovider -rA /tests/test_outputs.py -q`
  then `rc=$?` then the if/else writing 1 or 0 to /logs/verifier/reward.txt.
- [High] Identical logic for oracle and agent runs (no branch grading them differently).
- [High] Verifier internet use matches allow_internet: deps baked in the Dockerfile, none downloaded at runtime; no installs in test.sh.
- [High] Binary rewards only (0 or 1); no partial credit.
- [High] Aligned with the instruction: never test a requirement not stated or clearly implied.
- [High] Check correctness, not just format: exercises the real program under test (rerun the
  CLI / compiled entrypoint / HTTP API / DB), not only a reference in helpers.py; not mere file-existence or shape.
- Each test has an informative docstring; tests pass ruff lint; no order-dependent or hardcoded-random assertions.

### Rubrics (reviewer-graded; rubrics live in the platform, not the ZIP)
Rubric text is entered in the platform `test_rubrics` field. If a local draft exists
(`.review-scratch/<task>-rubrics.txt` or similar), run the linter and report its output; do not
reimplement its mechanical checks: `python3 /Users/fabrice-mac-mini/Documents/snorkel-ai/scripts/check-rubrics.py <path>`.
If no draft exists, mark these NA and note the rubric must be set in the UI before send-to-reviewer.
- [High] No references to /tests/ logic; no references to task.toml / instruction.md metadata.
- [High] At least 3 negative criteria.
- [High] Scores are one of +/- 1, 2, 3, 5; positives carry an explicit `+`; never 4.
- [High] One criterion per line, starts with `Agent`, ends `, <score>`. Milestone uses `# Rubric N`
  headers per milestone; non-milestone uses a flat list.
- [High] Criteria detailed and precise, not vague.
- [Medium] Each milestone rubric block has >= 1 negative criterion.
- [Medium] Scores map to importance (critical -> +/-5).
- [Medium] Phrased positively with a negative reward, not negated sentences.
- [Medium] No mention of oracle/NOP runs.
- [Low] 10-40 positive points per milestone (per block for milestone tasks).

### Task structure
- [High] Required files present for the detected type.
  - Non-milestone: environment/ (with Dockerfile), solution/solve.sh, tests/test.sh, instruction.md, task.toml.
  - Milestone: environment/, task.toml with one [[steps]] block per milestone, and
    steps/milestone_N/ each with instruction.md, tests/test.sh + tests/test_mN.py,
    solution/solve.sh + solution/solveN.sh; and NO root instruction.md, tests/, solution/, or milestone_x.md.
- [Low] No unnecessary files in the task folder (leftover jobs/ logs, stray data/ that belongs in environment/).

### Task metadata (grade task.toml)
- [High] All required fields. version = "2.0"; [metadata] with author_name, author_email,
  category, subcategories, difficulty, codebase_size, number_of_milestones, languages, tags,
  expert_time_estimate_min, junior_time_estimate_min. Non-milestone only: [verifier] timeout_sec,
  [agent] timeout_sec. Always: [environment] with build_timeout_sec, cpus, memory_mb, storage_mb,
  allow_internet. Milestone only: [environment] workdir plus one [[steps]] block per milestone with
  [steps.agent] timeout_sec and [steps.verifier] timeout_sec.
- [High] Compose tasks flagged: custom_docker_compose = true for any compose task, plus
  is_multi_container = true when it defines a multi-container system.
- [Medium] tags, languages, category, subcategories actually match the task. `languages` lists only
  what the agent writes or the oracle uses - verifier-only python does not count (it also trips the python->HARD gate).
- [Low] Do not reject for omitted optional fields (gpus, gpu_types, docker_flags); gpu_types only matters when gpus > 0.

### Milestone rules (only if milestone task; else mark this section NA)
- [High] At least 2 milestones.
- [High] steps/ layout with per-milestone instruction.md, tests/, solution/.
- [High] One [[steps]] block per milestone, name = "milestone_N" matching the directory, count == number_of_milestones, each with agent and verifier timeout_sec.
- [High] solveN.sh per milestone scoped to that milestone only, plus a solve.sh wrapper that invokes it.
- [High] test_mN.py per milestone with a TestMilestoneN class, plus a test.sh runner writing reward.txt; solve1.sh pairs with test_m1.py, etc.; tests score only that milestone.
- [Medium] Per-milestone instruction.md covers only that milestone (milestone 1 also carries overall context).

## Step 3 - fold in the two live gates (both block; severity High)

- Difficulty gate. Read `difficulty` and `languages` from task.toml.
  - Minimum accepted is MEDIUM; TRIVIAL/EASY is bounced.
  - If `languages` includes `python`, the bar is HARD (best or worst model pass rate <= 20% under the OR rule).
  - If worst-model pass rate > 60%, the task bounces as EASY/TRIVIAL.
  - You usually cannot measure pass rate locally: if the declared difficulty is below the required
    bar (e.g. python present but difficulty != hard, or difficulty easy/trivial), FAIL it. Otherwise
    flag as a High risk that the declared value must be backed by measured platform runs, and warn
    that relabeling task.toml does not raise real difficulty.
- category_classifier gate. It reads task CONTENT, not the declared `category`, and blocks a task
  whose predicted category is currently blocked. Blocked (snapshot, re-check the portal Task Category
  Status page): data-processing, debugging, software-engineering. A `repair-*` / bug-fix task reads
  as software-engineering even when tagged security. If the folder name is `repair-*` or the
  instruction is framed as fixing a bug, flag High: reorient the task (folder name, instruction
  framing, policy/spec focus), not a metadata relabel. Confirm the declared category is in the open
  set (system-administration, build-and-dependency-management, games, machine-learning, security, scientific-computing).

## Step 4 - emit the verdict

Print criteria grouped by severity, most severe first: all High, then Medium, then Low. Each line:

`[PASS|FAIL|NA] <severity> <criterion> - <one line of evidence citing the file>`

Keep it compact. Include the two Step 3 gates in the High group. Then state the overall verdict
plainly using the checklist summary rule:

- Any High FAIL -> DO NOT SUBMIT.
- Several Medium FAILs -> DO NOT SUBMIT.
- A single Medium FAIL can still pass but must be noted in acceptance comments.
- Low-only failures do not block; fold them into revision notes if the task is going back anyway.

End with a prioritized fix list, High fixes first, each naming the file and the change needed.

## Read-only

This skill reports and stops. Do not edit any task file. After the verdict, offer to fix the
findings, but make no changes unless the user asks.
