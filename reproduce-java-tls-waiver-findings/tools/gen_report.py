"""Renders the long Mariner TLS waiver review narrative.

The report is deliberately long (~70k tokens). The decisive material — the
adjudication rules and each service's waiver context (type, scope, grant and
expiry dates, and whether the waiver was later revoked) — is embedded in prose
and spread across sections and appendices. The report never states a service's
final disposition (allow / deny / rotate); only the aggregate counts appear, as
a cross-check. The concrete probe evidence (TLS versions, fingerprints on the
wire, mTLS results) lives only in the inventory database, not here.
"""

from __future__ import annotations

import pathlib

import reference as ref

TYPE_PHRASE = {
    "tls": "transport-protocol",
    "mtls": "mutual-TLS",
    "chain": "certificate-chain",
}
SCOPE_PHRASE = {
    "all": "the service's entire footprint across every environment",
    "prod": "the production listener only",
    "staging": "the staging surface only",
    "dev": "the development surface only",
}
INCIDENTS = [
    "incident INC-2026-0418, a mis-issued intermediate traced to a stale cross-sign",
    "incident INC-2026-0331, an unscheduled key-ceremony rollback",
    "incident INC-2026-0402, a private-key exposure on a decommissioned bastion",
    "incident INC-2026-0455, a chain-of-custody gap in the evidence pipeline",
    "incident INC-2026-0510, a downgrade observed during a partner interconnect test",
]


def purpose(name: str) -> str:
    tail = name.replace("mariner-", "").replace("-", " ")
    table = {
        "edge gateway": "terminates external traffic at the perimeter and fans it into the mesh",
        "auth broker": "issues and validates session assertions for downstream callers",
        "billing api": "settles metered usage into the revenue ledger",
        "fulfillment": "coordinates warehouse hand-off and carrier manifests",
        "telemetry": "ingests high-cardinality metrics from the fleet",
        "config service": "distributes signed configuration bundles to runtime nodes",
        "search index": "serves the customer-facing catalogue query path",
        "dev sandbox": "hosts throwaway integration environments for feature teams",
        "payments gw": "bridges card-network settlement into the payments core",
        "partner api": "exposes a constrained surface to federated third parties",
        "audit log": "is the append-only system of record for security events",
        "notifications": "delivers transactional mail and push to end users",
        "staging portal": "is the pre-production console used by release engineering",
        "reporting": "compiles scheduled analytical extracts for finance",
        "legacy soap": "wraps a remaining SOAP integration kept alive for one partner",
        "iot bridge": "relays device-originated telemetry from the field",
        "cdn origin": "is the shielded origin behind the content delivery tier",
        "docs site": "publishes versioned product documentation",
        "grpc mesh": "carries internal service-to-service RPC over the mesh",
        "webhook relay": "fans outbound event callbacks to subscriber endpoints",
        "ml gateway": "fronts model-inference traffic for product surfaces",
        "vault proxy": "mediates secret retrieval for workloads",
        "status page": "drives the public availability dashboard",
        "feature flags": "evaluates rollout cohorts for product experiments",
        "batch scheduler": "dispatches and tracks recurring batch jobs across the fleet",
        "export gateway": "streams bulk data extracts to downstream consumers",
        "archive store": "retains cold records under the long-term retention policy",
        "quota service": "enforces per-tenant rate and usage quotas at the edge",
        "rate limiter": "shapes inbound request bursts ahead of the mesh",
        "session store": "persists short-lived session state for the auth tier",
        "pref service": "stores per-user preference and personalization data",
        "trace collector": "ingests distributed-tracing spans from the fleet",
        "preview portal": "hosts pre-release preview builds for reviewers",
    }
    return table.get(tail, f"supports the {tail} capability")


