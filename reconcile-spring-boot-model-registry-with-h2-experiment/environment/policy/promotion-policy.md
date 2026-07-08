# Churn Model Promotion Policy

This document defines the rules the `reconcile-model-release` step applies when
deciding whether a candidate churn model is safe to promote to the `production`
alias. A promotion decision is made by evaluating every candidate model against
the gates below and selecting at most one winner. The policy is written so that
the promote/reject outcome is fully determined by the H2 experiment DB canonical
evidence together with the model-registry metadata — there is no discretionary
judgement, and the same inputs always produce the same manifest (no timestamps,
hostnames, or other run-dependent fields).

## Sources of truth

Two systems describe each model. They are canonical for different fields, and
they must not be treated interchangeably.

| Field | Canonical source |
| --- | --- |
| Candidate set and identity (id / name / version) | Registry API |
| Deployment aliases | Registry API |
| Validation AUC | H2 experiment DB (`validation_metrics`) |
| Validation accuracy | H2 experiment DB (`validation_metrics`) |
| Feature-hash lineage | H2 experiment DB (`feature_hash_lineage`) |
| Calibration status | H2 experiment DB (`calibration_status`) |

The registry API defines *which models are candidates*. Models that appear only
in the experiment DB (retired or never registered) are not candidates and are
ignored entirely: they are not evaluated, never promoted, and never listed in
`rejected` or `conflicts`, no matter how strong their recorded metrics are.

When the registry API and the H2 experiment DB disagree on a field that this
table marks canonical to H2 (AUC, accuracy, or feature-hash lineage), the H2
value is authoritative and the registry value is ignored for gate evaluation.
Every such disagreement must be recorded in the decision manifest under
`conflicts` (see below). The registry does not report calibration at all, so
calibration can never conflict; it is read exclusively from H2.

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

Both thresholds must hold, evaluated against the H2 canonical
`validation_metrics`:

| Metric | Requirement |
| --- | --- |
| AUC | must be greater than or equal to 0.80 |
| Accuracy | must be greater than or equal to 0.75 |

A model whose canonical AUC is below 0.80, or whose canonical accuracy is below
0.75, fails this gate. Reason code: `metric_threshold`.

### Gate 2 — Calibration

A model must be calibrated to be eligible for promotion. Calibration is read
from the H2 canonical `calibration_status.calibrated` flag: the model passes
this gate only when `calibrated` is `TRUE`.

An uncalibrated model (`calibrated = FALSE`) must not be promoted even if its
validation metrics pass Gate 1. Reason code: `uncalibrated`.

### Gate 3 — Feature-hash lineage consistency

The feature-hash reported by the registry API for the candidate must match the
H2 canonical `feature_hash_lineage` row for that model id **and** the
registry-reported version. The lineage table is historical — it keeps one row
per (model, version) that ever shipped — so the comparison must select the row
whose `model_version` equals the candidate's registry-reported version, not
just any row for that model id. If the two hashes match, the lineage is
consistent and the model passes this gate. If they differ, the lineage is
inconsistent and the model must not be promoted. Reason code:
`lineage_mismatch`.

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

1. Choose the candidate with the highest canonical AUC (from the H2
   `validation_metrics`).
2. If two or more candidates are still tied on canonical AUC, choose the one
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
