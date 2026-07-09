#!/usr/bin/env python3
"""Generate the HarborDesk Edge API Hardening Standard dossier.

The dossier is intentionally long. The normative clauses the API must implement
are embedded among realistic filler controls, and several of them are superseded
by the authoritative amendments in Appendix G. Where the body and Appendix G
disagree, Appendix G governs (see section 1.4).

Run from the task root:  python3 tools/gen_standard.py
"""

import os
import random

OUT = os.path.join(os.path.dirname(__file__), "..", "environment", "docs", "standard.md")

rng = random.Random(54193)

DOMAINS = [
    ("AC", "Access Control"),
    ("AU", "Audit and Accountability"),
    ("CO", "Cross-Origin Controls"),
    ("EH", "Error Handling and Disclosure"),
    ("SV", "Service Configuration"),
    ("MA", "Maintenance"),
    ("NW", "Network Controls"),
    ("IR", "Incident Response"),
]

SEV = ["Low", "Moderate", "High", "Critical"]
HOSTCLASS = [
    "all HarborDesk API deployments",
    "edge and gateway deployments",
    "internet-facing API nodes",
    "internal staging deployments",
    "credential-bearing API nodes",
]

RATIONALE = [
    "Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment.",
    "Adversaries routinely probe for misconfigurations of this control when establishing a foothold against the API edge.",
    "Consistent enforcement reduces the mean time to detect anomalous access across the fleet.",
    "The control exists to keep responses deterministic so that repeated assessments converge on a stable state.",
    "Inconsistent application of this requirement across nodes complicates evidence collection and weakens attestations.",
    "This requirement aligns the API with the principle of least privilege mandated by the governing security policy.",
    "Operational experience shows that small deviations here cascade into larger exposure during incident response.",
    "The control supports reproducible deployments of the API baseline and simplifies forensic comparison.",
]

GUIDANCE = [
    "Operators should prefer configuration that is idempotent so that re-deploying the API produces no further changes.",
    "Where automation is used, ensure the tooling reads the canonical source files rather than cached copies.",
    "Changes should be staged in a non-production environment and validated against the verification procedure below.",
    "Document any approved deviation in the exceptions register with a scheduled review date.",
    "Prefer explicit values over relying on framework defaults, which may vary between runtime versions.",
    "When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner.",
    "Coordinate with the platform team before altering anything that affects credential handling.",
    "Retain the prior configuration so that a rollback can be performed without redeploying the node.",
]

VERIFY = [
    "Verification is performed by replaying a sequence of requests and comparing each response to the normalized policy expectation.",
    "Evidence is the API's response status, headers, and body together with the resulting audit ledger rows.",
    "Assessors may replay the request sequence after applying fixes to confirm the node has converged.",
    "Automated property checks generate varied request sequences to confirm the control behaves consistently.",
    "The verifier records the request and response for inclusion in the assessment package.",
]

REFS = [
    "Governing Security Policy GSP-2024 §{a}.{b}",
    "Edge Operations Runbook ROB-{a}",
    "Baseline Configuration Guide BCG-{a}.{b}",
    "Prior assessment finding AF-{a}",
    "Vendor hardening note VHN-{a}-{b}",
]


def refs():
    return "; ".join(
        rng.choice(REFS).format(a=rng.randint(1, 9), b=rng.randint(0, 9))
        for _ in range(rng.randint(2, 4))
    )


def revhist(cid):
    out = []
    for _ in range(rng.randint(2, 4)):
        y = rng.choice([2022, 2023, 2024, 2025])
        m = rng.randint(1, 12)
        out.append(
            f"- {y}-{m:02d}: editorial revision to {cid}; clarified scope and wording."
        )
    return "\n".join(out)


def para(bank, n):
    return " ".join(rng.choice(bank) for _ in range(n))


def filler_control(cid, title, domain):
    return f"""### {cid} — {title}

**Domain:** {domain}  **Severity:** {rng.choice(SEV)}  **Applies to:** {rng.choice(HOSTCLASS)}

**Rationale.** {para(RATIONALE, rng.randint(3, 5))}

**Requirement.** {para(GUIDANCE, 1)} The deployment shall maintain the configuration described in this control at all times, and the verifier shall treat any deviation as reportable. {para(RATIONALE, 1)}

**Implementation guidance.** {para(GUIDANCE, rng.randint(5, 8))}

**Verification.** {para(VERIFY, rng.randint(3, 5))}

**References.** {refs()}

**Revision history.**
{revhist(cid)}
"""


