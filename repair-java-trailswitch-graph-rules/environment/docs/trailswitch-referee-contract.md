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
  lineup; a NULL `lock_sw1` or `lock_sw2` means ignore that switch. Rules on the
  same edge are ordered by ascending `rule_priority`; walk them in that order.
  Skip rules that do not match and keep evaluating later rules on the same edge.
  Apply the first matching rule only. A matching `lock` rule blocks the edge; a
  matching `clear` rule leaves it open and stops further rules on that edge.
- `lock_groups` tie edges together. After route rules run on every edge, if any edge
  in a group is locked, lock every edge listed for that same `group_id`. Each edge
  still has its own ascending route-rule chain before relay runs. Relay must not
  run until route rules finish, and `loadLockGroups` must keep every edge id for a
  group — do not drop members when building the map.

## API shape (keep intact)

- `GET /health` → `{"status":"ok"}`
- `POST /v1/plan` body `{"from","to","switches":{"sw1","sw2"}}` →
  `{"reachable":bool,"path":[...],"cycle_guard":true}`

`cycle_guard` must be true when planning finishes normally. When no path exists under
the active locks and switch positions, return `"reachable": false` and an empty path.

Rebuild with `bash /app/trailswitch/build.sh` and restart via
`bash /app/trailswitch/start.sh` after edits. The service listens on
`http://127.0.0.1:8080`.
