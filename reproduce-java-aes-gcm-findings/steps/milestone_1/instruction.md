We're closing the mid-year 2026 Mariner AES-GCM media-evidence review and I need the signed cryptographic findings rebuilt from source. Everything is on the box:

- the forensic write-up at /app/reports/mariner-aes-gcm-forensic-review.md (long — the decisive exception rules for key-version and nonce selection are in the appendices, not a table),
- the policy at /app/config/policy.yaml and /app/config/crypto.toml,
- JSON Schemas for every input and output under /app/schema/,
- the audit ledger in SQLite at /app/data/forensic_audit.db (JDBC `jdbc:sqlite:/app/data/forensic_audit.db`, no password),
- the multi-frame GIF fixture at /app/fixtures/evidence.gif with per-frame encrypted payloads in MRNR/CRYPTO1 application extension blocks,
- Jackson and the SQLite JDBC driver vendored under /app/lib/ (no internet).

A starter scaffold is provided at /app/pipeline — the `com.mariner.forensic.Main` dispatcher with stubbed `rules`, `correlate`, and `decrypt` subcommands, plus a build.sh. Extend it over this and the next two milestones; implement the stage stubs rather than starting from nothing. Compile so `com.mariner.forensic.Main` ends up under `/app/classes` or `/app/pipeline/classes` — each stage needs to be reproducible from those compiled classes (`com.mariner.forensic.Main rules`, `com.mariner.forensic.Main correlate`, and `com.mariner.forensic.Main decrypt`), each runnable with no further arguments. Don't hand-write the JSON outputs.

For this milestone, read the forensic report appendices and extract the operative cryptographic rules into `/app/out/rules.json`: review date, key-selection precedence, nonce-selection precedence, the derived-nonce rule, and every report-level nonce override. Use `/app/schema/rules.schema.json` for field names and allowed values. Validate against that schema.
