# Harbor Terminal Trivia Scoring Standard

Version 2026-03. This document governs ledger replay for match night audits.

## 1. Governance

### 1.1 Scope

These controls apply to replay workers that ingest rows from a match ledger CSV into
the Harbor referee API.

### 1.2 Amendments

Appendix G lists authoritative amendments. Where a body control and an amendment
conflict, the amendment governs. Appendix H (amendments H-2026-01 through
H-2026-40) governs the stewards' review reconciliation; every amendment in it
applies.

### 1.3 Ledger ordering

**TR-ORDER-SEQ** — Rows must be applied in ascending `seq` order. The `ts` column is
informational only and must not reorder replay.

## 2. Event controls

Each CSV row has columns `seq`, `ts`, `kind`, `question`, `player`, `payload` (JSON).

Supported `kind` values: `open`, `lock`, `buzzer`, `answer`, `penalty`, `mod_override`.

### TR-OPEN

`open` marks a question as open for buzzers. Payload must be `{}`.

### TR-LOCK

`lock` marks a question locked. No buzzer or answer credit may be granted while locked.

### TR-BUZZER

`buzzer` awards the right to answer for an open, unlocked question. The first buzzer
row per question wins. Additional buzzer rows for the same question are ignored (no
penalty, no reassignment).

### TR-ANSWER

`answer` applies only when:

- the question is open and not locked;
- the answering `player` is the current buzzer holder for that question;
- the question has not already been answered.

Payload `{"correct": true}` awards **+10** points and increments the player's correct
count. Payload `{"correct": false}` applies **-5** points. The question becomes
answered after either outcome.

### TR-PENALTY

`penalty` subtracts points from `player`. Payload `{"points": N}`; when omitted,
**N = 5**.

### TR-MOD-OVERRIDE

`mod_override` payload field `action` controls behavior:

| action | payload | effect |
|--------|---------|--------|
| `award` | `{"points": N}` | add N points to `player` |
| `deduct` | `{"points": N}` | subtract N points from `player` |
| `void_buzzer` | `{}` | clear the buzzer holder for `question` |
| `reassign` | `{"player": "<id>"}` | set buzzer holder to the named player on an open, unlocked, unanswered question |

## 3. API ingest

### TR-IDEMPOTENCY

Every ingest POST must include header `X-Idempotency-Key` set to
`match-night-{seq}` for that ledger row.

Replaying the same key with the same body is a no-op. Replaying the same key with a
different body returns `409`.

### TR-INGEST-BODY

The POST body must be the ledger row as JSON with keys `seq`, `ts`, `kind`,
`question`, `player`, and `payload`. Use JSON `null` for empty `question` or
`player` cells. An empty `payload` cell must be `{}`, not `null`. Omitting a key
or changing `ts` counts as a different body for idempotency purposes. Serialize
with default JSON key order and spacing (do not sort keys or use compact
separators); the referee stores the request body bytes verbatim for idempotency
comparison.

### TR-RETRY-503

The referee may return `503` for transient overload. Workers must retry with
exponential backoff (starting at 50 ms, cap 800 ms) until the ingest succeeds or a
non-retryable status is returned.

## 4. Standings transcript

After all rows are ingested and the stewards' review has been reconciled
(Appendix H), write the **official** standings to a text file with this exact shape
(no blank lines between rows; the file must end with a newline after the last player
row):

```
STANDINGS match-night-2026-03-15
rank player score correct first_buzz_seq
<rank> <player> <score> <correct> <first_buzz_seq>
...
```

Sort players for output using **TR-TIEBREAK** (section 5). `first_buzz_seq` is the
lowest `seq` at which that player won a buzzer during the match, or `-` if they never
won a buzzer.

## 5. Tie-breaking

### TR-TIEBREAK

When ordering the transcript, sort players by:

1. higher `score` descending;
2. higher `correct` count descending;
3. lower `first_buzz_seq` ascending (earlier buzzer wins);
4. `player` id ascending (stable final tie).

