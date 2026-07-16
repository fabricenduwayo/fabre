# Churn Model Promotion Policy — Amendments

These amendments override `/app/policy/promotion-policy.md` wherever they
conflict (see body section 1.4).

## A-2026-01 — amends Sources of truth / Gate 1

Effective validation metrics are canonical from the H2 experiment DB
(`validation_runs`, subject to A-2026-04 run selection), not the registry API.

## A-2026-02 — amends Gate 3

Feature-hash lineage is version-scoped. Select the `feature_hash_lineage` row
whose `model_version` equals the candidate's registry-reported version. Rows for
other versions of the same model id do not apply.

## A-2026-03 — amends Tie-break

Tie-break ranks qualifiers by highest H2 canonical AUC from the operative
validation run (see A-2026-04), then lexicographically smallest model id.
Registry-reported metrics are not used for ranking.

## A-2026-04 — amends Gate 1 metric selection

`validation_runs` may contain multiple rows per model. Gate 1 uses the metrics
from the temporally latest row whose `status` is exactly `completed`. Rows with
any other status are ignored even when they have a later `captured_at`. When
the registry and H2 disagree on AUC or accuracy for that operative run, the H2
value governs gate evaluation and the disagreement is recorded under `conflicts`
with `canonical_source` set to `h2`.
