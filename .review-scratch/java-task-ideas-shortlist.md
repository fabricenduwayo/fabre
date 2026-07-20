# SHORTLIST

## 1. TOP 3, RANKED

### #1 — `rebuild-java-ledger-ingest-parity`

**Category:** `data-processing` · **Subcategories:** `db_interaction` · **Languages:** `java`, `bash`, `sql`

**Stack:** Java 17, plain `javac`, bundled Jackson 2.17.2 + H2 2.2.224 from `/app/lib/` (the exact jars already sitting in `enforce-java-release-signature-trust/environment/lib/`), no Spring, no network.

**Premise (his voice):** The old branch-office ingester is being decommissioned and nobody kept the source — all that survives is the jar at `/opt/legacy/ledger-oracle.jar` and one 40-row sample corpus with the output it produced. Write a replacement at `/app/ingest` that normalises raw ledger files into canonical rows in H2 and emits a JSON summary, and make it agree with the old one exactly. Not just on the sample — on any corpus the branches send. The jar won't be on the box when your ingester runs, so don't call it.

**Where the difficulty lives:** Nowhere in any document, because there is no document. The normalisation semantics exist only as behaviour of a compiled binary, and the three decisions that matter each have a strongly-endorsed wrong default: (a) decode is UTF-8-with-CP1252-fallback where the fallback is **per file, not per row** — one bad byte at the end of a file retroactively changes how every row above it decoded; (b) the dedup key is computed **after** NFKC + case-fold + internal-whitespace collapse, so an encoding misjudgement silently changes which rows collapse; (c) the surviving row of a duplicate group is **max source sequence number, not first-seen**. Each is invisible individually and they compose.

**Why a frontier model fails it (not "the rules are intricate"):** The model gets a clean, unambiguous green light on the only data it has. It writes UTF-8-with-replacement plus first-seen dedup, runs the sample, matches all 40 rows byte-for-byte, and stops. There is no error signal to act on and no rule list it failed to read — it fails because it stopped probing at the moment its evidence said it was done. The grading corpora do not exist when it makes that decision. This is precisely the generalisation gap the signature-trust task had no way to expose: there, everything the verifier checked was derivable from a forward read; here, nothing the verifier checks is present at solve time.

---

### #2 — `recover-java-chunk-transfer-integrity`

**Category:** `security` · **Subcategories:** `api_integration`, `db_interaction` · **Languages:** `java`, `bash`, `sql`

**Stack:** Java 17, `com.sun.net.httpserver` in-process service (same shape as the existing `artifact-api`), H2-backed object store, agent extends `/app/transfer-client`.

**Premise:** The transfer service takes resumable chunked uploads and we keep getting objects out the other side that don't match what went in. Extend `/app/transfer-client` so `com.snorkel.transfer.Main push` moves a file set through the service such that the committed object bytes equal the source bytes exactly, and record each file's digest in the results table.

**Where the difficulty lives:** Every signal during transfer says success — 200s, monotonically advancing committed offsets, clean commit — while a deterministic content-keyed subset of chunks is never durably stored. The read-back path lies too: it serves from the write-behind buffer unless a specific query form forces a durable read, so the obvious verification step also reports success. And the drop predicate is a function of the chunk payload, so retrying the identical bytes at the identical offset is dropped again, forever.

**Why a frontier model fails it:** The wrong hypothesis — "flaky server" — is the one that both prior experience and every observable endorse, and it is unfalsifiable without a designed experiment (same payload twice at one offset; same payload at a different offset; different payload at the same offset). Models diagnose transience, write retry-with-backoff, and burn the budget in a loop their own logs describe as recovering. The failure is not "missed a clause," it's "adopted the industry-standard mitigation for a failure mode that isn't this one."

---

### #3 — `reconcile-java-settlement-rounding-drift`, **hardened**

**Category:** `data-processing` · **Subcategories:** `db_interaction` · **Languages:** `java`, `bash`, `sql`

**Stack:** identical to #1 — opaque legacy jar as ground truth, H2 metadata table, `javac` + bundled libs.

**Premise:** The legacy settlement engine and the reconciler at `/app/settle` disagree on per-counterparty totals. Fix the reconciler so it matches the legacy engine exactly on any input file, and so its output doesn't move when the input rows arrive in a different order. Currency scales and fee treatment are in the H2 metadata table — read them, don't assume them.

