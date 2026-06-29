# Terminus task lessons learned

Practical notes from revising three tasks on the Snorkel Terminus / Harbor
platform:

- `reproduce-java-tls-waiver-findings` (milestone task, Java)
- `repair-cpp-setup-auditor` (regular task, C++)
- `harden-php-api-defaults` (regular task, PHP)

This is the "things that actually bit us" list. Read it before starting a new
task so we do not repeat the same mistakes. It complements the general format
rules in `.cursor/rules/terminus.mdc` and `.cursor/rules/final-check.mdc`; this
file focuses on the concrete failures and the fix for each.

Each item is written as: **Symptom -> Root cause -> Fix -> How to avoid it.**

---

## 0. The three cliffs (read the UI, not "AutoEval Failure")

Expert platform note — treat this as the default triage order after every eval.

### 0.1 "AutoEval execution failed" is usually noise

- **Symptom:** `revision_notes` says `AutoEval execution failed` / build FAILED.
- **Root cause:** Default wrapper when the submission did not reach a human
  reviewer. The **real reason** is in the Web UI summary (difficulty, solvability,
  instruction sufficiency, per-test breakdown) or in `stb submissions feedback`.
- **Fix:** Ignore the wrapper line; triage using section 0.2 below.
- **How to avoid it:** Do not ask Terminus Bot to explain "AutoEval Failure" — it
  chases the boilerplate and misses the LLMaJ summary.

### 0.2 Oracle solution failed (cliff #1)

- **Symptom:** Reference oracle not 100% on platform; difficulty-check build FAILED.
- **Root cause:** Local oracle passed but platform env differs (Docker, deps, apt
  mirrors, image cache).
- **Fix:** Download the difficulty-check artifact from the summary window; read the
  job log for the failing command/test. Fix, `harbor run -a oracle` locally, bump
  ZIP (`# platform-revision: …` in `environment/Dockerfile`), resubmit.
- **How to avoid it:** Oracle green before every upload; never skip re-verify after
  "small" edits.

### 0.3 Difficulty TRIVIAL / EASY (cliff #2)

- **Symptom:** `Difficulty: ❌ EASY` or `TRIVIAL — Requires at least MEDIUM`.
- **Root cause:** Worst-model pass rate **> 60%** on frontier agents. If
  `languages` includes `python`, need **HARD** (best or worst ≤ **20%**).
- **Fix:** Harden with interacting logic/state — not relabeling `task.toml`, not
  edge-case spam. Re-run agent eval after hardening.
- **How to avoid it:** Measure on platform; do not guess difficulty from local runs.

### 0.4 Solvability — tests not passed by any agent (cliff #3)

- **Symptom:** `Status: ❌ Unsolvable` / some tests **0/10**.
- **Root cause (killer test):** Spec gap or broken test — one test never passes.
  Check per-test breakdown; common pattern is instruction sufficiency FAIL (requirement
  tested but not stated in `instruction.md`).
- **Root cause (verifier timeout):** Tests are passable but verifier times out on
  **5+ of 10** attempts (need **≥ 6/10** within budget). Agent cap ~30 min;
  verifier budget is separate.
- **Fix (killer):** Name the requirement in `instruction.md` or relax the test.
- **Fix (timeout):** Trim image bloat, costly milestones, installs in `test.sh`,
  cold dependency chains in the agent path.
- **How to avoid it:** Everything tested is stated or clearly implied; keep env lean.

---

## 1. Submission and review workflow (the most expensive mistakes)

### 1.1 We accidentally sent everything to a human reviewer

- **Symptom:** All three tasks jumped to `REVIEW_PENDING` when we only wanted
  AutoEval / static checks.
- **Root cause:** `stb submissions update` (and the submit flow) defaults to
  **send-to-reviewer**. We did not pass the opt-out flag.
- **Fix:** Always pass `--no-send-to-reviewer` on every `update`/submit unless
  the user explicitly says "send it to the reviewer now".
- **How to avoid it:** Treat "send to reviewer" as a separate, deliberate, final
  step. Default to checks-only.

### 1.2 There is no self-service recall from `REVIEW_PENDING`

- **Symptom:** Once in `REVIEW_PENDING`, we could not pull the tasks back to fix
  them.
- **Root cause:** The CLI/UI has no "recall" action. Only an admin can move a
  submission back to `NEEDS_REVISION`.