# Topical padding paragraph bank. Each entry is a format string parameterised on
# a service's attributes; rotated per (service, paragraph) so dossiers vary.
PAD = [
    "Within the review boundary, {name} ({sid}) {purpose}. It is owned by {owner} "
    "and presents on {endpoint}, which the inventory classifies as a {env} surface. "
    "The transport posture of any {env} endpoint is weighed against the operative "
    "policy rather than against historical convention, and the assessment proceeds "
    "from the evidence of record rather than from operator attestation.",

    "The harness recorded the {name} endpoint over successive sweeps; only the most "
    "recent capture per service is treated as authoritative, since earlier sweeps "
    "frequently predate a remediation or a re-issue. Reviewers are reminded that the "
    "captured negotiation outcomes, the chain-validation result, and the leaf "
    "fingerprint seen on the wire are held in the inventory database and must be read "
    "from there, not inferred from this narrative.",

    "For {name}, issuer trust is a policy question settled against the maintained anchor "
    "set rather than the popularity of a commercial authority. The specific issuer and "
    "key parameters of {name}'s certificate of record are carried in the inventory "
    "database; what matters to the review is whether that issuer sits inside the "
    "governed anchor set, since a leaf that validates today but chains outside the set "
    "is still a rotation candidate on governance grounds.",

    "Key strength for {name} is judged against the floor for its algorithm family. The "
    "review does not grade keys on a curve: a key below the floor is a rotation finding "
    "irrespective of the sensitivity of the workload, because under-strength material "
    "weakens the whole interconnect graph that {name} participates in.",

    "Certificate lifetime is the other half of hygiene. A leaf approaching its "
    "not-after boundary inside the rotation window is scheduled for replacement well "
    "ahead of the cliff, on the principle that a lapse on the {env} surface is an "
    "availability incident as much as a security one. The window is uniform across "
    "services so that nothing in {name}'s profile earns special treatment.",

    "Mutual TLS expectations for {name} follow the environment. The production trust "
    "boundary requires a client certificate; a non-production surface is not penalised "
    "for the absence of one. Where {name} is expected to present a client certificate "
    "and the capture shows none, the gap is a protocol-level finding unless a waiver of "
    "the matching kind and scope is in force.",

    "The protocol floor matters for {name} because a single tolerated downgrade becomes "
    "a precedent. The review treats any negotiated version outside the allowed set as a "
    "finding in every environment, including development, so that a sandbox habit does "
    "not migrate into production by copy-paste.",

    "Evidence handling for {name} is deliberately conservative. When the fingerprint "
    "observed on the wire disagrees with the inventory of record, the review does not "
    "attempt to reconcile the two in the agent's favour; the disagreement is itself the "
    "finding, and it is escalated rather than waived, regardless of any paperwork that "
    "might otherwise have applied.",

    "Ownership context: {owner} maintains {name} and is the counterparty for any "
    "remediation. The review records owning teams so that rotation and re-issuance work "
    "lands with the group that can actually schedule a maintenance window on the {env} "
    "surface, but ownership confers no relief from policy.",

    "The {name} interconnect was modelled as part of the broader dependency graph. A "
    "weakness here propagates to every caller that trusts this endpoint, which is why "
    "the review resists the temptation to treat {purpose_clause} as a low-stakes "
    "carve-out. The posture is assessed on its own merits and against the same bar as "
    "the busiest production path.",

    "Operationally, {name} has been stable, but stability is not conformance. The "
    "review separates 'has not failed yet' from 'meets policy today', and it is the "
    "latter that governs the finding. Where the captured evidence and the live "
    "configuration disagree, the captured evidence is taken as the ground truth.",

    "Documentation for {name} was cross-checked against the configuration set. Where a "
    "policy value is needed — the rotation window, the protocol allow-list, the key "
    "floors, or the issuer anchor set — it is read from the validated configuration "
    "rather than from this prose, which paraphrases policy for the reader's convenience "
    "only.",

    "Revocation freshness was considered for {name}. The review notes whether the "
    "endpoint's stapled status was recent and whether the validating party had a live "
    "path to revocation information, but treats stapling hygiene as advisory this cycle; "
    "the governing chain question remains whether the presented chain validated to a "
    "trusted anchor at capture time.",

    "Cipher-suite selection at {name} was inspected for obviously deprecated "
    "constructions. While suite negotiation is not itself a graded axis in this review, "
    "a modern protocol version on {endpoint} strongly constrains the suite space, which "
    "is part of why the version allow-list does so much of the work and why a downgrade "
    "is treated as consequential rather than cosmetic.",

    "Session resumption behaviour for {name} was characterised so that repeat captures "
    "could be compared fairly. Resumption can mask a renegotiated parameter, so the "
    "harness records full-handshake outcomes where it can; the authoritative capture for "
    "{name} is still the most recent row, and resumption never changes which row is "
    "current.",

    "SNI and virtual-host disambiguation were verified for {name} so that the captured "
    "leaf is unambiguously the one {endpoint} intends to serve. A mismatch between the "
    "requested name and the served certificate would itself be an integrity concern, "
    "which is one more reason the observed fingerprint is compared against the inventory "
    "of record rather than assumed.",

    "ALPN negotiation at {name} was noted to confirm the application protocol riding "
    "over the tunnel, but protocol-version policy is enforced at the TLS layer and does "
    "not bend to the application above it. A modern application protocol over a legacy "
    "transport is still a transport finding for {name}.",

    "Transport strictness headers on responses from {name} were observed where "
    "applicable. Strict-transport signalling reduces downgrade opportunity for browser "
    "clients but does not substitute for the server-side protocol floor; the review "
    "credits it as defence in depth and nothing more for a {env} surface.",

    "Key-ceremony provenance for {name}'s material was reviewed at a high level. Where "
    "{owner} can attest that the private key was generated and held in a hardware "
    "security module, the operational risk of the key is lower, but provenance does not "
    "raise an under-strength key above the floor or extend a certificate past its "
    "not-after date.",

    "Cross-signing arrangements that touch {name}'s issuer were enumerated to make sure "
    "the chain the review reasons about is the chain clients actually build. A leaf can "
    "validate via more than one path; the governed question for {name} is whether the "
    "issuer of record sits in the trust anchor set, independent of which cross-signed "
    "path a particular client happens to choose.",

    "Certificate-transparency presence for {name}'s leaf was checked as a tamper-"
    "evidence signal. CT inclusion does not by itself make a certificate compliant — it "
    "is neither a protocol version nor an issuer-trust decision — but its absence on a "
    "publicly reachable {env} endpoint would be a flag worth a follow-up outside this "
    "review's transport remit.",

    "Forward-looking, the review recorded whether {name} is on a path toward "
    "post-quantum-ready key exchange. This cycle treats PQC readiness as informational; "
    "it changes no disposition, but it is captured so that {owner} can sequence the work "
    "against the rotation cadence the hygiene rules already impose.",

    "For mesh participants such as {name}, certificate rotation is automated through the "
    "issuing control plane, which lowers the cost of a rotation finding but does not "
    "remove the obligation: an automated rotation that has not yet run still leaves a "
    "soon-to-expire leaf on {endpoint}, and the review grades the state at capture time, "
    "not the intention encoded in automation.",

    "Where {name} terminates TLS at a sidecar or a shared load balancer rather than in "
    "the application process, the review attributes the captured posture to the service "
    "as exposed on {endpoint}. Termination topology is an implementation detail; the "
    "obligation to meet policy attaches to the exposed {env} surface regardless of which "
    "component holds the key.",

    "Partner-facing exposure was a specific consideration for {name} where federated "
    "third parties consume it. Federation raises the stakes of a mutual-TLS gap because "
    "the counterparty's assurance depends on it, which is why a production federation "
    "surface is held to the client-authentication expectation without sympathy for "
    "integration convenience.",

    "Audit retention for {name}'s captures follows the standard schedule: every sweep is "
    "retained, and the review reads the latest. This matters when reconstructing a "
    "finding months later — the row that was current at review time is identifiable by "
    "its capture timestamp, and the reconstruction must use that row rather than "
    "whatever happens to be newest at reconstruction time.",

    "The review explicitly separated configuration intent from observed behaviour for "
    "{name}. A configuration file may declare a strict posture, but if the captured "
    "evidence on {endpoint} shows otherwise, the evidence governs the finding; "
    "conversely a permissive-looking configuration that nonetheless negotiated within "
    "policy is judged on what actually happened on the wire.",

    "Finally, {name} was checked for consistency between its environment label and its "
    "exposure. A service labelled {env} is assessed under the rules for that "
    "environment; the review does not reclassify a surface to soften a finding, and "
    "{owner} retains the route to reclassification through inventory governance rather "
    "than through this review.",

    "Subject-alternative-name coverage on {name}'s leaf was checked against the hostnames "
    "{endpoint} actually answers for. A name not covered by the served certificate would "
    "surface as a verification failure in the capture, so SAN gaps tend to show up "
    "indirectly through the recorded verification outcome rather than as a separate "
    "graded axis.",

    "Wildcard usage at {name} was noted where present. A wildcard leaf broadens blast "
    "radius if its key is compromised, so although a wildcard is not itself a finding, "
    "it raises the priority of the hygiene rules for {name} — a near-expiry or "
    "under-strength wildcard is a rotation the review would rather see scheduled sooner "
    "than later.",

    "Renewal automation for {name} was reviewed at the level of 'does a pipeline exist', "
    "not 'did it run'. An ACME-style renewal loop lowers the operational cost of the "
    "rotation findings this review may raise, but the disposition is taken from the "
    "captured state of {endpoint}, so a renewal that is configured but not yet effective "
    "does not pre-empt a near-expiry finding.",

    "Truststore management on the {env} side of {name} matters for mutual TLS. Where the "
    "endpoint demands a client certificate, the set of client anchors it accepts is an "
    "operational concern for {owner}; the review records only whether a client "
    "certificate was presented and validated, leaving truststore curation to the owning "
    "team's runbooks.",

    "Clock discipline was assumed but noted for {name}: certificate validity windows are "
    "only meaningful if the validating hosts agree on the time. The review reasons about "
    "not-after relative to a single fixed review date, which removes any ambiguity that "
    "wall-clock skew on individual probers might otherwise introduce into the near-expiry "
    "judgement.",

    "Revocation-list distribution touching {name}'s issuer was sanity-checked so that a "
    "client choosing CRL over stapled status still has a path. As with stapling, the "
    "review treats CRL reachability as advisory this cycle; the governing question for "
    "{name} remains whether the presented chain validated at capture time.",

    "Encrypted-client-hello readiness for {name} was recorded as informational. ECH "
    "changes what an on-path observer can see about the handshake to {endpoint} but does "
    "not alter any graded axis here; it neither relaxes the protocol floor nor changes "
    "how a client certificate or a chain is judged.",

    "Early-data exposure for {name} was considered where 0-RTT resumption is enabled. "
    "Replayable early data is an application-layer hazard rather than a transport-policy "
    "axis, so it does not move {name}'s disposition, but it is flagged for {owner} as a "
    "design note to weigh against the latency benefit on the {env} surface.",

    "Certificate pinning by clients of {name} was inventoried lightly, because pinning "
    "interacts badly with rotation: a pinned client can break when {name} legitimately "
    "rotates. The review's rotation findings therefore come with a reminder that any "
    "pin held against {name}'s current leaf must be updated in lockstep with the "
    "re-issue.",
]