## Appendix G — Authoritative amendments

### G-2026-03 — Locked questions

Amends TR-BUZZER and TR-ANSWER. While a question is locked, buzzer and answer rows
must not change any player's score or correct count. The referee returns `422` for
such ingests; workers must still send them (with idempotency keys) but must not
locally invent points.

### G-2026-04 — Duplicate buzzers

Amends TR-BUZZER. Duplicate buzzer rows for the same question are silently ignored.
Workers must not treat them as penalties or reassignments.

### G-2026-05 — Standings source

Amends section 4. The per-player `score`, `correct`, and `first_buzz_seq` totals must
come from `GET /v1/standings` after all ledger rows are ingested; workers must not
recompute them from the CSV. That endpoint is **provisional** (`status:
"provisional"`): it reflects only the ingested ledger and not the stewards' review.
The official transcript is the provisional standings reconciled with the rulings feed
per Appendix H, then re-ranked with TR-TIEBREAK.

## Appendix H — Stewards' review reconciliation

### H-2026-01 — Rulings feed

`GET /v1/rulings` returns the stewards' review as a list of ruling objects, each with
`ruling_seq`, `incident`, `op` (`issue`, `amend`, `rescind`, or `reinstate`),
`player`, `delta` (a signed integer score adjustment; `0` for `rescind`), and
optional `correct_delta` (a signed integer adjustment to the player's `correct`
count). A `reinstate` ruling carries only `ruling_seq`, `incident`, and `op`
(H-2026-25). `issued_at` is informational and must not be used for ordering.

### H-2026-02 — Incident precedence

Replay the rulings in ascending `ruling_seq`, keyed by `incident`: `issue` and `amend`
set that incident's effective `(player, delta, correct_delta)`, a later one for the
same incident supersedes an earlier one (including replacing the target `player`, not
just the `delta`), and `rescind` clears the incident so it contributes nothing. An
incident whose latest op is `rescind`, or that only ever appears with `rescind`, has
no effect. When an `amend` omits `correct_delta`, the incident's `correct_delta`
resets to **0**.

### H-2026-03 — Net adjustment

For each incident that still has an effective `(player, delta, correct_delta)` after
replay, add `delta` to that player's provisional `score` and `correct_delta` to their
`correct` count. `first_buzz_seq` is not changed by rulings. When a ruling omits
`correct_delta`, treat it as **0**. A ruling whose `player` did not participate in
the match (never appears in the provisional standings) is void and must not introduce
a new player.

### H-2026-04 — Score and correct floors

After all surviving **primary** adjustments (those without `applies_after_floor`) are
applied, clamp each player's `score` and `correct` to a minimum of **0** before any
post-floor rulings (H-2026-07) and before re-ranking with TR-TIEBREAK for the
official transcript.

### H-2026-06 — Incident dependency

A ruling may include optional `requires_incident` naming another incident id. The
ruling is **void** unless that incident still has an effective entry in the incident
map **after** all lower `ruling_seq` entries have been replayed (i.e. the dependency
was not rescinded). Void rulings must not update the incident map and must not change
any score or correct count.

### H-2026-07 — Post-floor adjustments

A ruling may include `"applies_after_floor": true`. Defer such rulings until after
H-2026-04 has clamped every participant. Then apply each deferred incident's surviving
adjustment in ascending `ruling_seq`, including incidents that survive only as a
frozen deferred snapshot (H-2026-19) even when they no longer appear in the
effective map at replay end. Merge snapshotted and ordinary deferred incidents into
one pass ordered by ascending `ruling_seq`. For each step, add `delta` and
`correct_delta` to the named participant (if they appear in the provisional
standings), and clamp each adjusted `score` and `correct` to **0** again before
re-ranking with TR-TIEBREAK.

### H-2026-08 — Deferred dependency snapshot

