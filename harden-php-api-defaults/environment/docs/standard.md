# HarborDesk Edge API Hardening Standard (HEAS)

| Field | Value |
|---|---|
| Document | HEAS |
| Status | In force |
| Edition | 2026.1 |
| Owner | HarborDesk Platform Security |
| Classification | Internal |


## 1. Purpose and scope

This Standard defines the configuration and behavioral baseline that the HarborDesk Edge API enforces. It is the single source of truth for how the API answers cross-origin, authentication, bootstrap, error, and audit-logging requests. The deployment must agree with this Standard for every request it serves.

### 1.4 Precedence of amendments

This Standard is maintained as a body of numbered controls followed by an authoritative list of amendments in **Appendix G**. Where the body of a control and an amendment in Appendix G disagree, **the amendment in Appendix G governs**. Implementers must therefore read both the relevant control and any amendment that references it before encoding behavior. Amendments that state they do not affect API behavior may be noted and disregarded for implementation.


## 2. Definitions


**Origin.** The value of the HTTP `Origin` request header, compared exactly against the allowlist of CO-ORIGIN-ALLOW as amended.


**Allowed origin.** An origin that is byte-for-byte a member of the allowlist as amended by Appendix G.


**Bootstrap secret.** The shared secret in `data/bootstrap_secret` proving authority to mint the administrative token.


**Administrative token.** The single credential minted by AC-BOOTSTRAP and verified by AC-HEALTH.


**Credential generation.** The monotonically increasing deployment value in `data/credential_generation` that authorizes an administrative credential cutover.


**Predecessor credential.** The displaced current credential retained for the bounded AC-CREDENTIAL-CUTOVER overlap.


**Decision.** The audited outcome of a request, one of `accepted` or `denied`.


**Reason.** The audited denial reason, where applicable, as defined by the relevant control as amended.


**Audited request.** A `GET /health` or `POST /admin/bootstrap` request, recorded per AU-LEDGER-SCOPE.


**Ledger.** The persistent SQLite record at `data/audit.db`.


## 3. Access Control


### AC-BOOTSTRAP — One-time administrative bootstrap

**Domain:** Access Control  **Severity:** Critical  **Applies to:** credential-bearing API nodes

**Rationale.** The administrative token may be minted exactly once, and only by a caller proving possession of the deployment bootstrap secret. Plaintext or repeatable bootstrap is prohibited.

**Requirement.** `POST /admin/bootstrap` shall be evaluated in the following order:

1. If the request body is non-empty and is not valid JSON, the response shall be `400` with decision `denied` and reason `malformed_request`.
2. If an administrative token already exists, the request shall be refused. In the body of this Standard this refusal is `403` with reason `already_bootstrapped`.
3. Otherwise, the `X-Bootstrap-Secret` request header shall be compared (using a constant-time comparison) against the deployment secret in `data/bootstrap_secret`. If the header is absent or does not match, the response shall be `403` with reason `invalid_secret`.
4. Otherwise the bootstrap succeeds: the response shall be `201` carrying the freshly minted token in the JSON body field `token`, with decision `accepted` and no reason.

Every bootstrap attempt is audited per AU-LEDGER-SCOPE. *(Appendix G amends both the already-bootstrapped status and the evaluation order.)*

**Implementation guidance.** The secret comparison must not short-circuit on length; use a constant-time primitive.

**Verification.** A first correct bootstrap mints a token; a repeat is refused; a wrong or missing secret is refused; malformed input is refused.

**References.** Governing Security Policy GSP-2024 §4.4; Prior assessment finding AF-58

**Revision history.**
- 2023-07: initial publication.
- 2024-03: added malformed-input handling.


### AC-TOKEN-STORE — Administrative token storage

**Domain:** Access Control  **Severity:** Critical  **Applies to:** credential-bearing API nodes

**Rationale.** A leaked token file must not hand an attacker a working credential, and the file must not be world-readable.

