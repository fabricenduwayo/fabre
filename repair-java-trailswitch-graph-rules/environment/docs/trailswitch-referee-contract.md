# TrailSwitch referee contract

The TrailSwitch debugging arena at `/app/trailswitch` is a Spring Boot API over the
PostgreSQL dataset in `/app/sql/schema.sql` and `/app/sql/seed.sql`. Operators audit
it from source and SQL only — do not rely on manual playthroughs.

## Graph model

- `stations` lists node ids (`A` depot through `E` arrival).
- `edges` are directed rails. `requires_sw1` / `requires_sw2` list the switch
  positions that must be set for the edge to be traversable (`NULL` means any).
- `route_rules` govern edge locks. Each row has `rule_action` of `lock` or `clear`.
  Lock positions use conjunction: every non-null `lock_sw*` must match the active
  lineup. Rules on the same edge are ordered by ascending `rule_priority`; evaluate
  in that order and apply the first matching rule. A matching `lock` rule blocks the
  edge; a matching `clear` rule leaves it open and stops further rules on that edge.

## API shape (keep intact)

- `GET /health` → `{"status":"ok"}`
- `POST /v1/plan` body `{"from","to","switches":{"sw1","sw2"}}` →
  `{"reachable":bool,"path":[...],"cycle_guard":true}`

`cycle_guard` must be true when planning finishes normally. When no path exists under
the active locks and switch positions, return `"reachable": false` and an empty path.

## Handler requirements

`GraphPathRepository` must load outgoing edges with **parameterized** SQL only — no
string concatenation of station ids into queries. Route rules must load in ascending
`rule_priority` order.

`PathPlanner` must breadth-first search with a visited set and stop after depth 12.
The seed graph contains a cycle (`E`→`C`); planning without a visited guard loops.

`SwitchRuleHandler` must honor ascending per-edge rule order, conjunction lock matching,
and `clear` vs `lock` semantics from the graph model above.

Rebuild with `bash /app/trailswitch/build.sh` and restart via
`bash /app/trailswitch/start.sh` after edits. The service listens on
`http://127.0.0.1:8080`.