For a deferred ruling (`applies_after_floor: true`) that carries `requires_incident`,
evaluate that dependency when the ruling is **recorded** during the ascending
`ruling_seq` replay. If the dependency was active at that moment, the deferred ruling
remains eligible for the post-floor pass even when a **later** ruling rescinds the
dependency incident before floor application. Rescinding the dependency after the
deferred ruling was accepted does not retroactively void it.

### H-2026-09 — Sequential primary floor checkpoints

Surviving **primary** adjustments (those without `applies_after_floor`) must be applied
in ascending `ruling_seq` order — not by incident id or map insertion order. After
each primary adjustment is applied to a participant, clamp that participant's `score`
and `correct` to a minimum of **0** before the next primary ruling runs. H-2026-04's
global clamp still runs after all primaries finish; the post-floor pass (H-2026-07) is
unchanged.

### H-2026-10 — Primary dependency still active at replay end

After the ascending `ruling_seq` replay finishes building the incident map, a surviving
**primary** ruling (one without `applies_after_floor`) whose `requires_incident` names
another incident is **void** unless that dependency incident is still present in the
effective map. A ruling that was eligible when recorded but whose dependency is later
`rescind`ed before replay completes must not run in the primary pass. Deferred
`applies_after_floor` rulings are unchanged: H-2026-08 still snapshots dependency
eligibility at record time and does not re-check the dependency during the post-floor
pass.

### H-2026-11 — Amend omission resets delta

When an `amend` omits `delta`, the incident's effective `delta` resets to **0** (the
same omission rule H-2026-02 already applies to `correct_delta`).

### H-2026-12 — Paired incident rescind cascade

A ruling may include optional `paired_incident` naming another incident id. A ruling
with `paired_incident` is **void** unless that named incident is active in the map when
the ruling is recorded (the same moment as H-2026-06). When accepted, store the link
on the incident's effective entry; an `amend` that omits `paired_incident` clears any
stored link **and drops any frozen deferred snapshot (H-2026-19) held for that
incident** — when such an amend keeps `applies_after_floor: true`, the incident stays
in the deferred pass as an ordinary, unsnapshotted deferred ruling. When a `rescind`
clears incident X, also clear every other incident Y still in the map whose effective
entry has `paired_incident` equal to X (and remove Y from the deferred pass list if
present) before continuing replay.

### H-2026-13 — Amend omission resets deferred flag and dependency

When an `amend` omits `applies_after_floor`, the incident's effective
`applies_after_floor` resets to **false** (primary). When an `amend` omits
`requires_incident`, clear any stored dependency link. A ruling demoted from deferred
to primary by such an amend is subject to H-2026-10 at replay end, not H-2026-08's
record-time snapshot.

### H-2026-14 — Transitive primary dependency at replay end

Extends H-2026-10. After the ascending `ruling_seq` replay finishes, a surviving
**primary** ruling whose `requires_incident` names another incident is void unless
every link in that dependency chain is still present in the effective map — not only
the direct parent. Example: if `INC-B` requires `INC-A`, `INC-C` requires `INC-B`, and
`INC-A` was rescinded before replay completes, both `INC-B` and `INC-C` are void at
primary apply time even though `INC-B` may still appear in the map when `INC-C` is
evaluated. Deferred `applies_after_floor` rulings are unchanged: H-2026-08 still
snapshots only the direct `requires_incident` at record time.

### H-2026-15 — Transitive paired_incident cascade on rescind

Extends H-2026-12. When a `rescind` clears incident X, remove every other incident
whose effective entry has `paired_incident` equal to X, then repeat until no more
removals — any incident paired to a removed incident is also cleared (and dropped
from the deferred pass list if present) before continuing replay. Example: if
`INC-B` has `paired_incident: INC-A`, `INC-C` has `paired_incident: INC-B`, and
`INC-A` is rescinded, both `INC-B` and `INC-C` are cleared even though `INC-C`
does not point directly at `INC-A`.

