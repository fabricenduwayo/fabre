We're closing out the mid-year 2026 Mariner transport-security waiver review and need the findings rebuilt from source instead of hand-copied. Everything is already on the box:

- the review write-up at `/app/reports/mariner-tls-waiver-review.md` (decisive waiver facts are in the narrative appendices, not a table),
- the security config at `/app/config/policy.yaml` and `/app/config/crypto.toml`,
- JSON Schemas for every input and output under `/app/schema/`,
- the service inventory, certificates, and captured probe results in an H2 database at `/app/data/mariner.mv.db` (JDBC `jdbc:h2:/app/data/mariner`, user `sa`, no password),
- the H2 JDBC driver, Jackson, and the networknt schema validator vendored under `/app/lib/` (no internet).

A broken starter pipeline is at `/app/pipeline` — `com.mariner.audit.Main` dispatches `decode`, `join`, and `validate` subcommands with stubbed stage classes and a `build.sh`. Repair it across this and the next two milestones rather than starting from scratch. Compile so `com.mariner.audit.Main` ends up under `/app/classes` or `/app/pipeline/classes`, and keep one output tree for all three milestones — delete stale `Main.class` from the other location before later builds so an earlier compile cannot shadow the current one. Each stage runs with no further arguments and writes its own output under `/app/out/`. Do not hand-write the JSON outputs.

For this milestone, query the H2 `services` table for the in-scope inventory, read the report waiver narrative (Appendices A and B), and decode the final waiver register into `/app/out/waivers.json` — one flat object per service per `/app/schema/waivers.schema.json`. Reflect replacement waivers and rescissions by waiver ID: when a waiver line is RESCINDED, keep the service row with `status` `revoked`, preserve the waiver fields, and set `revoked_on` — do not treat a rescinded waiver as `status` `none`. When a service has both an older rescinded grant and a later replacement grant, the replacement wins. Validate against that schema.