# ---------------------------------------------------------------------------
# Normative controls (the API must implement these). Body states the BASE
# values; Appendix G amends several of them.
# ---------------------------------------------------------------------------
NORMATIVE = {}

NORMATIVE["CO-ORIGIN-ALLOW"] = """### CO-ORIGIN-ALLOW — Cross-origin allowlist

**Domain:** Cross-Origin Controls  **Severity:** Critical  **Applies to:** all HarborDesk API deployments

**Rationale.** A credentialed API must never reflect an arbitrary origin. Only an explicit allowlist of trusted internal origins may receive a cross-origin grant.

**Requirement.** The API shall maintain an **origin allowlist**. In the body of this Standard the allowlist contains the single origin `https://harbordesk.internal`. For any request carrying an `Origin` header:

1. If the origin is **exactly** a member of the allowlist (byte-for-byte comparison of scheme, host, and any port; no normalization, no suffix matching), the response shall set `Access-Control-Allow-Origin` to that exact origin, set `Access-Control-Allow-Credentials: true`, and set `Vary: Origin`.
2. Otherwise the response shall carry **no** `Access-Control-Allow-Origin` and **no** `Access-Control-Allow-Credentials` header at all.

The wildcard value `*` shall never be emitted. *(Appendix G amends the allowlist.)*

**Implementation guidance.** Comparison is exact; `https://harbordesk.internal` and `https://harbordesk.internal/` are different strings and only the former matches.

**Verification.** Allowed origins receive an exact echoed grant; all other origins receive none.

**References.** Governing Security Policy GSP-2024 §5.1; Baseline Configuration Guide BCG-2.2

**Revision history.**
- 2023-02: initial publication of CO-ORIGIN-ALLOW.
- 2024-06: clarified exact-match semantics.
"""

NORMATIVE["CO-PREFLIGHT"] = """### CO-PREFLIGHT — Preflight handling

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
"""

NORMATIVE["AC-BOOTSTRAP"] = """### AC-BOOTSTRAP — One-time administrative bootstrap

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
"""

NORMATIVE["AC-TOKEN-STORE"] = """### AC-TOKEN-STORE — Administrative token storage

**Domain:** Access Control  **Severity:** Critical  **Applies to:** credential-bearing API nodes

**Rationale.** A leaked token file must not hand an attacker a working credential, and the file must not be world-readable.

**Requirement.** The administrative token shall be stored in a **non-recoverable** form: reading the token file shall not yield a value that can be presented as a bearer credential. The raw token is returned to the caller exactly once, at bootstrap time, and never persisted in cleartext. The token file shall be created with octal mode `0600` (owner read/write only). The specific one-way representation (for example a salted or unsalted cryptographic digest) is an implementation choice, provided it satisfies both the non-recoverability and the AC-HEALTH verification requirements.

**Implementation guidance.** Whatever representation is chosen must allow AC-HEALTH to verify a presented bearer token without storing the token itself.

**Verification.** The raw bearer token does not appear in the token file; the file mode is `0600`; AC-HEALTH still accepts the raw token.

**References.** Governing Security Policy GSP-2024 §4.6; Baseline Configuration Guide BCG-4.1

**Revision history.**
- 2023-08: initial publication.
"""

NORMATIVE["AC-HEALTH"] = """### AC-HEALTH — Authenticated health endpoint

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
"""

NORMATIVE["EH-NO-DISCLOSE"] = """### EH-NO-DISCLOSE — No internal disclosure in responses

**Domain:** Error Handling and Disclosure  **Severity:** High  **Applies to:** all HarborDesk API deployments

**Rationale.** Debug traces and internal details must never be returned to callers in a hardened deployment.

**Requirement.** Debug mode shall be disabled. No response shall contain a stack trace, exception text, internal file path, or a `X-Debug-Mode` header. Error responses shall carry a generic JSON body of the form `{"error":"<short message>"}` with no `trace` field. An unknown route or unsupported method shall return `404` with body `{"error":"not found"}` and shall not be audited.

**Implementation guidance.** Ensure framework display-errors settings are disabled and that error helpers do not attach diagnostic fields.

**Verification.** Malformed input yields a generic `400` with no trace and no debug header; unknown routes yield a generic `404`.

**References.** Governing Security Policy GSP-2024 §7.1; Vendor hardening note VHN-7-3

**Revision history.**
- 2023-04: initial publication.
"""