### H-2026-16 — Rescinded incidents stay tainted

Extends H-2026-10 and H-2026-14. During the ascending `ruling_seq` replay, track
every incident id that was `rescind`ed at least once. After replay finishes, a
surviving **primary** ruling is void if any id in its `requires_incident` chain
appears in that set — even when a later `issue` or `amend` re-establishes an
effective entry for the same incident id. Re-issuing an incident after rescind does
not revive primaries that depend on it. The taint walk follows `requires_incident`
links only; it must never continue through `paired_incident` links (H-2026-17 covers
the ruling's own direct paired parent and nothing further). Deferred
`applies_after_floor` rulings are unchanged: H-2026-08 still snapshots only the
direct dependency at record time.

### H-2026-17 — Rescinded paired parents stay tainted

Extends H-2026-12 and H-2026-16. During the ascending `ruling_seq` replay, use
the same set of incident ids that were `rescind`ed at least once (H-2026-16).
After replay finishes, a surviving **primary** ruling is void if its
`paired_incident` names an id in that set — even when that parent was re-issued
and is active again in the effective map. Re-issuing a paired parent after rescind
does not revive primaries that point at it. This check is **direct-only**: compare
the ruling's own `paired_incident` value against the set. Do not walk chains of
paired incidents, and do not extend the H-2026-16 requires-chain walk through
paired links. Deferred `applies_after_floor` rulings are unchanged.

### H-2026-18 — Amend omission retains player

Extends H-2026-02. When an `amend` omits `player`, the incident's effective
`player` remains the previous value from the prior `issue` or `amend` for that
incident.

### H-2026-19 — Deferred paired snapshot

Extends H-2026-08 and H-2026-12. For a deferred ruling (`applies_after_floor:
true`) that carries `paired_incident`, evaluate that paired parent when the ruling
is **recorded** during the ascending `ruling_seq` replay. If the paired parent
was active in the effective map at that moment, store a frozen deferred snapshot
for that incident and keep it eligible for the post-floor pass even when a
**later** ruling rescinds the paired parent before floor application. Do not
store a frozen snapshot for deferred rulings that lack `paired_incident`, or when
the paired parent was not active at record time. Rescinding the paired parent
after the deferred ruling was accepted does not retroactively remove a
snapshotted deferred ruling from the post-floor pass (H-2026-12's paired cascade
still clears the incident from the map but must not drop a snapshotted deferred
ruling). A `rescind` that directly names the snapshotted incident itself removes
the frozen snapshot along with the effective entry — only removals via the paired
cascade preserve the snapshot. An `amend` that omits `applies_after_floor`
demotes the incident to primary per H-2026-13 and clears any deferred paired
snapshot for that incident.

### H-2026-20 — Frozen deferred snapshot sync on amend

Extends H-2026-19. When an incident already has a frozen deferred snapshot entry
and a later `amend` supersedes that incident's effective entry, copy the amended
`player`, `delta`, and `correct_delta` into the frozen snapshot before the
post-floor pass. The snapshotted post-floor adjustment must use the latest amended
values even when the paired parent is later rescinded and the incident is cleared
from the effective map. This sync applies only when the amend itself still carries
an active `paired_incident`; an amend that omits `paired_incident` drops the
snapshot entirely per H-2026-12.

### H-2026-21 — Supersede clears without rescind taint

A ruling may include optional `supersedes_incident` naming another incident id that
is present in the effective map when the ruling is recorded. Before storing the
new entry, remove the named incident from the map and deferred pass list, drop any
frozen snapshot keyed to that incident id, and run the paired cascade from
H-2026-15 on the removed id. Do **not** add the superseded id to the
ever-rescinded set from H-2026-16. A later `issue` or `amend` may establish a new
effective entry for the same incident id; primaries whose `requires_incident` chain
reaches that id are evaluated at replay end against the map, not against the
supersede history. An `amend` that omits `supersedes_incident` does not restore a
previously superseded incident.

### H-2026-22 — Demotion clears paired frozen snapshots

When an `amend` omits `applies_after_floor` (H-2026-13 demotion to primary),
remove from `frozen_deferred` every incident whose snapshotted entry has
`paired_incident` equal to the demoted incident id. The demoted incident itself
follows H-2026-10 at replay end.

### H-2026-23 — Deferred score ceiling

A deferred ruling (`applies_after_floor: true`) may include optional integer
`score_ceiling`. During the post-floor pass, before adding `delta` to the named
player, cap the applied score change so the player's `score` after the step does
not exceed `score_ceiling`. If the player is already at or above the ceiling,
apply **0** for that step's score change. `correct_delta` is unchanged. An
`amend` that omits `score_ceiling` clears any ceiling on the incident. When
H-2026-20 syncs a frozen deferred snapshot on amend, copy `score_ceiling` into
the snapshot as well.

### H-2026-24 — Mutex at record time

A ruling may include optional `mutex_incident` naming another incident id. When an
`issue` or `amend` is recorded during the ascending `ruling_seq` replay, the
ruling is **void** if `mutex_incident` names an incident that is present in the
effective map at that moment. Void mutex rulings must not update the incident map.
An `amend` that omits `mutex_incident` clears any mutex on the incident.

### H-2026-25 — Reinstate restores the pre-rescind entry

New op `reinstate`, carrying only `ruling_seq`, `incident`, and `op`. When a
`rescind` **directly names** an incident and clears its effective entry, retain a
copy of that entry (the rescind snapshot). A later `reinstate` for the incident:

- is a **no-op** when the incident currently has an effective entry, or when no
  rescind snapshot exists. An incident that was never directly rescinded has no
  snapshot. Removal via the paired cascade or via `supersedes_incident` also
  **deletes** any rescind snapshot held for the removed incident, so such
  incidents cannot be reinstated until directly rescinded again;
- otherwise restores the snapshot as the incident's effective entry with
  `ruling_seq` set to the reinstate ruling's own seq. When the incident was
  directly rescinded more than once, the snapshot from the **most recent** direct
  rescind wins — earlier lifetimes of the incident are not restored.

Reinstate does **not** remove the incident id from the ever-rescinded set
(H-2026-16 / H-2026-17): primaries whose `requires_incident` chain reaches the id,
or whose `paired_incident` names it, stay void, while the reinstated incident's
own adjustment applies normally. Incidents cleared by the paired cascade of the
original rescind are not restored by reinstating the parent.

### H-2026-26 — Reinstated deferred rulings

When the restored entry has `applies_after_floor: true`, the incident rejoins the
deferred pass ordered by the reinstate ruling's `ruling_seq`. Reinstate never
creates or restores a frozen paired snapshot (H-2026-19), even when the restored
entry carries `paired_incident`. Reinstate does not re-evaluate
`requires_incident`, `paired_incident`, or `mutex_incident` at reinstate time;
primary eligibility is still decided at replay end per H-2026-10/14/16/17.

### H-2026-27 — Primary max score after cap

A surviving **primary** ruling may include optional integer `max_score_after`.
During the primary pass, after adding `delta` to the named participant and before
the per-step floor clamp from H-2026-09, cap that participant's `score` to
`max_score_after` when it would exceed the limit — discard only the excess from
this step. `correct_delta` is applied in full before the cap. An `amend` that
omits `max_score_after` clears any cap on the incident. When H-2026-20 syncs a
frozen deferred snapshot, copy `max_score_after` into the snapshot even though
the cap itself applies only in the primary pass.

### H-2026-28 — Offset player transfer

A surviving **primary** ruling may include optional `offset_player` naming another
participant in the provisional standings. During the primary pass, after applying
`delta`, any `max_score_after` cap from H-2026-27 on the same ruling, and
`correct_delta` to the incident's `player`, subtract from `offset_player`'s
`score` the **applied score change** to `player` in that step (after the cap, not
the nominal `delta`). Only `score` moves; `correct` is unchanged on the offset
target. Apply the offset before the per-step floor checkpoint for both
participants. An `amend` that omits `offset_player` clears any offset. At record
time, the **entire** ruling is **void** when `offset_player` is absent from the
provisional standings or equals the incident's `player` — drop the incident with
no `delta`, `correct_delta`, or offset transfer applied.

### H-2026-29 — Deferred correct ceiling

A deferred ruling (`applies_after_floor: true`) may include optional integer
`correct_ceiling`. During the post-floor pass, before adding `correct_delta` to
the named participant, cap the applied correct change so the participant's
`correct` after the step does not exceed `correct_ceiling`. If the participant is
already at or above the ceiling, apply **0** for that step's correct change.
`delta` / `score_ceiling` handling is unchanged. An `amend` that omits
`correct_ceiling` clears any ceiling on the incident. When H-2026-20 syncs a
frozen deferred snapshot, copy `correct_ceiling` into the snapshot as well.

### H-2026-30 — Deferred offset before ceiling

Extends H-2026-23 and H-2026-28. For a deferred ruling (`applies_after_floor:
true`) that carries both `score_ceiling` and `offset_player`, subtract the full
nominal `delta` from `offset_player` **before** computing `score_ceiling`
headroom and applying the score change to `player`. Record-time void rules for
`offset_player` match H-2026-28. When only one of the two fields is present,
behavior is unchanged from H-2026-23/H-2026-28. When H-2026-20 syncs a frozen
deferred snapshot, copy `offset_player` into the snapshot as well.

### H-2026-31 — Conditional partial primary offset

Extends H-2026-27 and H-2026-28. A surviving **primary** ruling may include
optional integer `offset_min_score`. During the primary pass, after applying
`delta`, `correct_delta`, and any `max_score_after` cap, compare the
beneficiary's score **before** the per-step floor checkpoint to
`offset_min_score`. When that score is **strictly below** `offset_min_score`,
subtract only `applied // 2` (floor division) from `offset_player` instead of
the full applied amount; otherwise subtract the full applied amount. An
`amend` that omits `offset_min_score` clears the threshold. When H-2026-20
syncs a frozen deferred snapshot, copy `offset_min_score` into the snapshot
even though the threshold applies only in the primary pass.

### H-2026-32 — Offset solvency cap

Extends H-2026-28, H-2026-30, and H-2026-31. Whenever a ruling subtracts a
positive amount from `offset_player`, cap the transfer at that participant's
**current score before the subtraction** (never below **0** collected). The
beneficiary still receives the full score change computed by the ruling; only
the offset debit is trimmed. Negative transfers (when the applied score change
is negative and the offset target gains points) are unchanged. When H-2026-20
syncs a frozen deferred snapshot, no extra field is needed — solvency applies
whenever an offset runs.

### H-2026-33 — Deferred offset without score ceiling

Extends H-2026-28 and H-2026-30. For a deferred ruling
(`applies_after_floor: true`) that carries `offset_player` but omits
`score_ceiling`, subtract the full nominal `delta` from `offset_player`
(subject to H-2026-32 solvency) **before** applying the score change to
`player`. Record-time void rules for `offset_player` match H-2026-28. When
only one of `offset_player` or `score_ceiling` is present, behavior is
unchanged from H-2026-23 or H-2026-28/32 respectively. When both are present,
H-2026-30 still runs the offset before ceiling headroom. When H-2026-20 syncs
a frozen deferred snapshot, copy `offset_player` into the snapshot as today.

### H-2026-34 — Blocked score zeroes paired correct credit

Extends H-2026-23 and H-2026-29. During the post-floor pass, when a deferred
ruling carries **both** `score_ceiling` and `correct_ceiling`, apply the score
path first (offset, solvency, and score ceiling per H-2026-30/32/33). If the
**applied score change** for that step is **0** because the beneficiary is
already at or above `score_ceiling`, treat `correct_delta` as **0** for that
step as well — do not apply `correct_ceiling` headroom when the score credit
was fully blocked. This applies even when the ruling's nominal `delta` is **0**.

### H-2026-35 — Deferred offset minimum score

Extends H-2026-31 and H-2026-33. A deferred ruling (`applies_after_floor:
true`) may include optional integer `offset_min_score`. During the post-floor
pass, immediately before the offset debit to `offset_player`, compare the
beneficiary's `score` (before that step's score credit) to
`offset_min_score`. When the score is **strictly below** the threshold, debit
only `delta // 2` (floor division) from `offset_player` instead of the full
nominal `delta`, then apply H-2026-32 solvency to that halved debit. The
beneficiary still receives the full score change computed by H-2026-23/30
(subject to `score_ceiling`). An `amend` that omits `offset_min_score` clears
the threshold. When H-2026-20 syncs a frozen deferred snapshot, copy
`offset_min_score` into the snapshot as well.

