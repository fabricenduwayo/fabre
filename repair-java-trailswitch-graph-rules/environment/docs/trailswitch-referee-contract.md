# TrailSwitch referee contract

The TrailSwitch debugging arena at `/app/trailswitch` is a Spring Boot API over the
PostgreSQL dataset in `/app/sql/schema.sql` and `/app/sql/seed.sql`. Operators audit
it from source and SQL only — do not rely on manual playthroughs.

## Graph model

- `stations`, `edges`, `route_rules`, `lock_groups`, `relay_latches`,
  `edge_relay_transitions`, and `release_sequences` define the railway graph,
  relay state, ordered circuit evidence, and lock semantics.
  Authoritative rows live in `/app/sql/schema.sql` and `/app/sql/seed.sql`.
- An edge is available only when its non-NULL `requires_sw1` and `requires_sw2`
  positions match the request and it is not locked under the current search context.

## Relay semantics

- `relay_latches` stores the current latch state for each relay id. Load a fresh
  initial snapshot for every `POST /v1/plan`; the table is live operational input
  and must not be cached across requests. Transition counts and release-sequence
  progress always begin empty, including when a relay starts released in the table.
- `edge_relay_transitions` defines ordered relay changes that fire only after an
  authorized edge traversal. Apply transitions only once the edge is active and
  unlocked; copy the relay snapshot before applying changes for that edge.
- A transition may list `requires_relay_id` and `requires_relay_state`; it fires only
  when that predicate matches the snapshot being updated.
- Increment a per-relay transition counter whenever a transition actually fires.

## Ordered release sequences

- `release_sequences` lists contiguous edge sequences by `sequence_id` and
  ascending `step_order`. Track progress independently for every sequence in each
  search state.
- After an authorized traversal, an edge matching the next step advances that
  sequence. A mismatch restarts at step one when the edge itself is the first step,
  otherwise it resets progress to zero. Completing the final step records that
  sequence as completed for the remainder of the candidate path.
- When a relay returns to its per-request initial snapshot after at least one
  transition fired on that relay during the candidate path, void every completed
  sequence whose ordered steps include a transition on that relay. Re-earn
  sequence clearance before any later rule may rely on it.
- A station visit or relay transition does not substitute for sequence completion:
  the listed edges must be crossed in order. Sequence progress and completion are
  candidate-path state, not shared state and not PostgreSQL writes.

## Route and lock semantics

- Evaluate route rules in ascending `rule_priority`, breaking ties by ascending
  `rule_id`.
- A route rule matches when all of its non-NULL `lock_sw1` and `lock_sw2` values
  equal the requested positions, any relay predicate matches the current relay
  snapshot, any `requires_visited_station` appears in the path visited so far,
  any `count_relay_id` minimum/maximum transition-count range is met, and any
  `requires_completed_sequence` has completed on that candidate path. NULL switch
  columns are wildcards; when both switch values are non-NULL, both must match.
- The first matching rule for an edge decides that edge: `lock` locks it and
  `clear` leaves it unlocked. Ignore every later matching rule for the same edge.
- Finish route-rule evaluation before lock-group relay. A group with any locked
  member locks all of its members; repeat this across overlapping groups until no
  additional edge becomes locked.
- A lock group may arm only when optional `arm_relay_id` / `arm_relay_state` match
  the current relay snapshot; disarmed groups do not participate in relay.
- Recompute route decisions and lock-group closure independently for every search
  state, including relay snapshot, transition counters, release-sequence state,
  and visited stations.

## Path planning

- Search over `(station, relay snapshot, transition counters, release-sequence
  progress/completions, visited stations)`, not stations alone.
- Prefer the shortest authorized path by edge count; break ties by ascending
  `edge_id` on the first differing edge.
- Returned paths list every station visit, including repeats when a release circuit
  revisits a junction under a new relay snapshot.

Path planning must terminate even though the seeded graph contains cycles. Deduplicate
the full search state and keep a finite traversal bound. A normal reachable or
unreachable result reports `cycle_guard` as true.

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
