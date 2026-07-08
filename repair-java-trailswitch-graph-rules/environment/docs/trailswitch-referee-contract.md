# TrailSwitch referee contract

The TrailSwitch debugging arena at `/app/trailswitch` is a Spring Boot API over the
PostgreSQL dataset in `/app/sql/schema.sql` and `/app/sql/seed.sql`. Operators audit
it from source and SQL only — do not rely on manual playthroughs.

## Graph model

- `stations`, `edges`, `route_rules`, and `lock_groups` define the railway graph and
  lock semantics. Authoritative rows live in `/app/sql/schema.sql` and
  `/app/sql/seed.sql`.
- `GraphPathRepository` must bind station ids as SQL parameters — do not concatenate
  them into query strings.
- Path planning on the cyclic graph (including the `E`→`C` return edge) must track
  visited nodes so search terminates with `cycle_guard` true.
- `SwitchRuleHandler` must implement route-lock and lock-group relay semantics
  consistent with the `route_rules` and `lock_groups` seed rows.

## Route and lock semantics

Route locks and lock-group relay are defined only by the `route_rules` and
`lock_groups` rows in `/app/sql/seed.sql`. Reconcile behavior from those rows and
the graph topology; do not infer a complete policy from this doc alone.

## API shape (keep intact)

- `GET /health` → `{"status":"ok"}`
- `POST /v1/plan` body `{"from","to","switches":{"sw1","sw2"}}` →
  `{"reachable":bool,"path":[...],"cycle_guard":true}`

`cycle_guard` must be true when planning finishes normally. When no path exists under
the active locks and switch positions, return `"reachable": false` and an empty path.

Rebuild with `bash /app/trailswitch/build.sh` and restart via
`bash /app/trailswitch/start.sh` after edits. The service listens on
`http://127.0.0.1:8080`.