### H-2026-36 — Frozen snapshot amend sync for offset fields

Extends H-2026-20. When an incident already has a frozen deferred snapshot
(H-2026-19) and a later `amend` supersedes that incident while still carrying
an active `paired_incident`, copy the amended `offset_player`,
`offset_min_score`, `score_ceiling`, `correct_ceiling`, `delta`, `correct_delta`,
and `player` into the frozen snapshot **even when** the paired parent is no
longer in the effective map. The post-floor pass must use those synced offset
fields from the snapshot, not stale values from the earlier `issue`.

### H-2026-37 — Deferred offset refund on ceiling block

Extends H-2026-30 and H-2026-23. During the post-floor pass, when a deferred
ruling carries both `offset_player` and `score_ceiling`, run the offset debit
first per H-2026-30/35/32, then compute `score_applied` per H-2026-23. If
`score_applied` is **0** because the beneficiary is already at or above
`score_ceiling` (not because `delta` itself is **0**), **refund** the offset
debit — add back to `offset_player` exactly what was subtracted in that step
(after solvency trimming). When `score_ceiling` is absent, or when some score
credit is applied, the offset debit stands. When H-2026-20 syncs a frozen
deferred snapshot, no extra field is needed — the refund rule applies whenever
the post-floor step runs.

### H-2026-38 — Offset correct player