**Where the difficulty lives:** The composition rule is asymmetric across line types and stated nowhere: principal lines net **before** rounding, fee lines round individually **before** netting, and — this is the hardening the author already identified — fee rounding mode depends on **counterparty tier**, also metadata-driven, also unstated. Separately, the modern reconciler accumulates in `double` in arrival order, so its answers move under shuffle, a defect no single run reveals.

**Why a frontier model fails it:** BigDecimal-with-per-currency-scale is instinct and gets it *close* — close enough to pass casual inspection and to balance most batches. The netting/rounding order split is not a rule it can fail to read; it's an arithmetic property recoverable only by feeding constructed one-line and two-line mixes through the jar. Honest caveat: this is the weakest of the three and I list it third because it is the **same machine as #1 with a different payload**, so once #1's harness exists this costs a fraction to build.

---

## 2. BUILD SKETCH — `rebuild-java-ledger-ingest-parity`

**What the container runs.** Base `public.ecr.aws/docker/library/python:3.13-slim-bookworm@sha256:01f42367...` (the digest already pinned in `/Users/fabrice-mac-mini/Documents/snorkel-ai/enforce-java-release-signature-trust/environment/Dockerfile`), plus `openjdk-17-jdk-headless`, `curl`, `procps`, `tmux`, `asciinema`. Copy `lib/` over verbatim from the signature-trust task. No HTTP service needed, so this image is *simpler* than the one already shipping.

- `/opt/legacy/ledger-oracle.jar` — the reference ingester, built in a **discarded** multi-stage build so no source lands in the runtime image. Author it with opaque class names; compile `-g:none`. Do not ship a decompiler. Note: `javap -c` will always work, and that is fine — the difficulty must not rest on the jar being unreadable, it rests on the held-out corpora. An agent that reads bytecode and gets the semantics right has earned the pass.
- `/app/ingest/` — non-solution scaffold satisfying the `codebase_applicability` gate: `Main.java` dispatcher, stubbed normaliser classes throwing `UnsupportedOperationException`, `build.sh`, `run.sh`. Compilable, zero answer logic.
- `/app/samples/corpus-40/` plus `/app/samples/expected/` — one worked example. **Critical design decision below.**
- H2 store initialised at build time via `org.h2.tools.RunScript` exactly as the existing Dockerfile does at lines 31-36.

**The single most important construction detail.** The sample corpus must **not** exercise every quirk. Ship it with one CP1252 file (so the encoding axis is hinted) and **no duplicate groups at all**, so the max-sequence survivor rule has zero representation in anything the agent can read. If the sample covers all three quirks, a model converges by fitting it and you have built TRIVIAL again. If it covers one, the model must generate adversarial input to find the other two. That is the whole task.

**What the agent must produce.** `bash /app/ingest/build.sh` compiles; `bash /app/ingest/run.sh <corpus-dir> <jdbc-url> <summary-json-path>` ingests. Canonical rows land in `canonical_ledger`; the summary JSON carries per-file and aggregate counts. Stated requirement: parity with the legacy jar on any corpus.

**What the oracle does.** `solution/solve.sh` drops in a human-written Java ingester replicating the semantics, compiles with `javac` against `/app/lib`, runs it. Fully deterministic — no clock, no threads, no network. A ~5k-row corpus across ~12 files runs in seconds; the whole oracle is minutes inside the 900s budget.

**What pytest asserts.**

1. **Sample parity** — agent output vs. oracle output computed at verify time on the shipped corpus.
2. **Held-out parity, N seeded corpora** — generator synthesises fresh corpora per test (mixed encodings, BOM/no-BOM, mojibake, NFC vs NFD, CRLF/LF, truncated final line), runs the stashed oracle jar for expected, runs the agent, diffs canonical rows read back out of H2 plus the summary JSON.
3. **The killer test** — a corpus whose duplicate groups have shuffled sequence numbers, so first-seen and max-sequence disagree on every group. This is the test that catches "matched the sample and shipped."
4. **Per-file fallback test** — a file that is valid UTF-8 except for one byte near the end. Per-row and per-file fallback disagree on every row above it.
5. **Program actually ran** — point the agent's `run.sh` at a fresh empty store; hand-written rows fail.
6. **No delegation** — `tests/test.sh` relocates `/opt/legacy/ledger-oracle.jar` to a tests-side path before pytest starts. The instruction already told the agent the jar won't be present at run time, so this is fair, and it kills the shell-out cheat cleanly.
7. **Nop baseline** — scaffold throws, score 0.0.

