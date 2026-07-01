# Harbor Terminal Trivia Scoring Standard

Version 2026-03. This document governs ledger replay for match night audits.

## 1. Governance

### 1.1 Scope

These controls apply to replay workers that ingest rows from a match ledger CSV into
the Harbor referee API.

### 1.2 Amendments

Appendix G lists authoritative amendments. Where a body control and an amendment
conflict, the amendment governs.

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
`ruling_seq`, `incident`, `op` (`issue`, `amend`, or `rescind`), `player`, `delta`
(a signed integer score adjustment; `0` for `rescind`), and optional `correct_delta`
(a signed integer adjustment to the player's `correct` count). `issued_at` is
informational and must not be used for ordering.

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
adjustment in ascending `ruling_seq`, adding its `delta` and `correct_delta` to the
named participant (if they appear in the provisional standings), and clamp each
adjusted `score` and `correct` to **0** again before re-ranking with TR-TIEBREAK.

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
stored link. When a `rescind` clears incident X, also clear every other incident Y
still in the map whose effective entry has `paired_incident` equal to X (and remove Y
from the deferred pass list if present) before continuing replay.

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
not revive primaries that depend on it. Deferred `applies_after_floor` rulings are
unchanged: H-2026-08 still snapshots only the direct dependency at record time.

### H-2026-17 — Rescinded paired parents stay tainted

Extends H-2026-12 and H-2026-16. During the ascending `ruling_seq` replay, use
the same set of incident ids that were `rescind`ed at least once (H-2026-16).
After replay finishes, a surviving **primary** ruling is void if its
`paired_incident` names an id in that set — even when that parent was re-issued
and is active again in the effective map. Re-issuing a paired parent after rescind
does not revive primaries that point at it. Deferred `applies_after_floor` rulings
are unchanged.

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
ruling). An `amend` that omits `applies_after_floor` demotes the incident to
primary per H-2026-13 and clears any deferred paired snapshot for that incident.

### H-2026-20 — Frozen deferred snapshot sync on amend

Extends H-2026-19. When an incident already has a frozen deferred snapshot entry
and a later `amend` supersedes that incident's effective entry, copy the amended
`player`, `delta`, and `correct_delta` into the frozen snapshot before the
post-floor pass. The snapshotted post-floor adjustment must use the latest amended
values even when the paired parent is later rescinded and the incident is cleared
from the effective map.

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
