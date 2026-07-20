I have everything I need. I read the policy body, all eleven amendments, the schema, the seed, the API fixture, the oracle, the tests, and the author's own hardening plan.

## 0. Blocking precondition (read before acting on anything below)

The readers assessed a policy whose fixture does not exist yet. `environment/attestation-db/{schema,seed}.sql` and `signing-trust-policy.md` are rewritten (uncommitted), `signing-trust-amendments.md` is new (untracked), but **every consumer is still the old 5-artifact task**:

- `/Users/fabrice-mac-mini/Documents/snorkel-ai/enforce-java-release-signature-trust/environment/artifact-api/data/registry.json` — 5 old artifacts, digests `d1111111…`; the new seed uses `RPAD('a1a1a1a1',64,'0')`. Eight of the fourteen artifacts 404, the rest 409.
- `environment/artifact-api/src/com/snorkel/attestapi/ApiServer.java:184` — still hardcodes the `art-beta` canonical digest.
- `solution/attest-worker/src/com/snorkel/attest/Worker.java:37,90` — reads `evidence.revoked`, a column the new schema does not have. The oracle cannot run.
- `tests/helpers.py:206` — same dead `revoked` column; `expected_report()` implements the *old* policy.
- `tests/test_outputs.py:61-93` — asserts answers that **contradict** the new key: art-alpha `trusted/verified` (new: `denied/bad_signature`), art-gamma `denied/revoked_signer` (new: `quarantine/no_operative_evidence`), art-delta `denied/bad_signature` (new: `trusted/verified`), art-epsilon `quarantine/verify_degraded` (new: `denied/revoked_signer`).

Your plan already flags this (`.review-scratch/signature-trust-hardening-plan.md`, risk table line 682, step 6). It is still outstanding. Nothing below can be validated until `tools/gen_registry.py` exists and the oracle runs green. Note also that readers were *handed* the API outcomes for art-alpha and art-nu — those two artifacts are free points and carry no evidence about anything.

## 1. Spec sufficiency

**No reader disagreed with the key. 70/70 verdict+reason pairs.** So the "disagreement" bucket is empty. The real question is which of the raised ambiguities are defects that survived on luck. I checked each against the text.

**Not gaps — the text settles them:**

- **A-2026-03 cascade direction (readers 1, 2, 3, 5 — all four called this their hardest point, and all four mis-analyzed it).** They believed art-gamma hinges on the cascade. It does not. A-2026-03 sentence 1: *"A row whose `supersedes_evidence_id` is non-null voids the row it references."* `ev-g2.supersedes_evidence_id = 'ev-g1'` and ev-g2 is not discarded (amendment key key-a live at 2026-01-20), so **ev-g2 voids ev-g1 directly**, no cascade involved. ev-g3 voids ev-g2 the same way. The "restorative reading" they feared is separately foreclosed by A-2026-04 (*"follows from the reference alone"*) and by A-2026-05 granting loss of voiding power **only** to discarded amendments. art-gamma is over-determined by two independent routes. Legitimate difficulty at most — and in truth easier than four of five readers thought. Reader 4 was the only one who saw the direct route.
- **`amendment_key_id` exposing a channel (readers 1, 2, 3, 5).** A-2026-11: *"an artifact whose **operative** evidence names the compromised key as **`signer_key_id`**."* ev-d2 fails both limbs independently — it is discarded (not operative) and its `signer_key_id` is key-a. Settled. This is the best trap in the seed; it moves four verdicts.
- **A-2026-11 exemption conjunctive vs disjunctive (reader 4, "the least-determined point in the whole policy").** *"…names a `tsa_id` whose window covers that row's `signed_at` **and** that `signed_at` is strictly earlier…"* — one `when` clause, two conjuncts. The disjunctive parse is not grammatically available (the second conjunct is a clause; `covers` cannot take it). Settled. Reader 4 reached the right answer partly by arguing from authorial intent ("otherwise the machinery is inert"), which is worth noting, but the text does stand on its own. Optional zero-cost polish: `"…when both its operative row names…"`.
- **Denied artifacts still expose (reader 1).** Exposure is defined over operative evidence with no verdict condition, and *"arbitrated after every artifact already has a verdict"* implies verdict-independence. Also not load-bearing: art-zeta and art-omega expose `edge` regardless.
- **Was the countersignature load-bearing for art-zeta (reader 3).** A-2026-11 asks only that the row *name* a covering `tsa_id`. Plain text. Settled.

**One real latent gap — fix it:**

**A-2026-04 sentence 1 vs A-2026-05 (raised by reader 3, who correctly noted it does not bite in this seed).** A-2026-04 says voiding *"follows from the reference alone"*; A-2026-05 says a discarded amendment *"voids nothing under A-2026-03."* Read literally these contradict. The intended resolution is that A-2026-04 governs **status** and A-2026-05 governs **authority**, sequenced by A-2026-05's *"Amendment authority is settled before A-2026-03 computes the void set."* It is inert today only because ev-g3 is withdrawn **and** has a live amendment key, so both readings agree. Add any row that is withdrawn with a dead amendment key and the policy becomes genuinely indeterminate. Since my difficulty proposal below adds exactly such a row, fix this first.

> **In A-2026-04**, replace *"Voiding under A-2026-03 follows from the reference alone."* with:
> **"Voiding under A-2026-03 is independent of the referring row's `status`, though not of the authority A-2026-05 requires."**