def _rot(seq, n):
    return seq[n % len(seq)]


def _fields(s):
    c = s["cert"]
    return {
        "name": s["name"],
        "sid": s["sid"],
        "env": s["env"],
        "owner": s["owner"],
        "endpoint": s["endpoint"],
        "issuer": c["issuer"],
        "algo": "an RSA" if c["key_algo"] == "RSA" else "an elliptic-curve",
        "purpose": purpose(s["name"]),
        "purpose_clause": purpose(s["name"]),
    }


def waiver_paragraph(s) -> str:
    w = s["waiver"]
    f = _fields(s)
    if w is None:
        return (
            f"Exception status. {f['name']} ({f['sid']}) carries no transport-security "
            f"waiver of any kind in the register — no protocol exception, no mutual-TLS "
            f"carve-out, and no chain exception. It is therefore assessed directly "
            f"against the operative policy, with the captured evidence in the inventory "
            f"database standing as the sole record of how the {f['env']} endpoint "
            f"actually negotiated."
        )
    idx = int(s["sid"].split("-")[1])
    tp = TYPE_PHRASE[w["type"]]
    sc = SCOPE_PHRASE[w["scope"]]
    base = (
        f"Exception status. {f['name']} ({f['sid']}) holds waiver {w['id']}, a {tp} "
        f"exception scoped to {sc}. The register shows it granted on {w['granted_on']} "
        f"with a nominal expiry of {w['expires_on']}."
    )
    if w["status"] == "revoked":
        inc = _rot(INCIDENTS, idx)
        base += (
            f" That exception did not run its course: it was rescinded on "
            f"{w['revoked_on']} following {inc}, and the register now carries {w['id']} "
            f"in a revoked state. A rescinded waiver provides no cover, so the nominal "
            f"expiry of {w['expires_on']} is moot — the underlying posture is judged as "
            f"though the exception had never issued."
        )
    else:
        base += (
            f" The register carries {w['id']} as granted and in force as written; "
            f"whether it still provides cover at review time is a separate question, "
            f"settled by reading the policy review date against the recorded expiry, "
            f"and by checking that the scope actually reaches the {f['env']} surface "
            f"under assessment."
        )
    return base


def dossier(s, n_paras: int) -> str:
    f = _fields(s)
    idx = int(s["sid"].split("-")[1])
    out = [f"### {s['sid']} — {s['name']}", ""]
    # Insert the decisive waiver paragraph early, then rotate padding around it.
    blocks = [waiver_paragraph(s)]
    for k in range(n_paras):
        tmpl = _rot(PAD, idx * 13 + k * 11 + 3)
        blocks.append(tmpl.format(**f))
    # Interleave so the waiver paragraph is not always first.
    pos = 1 + (idx % 3)
    blocks = blocks[1 : 1 + pos] + [blocks[0]] + blocks[1 + pos :]
    out.append("\n\n".join(blocks))
    out.append("")
    return "\n".join(out)