- **Fix:** Ask an admin (via Slack) to return the task(s) to `NEEDS_REVISION`.
- **How to avoid it:** See 1.1. Do not send to reviewer until checks pass and the
  user confirms.

### 1.3 Submissions are only editable in `NEEDS_REVISION`

- **Symptom:** Updates and rubric edits were rejected; we saw "Duplicate
  submission detected" or `403 Forbidden` on ZIP upload.
- **Root cause:** `REVIEW_PENDING` and `EVALUATION_PENDING` are locked states. A
  `create_submission` call flips the task to `EVALUATION_PENDING` immediately, so
  a *follow-up* ZIP upload or rubric call then fails.
- **Fix:** Do all edits (content **and** rubric **and** explanations) while the
  task is in `NEEDS_REVISION`, in one submission action.
- **How to avoid it:** Check state first. Batch everything into one pass.

### 1.3a Do not push platform fields before the ZIP on a revision

- **Symptom:** Explanations and rubrics saved, but instruction fixes stayed
  local; `stb submissions update` failed with "must be NEEDS_REVISION"; direct
  S3 upload returned `403 Forbidden`.
- **Root cause:** We called `create_submission` via API for explanations/rubrics
  only. That locked the assignment in `EVALUATION_PENDING` before the revised ZIP
  uploaded. The platform will not accept a ZIP upload until an admin returns the
  task to `NEEDS_REVISION`.
- **Fix:** Wait for `NEEDS_REVISION`, then upload ZIP and platform fields
  together in one `create_submission` (single payload with `upload_a_zip_file`
  plus explanation/rubric fields). Draft text locally first; do not trigger
  evaluation until the ZIP is in that same payload.
- **How to avoid it:** Revision order: (1) all local edits + oracle green, (2)
  draft `.submission-explanations.txt` and rubric text, (3) one combined update
  that uploads the ZIP **and** sets `difficulty_explanation`,
  `solution_explanation`, `verification_explanation`, `test_rubrics`, and
  `checkbox_evaluate_rubrics`. Never API-push explanations/rubrics alone first.

### 1.4 Rubric is a platform field, not a file, and an empty one fails CI

- **Symptom:** CI failed with "No rubric found" on the non-milestone tasks.
  Reviewer sent back the Java TLS milestone task for a missing rubric even after
  AutoEval passed.
- **Root cause:** The rubric lives in the submission payload (`test_rubrics`),
  not in the ZIP. There is no `rubric.txt`.
- **Fix:** Populate the rubric in the submission form ("Generate your Rubric(s)"
  checkbox), or inject it programmatically into `test_rubrics` via the `stb`
  Python API while the task is in `NEEDS_REVISION` — in the same submission
  action as the ZIP upload (see 1.3a).
- **Rubric shape:**
  - **Non-milestone:** flat list with **at least 3 negative criteria**.
  - **Milestone (`number_of_milestones` > 0):** one `# Rubric N` block per
    milestone; each block needs at least one negative line and a positive-point
    total between 10 and 40. Set `checkbox_evaluate_rubrics = true`.
- **How to avoid it:** Add "rubric populated (correct shape for task type)" to the
  pre-submit checklist. Never assume the zip carries the rubric.

### 1.5 Always run the oracle before every (re)submission

- **Symptom:** A resubmission failed tests that a quick oracle run would have
  caught.
- **Root cause:** Resubmitting on the assumption that "a small edit can't break
  it".
- **Fix:** `harbor run -a oracle -p <task-folder>` must pass green *every* time
  before we update the submission.
- **How to avoid it:** No edit is too small to re-verify. Oracle first, submit
  second.

### 1.6 Explanation fields are required — blank ones get sent back

- **Symptom:** AutoEval passed, but a human reviewer returned the Java TLS task
  because Difficulty, Solution, and Verification were all blank.
- **Root cause:** The three fields live in the submission payload, not the ZIP.
  We submitted content without filling them (or filled them in a separate API
  call that did not survive / was done out of order).
- **Fix:** Draft all three before every submit/resubmit. Keep a local copy in
  `.submission-explanations.txt`. Include them in the same `create_submission`
  payload as the ZIP upload.
