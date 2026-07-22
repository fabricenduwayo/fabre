# TrailSwitch referee contract

TrailSwitch is a Spring Boot API over the live PostgreSQL graph defined by
`/app/sql/schema.sql`. Rows may change while the service remains running, so
planning must derive authorization from the current database on every request.

## Graph model

- The graph, route rules, relay transitions, ordered sequences, sequence
  requirements, and armed lock groups come from their same-named schema tables.
- Non-null edge switch requirements are conjunctive. An active edge is usable only
  when its switch positions match and the current search branch leaves it unlocked.

## Relay semantics

- Snapshot `relay_latches` at the start of each plan; never cache it across requests.
  Branch-local transition counts, reset epochs, and sequence state start empty.
- Apply an edge's transitions in database order only after that edge is authorized.
  Relay guards inspect the evolving branch snapshot.
- A sequence-guarded transition with `requires_sequence_progress` needs that exact
  pre-traversal in-flight progress. When the sequence id is present and progress is
  null, the branch must already hold that sequence's grant.
- Count only transitions that fire. Returning a relay to its request-start state
  after it changed advances that relay's reset epoch.

## Ordered release sequences

- Track every sequence independently and in edge order. A mismatch resets in-flight
  progress, except that its first edge starts a new attempt. Existing grants remain.
- A completed sequence grants the branch evidence stamped with the current reset
  epochs of its dependency relays and their transition counts. Transitions and
  reset-epoch changes on the completing traversal are applied before the new grant
  is stamped. When a relay later returns to its request-start state its reset epoch
  advances again, and any grant already stamped against an older epoch of that relay
  is voided: the branch must re-earn that grant before a requirement measured against
  that relay can pass. A newer-epoch grant is unaffected.
- Every requirement attached to a route rule is conjunctive. Its freshness range is
  measured against the row's named relay, independently of other requirements.
  Legacy `requires_completed_sequence` is an additional unwindowed requirement.
- A grant also snapshots the reset epoch of every relay at the moment it is stamped,
  not only its dependency relays. A requirement may name a `witness_relay_id`. When
  it does, the requirement is satisfied only while that witness relay's current reset
  epoch equals the epoch the grant snapshotted; if the witness relay has returned to
  its request-start state since the grant, the requirement fails. A witness that is
  not one of the sequence's dependency relays never voids the grant. The grant stays
  live and still satisfies its other requirements; only the requirements naming the
  reset witness fail, and the branch can re-earn nothing without a fresh grant.
- Sequence progress and grants belong to one candidate path. Visits and relay state
  do not substitute for crossing the listed edges in order.

## Seeded siding witness branch

The siding stations (`P` through `S`) exercise witness-only requirements. Sequence
`siding_release` depends on relay `siding_arm`. Route rule `r_siding_gate` on edge
`e_w_s` clears only when a grant for `siding_release` names `siding_bolt` as
`witness_relay_id`. Because `siding_bolt` is not a dependency relay of that
sequence, resetting `siding_bolt` after the grant does not void the grant; it fails
only the witness-guarded requirement until a fresh grant is earned.

## Route and lock semantics

- Rules are ordered by ascending priority then rule id. The first matching rule per
  edge decides `clear` or `lock`; null match fields are wildcards.
- Switch, relay, visited-station, transition-count, and all sequence predicates on
  that rule must match together.
- After direct decisions, propagate locks through armed and overlapping groups to a
  fixed point. Relay transitions can arm or disarm groups later in the same branch,
  so recompute decisions for each authorization-relevant search state.

## Path planning

- Preserve every branch state that can change later authorization; station-only
  visitation is insufficient. Cyclic searches must terminate with bounded full-state
  deduplication.
- Choose the fewest-edge authorized path, then the lexicographically smaller edge-id
  sequence. Returned station paths retain repeated visits.

## API shape (keep intact)

- `GET /health` → `{"status":"ok"}`
- `POST /v1/plan` body `{"from","to","switches":{"sw1","sw2"}}` →
  `{"reachable":bool,"path":[...],"cycle_guard":true}`

`cycle_guard` must be true when planning finishes normally. When no path exists
under the active locks and switch positions, return
`"reachable": false` and an empty path.

Rebuild with `bash /app/trailswitch/build.sh` and restart via
`bash /app/trailswitch/start.sh` after edits. The service listens on
`http://127.0.0.1:8080`.
