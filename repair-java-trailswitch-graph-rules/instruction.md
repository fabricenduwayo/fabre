The TrailSwitch referee at `/app/trailswitch` is out of spec against PostgreSQL in `/app/sql/schema.sql` and `/app/sql/seed.sql`. Repair `GraphPathRepository`, `PathPlanner`, and `SwitchRuleHandler` so route locking and lock-group relay match the seed rows and `/app/docs/trailswitch-referee-contract.md`.

Rebuild with `bash /app/trailswitch/build.sh`, restart with `bash /app/trailswitch/start.sh` (`http://127.0.0.1:8080`), and keep the existing HTTP JSON shape.