**A second gap that opens the moment you raise difficulty.** A-2026-03's cascade (*"void any row whose `evidence_id` equals a voided row's `supersedes_evidence_id`"*) and A-2026-05's *"voids nothing"* collide for a row that is **both discarded and voided**: literally the cascade follows its pointer, while A-2026-05 says it is powerless. No such row exists today. Pre-empt it:

> **In A-2026-05**, after *"…so the row it names stands."*, add:
> **"A discarded amendment is inert in the A-2026-03 cascade: its own `supersedes_evidence_id` is never followed, even when the discarded row is itself voided."**

## 2. Difficulty — the task does NOT clear EASY

State it plainly: **5/5 readers at 14/14, 70/70 pairs, 66 of 70 self-rated "high" confidence.** Only 4 verdicts were rated "medium" (gamma ×2, zeta/omega ×2). The point estimate for pass rate is **1.0** against a gate that needs the *worst* model under **0.60**. Rule-of-three gives per-verdict accuracy ≥ 0.957 at 95%, so pass = p^14 ≥ 0.54 — the gate is only satisfiable at the extreme floor of the interval, and the data actively points at the ceiling. It clears TRIVIAL. It does not clear EASY on the reasoning axis, and you should not bank the gate on Java/H2 implementation friction — that produces flaky failures, not discriminating ones.

**Discriminating (keep, unchanged):**
1. **art-delta** — discarded amendment loses voiding power so the *older* row wins. Defeats both naive heuristics (latest `recorded_at`; compromised amendment key → deny). Strongest mechanic in the set.
2. **art-delta / stable non-exposure** — `amendment_key_id` must not expose. Moves four verdicts.
3. **zeta / omega / kappa** — one key, three verdicts, split by backdated effective instant and tsa presence.
4. **art-eta** — `cessation_of_operation` disregards a backdated `effective_from`.
5. **art-kappa** — A-2026-09 before A-2026-10; the tsa looks decisive and confers nothing.

**Decorative — eight clauses that do zero work in this seed.** I verified each against the data:
- A-2026-03's cascade sentence (provably adds no row anywhere; the void set is complete after sentence 1).
- A-2026-02's lexicographic `evidence_id` tiebreak (no two rows share a `recorded_at` within an artifact).
- A-2026-07's lexicographic `event_id` tiebreak (no two events share an effective instant per key).
- A-2026-11's *"earliest such instant governs"* (only one `key_compromise` in the seed).
- A-2026-11's *"whether or not they appear in `pending_attestations`"* (`artifacts` == the 14 queued rows).
- A-2026-08's *"or at its `occurred_at` when `effective_from` is null"* (kev-005 has a non-null `effective_from`).
- A-2026-05's *"A null `amendment_key_id` is not live"* (all four amendment rows name a key).
- A-2026-06's *"countersignature… has no bearing on whether a key is live"* (no amendment row carries a `tsa_id`).

**Two silent correctness holes — an implementation that skips a stated check still scores 14/14:**
- **The TSA window predicate is dead.** `tsa-1` is the only TSA and its `[2025-01-01, 2027-01-01)` window covers every `signed_at` in the seed. Treating "`tsa_id` is non-null" as sufficient passes everything, in both A-2026-10 and A-2026-11.
- **Half-open `[…)` semantics are never exercised.** No `signed_at` or `recorded_at` lands exactly on a `not_after` or on the 2026-01-10 effective instant. Inclusive `<=` on both ends passes everything, despite the amendments stating half-open three times.

**Four concrete tightenings, cheapest first:**
1. **Add `tsa-2`, window `[2025-01-01, 2026-01-01)`.** New `art-omicron`, signer key-b, `signed_at 2026-03-03` (outside key-b's window), `tsa_id tsa-2` → not covered → `denied/expired_key_signature`. Direct foil to art-iota. Kills hole #1.
2. **Add `art-xi` in `edge`, signer key-a (clean), `signed_at 2026-01-10 00:00:00` exactly, `tsa_id tsa-1`** → trusted on the merits, `edge` exposed at 2026-01-10, `signed_at` is *not strictly earlier* → `quarantine/channel_exposure`. Tests the strict inequality, tests exposure of a clean-key artifact, and forces the two-phase worker your plan wanted. Kills hole #2.
3. **Second `key_compromise` into `edge` at a later instant** (key-e, effective 2026-02-20) → activates *"the earliest such instant governs"* and makes art-xi's boundary meaningful rather than coincidental.
4. **Make the cascade load-bearing** — the biggest difficulty gain. Chain `ev-p1` (attested, supersedes NULL) ← `ev-p2` (attested, supersedes ev-p1, `amendment_key_id key-c`, `recorded_at 2026-03-01` → **discarded**) ← `ev-p3` (**withdrawn**, supersedes ev-p2, `amendment_key_id key-a`, `recorded_at 2026-03-15` → stands). ev-p3 voids ev-p2; ev-p2 is discarded so it voids nothing; whether ev-p1 survives turns entirely on the A-2026-03/A-2026-05 collision. With the A-2026-05 sentence above, ev-p1 is operative → `trusted/verified`; without it the artifact is indeterminate. This composes four mechanics in one artifact — harder than anything currently in the set — and it is the reason both drafted sentences are non-optional.

**Order of work:** land the two amendment sentences, then the seed additions, then `tools/gen_registry.py` and the oracle/test/ApiServer rewrite. Re-run the readers after; if they still come in at 14/14 across the board, the problem is the format rather than the content, and the honest move is to stop adding artifacts and instead remove the stipulated API outcomes so the agent has to discover them.