**Requirement.** The administrative token shall be stored in a **non-recoverable** form: reading the token file shall not yield a value that can be presented as a bearer credential. The raw token is returned to the caller exactly once, at bootstrap time, and never persisted in cleartext. The token file shall be created with octal mode `0600` (owner read/write only). The specific one-way representation (for example a salted or unsalted cryptographic digest) is an implementation choice, provided it satisfies both the non-recoverability and the AC-HEALTH verification requirements.

**Implementation guidance.** Whatever representation is chosen must allow AC-HEALTH to verify a presented bearer token without storing the token itself.

**Verification.** The raw bearer token does not appear in the token file; the file mode is `0600`; AC-HEALTH still accepts the raw token.

**References.** Governing Security Policy GSP-2024 §4.6; Baseline Configuration Guide BCG-4.1

**Revision history.**
- 2023-08: initial publication.


### AC-HEALTH — Authenticated health endpoint

**Domain:** Access Control  **Severity:** High  **Applies to:** all HarborDesk API deployments

**Rationale.** The health endpoint confirms liveness only to an authenticated caller, so that deployment topology is not disclosed to anonymous clients.

**Requirement.** `GET /health` shall require a bearer credential in the `Authorization` header of the form `Bearer <token>`:

1. If no bearer credential is presented, the response shall be `401` with decision `denied` and reason `missing_token`.
2. If a bearer credential is presented but does not verify against the stored administrative token (AC-TOKEN-STORE), the response shall be `401` with decision `denied` and reason `invalid_token`.
3. If the bearer credential verifies, the response shall be `200` with JSON body exactly `{"status":"ok"}`, decision `accepted`, and no reason.

Verification of the presented token shall use a constant-time comparison against the stored representation. Every health request is audited per AU-LEDGER-SCOPE. *(Appendix G amends the missing-credential reason string.)*

**Implementation guidance.** Parse the `Bearer` scheme case-sensitively for the scheme token; the credential itself is opaque.

**Verification.** Health returns ok only for the bootstrapped token; missing and invalid credentials are refused and audited with the correct reasons.

**References.** Governing Security Policy GSP-2024 §4.7; Edge Operations Runbook ROB-5

**Revision history.**
- 2023-05: initial publication.


### AC-CREDENTIAL-CUTOVER — Deployment generation cutover

**Domain:** Access Control  **Severity:** Critical  **Applies to:** credential-bearing API nodes

**Rationale.** Operators need to replace an administrative credential without restarting the edge process or creating an unbounded overlap in which old credentials remain valid.

**Requirement.** The deployment publishes its current unsigned decimal credential generation in `data/credential_generation`. A first successful AC-BOOTSTRAP binds the minted credential to that generation. While the published generation has not advanced, the node remains already bootstrapped. When the published generation is greater than the stored current generation, a secret-authorized AC-BOOTSTRAP performs a cutover: it mints and returns a new current credential for the published generation and retains only the displaced current credential as the predecessor. A published generation equal to or below the stored generation does not authorize a cutover.

AC-HEALTH accepts the current credential. During cutover it also accepts the predecessor for a bounded overlap, consuming one allowance for each accepted predecessor request. Current-credential, missing-credential, and invalid-credential requests do not consume that allowance. A later cutover immediately replaces any earlier predecessor and its unused allowance. Generation, current credential, predecessor credential, and remaining allowance form one state transition: concurrent bootstrap and health requests must not observe a partial update or consume the same allowance twice.

The generation input and credential state shall be consulted on every relevant request. Persisted credential material remains subject to AC-TOKEN-STORE; raw bearer values must not be stored.

**Implementation guidance.** Use one cross-process critical section for each read/modify/write transition and publish the resulting state atomically.

**Verification.** Assessors advance the generation while the service remains running, perform repeated and overlapping health checks with both credentials, and perform another cutover before the earlier overlap is exhausted.

**References.** Governing Security Policy GSP-2024 §4.8; Edge Operations Runbook ROB-7

**Revision history.**
- 2026-02: initial publication.


## 4. Audit and Accountability


