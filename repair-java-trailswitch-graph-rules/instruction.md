TrailSwitch at `/app/trailswitch` scores railway reachability from switch lineups against the PostgreSQL graph in `/app/sql/schema.sql` and `/app/sql/seed.sql`, using `/app/docs/trailswitch-referee-contract.md` for the HTTP contract.

Reconcile `GraphPathRepository`, `PathPlanner`, and `SwitchRuleHandler` with the seeded `route_rules` and `lock_groups` rows so `POST /v1/plan` at `http://127.0.0.1:8080` returns the correct reachability and path, including per-edge route locks and `yard_spur` relay.

Route rules load in ascending `rule_priority` then `rule_id`. For each edge, the first matching rule decides — later rules for that edge are ignored. A matching `clear` leaves the edge unlocked; a matching `lock` blocks it. Every non-null `lock_sw1` / `lock_sw2` on a rule must match the request switches (NULL is a wildcard). Apply route locks before `yard_spur` relay propagates a lock to every edge in the group.

Station lookups must not embed raw station ids in SQL text. Path planning must terminate cleanly on cyclic graphs with `cycle_guard` true. Keep the documented POST response shape.
