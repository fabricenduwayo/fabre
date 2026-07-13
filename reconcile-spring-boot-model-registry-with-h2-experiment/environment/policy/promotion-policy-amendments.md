# Churn Model Promotion Policy — Amendments

These amendments override `/app/policy/promotion-policy.md` wherever they
conflict (see body section 1.4).

## A-2026-01 — amends Sources of truth / Gate 1

Effective validation metrics are canonical from the H2 experiment DB
(`validation_metrics`), not the registry API. When the registry and H2 disagree
on AUC, accuracy, or feature-hash lineage, the H2 value governs gate evaluation
and every disagreement is recorded under `conflicts` with `canonical_source`
set to `h2`.

## A-2026-02 — amends Gate 3

Feature-hash lineage is version-scoped. Select the `feature_hash_lineage` row
whose `model_version` equals the candidate's registry-reported version. Rows for
other versions of the same model id do not apply.

## A-2026-03 — amends Tie-break

Tie-break ranks qualifiers by highest H2 canonical AUC from `validation_metrics`,
then lexicographically smallest model id. Registry-reported metrics are not used
for ranking.