# --------------------------------------------------------------------------
# Static narrative sections. The normative adjudication rules live in §3, §4 and
# Appendix G; they are phrased in prose and must be assembled by the reader.
# --------------------------------------------------------------------------
def _header() -> str:
    return (
        "# Mariner Transport-Security Waiver Review — Mid-Year 2026\n\n"
        "Classification: Internal — Restricted. Distribution: Platform Security, "
        "Service Owners, Risk & Compliance.\n\n"
        "Prepared by the Transport Assurance working group. This document is the "
        "narrative of record for the 2026 mid-year review of TLS, mutual-TLS, and "
        "certificate-chain waivers across the Mariner service estate. It explains why "
        "each in-scope service did or did not hold an exception, how the review weighs "
        "the captured evidence against policy, and how a final disposition is reached "
        "for every service. It is written to be read end to end; the rules that decide "
        "a service's fate are stated across the policy and adjudication sections and "
        "restated formally in Appendix G.\n"
    )


def _exec_summary() -> str:
    c = ref.aggregate_counts()
    total = len(ref.SERVICES)
    return (
        "## Executive Summary\n\n"
        f"The review covered {total} services drawn from the production, staging, and "
        "development estates. Each was assessed against the operative transport-security "
        "policy as amended, using the certificate inventory and the captured curl/httpie "
        "probe evidence held in the inventory database, and against the waiver register "
        "transcribed in the appendices.\n\n"
        f"Of the {total} services in scope, the review allowed {c['allow']}, denied "
        f"{c['deny']}, and scheduled {c['rotate']} for certificate rotation. These "
        "totals are the only service-level outcome stated in this narrative; the "
        "per-service disposition is intentionally left to be reproduced from the "
        "evidence and the rules, so that the finding can be audited rather than merely "
        "read. Where this prose and the configuration set differ on a number, the "
        "validated configuration governs; where this prose and the waiver register "
        "differ from an out-of-band claim, the register governs.\n\n"
        "Three themes recur. First, a meaningful number of exceptions had already "
        "lapsed or been rescinded by the review date, and a lapsed exception provides "
        "no cover. Second, several services that negotiate acceptably today are carrying "
        "certificates that are either close to expiry, under-strength for their "
        "algorithm, or anchored to an authority outside the trust list, and those are "
        "rotation findings independent of any protocol exception. Third, a small number "
        "of endpoints presented a leaf on the wire whose fingerprint did not match the "
        "inventory of record; those are treated as chain-of-custody failures and are "
        "not eligible for waiver relief.\n"
    )


def _section_scope() -> str:
    paras = [
        "## 1. Scope and Objectives\n",
        "The objective of this review is narrow and concrete: for every in-scope "
        "service, determine whether its transport-security posture is acceptable as it "
        "stands, must be blocked, or must be scheduled for certificate rotation, and to "
        "do so reproducibly from evidence. The review is not a design exercise and does "
        "not propose architecture changes; it adjudicates the current state against the "
        "current policy.",
        "Scope is the set of services enumerated in the inventory with an externally or "
        "internally reachable TLS listener. Each carries an environment label — "
        "production, staging, or development — that materially affects how some rules "
        "apply, most notably the mutual-TLS expectation. The environment label is taken "
        "from the inventory and is not re-litigated here.",
        "Out of scope are plaintext internal channels protected by network controls, "
        "message-layer security inside asynchronous pipelines, and host-level posture. "
        "Those are covered by separate reviews. The reader should not infer anything "
        "about a service's overall security from its treatment here; this is a transport "
        "review only.",
        "The deliverable that this narrative supports is a machine-checkable set of "
        "findings: one disposition per service, with a single governing reason. The "
        "appendices and the inventory database together carry everything required to "
        "regenerate that set without reference to the authors.",
    ]
    return "\n\n".join(paras) + "\n"


def _section_methodology() -> str:
    paras = [
        "## 2. Methodology\n",
        "### 2.1 Inventory sourcing\n",
        "The service inventory, the certificate facts, and the probe captures are "
        "maintained in a relational store and are the authoritative inputs to this "
        "review. The narrative paraphrases them for readability but does not replace "
        "them; in particular, the negotiated protocol version, the mutual-TLS outcome, "
        "the chain-validation result, the HTTP status, and the leaf fingerprint observed "
        "on the wire are recorded per probe in the database and must be read from there.",
        "### 2.2 Probe harness\n",
        "Endpoints were exercised with scripted curl and httpie invocations that record, "
        "for each attempt, the negotiated TLS version, whether certificate verification "
        "succeeded, whether the server demanded a client certificate, whether the client "
        "presented one, whether the presented chain validated to a trusted anchor, the "
        "resulting HTTP status, and the SHA-256 fingerprint of the leaf actually served. "
        "Each attempt is stored as a row stamped with its capture time.",
        "Crucially, a service is probed more than once over the review period. Earlier "
        "captures are retained for audit but are stale: they may predate a re-issue, a "
        "configuration fix, or a regression. The review uses only the most recent "
        "capture per service — the row with the latest capture timestamp — as the "
        "evidence of record. Selecting any earlier row, or selecting by insertion order, "
        "will misstate the evidence and therefore the finding.",
        "### 2.3 Evidence integrity\n",
        "The fingerprint recorded in the certificate inventory is the leaf the service "
        "is expected to serve. The fingerprint observed by the probe is what was actually "
        "served. When the two agree, the certificate facts in the inventory can be "
        "trusted for the rest of the assessment. When they disagree, the review stops "
        "treating the inventory as descriptive of the live endpoint and records a "
        "chain-of-custody failure, which §4 explains is non-waivable.",
    ]
    return "\n\n".join(paras) + "\n"


