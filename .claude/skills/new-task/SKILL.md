---
name: New Terminus task
description: Scaffold a new sanctioned Terminus task folder (canonical base image, reward block, task.toml metadata, codebase scaffold) after checking the live category gate. Use this to start any brand-new non-milestone Terminus/Harbor task so it clears the gates that have bounced us - category_classifier, codebase_applicability, check_test_sh, and the difficulty bar.
argument-hint: [task-name]
---

# Scaffold a new Terminus task

Create one new non-milestone task folder at the repo root, wired so the known AutoEval gates pass on the first submission. Do not write any files until Step 0 and Step 1 both clear.

## Step 0 - resolve the new task name and category (do this first, every run)

You are creating a brand-new task folder at the repo root /Users/fabrice-mac-mini/Documents/snorkel-ai. Nothing exists yet.

1. If $ARGUMENTS is non-empty, treat it as the kebab-case task name. If it is empty, ask the user with AskUserQuestion for two things: the task name and the intended category.
2. Normalize the name to kebab-case. Avoid a `repair-*` / `fix-*` / `debug-*` prefix - it reads as software-engineering to the classifier (see Step 1).
3. Confirm /Users/fabrice-mac-mini/Documents/snorkel-ai/<name> does NOT already exist. If it does, stop and tell the user the exact path - never overwrite an existing folder.
4. Hold the intended category; you validate it against the live gate in Step 1 before creating anything.

Do not proceed past Step 0 until the name is kebab-case, confirmed free, and you have an intended category.

## Step 1 - check the live category gate (before writing files)

The category list is a live platform gate that moves. The snapshot in `.cursor/rules/terminus-submission-hardening.mdc` is only a snapshot:

- Blocked in that snapshot: `data-processing`, `debugging`, `software-engineering`, and all milestone tasks.
- Open in that snapshot: `system-administration`, `build-and-dependency-management`, `games`, `machine-learning`, `security`, `scientific-computing`.

Do this:

1. Tell the user to re-check the portal Task Category Status page - the snapshot may be stale and a category could have flipped either way.
2. Warn that `category_classifier` reads the task CONTENT, not the declared `category`. A repair / bug-fix / "the service is broken, fix it" framing reads as software-engineering (blocked) even when tagged `security`. It has fired at 0.95 confidence.
3. If the intended category looks blocked, or the framing would classify into a blocked category, stop and confirm the direction with the user before scaffolding. Reorienting the task (folder name, instruction framing, spec focus) is the fix, not a metadata relabel.

Only start writing files once the category is clear.

## Step 2 - scaffold the non-milestone layout

Create this tree under /Users/fabrice-mac-mini/Documents/snorkel-ai/<name>/. `number_of_milestones = 0`, no `steps/`, root-level instruction and tests.

```
<name>/
  instruction.md
  task.toml
  environment/
    Dockerfile
    .dockerignore          # for any non-trivial env
    requirements.txt        # hash-pinned pip deps
    <project>/              # non-solution codebase scaffold (Step 6)
  solution/
    solve.sh
  tests/
    test.sh
    test_outputs.py
```

## Step 3 - environment/Dockerfile

Start from the canonical digest-pinned base (sanctioned even for non-Python tasks - install the real runtime on top via apt) and set the revision comment to today:

```dockerfile
FROM public.ecr.aws/docker/library/python:3.13-slim-bookworm@sha256:01f42367a0a94ad4bc17111776fd66e3500c1d87c15bbd6055b7371d39c124fb
# platform-revision: 2026-07-21-r1
```

Rules:

- One apt block: `apt-get update && apt-get install -y --no-install-recommends ... && rm -rf /var/lib/apt/lists/*`. Install `tmux` and `asciinema` - the agent runtime needs both or every run fails. Add the task's real runtime here (g++, cmake, default-jdk, nodejs/npm from apt, etc.). No `apt-get upgrade`.
- Pin app deps: pip via a hash-locked `requirements.txt` (`pip install --no-cache-dir --require-hashes --no-deps -r`), downloaded binaries by version + sha256. Do NOT pipe remote setup scripts into the shell (`curl ... | bash`).
- `COPY <project>/ /app/<project>/` the scaffold from Step 6. Do NOT copy `solution/` or `tests/` into the image.
- No `--privileged`, no `/var/run/docker.sock` mount, no `SYS_ADMIN` / `NET_ADMIN` / `SYS_MODULE`. No reserved volume mounts (`/logs/...`, `/tests/`, `/solution/`).
- Keep `environment/` at or below 100 MiB total, 50 MiB per file. Store source as real files, not heredocs.

Ship a `.dockerignore` for any non-trivial env: `.git`, `**/__pycache__/`, `**/*.pyc`, `**/build/`, `**/node_modules/`, `.env`, `.DS_Store`, `solution/`, `tests/`.

## Step 4 - task.toml

Fill every field with a real value - no `"unknown"` placeholders. Template:

