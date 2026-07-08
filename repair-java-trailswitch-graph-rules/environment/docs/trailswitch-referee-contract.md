# TrailSwitch referee contract

The TrailSwitch debugging arena at `/app/trailswitch` is a Spring Boot API over the
PostgreSQL dataset in `/app/sql/schema.sql` and `/app/sql/seed.sql`. Operators audit
it from source and SQL only — do not rely on manual playthroughs.

## Graph model

- `stations`, `edges`, `route_rules`, and `lock_groups` define the railway graph and
  lock semantics. The authoritative rows live in `/app/sql/schema.sql` and
  `/app/sql/seed.sql`.
- `GraphPathRepository` must bind station ids as SQL parameters — do not concatenate
  them into query strings.
- Path planning on the cyclic graph (including the `E`→`C` return edge) must track
  visited nodes so search terminates with `cycle_guard` true.
- `SwitchRuleHandler` must implement route-lock semantics consistent with the
  `route_rules` and `lock_groups` seed rows and this contract.
- For each edge, evaluate that edge's `route_rules` rows in **ascending**
  `rule_priority` order. The **first** row on the edge whose switch-position
  predicates match the request wins for that edge; later rows on the same edge
  are not consulted.
- A winning row with `rule_action` `clear` opens the edge. A winning row with
  `rule_action` `lock` locks it. Both `lock_sw1` and `lock_sw2` must match when
  present; a NULL column is a wildcard for that switch.

## API shape (keep intact)

- `GET /health` → `{"status":"ok"}`
- `POST /v1/plan` body `{"from","to","switches":{"sw1","sw2"}}` →
  `{"reachable":bool,"path":[...],"cycle_guard":true}`

`cycle_guard` must be true when planning finishes normally. When no path exists under
the active locks and switch positions, return `"reachable": false` and an empty path.

Rebuild with `bash /app/trailswitch/build.sh` and restart via
`bash /app/trailswitch/start.sh` after edits. The service listens on
`http://127.0.0.1:8080`.