### AU-LEDGER-SCOPE — Audit ledger scope and durability

**Domain:** Audit and Accountability  **Severity:** Critical  **Applies to:** all HarborDesk API deployments

**Rationale.** Every authentication-relevant attempt must be durably recorded so that operators can review access after the fact. A ledger that silently stops recording is itself a reportable failure.

**Requirement.** The API shall maintain a persistent SQLite audit ledger at `data/audit.db`. For every `GET /health` request and every `POST /admin/bootstrap` request — whether accepted or denied — the API shall append exactly one ledger row capturing, at minimum: a timestamp, the event class (`health` or `bootstrap`), the request route, the decision (`accepted` or `denied`), the denial reason where applicable, and the request **origin**. Preflight (`OPTIONS`) requests, unknown routes, and unsupported methods shall **not** be recorded.

The ledger is an operational record that predates the current deployment and **already contains historical rows**; reconciling the ledger so that new writes succeed shall **preserve** those existing rows. A reconciliation that discards history is non-compliant.

**Implementation guidance.** Audit writes must not be best-effort silent: if a write fails, that is a defect to be fixed, not swallowed. Investigate the on-disk ledger to understand the current write failure.

**Verification.** After replaying the request sequence, the ledger contains one row per audited request with the correct decision and reason, the request origin is recorded, and the pre-existing historical rows remain present. *(Appendix G amends the recorded-origin and migration requirements.)*

**References.** Governing Security Policy GSP-2024 §3.2; Prior assessment finding AF-22

**Revision history.**
- 2023-06: initial publication.
- 2024-09: emphasized durability after AF-22.


## 5. Cross-Origin Controls


### CO-ORIGIN-ALLOW — Cross-origin allowlist

**Domain:** Cross-Origin Controls  **Severity:** Critical  **Applies to:** all HarborDesk API deployments

**Rationale.** A credentialed API must never reflect an arbitrary origin. Only an explicit allowlist of trusted internal origins may receive a cross-origin grant.

**Requirement.** The API shall maintain an **origin allowlist**. In the body of this Standard the allowlist contains the single origin `https://harbordesk.internal`. For any request carrying an `Origin` header:

1. If the origin is **exactly** a member of the allowlist (byte-for-byte comparison of scheme, host, and any port; no normalization, no suffix matching), the response shall set `Access-Control-Allow-Origin` to that exact origin, set `Access-Control-Allow-Credentials: true`, and set `Vary: Origin`.
2. Otherwise the response shall carry **no** `Access-Control-Allow-Origin` and **no** `Access-Control-Allow-Credentials` header at all.

The wildcard value `*` shall never be emitted. *(Appendix G amends the allowlist.)*

The allowlist is defined solely by this Standard as amended; it shall not be read from, extended by, or overridden by any node-local file, environment variable, or other deployment data. A legacy `data/allowed_origins` file may be present on the node from an earlier configuration and is **not** policy: it shall not affect any grant.

**Implementation guidance.** Comparison is exact; `https://harbordesk.internal` and `https://harbordesk.internal/` are different strings and only the former matches. Build the allowlist from this Standard, not from any origins file the deployment happens to ship.

**Verification.** Allowed origins receive an exact echoed grant; all other origins receive none. Rewriting or removing a node-local origins file does not change any grant.

**References.** Governing Security Policy GSP-2024 §5.1; Baseline Configuration Guide BCG-2.2

**Revision history.**
- 2023-02: initial publication of CO-ORIGIN-ALLOW.
- 2024-06: clarified exact-match semantics.
- 2026-03: clarified that the allowlist is Standard-defined and not file-sourced.


### CO-PREFLIGHT — Preflight handling

**Domain:** Cross-Origin Controls  **Severity:** High  **Applies to:** all HarborDesk API deployments

**Rationale.** Browser preflight (`OPTIONS`) requests must be answered consistently so that legitimate cross-origin clients function while untrusted origins gain nothing.