A surviving **primary** or deferred ruling may include optional
`offset_correct_player` naming another participant in the provisional
standings. After applying `correct_delta` (including any `correct_ceiling` cap
on deferred rulings), subtract the **applied correct change** from
`offset_correct_player`'s `correct` count. Only `correct` moves; `score` is
unchanged on the offset target. Apply the correct offset after the score path
for deferred rulings (including any H-2026-37 refund). At record time, the
ruling is **void** when `offset_correct_player` is absent from the provisional
standings or equals the incident's `player`. An `amend` that omits
`offset_correct_player` clears any correct offset. When H-2026-20 syncs a
frozen deferred snapshot, copy `offset_correct_player` into the snapshot as
well.

### H-2026-39 — Correct offset solvency cap

Extends H-2026-38. Whenever a ruling subtracts a positive amount from
`offset_correct_player`'s `correct` count, cap the debit at that participant's
**current correct count before the subtraction** (never below **0**
collected). The beneficiary still receives the full applied correct change;
only the correct offset debit is trimmed.

### H-2026-40 — Blocked correct cancels correct offset

Extends H-2026-34 and H-2026-38. During the post-floor pass, when a deferred
ruling carries both `score_ceiling` and `correct_ceiling` and H-2026-34 forces
`correct_delta` to **0** because score credit was fully blocked, **refund** any
`offset_correct_player` debit made in that step — add back exactly what was
subtracted (after H-2026-39 solvency trimming). When some correct credit is
applied, the correct offset debit stands.
