TrailSwitch in `/app/trailswitch` is a PostgreSQL-backed railway safety interlock. The board now includes an approach-release relay whose state can change only after an authorized edge is crossed; `/app/docs/trailswitch-referee-contract.md` defines the rule, transition, lock-relay, path-ordering, and HTTP semantics.

Repair authorization so each search state includes both the station and relay snapshot. For every state, evaluate ordered first-match route rules and relay lock groups to a fixed point before considering an edge, then apply that edge's relay transitions after crossing it. A station reached under a different relay snapshot must remain searchable, and returned paths must include repeated stations when the safe route uses a release circuit.

Keep request-derived station lookups parameterized, terminate promptly on cyclic graphs, preserve the documented response shapes, and return an empty path when no authorized state-space route exists.
