TrailSwitch at `/app/trailswitch` is a railway routing puzzle. Its referee must score switch lineups from `/app/sql/schema.sql`, `/app/sql/seed.sql`, and `/app/docs/trailswitch-referee-contract.md` through `POST /v1/plan` at `http://127.0.0.1:8080`.

Update `GraphPathRepository`, `PathPlanner`, and `SwitchRuleHandler` so the service returns the correct reachability and path for the seeded board, including per-edge route locks and `yard_spur` relay. Keep the HTTP JSON response shape from the contract.

Route rules load in ascending `rule_priority` then `rule_id`. For each edge, stop at the first matching rule — later rules for that edge are ignored. A matching `clear` leaves the edge unlocked; a matching `lock` blocks it. Every non-null `lock_sw1` / `lock_sw2` on a rule must match the request switches (NULL is a wildcard). Apply route locks before `yard_spur` relay propagates a lock to every edge in the group.

`GraphPathRepository.loadOutgoing` must use JDBC bind parameters, not string-built station ids. `PathPlanner` must mark stations visited when enqueued so cyclic planning finishes with `cycle_guard` true.
