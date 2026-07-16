# TrailSwitch referee contract

The TrailSwitch debugging arena at `/app/trailswitch` is a Spring Boot API over the
PostgreSQL dataset in `/app/sql/schema.sql` and `/app/sql/seed.sql`. Operators audit
it from source and SQL only — do not rely on manual playthroughs.

## Graph model

- `stations`, `edges`, `route_rules`, and `lock_groups` define the railway graph and
  lock semantics. Authoritative rows live in `/app/sql/schema.sql` and
  `/app/sql/seed.sql`.
- An edge is available only when its non-NULL `requires_sw1` and `requires_sw2`
  positions match the request and it is not locked.

## Route and lock semantics

- Evaluate route rules in ascending `rule_priority`, breaking ties by ascending
  `rule_id`.
- A route rule matches when all of its non-NULL `lock_sw1` and `lock_sw2` values
  equal the requested positions. NULL is a wildcard; when both values are
  non-NULL, both must match.
- The first matching rule for an edge decides that edge: `lock` locks it and
  `clear` leaves it unlocked. Ignore every later matching rule for the same edge.
- Finish route-rule evaluation before lock-group relay. A group with any locked
  member locks all of its members; repeat this across overlapping groups until no
  additional edge becomes locked.

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