- **What to write** (~1 paragraph / 4-6 sentences each, your own words, engineer
  tone — not polished AI prose):
  - **Difficulty** — why the task is hard for an agent (not just humans).
  - **Solution** — high-level pipeline approach and key insight.
  - **Verification** — how the tests (per-milestone or final) confirm correctness.
- **How to avoid it:** Treat blank explanation fields as a blocker on the
  pre-submit checklist. Milestone tasks need them too.

---

## 2. `task.toml` pitfalls

### 2.1 `difficulty` must be a real measured value

- **Symptom:** `difficulty = "unknown"` was rejected (Java).
- **Root cause:** Leftover skeleton default.
- **Fix:** Use `easy` / `medium` / `hard`, set from the measured accuracy over
  the frontier-model runs.
- **How to avoid it:** Never ship a skeleton placeholder. Grep the toml for
  `unknown` before zipping.

### 2.2 The difficulty gate is enforced, and it is language-dependent

- **Symptom:** C++ came back `TRIVIAL` (needs >= MEDIUM); Java came back `EASY`
  (needs >= MEDIUM); PHP came back `MEDIUM` but failed "requires HARD for python".
- **Root cause:** There is a minimum difficulty gate. Tasks measured below it are
  rejected. **Python-language tasks must be HARD.**
- **Fix:** If the measured difficulty is under the gate, genuinely harden the
  task (see section 6); do not just relabel the toml. For Python, either reach
  HARD or remove Python from `languages` if it is verifier-only (see 2.3).
- **How to avoid it:** Decide the target difficulty up front and design enough
  real, interacting complexity to hit it. (if need ask the use to confirm if you can test this against opus or gpt this project has ways to this this) but this should done maybe after we have done a couple of submissions and we can figure out the level of difficulty

### 2.3 `languages` lists only what the agent/oracle uses, not the verifier

- **Symptom:** PHP and Java tripped the "python => HARD" gate even though the
  agent never wrote Python.
- **Root cause:** We listed `python` in `languages`, but Python was only the
  pytest verifier. The gate keys off `languages`.
- **Fix:** Remove verifier-only languages. PHP became `["php", "bash", "sql"]`;
  Java became `["java", "bash", "sql"]`. The pytest verifier does not count.
- **How to avoid it:** `languages` = languages the **agent** writes or the
  **oracle** solution uses. The verifier is always Python and is implied.

### 2.4 `codebase_size` must match the actual file count

- **Symptom:** `codebase_size = "minimal"` was wrong for a ~22-file environment
  (Java).
- **Root cause:** Mislabeled size; `minimal` is for very small trees (~<20
  files), `small` for larger.
- **Fix:** Count the files actually shipped in `environment/` and set the band
  accordingly (Java -> `small`).
- **How to avoid it:** Set `codebase_size` after the environment is final, not
  from the skeleton.

---

## 3. Environment / Dockerfile

### 3.1 Use the platform's canonical base image digest - do not "upgrade" it

- **Symptom:** `manifest verification failed` in AutoEval after we pinned a
  newer public digest.
- **Root cause:** The platform only trusts its sanctioned/canonical base digest.
  A "newer" public digest for the same tag is not accepted.
- **Fix:** Pin the canonical image used across all our tasks:

```dockerfile
FROM public.ecr.aws/docker/library/python:3.13-slim-bookworm@sha256:01f42367a0a94ad4bc17111776fd66e3500c1d87c15bbd6055b7371d39c124fb
```

- **How to avoid it:** This Python base is sanctioned even for non-Python tasks
  (PHP, C++, Java) because it runs the pytest verifier; install language runtimes
  (php, g++/cmake, jdk) on top of it. Do not bump the digest to chase a newer
  build.

### 3.2 `codebase_applicability` fails build-from-scratch tasks with no source

- **Symptom:** Task stuck in `NEEDS_REVISION` even though difficulty (MEDIUM),
  instruction sufficiency, tests, `tb_check`, `test_quality_judge`, and
  `claude_code_reviewer` all pass. The only red child is `codebase_applicability`,
  failing on *every* eval with `is_real_code_base=False` -> `BUILD FAILED`.
- **Root cause:** The checker scans `environment/`; if it sees only configs,
  schemas, JARs, SQL, fixtures, and a report (no `.py`/`.java`/`.js`), it decides
  the task is "not a real software project" and exits non-zero. Build-from-scratch
  tasks ship zero source by design, so they trip this deterministically.