**Requirement.** An `OPTIONS` request to any path shall return HTTP `204` with no response body, including when the request omits `Access-Control-Request-Method`. The cross-origin grant of CO-ORIGIN-ALLOW applies to the preflight response under the same allowlist rule. When (and only when) the origin is allowed, the preflight response shall additionally set:

- `Access-Control-Allow-Methods: GET, POST, OPTIONS`
- `Access-Control-Allow-Headers: Authorization, Content-Type, X-Bootstrap-Secret`
- `Access-Control-Max-Age` to the preflight cache lifetime, which in the body of this Standard is `600` seconds.

Preflight requests are **not** audited (see AU-LEDGER-SCOPE). *(Appendix G amends the cache lifetime.)*

**Implementation guidance.** Do not emit the method/header/max-age hints for disallowed origins.

**Verification.** A preflight from an allowed origin returns 204 with the full hint set; from a disallowed origin it returns 204 with no cross-origin headers.

**References.** Governing Security Policy GSP-2024 §5.2; Vendor hardening note VHN-5-1

**Revision history.**
- 2023-09: initial publication.
- 2024-11: clarified that disallowed origins receive no hints.


## 6. Error Handling and Disclosure


### EH-NO-DISCLOSE — No internal disclosure in responses

**Domain:** Error Handling and Disclosure  **Severity:** High  **Applies to:** all HarborDesk API deployments

**Rationale.** Debug traces and internal details must never be returned to callers in a hardened deployment.

**Requirement.** Debug mode shall be disabled. No response shall contain a stack trace, exception text, internal file path, or a `X-Debug-Mode` header. Error responses shall carry a generic JSON body of the form `{"error":"<short message>"}` with no `trace` field. A rejection of malformed JSON input under AC-BOOTSTRAP shall use the exact body `{"error":"bad request"}`. An unknown route or unsupported method shall return `404` with body `{"error":"not found"}` and shall not be audited.

**Implementation guidance.** Ensure framework display-errors settings are disabled and that error helpers do not attach diagnostic fields.

**Verification.** Malformed input yields a generic `400` with no trace and no debug header; unknown routes yield a generic `404`.

**References.** Governing Security Policy GSP-2024 §7.1; Vendor hardening note VHN-7-3

**Revision history.**
- 2023-04: initial publication.


## Appendix G. Amendments (authoritative)


The following amendments are in force and **supersede** the body of the referenced controls per section 1.4. They are listed in effective-date order.


### G-2026-01 — amends CO-ORIGIN-ALLOW

The origin allowlist in CO-ORIGIN-ALLOW is extended to add the operations console origin `https://ops.harbordesk.internal`. The allowlist is therefore exactly `https://harbordesk.internal` and `https://ops.harbordesk.internal`. Exact-match semantics are unchanged: neither a trailing slash nor a differing port matches. This list is closed and Standard-defined: it is not read from, added to, or overridden by any node-local file (including a legacy `data/allowed_origins` file), environment variable, or deployment data.


### G-2026-02 — amends CO-PREFLIGHT

The preflight cache lifetime in CO-PREFLIGHT is lowered from `600` to `300` seconds. The `Access-Control-Max-Age` header on an allowed-origin preflight shall therefore be `300`.


### G-2026-03 — amends AC-BOOTSTRAP

The refusal status for an already-bootstrapped node is changed from `403` to `409` (Conflict). The decision remains `denied` and the reason remains `already_bootstrapped`; only the HTTP status changes.


### G-2026-04 — amends AC-HEALTH

The denial reason for a health request that presents no bearer credential is renamed from `missing_token` to `missing_credentials`. The status (`401`) and the `invalid_token` reason for a present-but-wrong credential are unchanged.


### G-2026-05 — amends AC-BOOTSTRAP

The evaluation order of AC-BOOTSTRAP is amended so that the already-bootstrapped check takes precedence over secret validation. After the malformed-input check, an existing administrative token shall cause an `already_bootstrapped` refusal **even when the presented bootstrap secret is absent or wrong** while the published generation has not advanced beyond the bound in G-2026-21 and G-2026-28. Secret validation is reached when no token yet exists, and again once the published generation exceeds that bound even though token state remains on disk.


