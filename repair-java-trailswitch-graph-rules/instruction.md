The TrailSwitch debugging arena at `/app/trailswitch` is a Spring Boot API over
the PostgreSQL railway graph seeded from `/app/sql/schema.sql` and
`/app/sql/seed.sql`. Handlers under
`/app/trailswitch/src/main/java/com/trailswitch` must satisfy
`/app/docs/trailswitch-referee-contract.md` so `POST /v1/plan` keeps its
existing JSON shape.

Bring GraphPathRepository, PathPlanner, and SwitchRuleHandler into compliance
with that contract, then rebuild with `bash /app/trailswitch/build.sh` and
restart with `bash /app/trailswitch/start.sh` (service on
`http://127.0.0.1:8080`).