def _section_policy() -> str:
    allowed = ", ".join(ref.ALLOWED_TLS_VERSIONS)
    issuers = "; ".join(ref.TRUSTED_ISSUERS)
    envs = ", ".join(ref.MTLS_REQUIRED_ENVS)
    paras = [
        "## 3. Policy Framework\n",
        "The operative policy is small but exact, and the exact thresholds are carried "
        "in the configuration set rather than in this prose. The paragraphs below "
        "describe each rule so the reader understands intent; the validated "
        "configuration is what the pipeline must actually consume.",
        "### 3.1 Transport protocol\n",
        f"Only modern protocol versions are acceptable: the allow-list is {allowed}. A "
        "negotiated version outside that set is a protocol violation. This rule is "
        "uniform across environments — a development endpoint that negotiates a legacy "
        "version is in violation exactly as a production endpoint would be — because "
        "tolerated downgrades migrate. A protocol violation may be excused only by an "
        "in-force transport-protocol waiver whose scope reaches the endpoint's "
        "environment.",
        "### 3.2 Mutual TLS\n",
        f"Mutual TLS is mandatory on the following environments only: {envs}. On those "
        "surfaces, a service that does not present a client certificate when the "
        "endpoint expects one is in violation. On every other environment the absence "
        "of a client certificate is not a finding at all. A mutual-TLS violation may be "
        "excused only by an in-force mutual-TLS waiver whose scope reaches the "
        "environment; a waiver scoped to staging does nothing for a production listener.",
        "### 3.3 Certificate chain and issuer trust\n",
        f"The maintained trust anchors are: {issuers}. Two distinct things are checked. "
        "First, does the chain presented on the wire validate? A chain that does not "
        "validate is a chain violation, excusable only by an in-force certificate-chain "
        "waiver in scope. Second, independent of live validation, is the issuer of the "
        "certificate of record inside the trust anchor set? A leaf that validates today "
        "but is anchored to an issuer outside the set is not blocked, but it is a "
        "rotation candidate on governance grounds (see §3.4).",
        "### 3.4 Certificate hygiene and rotation\n",
        "Independently of any protocol exception, every certificate is assessed for "
        "hygiene, and any hygiene failure schedules the service for rotation. There are "
        "three hygiene triggers. A certificate whose not-after date falls within the "
        "rotation window of the review date is near expiry and must be rotated ahead of "
        "the cliff. A key below the floor for its algorithm family is under-strength and "
        "must be rotated. A leaf anchored to an issuer outside the trust list must be "
        "re-issued under a trusted authority. The rotation window length and the "
        "per-algorithm key floors are policy values read from the configuration set.",
        "Hygiene is assessed for every service that is not already being denied, "
        "including services whose protocol violation is fully excused by an in-force "
        "waiver: an active waiver removes the protocol objection, but it does not make a "
        "soon-to-expire, under-strength, or untrusted certificate acceptable. In other "
        "words, a clean waiver can turn a would-be denial into an allowance, but hygiene "
        "can still pull that allowance up to a rotation.",
        "### 3.5 Waiver lifecycle\n",
        "A waiver has a type (transport-protocol, mutual-TLS, or certificate-chain), a "
        "scope (an environment, or the entire footprint), a grant date, and a nominal "
        "expiry. A waiver is in force at review time only if it was granted and not "
        "revoked and its expiry date is on or after the review date. A waiver that has "
        "passed its expiry, or that was rescinded before the review, is not in force and "
        "provides no cover whatsoever. A waiver only ever excuses a violation of its own "
        "type, and only within its scope.",
        "One nuance sits at the boundary of the lifecycle. Where a violation is genuinely "
        "excused by an in-force waiver, but that waiver itself will lapse within the "
        "rotation window measured from the review date, the service is not left on a "
        "quiet allowance that is about to expire; it is scheduled for rotation so the "
        "underlying condition is fixed before the cover disappears. A waiver that is "
        "comfortably in date imposes no such pull.",
        "This cycle's amendment sharpens that nuance and changes where it sits in the "
        "order of operations. The lapsing-waiver pull is now determined ahead of the "
        "ordinary certificate-hygiene triggers, not after them. Concretely: when a "
        "service's protocol violation is excused by an in-force waiver that itself "
        "lapses within the rotation window, the governing reason is the lapsing waiver "
        "(`waiver_expiring_soon`), and that reason stands even if the same certificate "
        "is independently near expiry, under-strength, or anchored to an untrusted "
        "issuer. The hygiene triggers continue to govern every service that is not "
        "resting on such a lapsing waiver, exactly as before; only the relative "
        "ordering for this specific overlap has moved.",
    ]
    return "\n\n".join(paras) + "\n"


def _section_adjudication() -> str:
    paras = [
        "## 4. Adjudication Model\n",
        "A service's disposition is one of three values — allow, deny, or rotate — and "
        "is reached by applying the rules in a fixed order of precedence. The order "
        "matters: a service can trip more than one rule, and the governing reason is the "
        "first one that applies in the order below. The model is intentionally "
        "deterministic so that two reviewers, or a reviewer and a pipeline, reach the "
        "same finding from the same evidence.",
        "The highest-precedence check is evidence integrity. If the leaf fingerprint "
        "observed on the wire does not match the certificate of record, the service is "
        "denied for a chain-of-custody failure, and no waiver — of any type, scope, or "
        "currency — changes that outcome. This check comes before everything else.",
        "Next come protocol violations. If the most recent probe shows a protocol, "
        "mutual-TLS, or chain violation as defined in §3, the review asks whether an "
        "in-force waiver of the matching type and reaching the environment excuses it. "
        "If no such cover exists, the service is denied. The reason recorded depends on "
        "why cover is absent: if a waiver of the matching type exists but has passed its "
        "expiry, the reason is the lapse; if such a waiver was rescinded, the reason is "
        "the revocation; otherwise — no waiver at all, the wrong type, or a scope that "
        "does not reach the environment — the reason is the violation itself.",
        "If the service has not been denied, the lapsing-waiver rule is applied first, "
        "as amended this cycle (§3.5): a protocol violation excused by an in-force waiver "
        "that will itself expire within the rotation window pulls the service to rotation "
        "with reason `waiver_expiring_soon`, and that determination is made before the "
        "hygiene triggers are even consulted. Only a service that is not held up by such "
        "a lapsing waiver proceeds to the hygiene assessment (§3.4). There, any hygiene "
        "trigger schedules rotation, and the triggers are themselves ordered: imminent "
        "expiry is considered first, then under-strength keys, then untrusted issuers. "
        "The practical consequence of the amendment is that a service carrying both a "
        "lapsing protective waiver and a hygiene defect is reported under the waiver, not "
        "the hygiene trigger.",
        "Finally, what remains is an allowance. A service whose only objection was a "
        "protocol violation fully and durably excused by an in-force, in-scope waiver is "
        "allowed on the strength of that waiver. A service with no objection at all — no "
        "integrity problem, no protocol violation, and clean hygiene — is allowed as "
        "compliant. Every service resolves to exactly one disposition and one governing "
        "reason.",
    ]
    return "\n\n".join(paras) + "\n"


