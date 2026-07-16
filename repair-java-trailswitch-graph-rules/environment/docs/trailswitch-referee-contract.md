# TrailSwitch referee contract

The TrailSwitch debugging arena at `/app/trailswitch` is a Spring Boot API over the
PostgreSQL dataset in `/app/sql/schema.sql` and `/app/sql/seed.sql`. Operators audit
it from source and SQL only — do not rely on manual playthroughs.

## Graph model

- `stations`, `edges`, `route_rules`, and `lock_groups` define the railway graph and
  lock semantics. Authoritative rows live in `/app/sql/schema.sql` and
  `/app/sql/seed.sql`.
- `SwitchRuleHandler` must implement route-lock and lock-group relay semantics
  consistent with the `route_rules` and `lock_groups` seed rows.

## Route and lock semantics

Route locks and lock-group relay are defined only by the `route_rules` and
`lock_groups` rows in `/app/sql/seed.sql`. Reconcile behavior from those rows and
the graph topology.

Load matching route rules in ascending `rule_priority`, then ascending `rule_id`.
For each edge, only the first matching rule applies — skip any later rule targeting
the same edge. A matching `clear` leaves that edge unlocked; a matching `lock`
adds it to the locked set. When both `lock_sw1` and `lock_sw2` are set on a rule,
both switch positions must match (a null position is a wildcard).

Apply route-lock evaluation first, then relay lock groups. When any edge in a
group is locked, lock every edge in that group. Repeat until no new edges are
locked — overlapping groups must reach a fixed point before path planning runs.

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