### G-2026-06 — amends AU-LEDGER-SCOPE

Migration of the legacy ledger is made explicit. The on-disk ledger is in a legacy layout carrying a non-null `actor` column and lacking an `origin` column, which is why current writes fail. Reconciliation shall move the ledger to a layout whose columns are exactly `id`, `ts`, `event`, `route`, `origin`, `decision`, and `reason`: the request `origin` is recorded for every audited row (including denials), and the legacy `actor` column is removed from the table rather than merely left nullable. Adding an `origin` column while retaining `actor` is non-compliant. Reconciliation shall carry every pre-existing historical row forward unchanged with the same row ids. When migrating legacy rows that predate the `origin` column, the stored `origin` value shall be SQL `NULL`; legacy `actor` values must not be copied into `origin`. When a request carries no `Origin` header, the stored `origin` value for that audited row shall be SQL `NULL`, not an empty string.


### G-2026-07 — amends NW-TLS-CIPHERS

The approved TLS cipher suite list is updated. This amendment does not affect API behavior.


### G-2026-08 — amends MA-PATCH-WINDOW

The maintenance window is shifted by one hour for the eastern region. This amendment does not affect API behavior.


### G-2026-09 — amends IR-CONTACT

The incident-response on-call rotation contact list is revised. This amendment does not affect API behavior.


### G-2026-10 — amends SV-BANNER

The approved service banner wording is updated. This amendment does not affect API behavior.


### G-2026-11 — amends CO-PREFLIGHT

The method, header, and max-age hint headers in CO-PREFLIGHT (`Access-Control-Allow-Methods`, `Access-Control-Allow-Headers`, and `Access-Control-Max-Age`) shall be emitted **only** on an `OPTIONS` preflight for an allowed origin. Non-preflight responses (including credentialed `GET` or `POST`) shall carry at most the grant headers of CO-ORIGIN-ALLOW and shall not include those preflight hints. The CO-ORIGIN-ALLOW grant itself — `Access-Control-Allow-Origin`, `Access-Control-Allow-Credentials`, and `Vary: Origin` — shall be present on **every** allowed-origin response regardless of method; `Vary: Origin` is part of the cross-origin grant, not a preflight hint.


### G-2026-12 — amends AC-TOKEN-STORE

The on-disk administrative token representation shall be the lowercase hexadecimal SHA-256 digest of the raw bearer token (64 hex characters). AC-HEALTH shall verify a presented bearer by applying the same digest before comparison.


### G-2026-13 — amends CO-ORIGIN-ALLOW

Cross-origin grant and preflight hint headers apply only to the current request. When a request carries no `Origin` header, the response shall include none of the headers defined by CO-ORIGIN-ALLOW or CO-PREFLIGHT, including `Vary: Origin`, even if an earlier request in the same long-lived process carried an allowed origin.


### G-2026-14 — amends AC-BOOTSTRAP

Bootstrap eligibility and AC-HEALTH credential verification shall consult the on-disk token file on every request. In-process caches of whether a token exists or of the stored credential representation are non-compliant.


### G-2026-15 — amends AC-BOOTSTRAP

Bootstrap secret validation shall compare the presented `X-Bootstrap-Secret` header to the on-disk secret using a **case-insensitive** ASCII match. Letter case in the header value must not cause an otherwise-correct secret to be rejected.


### G-2026-16 — amends AC-BOOTSTRAP

Before the case-insensitive comparison of G-2026-15, both the presented `X-Bootstrap-Secret` header value and the on-disk bootstrap secret file contents shall be trimmed of leading and trailing ASCII whitespace.


### G-2026-17 — amends AC-BOOTSTRAP

The deployment bootstrap secret in `data/bootstrap_secret` shall be read from disk on every bootstrap attempt. In-process caches of the secret value are non-compliant: if the on-disk secret is replaced between attempts, the next evaluation shall use the current file contents.


