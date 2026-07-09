The TrailSwitch referee at `/app/trailswitch` is out of spec against `/app/sql/schema.sql`, `/app/sql/seed.sql`, and `/app/docs/trailswitch-referee-contract.md`. Repair `GraphPathRepository`, `PathPlanner`, and `SwitchRuleHandler` so path planning, route locks, and lock-group relay match the seed data.

Rebuild with `bash /app/trailswitch/build.sh`, restart with `bash /app/trailswitch/start.sh`, and keep the existing HTTP JSON shape at `http://127.0.0.1:8080`.
