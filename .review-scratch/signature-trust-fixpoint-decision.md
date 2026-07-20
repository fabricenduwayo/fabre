## 1. DECISION: PARK. Do not ship any of the three.

Design 1 is the only one that is technically sound (design 3's non-retraction theorem is false — the judge's period-2 oscillation is real, because sealing an amendment un-voids its target, and an un-voided row with higher `recorded_at` displaces the min witness *without that witness ever being sealed*; design 2 abandons the fixpoint for a stipulated pass count and its own difficulty judge said he'd ship nothing rather than that). Design 1's monotonicity proof holds, and it holds for a specific reason: ineligibility touches only A-2026-02 candidacy and never leaks into A-2026-03, so the candidate set is pure set subtraction and the compromised-signer min witness is pinned. That is careful work and it is correct.

It still should not ship, for one reason that is not opinion:

**The task already contains this exact mechanic, and it discriminates nothing.** A-2026-03 (amendments line 24-26) says "repeating until the void set stops growing." Both the oracle (`Worker.java:201-215`, `while (growing)`) and the verifier (`helpers.py:172-182`) implement it as a literal iterate-to-stability loop — *including* a subtle non-leaking carve-out (`Worker.java:206-209`, A-2026-05's "discarded amendment is inert in the cascade"). There is a dedicated test for that carve-out, `test_discarded_amendment_is_inert_in_the_cascade` at `test_outputs.py:113`. Both frontier models pass it 10/10.

All three designs propose: seed, iterate to stability, plus a non-leaking exemption clause. That is structurally identical to a mechanic measured non-discriminating **on this task, by these solvers, right now**. This is not an analogy from elsewhere; it is the same idiom one level up the call stack.

And the conflict is structural, not fixable by better authoring. Your binding constraint says the amendments must *state* which fixpoint and how it is reached. Satisfying that means writing a while loop in English. Compare what each design actually produced — "Seed the exposure set empty… Repeat until a pass leaves the exposure set unchanged" (D1), "There is no third pass" (D2), "Stop at the first round whose derived map equals the map it started from" (D3). Each is transcription, not inference. Determinacy and difficulty are in direct opposition here, and determinacy has to win, so difficulty loses by construction. All three difficulty judges scored 3/10 independently, two calling it fatal.

## 2. Exact edits — moot. 
Not producing them. The only design worth the diff is D1, and I expect it back at EASY.

## 3. Validation protocol — only if you override me.
In this order, abort at the first failure. (a) Exhaustively enumerate F's fixpoints over the full lattice for the shipped store **and every variant seed** — the judge measured ~3.9% of plausible stores admitting multiple fixpoints; more than one fixpoint on any shipped store means abort, not "state least harder." (b) Ablation: run the single-pass resolver and confirm `art-zeta` comes back `trusted/verified/ev-z1` where policy wants `quarantine/channel_exposure/ev-z1`, and `art-sigma` `denied/digest_mismatch/ev-s2` where policy wants `trusted/verified/ev-s1`. If a single pass gets both right, the recursion is decorative — abort. (c) Cold read: hand a fresh model *only* the shipped files and ask for the settled exposure instant. Anything other than `2026-01-05 08:00:00`, or any request for clarification, means the spec is underdetermined — abort. (d) Oracle run green, all 22 tests plus new ones, inside 900s with three variant builds. (e) Full 5-run difficulty check on both models. **Worst-model pass rate above 60% means abort and abandon** — do not relabel `task.toml`.

## 4. Honest probability of reaching MEDIUM: 10-15%.

You need the worst model failing 2 of 5 runs. D1's author pinned his hopes on two failure modes, and both have exact precedents in the current task that the models already handle perfectly:

- *"Model hardcodes a pass count instead of testing stability."* It doesn't do that for A-2026-03 today, and A-2026-03's prose is **terser** than the proposed A-2026-13. A model that correctly writes `while (growing)` from "repeating until the void set stops growing" will not hardcode three passes when handed "Repeat until a pass leaves the exposure set unchanged."
- *"Model drops the compromised-signer carve-out."* A-2026-05 already ships a directly analogous non-leaking carve-out, models implement it correctly, and there is a green test proving it.

So the concrete answer to "why is this different" is: it isn't. That is the whole finding. Seven mechanics have now been defeated 10/10, and the pattern across all seven is identical — every trap was *specified*, and these models transcribe specifications reliably. The difficulty surface of this task is reading comprehension over a well-written rule list, and that surface is saturated. The judges who suggested "target underspecification or conflicting sources instead" are pointing at the one axis with headroom, but it is closed to you here: your own instruction-sufficiency and determinacy constraints forbid it, and a task that discriminates by underspecification bounces on solvability, which is strictly worse than TRIVIAL.

## 5. What to do with it.

**The current build has no submission path, so "submit as-is" is not on the table.** Per `terminus-submission-hardening.mdc:34-37`, the diversity gate accepts MEDIUM or HARD only and bounces anything with worst-model pass rate above 60%; yours is 100%. `task.toml:6` currently claims `difficulty = "medium"` against a measured 1.0/1.0, and the same rules explicitly forbid relabeling to clear the gate (line 111) — the platform re-measures anyway. So the real choice is: harden successfully, or abandon. There is no honest-easy middle.

Abandon it as a submission candidate. Stop spending cycles on the policy layer.

What is worth salvaging is the engineering, which is genuinely good and cost most of the nine commits: the Java + H2 + amendment-log + bundled HTTP API scaffold, the variant-store harness in `helpers.py` that recomputes expected answers from any store rather than hardcoding a winner, the registry generator, and the clean 0.0-nop property. That scaffold is reusable and it is the expensive part. Retarget it at a task whose difficulty comes from somewhere other than reading a rule list — where the agent has to *discover* behavior by probing the running system, reconcile two sources that disagree, or debug a failure that only manifests under the real environment. Keep the environment, throw away the amendment stack.

If you want one last shot before abandoning, spend it on D1 and D1 only, run the protocol in section 3, and pre-commit to abandoning on an EASY result rather than opening a tenth cycle. But my recommendation is to skip that shot — at 10-15% it is not worth another cycle against a task that has already consumed nine.