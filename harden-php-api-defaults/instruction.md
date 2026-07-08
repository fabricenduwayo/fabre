Our HarborDesk Edge API in `/app/harbordesk` still reflects an older edition of
the HarborDesk Edge API Hardening Standard in `/app/docs/standard.md`. Operators
report it disagrees with policy on several fronts, and the SQLite audit ledger at
`/app/harbordesk/data/audit.db` has stopped taking new rows even though requests
still get answers. The Standard is a body of numbered controls plus an
authoritative amendments appendix (Appendix G); where the body and an amendment
conflict, the amendment governs (section 1.4).

Bring the running service into conformance so that, for every request, the API
returns exactly the status, headers, and body the Standard as amended requires
and records exactly the audit row it implies. Reconcile the full Standard at
`/app/docs/standard.md`, including at least these controls as amended in
Appendix G: CO-ORIGIN-ALLOW (credentialed exact-origin grants, including
`Vary: Origin`); CO-PREFLIGHT (including G-2026-11 preflight-hint scoping);
AC-BOOTSTRAP (including G-2026-03, G-2026-05, G-2026-15, and G-2026-16);
AC-HEALTH (including G-2026-04); AC-TOKEN-STORE (including G-2026-12);
AU-LEDGER-SCOPE (including G-2026-06); and EH-NO-DISCLOSE. Keep the existing
routes (`GET /health`, `POST /admin/bootstrap`) and their JSON shapes. The ledger already
holds historical rows that reconciliation must preserve; note that the on-disk
ledger is restored to its older layout before every run, so the migration has to
be idempotent runtime code that reconciles the schema whenever the database is
opened (effectively on each request) — a one-off migration done once at deploy
time will be wiped and won't survive.

Cross-origin grants, bootstrap eligibility, and credential checks must follow
the current request and on-disk state, not stale in-process bookkeeping left
over from earlier requests in the same long-lived process. When a request has no
`Origin` header, the audit ledger's `origin` column for that row must be SQL
`NULL`, not an empty string.

PHP, SQLite, and `curl` are already installed and everything runs offline.
