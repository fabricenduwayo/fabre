# TrailSwitch seed semantics

Authoritative graph and rule rows live in `/app/sql/schema.sql` and `/app/sql/seed.sql`.
Reconcile the route referee against those rows and `/app/docs/trailswitch-referee-contract.md`.

## Route rules

- Load `route_rules` in ascending `rule_priority`, then `rule_id`.
- For each `edge_id`, the first matching row decides; later rows for that edge are ignored.
- A matching `clear` leaves the edge unlocked. A matching `lock` blocks it.
- Every non-null `lock_sw1` / `lock_sw2` on a row must match the request switches. NULL is a wildcard.

## Lock groups

- Evaluate route locks before `yard_spur` relay.
- If any edge in a lock group is locked, relay that lock to every edge in the group.

## Graph lookups

- Outgoing-edge lookups must not embed raw station ids in SQL text.

## Planning

- Path planning must terminate cleanly on cyclic graphs with `cycle_guard` true.