def _section_threat() -> str:
    # Topical padding that reinforces intent without leaking outcomes.
    paras = ["## 5. Threat Model and Rationale\n"]
    seeds = [
        "The review's threat model centres on the interconnect graph rather than on any "
        "single endpoint. A transport weakness is rarely catastrophic in isolation; it "
        "becomes material when a trusted caller inherits the weakness transitively. That "
        "is why protocol floors apply uniformly and why issuer governance is enforced "
        "even where a chain validates today.",
        "Downgrade resistance is a first-class concern. An endpoint that will still "
        "negotiate a legacy protocol offers an attacker a cheaper path than breaking a "
        "modern one, and the existence of the option is the exposure regardless of "
        "whether it is exercised in normal traffic. The allow-list exists to remove the "
        "option, not merely to discourage it.",
        "Client-authentication assurance underpins the production trust boundary. Where "
        "mutual TLS is mandatory, the absence of a presented client certificate means a "
        "caller that should have proven itself did not, and the review treats that as a "
        "control failure rather than a cosmetic gap. Outside that boundary the same "
        "absence is unremarkable.",
        "Key-material strength and certificate lifetime are slower-moving risks that the "
        "review nonetheless takes seriously, because rotation work is cheapest when "
        "scheduled and most expensive when forced by an outage or a compromise. The "
        "rotation window is sized to give owners room to act before either pressure "
        "arrives.",
        "Finally, evidence integrity is treated as foundational. If the review cannot "
        "trust that the certificate it is reasoning about is the one actually served, "
        "every downstream conclusion is suspect. That is why a fingerprint disagreement "
        "is escalated rather than absorbed, and why no exception is allowed to paper "
        "over it.",
    ]
    paras.extend(seeds)
    return "\n\n".join(paras) + "\n"


def _section_findings_overview() -> str:
    c = ref.aggregate_counts()
    return (
        "## 6. Findings Overview\n\n"
        f"The review resolves to {c['allow']} allowances, {c['deny']} denials, and "
        f"{c['rotate']} rotations. The denials are dominated by lapsed and rescinded "
        "exceptions and by a handful of integrity failures; the rotations are split "
        "between certificates near expiry, under-strength keys, untrusted issuers, and "
        "a few services whose protective waivers are about to lapse. The allowances are "
        "a mix of fully compliant services and services resting on an exception that is "
        "both in force and comfortably in date.\n\n"
        "The per-service detail required to reproduce these totals is distributed across "
        "Appendix A (the service dossiers, which carry each waiver's type, scope, and "
        "lifecycle) and the inventory database (which carries the certificate facts and "
        "the captured probe evidence). Appendix G restates the precedence so the "
        "reproduction can be mechanised.\n"
    )


def _appendix_a(paras_per_service: int) -> str:
    out = [
        "## Appendix A — Service Dossiers\n",
        "One dossier per in-scope service, in inventory order. Each dossier records the "
        "service's role and ownership and, decisively, its waiver context: the type and "
        "scope of any exception, its grant and expiry dates, and whether it was later "
        "rescinded. The dossiers do not state a disposition; that is reproduced from "
        "this context, the configuration set, and the inventory database.\n",
    ]
    for s in sorted(ref.SERVICES, key=lambda x: x["sid"]):
        out.append(dossier(s, paras_per_service))
    return "\n".join(out)


def _appendix_b() -> str:
    events = []
    for s in ref.SERVICES:
        w = s["waiver"]
        if w is None:
            continue
        events.append((
            w["granted_on"],
            f"- {w['granted_on']}: {w['id']} granted to {s['name']} ({s['sid']}) — "
            f"{TYPE_PHRASE[w['type']]} exception, scope {w['scope']}, nominal expiry "
            f"{w['expires_on']}.",
        ))
        if w["status"] == "revoked":
            events.append((
                w["revoked_on"],
                f"- {w['revoked_on']}: {w['id']} for {s['name']} ({s['sid']}) RESCINDED "
                f"— exception no longer in force; treat as though never issued.",
            ))
    # Historical replacement edge case: svc-021 briefly held a staging-scoped
    # waiver that was rescinded before the current all-scope waiver was granted.
    # The final register must follow waiver IDs, not mark the replacement revoked
    # just because an older event mentions the same service.
    events.append((
        "2026-02-05",
        "- 2026-02-05: WV-2026-021A granted to mariner-ml-gateway (svc-021) — "
        "transport-protocol exception, scope staging, nominal expiry 2026-05-15.",
    ))
    events.append((
        "2026-02-12",
        "- 2026-02-12: WV-2026-021A for mariner-ml-gateway (svc-021) RESCINDED "
        "— exception no longer in force; replacement review required before prod "
        "coverage can be claimed.",
    ))
    events.sort(key=lambda e: e[0])
    body = "\n".join(e[1] for e in events)
    return (
        "## Appendix B — Waiver Register Timeline\n\n"
        "A chronological transcription of waiver lifecycle events. Read together with "
        "Appendix A; a grant line establishes an exception, but a later rescission line "
        "withdraws it, and only the net state at the review date matters. Services not "
        "listed here never held an exception.\n\n"
        f"{body}\n"
    )