NORMATIVE["AU-LEDGER-SCOPE"] = """### AU-LEDGER-SCOPE — Audit ledger scope and durability

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
"""

# ---------------------------------------------------------------------------
# Appendix G amendments (authoritative). Real overrides + filler.
# ---------------------------------------------------------------------------
AMENDMENTS_REAL = [
    ("G-2026-01", "CO-ORIGIN-ALLOW",
     "The origin allowlist in CO-ORIGIN-ALLOW is extended to add the operations "
     "console origin `https://ops.harbordesk.internal`. The allowlist is "
     "therefore exactly `https://harbordesk.internal` and "
     "`https://ops.harbordesk.internal`. Exact-match semantics are unchanged: "
     "neither a trailing slash nor a differing port matches."),
    ("G-2026-02", "CO-PREFLIGHT",
     "The preflight cache lifetime in CO-PREFLIGHT is lowered from `600` to "
     "`300` seconds. The `Access-Control-Max-Age` header on an allowed-origin "
     "preflight shall therefore be `300`."),
    ("G-2026-03", "AC-BOOTSTRAP",
     "The refusal status for an already-bootstrapped node is changed from `403` "
     "to `409` (Conflict). The decision remains `denied` and the reason remains "
     "`already_bootstrapped`; only the HTTP status changes."),
    ("G-2026-04", "AC-HEALTH",
     "The denial reason for a health request that presents no bearer credential "
     "is renamed from `missing_token` to `missing_credentials`. The status "
     "(`401`) and the `invalid_token` reason for a present-but-wrong credential "
     "are unchanged."),
    ("G-2026-05", "AC-BOOTSTRAP",
     "The evaluation order of AC-BOOTSTRAP is amended so that the "
     "already-bootstrapped check takes precedence over secret validation. After "
     "the malformed-input check, an existing administrative token shall cause an "
     "`already_bootstrapped` refusal **even when the presented bootstrap secret "
     "is absent or wrong**. Secret validation is reached only when no token yet "
     "exists."),
    ("G-2026-06", "AU-LEDGER-SCOPE",
     "Migration of the legacy ledger is made explicit. The on-disk ledger is in "
     "a legacy layout carrying a non-null `actor` column and lacking an `origin` "
     "column, which is why current writes fail. Reconciliation shall move the "
     "ledger to a layout that records the request `origin` for every audited row "
     "(including denials) and no longer requires `actor`, while carrying every "
     "pre-existing historical row forward unchanged. When a request carries no "
     "`Origin` header, the stored `origin` value for that audited row shall be "
     "SQL `NULL`, not an empty string."),
    ("G-2026-11", "CO-PREFLIGHT",
     "The method, header, and max-age hint headers in CO-PREFLIGHT "
     "(`Access-Control-Allow-Methods`, `Access-Control-Allow-Headers`, and "
     "`Access-Control-Max-Age`) shall be emitted **only** on an `OPTIONS` "
     "preflight for an allowed origin. Non-preflight responses (including "
     "credentialed `GET` or `POST`) shall carry at most the grant headers of "
     "CO-ORIGIN-ALLOW and shall not include those preflight hints."),
    ("G-2026-12", "AC-TOKEN-STORE",
     "The on-disk administrative token representation shall be the lowercase "
     "hexadecimal SHA-256 digest of the raw bearer token (64 hex characters). "
     "AC-HEALTH shall verify a presented bearer by applying the same digest "
     "before comparison."),
    ("G-2026-13", "CO-ORIGIN-ALLOW",
     "Cross-origin grant and preflight hint headers apply only to the current "
     "request. When a request carries no `Origin` header, the response shall "
     "include none of the headers defined by CO-ORIGIN-ALLOW or CO-PREFLIGHT, "
     "even if an earlier request in the same long-lived process carried an "
     "allowed origin."),
    ("G-2026-15", "AC-BOOTSTRAP",
     "Bootstrap secret validation shall compare the presented "
     "`X-Bootstrap-Secret` header to the on-disk secret using a "
     "**case-insensitive** ASCII match. Letter case in the header value must "
     "not cause an otherwise-correct secret to be rejected."),
    ("G-2026-16", "AC-BOOTSTRAP",
     "Before the case-insensitive comparison of G-2026-15, both the presented "
     "`X-Bootstrap-Secret` header value and the on-disk bootstrap secret file "
     "contents shall be trimmed of leading and trailing ASCII whitespace."),
    ("G-2026-14", "AC-BOOTSTRAP",
     "Bootstrap eligibility and AC-HEALTH credential verification shall consult "
     "the on-disk token file on every request. In-process caches of whether a "
     "token exists or of the stored credential representation are non-compliant."),
    ("G-2026-17", "AC-BOOTSTRAP",
     "The deployment bootstrap secret in `data/bootstrap_secret` shall be read "
     "from disk on every bootstrap attempt. In-process caches of the secret "
     "value are non-compliant: if the on-disk secret is replaced between "
     "attempts, the next evaluation shall use the current file contents."),
    ("G-2026-18", "AC-HEALTH",
     "AC-HEALTH denial reasons are narrowed. The `invalid_token` reason applies "
     "only when a **non-empty** bearer credential was extracted from the "
     "`Authorization` header (a `Bearer` scheme token with at least one "
     "non-whitespace character). If the header is absent, uses a non-`Bearer` "
     "scheme, or presents `Bearer` with no credential, the reason shall be "
     "`missing_credentials` (status `401` unchanged)."),
    ("G-2026-19", "AC-BOOTSTRAP",
     "Bootstrap eligibility under AC-BOOTSTRAP is determined solely by whether "
     "the administrative token file exists on disk. AC-HEALTH credential "
     "verification, however, shall treat the on-disk representation as absent "
     "unless the token file contains a valid 64-character lowercase hexadecimal "
     "SHA-256 digest. An empty, whitespace-only, or otherwise malformed file "
     "therefore retains already-bootstrapped refusal while denying every "
     "presented bearer credential with reason `invalid_token`."),
    ("G-2026-20", "CO-ORIGIN-ALLOW",
     "When a request carries an `Origin` header that is not on the allowlist, "
     "the response shall include none of the CO-ORIGIN-ALLOW grant headers and "
     "shall not include `Vary: Origin`."),
]

