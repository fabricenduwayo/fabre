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

## A-2026-05 — amends Gate 1 run voiding

When a `validation_runs` row carries a non-null `supersedes_run_id`, the
referenced earlier run is void for operative-run selection under A-2026-04.
Voided runs are excluded before choosing the latest completed row. The
superseding row's own status still follows A-2026-04: a `superseded` row does
not become operative even when it is temporally latest.

## A-2026-06 — governance waiver lifecycle

Promotion waivers are version- and reason-scoped. Evaluate `promotion_waivers`
and `waiver_events` as of the single `release_context.decision_at`; future
events do not exist for this decision. A waiver is active only when its latest
valid event at or before that time is a `grant`, and the decision time is in
its half-open `[valid_from, valid_until)` interval.

An unpaired `grant` is valid only for a waiver with no `replaces_waiver_id`;
an unpaired `revoke` is valid for any waiver. A paired event is valid only as
part of one reciprocal two-event replacement transaction: one event revokes
the predecessor, the other grants the successor, both name each other in
`paired_event_id`, both have the same `occurred_at`, the successor names the
predecessor in `replaces_waiver_id`, and both waivers have the same model id,
model version, and reason code. Ignore both sides of every malformed pair.
Order valid events by `occurred_at`, then lexicographically by `event_id`.
Revoking an active replacement later does not revive its revoked predecessor.

After evaluating the ordinary policy gates, an active waiver suppresses only
the matching raw `metric_threshold`, `uncalibrated`, or `lineage_mismatch`
failure for the same candidate id and version. It cannot suppress
`missing_canonical_evidence` or `lost_tiebreak`. If multiple active waivers
cover one raw failure, select the one with the latest grant event, breaking a
tie by lexicographically greatest waiver id. Add each selected, suppressing
grant to `applied_waivers` with `waiver_id`, `model`, `model_version`, and
`reason`; do not report inactive, malformed, expired, future, or irrelevant
waivers.

## A-2026-07 — amends Gate 2 calibration source

The `calibration_status` table is a dashboard snapshot only. Gate 2 replays
`calibration_events` per model id through `release_context.decision_at`: start
from the snapshot flag, apply every event with `occurred_at` at or before
decision time in ascending `occurred_at` order (tie-break by lexicographic
`event_id`), and let each `calibrate` or `uncalibrate` event overwrite the
effective flag. When no events exist for a model, the snapshot stands.

## A-2026-08 — amends Gate 1 transitive voiding

Extends A-2026-05. After collecting every run voided because another row's
`supersedes_run_id` references it, also void any run whose `run_id` equals a
voided run's `supersedes_run_id`, repeating until the void set stops growing.
Only then apply A-2026-04 to choose the operative completed row.

## A-2026-09 — amends Gate 2 same-timestamp ordering

When two or more `calibration_events` for the same model share the same
`occurred_at`, apply them in ascending lexicographic `event_id` order within
that timestamp before continuing to later timestamps.

## A-2026-10 — amends A-2026-06 waiver suppression timing

An active waiver may suppress a raw gate failure only when its grant event's
`occurred_at` is strictly before the operative validation run's `captured_at`
from A-2026-04 through A-2026-08. Waivers granted on or after that instant
cannot suppress failures derived from that operative run and must not appear in
`applied_waivers` for it.

## A-2026-11 — amends A-2026-06 waiver approval quorum

A waiver may suppress a raw failure only when it has an effective approval
quorum for its **latest valid grant epoch**. Replay `waiver_approval_events`
through `release_context.decision_at`, ordered by `occurred_at` and then
lexicographic `event_id`. Ignore approval events that do not sort strictly
after the active waiver's latest valid grant event. For each
`(waiver_id, reviewer_id, reviewer_role)`, only the latest remaining event is
effective; `withdraw` removes that reviewer's approval for that role.

Quorum requires an effective `approve` from role `risk` and an effective
`approve` from role `model_owner`, with **different reviewer ids**. A
replacement waiver never inherits its predecessor's approvals, and a waiver
that is revoked and later granted again cannot reuse approvals from an earlier
grant epoch.

For each raw failure, first discard active waivers that fail this quorum or
A-2026-10's operative-run timing rule. Select the suppressing waiver from the
remaining eligible set by A-2026-06's latest-grant and waiver-id tie-break. This
means a newer active but under-approved waiver does not shadow an older active
waiver that is fully eligible.

## A-2026-12 — amends A-2026-06 / A-2026-10 metric suppression anchoring

`promotion_waivers` may carry an optional `anchors_run_id` referencing
`validation_runs.run_id`. When set, a waiver may suppress only
`metric_threshold` for its model id and version, and only when all of the
following hold:

1. The referenced run exists and its `model_id` equals the waiver's model id.
2. After A-2026-04 through A-2026-08, that run is exactly the operative
   completed validation run for the model at `release_context.decision_at`.
3. The waiver's latest valid grant event's `occurred_at` is strictly before
   that run's `captured_at` (replacing A-2026-10's operative-run reference
   for anchored waivers).
4. A-2026-11 approval quorum is satisfied for the latest grant epoch.

When `anchors_run_id` is null, A-2026-10 continues to use the operative run
from A-2026-04 through A-2026-08.

A reciprocal replacement pair is malformed unless both waivers carry the
same `anchors_run_id` (including both null). A voided or non-operative
anchored run does not fall back to an unanchored waiver for the same raw
failure unless that other waiver independently passes A-2026-06, A-2026-10,
and A-2026-11.
