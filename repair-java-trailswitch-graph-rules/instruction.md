TrailSwitch at `/app/trailswitch` scores railway reachability from switch lineups against the PostgreSQL graph in `/app/sql/schema.sql` and `/app/sql/seed.sql`. Reconcile the route referee with `/app/docs/trailswitch-referee-contract.md` and `/app/docs/trailswitch-seed-semantics.md`.

Make `POST /v1/plan` at `http://127.0.0.1:8080` return the correct reachability and path for the seeded board, including per-edge route locks and `yard_spur` relay. Keep the documented response shape.
