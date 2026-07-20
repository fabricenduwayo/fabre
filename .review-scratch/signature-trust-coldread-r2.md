## 0. BLOCKER — the answer key is currently unrealizable in the environment

Before difficulty: this task cannot produce the intended 17 answers as checked in. The cold read was run against a hypothetical fixture ("assume GET and POST succeed"), so it validated a *document*, not the task.

- `/Users/fabrice-mac-mini/Documents/snorkel-ai/enforce-java-release-signature-trust/environment/artifact-api/data/registry.json` holds 6 artifacts (`art-alpha, beta, gamma, delta, epsilon, art-live`) against a 17-artifact seed. Eleven seeded artifacts are absent — including **art-zeta, art-omega, art-eta, art-iota, art-nu, art-xi, art-pi**, ten of which must reach the API to earn their intended verdicts. All would 404 → `denied/unknown_artifact`.
- Registry digests are 62 chars and match no H2 digest. `ApiServer.canonicalDigest` defaults to `registry_digest`, so **art-alpha returns 409 `digest_mismatch`, not 400 `bad_signature`** — the intended answer is unreachable even for an artifact that *is* in the registry.
- `ApiServer.java:184-186` hardcodes `if ("art-beta".equals(artifactId)) canonicalDigest = "d2222…"` — a leftover from the pre-amendment design that must go.
- `/Users/fabrice-mac-mini/Documents/snorkel-ai/enforce-java-release-signature-trust/solution/attest-worker/src/com/snorkel/attest/Worker.java` is the pre-amendment stub: it selects evidence with `SELECT … revoked FROM artifact_evidence` (no such column in `schema.sql`), takes the first row for an artifact, and implements none of A-2026-01…11. There is no oracle.
- `signing-trust-amendments.md` is untracked; `schema.sql`, `seed.sql`, `signing-trust-policy.md` are modified vs HEAD; tests are stale.

Reader 4 half-detected this: *"If the fixture actually holds a stale canonical digest for one of my seven trusted artifacts, that artifact would flip to denied digest_mismatch and I would have no way to see it."* It does, for all of them.

Registry entries required (canonical digest = H2 operative digest; `detached_signature` = `sig-<digest[0:8]>-<signer>`):

| artifact | operative | canonical digest | signer | signature | outcome |
|---|---|---|---|---|---|
| art-alpha | ev-a1 | `a1a1a1a1`+56×`0` | key-a | `sig-bad00000-key-a` | 400 bad_signature |
| art-beta | ev-b2 | `b2b2b2b2`+56×`0` | key-a | `sig-b2b2b2b2-key-a` | 200 |
| art-delta | ev-d1 | `d1d1d1d1`+56×`0` | key-a | `sig-d1d1d1d1-key-a` | 200 |
| art-zeta | ev-z1 | `f1f1f1f1`+56×`0` | key-c | `sig-f1f1f1f1-key-c` | 200 |
| art-omega | ev-o1 | `0a0a0a0a`+56×`0` | key-c | `sig-0a0a0a0a-key-c` | 200 → downgraded |
| art-eta | ev-h1 | `1b1b1b1b`+56×`0` | key-d | `sig-1b1b1b1b-key-d` | 200 |
| art-iota | ev-i1 | `3d3d3d3d`+56×`0` | key-b | `sig-3d3d3d3d-key-b` | 200 |
| art-nu | ev-n1 | `6a6a6a6a`+56×`0` | key-a | any | `verify_degraded:true` |
| art-xi | ev-x2 | `8c8c8c8c`+56×`0` | key-a | `sig-8c8c8c8c-key-a` | 200 → downgraded |
| art-pi | ev-p1 | `9d9d9d9d`+56×`0` | key-a | `sig-9d9d9d9d-key-a` | 200 |

Keep `registry_digest` ≠ canonical on every row (preserves the "never send the registry digest" trap). Keep `art-epsilon`'s `verify_degraded:true` — it is a good trap: skipping A-2026-09 yields `quarantine/verify_degraded` instead of `denied/revoked_signer`. Add verifiable entries for **art-theta, art-kappa, art-omicron** so that skipping A-2026-09/10 produces a loud `trusted/verified` rather than a coincidentally-denied `unknown_artifact`.

**Silver lining, and it matters for §3:** because the operative digest is what gets POSTed, wrong operative selection produces 409 `digest_mismatch` — a *different* verdict. art-beta (b1/b2), art-delta (d1/d2), art-pi (p1/p2/p3) all route selection errors through the API into a distinct wrong answer. The cold read is structurally blind to this, since readers were told to assume verification succeeds.

## 1. Spec sufficiency

**No true spec gaps.** Every contested artifact is determined by amendment text. Detail:

| Contested | Cause | Governing text |
|---|---|---|
| art-xi (strict tie) | **DIFFICULTY** | A-2026-11: "that `signed_at` is **strictly earlier** than the instant the channel became exposed." Unambiguous; equality fails. |
| art-pi (inertness) | **DIFFICULTY** as written | A-2026-05: "its own `supersedes_evidence_id` is never followed, even when the discarded row is itself voided." Explicit. (But see §2 — the rule is vacuous.) |
| art-delta / art-pi (discarded row still attested + greatest `recorded_at`) | **DIFFICULTY** | A-2026-02 excludes rows "discarded under A-2026-05"; A-2026-05: "A discarded amendment is not operative under A-2026-02." Stated twice. |
| exposure via `amendment_key_id` (5 readers flagged) | **DIFFICULTY** | A-2026-11: "names the compromised key **as `signer_key_id`**." The column is named. Good drafting. |
| art-zeta (TSA earns exemption without doing work) | **DIFFICULTY** | A-2026-11 ¶3 conditions only on naming a `tsa_id` whose window covers `signed_at`. Substantively odd, textually determinate. |
| art-eta (backdated `effective_from`) | **DIFFICULTY** | A-2026-08: "A `revoke` with any other reason takes effect at its `occurred_at`, and its `effective_from` is disregarded." |
| art-kappa (two competing denials) | **DIFFICULTY** | A-2026-09: "This is settled before A-2026-10"; A-2026-10: "It confers nothing against A-2026-09." |
| art-omicron | **DIFFICULTY** | A-2026-10: "unless the operative row names a `tsa_id` whose own half-open `[valid_from, valid_until)` window covers that `signed_at`." |
| **art-lambda (`missing_evidence` class)** | **REAL DEFECT** (still determinate) | See below. |

**The one wording defect.** A-2026-04 says `no_operative_evidence` is quarantine, then: *"That is a **different outcome** from `missing_evidence`."* "Outcome" reads naturally as *verdict*, and amendments override the body — so a careful reader can conclude art-lambda is **not** quarantine. Only the body's prose classifier ("an absence of evidence to decide on") rescues it. Reader 1 landed correctly at **medium** confidence and marked it verdict-changing; every other reader asserted quarantine without derivation. That is a spec relying on a prose classifier to settle a verdict class the amendment appears to contradict.

Draft replacement — **A-2026-04**, final sentence:

> An artifact with no `artifact_evidence` rows at all is instead recorded `quarantine` with reason_code `missing_evidence`. Both are `quarantine`; only the reason_code differs.

**Second (optional, zero-cost) clarification** — A-2026-11 ¶1, appended. Four readers asked whether a `denied` artifact can be an exposure *source*. Currently determinate and overdetermined by art-zeta/art-omega, but load-bearing the moment the seed changes:

> An artifact exposes its channel by its operative row's `signer_key_id` alone; its own verdict is irrelevant.

## 2. Did the tightening work?

Partly. Ranked:

**art-xi — earned its place. The best artifact in the set.** It is the *only* artifact that breaks the shortcut "exposure = artifact signed by the compromised key" (its signer is key-a; art-omega's is key-c). It is also the only test of the strict-inequality boundary — art-zeta tests the passing side from 5 days clear. Two independent discriminators, and it drew `medium` confidence from 3 of 6 readers, the most hesitation in the set.

**art-omicron — earned its place, but as coverage, not difficulty.** It genuinely kills the "non-null `tsa_id` ⇒ rescued" shortcut, which art-iota alone would have rewarded. But it is a single window comparison: 6/6 high confidence, zero ambiguities raised. Necessary, not hard.

**art-pi — decorative, and worse than decorative.** Six of six readers named it their `hardest_part`. All six got it right. The rule they agonized over cannot change any answer.

Proof that A-2026-03's cascade clause is vacuous under A-2026-05: the cascade adds `Y` when a voided row `X` has `X.supersedes_evidence_id = Y`. Every row with non-null `supersedes` is an amendment (A-2026-05 s1), so `X` is either discarded or not.
- Discarded → A-2026-05 s4 forbids following its pointer. Nothing added.
- Not discarded → A-2026-03 s1 ("A row whose `supersedes_evidence_id` is non-null voids the row it references") already voided `Y` directly, regardless of whether `X` is itself void. `Y` is already in the void set.

∎ **A-2026-03 sentence 2 and A-2026-05 sentence 4 are both dead text.** I verified this against all four chains in the seed (beta, gamma, delta, pi): a solver implementing *direct voiding only* is behaviorally identical to one implementing the full spec, and scores 17/17.

So art-pi discriminates against exactly one solver: the one who implements the cascade *and* misses the inertness clause. A solver who never reads A-2026-03's second sentence passes. **The trap penalizes thoroughness and rewards omission** — backwards for a spec-following task. The readers' unanimous "this was the hardest part" is measuring illusory difficulty.

Against the prior 5/5 at 14/14: net discrimination added is art-xi plus one shortcut-closure from art-omicron. That is real but small, and it did not move the reading needle at all — 6/6 at 17/17.

## 3. Difficulty verdict

**The cold read cannot clear or fail this gate, and reading it as evidence either way is a mistake.** It measures spec sufficiency, which now passes cleanly. It does not measure the task.

Blunt assessment of what it does tell you: **the reading layer is not hard and will not get harder by this route.** Six strong models at high effort, unanimous, mostly `high` confidence, with the entire policy in context and no implementation burden. The amendments are drafted so that each one explicitly anticipates its own trap ("though not of the authority A-2026-05 requires", "It confers nothing against A-2026-09", "even when the discarded row is itself voided"). That is excellent for solvability and actively hostile to difficulty — a careful model transcribes the amendments into code almost mechanically.

Where the gate will actually be decided, none of which the cold read touched:
- remembering channel exposure at all — it is the last amendment and a *post-pass* over completed verdicts, the single most commonly dropped structure;
- getting the post-pass one-directional (downgrades `trusted` only; never touches `denied`, never touches existing `quarantine`, never promotes);
- replaying `key_lifecycle_events` with the two-branch effective-instant rule instead of reading a column;
- three half-open boundaries (`[not_before, not_after)`, `[valid_from, valid_until)`, and `strictly earlier`);
- ordering discard → void → select, then routing the *correct operative digest* to `POST /verify`, where a selection error surfaces as 409.

That last one is the real discriminator and it is invisible to a policy read. My estimate: a mid-tier model clears well under 60% on all-17, dominated by dropping or mis-scoping the exposure post-pass. **It probably clears EASY — but on implementation surface, not on the reading, and you have no evidence for it yet because there is no oracle and no runnable environment.** Do not record the 6/6 as difficulty evidence.

## 4. What next

**Do not ship. Do not add artifacts.** More artifacts will not help: six strong readers are unanimous with the policy in front of them, so the reading is saturated. The format is at its ceiling for *derivation* difficulty.

In order:

1. **Regenerate `registry.json` from `seed.sql`** per the table in §0, delete the `art-beta` hardcode at `ApiServer.java:184-186`, drop `art-live`, and add verifiable entries for art-theta/art-kappa/art-omicron so H2-stage shortcuts fail loudly.

2. **Write the real oracle** in `solution/attest-worker/…/Worker.java`. It currently implements none of A-2026-01…11 and queries a column that does not exist. Nothing about this task is verified until the oracle reproduces all 17 against the live API.

3. **Fix A-2026-04's `missing_evidence` sentence** (§1). One-line change, removes the only place a reader can correctly derive a wrong verdict class.

4. **Resolve the vacuous cascade.** Two honest options:

   - *Delete* A-2026-03 sentence 2 and A-2026-05 sentence 4. Costs nothing behaviorally, removes text that reads load-bearing and is not.
   - *Make it reachable* — better, and it raises real difficulty. Restrict direct voiding to the head of each chain, so deeper links are reached **only** by cascade. Redraft **A-2026-03** sentence 1:

     > Among an artifact's amendments that are not discarded under A-2026-05, the one with the greatest `recorded_at` voids the row it references; break a tie by lexicographically greatest `evidence_id`. Then void any row whose `evidence_id` equals a voided row's `supersedes_evidence_id`, repeating until the void set stops growing.

     Under this, **art-gamma's ev-g1 becomes void only via the cascade** — a solver who skips the cascade leaves ev-g1 attested and non-void, making it operative and flipping art-gamma from `quarantine/no_operative_evidence` to `trusted/verified`. And art-pi's inertness clause becomes genuinely load-bearing in the opposite direction. Every one of the 17 intended answers is preserved (verified against beta, gamma, delta, pi); art-gamma and art-pi become a true mirrored pair instead of a pair where only one direction is testable.

5. **Then** re-run the cold read. If it stays 6/6 after step 4, stop tightening the policy — the reading is done, and difficulty lives entirely in the implementation. At that point the only structural lever that would actually raise it is removing the *scaffolding*, not adding artifacts: the amendments currently pre-announce every interaction and pin every ordering. Deleting the explicit ordering pins ("This is settled before A-2026-02", "Amendment authority is settled before A-2026-03 computes the void set", "This is settled before A-2026-10") would force solvers to *derive* the evaluation order from consistency rather than read it off — but that trades directly against solvability and would need its own cold read to confirm it stays determinate. Given the gate is about the worst model's implementation, I would not spend that risk. Fix the environment, write the oracle, take the difficulty from implementation.

## 5. Defects behind correct answers

- **`missing_evidence` verdict class** (art-lambda) — real, fix per §1. The only case where the amendments point away from the intended answer and the body's prose has to rescue it.
- **Vacuous cascade / inertness pair** — real, §2/§4.4. Two rules that provably cannot fire; all six readers treated them as the crux.
- **Exposure source vs. artifact verdict** — determinate and overdetermined today (zeta and omega are non-denied key-c sources), so it is latent, not live. Flagged by 4 readers. One appended clause makes it immune to future seed edits.
- **Non-load-bearing TSA earns the exposure exemption** (art-zeta vs art-omega, identical but for a `tsa_id` that does no work under A-2026-10) — flagged by readers 3 and 6 as substantively strange. Textually determinate, so not a defect in specification, but if art-zeta/art-omega are meant to read as a designed pair rather than an accident, A-2026-11 ¶3 should say so outright: the countersignature is evidence of *when*, independent of whether A-2026-10 needed it.