**How the variant harness is reused.** `run_h2_script()`, `h2_rows()` (including the `|| '~' ||` column-concatenation trick around RunScript's space-delimited output) and the `/tmp/variant-{name}` isolation pattern port over from `enforce-java-release-signature-trust/tests/helpers.py` essentially unchanged. Two swaps: `build_variant_store(seed_sql)` becomes `build_empty_store(name)` (schema only), and `expected_reports_for_db()` becomes `oracle_output(corpus_dir, db_url)` which shells to the stashed jar. `test.sh` is the existing 18-line file verbatim — canonical reward block, nothing after `fi`.

---

## 3. HONEST DIFFICULTY ESTIMATES

Stated as **worst-model pass rate**, since that is what the gate reads. Gate needs ≤ 60%.

| Task | Expected worst-model pass | Dominant failure mode | Would I bet on it? |
|---|---|---|---|
| #1 ingest-parity | **40-55%** | Matched the 40-row sample, shipped, diverged on held-out corpora — specifically the sequence-survivor rule | **Yes, with a mandatory pilot** |
| #2 chunk-transfer | **40-50%** | Diagnosed transient failure, wrote retry-with-backoff, never converged, burned the budget | Yes, but second |
| #3 rounding-drift | **50-60%** | Landed close via BigDecimal instinct; wrong on tier-dependent fee rounding | Only after #1 exists |

**Where I am deliberately not repeating the last task's optimism.**

#1 clears the bar but **not comfortably** — 40-55% is a real margin over the 60% ceiling, not a rout, and I would not tell you it is safe before you pilot it. Run 5×2 before you build the full test matrix. If it comes back above 60%, the lever is **not** more quirks. It is removing sample coverage: strip the sample corpus down until only the encoding axis is visible in it. A model cannot fit what it cannot see.

#2 has the higher ceiling but higher variance in *measurement*, because its failure mode is budget exhaustion rather than a wrong answer. How much budget a model burns in a retry loop varies run to run, so your 5-run pass rate will be noisier than #1's. It also has real construction risk: the drop predicate has to be dense enough that no fixed re-chunking gets lucky, or an agent passes by accident without discovering anything. That is tunable, but it is tuning you cannot do until the thing runs.

#3 at 50-60% is close enough to the line that I would not build it standalone. Build it second, on #1's harness, when the marginal cost is low and a bounce is cheap.

**If I had to pick one to start today: #1.** Not because it is the hardest — #2 probably is — but because its ground truth is a *function*, not a value. There is nothing to hardcode, nothing to transcribe, no clock, no scheduler, no timing. The oracle cannot disagree with itself. After nine commits into a task that measured TRIVIAL, the property worth optimising is *the difficulty cannot leak out through a route you did not anticipate*, and #1 is the only one on the list where I can argue that from structure rather than from hope.

---

## 4. WHAT TO AVOID

**Spec-reading in disguise, or prior-reading with the trap cancelled:**

- **`reconcile-java-sso-session-clocks`** — looks like discovery, is a two-parameter fit with a built-in green light. The property that makes it *fair* ("check that all co-observed pairs agree under your fit") is exactly the property that makes it *easy*: the agent gets told when it is right. Residuals split into two visible clusters the moment anyone diffs the co-observed set. Predict EASY.
- **`reconcile-java-settlement-currency-scales`** — the premise is right (punish the ISO 4217 prior) but the instruction requirement "emit the scale you determined for each currency" **signposts that scales must be determined rather than recalled**, which cancels the trap it depends on. And the search is ~5 exponents per currency, over-determined and self-verifying. Genuine tension: remove the signpost and you lose the ability to detect compensating errors. Not resolvable today.
- **`recover-java-mojibake-catalog-build`** — missing `-encoding` plus POSIX locale is a named, well-known Java gotcha, and charset reasoning is a model strength, not a weakness. The recoverable/unrecoverable boundary is computable by a round-trip test the agent can run itself.

**Difficulty leaks — a safe path passes without the discovery.** These three are the same failure shape as the last task: the correct behaviour is reachable without ever being wrong first.

- **`settle-java-ledger-exactly-once`** — your own solvability argument concedes "a fully safe (check-before-retry) implementation needs no measurement at all." Check-before-retry against a documented `GET /ledger/{key}` is the *first* thing a careful model writes. The LRU-eviction discovery is optional, so it does not gate.
- **`drain-java-lease-queue-under-backpressure`** — "halve concurrency on revocation, abandon on rejection" is the textbook shape and you note it passes.
- **`negotiate-java-relaykit-session-protocol`** — "a conservative client that waits for an explicit ready signal also passes." Plus high authoring cost and no scaffold reuse. Worst cost-to-difficulty ratio on the list.

**Flaky oracles — cannot meet the 6-of-10-verifier-runs bar:**

- **`repair-java-ledger-transfer-drift`** — difficulty realism 9, the best diagnosis in the list, and unshippable as specified: pass/fail depends on H2 actually detecting a lock-ordering deadlock under generated load, which is scheduler-dependent. A quiet run passes a still-broken fix. Salvageable only by making the retry trigger deterministic (injected conflict on a keyed lock rather than a real deadlock) — that is a rebuild, not today's task, but the non-idempotent inner-transaction accrual is a good enough idea to keep in the drawer.
- **`harden-java-stream-replay-checkpoint`** — SIGKILL at randomised wall-clock offsets, 3-40 times per test, plus a 200k-event throughput floor. Where the kills land relative to the batch loop is not reproducible across machines.
- **`trace-java-export-descriptor-exhaustion`** — fd accounting is sensitive to JDBC pool size, JVM version and `/proc` semantics under the platform's container runtime, and soak tests eat verifier budget.

**Solvability risk, which is worse than TRIVIAL:**

- **`calibrate-java-admission-shaper`** — "zero rejections, ever" against an unknown bucket forces conservatism, which then misses the tick budget. The pass region may be narrow enough to produce a 0/10 test, which bounces on solvability. Relax it to "at most K rejections" and the difficulty evaporates. Don't.

- **`resolve-java-duplicate-class-closure`** — well-trodden Java territory; `-verbose:class` plus shade is a route both models take reliably, and per-exercise pass/fail lets them bisect mechanically.

**One framing warning for #1.** Reviewers reject difficulty built from "a long list of trivial edge cases," and three normalisation quirks could be *mistaken* for that. Build and describe it as one semantic surface — how does this system normalise text? — and make the defence explicit in the difficulty explanation: each quirk changes the output of **every row in the corpus**, not a corner case. If you find yourself adding a fourth and fifth quirk to raise the pass rate, stop; strip sample coverage instead.

---

## 5. DOES ANYTHING CLEAR THE BAR

Yes — **#1 clears it, conditional on a pilot**, and I would start building it today rather than continue searching.

More useful than the individual ranking is the class it belongs to, because that is what to generate from next time:

> **Ground truth is a function held by an opaque in-container reference, and the agent is graded on inputs that do not exist while it is working.**

That construction defeats all three routes the signature-trust task left open at once. There is nothing to transcribe, because there is no document. There is nothing to recall, because the reference is authored rather than standard. And there is nothing to fit, because the grading corpora are generated after the agent stops. The only strategy that survives is *design an experiment, then verify your artifact against inputs you invented yourself* — which is the one behaviour frontier models reliably skip when their current evidence says they are finished.

Everything else on this list is a weaker instance of that pattern or of its sibling ("the system lies to you in the exact place you would verify," which is #2). The concepts that scored badly did so because they are neither: they are policy transcription with extra steps, or they hand the agent a safe path that needs no discovery.

Concretely: build #1 now. Pilot at 5×2 before writing the full test matrix. If it measures above 60%, cut sample coverage rather than adding mechanics. Then reuse the harness for #3 at a fraction of the cost, and keep #2 as the next standalone once you have seen how the ingest-parity numbers land.