### G-2026-18 — amends AC-HEALTH

AC-HEALTH denial reasons are narrowed. The `invalid_token` reason applies only when a **non-empty** bearer credential was extracted from the `Authorization` header (a `Bearer` scheme token with at least one non-whitespace character). If the header is absent, uses a non-`Bearer` scheme, or presents `Bearer` with no credential, the reason shall be `missing_credentials` (status `401` unchanged).


### G-2026-19 — amends AC-BOOTSTRAP

Bootstrap eligibility under AC-BOOTSTRAP is determined solely by whether the administrative token file exists on disk. AC-HEALTH credential verification, however, shall treat the on-disk representation as absent unless the token file contains a valid 64-character lowercase hexadecimal SHA-256 digest. An empty, whitespace-only, or otherwise malformed file therefore retains already-bootstrapped refusal while denying every presented bearer credential with reason `invalid_token`. This malformed-file refusal is a hard gate immediately after AC-BOOTSTRAP's malformed-request check: it returns `409` / `already_bootstrapped` before secret validation or any generation comparison, even when the published generation has advanced. Generation-authorized cutover requires a valid existing state envelope from which a current generation can be established.


### G-2026-20 — amends CO-ORIGIN-ALLOW

When a request carries an `Origin` header that is not on the allowlist, the response shall include none of the CO-ORIGIN-ALLOW grant headers and shall not include `Vary: Origin`.


### G-2026-21 — amends AC-CREDENTIAL-CUTOVER

The predecessor overlap in AC-CREDENTIAL-CUTOVER is exactly **two accepted predecessor health requests per cutover**, shared across all workers. The third and later presentation of that predecessor is denied as `invalid_token`. A successful initial bootstrap or cutover returns `201` with the existing `token` JSON shape. When a token state already exists and the published generation has not advanced, AC-BOOTSTRAP keeps the amended `409` / `already_bootstrapped` outcome before secret validation. Once the generation advances, secret validation is required and a successful request performs the cutover. This amendment supersedes G-2026-12 and G-2026-19 only as to the physical shape recognized as valid: `/app/harbordesk/data/admin_token` may be an implementation-defined state envelope rather than a bare digest, but every credential in it must still be represented only by a 64-character lowercase SHA-256 digest and the file must remain mode `0600`. A malformed envelope retains G-2026-19's split behavior at every published generation: it blocks bootstrap before the generation bound is evaluated and verifies no health credential. The envelope itself must be stored solely in `/app/harbordesk/data/admin_token`; auxiliary credential-state files are non-compliant.


### G-2026-22 — amends AU-LEDGER-SCOPE

All audited append operations shall target `audit_log` only. Other SQLite tables in the same database, including legacy shadow ledgers, shall neither receive new audit rows nor supply rows during reconciliation or migration. Those tables shall also be left in place: reconciliation shall not drop, rename, or otherwise alter them, and their existing rows shall remain unchanged. Ignoring a shadow ledger means never reading from or writing to it, not removing it.


### G-2026-23 — amends AC-TOKEN-STORE

All mutable credential and cutover state—current and predecessor digests, generation binding, and predecessor-overlap counters—shall be persisted only in `/app/harbordesk/data/admin_token`. Sidecar state files such as `admin_token.state` or `token_state.json` are non-compliant. `/app/harbordesk/data/admin_token.lock` is permitted for concurrency coordination only and is not credential state.


### G-2026-24 — amends AU-LEDGER-SCOPE

The request origin recorded by AU-LEDGER-SCOPE is the origin as resolved against the CO-ORIGIN-ALLOW allowlist for the current request. An allowlisted `Origin` header value shall be stored exactly; a disallowed or absent `Origin` shall be stored as SQL `NULL`. Raw unvalidated origin identifiers must never be persisted in the ledger. This resolution applies to every audited row, including denials.


### G-2026-25 — amends AC-CREDENTIAL-CUTOVER

