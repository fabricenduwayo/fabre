Our HarborDesk Edge API in `/app/harbordesk` still reflects an older edition of the HarborDesk Edge API Hardening Standard in `/app/docs/standard.md`. The SQLite audit ledger at `/app/harbordesk/data/audit.db` has stopped taking new rows even though requests still get answers. Appendix G amendments override the body where they conflict (section 1.4).

Bring the running service into conformance so every request gets the amended Standard's status, headers, body, and audit row. Reconcile at least CO-ORIGIN-ALLOW, CO-PREFLIGHT, AC-BOOTSTRAP, AC-HEALTH, AC-TOKEN-STORE, AU-LEDGER-SCOPE, and EH-NO-DISCLOSE against Appendix G in `/app/docs/standard.md`. Keep `GET /health` and `POST /admin/bootstrap` JSON shapes. Files under `/app/harbordesk/data/` are deployment inputs, not policy — the amended Standard governs grants, credentials, bootstrap, and ledger layout.

Grants, bootstrap eligibility, secret validation, and health credentials must follow each request's headers and on-disk state, not stale in-process caches. The ledger is reseeded to the legacy layout while PHP keeps running, so startup-only migration is insufficient.

PHP, SQLite, and `curl` are installed; everything runs offline.