```toml
version = "2.0"

[metadata]
author_name = "Fabrice Nduwayo"
author_email = "fabrice.nduwayo12@gmail.com"
difficulty = "medium"
category = "<open category from Step 1>"
subcategories = []
number_of_milestones = 0
codebase_size = "minimal"
languages = ["<agent/oracle langs only>"]
tags = ["tag1", "tag2", "tag3"]
expert_time_estimate_min = 120
junior_time_estimate_min = 240

[verifier]
timeout_sec = 450.0

[agent]
timeout_sec = 1200.0

[environment]
build_timeout_sec = 900.0
cpus = 2
memory_mb = 4096
storage_mb = 10240
allow_internet = false
```

Field rules:

- `difficulty`: a real target, `medium` minimum. If `languages` includes `python`, the bar is `hard` - set `hard`. This is the target you are aiming for; measured runs confirm it later. Never `"unknown"`.
- `languages`: only what the agent writes or the oracle uses. The pytest verifier is always Python and does NOT count - listing verifier-only `python` falsely trips the python => HARD gate.
- `codebase_size`: from the actual `environment/` file count. Under ~20 files => `minimal`; more => `small`.
- `tags`: 3 to 6, matching the real task.
- `allow_internet = false` unless the task genuinely needs the network (an eval checks whether it is actually needed).
- The oracle must pass inside the declared timeouts.

## Step 5 - tests

`tests/test.sh`: drive the real program under test (rerun the CLI / compiled entrypoint / HTTP API from pytest), never a shadow reference only. End the file with the canonical reward block - `rc=$?` immediately before the `if`, nothing after `fi`:

```bash
PYTHONPATH=/tests python3 -m pytest --ctrf /logs/verifier/ctrf.json -p no:cacheprovider -rA /tests/test_outputs.py -q
rc=$?
if [ "$rc" -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi
```

- Write `/logs/verifier/reward.txt` on every exit path. An early `echo 0 > /logs/verifier/reward.txt; exit 0` is fine for a build/startup failure BEFORE pytest.
- No trailing `exit "$rc"` after `fi` (fails `check_test_sh`). No logic between `rc=$?` and the `if`.
- No installs or downloads in `test.sh` - all test deps live in the Dockerfile.

`tests/test_outputs.py`: start with at least one test that has an informative docstring, asserts on behavior / final correctness (not source-text patterns), and passes ruff lint. Leave the real assertions to fill in once the oracle exists - do not test anything not stated or clearly implied in `instruction.md`.

## Step 6 - environment/ codebase scaffold (build-from-scratch tasks)

`codebase_applicability` fails the build when `environment/` has no real source (only config, schemas, jars, fixtures). If the agent writes the whole program from scratch, ship a minimal NON-SOLUTION scaffold so the env reads as a real codebase:

- A `Main` dispatcher, stubbed stage classes that throw (`UnsupportedOperationException` for Java, `NotImplementedError` for Python, a thrown error for C++), and a `build.sh`.
- Keep it compilable - verify it builds in the task image. Point `instruction.md` at it ("extend the provided scaffold at /app/<project>").
- No answer logic: no real stage bodies, thresholds, or expected values in the scaffold - it ships in the image and would leak the solution or drop difficulty.

For a task that ships real (broken) source the agent edits, that source is the codebase and satisfies the gate on its own - just keep the fix and expected values out of `environment/` entirely.

## Step 7 - instruction.md

Write it short and in Fabrice's voice. If you are unsure of the task's specifics, write the frame and leave the details for Fabrice to finish rather than inventing them.

- One sentence to three short paragraphs. Give the goal (what) and the requirements, not step-by-step how. No solution hints.
- Absolute paths for every path. No canary string. No task name as a first-line comment. No emojis, no heavy markdown, no long bullet checklists.
- Name every control/requirement the tests will check, without giving the solution; or keep it uniformly "reconcile the whole spec at <path>". Keep requirements and tests in lockstep.
- Write it agent-facing. Never say "the verifier reruns ..." or describe verifier behavior.
- Read at least three existing `instruction.md` files in this repo first (e.g. repair-cpp-setup-auditor, reproduce-java-aes-gcm-findings) and match that voice.

## Step 8 - report and next steps

Show the created tree. Then give a short, prioritized next-steps list, most important first:

1. Write the oracle in `solution/solve.sh` (deterministic, human-written, no hardcoded answer, no network) so it satisfies every requirement in `instruction.md`.
2. Fill the real assertions in `tests/test_outputs.py` against the oracle output.
3. Run `/verify-local` (or by hand: `export ANTHROPIC_API_KEY=dummy`, then `harbor run -a oracle -p <name>` expecting reward 1.0 and `harbor run -a nop -p <name>` expecting reward 0.0). Never use a personal API key.
4. Rubrics go in the platform `test_rubrics` field at submit time, not in the ZIP - a flat list, at least 3 negative criteria. Lint them with `python3 /Users/fabrice-mac-mini/Documents/snorkel-ai/scripts/check-rubrics.py <path>`.

Give a compact verdict for the scaffold itself, most severe first, then the fix list:

- PASS/FAIL/NA per gate you can check now (category clear, base image pinned, reward block exact, task.toml complete, scaffold compiles), one line of evidence each.
- Then the prioritized list of what Fabrice must finish before the task is submittable.