An accepted `GET /health` request that consumes a predecessor-overlap allowance under AC-CREDENTIAL-CUTOVER shall be audited with decision `accepted` and reason `predecessor_overlap`. An accepted request presenting the current credential keeps a SQL `NULL` audit reason. Denial reasons are unchanged.


### G-2026-26 — amends AC-CREDENTIAL-CUTOVER

A first successful AC-BOOTSTRAP activates its credential immediately. Every later generation-authorized bootstrap still returns `201` with the existing `token` JSON shape, but stages that credential as a pending successor instead of displacing the current credential. A pending successor becomes current only after successful health presentations from both distinct origins in the amended CO-ORIGIN-ALLOW allowlist. Repeated presentations from one allowed origin do not complete this confirmation quorum. Those confirming presentations are of the pending successor credential itself, and each is further gated by G-2026-27 and by the incumbent-credential sponsorship of G-2026-30; all three amendments apply together. Sponsorship, confirmation, and activation all occur on `GET /health`: a `POST /admin/bootstrap` request only stages a successor and never sponsors, confirms, or activates one. Until activation, the existing current credential continues to verify normally and no predecessor allowance is created.


### G-2026-27 — amends AC-CREDENTIAL-CUTOVER

A health presentation of the pending successor is accepted only when the request Origin is one of the two amended allowed origins. The first distinct-origin confirmation, and repeats from that same origin while the successor remains pending, are audited `accepted` with reason `cutover_confirmation`. The request that supplies the second distinct allowed origin atomically activates the successor and is audited `accepted` with reason `cutover_activated`. A pending-successor presentation with a disallowed or absent Origin is denied as `invalid_token` and does not change confirmation state. After activation, ordinary current and predecessor audit reasons follow G-2026-25.


### G-2026-28 — amends AC-TOKEN-STORE

The pending successor digest, its generation, and its set of confirmed allowed origins are mutable credential state governed by G-2026-23 and must participate in the same cross-worker critical section as current and predecessor state. Activating a successor atomically makes the displaced current credential the sole predecessor with the two-use allowance, discarding any older predecessor and unused allowance. A valid bootstrap for a still higher published generation replaces an unfinished pending successor without displacing current or altering an existing predecessor allowance; the replaced pending credential becomes invalid. Bootstrap's already-bootstrapped comparison uses the greater of current and pending generation, and a higher-generation replacement still requires the live bootstrap secret.


### G-2026-29 — amends AC-CREDENTIAL-CUTOVER

If the published generation advances beyond the generation bound to an unfinished pending successor, presentations of that stale pending credential are denied as `invalid_token` and must not confirm or activate. Current and predecessor credentials continue to verify until a secret-authorized bootstrap for the higher published generation stages a replacement successor.


### G-2026-30 — amends AC-CREDENTIAL-CUTOVER

Each allowed-origin successor confirmation must be sponsored by the incumbent current credential at that same origin after the successor was staged. While a non-stale pending successor exists, an accepted current-credential `GET /health` from an allowed origin records sponsorship for that origin inside the credential state critical section; its audit reason remains SQL `NULL`. A pending-successor presentation from an allowed but unsponsored origin is denied as `invalid_token` and records no confirmation. Once sponsored, that origin may confirm under G-2026-27. Sponsorship before staging does not count, predecessor requests never sponsor, and replacing an unfinished successor clears both its sponsorships and confirmations. Sponsorships are mutable credential state under G-2026-23 and activation atomically clears them with the pending successor.


### G-2026-31 — amends AC-CREDENTIAL-CUTOVER

The two-use predecessor overlap is origin-partitioned: activation creates one predecessor allowance for each of the two amended allowed origins. A predecessor credential is accepted only when the request Origin is an allowed origin whose allowance remains, and that origin's allowance is consumed atomically. A repeated presentation from the same origin, or a presentation with a disallowed or absent Origin, is denied as `invalid_token` without consuming another origin's allowance. The two remaining-origin allowances are mutable credential state under G-2026-23. A later activation discards all older allowances and initializes exactly the two allowances for its newly displaced current credential.