- **Fix:** Ship a minimal **non-solution scaffold** in `environment/` (e.g.
  `environment/pipeline/`: a `Main` dispatcher, stage-class stubs that throw
  `UnsupportedOperationException`, a `build.sh`, a short README) and `COPY` it into
  the image. Point `instruction.md` at it ("extend the provided scaffold"). No
  answer logic in the scaffold. Verify it compiles in the task image and that the
  oracle (which `rm -rf /app/pipeline` then copies its own tree) still passes.
- **Bonus:** it removes the "agent hallucinated a pipeline / context overflow on
  the from-scratch setup" robustness failures AutoEval otherwise attributes to the
  task.

---

## 4. `tests/test.sh`

### 4.1 The reward block has a strict canonical shape

- **Symptom:** Static check `check_test_sh` failed.
- **Root cause:** Two issues we hit: (a) a trailing `exit "$RC"` after the reward
  block, and (b) extra logic between `rc=$?` and the `if`.
- **Fix:** End the file with exactly this, with `rc=$?` *immediately* before the
  `if`, and nothing after `fi`:

```bash
PYTHONPATH=/tests python3 -m pytest --ctrf /logs/verifier/ctrf.json -p no:cacheprovider -rA /tests/test_outputs.py -q
rc=$?
if [ "$rc" -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi
```