def _appendix_ca() -> str:
    issuers = "\n".join(f"- {i}" for i in ref.TRUSTED_ISSUERS)
    paras = [
        "## Appendix C — Certificate-Authority Governance\n",
        "The trust anchor set is maintained deliberately small. Inclusion is a "
        "governance decision, not a reflection of an authority's market share or "
        "ubiquity in public trust stores. The currently trusted issuers are:",
        issuers,
        "An authority outside this set is not inherently untrustworthy in the public "
        "sense; it is simply not part of Mariner's governed anchor set, and leaves "
        "anchored to it are scheduled for re-issuance under a governed authority. This "
        "keeps the estate's trust dependencies enumerable and revocable on Mariner's "
        "own timeline rather than a third party's.",
        "Re-issuance under a trusted authority is treated as routine rotation work, not "
        "as an incident, provided the chain validates in the interim. Where the chain "
        "does not validate, the matter is a protocol-level chain violation rather than a "
        "governance rotation, and is handled under the denial rules unless an in-force "
        "chain waiver applies.",
    ]
    return "\n\n".join(paras) + "\n"


def _appendix_harness() -> str:
    paras = [
        "## Appendix D — Probe Harness Configuration\n",
        "The harness wraps curl and httpie with a fixed option set so captures are "
        "comparable across services and sweeps. Each tool is invoked to record the "
        "negotiated protocol version, the verification result, the server's "
        "client-certificate demand, whether a client certificate was presented, the "
        "chain-validation outcome, the HTTP status, and the leaf fingerprint, and to "
        "stamp the row with a capture time.",
        "Multiple sweeps were run over the review period. The harness never overwrites a "
        "prior capture; it appends. This preserves an audit trail but means the database "
        "holds several rows per service, of which only the most recent is current. "
        "Consumers must order by capture time and take the latest row per service; the "
        "primary key is an opaque auto-increment and carries no recency meaning.",
        "The harness does not interpret its captures. It records what happened on the "
        "wire and leaves adjudication to the review. In particular it does not decide "
        "whether a missing client certificate matters — that depends on the "
        "environment — and it does not decide whether a fingerprint disagreement is "
        "benign; it simply records both fingerprints for the review to compare.",
    ]
    return "\n\n".join(paras) + "\n"


def _appendix_glossary() -> str:
    items = [
        ("Allowance", "a disposition meaning the service's transport posture is "
         "acceptable as it stands, whether because it is fully compliant or because an "
         "in-force, in-scope waiver durably excuses its only objection."),
        ("Denial", "a disposition meaning the service must be blocked: an integrity "
         "failure, or an unexcused protocol/mutual-TLS/chain violation, or a violation "
         "whose only would-be cover has lapsed or been rescinded."),
        ("Rotation", "a disposition meaning the service is not blocked but must replace "
         "or re-issue its certificate: near expiry, under-strength key, untrusted "
         "issuer, or an excused violation whose waiver lapses within the window."),
        ("In force", "said of a waiver that was granted, not rescinded, and whose expiry "
         "is on or after the review date."),
        ("Scope", "the environments a waiver reaches; a waiver excuses a violation only "
         "on a surface its scope covers."),
        ("Hygiene", "the expiry, key-strength, and issuer-trust properties of a "
         "certificate, assessed independently of protocol exceptions."),
        ("Chain-of-custody failure", "a disagreement between the leaf fingerprint served "
         "on the wire and the certificate of record; non-waivable."),
    ]
    body = "\n".join(f"- **{t}** — {d}" for t, d in items)
    return "## Appendix E — Glossary\n\n" + body + "\n"


def _appendix_changelog() -> str:
    paras = [
        "## Appendix F — Revision History\n",
        "This narrative supersedes the prior quarter's transport-security review. The "
        "material changes this cycle are a tightened protocol allow-list, an explicit "
        "ordering of hygiene triggers, and a re-ordering of the lapsing-waiver pull "
        "ahead of those hygiene triggers. The waiver register was reconciled against the "
        "exceptions ledger, and two exceptions found to have been rescinded operationally "
        "were corrected in the register to a revoked state.",
        "The lapsing-waiver re-ordering is the one change that alters how an overlap is "
        "reported rather than merely what is in scope. In the prior cycle the hygiene "
        "triggers were evaluated before the lapsing-waiver pull, so a certificate that "
        "was near expiry, under-strength, or untrusted reported under that hygiene "
        "trigger even when a protective waiver was also about to lapse. From this cycle "
        "the lapsing-waiver pull is evaluated first for any service whose violation it "
        "excuses, so that overlap now reports as `waiver_expiring_soon`. The normative "
        "ordering in Appendix G reflects the amended order; any reader reproducing the "
        "findings must follow the amended order, not the prior one.",
        "No service was granted a new exception during the compilation of this review. "
        "Where the configuration set and this narrative were found to disagree on a "
        "threshold, the configuration set was treated as authoritative and the prose was "
        "reconciled to it. Readers reproducing the findings should likewise prefer the "
        "validated configuration over any number quoted in passing here.",
    ]
    return "\n\n".join(paras) + "\n"


