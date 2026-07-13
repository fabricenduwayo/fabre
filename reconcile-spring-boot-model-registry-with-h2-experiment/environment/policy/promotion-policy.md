# Churn Model Promotion Policy

This document defines the rules the `reconcile-model-release` step applies when
deciding whether a candidate churn model is safe to promote to the `production`
alias. A promotion decision is made by evaluating every candidate model against
the gates below and selecting at most one winner. The policy is written so that
the promote/reject outcome is fully determined by the H2 experiment DB canonical
evidence together with the model-registry metadata — there is no discretionary
judgement, and the same inputs always produce the same manifest (no timestamps,
hostnames, or other run-dependent fields).

## Document control

Section 1.4 applies: where this document conflicts with
`/app/policy/promotion-policy-amendments.md`, the amendments govern.

### 1.4 Amendments

Authoritative corrections live in `/app/policy/promotion-policy-amendments.md`.
When the body and an amendment disagree, the amendment wins.

## Sources of truth

Two systems describe each model. They are canonical for different fields, and
they must not be treated interchangeably.

| Field | Canonical source |
| --- | --- |
| Candidate set and identity (id / name / version) | Registry API |
| Deployment aliases | Registry API |
| Validation AUC | Registry API |
| Validation accuracy | Registry API |
| Feature-hash lineage | H2 experiment DB (`feature_hash_lineage`) |
| Calibration status | H2 experiment DB (`calibration_status`) |

The registry API defines *which models are candidates*. Models that appear only
in the experiment DB (retired or never registered) are not candidates and are
ignored entirely: they are not evaluated, never promoted, and never listed in
`rejected` or `conflicts`, no matter how strong their recorded metrics are.

When the registry API and the H2 experiment DB disagree on validation metrics or
feature-hash lineage, record the disagreement under `conflicts` but evaluate
Gate 1 and the tie-break using the registry API's reported metrics when present.
The registry does not report calibration at all, so calibration is read
exclusively from H2.

## Evidence completeness — fail closed

A candidate is evaluated only against complete canonical evidence. If the H2
experiment DB has no `validation_metrics` row, no `calibration_status` row, or
no `feature_hash_lineage` row matching the candidate's registry-reported id and
version, the candidate is not eligible for promotion. It is rejected with the
reason code `missing_canonical_evidence`, its gates are not evaluated, and the
missing evidence is not recorded as a conflict (a conflict requires two values
that disagree; absence is not a value).

## Promotion gates

A model with complete evidence is eligible for promotion only if it passes all
three gates below, evaluated against the H2 canonical evidence for that model
and its registry-reported version.

### Gate 1 — Validation-metric thresholds

Compare the registry API's reported `metrics.auc` and `metrics.accuracy` for
the candidate against the Gate 1 floors below. Use the H2 `validation_metrics`
table only when the registry omits a metric.

| Metric | Requirement |
| --- | --- |
| AUC | must be greater than or equal to 0.80 |
| Accuracy | must be greater than or equal to 0.75 |

A model below either floor fails this gate. Reason code: `metric_threshold`.

### Gate 2 — Calibration

A model must be calibrated to be eligible for promotion. Calibration is read
from the H2 canonical `calibration_status.calibrated` flag: the model passes
this gate only when `calibrated` is `TRUE`.

An uncalibrated model (`calibrated = FALSE`) must not be promoted even if its
validation metrics pass Gate 1. Reason code: `uncalibrated`.

### Gate 3 — Feature-hash lineage consistency

The feature-hash reported by the registry API for the candidate must match an
H2 `feature_hash_lineage` row for that model id. Any historical row for the
model id is sufficient.

If they differ, the lineage is inconsistent and the model must not be promoted.
Reason code: `lineage_mismatch`.

## Promotion decision rule

1. Evaluate every candidate for evidence completeness, then against Gate 1,
   Gate 2, and Gate 3.
2. A candidate qualifies only if its evidence is complete and it passes all
   three gates.
3. If exactly one candidate qualifies, promote it.
4. If more than one candidate qualifies, apply the tie-break below and promote
   the single winner.
5. If no candidate qualifies, promote none — set `promoted` to `null`.

Every candidate that is not promoted must appear in `rejected`, annotated with
every reason code that applies to it:

| Reason code | Meaning |
| --- | --- |
| `metric_threshold` | canonical AUC or accuracy below the Gate 1 floors |
| `uncalibrated` | canonical `calibrated` flag is `FALSE` |
| `lineage_mismatch` | registry feature-hash differs from the canonical lineage row for that version |
| `missing_canonical_evidence` | no metrics, calibration, or version-matching lineage row in H2 |
| `lost_tiebreak` | passed every gate but another qualifier won the tie-break |

A candidate may fail more than one gate; all applicable codes are listed, and
no others. Reason codes are exact strings.

### Tie-break

When more than one candidate passes all gates, select the winner as follows:

1. Choose the candidate with the highest registry-reported AUC.
2. If two or more candidates are still tied on registry AUC, choose the one
   whose model id is lexicographically smallest.

This procedure always resolves to a single winner because model ids are unique.

## Decision manifest expectations

The manifest records:

- `promoted`: the registry id of the single promoted model, or `null` when no
  candidate passes all gates.
- `rejected`: every non-promoted candidate, keyed by registry id, with its
  reason code(s).
- `conflicts`: one entry per field where the registry API disagreed with the H2
  canonical value on an H2-canonical field, for candidates with a canonical row
  to compare against. The `field` values are exactly `auc`, `accuracy`, and
  `feature_hash`; each entry carries the registry value (`api_value`), the H2
  value (`db_value`), and `canonical_source` set to `h2`.

No gate beyond the three defined here is applied. The thresholds (AUC >= 0.80,
accuracy >= 0.75) are exact and are not rounded, relaxed, or supplemented.