- **How to avoid it:** Early failure paths (build failed, service didn't start)
  may `echo 0 > reward.txt; exit 0` *before* pytest, but the final pytest reward
  block is the literal end of the file. Always write `reward.txt` on every exit
  path. Never install or download inside `test.sh`.

---

## 5. Verifier robustness (do not encode hidden requirements)

### 5.1 Do not hardcode an undocumented path or convention the agent can't infer

- **Symptom:** All 10 Java agent runs failed even though the logic was correct.
- **Root cause:** The verifier required `Main.class` at `/app/pipeline/classes`,
  but agents reasonably compiled to `/app/classes`. That exact output path was
  never stated in `instruction.md`, so the test enforced a hidden convention.
- **Fix:** Make the verifier flexible - search the common compiled-output
  directories under `/app` (e.g. `/app/classes`, `/app/pipeline/classes`) instead
  of one hardcoded path. Alternatively, state the exact required path in
  `instruction.md`.
- **How to avoid it:** A test may only enforce what the instruction states or
  clearly implies. If correctness depends on a specific path/command/filename,
  either accept reasonable variants or document it explicitly.

### 5.2 Milestone tests are tightly coupled - keep early checks robust

- **Symptom:** A brittle Milestone 1 check cascaded into later milestone failures.
- **Root cause:** Milestones share cumulative state in the same container, and
  later graders depend on earlier artifacts.
- **Fix:** Keep each milestone verifier tolerant of legitimate placement of build
  outputs and intermediate files; assert on behavior, not on incidental layout.
- **How to avoid it:** Test the milestone's *outcome*, not where the agent put a
  scratch file.

---

## 6. Instruction sufficiency (LLM-as-judge)

### 6.1 Every tested control must be discoverable from the instruction

- **Symptom:** Instruction Sufficiency FAIL on PHP - agents missed the
  `AC-TOKEN-STORE` control (token hashing + owner-only file permissions).
- **Root cause:** We named some controls but not others, which implied the list
  was complete and left a "silent gap" for a control the tests still checked.
- **Fix:** Explicitly name every control area the tests verify (e.g.
  `AC-TOKEN-STORE`, CORS policy, bootstrap ordering, audit logging, debug-
  disclosure), without giving the solution.
- **How to avoid it:** Two valid styles - (a) enumerate all tested control areas,
  or (b) keep it uniformly "reconcile the entire standard at <path>". Never
  half-enumerate. Every requirement tested must be stated or clearly implied; and
  everything stated must have a matching test.

### 6.2 Write instructions for the agent, not the verifier

- **Symptom:** Reviewer asked us to reword all three milestone instructions.
  AutoEval did not catch it.
- **Root cause:** Instructions said things like "the verifier may rerun
  `com.mariner.audit.Main decode` from the compiled classes". The agent never
  sees the verifier — that phrasing leaks grader implementation into the prompt.
- **Fix:** Rephrase in agent-facing terms: each stage must be reproducible from
  compiled classes (name the `Main` subcommands), and JSON outputs must not be
  hand-written. Keep the intent; drop "verifier reruns / checks" wording.
- **How to avoid it:** On every milestone `instruction.md`, grep for
  "verifier" before zipping. If it appears, rewrite for the agent.

---

## 7. Making a task harder the right way

- **Symptom:** Tasks measured too easy; the temptation is to pile on edge cases.
- **Root cause:** Edge-case spam does not raise *real* difficulty and is a
  reviewer red flag.
- **Fix:** Add genuinely interacting policy/logic. Examples that worked:
  - **C++:** sudo *sticky command-tag* semantics (`NOPASSWD:` tags persist across
    entries until overridden) and *active* authorized-key-line parsing (markers
    that disable a key). These force real state tracking.
  - **Java:** a waiver lifecycle where an old waiver is granted, rescinded, then
    *replaced* by a new waiver for the same service - forcing the agent to pair
    rescissions by `waiver_id` and reason over a timeline, not just by service.
- **How to avoid the wrong path:** Difficulty should come from reasoning across
  files/state/time, not from a long list of trivial corner cases.

---

## 8. Housekeeping

- Keep ground truth and expected outputs only in `tests/`, never in
  `environment/`. Do not copy `solution/` or `tests/` into the image.
- Clean junk before zipping: `__pycache__/`, `.pytest_cache/`, `.ruff_cache/`,
  `.DS_Store`, stray `jobs/` or scratch dirs.
- Keep a `.dockerignore` (we had to add `**/node_modules/`) so the build context
  stays small.

---

## 9. Fast pre-submission checklist (the deltas that bit us)

1. Oracle passes locally (`harbor run -a oracle -p <task>`), green, this run.
2. `task.toml`: `difficulty` is real (not `unknown`); meets the gate; Python is
   HARD if listed.
3. `languages` excludes verifier-only Python; lists only agent/oracle languages.
4. `codebase_size` matches the actual environment file count.
5. Base image is the canonical digest (`sha256:01f42367...`), not a bumped one.
6. `test.sh` ends with the canonical `rc=$?` reward block; reward written on all
   paths; no trailing `exit`; no installs/downloads.
7. Verifier does not depend on an undocumented path/convention.
8. `instruction.md` names every tested control area; every requirement has a
   test, and every test maps to the instruction.
9. No "verifier" wording in milestone instructions — agent-facing reproducibility
   language only.
10. Three explanation fields drafted and non-blank (difficulty / solution /
    verification); local copy in `.submission-explanations.txt`.
11. Rubric populated in the platform with the correct shape:
    - non-milestone: flat list, >= 3 negative criteria;
    - milestone: one block per milestone, each with >= 1 negative line and
      10–40 positive points; `checkbox_evaluate_rubrics = true`.
12. Assignment is `NEEDS_REVISION` before a revision; ZIP upload and platform
    fields go in one `create_submission` (never API-push explanations/rubrics
    before the ZIP — see 1.3a).
13. Submit with `--no-send-to-reviewer`. Only send to reviewer after checks pass
    and the user confirms.

---

## 10. Per-task quick reference

- **`harden-php-api-defaults` (PHP):** dropped verifier-only `python` from
  `languages` (-> `php, bash, sql`), set `difficulty = "medium"`, and named the
  tested controls (incl. `AC-TOKEN-STORE`) in the instruction.
- **`repair-cpp-setup-auditor` (C++):** raised from `TRIVIAL` to `medium` by
  adding sudo sticky command-tag semantics and active authorized-key parsing,
  with matching fixtures/tests/docs.
- **`reproduce-java-tls-waiver-findings` (Java, milestones):** fixed the
  `unknown` difficulty, corrected `codebase_size` to `small`, removed trailing
  `exit` from each milestone `test.sh`, made the verifier find compiled classes
  flexibly, and hardened Milestone 1 with a replacement-waiver lifecycle.
  **Second reviewer pass:** filled blank explanation fields, added three
  milestone rubric blocks (10–40 positive points, negative lines each),
  reworded milestone instructions to agent-facing reproducibility language (no
  "verifier reruns" phrasing). Lesson: upload ZIP and platform fields in one
  submission action — API-only payload update locked the assignment before the
  instruction ZIP landed.
