Our HarborDesk Edge API in `/app/harbordesk` still reflects an older edition of
the HarborDesk Edge API Hardening Standard in `/app/docs/standard.md`. Operators
report it disagrees with policy on several fronts, and the SQLite audit ledger at
`/app/harbordesk/data/audit.db` has stopped taking new rows even though requests
still get answers. The Standard is a body of numbered controls plus an
authoritative amendments appendix (Appendix G); where the body and an amendment
conflict, the amendment governs (section 1.4).

Bring the running service into conformance so that, for every request, the API
returns exactly the status, headers, and body the Standard as amended requires
and records exactly the audit row it implies. Keep the existing routes (`GET
/health`, `POST /admin/bootstrap`) and their JSON shapes. The ledger already
holds historical rows that reconciliation must preserve; note that the on-disk
ledger is restored to its older layout before every run, so the migration has to
be idempotent runtime code that reconciles the schema whenever the database is
opened (effectively on each request) — a one-off migration done once at deploy
time will be wiped and won't survive.

Reconcile the full Standard as amended for at least CO-ORIGIN-ALLOW, CO-PREFLIGHT,
AC-BOOTSTRAP, AC-HEALTH, AC-TOKEN-STORE, AU-LEDGER-SCOPE, and EH-NO-DISCLOSE.
Allowed-origin responses must echo the exact `Origin` value, set
`Access-Control-Allow-Credentials: true`, and include `Vary: Origin`. Every
`OPTIONS` request to any path is a preflight and must return `204` with an empty
body even when `Access-Control-Request-Method` is absent; only allowed origins
receive the preflight hint headers (`Access-Control-Allow-Methods`,
`Access-Control-Allow-Headers`, `Access-Control-Max-Age`). G-2026-13: when the
current request has no `Origin` header, emit no cross-origin grant or preflight
hint headers even if an earlier request in the same process carried an allowed
origin. Cross-origin grants,
bootstrap eligibility, and credential checks must follow the current request and
on-disk state, not stale in-process bookkeeping left over from earlier requests
in the same long-lived process. When a request has no `Origin`
header, the audit ledger's `origin` column for that row must be SQL `NULL`, not an
empty string. Read `/app/docs/standard.md` including Appendix G for the exact
allowlists, status codes, denial reasons, token representation, and ledger layout.

PHP, SQLite, and `curl` are already installed and everything runs offline.
