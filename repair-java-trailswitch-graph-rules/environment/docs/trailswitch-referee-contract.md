# TrailSwitch referee contract

The TrailSwitch debugging arena at `/app/trailswitch` is a Spring Boot API over the
PostgreSQL dataset in `/app/sql/schema.sql` and `/app/sql/seed.sql`. Operators audit
it from source and SQL only — do not rely on manual playthroughs.

## Graph model

- `stations`, `edges`, `route_rules`, `lock_groups`, `relay_latches`, and
  `edge_relay_transitions` define the railway graph, relay state, and lock semantics.
  Authoritative rows live in `/app/sql/schema.sql` and `/app/sql/seed.sql`.
- An edge is available only when its non-NULL `requires_sw1` and `requires_sw2`
  positions match the request and it is not locked under the current relay snapshot.

## Relay semantics

- `relay_latches` stores the current latch state for each relay id.
- `edge_relay_transitions` defines ordered relay changes that fire only after an
  authorized edge traversal. Apply transitions only once the edge is active and
  unlocked; copy the relay snapshot before applying changes for that edge.
- A route rule may optionally require a relay id and state via `match_relay_id` and
  `match_relay_state`. NULL switch columns remain wildcards.

## Route and lock semantics

- Evaluate route rules in ascending `rule_priority`, breaking ties by ascending
  `rule_id`.
- A route rule matches when all of its non-NULL `lock_sw1` and `lock_sw2` values
  equal the requested positions and any relay predicate matches the current relay
  snapshot. NULL switch columns are wildcards; when both switch values are non-NULL,
  both must match.
- The first matching rule for an edge decides that edge: `lock` locks it and
  `clear` leaves it unlocked. Ignore every later matching rule for the same edge.
- Finish route-rule evaluation before lock-group relay. A group with any locked
  member locks all of its members; repeat this across overlapping groups until no
  additional edge becomes locked.
- Recompute route decisions and lock-group closure independently for every search
  state `(station, relay snapshot)`.

## Path planning

- Search over `(station, relay snapshot)` pairs, not stations alone.
- Prefer the shortest authorized path by edge count; break ties by ascending
  `edge_id` on the first differing edge.
- Returned paths list every station visit, including repeats when a release circuit
  revisits a junction under a new relay snapshot.

Path planning must terminate promptly even though the seeded graph contains a
cycle. A normal reachable or unreachable result reports `cycle_guard` as true.

## API shape (keep intact)

- `GET /health` → `{"status":"ok"}`
- `POST /v1/plan` body `{"from","to","switches":{"sw1","sw2"}}` →
  `{"reachable":bool,"path":[...],"cycle_guard":true}`

`cycle_guard` must be true when planning finishes normally. Route planning on the
seed graph must finish within a couple of seconds even when cycles are present.
When no path exists under the active locks and switch positions, return
`"reachable": false` and an empty path.

Rebuild with `bash /app/trailswitch/build.sh` and restart via
`bash /app/trailswitch/start.sh` after edits. The service listens on
`http://127.0.0.1:8080`.
