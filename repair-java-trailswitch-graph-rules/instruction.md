The TrailSwitch debugging arena at `/app/trailswitch` is a Spring Boot API over
the PostgreSQL railway graph seeded from `/app/sql/schema.sql` and
`/app/sql/seed.sql`. Handlers under
`/app/trailswitch/src/main/java/com/trailswitch` must satisfy
`/app/docs/trailswitch-referee-contract.md` — including `lock` vs `clear`
route rules, NULL wildcard lock positions, non-matching rules that fall
through to later rules on the same edge, per-edge ascending priority, and
lock-group relay after every edge's route rules finish (including the arrival
leg's own rule chain). Relay must run only after those route rules complete, and
`loadLockGroups` must retain every edge id per group. `POST /v1/plan` must keep its existing JSON shape.

Bring GraphPathRepository, PathPlanner, and SwitchRuleHandler into compliance
with that contract, then rebuild with `bash /app/trailswitch/build.sh` and
restart with `bash /app/trailswitch/start.sh` (service on
`http://127.0.0.1:8080`).