def _appendix_precedence() -> str:
    return (
        "## Appendix G — Adjudication Precedence (Normative)\n\n"
        "This appendix restates the decision procedure formally. For each service, take "
        "the most recent probe capture (by capture time) as the evidence of record, take "
        "the certificate facts from the inventory, take the waiver state from the "
        "register as of the review date, and read all thresholds from the validated "
        "configuration. Then apply, in order, stopping at the first rule that fires; the "
        "rule that fires determines both the disposition and the single governing reason "
        "code in parentheses.\n\n"
        "1. **Evidence integrity (deny).** If the observed leaf fingerprint does not "
        "equal the certificate-of-record fingerprint, deny (`fingerprint_mismatch`). No "
        "waiver overrides this.\n"
        "2. **Unexcused protocol violation (deny).** Determine the single protocol "
        "violation, if any, in the order: disallowed negotiated TLS version (`tls`); on "
        "an mTLS-mandatory environment, no client certificate presented (`mtls`); chain "
        "did not validate (`chain`). If a violation exists and is not excused by an "
        "in-force waiver of the same type whose scope reaches the environment, then "
        "deny. The reason is `waiver_expired` if a same-type waiver exists but is past "
        "expiry; `waiver_revoked` if a same-type waiver was rescinded; otherwise the "
        "violation itself (`tls_version_blocked`, `mtls_missing`, or `chain_invalid`).\n"
        "3. **Lapsing-waiver rotation (rotate).** Otherwise, if the violation was excused "
        "by an in-force waiver that itself expires within the rotation window of the "
        "review date, rotate (`waiver_expiring_soon`). As amended this cycle (§3.5, "
        "Appendix F), this step is now evaluated before the hygiene triggers below, so "
        "it governs the reason even when a hygiene trigger would also fire.\n"
        "4. **Hygiene rotation (rotate).** Otherwise, in order: certificate not-after "
        "within the rotation window of the review date (`cert_near_expiry`); key below "
        "the floor for its algorithm (`weak_key`); issuer outside the trust anchor set "
        "(`untrusted_issuer`).\n"
        "5. **Allowance (allow).** Otherwise, if a violation was excused by an in-force, "
        "in-scope waiver, allow (`active_waiver_ok`). If there was no objection at all, "
        "allow (`compliant`).\n\n"
        "A waiver is recorded as applied whenever an in-force, in-scope, same-type waiver "
        "excused the protocol violation on the adjudication path — whether the final "
        "disposition is allow (`active_waiver_ok`), rotate because the waiver itself lapses "
        "soon (`waiver_expiring_soon`), or rotate because a hygiene trigger fired while "
        "that cover was still in force (`cert_near_expiry`, `weak_key`, or "
        "`untrusted_issuer`). Set `waiver_applied` to false only when no such waiver "
        "carried the service past rule 2, including denials where a waiver existed but "
        "had lapsed, been rescinded, was out of scope, or was the wrong type.\n"
    )


def _appendix_db() -> str:
    return (
        "## Appendix H — Inventory Database Reference\n\n"
        "The inventory store is a relational database holding three tables. The review "
        "and any pipeline reproducing it read these tables directly; the columns are as "
        "follows.\n\n"
        "`services` — one row per in-scope service: `service_id` (the `svc-NNN` key), "
        "`name`, `environment` (`prod`, `staging`, or `dev`), `owner`, and `endpoint`.\n\n"
        "`certificates` — one row per service describing the certificate of record: "
        "`service_id`, `fingerprint` (the expected leaf SHA-256), `not_after` (the "
        "expiry date), `key_algo` (`RSA` or `EC`), `key_bits`, and `issuer`.\n\n"
        "`probes` — many rows per service, one per captured curl/httpie attempt: "
        "`probe_id` (an opaque auto-increment with no recency meaning), `service_id`, "
        "`tool`, `tls_version`, `verify_ok`, `mtls_required` (did the server demand a "
        "client certificate), `mtls_presented` (did the client present one), "
        "`chain_valid`, `http_status`, `observed_fingerprint` (the leaf actually served), "
        "and `captured_at` (the capture timestamp).\n\n"
        "Because `probes` holds several rows per service, the evidence of record for a "
        "service is the row with the greatest `captured_at` for that `service_id`. The "
        "join that reconstructs a service's posture is therefore inventory-by-service, "
        "joined to its certificate of record, joined to its single most recent probe. "
        "Joining to all probe rows, or selecting by `probe_id`, will double-count or "
        "select stale evidence.\n"
    )


def _appendix_remediation() -> str:
    paras = [
        "## Appendix I — Remediation Playbook\n",
        "This playbook is advisory and changes no disposition; it exists so that owners "
        "receiving a finding know the expected path. A denial is the most urgent class "
        "of outcome and generally means traffic should be constrained until the "
        "underlying violation is corrected — a protocol floor raised, a client "
        "certificate wired in on the production boundary, or a chain repaired — after "
        "which a fresh capture should be taken to confirm the fix.",
        "A rotation outcome is planned work rather than an emergency. For a near-expiry "
        "or under-strength certificate the path is a re-issue under a trusted authority "
        "with an adequately sized key, sequenced against any client pins. For an "
        "untrusted issuer the path is re-issuance under a governed authority even if the "
        "current chain validates. Owners should treat the rotation window as the runway "
        "they have, not the deadline they must hit.",
        "An allowance is not a licence to stop maintaining a service; it records that the "
        "transport posture is acceptable at review time. Where an allowance rests on a "
        "waiver, owners should track the waiver's expiry, because the same posture will "
        "convert to a rotation finding as the waiver approaches its lapse, and to a "
        "denial once it lapses entirely.",
        "Requesting a new waiver, extending an existing one, or narrowing a scope are all "
        "governance actions handled through the exceptions process, not through this "
        "review. The review reads the register as it stands; it does not grant relief. "
        "Owners who believe a finding rests on stale register data should correct the "
        "register through that process and request a re-run.",
    ]
    return "\n\n".join(paras) + "\n"


def gen_report(path: pathlib.Path, paras_per_service: int = 37) -> None:
    parts = [
        _header(),
        _exec_summary(),
        _section_scope(),
        _section_methodology(),
        _section_policy(),
        _section_adjudication(),
        _section_threat(),
        _section_findings_overview(),
        _appendix_a(paras_per_service),
        _appendix_b(),
        _appendix_ca(),
        _appendix_harness(),
        _appendix_glossary(),
        _appendix_changelog(),
        _appendix_precedence(),
        _appendix_db(),
        _appendix_remediation(),
    ]
    text = "\n\n".join(parts).rstrip() + "\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    approx_tokens = len(text) // 4
    print(
        f"  wrote {path.name}  ({len(text):,} bytes, ~{approx_tokens:,} tokens, "
        f"{len(text.split()):,} words)"
    )


if __name__ == "__main__":
    gen_report(pathlib.Path(__file__).resolve().parent.parent
               / "environment" / "reports" / "mariner-tls-waiver-review.md")