### G-2026-32 — amends AC-CREDENTIAL-CUTOVER

Sponsorship is phase-fresh. When a pending successor records its first distinct-origin confirmation, every sponsorship for a still-unconfirmed origin is void, even when that sponsorship was recorded after staging. Before another origin may confirm, the incumbent current credential must be accepted again from that origin after the first confirmation. Repeats from an already-confirmed origin do not start another phase or invalidate fresh sponsorship for the remaining origin.


### G-2026-33 — amends AC-TOKEN-STORE

A staged successor is bound to a case-normalized SHA-256 fingerprint of the live bootstrap secret used to stage it. Every health request that touches valid pending state shall re-read the bootstrap secret while holding the credential lock. If its fingerprint changed, sponsorships and confirmations are atomically cleared and the pending state is rebound to the new live fingerprint; the pending digest and generation remain. The credential envelope stores this fingerprint in the top-level `pending_secret_digest` field as a 64-character lowercase hexadecimal SHA-256 digest, or SQL-style JSON `null` when no successor is pending. The request is then evaluated against the cleared state, so incumbent health may establish fresh sponsorship but a pending presentation cannot. An unreadable live secret permits neither sponsorship nor confirmation.


### G-2026-34 — amends AU-LEDGER-SCOPE

A health request that would register sponsorship, record confirmation, activate a successor, or consume predecessor overlap shall append its resolved `audit_log` row before publishing the changed credential envelope. Ledger reconciliation, append, and token publication all occur while the credential lock is held, with the SQLite transaction remaining open through token publication. If reconciliation or append fails, the request returns `500`, publishes no credential mutation, and consumes no allowance or progress. If token publication fails, the audit transaction is rolled back. Immediately before activation is published, the live credential generation is re-read in the same critical section; a pending successor that became stale is denied without confirmation or activation.


### G-2026-35 — amends AC-CREDENTIAL-CUTOVER

While a successor is pending, a `GET /health` request denied as `invalid_token` from an allowed origin revokes any sponsorship recorded for that same origin. The denial's audit append and sponsorship removal are one G-2026-34 ledger-gated credential-state mutation. Existing confirmations remain, sponsorships for other origins are unchanged, and an absent or disallowed Origin revokes nothing. The incumbent credential must be accepted again from the revoked origin before its pending successor can confirm there.


### G-2026-36 — amends AC-CREDENTIAL-CUTOVER

While a pending successor exists at the published generation, the predecessor overlap is frozen. A predecessor credential presented from an allowed origin that still holds an allowance is denied as `overlap_frozen` and consumes no allowance, and the request records no sponsorship or confirmation change. The freeze lifts when the pending successor is activated, replaced, or fenced as stale by a higher published generation; any allowance untouched during the freeze is still spendable afterwards exactly as G-2026-31 describes. A denial under this amendment is not an `invalid_token` denial and therefore does not revoke sponsorship under G-2026-35.


### G-2026-37 — amends AC-CREDENTIAL-CUTOVER

An origin that confirms a pending successor has cut over to it. If the incumbent current credential is afterwards accepted on `GET /health` from that same origin while that successor is still pending, the origin's confirmation is void and the successor falls back to the confirmation set it held beforehand. The same request still records sponsorship for that origin under G-2026-30, so the origin may confirm again. A confirmation set emptied this way makes the next confirmation a first confirmation for the purposes of G-2026-32. Whether the quorum is complete is judged only after the current request's effect on the confirmation set is applied.


### G-2026-38 — amends AU-LEDGER-SCOPE

A successful `POST /admin/bootstrap` is subject to the same ledger gate as G-2026-34, whether it mints the initial credential or stages a pending successor. Its `audit_log` row is appended before the credential envelope is published, inside the credential lock, with the SQLite transaction held open across publication. If the append fails, the request returns `500`, publishes no credential state, and returns no token the caller could use. If publication fails, the audit row is rolled back and the request returns `500`. Denied bootstrap attempts record their row as before.