AMENDMENTS_FILLER = [
    ("G-2026-07", "NW-TLS-CIPHERS",
     "The approved TLS cipher suite list is updated; see Appendix C. This "
     "amendment does not affect API behavior."),
    ("G-2026-08", "MA-PATCH-WINDOW",
     "The maintenance window is shifted by one hour for the eastern region. This "
     "amendment does not affect API behavior."),
    ("G-2026-09", "IR-CONTACT",
     "The incident-response on-call rotation contact list is revised. This "
     "amendment does not affect API behavior."),
    ("G-2026-10", "SV-BANNER",
     "The approved service banner wording is updated. This amendment does not "
     "affect API behavior."),
]


def build():
    rng.seed(54193)
    parts = []
    parts.append("# HarborDesk Edge API Hardening Standard (HEAS)\n")
    parts.append(
        "| Field | Value |\n|---|---|\n| Document | HEAS |\n| Status | In force |\n"
        "| Edition | 2026.1 |\n| Owner | HarborDesk Platform Security |\n"
        "| Classification | Internal |\n"
    )
    parts.append(
        "\n## 1. Purpose and scope\n\n"
        "This Standard defines the configuration and behavioral baseline that the "
        "HarborDesk Edge API enforces. It is the single source of truth for how "
        "the API answers cross-origin, authentication, bootstrap, error, and "
        "audit-logging requests. The deployment must agree with this Standard for "
        "every request it serves.\n\n"
        + para(RATIONALE, 4)
        + "\n\n### 1.4 Precedence of amendments\n\n"
        "This Standard is maintained as a body of numbered controls followed by "
        "an authoritative list of amendments in **Appendix G**. Where the body of "
        "a control and an amendment in Appendix G disagree, **the amendment in "
        "Appendix G governs**. Implementers must therefore read both the relevant "
        "control and any amendment that references it before encoding behavior. "
        "Amendments that state they do not affect API behavior may be noted and "
        "disregarded for implementation.\n"
    )

    parts.append("\n## 2. Definitions\n")
    terms = [
        ("Origin", "The value of the HTTP `Origin` request header, compared exactly against the allowlist of CO-ORIGIN-ALLOW as amended."),
        ("Allowed origin", "An origin that is byte-for-byte a member of the allowlist as amended by Appendix G."),
        ("Bootstrap secret", "The shared secret in `data/bootstrap_secret` proving authority to mint the administrative token."),
        ("Administrative token", "The single credential minted by AC-BOOTSTRAP and verified by AC-HEALTH."),
        ("Decision", "The audited outcome of a request, one of `accepted` or `denied`."),
        ("Reason", "The audited denial reason, where applicable, as defined by the relevant control as amended."),
        ("Audited request", "A `GET /health` or `POST /admin/bootstrap` request, recorded per AU-LEDGER-SCOPE."),
        ("Ledger", "The persistent SQLite record at `data/audit.db`."),
    ]
    for t, d in terms:
        parts.append(f"\n**{t}.** {d} {para(RATIONALE, rng.randint(1,2))}\n")

    normative_by_domain = {
        "Access Control": ["AC-BOOTSTRAP", "AC-TOKEN-STORE", "AC-HEALTH"],
        "Cross-Origin Controls": ["CO-ORIGIN-ALLOW", "CO-PREFLIGHT"],
        "Error Handling and Disclosure": ["EH-NO-DISCLOSE"],
        "Audit and Accountability": ["AU-LEDGER-SCOPE"],
    }

    section = 3
    for code, dname in DOMAINS:
        parts.append(f"\n## {section}. {dname}\n")
        parts.append(para(RATIONALE, rng.randint(4, 6)) + "\n\n")
        parts.append(para(GUIDANCE, rng.randint(4, 6)) + "\n")
        n_filler = rng.randint(11, 15)
        idx = 1
        for _ in range(n_filler):
            cid = f"{code}-{idx:03d}"
            title = filler_title(rng)
            parts.append("\n" + filler_control(cid, title, dname))
            idx += 1
            if dname in normative_by_domain and normative_by_domain[dname] and rng.random() < 0.4:
                nid = normative_by_domain[dname].pop(0)
                parts.append("\n" + NORMATIVE[nid])
        for nid in normative_by_domain.get(dname, []):
            parts.append("\n" + NORMATIVE[nid])
        normative_by_domain[dname] = []
        section += 1

    parts.append("\n## Appendix A. Deployment classification\n")
    for _ in range(rng.randint(8, 12)):
        parts.append(
            f"\n- **{rng.choice(['DC', 'GW', 'ED', 'SV'])}-{rng.randint(100,999)}**: "
            + para(GUIDANCE, rng.randint(2, 3))
        )
    parts.append("\n\n## Appendix C. Banner and cipher wording\n\n" + para(GUIDANCE, 6) + "\n")
    parts.append("\n## Appendix B. Control rationale narratives\n")
    for _ in range(rng.randint(14, 20)):
        parts.append(
            f"\n### Narrative {rng.choice(['NB','RB','XB'])}-{rng.randint(10,99)}\n\n"
            + para(RATIONALE + GUIDANCE, rng.randint(6, 10))
        )
    parts.append("\n\n## Appendix D. Assessment procedures\n")
    for _ in range(rng.randint(12, 18)):
        parts.append(
            f"\n- **Procedure {rng.randint(100,999)}.** "
            + para(VERIFY + GUIDANCE, rng.randint(3, 5))
        )
    parts.append("\n\n## Appendix E. Change log\n")
    for _ in range(rng.randint(70, 100)):
        y = rng.choice([2023, 2024, 2025, 2026])
        parts.append(
            f"\n- {y}-{rng.randint(1,12):02d}-{rng.randint(1,28):02d}: "
            + para(RATIONALE + GUIDANCE, rng.randint(1, 2))
        )

    parts.append("\n\n## Appendix G. Amendments (authoritative)\n\n")
    parts.append(
        "The following amendments are in force and **supersede** the body of the "
        "referenced controls per section 1.4. They are listed in effective-date "
        "order.\n"
    )
    all_amends = list(AMENDMENTS_REAL) + list(AMENDMENTS_FILLER)
    rng.shuffle(all_amends)
    for aid, target, text in all_amends:
        parts.append(f"\n### {aid} — amends {target}\n\n{text}\n")

    text = "\n".join(parts) + "\n"
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as fh:
        fh.write(text)
    words = len(text.split())
    print(f"wrote {OUT}: {len(text)} chars, ~{words} words, ~{int(words*1.33)} tokens")


TITLE_A = ["Mandatory", "Approved", "Restricted", "Centralized", "Hardened",
           "Verified", "Controlled", "Standard", "Baseline", "Monitored"]
TITLE_B = ["request logging", "rate limiting", "session timeout",
           "log forwarding", "header normalization", "package provenance",
           "content-type enforcement", "service enablement", "credential rotation",
           "interface configuration", "response compression", "cache directive",
           "method allowlisting", "TLS configuration", "console access"]


def filler_title(rng):
    return f"{rng.choice(TITLE_A)} {rng.choice(TITLE_B)}"


if __name__ == "__main__":
    build()
