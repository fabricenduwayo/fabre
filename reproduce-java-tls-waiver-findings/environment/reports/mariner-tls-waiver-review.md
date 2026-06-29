# Mariner Transport-Security Waiver Review — Mid-Year 2026

Classification: Internal — Restricted. Distribution: Platform Security, Service Owners, Risk & Compliance.

Prepared by the Transport Assurance working group. This document is the narrative of record for the 2026 mid-year review of TLS, mutual-TLS, and certificate-chain waivers across the Mariner service estate. It explains why each in-scope service did or did not hold an exception, how the review weighs the captured evidence against policy, and how a final disposition is reached for every service. It is written to be read end to end; the rules that decide a service's fate are stated across the policy and adjudication sections and restated formally in Appendix G.


## Executive Summary

The review covered 33 services drawn from the production, staging, and development estates. Each was assessed against the operative transport-security policy as amended, using the certificate inventory and the captured curl/httpie probe evidence held in the inventory database, and against the waiver register transcribed in the appendices.

Of the 33 services in scope, the review allowed 6, denied 13, and scheduled 14 for certificate rotation. These totals are the only service-level outcome stated in this narrative; the per-service disposition is intentionally left to be reproduced from the evidence and the rules, so that the finding can be audited rather than merely read. Where this prose and the configuration set differ on a number, the validated configuration governs; where this prose and the waiver register differ from an out-of-band claim, the register governs.

Three themes recur. First, a meaningful number of exceptions had already lapsed or been rescinded by the review date, and a lapsed exception provides no cover. Second, several services that negotiate acceptably today are carrying certificates that are either close to expiry, under-strength for their algorithm, or anchored to an authority outside the trust list, and those are rotation findings independent of any protocol exception. Third, a small number of endpoints presented a leaf on the wire whose fingerprint did not match the inventory of record; those are treated as chain-of-custody failures and are not eligible for waiver relief.


## 1. Scope and Objectives


The objective of this review is narrow and concrete: for every in-scope service, determine whether its transport-security posture is acceptable as it stands, must be blocked, or must be scheduled for certificate rotation, and to do so reproducibly from evidence. The review is not a design exercise and does not propose architecture changes; it adjudicates the current state against the current policy.

Scope is the set of services enumerated in the inventory with an externally or internally reachable TLS listener. Each carries an environment label — production, staging, or development — that materially affects how some rules apply, most notably the mutual-TLS expectation. The environment label is taken from the inventory and is not re-litigated here.

Out of scope are plaintext internal channels protected by network controls, message-layer security inside asynchronous pipelines, and host-level posture. Those are covered by separate reviews. The reader should not infer anything about a service's overall security from its treatment here; this is a transport review only.

The deliverable that this narrative supports is a machine-checkable set of findings: one disposition per service, with a single governing reason. The appendices and the inventory database together carry everything required to regenerate that set without reference to the authors.


## 2. Methodology


### 2.1 Inventory sourcing


The service inventory, the certificate facts, and the probe captures are maintained in a relational store and are the authoritative inputs to this review. The narrative paraphrases them for readability but does not replace them; in particular, the negotiated protocol version, the mutual-TLS outcome, the chain-validation result, the HTTP status, and the leaf fingerprint observed on the wire are recorded per probe in the database and must be read from there.

### 2.2 Probe harness


Endpoints were exercised with scripted curl and httpie invocations that record, for each attempt, the negotiated TLS version, whether certificate verification succeeded, whether the server demanded a client certificate, whether the client presented one, whether the presented chain validated to a trusted anchor, the resulting HTTP status, and the SHA-256 fingerprint of the leaf actually served. Each attempt is stored as a row stamped with its capture time.

Crucially, a service is probed more than once over the review period. Earlier captures are retained for audit but are stale: they may predate a re-issue, a configuration fix, or a regression. The review uses only the most recent capture per service — the row with the latest capture timestamp — as the evidence of record. Selecting any earlier row, or selecting by insertion order, will misstate the evidence and therefore the finding.

### 2.3 Evidence integrity


The fingerprint recorded in the certificate inventory is the leaf the service is expected to serve. The fingerprint observed by the probe is what was actually served. When the two agree, the certificate facts in the inventory can be trusted for the rest of the assessment. When they disagree, the review stops treating the inventory as descriptive of the live endpoint and records a chain-of-custody failure, which §4 explains is non-waivable.


## 3. Policy Framework


The operative policy is small but exact, and the exact thresholds are carried in the configuration set rather than in this prose. The paragraphs below describe each rule so the reader understands intent; the validated configuration is what the pipeline must actually consume.

### 3.1 Transport protocol


Only modern protocol versions are acceptable: the allow-list is TLS1.2, TLS1.3. A negotiated version outside that set is a protocol violation. This rule is uniform across environments — a development endpoint that negotiates a legacy version is in violation exactly as a production endpoint would be — because tolerated downgrades migrate. A protocol violation may be excused only by an in-force transport-protocol waiver whose scope reaches the endpoint's environment.

### 3.2 Mutual TLS


Mutual TLS is mandatory on the following environments only: prod. On those surfaces, a service that does not present a client certificate when the endpoint expects one is in violation. On every other environment the absence of a client certificate is not a finding at all. A mutual-TLS violation may be excused only by an in-force mutual-TLS waiver whose scope reaches the environment; a waiver scoped to staging does nothing for a production listener.

### 3.3 Certificate chain and issuer trust


The maintained trust anchors are: Mariner Internal CA G2; Mariner Public CA R3; DigiCert Global G3. Two distinct things are checked. First, does the chain presented on the wire validate? A chain that does not validate is a chain violation, excusable only by an in-force certificate-chain waiver in scope. Second, independent of live validation, is the issuer of the certificate of record inside the trust anchor set? A leaf that validates today but is anchored to an issuer outside the set is not blocked, but it is a rotation candidate on governance grounds (see §3.4).

### 3.4 Certificate hygiene and rotation


Independently of any protocol exception, every certificate is assessed for hygiene, and any hygiene failure schedules the service for rotation. There are three hygiene triggers. A certificate whose not-after date falls within the rotation window of the review date is near expiry and must be rotated ahead of the cliff. A key below the floor for its algorithm family is under-strength and must be rotated. A leaf anchored to an issuer outside the trust list must be re-issued under a trusted authority. The rotation window length and the per-algorithm key floors are policy values read from the configuration set.

Hygiene is assessed for every service that is not already being denied, including services whose protocol violation is fully excused by an in-force waiver: an active waiver removes the protocol objection, but it does not make a soon-to-expire, under-strength, or untrusted certificate acceptable. In other words, a clean waiver can turn a would-be denial into an allowance, but hygiene can still pull that allowance up to a rotation.

### 3.5 Waiver lifecycle


A waiver has a type (transport-protocol, mutual-TLS, or certificate-chain), a scope (an environment, or the entire footprint), a grant date, and a nominal expiry. A waiver is in force at review time only if it was granted and not revoked and its expiry date is on or after the review date. A waiver that has passed its expiry, or that was rescinded before the review, is not in force and provides no cover whatsoever. A waiver only ever excuses a violation of its own type, and only within its scope.

One nuance sits at the boundary of the lifecycle. Where a violation is genuinely excused by an in-force waiver, but that waiver itself will lapse within the rotation window measured from the review date, the service is not left on a quiet allowance that is about to expire; it is scheduled for rotation so the underlying condition is fixed before the cover disappears. A waiver that is comfortably in date imposes no such pull.

This cycle's amendment sharpens that nuance and changes where it sits in the order of operations. The lapsing-waiver pull is now determined ahead of the ordinary certificate-hygiene triggers, not after them. Concretely: when a service's protocol violation is excused by an in-force waiver that itself lapses within the rotation window, the governing reason is the lapsing waiver (`waiver_expiring_soon`), and that reason stands even if the same certificate is independently near expiry, under-strength, or anchored to an untrusted issuer. The hygiene triggers continue to govern every service that is not resting on such a lapsing waiver, exactly as before; only the relative ordering for this specific overlap has moved.


## 4. Adjudication Model


A service's disposition is one of three values — allow, deny, or rotate — and is reached by applying the rules in a fixed order of precedence. The order matters: a service can trip more than one rule, and the governing reason is the first one that applies in the order below. The model is intentionally deterministic so that two reviewers, or a reviewer and a pipeline, reach the same finding from the same evidence.

The highest-precedence check is evidence integrity. If the leaf fingerprint observed on the wire does not match the certificate of record, the service is denied for a chain-of-custody failure, and no waiver — of any type, scope, or currency — changes that outcome. This check comes before everything else.

Next come protocol violations. If the most recent probe shows a protocol, mutual-TLS, or chain violation as defined in §3, the review asks whether an in-force waiver of the matching type and reaching the environment excuses it. If no such cover exists, the service is denied. The reason recorded depends on why cover is absent: if a waiver of the matching type exists but has passed its expiry, the reason is the lapse; if such a waiver was rescinded, the reason is the revocation; otherwise — no waiver at all, the wrong type, or a scope that does not reach the environment — the reason is the violation itself.

If the service has not been denied, the lapsing-waiver rule is applied first, as amended this cycle (§3.5): a protocol violation excused by an in-force waiver that will itself expire within the rotation window pulls the service to rotation with reason `waiver_expiring_soon`, and that determination is made before the hygiene triggers are even consulted. Only a service that is not held up by such a lapsing waiver proceeds to the hygiene assessment (§3.4). There, any hygiene trigger schedules rotation, and the triggers are themselves ordered: imminent expiry is considered first, then under-strength keys, then untrusted issuers. The practical consequence of the amendment is that a service carrying both a lapsing protective waiver and a hygiene defect is reported under the waiver, not the hygiene trigger.

Finally, what remains is an allowance. A service whose only objection was a protocol violation fully and durably excused by an in-force, in-scope waiver is allowed on the strength of that waiver. A service with no objection at all — no integrity problem, no protocol violation, and clean hygiene — is allowed as compliant. Every service resolves to exactly one disposition and one governing reason.


## 5. Threat Model and Rationale


The review's threat model centres on the interconnect graph rather than on any single endpoint. A transport weakness is rarely catastrophic in isolation; it becomes material when a trusted caller inherits the weakness transitively. That is why protocol floors apply uniformly and why issuer governance is enforced even where a chain validates today.

Downgrade resistance is a first-class concern. An endpoint that will still negotiate a legacy protocol offers an attacker a cheaper path than breaking a modern one, and the existence of the option is the exposure regardless of whether it is exercised in normal traffic. The allow-list exists to remove the option, not merely to discourage it.

Client-authentication assurance underpins the production trust boundary. Where mutual TLS is mandatory, the absence of a presented client certificate means a caller that should have proven itself did not, and the review treats that as a control failure rather than a cosmetic gap. Outside that boundary the same absence is unremarkable.

Key-material strength and certificate lifetime are slower-moving risks that the review nonetheless takes seriously, because rotation work is cheapest when scheduled and most expensive when forced by an outage or a compromise. The rotation window is sized to give owners room to act before either pressure arrives.

Finally, evidence integrity is treated as foundational. If the review cannot trust that the certificate it is reasoning about is the one actually served, every downstream conclusion is suspect. That is why a fingerprint disagreement is escalated rather than absorbed, and why no exception is allowed to paper over it.


## 6. Findings Overview

The review resolves to 6 allowances, 13 denials, and 14 rotations. The denials are dominated by lapsed and rescinded exceptions and by a handful of integrity failures; the rotations are split between certificates near expiry, under-strength keys, untrusted issuers, and a few services whose protective waivers are about to lapse. The allowances are a mix of fully compliant services and services resting on an exception that is both in force and comfortably in date.

The per-service detail required to reproduce these totals is distributed across Appendix A (the service dossiers, which carry each waiver's type, scope, and lifecycle) and the inventory database (which carries the certificate facts and the captured probe evidence). Appendix G restates the precedence so the reproduction can be mechanised.


## Appendix A — Service Dossiers

One dossier per in-scope service, in inventory order. Each dossier records the service's role and ownership and, decisively, its waiver context: the type and scope of any exception, its grant and expiry dates, and whether it was later rescinded. The dossiers do not state a disposition; that is reproduced from this context, the configuration set, and the inventory database.

### svc-001 — mariner-edge-gateway

ALPN negotiation at mariner-edge-gateway was noted to confirm the application protocol riding over the tunnel, but protocol-version policy is enforced at the TLS layer and does not bend to the application above it. A modern application protocol over a legacy transport is still a transport finding for mariner-edge-gateway.

Finally, mariner-edge-gateway was checked for consistency between its environment label and its exposure. A service labelled prod is assessed under the rules for that environment; the review does not reclassify a surface to soften a finding, and team-edge retains the route to reclassification through inventory governance rather than through this review.

Exception status. mariner-edge-gateway (svc-001) carries no transport-security waiver of any kind in the register — no protocol exception, no mutual-TLS carve-out, and no chain exception. It is therefore assessed directly against the operative policy, with the captured evidence in the inventory database standing as the sole record of how the prod endpoint actually negotiated.

The harness recorded the mariner-edge-gateway endpoint over successive sweeps; only the most recent capture per service is treated as authoritative, since earlier sweeps frequently predate a remediation or a re-issue. Reviewers are reminded that the captured negotiation outcomes, the chain-validation result, and the leaf fingerprint seen on the wire are held in the inventory database and must be read from there, not inferred from this narrative.

Revocation freshness was considered for mariner-edge-gateway. The review notes whether the endpoint's stapled status was recent and whether the validating party had a live path to revocation information, but treats stapling hygiene as advisory this cycle; the governing chain question remains whether the presented chain validated to a trusted anchor at capture time.

Where mariner-edge-gateway terminates TLS at a sidecar or a shared load balancer rather than in the application process, the review attributes the captured posture to the service as exposed on https://edge-gateway.prod.mariner.internal. Termination topology is an implementation detail; the obligation to meet policy attaches to the exposed prod surface regardless of which component holds the key.

Encrypted-client-hello readiness for mariner-edge-gateway was recorded as informational. ECH changes what an on-path observer can see about the handshake to https://edge-gateway.prod.mariner.internal but does not alter any graded axis here; it neither relaxes the protocol floor nor changes how a client certificate or a chain is judged.

Ownership context: team-edge maintains mariner-edge-gateway and is the counterparty for any remediation. The review records owning teams so that rotation and re-issuance work lands with the group that can actually schedule a maintenance window on the prod surface, but ownership confers no relief from policy.

Cross-signing arrangements that touch mariner-edge-gateway's issuer were enumerated to make sure the chain the review reasons about is the chain clients actually build. A leaf can validate via more than one path; the governed question for mariner-edge-gateway is whether the issuer of record sits in the trust anchor set, independent of which cross-signed path a particular client happens to choose.

Renewal automation for mariner-edge-gateway was reviewed at the level of 'does a pipeline exist', not 'did it run'. An ACME-style renewal loop lowers the operational cost of the rotation findings this review may raise, but the disposition is taken from the captured state of https://edge-gateway.prod.mariner.internal, so a renewal that is configured but not yet effective does not pre-empt a near-expiry finding.

Certificate lifetime is the other half of hygiene. A leaf approaching its not-after boundary inside the rotation window is scheduled for replacement well ahead of the cliff, on the principle that a lapse on the prod surface is an availability incident as much as a security one. The window is uniform across services so that nothing in mariner-edge-gateway's profile earns special treatment.

SNI and virtual-host disambiguation were verified for mariner-edge-gateway so that the captured leaf is unambiguously the one https://edge-gateway.prod.mariner.internal intends to serve. A mismatch between the requested name and the served certificate would itself be an integrity concern, which is one more reason the observed fingerprint is compared against the inventory of record rather than assumed.

The review explicitly separated configuration intent from observed behaviour for mariner-edge-gateway. A configuration file may declare a strict posture, but if the captured evidence on https://edge-gateway.prod.mariner.internal shows otherwise, the evidence governs the finding; conversely a permissive-looking configuration that nonetheless negotiated within policy is judged on what actually happened on the wire.

Within the review boundary, mariner-edge-gateway (svc-001) terminates external traffic at the perimeter and fans it into the mesh. It is owned by team-edge and presents on https://edge-gateway.prod.mariner.internal, which the inventory classifies as a prod surface. The transport posture of any prod endpoint is weighed against the operative policy rather than against historical convention, and the assessment proceeds from the evidence of record rather than from operator attestation.

Documentation for mariner-edge-gateway was cross-checked against the configuration set. Where a policy value is needed — the rotation window, the protocol allow-list, the key floors, or the issuer anchor set — it is read from the validated configuration rather than from this prose, which paraphrases policy for the reader's convenience only.

For mesh participants such as mariner-edge-gateway, certificate rotation is automated through the issuing control plane, which lowers the cost of a rotation finding but does not remove the obligation: an automated rotation that has not yet run still leaves a soon-to-expire leaf on https://edge-gateway.prod.mariner.internal, and the review grades the state at capture time, not the intention encoded in automation.

Revocation-list distribution touching mariner-edge-gateway's issuer was sanity-checked so that a client choosing CRL over stapled status still has a path. As with stapling, the review treats CRL reachability as advisory this cycle; the governing question for mariner-edge-gateway remains whether the presented chain validated at capture time.

Evidence handling for mariner-edge-gateway is deliberately conservative. When the fingerprint observed on the wire disagrees with the inventory of record, the review does not attempt to reconcile the two in the agent's favour; the disagreement is itself the finding, and it is escalated rather than waived, regardless of any paperwork that might otherwise have applied.

Key-ceremony provenance for mariner-edge-gateway's material was reviewed at a high level. Where team-edge can attest that the private key was generated and held in a hardware security module, the operational risk of the key is lower, but provenance does not raise an under-strength key above the floor or extend a certificate past its not-after date.

Wildcard usage at mariner-edge-gateway was noted where present. A wildcard leaf broadens blast radius if its key is compromised, so although a wildcard is not itself a finding, it raises the priority of the hygiene rules for mariner-edge-gateway — a near-expiry or under-strength wildcard is a rotation the review would rather see scheduled sooner than later.

Key strength for mariner-edge-gateway is judged against the floor for its algorithm family. The review does not grade keys on a curve: a key below the floor is a rotation finding irrespective of the sensitivity of the workload, because under-strength material weakens the whole interconnect graph that mariner-edge-gateway participates in.

Session resumption behaviour for mariner-edge-gateway was characterised so that repeat captures could be compared fairly. Resumption can mask a renegotiated parameter, so the harness records full-handshake outcomes where it can; the authoritative capture for mariner-edge-gateway is still the most recent row, and resumption never changes which row is current.

Audit retention for mariner-edge-gateway's captures follows the standard schedule: every sweep is retained, and the review reads the latest. This matters when reconstructing a finding months later — the row that was current at review time is identifiable by its capture timestamp, and the reconstruction must use that row rather than whatever happens to be newest at reconstruction time.

Certificate pinning by clients of mariner-edge-gateway was inventoried lightly, because pinning interacts badly with rotation: a pinned client can break when mariner-edge-gateway legitimately rotates. The review's rotation findings therefore come with a reminder that any pin held against mariner-edge-gateway's current leaf must be updated in lockstep with the re-issue.

Operationally, mariner-edge-gateway has been stable, but stability is not conformance. The review separates 'has not failed yet' from 'meets policy today', and it is the latter that governs the finding. Where the captured evidence and the live configuration disagree, the captured evidence is taken as the ground truth.

Forward-looking, the review recorded whether mariner-edge-gateway is on a path toward post-quantum-ready key exchange. This cycle treats PQC readiness as informational; it changes no disposition, but it is captured so that team-edge can sequence the work against the rotation cadence the hygiene rules already impose.

Clock discipline was assumed but noted for mariner-edge-gateway: certificate validity windows are only meaningful if the validating hosts agree on the time. The review reasons about not-after relative to a single fixed review date, which removes any ambiguity that wall-clock skew on individual probers might otherwise introduce into the near-expiry judgement.

The protocol floor matters for mariner-edge-gateway because a single tolerated downgrade becomes a precedent. The review treats any negotiated version outside the allowed set as a finding in every environment, including development, so that a sandbox habit does not migrate into production by copy-paste.

Transport strictness headers on responses from mariner-edge-gateway were observed where applicable. Strict-transport signalling reduces downgrade opportunity for browser clients but does not substitute for the server-side protocol floor; the review credits it as defence in depth and nothing more for a prod surface.

Subject-alternative-name coverage on mariner-edge-gateway's leaf was checked against the hostnames https://edge-gateway.prod.mariner.internal actually answers for. A name not covered by the served certificate would surface as a verification failure in the capture, so SAN gaps tend to show up indirectly through the recorded verification outcome rather than as a separate graded axis.

For mariner-edge-gateway, issuer trust is a policy question settled against the maintained anchor set rather than the popularity of a commercial authority. The specific issuer and key parameters of mariner-edge-gateway's certificate of record are carried in the inventory database; what matters to the review is whether that issuer sits inside the governed anchor set, since a leaf that validates today but chains outside the set is still a rotation candidate on governance grounds.

Cipher-suite selection at mariner-edge-gateway was inspected for obviously deprecated constructions. While suite negotiation is not itself a graded axis in this review, a modern protocol version on https://edge-gateway.prod.mariner.internal strongly constrains the suite space, which is part of why the version allow-list does so much of the work and why a downgrade is treated as consequential rather than cosmetic.

Partner-facing exposure was a specific consideration for mariner-edge-gateway where federated third parties consume it. Federation raises the stakes of a mutual-TLS gap because the counterparty's assurance depends on it, which is why a production federation surface is held to the client-authentication expectation without sympathy for integration convenience.

Early-data exposure for mariner-edge-gateway was considered where 0-RTT resumption is enabled. Replayable early data is an application-layer hazard rather than a transport-policy axis, so it does not move mariner-edge-gateway's disposition, but it is flagged for team-edge as a design note to weigh against the latency benefit on the prod surface.

The mariner-edge-gateway interconnect was modelled as part of the broader dependency graph. A weakness here propagates to every caller that trusts this endpoint, which is why the review resists the temptation to treat terminates external traffic at the perimeter and fans it into the mesh as a low-stakes carve-out. The posture is assessed on its own merits and against the same bar as the busiest production path.

Certificate-transparency presence for mariner-edge-gateway's leaf was checked as a tamper-evidence signal. CT inclusion does not by itself make a certificate compliant — it is neither a protocol version nor an issuer-trust decision — but its absence on a publicly reachable prod endpoint would be a flag worth a follow-up outside this review's transport remit.

Truststore management on the prod side of mariner-edge-gateway matters for mutual TLS. Where the endpoint demands a client certificate, the set of client anchors it accepts is an operational concern for team-edge; the review records only whether a client certificate was presented and validated, leaving truststore curation to the owning team's runbooks.

Mutual TLS expectations for mariner-edge-gateway follow the environment. The production trust boundary requires a client certificate; a non-production surface is not penalised for the absence of one. Where mariner-edge-gateway is expected to present a client certificate and the capture shows none, the gap is a protocol-level finding unless a waiver of the matching kind and scope is in force.

### svc-002 — mariner-auth-broker

Wildcard usage at mariner-auth-broker was noted where present. A wildcard leaf broadens blast radius if its key is compromised, so although a wildcard is not itself a finding, it raises the priority of the hygiene rules for mariner-auth-broker — a near-expiry or under-strength wildcard is a rotation the review would rather see scheduled sooner than later.

Key strength for mariner-auth-broker is judged against the floor for its algorithm family. The review does not grade keys on a curve: a key below the floor is a rotation finding irrespective of the sensitivity of the workload, because under-strength material weakens the whole interconnect graph that mariner-auth-broker participates in.

Session resumption behaviour for mariner-auth-broker was characterised so that repeat captures could be compared fairly. Resumption can mask a renegotiated parameter, so the harness records full-handshake outcomes where it can; the authoritative capture for mariner-auth-broker is still the most recent row, and resumption never changes which row is current.

Exception status. mariner-auth-broker (svc-002) holds waiver WV-2026-002, a transport-protocol exception scoped to the service's entire footprint across every environment. The register shows it granted on 2026-02-01 with a nominal expiry of 2026-12-01. The register carries WV-2026-002 as granted and in force as written; whether it still provides cover at review time is a separate question, settled by reading the policy review date against the recorded expiry, and by checking that the scope actually reaches the staging surface under assessment.

Audit retention for mariner-auth-broker's captures follows the standard schedule: every sweep is retained, and the review reads the latest. This matters when reconstructing a finding months later — the row that was current at review time is identifiable by its capture timestamp, and the reconstruction must use that row rather than whatever happens to be newest at reconstruction time.

Certificate pinning by clients of mariner-auth-broker was inventoried lightly, because pinning interacts badly with rotation: a pinned client can break when mariner-auth-broker legitimately rotates. The review's rotation findings therefore come with a reminder that any pin held against mariner-auth-broker's current leaf must be updated in lockstep with the re-issue.

Operationally, mariner-auth-broker has been stable, but stability is not conformance. The review separates 'has not failed yet' from 'meets policy today', and it is the latter that governs the finding. Where the captured evidence and the live configuration disagree, the captured evidence is taken as the ground truth.

Forward-looking, the review recorded whether mariner-auth-broker is on a path toward post-quantum-ready key exchange. This cycle treats PQC readiness as informational; it changes no disposition, but it is captured so that team-identity can sequence the work against the rotation cadence the hygiene rules already impose.

Clock discipline was assumed but noted for mariner-auth-broker: certificate validity windows are only meaningful if the validating hosts agree on the time. The review reasons about not-after relative to a single fixed review date, which removes any ambiguity that wall-clock skew on individual probers might otherwise introduce into the near-expiry judgement.

The protocol floor matters for mariner-auth-broker because a single tolerated downgrade becomes a precedent. The review treats any negotiated version outside the allowed set as a finding in every environment, including development, so that a sandbox habit does not migrate into production by copy-paste.

Transport strictness headers on responses from mariner-auth-broker were observed where applicable. Strict-transport signalling reduces downgrade opportunity for browser clients but does not substitute for the server-side protocol floor; the review credits it as defence in depth and nothing more for a staging surface.

Subject-alternative-name coverage on mariner-auth-broker's leaf was checked against the hostnames https://auth-broker.staging.mariner.internal actually answers for. A name not covered by the served certificate would surface as a verification failure in the capture, so SAN gaps tend to show up indirectly through the recorded verification outcome rather than as a separate graded axis.

For mariner-auth-broker, issuer trust is a policy question settled against the maintained anchor set rather than the popularity of a commercial authority. The specific issuer and key parameters of mariner-auth-broker's certificate of record are carried in the inventory database; what matters to the review is whether that issuer sits inside the governed anchor set, since a leaf that validates today but chains outside the set is still a rotation candidate on governance grounds.

Cipher-suite selection at mariner-auth-broker was inspected for obviously deprecated constructions. While suite negotiation is not itself a graded axis in this review, a modern protocol version on https://auth-broker.staging.mariner.internal strongly constrains the suite space, which is part of why the version allow-list does so much of the work and why a downgrade is treated as consequential rather than cosmetic.

Partner-facing exposure was a specific consideration for mariner-auth-broker where federated third parties consume it. Federation raises the stakes of a mutual-TLS gap because the counterparty's assurance depends on it, which is why a production federation surface is held to the client-authentication expectation without sympathy for integration convenience.

Early-data exposure for mariner-auth-broker was considered where 0-RTT resumption is enabled. Replayable early data is an application-layer hazard rather than a transport-policy axis, so it does not move mariner-auth-broker's disposition, but it is flagged for team-identity as a design note to weigh against the latency benefit on the staging surface.

The mariner-auth-broker interconnect was modelled as part of the broader dependency graph. A weakness here propagates to every caller that trusts this endpoint, which is why the review resists the temptation to treat issues and validates session assertions for downstream callers as a low-stakes carve-out. The posture is assessed on its own merits and against the same bar as the busiest production path.

Certificate-transparency presence for mariner-auth-broker's leaf was checked as a tamper-evidence signal. CT inclusion does not by itself make a certificate compliant — it is neither a protocol version nor an issuer-trust decision — but its absence on a publicly reachable staging endpoint would be a flag worth a follow-up outside this review's transport remit.

Truststore management on the staging side of mariner-auth-broker matters for mutual TLS. Where the endpoint demands a client certificate, the set of client anchors it accepts is an operational concern for team-identity; the review records only whether a client certificate was presented and validated, leaving truststore curation to the owning team's runbooks.

Mutual TLS expectations for mariner-auth-broker follow the environment. The production trust boundary requires a client certificate; a non-production surface is not penalised for the absence of one. Where mariner-auth-broker is expected to present a client certificate and the capture shows none, the gap is a protocol-level finding unless a waiver of the matching kind and scope is in force.

ALPN negotiation at mariner-auth-broker was noted to confirm the application protocol riding over the tunnel, but protocol-version policy is enforced at the TLS layer and does not bend to the application above it. A modern application protocol over a legacy transport is still a transport finding for mariner-auth-broker.

Finally, mariner-auth-broker was checked for consistency between its environment label and its exposure. A service labelled staging is assessed under the rules for that environment; the review does not reclassify a surface to soften a finding, and team-identity retains the route to reclassification through inventory governance rather than through this review.

The harness recorded the mariner-auth-broker endpoint over successive sweeps; only the most recent capture per service is treated as authoritative, since earlier sweeps frequently predate a remediation or a re-issue. Reviewers are reminded that the captured negotiation outcomes, the chain-validation result, and the leaf fingerprint seen on the wire are held in the inventory database and must be read from there, not inferred from this narrative.

Revocation freshness was considered for mariner-auth-broker. The review notes whether the endpoint's stapled status was recent and whether the validating party had a live path to revocation information, but treats stapling hygiene as advisory this cycle; the governing chain question remains whether the presented chain validated to a trusted anchor at capture time.

Where mariner-auth-broker terminates TLS at a sidecar or a shared load balancer rather than in the application process, the review attributes the captured posture to the service as exposed on https://auth-broker.staging.mariner.internal. Termination topology is an implementation detail; the obligation to meet policy attaches to the exposed staging surface regardless of which component holds the key.

Encrypted-client-hello readiness for mariner-auth-broker was recorded as informational. ECH changes what an on-path observer can see about the handshake to https://auth-broker.staging.mariner.internal but does not alter any graded axis here; it neither relaxes the protocol floor nor changes how a client certificate or a chain is judged.

Ownership context: team-identity maintains mariner-auth-broker and is the counterparty for any remediation. The review records owning teams so that rotation and re-issuance work lands with the group that can actually schedule a maintenance window on the staging surface, but ownership confers no relief from policy.

Cross-signing arrangements that touch mariner-auth-broker's issuer were enumerated to make sure the chain the review reasons about is the chain clients actually build. A leaf can validate via more than one path; the governed question for mariner-auth-broker is whether the issuer of record sits in the trust anchor set, independent of which cross-signed path a particular client happens to choose.

Renewal automation for mariner-auth-broker was reviewed at the level of 'does a pipeline exist', not 'did it run'. An ACME-style renewal loop lowers the operational cost of the rotation findings this review may raise, but the disposition is taken from the captured state of https://auth-broker.staging.mariner.internal, so a renewal that is configured but not yet effective does not pre-empt a near-expiry finding.

Certificate lifetime is the other half of hygiene. A leaf approaching its not-after boundary inside the rotation window is scheduled for replacement well ahead of the cliff, on the principle that a lapse on the staging surface is an availability incident as much as a security one. The window is uniform across services so that nothing in mariner-auth-broker's profile earns special treatment.

SNI and virtual-host disambiguation were verified for mariner-auth-broker so that the captured leaf is unambiguously the one https://auth-broker.staging.mariner.internal intends to serve. A mismatch between the requested name and the served certificate would itself be an integrity concern, which is one more reason the observed fingerprint is compared against the inventory of record rather than assumed.

The review explicitly separated configuration intent from observed behaviour for mariner-auth-broker. A configuration file may declare a strict posture, but if the captured evidence on https://auth-broker.staging.mariner.internal shows otherwise, the evidence governs the finding; conversely a permissive-looking configuration that nonetheless negotiated within policy is judged on what actually happened on the wire.

Within the review boundary, mariner-auth-broker (svc-002) issues and validates session assertions for downstream callers. It is owned by team-identity and presents on https://auth-broker.staging.mariner.internal, which the inventory classifies as a staging surface. The transport posture of any staging endpoint is weighed against the operative policy rather than against historical convention, and the assessment proceeds from the evidence of record rather than from operator attestation.

Documentation for mariner-auth-broker was cross-checked against the configuration set. Where a policy value is needed — the rotation window, the protocol allow-list, the key floors, or the issuer anchor set — it is read from the validated configuration rather than from this prose, which paraphrases policy for the reader's convenience only.

For mesh participants such as mariner-auth-broker, certificate rotation is automated through the issuing control plane, which lowers the cost of a rotation finding but does not remove the obligation: an automated rotation that has not yet run still leaves a soon-to-expire leaf on https://auth-broker.staging.mariner.internal, and the review grades the state at capture time, not the intention encoded in automation.

Revocation-list distribution touching mariner-auth-broker's issuer was sanity-checked so that a client choosing CRL over stapled status still has a path. As with stapling, the review treats CRL reachability as advisory this cycle; the governing question for mariner-auth-broker remains whether the presented chain validated at capture time.

Evidence handling for mariner-auth-broker is deliberately conservative. When the fingerprint observed on the wire disagrees with the inventory of record, the review does not attempt to reconcile the two in the agent's favour; the disagreement is itself the finding, and it is escalated rather than waived, regardless of any paperwork that might otherwise have applied.

Key-ceremony provenance for mariner-auth-broker's material was reviewed at a high level. Where team-identity can attest that the private key was generated and held in a hardware security module, the operational risk of the key is lower, but provenance does not raise an under-strength key above the floor or extend a certificate past its not-after date.

### svc-003 — mariner-billing-api

Mutual TLS expectations for mariner-billing-api follow the environment. The production trust boundary requires a client certificate; a non-production surface is not penalised for the absence of one. Where mariner-billing-api is expected to present a client certificate and the capture shows none, the gap is a protocol-level finding unless a waiver of the matching kind and scope is in force.

Exception status. mariner-billing-api (svc-003) holds waiver WV-2026-003, a transport-protocol exception scoped to the service's entire footprint across every environment. The register shows it granted on 2026-01-15 with a nominal expiry of 2026-05-01. The register carries WV-2026-003 as granted and in force as written; whether it still provides cover at review time is a separate question, settled by reading the policy review date against the recorded expiry, and by checking that the scope actually reaches the prod surface under assessment.

ALPN negotiation at mariner-billing-api was noted to confirm the application protocol riding over the tunnel, but protocol-version policy is enforced at the TLS layer and does not bend to the application above it. A modern application protocol over a legacy transport is still a transport finding for mariner-billing-api.

Finally, mariner-billing-api was checked for consistency between its environment label and its exposure. A service labelled prod is assessed under the rules for that environment; the review does not reclassify a surface to soften a finding, and team-billing retains the route to reclassification through inventory governance rather than through this review.

The harness recorded the mariner-billing-api endpoint over successive sweeps; only the most recent capture per service is treated as authoritative, since earlier sweeps frequently predate a remediation or a re-issue. Reviewers are reminded that the captured negotiation outcomes, the chain-validation result, and the leaf fingerprint seen on the wire are held in the inventory database and must be read from there, not inferred from this narrative.

Revocation freshness was considered for mariner-billing-api. The review notes whether the endpoint's stapled status was recent and whether the validating party had a live path to revocation information, but treats stapling hygiene as advisory this cycle; the governing chain question remains whether the presented chain validated to a trusted anchor at capture time.

Where mariner-billing-api terminates TLS at a sidecar or a shared load balancer rather than in the application process, the review attributes the captured posture to the service as exposed on https://billing-api.prod.mariner.internal. Termination topology is an implementation detail; the obligation to meet policy attaches to the exposed prod surface regardless of which component holds the key.

Encrypted-client-hello readiness for mariner-billing-api was recorded as informational. ECH changes what an on-path observer can see about the handshake to https://billing-api.prod.mariner.internal but does not alter any graded axis here; it neither relaxes the protocol floor nor changes how a client certificate or a chain is judged.

Ownership context: team-billing maintains mariner-billing-api and is the counterparty for any remediation. The review records owning teams so that rotation and re-issuance work lands with the group that can actually schedule a maintenance window on the prod surface, but ownership confers no relief from policy.

Cross-signing arrangements that touch mariner-billing-api's issuer were enumerated to make sure the chain the review reasons about is the chain clients actually build. A leaf can validate via more than one path; the governed question for mariner-billing-api is whether the issuer of record sits in the trust anchor set, independent of which cross-signed path a particular client happens to choose.

Renewal automation for mariner-billing-api was reviewed at the level of 'does a pipeline exist', not 'did it run'. An ACME-style renewal loop lowers the operational cost of the rotation findings this review may raise, but the disposition is taken from the captured state of https://billing-api.prod.mariner.internal, so a renewal that is configured but not yet effective does not pre-empt a near-expiry finding.

Certificate lifetime is the other half of hygiene. A leaf approaching its not-after boundary inside the rotation window is scheduled for replacement well ahead of the cliff, on the principle that a lapse on the prod surface is an availability incident as much as a security one. The window is uniform across services so that nothing in mariner-billing-api's profile earns special treatment.

SNI and virtual-host disambiguation were verified for mariner-billing-api so that the captured leaf is unambiguously the one https://billing-api.prod.mariner.internal intends to serve. A mismatch between the requested name and the served certificate would itself be an integrity concern, which is one more reason the observed fingerprint is compared against the inventory of record rather than assumed.

The review explicitly separated configuration intent from observed behaviour for mariner-billing-api. A configuration file may declare a strict posture, but if the captured evidence on https://billing-api.prod.mariner.internal shows otherwise, the evidence governs the finding; conversely a permissive-looking configuration that nonetheless negotiated within policy is judged on what actually happened on the wire.

Within the review boundary, mariner-billing-api (svc-003) settles metered usage into the revenue ledger. It is owned by team-billing and presents on https://billing-api.prod.mariner.internal, which the inventory classifies as a prod surface. The transport posture of any prod endpoint is weighed against the operative policy rather than against historical convention, and the assessment proceeds from the evidence of record rather than from operator attestation.

Documentation for mariner-billing-api was cross-checked against the configuration set. Where a policy value is needed — the rotation window, the protocol allow-list, the key floors, or the issuer anchor set — it is read from the validated configuration rather than from this prose, which paraphrases policy for the reader's convenience only.

For mesh participants such as mariner-billing-api, certificate rotation is automated through the issuing control plane, which lowers the cost of a rotation finding but does not remove the obligation: an automated rotation that has not yet run still leaves a soon-to-expire leaf on https://billing-api.prod.mariner.internal, and the review grades the state at capture time, not the intention encoded in automation.

Revocation-list distribution touching mariner-billing-api's issuer was sanity-checked so that a client choosing CRL over stapled status still has a path. As with stapling, the review treats CRL reachability as advisory this cycle; the governing question for mariner-billing-api remains whether the presented chain validated at capture time.

Evidence handling for mariner-billing-api is deliberately conservative. When the fingerprint observed on the wire disagrees with the inventory of record, the review does not attempt to reconcile the two in the agent's favour; the disagreement is itself the finding, and it is escalated rather than waived, regardless of any paperwork that might otherwise have applied.

Key-ceremony provenance for mariner-billing-api's material was reviewed at a high level. Where team-billing can attest that the private key was generated and held in a hardware security module, the operational risk of the key is lower, but provenance does not raise an under-strength key above the floor or extend a certificate past its not-after date.

Wildcard usage at mariner-billing-api was noted where present. A wildcard leaf broadens blast radius if its key is compromised, so although a wildcard is not itself a finding, it raises the priority of the hygiene rules for mariner-billing-api — a near-expiry or under-strength wildcard is a rotation the review would rather see scheduled sooner than later.

Key strength for mariner-billing-api is judged against the floor for its algorithm family. The review does not grade keys on a curve: a key below the floor is a rotation finding irrespective of the sensitivity of the workload, because under-strength material weakens the whole interconnect graph that mariner-billing-api participates in.

Session resumption behaviour for mariner-billing-api was characterised so that repeat captures could be compared fairly. Resumption can mask a renegotiated parameter, so the harness records full-handshake outcomes where it can; the authoritative capture for mariner-billing-api is still the most recent row, and resumption never changes which row is current.

Audit retention for mariner-billing-api's captures follows the standard schedule: every sweep is retained, and the review reads the latest. This matters when reconstructing a finding months later — the row that was current at review time is identifiable by its capture timestamp, and the reconstruction must use that row rather than whatever happens to be newest at reconstruction time.

Certificate pinning by clients of mariner-billing-api was inventoried lightly, because pinning interacts badly with rotation: a pinned client can break when mariner-billing-api legitimately rotates. The review's rotation findings therefore come with a reminder that any pin held against mariner-billing-api's current leaf must be updated in lockstep with the re-issue.

Operationally, mariner-billing-api has been stable, but stability is not conformance. The review separates 'has not failed yet' from 'meets policy today', and it is the latter that governs the finding. Where the captured evidence and the live configuration disagree, the captured evidence is taken as the ground truth.

Forward-looking, the review recorded whether mariner-billing-api is on a path toward post-quantum-ready key exchange. This cycle treats PQC readiness as informational; it changes no disposition, but it is captured so that team-billing can sequence the work against the rotation cadence the hygiene rules already impose.

Clock discipline was assumed but noted for mariner-billing-api: certificate validity windows are only meaningful if the validating hosts agree on the time. The review reasons about not-after relative to a single fixed review date, which removes any ambiguity that wall-clock skew on individual probers might otherwise introduce into the near-expiry judgement.

The protocol floor matters for mariner-billing-api because a single tolerated downgrade becomes a precedent. The review treats any negotiated version outside the allowed set as a finding in every environment, including development, so that a sandbox habit does not migrate into production by copy-paste.

Transport strictness headers on responses from mariner-billing-api were observed where applicable. Strict-transport signalling reduces downgrade opportunity for browser clients but does not substitute for the server-side protocol floor; the review credits it as defence in depth and nothing more for a prod surface.

Subject-alternative-name coverage on mariner-billing-api's leaf was checked against the hostnames https://billing-api.prod.mariner.internal actually answers for. A name not covered by the served certificate would surface as a verification failure in the capture, so SAN gaps tend to show up indirectly through the recorded verification outcome rather than as a separate graded axis.

For mariner-billing-api, issuer trust is a policy question settled against the maintained anchor set rather than the popularity of a commercial authority. The specific issuer and key parameters of mariner-billing-api's certificate of record are carried in the inventory database; what matters to the review is whether that issuer sits inside the governed anchor set, since a leaf that validates today but chains outside the set is still a rotation candidate on governance grounds.

Cipher-suite selection at mariner-billing-api was inspected for obviously deprecated constructions. While suite negotiation is not itself a graded axis in this review, a modern protocol version on https://billing-api.prod.mariner.internal strongly constrains the suite space, which is part of why the version allow-list does so much of the work and why a downgrade is treated as consequential rather than cosmetic.

Partner-facing exposure was a specific consideration for mariner-billing-api where federated third parties consume it. Federation raises the stakes of a mutual-TLS gap because the counterparty's assurance depends on it, which is why a production federation surface is held to the client-authentication expectation without sympathy for integration convenience.

Early-data exposure for mariner-billing-api was considered where 0-RTT resumption is enabled. Replayable early data is an application-layer hazard rather than a transport-policy axis, so it does not move mariner-billing-api's disposition, but it is flagged for team-billing as a design note to weigh against the latency benefit on the prod surface.

The mariner-billing-api interconnect was modelled as part of the broader dependency graph. A weakness here propagates to every caller that trusts this endpoint, which is why the review resists the temptation to treat settles metered usage into the revenue ledger as a low-stakes carve-out. The posture is assessed on its own merits and against the same bar as the busiest production path.

Certificate-transparency presence for mariner-billing-api's leaf was checked as a tamper-evidence signal. CT inclusion does not by itself make a certificate compliant — it is neither a protocol version nor an issuer-trust decision — but its absence on a publicly reachable prod endpoint would be a flag worth a follow-up outside this review's transport remit.

Truststore management on the prod side of mariner-billing-api matters for mutual TLS. Where the endpoint demands a client certificate, the set of client anchors it accepts is an operational concern for team-billing; the review records only whether a client certificate was presented and validated, leaving truststore curation to the owning team's runbooks.

### svc-004 — mariner-fulfillment

Key-ceremony provenance for mariner-fulfillment's material was reviewed at a high level. Where team-logistics can attest that the private key was generated and held in a hardware security module, the operational risk of the key is lower, but provenance does not raise an under-strength key above the floor or extend a certificate past its not-after date.

Wildcard usage at mariner-fulfillment was noted where present. A wildcard leaf broadens blast radius if its key is compromised, so although a wildcard is not itself a finding, it raises the priority of the hygiene rules for mariner-fulfillment — a near-expiry or under-strength wildcard is a rotation the review would rather see scheduled sooner than later.

Exception status. mariner-fulfillment (svc-004) holds waiver WV-2026-004, a mutual-TLS exception scoped to the production listener only. The register shows it granted on 2026-01-20 with a nominal expiry of 2026-04-30. The register carries WV-2026-004 as granted and in force as written; whether it still provides cover at review time is a separate question, settled by reading the policy review date against the recorded expiry, and by checking that the scope actually reaches the prod surface under assessment.

Key strength for mariner-fulfillment is judged against the floor for its algorithm family. The review does not grade keys on a curve: a key below the floor is a rotation finding irrespective of the sensitivity of the workload, because under-strength material weakens the whole interconnect graph that mariner-fulfillment participates in.

Session resumption behaviour for mariner-fulfillment was characterised so that repeat captures could be compared fairly. Resumption can mask a renegotiated parameter, so the harness records full-handshake outcomes where it can; the authoritative capture for mariner-fulfillment is still the most recent row, and resumption never changes which row is current.

Audit retention for mariner-fulfillment's captures follows the standard schedule: every sweep is retained, and the review reads the latest. This matters when reconstructing a finding months later — the row that was current at review time is identifiable by its capture timestamp, and the reconstruction must use that row rather than whatever happens to be newest at reconstruction time.

Certificate pinning by clients of mariner-fulfillment was inventoried lightly, because pinning interacts badly with rotation: a pinned client can break when mariner-fulfillment legitimately rotates. The review's rotation findings therefore come with a reminder that any pin held against mariner-fulfillment's current leaf must be updated in lockstep with the re-issue.

Operationally, mariner-fulfillment has been stable, but stability is not conformance. The review separates 'has not failed yet' from 'meets policy today', and it is the latter that governs the finding. Where the captured evidence and the live configuration disagree, the captured evidence is taken as the ground truth.

Forward-looking, the review recorded whether mariner-fulfillment is on a path toward post-quantum-ready key exchange. This cycle treats PQC readiness as informational; it changes no disposition, but it is captured so that team-logistics can sequence the work against the rotation cadence the hygiene rules already impose.

Clock discipline was assumed but noted for mariner-fulfillment: certificate validity windows are only meaningful if the validating hosts agree on the time. The review reasons about not-after relative to a single fixed review date, which removes any ambiguity that wall-clock skew on individual probers might otherwise introduce into the near-expiry judgement.

The protocol floor matters for mariner-fulfillment because a single tolerated downgrade becomes a precedent. The review treats any negotiated version outside the allowed set as a finding in every environment, including development, so that a sandbox habit does not migrate into production by copy-paste.

Transport strictness headers on responses from mariner-fulfillment were observed where applicable. Strict-transport signalling reduces downgrade opportunity for browser clients but does not substitute for the server-side protocol floor; the review credits it as defence in depth and nothing more for a prod surface.

Subject-alternative-name coverage on mariner-fulfillment's leaf was checked against the hostnames https://fulfillment.prod.mariner.internal actually answers for. A name not covered by the served certificate would surface as a verification failure in the capture, so SAN gaps tend to show up indirectly through the recorded verification outcome rather than as a separate graded axis.

For mariner-fulfillment, issuer trust is a policy question settled against the maintained anchor set rather than the popularity of a commercial authority. The specific issuer and key parameters of mariner-fulfillment's certificate of record are carried in the inventory database; what matters to the review is whether that issuer sits inside the governed anchor set, since a leaf that validates today but chains outside the set is still a rotation candidate on governance grounds.

Cipher-suite selection at mariner-fulfillment was inspected for obviously deprecated constructions. While suite negotiation is not itself a graded axis in this review, a modern protocol version on https://fulfillment.prod.mariner.internal strongly constrains the suite space, which is part of why the version allow-list does so much of the work and why a downgrade is treated as consequential rather than cosmetic.

Partner-facing exposure was a specific consideration for mariner-fulfillment where federated third parties consume it. Federation raises the stakes of a mutual-TLS gap because the counterparty's assurance depends on it, which is why a production federation surface is held to the client-authentication expectation without sympathy for integration convenience.

Early-data exposure for mariner-fulfillment was considered where 0-RTT resumption is enabled. Replayable early data is an application-layer hazard rather than a transport-policy axis, so it does not move mariner-fulfillment's disposition, but it is flagged for team-logistics as a design note to weigh against the latency benefit on the prod surface.

The mariner-fulfillment interconnect was modelled as part of the broader dependency graph. A weakness here propagates to every caller that trusts this endpoint, which is why the review resists the temptation to treat coordinates warehouse hand-off and carrier manifests as a low-stakes carve-out. The posture is assessed on its own merits and against the same bar as the busiest production path.

Certificate-transparency presence for mariner-fulfillment's leaf was checked as a tamper-evidence signal. CT inclusion does not by itself make a certificate compliant — it is neither a protocol version nor an issuer-trust decision — but its absence on a publicly reachable prod endpoint would be a flag worth a follow-up outside this review's transport remit.

Truststore management on the prod side of mariner-fulfillment matters for mutual TLS. Where the endpoint demands a client certificate, the set of client anchors it accepts is an operational concern for team-logistics; the review records only whether a client certificate was presented and validated, leaving truststore curation to the owning team's runbooks.

Mutual TLS expectations for mariner-fulfillment follow the environment. The production trust boundary requires a client certificate; a non-production surface is not penalised for the absence of one. Where mariner-fulfillment is expected to present a client certificate and the capture shows none, the gap is a protocol-level finding unless a waiver of the matching kind and scope is in force.

ALPN negotiation at mariner-fulfillment was noted to confirm the application protocol riding over the tunnel, but protocol-version policy is enforced at the TLS layer and does not bend to the application above it. A modern application protocol over a legacy transport is still a transport finding for mariner-fulfillment.

Finally, mariner-fulfillment was checked for consistency between its environment label and its exposure. A service labelled prod is assessed under the rules for that environment; the review does not reclassify a surface to soften a finding, and team-logistics retains the route to reclassification through inventory governance rather than through this review.

The harness recorded the mariner-fulfillment endpoint over successive sweeps; only the most recent capture per service is treated as authoritative, since earlier sweeps frequently predate a remediation or a re-issue. Reviewers are reminded that the captured negotiation outcomes, the chain-validation result, and the leaf fingerprint seen on the wire are held in the inventory database and must be read from there, not inferred from this narrative.

Revocation freshness was considered for mariner-fulfillment. The review notes whether the endpoint's stapled status was recent and whether the validating party had a live path to revocation information, but treats stapling hygiene as advisory this cycle; the governing chain question remains whether the presented chain validated to a trusted anchor at capture time.

Where mariner-fulfillment terminates TLS at a sidecar or a shared load balancer rather than in the application process, the review attributes the captured posture to the service as exposed on https://fulfillment.prod.mariner.internal. Termination topology is an implementation detail; the obligation to meet policy attaches to the exposed prod surface regardless of which component holds the key.

Encrypted-client-hello readiness for mariner-fulfillment was recorded as informational. ECH changes what an on-path observer can see about the handshake to https://fulfillment.prod.mariner.internal but does not alter any graded axis here; it neither relaxes the protocol floor nor changes how a client certificate or a chain is judged.

Ownership context: team-logistics maintains mariner-fulfillment and is the counterparty for any remediation. The review records owning teams so that rotation and re-issuance work lands with the group that can actually schedule a maintenance window on the prod surface, but ownership confers no relief from policy.

Cross-signing arrangements that touch mariner-fulfillment's issuer were enumerated to make sure the chain the review reasons about is the chain clients actually build. A leaf can validate via more than one path; the governed question for mariner-fulfillment is whether the issuer of record sits in the trust anchor set, independent of which cross-signed path a particular client happens to choose.

Renewal automation for mariner-fulfillment was reviewed at the level of 'does a pipeline exist', not 'did it run'. An ACME-style renewal loop lowers the operational cost of the rotation findings this review may raise, but the disposition is taken from the captured state of https://fulfillment.prod.mariner.internal, so a renewal that is configured but not yet effective does not pre-empt a near-expiry finding.

Certificate lifetime is the other half of hygiene. A leaf approaching its not-after boundary inside the rotation window is scheduled for replacement well ahead of the cliff, on the principle that a lapse on the prod surface is an availability incident as much as a security one. The window is uniform across services so that nothing in mariner-fulfillment's profile earns special treatment.

SNI and virtual-host disambiguation were verified for mariner-fulfillment so that the captured leaf is unambiguously the one https://fulfillment.prod.mariner.internal intends to serve. A mismatch between the requested name and the served certificate would itself be an integrity concern, which is one more reason the observed fingerprint is compared against the inventory of record rather than assumed.

The review explicitly separated configuration intent from observed behaviour for mariner-fulfillment. A configuration file may declare a strict posture, but if the captured evidence on https://fulfillment.prod.mariner.internal shows otherwise, the evidence governs the finding; conversely a permissive-looking configuration that nonetheless negotiated within policy is judged on what actually happened on the wire.

Within the review boundary, mariner-fulfillment (svc-004) coordinates warehouse hand-off and carrier manifests. It is owned by team-logistics and presents on https://fulfillment.prod.mariner.internal, which the inventory classifies as a prod surface. The transport posture of any prod endpoint is weighed against the operative policy rather than against historical convention, and the assessment proceeds from the evidence of record rather than from operator attestation.

Documentation for mariner-fulfillment was cross-checked against the configuration set. Where a policy value is needed — the rotation window, the protocol allow-list, the key floors, or the issuer anchor set — it is read from the validated configuration rather than from this prose, which paraphrases policy for the reader's convenience only.

For mesh participants such as mariner-fulfillment, certificate rotation is automated through the issuing control plane, which lowers the cost of a rotation finding but does not remove the obligation: an automated rotation that has not yet run still leaves a soon-to-expire leaf on https://fulfillment.prod.mariner.internal, and the review grades the state at capture time, not the intention encoded in automation.

Revocation-list distribution touching mariner-fulfillment's issuer was sanity-checked so that a client choosing CRL over stapled status still has a path. As with stapling, the review treats CRL reachability as advisory this cycle; the governing question for mariner-fulfillment remains whether the presented chain validated at capture time.

Evidence handling for mariner-fulfillment is deliberately conservative. When the fingerprint observed on the wire disagrees with the inventory of record, the review does not attempt to reconcile the two in the agent's favour; the disagreement is itself the finding, and it is escalated rather than waived, regardless of any paperwork that might otherwise have applied.

### svc-005 — mariner-telemetry

Truststore management on the prod side of mariner-telemetry matters for mutual TLS. Where the endpoint demands a client certificate, the set of client anchors it accepts is an operational concern for team-observability; the review records only whether a client certificate was presented and validated, leaving truststore curation to the owning team's runbooks.

Mutual TLS expectations for mariner-telemetry follow the environment. The production trust boundary requires a client certificate; a non-production surface is not penalised for the absence of one. Where mariner-telemetry is expected to present a client certificate and the capture shows none, the gap is a protocol-level finding unless a waiver of the matching kind and scope is in force.

ALPN negotiation at mariner-telemetry was noted to confirm the application protocol riding over the tunnel, but protocol-version policy is enforced at the TLS layer and does not bend to the application above it. A modern application protocol over a legacy transport is still a transport finding for mariner-telemetry.

Exception status. mariner-telemetry (svc-005) holds waiver WV-2026-005, a certificate-chain exception scoped to the service's entire footprint across every environment. The register shows it granted on 2026-02-10 with a nominal expiry of 2026-09-01. That exception did not run its course: it was rescinded on 2026-04-15 following incident INC-2026-0418, a mis-issued intermediate traced to a stale cross-sign, and the register now carries WV-2026-005 in a revoked state. A rescinded waiver provides no cover, so the nominal expiry of 2026-09-01 is moot — the underlying posture is judged as though the exception had never issued.

Finally, mariner-telemetry was checked for consistency between its environment label and its exposure. A service labelled prod is assessed under the rules for that environment; the review does not reclassify a surface to soften a finding, and team-observability retains the route to reclassification through inventory governance rather than through this review.

The harness recorded the mariner-telemetry endpoint over successive sweeps; only the most recent capture per service is treated as authoritative, since earlier sweeps frequently predate a remediation or a re-issue. Reviewers are reminded that the captured negotiation outcomes, the chain-validation result, and the leaf fingerprint seen on the wire are held in the inventory database and must be read from there, not inferred from this narrative.

Revocation freshness was considered for mariner-telemetry. The review notes whether the endpoint's stapled status was recent and whether the validating party had a live path to revocation information, but treats stapling hygiene as advisory this cycle; the governing chain question remains whether the presented chain validated to a trusted anchor at capture time.

Where mariner-telemetry terminates TLS at a sidecar or a shared load balancer rather than in the application process, the review attributes the captured posture to the service as exposed on https://telemetry.prod.mariner.internal. Termination topology is an implementation detail; the obligation to meet policy attaches to the exposed prod surface regardless of which component holds the key.

Encrypted-client-hello readiness for mariner-telemetry was recorded as informational. ECH changes what an on-path observer can see about the handshake to https://telemetry.prod.mariner.internal but does not alter any graded axis here; it neither relaxes the protocol floor nor changes how a client certificate or a chain is judged.

Ownership context: team-observability maintains mariner-telemetry and is the counterparty for any remediation. The review records owning teams so that rotation and re-issuance work lands with the group that can actually schedule a maintenance window on the prod surface, but ownership confers no relief from policy.

Cross-signing arrangements that touch mariner-telemetry's issuer were enumerated to make sure the chain the review reasons about is the chain clients actually build. A leaf can validate via more than one path; the governed question for mariner-telemetry is whether the issuer of record sits in the trust anchor set, independent of which cross-signed path a particular client happens to choose.

Renewal automation for mariner-telemetry was reviewed at the level of 'does a pipeline exist', not 'did it run'. An ACME-style renewal loop lowers the operational cost of the rotation findings this review may raise, but the disposition is taken from the captured state of https://telemetry.prod.mariner.internal, so a renewal that is configured but not yet effective does not pre-empt a near-expiry finding.

Certificate lifetime is the other half of hygiene. A leaf approaching its not-after boundary inside the rotation window is scheduled for replacement well ahead of the cliff, on the principle that a lapse on the prod surface is an availability incident as much as a security one. The window is uniform across services so that nothing in mariner-telemetry's profile earns special treatment.

SNI and virtual-host disambiguation were verified for mariner-telemetry so that the captured leaf is unambiguously the one https://telemetry.prod.mariner.internal intends to serve. A mismatch between the requested name and the served certificate would itself be an integrity concern, which is one more reason the observed fingerprint is compared against the inventory of record rather than assumed.

The review explicitly separated configuration intent from observed behaviour for mariner-telemetry. A configuration file may declare a strict posture, but if the captured evidence on https://telemetry.prod.mariner.internal shows otherwise, the evidence governs the finding; conversely a permissive-looking configuration that nonetheless negotiated within policy is judged on what actually happened on the wire.

Within the review boundary, mariner-telemetry (svc-005) ingests high-cardinality metrics from the fleet. It is owned by team-observability and presents on https://telemetry.prod.mariner.internal, which the inventory classifies as a prod surface. The transport posture of any prod endpoint is weighed against the operative policy rather than against historical convention, and the assessment proceeds from the evidence of record rather than from operator attestation.

Documentation for mariner-telemetry was cross-checked against the configuration set. Where a policy value is needed — the rotation window, the protocol allow-list, the key floors, or the issuer anchor set — it is read from the validated configuration rather than from this prose, which paraphrases policy for the reader's convenience only.

For mesh participants such as mariner-telemetry, certificate rotation is automated through the issuing control plane, which lowers the cost of a rotation finding but does not remove the obligation: an automated rotation that has not yet run still leaves a soon-to-expire leaf on https://telemetry.prod.mariner.internal, and the review grades the state at capture time, not the intention encoded in automation.

Revocation-list distribution touching mariner-telemetry's issuer was sanity-checked so that a client choosing CRL over stapled status still has a path. As with stapling, the review treats CRL reachability as advisory this cycle; the governing question for mariner-telemetry remains whether the presented chain validated at capture time.

Evidence handling for mariner-telemetry is deliberately conservative. When the fingerprint observed on the wire disagrees with the inventory of record, the review does not attempt to reconcile the two in the agent's favour; the disagreement is itself the finding, and it is escalated rather than waived, regardless of any paperwork that might otherwise have applied.

Key-ceremony provenance for mariner-telemetry's material was reviewed at a high level. Where team-observability can attest that the private key was generated and held in a hardware security module, the operational risk of the key is lower, but provenance does not raise an under-strength key above the floor or extend a certificate past its not-after date.

Wildcard usage at mariner-telemetry was noted where present. A wildcard leaf broadens blast radius if its key is compromised, so although a wildcard is not itself a finding, it raises the priority of the hygiene rules for mariner-telemetry — a near-expiry or under-strength wildcard is a rotation the review would rather see scheduled sooner than later.

Key strength for mariner-telemetry is judged against the floor for its algorithm family. The review does not grade keys on a curve: a key below the floor is a rotation finding irrespective of the sensitivity of the workload, because under-strength material weakens the whole interconnect graph that mariner-telemetry participates in.

Session resumption behaviour for mariner-telemetry was characterised so that repeat captures could be compared fairly. Resumption can mask a renegotiated parameter, so the harness records full-handshake outcomes where it can; the authoritative capture for mariner-telemetry is still the most recent row, and resumption never changes which row is current.

Audit retention for mariner-telemetry's captures follows the standard schedule: every sweep is retained, and the review reads the latest. This matters when reconstructing a finding months later — the row that was current at review time is identifiable by its capture timestamp, and the reconstruction must use that row rather than whatever happens to be newest at reconstruction time.

Certificate pinning by clients of mariner-telemetry was inventoried lightly, because pinning interacts badly with rotation: a pinned client can break when mariner-telemetry legitimately rotates. The review's rotation findings therefore come with a reminder that any pin held against mariner-telemetry's current leaf must be updated in lockstep with the re-issue.

Operationally, mariner-telemetry has been stable, but stability is not conformance. The review separates 'has not failed yet' from 'meets policy today', and it is the latter that governs the finding. Where the captured evidence and the live configuration disagree, the captured evidence is taken as the ground truth.

Forward-looking, the review recorded whether mariner-telemetry is on a path toward post-quantum-ready key exchange. This cycle treats PQC readiness as informational; it changes no disposition, but it is captured so that team-observability can sequence the work against the rotation cadence the hygiene rules already impose.

Clock discipline was assumed but noted for mariner-telemetry: certificate validity windows are only meaningful if the validating hosts agree on the time. The review reasons about not-after relative to a single fixed review date, which removes any ambiguity that wall-clock skew on individual probers might otherwise introduce into the near-expiry judgement.

The protocol floor matters for mariner-telemetry because a single tolerated downgrade becomes a precedent. The review treats any negotiated version outside the allowed set as a finding in every environment, including development, so that a sandbox habit does not migrate into production by copy-paste.

Transport strictness headers on responses from mariner-telemetry were observed where applicable. Strict-transport signalling reduces downgrade opportunity for browser clients but does not substitute for the server-side protocol floor; the review credits it as defence in depth and nothing more for a prod surface.

Subject-alternative-name coverage on mariner-telemetry's leaf was checked against the hostnames https://telemetry.prod.mariner.internal actually answers for. A name not covered by the served certificate would surface as a verification failure in the capture, so SAN gaps tend to show up indirectly through the recorded verification outcome rather than as a separate graded axis.

For mariner-telemetry, issuer trust is a policy question settled against the maintained anchor set rather than the popularity of a commercial authority. The specific issuer and key parameters of mariner-telemetry's certificate of record are carried in the inventory database; what matters to the review is whether that issuer sits inside the governed anchor set, since a leaf that validates today but chains outside the set is still a rotation candidate on governance grounds.

Cipher-suite selection at mariner-telemetry was inspected for obviously deprecated constructions. While suite negotiation is not itself a graded axis in this review, a modern protocol version on https://telemetry.prod.mariner.internal strongly constrains the suite space, which is part of why the version allow-list does so much of the work and why a downgrade is treated as consequential rather than cosmetic.

Partner-facing exposure was a specific consideration for mariner-telemetry where federated third parties consume it. Federation raises the stakes of a mutual-TLS gap because the counterparty's assurance depends on it, which is why a production federation surface is held to the client-authentication expectation without sympathy for integration convenience.

Early-data exposure for mariner-telemetry was considered where 0-RTT resumption is enabled. Replayable early data is an application-layer hazard rather than a transport-policy axis, so it does not move mariner-telemetry's disposition, but it is flagged for team-observability as a design note to weigh against the latency benefit on the prod surface.

The mariner-telemetry interconnect was modelled as part of the broader dependency graph. A weakness here propagates to every caller that trusts this endpoint, which is why the review resists the temptation to treat ingests high-cardinality metrics from the fleet as a low-stakes carve-out. The posture is assessed on its own merits and against the same bar as the busiest production path.

Certificate-transparency presence for mariner-telemetry's leaf was checked as a tamper-evidence signal. CT inclusion does not by itself make a certificate compliant — it is neither a protocol version nor an issuer-trust decision — but its absence on a publicly reachable prod endpoint would be a flag worth a follow-up outside this review's transport remit.

### svc-006 — mariner-config-service

Evidence handling for mariner-config-service is deliberately conservative. When the fingerprint observed on the wire disagrees with the inventory of record, the review does not attempt to reconcile the two in the agent's favour; the disagreement is itself the finding, and it is escalated rather than waived, regardless of any paperwork that might otherwise have applied.

Exception status. mariner-config-service (svc-006) holds waiver WV-2026-006, a transport-protocol exception scoped to the service's entire footprint across every environment. The register shows it granted on 2026-01-05 with a nominal expiry of 2026-08-01. That exception did not run its course: it was rescinded on 2026-03-20 following incident INC-2026-0331, an unscheduled key-ceremony rollback, and the register now carries WV-2026-006 in a revoked state. A rescinded waiver provides no cover, so the nominal expiry of 2026-08-01 is moot — the underlying posture is judged as though the exception had never issued.

Key-ceremony provenance for mariner-config-service's material was reviewed at a high level. Where team-platform can attest that the private key was generated and held in a hardware security module, the operational risk of the key is lower, but provenance does not raise an under-strength key above the floor or extend a certificate past its not-after date.

Wildcard usage at mariner-config-service was noted where present. A wildcard leaf broadens blast radius if its key is compromised, so although a wildcard is not itself a finding, it raises the priority of the hygiene rules for mariner-config-service — a near-expiry or under-strength wildcard is a rotation the review would rather see scheduled sooner than later.

Key strength for mariner-config-service is judged against the floor for its algorithm family. The review does not grade keys on a curve: a key below the floor is a rotation finding irrespective of the sensitivity of the workload, because under-strength material weakens the whole interconnect graph that mariner-config-service participates in.

Session resumption behaviour for mariner-config-service was characterised so that repeat captures could be compared fairly. Resumption can mask a renegotiated parameter, so the harness records full-handshake outcomes where it can; the authoritative capture for mariner-config-service is still the most recent row, and resumption never changes which row is current.

Audit retention for mariner-config-service's captures follows the standard schedule: every sweep is retained, and the review reads the latest. This matters when reconstructing a finding months later — the row that was current at review time is identifiable by its capture timestamp, and the reconstruction must use that row rather than whatever happens to be newest at reconstruction time.

Certificate pinning by clients of mariner-config-service was inventoried lightly, because pinning interacts badly with rotation: a pinned client can break when mariner-config-service legitimately rotates. The review's rotation findings therefore come with a reminder that any pin held against mariner-config-service's current leaf must be updated in lockstep with the re-issue.

Operationally, mariner-config-service has been stable, but stability is not conformance. The review separates 'has not failed yet' from 'meets policy today', and it is the latter that governs the finding. Where the captured evidence and the live configuration disagree, the captured evidence is taken as the ground truth.

Forward-looking, the review recorded whether mariner-config-service is on a path toward post-quantum-ready key exchange. This cycle treats PQC readiness as informational; it changes no disposition, but it is captured so that team-platform can sequence the work against the rotation cadence the hygiene rules already impose.

Clock discipline was assumed but noted for mariner-config-service: certificate validity windows are only meaningful if the validating hosts agree on the time. The review reasons about not-after relative to a single fixed review date, which removes any ambiguity that wall-clock skew on individual probers might otherwise introduce into the near-expiry judgement.

The protocol floor matters for mariner-config-service because a single tolerated downgrade becomes a precedent. The review treats any negotiated version outside the allowed set as a finding in every environment, including development, so that a sandbox habit does not migrate into production by copy-paste.

Transport strictness headers on responses from mariner-config-service were observed where applicable. Strict-transport signalling reduces downgrade opportunity for browser clients but does not substitute for the server-side protocol floor; the review credits it as defence in depth and nothing more for a prod surface.

Subject-alternative-name coverage on mariner-config-service's leaf was checked against the hostnames https://config-service.prod.mariner.internal actually answers for. A name not covered by the served certificate would surface as a verification failure in the capture, so SAN gaps tend to show up indirectly through the recorded verification outcome rather than as a separate graded axis.

For mariner-config-service, issuer trust is a policy question settled against the maintained anchor set rather than the popularity of a commercial authority. The specific issuer and key parameters of mariner-config-service's certificate of record are carried in the inventory database; what matters to the review is whether that issuer sits inside the governed anchor set, since a leaf that validates today but chains outside the set is still a rotation candidate on governance grounds.

Cipher-suite selection at mariner-config-service was inspected for obviously deprecated constructions. While suite negotiation is not itself a graded axis in this review, a modern protocol version on https://config-service.prod.mariner.internal strongly constrains the suite space, which is part of why the version allow-list does so much of the work and why a downgrade is treated as consequential rather than cosmetic.

Partner-facing exposure was a specific consideration for mariner-config-service where federated third parties consume it. Federation raises the stakes of a mutual-TLS gap because the counterparty's assurance depends on it, which is why a production federation surface is held to the client-authentication expectation without sympathy for integration convenience.

Early-data exposure for mariner-config-service was considered where 0-RTT resumption is enabled. Replayable early data is an application-layer hazard rather than a transport-policy axis, so it does not move mariner-config-service's disposition, but it is flagged for team-platform as a design note to weigh against the latency benefit on the prod surface.

The mariner-config-service interconnect was modelled as part of the broader dependency graph. A weakness here propagates to every caller that trusts this endpoint, which is why the review resists the temptation to treat distributes signed configuration bundles to runtime nodes as a low-stakes carve-out. The posture is assessed on its own merits and against the same bar as the busiest production path.

Certificate-transparency presence for mariner-config-service's leaf was checked as a tamper-evidence signal. CT inclusion does not by itself make a certificate compliant — it is neither a protocol version nor an issuer-trust decision — but its absence on a publicly reachable prod endpoint would be a flag worth a follow-up outside this review's transport remit.

Truststore management on the prod side of mariner-config-service matters for mutual TLS. Where the endpoint demands a client certificate, the set of client anchors it accepts is an operational concern for team-platform; the review records only whether a client certificate was presented and validated, leaving truststore curation to the owning team's runbooks.

Mutual TLS expectations for mariner-config-service follow the environment. The production trust boundary requires a client certificate; a non-production surface is not penalised for the absence of one. Where mariner-config-service is expected to present a client certificate and the capture shows none, the gap is a protocol-level finding unless a waiver of the matching kind and scope is in force.

ALPN negotiation at mariner-config-service was noted to confirm the application protocol riding over the tunnel, but protocol-version policy is enforced at the TLS layer and does not bend to the application above it. A modern application protocol over a legacy transport is still a transport finding for mariner-config-service.

Finally, mariner-config-service was checked for consistency between its environment label and its exposure. A service labelled prod is assessed under the rules for that environment; the review does not reclassify a surface to soften a finding, and team-platform retains the route to reclassification through inventory governance rather than through this review.

The harness recorded the mariner-config-service endpoint over successive sweeps; only the most recent capture per service is treated as authoritative, since earlier sweeps frequently predate a remediation or a re-issue. Reviewers are reminded that the captured negotiation outcomes, the chain-validation result, and the leaf fingerprint seen on the wire are held in the inventory database and must be read from there, not inferred from this narrative.

Revocation freshness was considered for mariner-config-service. The review notes whether the endpoint's stapled status was recent and whether the validating party had a live path to revocation information, but treats stapling hygiene as advisory this cycle; the governing chain question remains whether the presented chain validated to a trusted anchor at capture time.

Where mariner-config-service terminates TLS at a sidecar or a shared load balancer rather than in the application process, the review attributes the captured posture to the service as exposed on https://config-service.prod.mariner.internal. Termination topology is an implementation detail; the obligation to meet policy attaches to the exposed prod surface regardless of which component holds the key.

Encrypted-client-hello readiness for mariner-config-service was recorded as informational. ECH changes what an on-path observer can see about the handshake to https://config-service.prod.mariner.internal but does not alter any graded axis here; it neither relaxes the protocol floor nor changes how a client certificate or a chain is judged.

Ownership context: team-platform maintains mariner-config-service and is the counterparty for any remediation. The review records owning teams so that rotation and re-issuance work lands with the group that can actually schedule a maintenance window on the prod surface, but ownership confers no relief from policy.

Cross-signing arrangements that touch mariner-config-service's issuer were enumerated to make sure the chain the review reasons about is the chain clients actually build. A leaf can validate via more than one path; the governed question for mariner-config-service is whether the issuer of record sits in the trust anchor set, independent of which cross-signed path a particular client happens to choose.

Renewal automation for mariner-config-service was reviewed at the level of 'does a pipeline exist', not 'did it run'. An ACME-style renewal loop lowers the operational cost of the rotation findings this review may raise, but the disposition is taken from the captured state of https://config-service.prod.mariner.internal, so a renewal that is configured but not yet effective does not pre-empt a near-expiry finding.

Certificate lifetime is the other half of hygiene. A leaf approaching its not-after boundary inside the rotation window is scheduled for replacement well ahead of the cliff, on the principle that a lapse on the prod surface is an availability incident as much as a security one. The window is uniform across services so that nothing in mariner-config-service's profile earns special treatment.

SNI and virtual-host disambiguation were verified for mariner-config-service so that the captured leaf is unambiguously the one https://config-service.prod.mariner.internal intends to serve. A mismatch between the requested name and the served certificate would itself be an integrity concern, which is one more reason the observed fingerprint is compared against the inventory of record rather than assumed.

The review explicitly separated configuration intent from observed behaviour for mariner-config-service. A configuration file may declare a strict posture, but if the captured evidence on https://config-service.prod.mariner.internal shows otherwise, the evidence governs the finding; conversely a permissive-looking configuration that nonetheless negotiated within policy is judged on what actually happened on the wire.

Within the review boundary, mariner-config-service (svc-006) distributes signed configuration bundles to runtime nodes. It is owned by team-platform and presents on https://config-service.prod.mariner.internal, which the inventory classifies as a prod surface. The transport posture of any prod endpoint is weighed against the operative policy rather than against historical convention, and the assessment proceeds from the evidence of record rather than from operator attestation.

Documentation for mariner-config-service was cross-checked against the configuration set. Where a policy value is needed — the rotation window, the protocol allow-list, the key floors, or the issuer anchor set — it is read from the validated configuration rather than from this prose, which paraphrases policy for the reader's convenience only.

For mesh participants such as mariner-config-service, certificate rotation is automated through the issuing control plane, which lowers the cost of a rotation finding but does not remove the obligation: an automated rotation that has not yet run still leaves a soon-to-expire leaf on https://config-service.prod.mariner.internal, and the review grades the state at capture time, not the intention encoded in automation.

Revocation-list distribution touching mariner-config-service's issuer was sanity-checked so that a client choosing CRL over stapled status still has a path. As with stapling, the review treats CRL reachability as advisory this cycle; the governing question for mariner-config-service remains whether the presented chain validated at capture time.

### svc-007 — mariner-search-index

Certificate-transparency presence for mariner-search-index's leaf was checked as a tamper-evidence signal. CT inclusion does not by itself make a certificate compliant — it is neither a protocol version nor an issuer-trust decision — but its absence on a publicly reachable prod endpoint would be a flag worth a follow-up outside this review's transport remit.

Truststore management on the prod side of mariner-search-index matters for mutual TLS. Where the endpoint demands a client certificate, the set of client anchors it accepts is an operational concern for team-search; the review records only whether a client certificate was presented and validated, leaving truststore curation to the owning team's runbooks.

Exception status. mariner-search-index (svc-007) carries no transport-security waiver of any kind in the register — no protocol exception, no mutual-TLS carve-out, and no chain exception. It is therefore assessed directly against the operative policy, with the captured evidence in the inventory database standing as the sole record of how the prod endpoint actually negotiated.

Mutual TLS expectations for mariner-search-index follow the environment. The production trust boundary requires a client certificate; a non-production surface is not penalised for the absence of one. Where mariner-search-index is expected to present a client certificate and the capture shows none, the gap is a protocol-level finding unless a waiver of the matching kind and scope is in force.

ALPN negotiation at mariner-search-index was noted to confirm the application protocol riding over the tunnel, but protocol-version policy is enforced at the TLS layer and does not bend to the application above it. A modern application protocol over a legacy transport is still a transport finding for mariner-search-index.

Finally, mariner-search-index was checked for consistency between its environment label and its exposure. A service labelled prod is assessed under the rules for that environment; the review does not reclassify a surface to soften a finding, and team-search retains the route to reclassification through inventory governance rather than through this review.

The harness recorded the mariner-search-index endpoint over successive sweeps; only the most recent capture per service is treated as authoritative, since earlier sweeps frequently predate a remediation or a re-issue. Reviewers are reminded that the captured negotiation outcomes, the chain-validation result, and the leaf fingerprint seen on the wire are held in the inventory database and must be read from there, not inferred from this narrative.

Revocation freshness was considered for mariner-search-index. The review notes whether the endpoint's stapled status was recent and whether the validating party had a live path to revocation information, but treats stapling hygiene as advisory this cycle; the governing chain question remains whether the presented chain validated to a trusted anchor at capture time.

Where mariner-search-index terminates TLS at a sidecar or a shared load balancer rather than in the application process, the review attributes the captured posture to the service as exposed on https://search-index.prod.mariner.internal. Termination topology is an implementation detail; the obligation to meet policy attaches to the exposed prod surface regardless of which component holds the key.

Encrypted-client-hello readiness for mariner-search-index was recorded as informational. ECH changes what an on-path observer can see about the handshake to https://search-index.prod.mariner.internal but does not alter any graded axis here; it neither relaxes the protocol floor nor changes how a client certificate or a chain is judged.

Ownership context: team-search maintains mariner-search-index and is the counterparty for any remediation. The review records owning teams so that rotation and re-issuance work lands with the group that can actually schedule a maintenance window on the prod surface, but ownership confers no relief from policy.

Cross-signing arrangements that touch mariner-search-index's issuer were enumerated to make sure the chain the review reasons about is the chain clients actually build. A leaf can validate via more than one path; the governed question for mariner-search-index is whether the issuer of record sits in the trust anchor set, independent of which cross-signed path a particular client happens to choose.

Renewal automation for mariner-search-index was reviewed at the level of 'does a pipeline exist', not 'did it run'. An ACME-style renewal loop lowers the operational cost of the rotation findings this review may raise, but the disposition is taken from the captured state of https://search-index.prod.mariner.internal, so a renewal that is configured but not yet effective does not pre-empt a near-expiry finding.

Certificate lifetime is the other half of hygiene. A leaf approaching its not-after boundary inside the rotation window is scheduled for replacement well ahead of the cliff, on the principle that a lapse on the prod surface is an availability incident as much as a security one. The window is uniform across services so that nothing in mariner-search-index's profile earns special treatment.

SNI and virtual-host disambiguation were verified for mariner-search-index so that the captured leaf is unambiguously the one https://search-index.prod.mariner.internal intends to serve. A mismatch between the requested name and the served certificate would itself be an integrity concern, which is one more reason the observed fingerprint is compared against the inventory of record rather than assumed.

The review explicitly separated configuration intent from observed behaviour for mariner-search-index. A configuration file may declare a strict posture, but if the captured evidence on https://search-index.prod.mariner.internal shows otherwise, the evidence governs the finding; conversely a permissive-looking configuration that nonetheless negotiated within policy is judged on what actually happened on the wire.

Within the review boundary, mariner-search-index (svc-007) serves the customer-facing catalogue query path. It is owned by team-search and presents on https://search-index.prod.mariner.internal, which the inventory classifies as a prod surface. The transport posture of any prod endpoint is weighed against the operative policy rather than against historical convention, and the assessment proceeds from the evidence of record rather than from operator attestation.

Documentation for mariner-search-index was cross-checked against the configuration set. Where a policy value is needed — the rotation window, the protocol allow-list, the key floors, or the issuer anchor set — it is read from the validated configuration rather than from this prose, which paraphrases policy for the reader's convenience only.

For mesh participants such as mariner-search-index, certificate rotation is automated through the issuing control plane, which lowers the cost of a rotation finding but does not remove the obligation: an automated rotation that has not yet run still leaves a soon-to-expire leaf on https://search-index.prod.mariner.internal, and the review grades the state at capture time, not the intention encoded in automation.

Revocation-list distribution touching mariner-search-index's issuer was sanity-checked so that a client choosing CRL over stapled status still has a path. As with stapling, the review treats CRL reachability as advisory this cycle; the governing question for mariner-search-index remains whether the presented chain validated at capture time.

Evidence handling for mariner-search-index is deliberately conservative. When the fingerprint observed on the wire disagrees with the inventory of record, the review does not attempt to reconcile the two in the agent's favour; the disagreement is itself the finding, and it is escalated rather than waived, regardless of any paperwork that might otherwise have applied.

Key-ceremony provenance for mariner-search-index's material was reviewed at a high level. Where team-search can attest that the private key was generated and held in a hardware security module, the operational risk of the key is lower, but provenance does not raise an under-strength key above the floor or extend a certificate past its not-after date.

Wildcard usage at mariner-search-index was noted where present. A wildcard leaf broadens blast radius if its key is compromised, so although a wildcard is not itself a finding, it raises the priority of the hygiene rules for mariner-search-index — a near-expiry or under-strength wildcard is a rotation the review would rather see scheduled sooner than later.

Key strength for mariner-search-index is judged against the floor for its algorithm family. The review does not grade keys on a curve: a key below the floor is a rotation finding irrespective of the sensitivity of the workload, because under-strength material weakens the whole interconnect graph that mariner-search-index participates in.

Session resumption behaviour for mariner-search-index was characterised so that repeat captures could be compared fairly. Resumption can mask a renegotiated parameter, so the harness records full-handshake outcomes where it can; the authoritative capture for mariner-search-index is still the most recent row, and resumption never changes which row is current.

Audit retention for mariner-search-index's captures follows the standard schedule: every sweep is retained, and the review reads the latest. This matters when reconstructing a finding months later — the row that was current at review time is identifiable by its capture timestamp, and the reconstruction must use that row rather than whatever happens to be newest at reconstruction time.

Certificate pinning by clients of mariner-search-index was inventoried lightly, because pinning interacts badly with rotation: a pinned client can break when mariner-search-index legitimately rotates. The review's rotation findings therefore come with a reminder that any pin held against mariner-search-index's current leaf must be updated in lockstep with the re-issue.

Operationally, mariner-search-index has been stable, but stability is not conformance. The review separates 'has not failed yet' from 'meets policy today', and it is the latter that governs the finding. Where the captured evidence and the live configuration disagree, the captured evidence is taken as the ground truth.

Forward-looking, the review recorded whether mariner-search-index is on a path toward post-quantum-ready key exchange. This cycle treats PQC readiness as informational; it changes no disposition, but it is captured so that team-search can sequence the work against the rotation cadence the hygiene rules already impose.

Clock discipline was assumed but noted for mariner-search-index: certificate validity windows are only meaningful if the validating hosts agree on the time. The review reasons about not-after relative to a single fixed review date, which removes any ambiguity that wall-clock skew on individual probers might otherwise introduce into the near-expiry judgement.

The protocol floor matters for mariner-search-index because a single tolerated downgrade becomes a precedent. The review treats any negotiated version outside the allowed set as a finding in every environment, including development, so that a sandbox habit does not migrate into production by copy-paste.

Transport strictness headers on responses from mariner-search-index were observed where applicable. Strict-transport signalling reduces downgrade opportunity for browser clients but does not substitute for the server-side protocol floor; the review credits it as defence in depth and nothing more for a prod surface.

Subject-alternative-name coverage on mariner-search-index's leaf was checked against the hostnames https://search-index.prod.mariner.internal actually answers for. A name not covered by the served certificate would surface as a verification failure in the capture, so SAN gaps tend to show up indirectly through the recorded verification outcome rather than as a separate graded axis.

For mariner-search-index, issuer trust is a policy question settled against the maintained anchor set rather than the popularity of a commercial authority. The specific issuer and key parameters of mariner-search-index's certificate of record are carried in the inventory database; what matters to the review is whether that issuer sits inside the governed anchor set, since a leaf that validates today but chains outside the set is still a rotation candidate on governance grounds.

Cipher-suite selection at mariner-search-index was inspected for obviously deprecated constructions. While suite negotiation is not itself a graded axis in this review, a modern protocol version on https://search-index.prod.mariner.internal strongly constrains the suite space, which is part of why the version allow-list does so much of the work and why a downgrade is treated as consequential rather than cosmetic.

Partner-facing exposure was a specific consideration for mariner-search-index where federated third parties consume it. Federation raises the stakes of a mutual-TLS gap because the counterparty's assurance depends on it, which is why a production federation surface is held to the client-authentication expectation without sympathy for integration convenience.

Early-data exposure for mariner-search-index was considered where 0-RTT resumption is enabled. Replayable early data is an application-layer hazard rather than a transport-policy axis, so it does not move mariner-search-index's disposition, but it is flagged for team-search as a design note to weigh against the latency benefit on the prod surface.

The mariner-search-index interconnect was modelled as part of the broader dependency graph. A weakness here propagates to every caller that trusts this endpoint, which is why the review resists the temptation to treat serves the customer-facing catalogue query path as a low-stakes carve-out. The posture is assessed on its own merits and against the same bar as the busiest production path.

### svc-008 — mariner-dev-sandbox

Revocation-list distribution touching mariner-dev-sandbox's issuer was sanity-checked so that a client choosing CRL over stapled status still has a path. As with stapling, the review treats CRL reachability as advisory this cycle; the governing question for mariner-dev-sandbox remains whether the presented chain validated at capture time.

Evidence handling for mariner-dev-sandbox is deliberately conservative. When the fingerprint observed on the wire disagrees with the inventory of record, the review does not attempt to reconcile the two in the agent's favour; the disagreement is itself the finding, and it is escalated rather than waived, regardless of any paperwork that might otherwise have applied.

Key-ceremony provenance for mariner-dev-sandbox's material was reviewed at a high level. Where team-devx can attest that the private key was generated and held in a hardware security module, the operational risk of the key is lower, but provenance does not raise an under-strength key above the floor or extend a certificate past its not-after date.

Exception status. mariner-dev-sandbox (svc-008) carries no transport-security waiver of any kind in the register — no protocol exception, no mutual-TLS carve-out, and no chain exception. It is therefore assessed directly against the operative policy, with the captured evidence in the inventory database standing as the sole record of how the dev endpoint actually negotiated.

Wildcard usage at mariner-dev-sandbox was noted where present. A wildcard leaf broadens blast radius if its key is compromised, so although a wildcard is not itself a finding, it raises the priority of the hygiene rules for mariner-dev-sandbox — a near-expiry or under-strength wildcard is a rotation the review would rather see scheduled sooner than later.

Key strength for mariner-dev-sandbox is judged against the floor for its algorithm family. The review does not grade keys on a curve: a key below the floor is a rotation finding irrespective of the sensitivity of the workload, because under-strength material weakens the whole interconnect graph that mariner-dev-sandbox participates in.

Session resumption behaviour for mariner-dev-sandbox was characterised so that repeat captures could be compared fairly. Resumption can mask a renegotiated parameter, so the harness records full-handshake outcomes where it can; the authoritative capture for mariner-dev-sandbox is still the most recent row, and resumption never changes which row is current.

Audit retention for mariner-dev-sandbox's captures follows the standard schedule: every sweep is retained, and the review reads the latest. This matters when reconstructing a finding months later — the row that was current at review time is identifiable by its capture timestamp, and the reconstruction must use that row rather than whatever happens to be newest at reconstruction time.

Certificate pinning by clients of mariner-dev-sandbox was inventoried lightly, because pinning interacts badly with rotation: a pinned client can break when mariner-dev-sandbox legitimately rotates. The review's rotation findings therefore come with a reminder that any pin held against mariner-dev-sandbox's current leaf must be updated in lockstep with the re-issue.

Operationally, mariner-dev-sandbox has been stable, but stability is not conformance. The review separates 'has not failed yet' from 'meets policy today', and it is the latter that governs the finding. Where the captured evidence and the live configuration disagree, the captured evidence is taken as the ground truth.

Forward-looking, the review recorded whether mariner-dev-sandbox is on a path toward post-quantum-ready key exchange. This cycle treats PQC readiness as informational; it changes no disposition, but it is captured so that team-devx can sequence the work against the rotation cadence the hygiene rules already impose.

Clock discipline was assumed but noted for mariner-dev-sandbox: certificate validity windows are only meaningful if the validating hosts agree on the time. The review reasons about not-after relative to a single fixed review date, which removes any ambiguity that wall-clock skew on individual probers might otherwise introduce into the near-expiry judgement.

The protocol floor matters for mariner-dev-sandbox because a single tolerated downgrade becomes a precedent. The review treats any negotiated version outside the allowed set as a finding in every environment, including development, so that a sandbox habit does not migrate into production by copy-paste.

Transport strictness headers on responses from mariner-dev-sandbox were observed where applicable. Strict-transport signalling reduces downgrade opportunity for browser clients but does not substitute for the server-side protocol floor; the review credits it as defence in depth and nothing more for a dev surface.

Subject-alternative-name coverage on mariner-dev-sandbox's leaf was checked against the hostnames https://dev-sandbox.dev.mariner.internal actually answers for. A name not covered by the served certificate would surface as a verification failure in the capture, so SAN gaps tend to show up indirectly through the recorded verification outcome rather than as a separate graded axis.

For mariner-dev-sandbox, issuer trust is a policy question settled against the maintained anchor set rather than the popularity of a commercial authority. The specific issuer and key parameters of mariner-dev-sandbox's certificate of record are carried in the inventory database; what matters to the review is whether that issuer sits inside the governed anchor set, since a leaf that validates today but chains outside the set is still a rotation candidate on governance grounds.

Cipher-suite selection at mariner-dev-sandbox was inspected for obviously deprecated constructions. While suite negotiation is not itself a graded axis in this review, a modern protocol version on https://dev-sandbox.dev.mariner.internal strongly constrains the suite space, which is part of why the version allow-list does so much of the work and why a downgrade is treated as consequential rather than cosmetic.

Partner-facing exposure was a specific consideration for mariner-dev-sandbox where federated third parties consume it. Federation raises the stakes of a mutual-TLS gap because the counterparty's assurance depends on it, which is why a production federation surface is held to the client-authentication expectation without sympathy for integration convenience.

Early-data exposure for mariner-dev-sandbox was considered where 0-RTT resumption is enabled. Replayable early data is an application-layer hazard rather than a transport-policy axis, so it does not move mariner-dev-sandbox's disposition, but it is flagged for team-devx as a design note to weigh against the latency benefit on the dev surface.

The mariner-dev-sandbox interconnect was modelled as part of the broader dependency graph. A weakness here propagates to every caller that trusts this endpoint, which is why the review resists the temptation to treat hosts throwaway integration environments for feature teams as a low-stakes carve-out. The posture is assessed on its own merits and against the same bar as the busiest production path.

Certificate-transparency presence for mariner-dev-sandbox's leaf was checked as a tamper-evidence signal. CT inclusion does not by itself make a certificate compliant — it is neither a protocol version nor an issuer-trust decision — but its absence on a publicly reachable dev endpoint would be a flag worth a follow-up outside this review's transport remit.

Truststore management on the dev side of mariner-dev-sandbox matters for mutual TLS. Where the endpoint demands a client certificate, the set of client anchors it accepts is an operational concern for team-devx; the review records only whether a client certificate was presented and validated, leaving truststore curation to the owning team's runbooks.

Mutual TLS expectations for mariner-dev-sandbox follow the environment. The production trust boundary requires a client certificate; a non-production surface is not penalised for the absence of one. Where mariner-dev-sandbox is expected to present a client certificate and the capture shows none, the gap is a protocol-level finding unless a waiver of the matching kind and scope is in force.

ALPN negotiation at mariner-dev-sandbox was noted to confirm the application protocol riding over the tunnel, but protocol-version policy is enforced at the TLS layer and does not bend to the application above it. A modern application protocol over a legacy transport is still a transport finding for mariner-dev-sandbox.

Finally, mariner-dev-sandbox was checked for consistency between its environment label and its exposure. A service labelled dev is assessed under the rules for that environment; the review does not reclassify a surface to soften a finding, and team-devx retains the route to reclassification through inventory governance rather than through this review.

The harness recorded the mariner-dev-sandbox endpoint over successive sweeps; only the most recent capture per service is treated as authoritative, since earlier sweeps frequently predate a remediation or a re-issue. Reviewers are reminded that the captured negotiation outcomes, the chain-validation result, and the leaf fingerprint seen on the wire are held in the inventory database and must be read from there, not inferred from this narrative.

Revocation freshness was considered for mariner-dev-sandbox. The review notes whether the endpoint's stapled status was recent and whether the validating party had a live path to revocation information, but treats stapling hygiene as advisory this cycle; the governing chain question remains whether the presented chain validated to a trusted anchor at capture time.

Where mariner-dev-sandbox terminates TLS at a sidecar or a shared load balancer rather than in the application process, the review attributes the captured posture to the service as exposed on https://dev-sandbox.dev.mariner.internal. Termination topology is an implementation detail; the obligation to meet policy attaches to the exposed dev surface regardless of which component holds the key.

Encrypted-client-hello readiness for mariner-dev-sandbox was recorded as informational. ECH changes what an on-path observer can see about the handshake to https://dev-sandbox.dev.mariner.internal but does not alter any graded axis here; it neither relaxes the protocol floor nor changes how a client certificate or a chain is judged.

Ownership context: team-devx maintains mariner-dev-sandbox and is the counterparty for any remediation. The review records owning teams so that rotation and re-issuance work lands with the group that can actually schedule a maintenance window on the dev surface, but ownership confers no relief from policy.

Cross-signing arrangements that touch mariner-dev-sandbox's issuer were enumerated to make sure the chain the review reasons about is the chain clients actually build. A leaf can validate via more than one path; the governed question for mariner-dev-sandbox is whether the issuer of record sits in the trust anchor set, independent of which cross-signed path a particular client happens to choose.

Renewal automation for mariner-dev-sandbox was reviewed at the level of 'does a pipeline exist', not 'did it run'. An ACME-style renewal loop lowers the operational cost of the rotation findings this review may raise, but the disposition is taken from the captured state of https://dev-sandbox.dev.mariner.internal, so a renewal that is configured but not yet effective does not pre-empt a near-expiry finding.

Certificate lifetime is the other half of hygiene. A leaf approaching its not-after boundary inside the rotation window is scheduled for replacement well ahead of the cliff, on the principle that a lapse on the dev surface is an availability incident as much as a security one. The window is uniform across services so that nothing in mariner-dev-sandbox's profile earns special treatment.

SNI and virtual-host disambiguation were verified for mariner-dev-sandbox so that the captured leaf is unambiguously the one https://dev-sandbox.dev.mariner.internal intends to serve. A mismatch between the requested name and the served certificate would itself be an integrity concern, which is one more reason the observed fingerprint is compared against the inventory of record rather than assumed.

The review explicitly separated configuration intent from observed behaviour for mariner-dev-sandbox. A configuration file may declare a strict posture, but if the captured evidence on https://dev-sandbox.dev.mariner.internal shows otherwise, the evidence governs the finding; conversely a permissive-looking configuration that nonetheless negotiated within policy is judged on what actually happened on the wire.

Within the review boundary, mariner-dev-sandbox (svc-008) hosts throwaway integration environments for feature teams. It is owned by team-devx and presents on https://dev-sandbox.dev.mariner.internal, which the inventory classifies as a dev surface. The transport posture of any dev endpoint is weighed against the operative policy rather than against historical convention, and the assessment proceeds from the evidence of record rather than from operator attestation.

Documentation for mariner-dev-sandbox was cross-checked against the configuration set. Where a policy value is needed — the rotation window, the protocol allow-list, the key floors, or the issuer anchor set — it is read from the validated configuration rather than from this prose, which paraphrases policy for the reader's convenience only.

For mesh participants such as mariner-dev-sandbox, certificate rotation is automated through the issuing control plane, which lowers the cost of a rotation finding but does not remove the obligation: an automated rotation that has not yet run still leaves a soon-to-expire leaf on https://dev-sandbox.dev.mariner.internal, and the review grades the state at capture time, not the intention encoded in automation.

### svc-009 — mariner-payments-gw

The mariner-payments-gw interconnect was modelled as part of the broader dependency graph. A weakness here propagates to every caller that trusts this endpoint, which is why the review resists the temptation to treat bridges card-network settlement into the payments core as a low-stakes carve-out. The posture is assessed on its own merits and against the same bar as the busiest production path.

Exception status. mariner-payments-gw (svc-009) carries no transport-security waiver of any kind in the register — no protocol exception, no mutual-TLS carve-out, and no chain exception. It is therefore assessed directly against the operative policy, with the captured evidence in the inventory database standing as the sole record of how the prod endpoint actually negotiated.

Certificate-transparency presence for mariner-payments-gw's leaf was checked as a tamper-evidence signal. CT inclusion does not by itself make a certificate compliant — it is neither a protocol version nor an issuer-trust decision — but its absence on a publicly reachable prod endpoint would be a flag worth a follow-up outside this review's transport remit.

Truststore management on the prod side of mariner-payments-gw matters for mutual TLS. Where the endpoint demands a client certificate, the set of client anchors it accepts is an operational concern for team-payments; the review records only whether a client certificate was presented and validated, leaving truststore curation to the owning team's runbooks.

Mutual TLS expectations for mariner-payments-gw follow the environment. The production trust boundary requires a client certificate; a non-production surface is not penalised for the absence of one. Where mariner-payments-gw is expected to present a client certificate and the capture shows none, the gap is a protocol-level finding unless a waiver of the matching kind and scope is in force.

ALPN negotiation at mariner-payments-gw was noted to confirm the application protocol riding over the tunnel, but protocol-version policy is enforced at the TLS layer and does not bend to the application above it. A modern application protocol over a legacy transport is still a transport finding for mariner-payments-gw.

Finally, mariner-payments-gw was checked for consistency between its environment label and its exposure. A service labelled prod is assessed under the rules for that environment; the review does not reclassify a surface to soften a finding, and team-payments retains the route to reclassification through inventory governance rather than through this review.

The harness recorded the mariner-payments-gw endpoint over successive sweeps; only the most recent capture per service is treated as authoritative, since earlier sweeps frequently predate a remediation or a re-issue. Reviewers are reminded that the captured negotiation outcomes, the chain-validation result, and the leaf fingerprint seen on the wire are held in the inventory database and must be read from there, not inferred from this narrative.

Revocation freshness was considered for mariner-payments-gw. The review notes whether the endpoint's stapled status was recent and whether the validating party had a live path to revocation information, but treats stapling hygiene as advisory this cycle; the governing chain question remains whether the presented chain validated to a trusted anchor at capture time.

Where mariner-payments-gw terminates TLS at a sidecar or a shared load balancer rather than in the application process, the review attributes the captured posture to the service as exposed on https://payments-gw.prod.mariner.internal. Termination topology is an implementation detail; the obligation to meet policy attaches to the exposed prod surface regardless of which component holds the key.

Encrypted-client-hello readiness for mariner-payments-gw was recorded as informational. ECH changes what an on-path observer can see about the handshake to https://payments-gw.prod.mariner.internal but does not alter any graded axis here; it neither relaxes the protocol floor nor changes how a client certificate or a chain is judged.

Ownership context: team-payments maintains mariner-payments-gw and is the counterparty for any remediation. The review records owning teams so that rotation and re-issuance work lands with the group that can actually schedule a maintenance window on the prod surface, but ownership confers no relief from policy.

Cross-signing arrangements that touch mariner-payments-gw's issuer were enumerated to make sure the chain the review reasons about is the chain clients actually build. A leaf can validate via more than one path; the governed question for mariner-payments-gw is whether the issuer of record sits in the trust anchor set, independent of which cross-signed path a particular client happens to choose.

Renewal automation for mariner-payments-gw was reviewed at the level of 'does a pipeline exist', not 'did it run'. An ACME-style renewal loop lowers the operational cost of the rotation findings this review may raise, but the disposition is taken from the captured state of https://payments-gw.prod.mariner.internal, so a renewal that is configured but not yet effective does not pre-empt a near-expiry finding.

Certificate lifetime is the other half of hygiene. A leaf approaching its not-after boundary inside the rotation window is scheduled for replacement well ahead of the cliff, on the principle that a lapse on the prod surface is an availability incident as much as a security one. The window is uniform across services so that nothing in mariner-payments-gw's profile earns special treatment.

SNI and virtual-host disambiguation were verified for mariner-payments-gw so that the captured leaf is unambiguously the one https://payments-gw.prod.mariner.internal intends to serve. A mismatch between the requested name and the served certificate would itself be an integrity concern, which is one more reason the observed fingerprint is compared against the inventory of record rather than assumed.

The review explicitly separated configuration intent from observed behaviour for mariner-payments-gw. A configuration file may declare a strict posture, but if the captured evidence on https://payments-gw.prod.mariner.internal shows otherwise, the evidence governs the finding; conversely a permissive-looking configuration that nonetheless negotiated within policy is judged on what actually happened on the wire.

Within the review boundary, mariner-payments-gw (svc-009) bridges card-network settlement into the payments core. It is owned by team-payments and presents on https://payments-gw.prod.mariner.internal, which the inventory classifies as a prod surface. The transport posture of any prod endpoint is weighed against the operative policy rather than against historical convention, and the assessment proceeds from the evidence of record rather than from operator attestation.

Documentation for mariner-payments-gw was cross-checked against the configuration set. Where a policy value is needed — the rotation window, the protocol allow-list, the key floors, or the issuer anchor set — it is read from the validated configuration rather than from this prose, which paraphrases policy for the reader's convenience only.

For mesh participants such as mariner-payments-gw, certificate rotation is automated through the issuing control plane, which lowers the cost of a rotation finding but does not remove the obligation: an automated rotation that has not yet run still leaves a soon-to-expire leaf on https://payments-gw.prod.mariner.internal, and the review grades the state at capture time, not the intention encoded in automation.

Revocation-list distribution touching mariner-payments-gw's issuer was sanity-checked so that a client choosing CRL over stapled status still has a path. As with stapling, the review treats CRL reachability as advisory this cycle; the governing question for mariner-payments-gw remains whether the presented chain validated at capture time.

Evidence handling for mariner-payments-gw is deliberately conservative. When the fingerprint observed on the wire disagrees with the inventory of record, the review does not attempt to reconcile the two in the agent's favour; the disagreement is itself the finding, and it is escalated rather than waived, regardless of any paperwork that might otherwise have applied.

Key-ceremony provenance for mariner-payments-gw's material was reviewed at a high level. Where team-payments can attest that the private key was generated and held in a hardware security module, the operational risk of the key is lower, but provenance does not raise an under-strength key above the floor or extend a certificate past its not-after date.

Wildcard usage at mariner-payments-gw was noted where present. A wildcard leaf broadens blast radius if its key is compromised, so although a wildcard is not itself a finding, it raises the priority of the hygiene rules for mariner-payments-gw — a near-expiry or under-strength wildcard is a rotation the review would rather see scheduled sooner than later.

Key strength for mariner-payments-gw is judged against the floor for its algorithm family. The review does not grade keys on a curve: a key below the floor is a rotation finding irrespective of the sensitivity of the workload, because under-strength material weakens the whole interconnect graph that mariner-payments-gw participates in.

Session resumption behaviour for mariner-payments-gw was characterised so that repeat captures could be compared fairly. Resumption can mask a renegotiated parameter, so the harness records full-handshake outcomes where it can; the authoritative capture for mariner-payments-gw is still the most recent row, and resumption never changes which row is current.

Audit retention for mariner-payments-gw's captures follows the standard schedule: every sweep is retained, and the review reads the latest. This matters when reconstructing a finding months later — the row that was current at review time is identifiable by its capture timestamp, and the reconstruction must use that row rather than whatever happens to be newest at reconstruction time.

Certificate pinning by clients of mariner-payments-gw was inventoried lightly, because pinning interacts badly with rotation: a pinned client can break when mariner-payments-gw legitimately rotates. The review's rotation findings therefore come with a reminder that any pin held against mariner-payments-gw's current leaf must be updated in lockstep with the re-issue.

Operationally, mariner-payments-gw has been stable, but stability is not conformance. The review separates 'has not failed yet' from 'meets policy today', and it is the latter that governs the finding. Where the captured evidence and the live configuration disagree, the captured evidence is taken as the ground truth.

Forward-looking, the review recorded whether mariner-payments-gw is on a path toward post-quantum-ready key exchange. This cycle treats PQC readiness as informational; it changes no disposition, but it is captured so that team-payments can sequence the work against the rotation cadence the hygiene rules already impose.

Clock discipline was assumed but noted for mariner-payments-gw: certificate validity windows are only meaningful if the validating hosts agree on the time. The review reasons about not-after relative to a single fixed review date, which removes any ambiguity that wall-clock skew on individual probers might otherwise introduce into the near-expiry judgement.

The protocol floor matters for mariner-payments-gw because a single tolerated downgrade becomes a precedent. The review treats any negotiated version outside the allowed set as a finding in every environment, including development, so that a sandbox habit does not migrate into production by copy-paste.

Transport strictness headers on responses from mariner-payments-gw were observed where applicable. Strict-transport signalling reduces downgrade opportunity for browser clients but does not substitute for the server-side protocol floor; the review credits it as defence in depth and nothing more for a prod surface.

Subject-alternative-name coverage on mariner-payments-gw's leaf was checked against the hostnames https://payments-gw.prod.mariner.internal actually answers for. A name not covered by the served certificate would surface as a verification failure in the capture, so SAN gaps tend to show up indirectly through the recorded verification outcome rather than as a separate graded axis.

For mariner-payments-gw, issuer trust is a policy question settled against the maintained anchor set rather than the popularity of a commercial authority. The specific issuer and key parameters of mariner-payments-gw's certificate of record are carried in the inventory database; what matters to the review is whether that issuer sits inside the governed anchor set, since a leaf that validates today but chains outside the set is still a rotation candidate on governance grounds.

Cipher-suite selection at mariner-payments-gw was inspected for obviously deprecated constructions. While suite negotiation is not itself a graded axis in this review, a modern protocol version on https://payments-gw.prod.mariner.internal strongly constrains the suite space, which is part of why the version allow-list does so much of the work and why a downgrade is treated as consequential rather than cosmetic.

Partner-facing exposure was a specific consideration for mariner-payments-gw where federated third parties consume it. Federation raises the stakes of a mutual-TLS gap because the counterparty's assurance depends on it, which is why a production federation surface is held to the client-authentication expectation without sympathy for integration convenience.

Early-data exposure for mariner-payments-gw was considered where 0-RTT resumption is enabled. Replayable early data is an application-layer hazard rather than a transport-policy axis, so it does not move mariner-payments-gw's disposition, but it is flagged for team-payments as a design note to weigh against the latency benefit on the prod surface.

### svc-010 — mariner-partner-api

For mesh participants such as mariner-partner-api, certificate rotation is automated through the issuing control plane, which lowers the cost of a rotation finding but does not remove the obligation: an automated rotation that has not yet run still leaves a soon-to-expire leaf on https://partner-api.prod.mariner.internal, and the review grades the state at capture time, not the intention encoded in automation.

Revocation-list distribution touching mariner-partner-api's issuer was sanity-checked so that a client choosing CRL over stapled status still has a path. As with stapling, the review treats CRL reachability as advisory this cycle; the governing question for mariner-partner-api remains whether the presented chain validated at capture time.

Exception status. mariner-partner-api (svc-010) holds waiver WV-2026-010, a mutual-TLS exception scoped to the staging surface only. The register shows it granted on 2026-02-01 with a nominal expiry of 2026-09-01. The register carries WV-2026-010 as granted and in force as written; whether it still provides cover at review time is a separate question, settled by reading the policy review date against the recorded expiry, and by checking that the scope actually reaches the prod surface under assessment.

Evidence handling for mariner-partner-api is deliberately conservative. When the fingerprint observed on the wire disagrees with the inventory of record, the review does not attempt to reconcile the two in the agent's favour; the disagreement is itself the finding, and it is escalated rather than waived, regardless of any paperwork that might otherwise have applied.

Key-ceremony provenance for mariner-partner-api's material was reviewed at a high level. Where team-partners can attest that the private key was generated and held in a hardware security module, the operational risk of the key is lower, but provenance does not raise an under-strength key above the floor or extend a certificate past its not-after date.

Wildcard usage at mariner-partner-api was noted where present. A wildcard leaf broadens blast radius if its key is compromised, so although a wildcard is not itself a finding, it raises the priority of the hygiene rules for mariner-partner-api — a near-expiry or under-strength wildcard is a rotation the review would rather see scheduled sooner than later.

Key strength for mariner-partner-api is judged against the floor for its algorithm family. The review does not grade keys on a curve: a key below the floor is a rotation finding irrespective of the sensitivity of the workload, because under-strength material weakens the whole interconnect graph that mariner-partner-api participates in.

Session resumption behaviour for mariner-partner-api was characterised so that repeat captures could be compared fairly. Resumption can mask a renegotiated parameter, so the harness records full-handshake outcomes where it can; the authoritative capture for mariner-partner-api is still the most recent row, and resumption never changes which row is current.

Audit retention for mariner-partner-api's captures follows the standard schedule: every sweep is retained, and the review reads the latest. This matters when reconstructing a finding months later — the row that was current at review time is identifiable by its capture timestamp, and the reconstruction must use that row rather than whatever happens to be newest at reconstruction time.

Certificate pinning by clients of mariner-partner-api was inventoried lightly, because pinning interacts badly with rotation: a pinned client can break when mariner-partner-api legitimately rotates. The review's rotation findings therefore come with a reminder that any pin held against mariner-partner-api's current leaf must be updated in lockstep with the re-issue.

Operationally, mariner-partner-api has been stable, but stability is not conformance. The review separates 'has not failed yet' from 'meets policy today', and it is the latter that governs the finding. Where the captured evidence and the live configuration disagree, the captured evidence is taken as the ground truth.

Forward-looking, the review recorded whether mariner-partner-api is on a path toward post-quantum-ready key exchange. This cycle treats PQC readiness as informational; it changes no disposition, but it is captured so that team-partners can sequence the work against the rotation cadence the hygiene rules already impose.

Clock discipline was assumed but noted for mariner-partner-api: certificate validity windows are only meaningful if the validating hosts agree on the time. The review reasons about not-after relative to a single fixed review date, which removes any ambiguity that wall-clock skew on individual probers might otherwise introduce into the near-expiry judgement.

The protocol floor matters for mariner-partner-api because a single tolerated downgrade becomes a precedent. The review treats any negotiated version outside the allowed set as a finding in every environment, including development, so that a sandbox habit does not migrate into production by copy-paste.

Transport strictness headers on responses from mariner-partner-api were observed where applicable. Strict-transport signalling reduces downgrade opportunity for browser clients but does not substitute for the server-side protocol floor; the review credits it as defence in depth and nothing more for a prod surface.

Subject-alternative-name coverage on mariner-partner-api's leaf was checked against the hostnames https://partner-api.prod.mariner.internal actually answers for. A name not covered by the served certificate would surface as a verification failure in the capture, so SAN gaps tend to show up indirectly through the recorded verification outcome rather than as a separate graded axis.

For mariner-partner-api, issuer trust is a policy question settled against the maintained anchor set rather than the popularity of a commercial authority. The specific issuer and key parameters of mariner-partner-api's certificate of record are carried in the inventory database; what matters to the review is whether that issuer sits inside the governed anchor set, since a leaf that validates today but chains outside the set is still a rotation candidate on governance grounds.

Cipher-suite selection at mariner-partner-api was inspected for obviously deprecated constructions. While suite negotiation is not itself a graded axis in this review, a modern protocol version on https://partner-api.prod.mariner.internal strongly constrains the suite space, which is part of why the version allow-list does so much of the work and why a downgrade is treated as consequential rather than cosmetic.

Partner-facing exposure was a specific consideration for mariner-partner-api where federated third parties consume it. Federation raises the stakes of a mutual-TLS gap because the counterparty's assurance depends on it, which is why a production federation surface is held to the client-authentication expectation without sympathy for integration convenience.

Early-data exposure for mariner-partner-api was considered where 0-RTT resumption is enabled. Replayable early data is an application-layer hazard rather than a transport-policy axis, so it does not move mariner-partner-api's disposition, but it is flagged for team-partners as a design note to weigh against the latency benefit on the prod surface.

The mariner-partner-api interconnect was modelled as part of the broader dependency graph. A weakness here propagates to every caller that trusts this endpoint, which is why the review resists the temptation to treat exposes a constrained surface to federated third parties as a low-stakes carve-out. The posture is assessed on its own merits and against the same bar as the busiest production path.

Certificate-transparency presence for mariner-partner-api's leaf was checked as a tamper-evidence signal. CT inclusion does not by itself make a certificate compliant — it is neither a protocol version nor an issuer-trust decision — but its absence on a publicly reachable prod endpoint would be a flag worth a follow-up outside this review's transport remit.

Truststore management on the prod side of mariner-partner-api matters for mutual TLS. Where the endpoint demands a client certificate, the set of client anchors it accepts is an operational concern for team-partners; the review records only whether a client certificate was presented and validated, leaving truststore curation to the owning team's runbooks.

Mutual TLS expectations for mariner-partner-api follow the environment. The production trust boundary requires a client certificate; a non-production surface is not penalised for the absence of one. Where mariner-partner-api is expected to present a client certificate and the capture shows none, the gap is a protocol-level finding unless a waiver of the matching kind and scope is in force.

ALPN negotiation at mariner-partner-api was noted to confirm the application protocol riding over the tunnel, but protocol-version policy is enforced at the TLS layer and does not bend to the application above it. A modern application protocol over a legacy transport is still a transport finding for mariner-partner-api.

Finally, mariner-partner-api was checked for consistency between its environment label and its exposure. A service labelled prod is assessed under the rules for that environment; the review does not reclassify a surface to soften a finding, and team-partners retains the route to reclassification through inventory governance rather than through this review.

The harness recorded the mariner-partner-api endpoint over successive sweeps; only the most recent capture per service is treated as authoritative, since earlier sweeps frequently predate a remediation or a re-issue. Reviewers are reminded that the captured negotiation outcomes, the chain-validation result, and the leaf fingerprint seen on the wire are held in the inventory database and must be read from there, not inferred from this narrative.

Revocation freshness was considered for mariner-partner-api. The review notes whether the endpoint's stapled status was recent and whether the validating party had a live path to revocation information, but treats stapling hygiene as advisory this cycle; the governing chain question remains whether the presented chain validated to a trusted anchor at capture time.

Where mariner-partner-api terminates TLS at a sidecar or a shared load balancer rather than in the application process, the review attributes the captured posture to the service as exposed on https://partner-api.prod.mariner.internal. Termination topology is an implementation detail; the obligation to meet policy attaches to the exposed prod surface regardless of which component holds the key.

Encrypted-client-hello readiness for mariner-partner-api was recorded as informational. ECH changes what an on-path observer can see about the handshake to https://partner-api.prod.mariner.internal but does not alter any graded axis here; it neither relaxes the protocol floor nor changes how a client certificate or a chain is judged.

Ownership context: team-partners maintains mariner-partner-api and is the counterparty for any remediation. The review records owning teams so that rotation and re-issuance work lands with the group that can actually schedule a maintenance window on the prod surface, but ownership confers no relief from policy.

Cross-signing arrangements that touch mariner-partner-api's issuer were enumerated to make sure the chain the review reasons about is the chain clients actually build. A leaf can validate via more than one path; the governed question for mariner-partner-api is whether the issuer of record sits in the trust anchor set, independent of which cross-signed path a particular client happens to choose.

Renewal automation for mariner-partner-api was reviewed at the level of 'does a pipeline exist', not 'did it run'. An ACME-style renewal loop lowers the operational cost of the rotation findings this review may raise, but the disposition is taken from the captured state of https://partner-api.prod.mariner.internal, so a renewal that is configured but not yet effective does not pre-empt a near-expiry finding.

Certificate lifetime is the other half of hygiene. A leaf approaching its not-after boundary inside the rotation window is scheduled for replacement well ahead of the cliff, on the principle that a lapse on the prod surface is an availability incident as much as a security one. The window is uniform across services so that nothing in mariner-partner-api's profile earns special treatment.

SNI and virtual-host disambiguation were verified for mariner-partner-api so that the captured leaf is unambiguously the one https://partner-api.prod.mariner.internal intends to serve. A mismatch between the requested name and the served certificate would itself be an integrity concern, which is one more reason the observed fingerprint is compared against the inventory of record rather than assumed.

The review explicitly separated configuration intent from observed behaviour for mariner-partner-api. A configuration file may declare a strict posture, but if the captured evidence on https://partner-api.prod.mariner.internal shows otherwise, the evidence governs the finding; conversely a permissive-looking configuration that nonetheless negotiated within policy is judged on what actually happened on the wire.

Within the review boundary, mariner-partner-api (svc-010) exposes a constrained surface to federated third parties. It is owned by team-partners and presents on https://partner-api.prod.mariner.internal, which the inventory classifies as a prod surface. The transport posture of any prod endpoint is weighed against the operative policy rather than against historical convention, and the assessment proceeds from the evidence of record rather than from operator attestation.

Documentation for mariner-partner-api was cross-checked against the configuration set. Where a policy value is needed — the rotation window, the protocol allow-list, the key floors, or the issuer anchor set — it is read from the validated configuration rather than from this prose, which paraphrases policy for the reader's convenience only.

### svc-011 — mariner-audit-log

Early-data exposure for mariner-audit-log was considered where 0-RTT resumption is enabled. Replayable early data is an application-layer hazard rather than a transport-policy axis, so it does not move mariner-audit-log's disposition, but it is flagged for team-security as a design note to weigh against the latency benefit on the prod surface.

The mariner-audit-log interconnect was modelled as part of the broader dependency graph. A weakness here propagates to every caller that trusts this endpoint, which is why the review resists the temptation to treat is the append-only system of record for security events as a low-stakes carve-out. The posture is assessed on its own merits and against the same bar as the busiest production path.

Certificate-transparency presence for mariner-audit-log's leaf was checked as a tamper-evidence signal. CT inclusion does not by itself make a certificate compliant — it is neither a protocol version nor an issuer-trust decision — but its absence on a publicly reachable prod endpoint would be a flag worth a follow-up outside this review's transport remit.

Exception status. mariner-audit-log (svc-011) carries no transport-security waiver of any kind in the register — no protocol exception, no mutual-TLS carve-out, and no chain exception. It is therefore assessed directly against the operative policy, with the captured evidence in the inventory database standing as the sole record of how the prod endpoint actually negotiated.

Truststore management on the prod side of mariner-audit-log matters for mutual TLS. Where the endpoint demands a client certificate, the set of client anchors it accepts is an operational concern for team-security; the review records only whether a client certificate was presented and validated, leaving truststore curation to the owning team's runbooks.

Mutual TLS expectations for mariner-audit-log follow the environment. The production trust boundary requires a client certificate; a non-production surface is not penalised for the absence of one. Where mariner-audit-log is expected to present a client certificate and the capture shows none, the gap is a protocol-level finding unless a waiver of the matching kind and scope is in force.

ALPN negotiation at mariner-audit-log was noted to confirm the application protocol riding over the tunnel, but protocol-version policy is enforced at the TLS layer and does not bend to the application above it. A modern application protocol over a legacy transport is still a transport finding for mariner-audit-log.

Finally, mariner-audit-log was checked for consistency between its environment label and its exposure. A service labelled prod is assessed under the rules for that environment; the review does not reclassify a surface to soften a finding, and team-security retains the route to reclassification through inventory governance rather than through this review.

The harness recorded the mariner-audit-log endpoint over successive sweeps; only the most recent capture per service is treated as authoritative, since earlier sweeps frequently predate a remediation or a re-issue. Reviewers are reminded that the captured negotiation outcomes, the chain-validation result, and the leaf fingerprint seen on the wire are held in the inventory database and must be read from there, not inferred from this narrative.

Revocation freshness was considered for mariner-audit-log. The review notes whether the endpoint's stapled status was recent and whether the validating party had a live path to revocation information, but treats stapling hygiene as advisory this cycle; the governing chain question remains whether the presented chain validated to a trusted anchor at capture time.

Where mariner-audit-log terminates TLS at a sidecar or a shared load balancer rather than in the application process, the review attributes the captured posture to the service as exposed on https://audit-log.prod.mariner.internal. Termination topology is an implementation detail; the obligation to meet policy attaches to the exposed prod surface regardless of which component holds the key.

Encrypted-client-hello readiness for mariner-audit-log was recorded as informational. ECH changes what an on-path observer can see about the handshake to https://audit-log.prod.mariner.internal but does not alter any graded axis here; it neither relaxes the protocol floor nor changes how a client certificate or a chain is judged.

Ownership context: team-security maintains mariner-audit-log and is the counterparty for any remediation. The review records owning teams so that rotation and re-issuance work lands with the group that can actually schedule a maintenance window on the prod surface, but ownership confers no relief from policy.

Cross-signing arrangements that touch mariner-audit-log's issuer were enumerated to make sure the chain the review reasons about is the chain clients actually build. A leaf can validate via more than one path; the governed question for mariner-audit-log is whether the issuer of record sits in the trust anchor set, independent of which cross-signed path a particular client happens to choose.

Renewal automation for mariner-audit-log was reviewed at the level of 'does a pipeline exist', not 'did it run'. An ACME-style renewal loop lowers the operational cost of the rotation findings this review may raise, but the disposition is taken from the captured state of https://audit-log.prod.mariner.internal, so a renewal that is configured but not yet effective does not pre-empt a near-expiry finding.

Certificate lifetime is the other half of hygiene. A leaf approaching its not-after boundary inside the rotation window is scheduled for replacement well ahead of the cliff, on the principle that a lapse on the prod surface is an availability incident as much as a security one. The window is uniform across services so that nothing in mariner-audit-log's profile earns special treatment.

SNI and virtual-host disambiguation were verified for mariner-audit-log so that the captured leaf is unambiguously the one https://audit-log.prod.mariner.internal intends to serve. A mismatch between the requested name and the served certificate would itself be an integrity concern, which is one more reason the observed fingerprint is compared against the inventory of record rather than assumed.

The review explicitly separated configuration intent from observed behaviour for mariner-audit-log. A configuration file may declare a strict posture, but if the captured evidence on https://audit-log.prod.mariner.internal shows otherwise, the evidence governs the finding; conversely a permissive-looking configuration that nonetheless negotiated within policy is judged on what actually happened on the wire.

Within the review boundary, mariner-audit-log (svc-011) is the append-only system of record for security events. It is owned by team-security and presents on https://audit-log.prod.mariner.internal, which the inventory classifies as a prod surface. The transport posture of any prod endpoint is weighed against the operative policy rather than against historical convention, and the assessment proceeds from the evidence of record rather than from operator attestation.

Documentation for mariner-audit-log was cross-checked against the configuration set. Where a policy value is needed — the rotation window, the protocol allow-list, the key floors, or the issuer anchor set — it is read from the validated configuration rather than from this prose, which paraphrases policy for the reader's convenience only.

For mesh participants such as mariner-audit-log, certificate rotation is automated through the issuing control plane, which lowers the cost of a rotation finding but does not remove the obligation: an automated rotation that has not yet run still leaves a soon-to-expire leaf on https://audit-log.prod.mariner.internal, and the review grades the state at capture time, not the intention encoded in automation.

Revocation-list distribution touching mariner-audit-log's issuer was sanity-checked so that a client choosing CRL over stapled status still has a path. As with stapling, the review treats CRL reachability as advisory this cycle; the governing question for mariner-audit-log remains whether the presented chain validated at capture time.

Evidence handling for mariner-audit-log is deliberately conservative. When the fingerprint observed on the wire disagrees with the inventory of record, the review does not attempt to reconcile the two in the agent's favour; the disagreement is itself the finding, and it is escalated rather than waived, regardless of any paperwork that might otherwise have applied.

Key-ceremony provenance for mariner-audit-log's material was reviewed at a high level. Where team-security can attest that the private key was generated and held in a hardware security module, the operational risk of the key is lower, but provenance does not raise an under-strength key above the floor or extend a certificate past its not-after date.

Wildcard usage at mariner-audit-log was noted where present. A wildcard leaf broadens blast radius if its key is compromised, so although a wildcard is not itself a finding, it raises the priority of the hygiene rules for mariner-audit-log — a near-expiry or under-strength wildcard is a rotation the review would rather see scheduled sooner than later.

Key strength for mariner-audit-log is judged against the floor for its algorithm family. The review does not grade keys on a curve: a key below the floor is a rotation finding irrespective of the sensitivity of the workload, because under-strength material weakens the whole interconnect graph that mariner-audit-log participates in.

Session resumption behaviour for mariner-audit-log was characterised so that repeat captures could be compared fairly. Resumption can mask a renegotiated parameter, so the harness records full-handshake outcomes where it can; the authoritative capture for mariner-audit-log is still the most recent row, and resumption never changes which row is current.

Audit retention for mariner-audit-log's captures follows the standard schedule: every sweep is retained, and the review reads the latest. This matters when reconstructing a finding months later — the row that was current at review time is identifiable by its capture timestamp, and the reconstruction must use that row rather than whatever happens to be newest at reconstruction time.

Certificate pinning by clients of mariner-audit-log was inventoried lightly, because pinning interacts badly with rotation: a pinned client can break when mariner-audit-log legitimately rotates. The review's rotation findings therefore come with a reminder that any pin held against mariner-audit-log's current leaf must be updated in lockstep with the re-issue.

Operationally, mariner-audit-log has been stable, but stability is not conformance. The review separates 'has not failed yet' from 'meets policy today', and it is the latter that governs the finding. Where the captured evidence and the live configuration disagree, the captured evidence is taken as the ground truth.

Forward-looking, the review recorded whether mariner-audit-log is on a path toward post-quantum-ready key exchange. This cycle treats PQC readiness as informational; it changes no disposition, but it is captured so that team-security can sequence the work against the rotation cadence the hygiene rules already impose.

Clock discipline was assumed but noted for mariner-audit-log: certificate validity windows are only meaningful if the validating hosts agree on the time. The review reasons about not-after relative to a single fixed review date, which removes any ambiguity that wall-clock skew on individual probers might otherwise introduce into the near-expiry judgement.

The protocol floor matters for mariner-audit-log because a single tolerated downgrade becomes a precedent. The review treats any negotiated version outside the allowed set as a finding in every environment, including development, so that a sandbox habit does not migrate into production by copy-paste.

Transport strictness headers on responses from mariner-audit-log were observed where applicable. Strict-transport signalling reduces downgrade opportunity for browser clients but does not substitute for the server-side protocol floor; the review credits it as defence in depth and nothing more for a prod surface.

Subject-alternative-name coverage on mariner-audit-log's leaf was checked against the hostnames https://audit-log.prod.mariner.internal actually answers for. A name not covered by the served certificate would surface as a verification failure in the capture, so SAN gaps tend to show up indirectly through the recorded verification outcome rather than as a separate graded axis.

For mariner-audit-log, issuer trust is a policy question settled against the maintained anchor set rather than the popularity of a commercial authority. The specific issuer and key parameters of mariner-audit-log's certificate of record are carried in the inventory database; what matters to the review is whether that issuer sits inside the governed anchor set, since a leaf that validates today but chains outside the set is still a rotation candidate on governance grounds.

Cipher-suite selection at mariner-audit-log was inspected for obviously deprecated constructions. While suite negotiation is not itself a graded axis in this review, a modern protocol version on https://audit-log.prod.mariner.internal strongly constrains the suite space, which is part of why the version allow-list does so much of the work and why a downgrade is treated as consequential rather than cosmetic.

Partner-facing exposure was a specific consideration for mariner-audit-log where federated third parties consume it. Federation raises the stakes of a mutual-TLS gap because the counterparty's assurance depends on it, which is why a production federation surface is held to the client-authentication expectation without sympathy for integration convenience.

### svc-012 — mariner-notifications

Documentation for mariner-notifications was cross-checked against the configuration set. Where a policy value is needed — the rotation window, the protocol allow-list, the key floors, or the issuer anchor set — it is read from the validated configuration rather than from this prose, which paraphrases policy for the reader's convenience only.

Exception status. mariner-notifications (svc-012) carries no transport-security waiver of any kind in the register — no protocol exception, no mutual-TLS carve-out, and no chain exception. It is therefore assessed directly against the operative policy, with the captured evidence in the inventory database standing as the sole record of how the prod endpoint actually negotiated.

For mesh participants such as mariner-notifications, certificate rotation is automated through the issuing control plane, which lowers the cost of a rotation finding but does not remove the obligation: an automated rotation that has not yet run still leaves a soon-to-expire leaf on https://notifications.prod.mariner.internal, and the review grades the state at capture time, not the intention encoded in automation.

Revocation-list distribution touching mariner-notifications's issuer was sanity-checked so that a client choosing CRL over stapled status still has a path. As with stapling, the review treats CRL reachability as advisory this cycle; the governing question for mariner-notifications remains whether the presented chain validated at capture time.

Evidence handling for mariner-notifications is deliberately conservative. When the fingerprint observed on the wire disagrees with the inventory of record, the review does not attempt to reconcile the two in the agent's favour; the disagreement is itself the finding, and it is escalated rather than waived, regardless of any paperwork that might otherwise have applied.

Key-ceremony provenance for mariner-notifications's material was reviewed at a high level. Where team-messaging can attest that the private key was generated and held in a hardware security module, the operational risk of the key is lower, but provenance does not raise an under-strength key above the floor or extend a certificate past its not-after date.

Wildcard usage at mariner-notifications was noted where present. A wildcard leaf broadens blast radius if its key is compromised, so although a wildcard is not itself a finding, it raises the priority of the hygiene rules for mariner-notifications — a near-expiry or under-strength wildcard is a rotation the review would rather see scheduled sooner than later.

Key strength for mariner-notifications is judged against the floor for its algorithm family. The review does not grade keys on a curve: a key below the floor is a rotation finding irrespective of the sensitivity of the workload, because under-strength material weakens the whole interconnect graph that mariner-notifications participates in.

Session resumption behaviour for mariner-notifications was characterised so that repeat captures could be compared fairly. Resumption can mask a renegotiated parameter, so the harness records full-handshake outcomes where it can; the authoritative capture for mariner-notifications is still the most recent row, and resumption never changes which row is current.

Audit retention for mariner-notifications's captures follows the standard schedule: every sweep is retained, and the review reads the latest. This matters when reconstructing a finding months later — the row that was current at review time is identifiable by its capture timestamp, and the reconstruction must use that row rather than whatever happens to be newest at reconstruction time.

Certificate pinning by clients of mariner-notifications was inventoried lightly, because pinning interacts badly with rotation: a pinned client can break when mariner-notifications legitimately rotates. The review's rotation findings therefore come with a reminder that any pin held against mariner-notifications's current leaf must be updated in lockstep with the re-issue.

Operationally, mariner-notifications has been stable, but stability is not conformance. The review separates 'has not failed yet' from 'meets policy today', and it is the latter that governs the finding. Where the captured evidence and the live configuration disagree, the captured evidence is taken as the ground truth.

Forward-looking, the review recorded whether mariner-notifications is on a path toward post-quantum-ready key exchange. This cycle treats PQC readiness as informational; it changes no disposition, but it is captured so that team-messaging can sequence the work against the rotation cadence the hygiene rules already impose.

Clock discipline was assumed but noted for mariner-notifications: certificate validity windows are only meaningful if the validating hosts agree on the time. The review reasons about not-after relative to a single fixed review date, which removes any ambiguity that wall-clock skew on individual probers might otherwise introduce into the near-expiry judgement.

The protocol floor matters for mariner-notifications because a single tolerated downgrade becomes a precedent. The review treats any negotiated version outside the allowed set as a finding in every environment, including development, so that a sandbox habit does not migrate into production by copy-paste.

Transport strictness headers on responses from mariner-notifications were observed where applicable. Strict-transport signalling reduces downgrade opportunity for browser clients but does not substitute for the server-side protocol floor; the review credits it as defence in depth and nothing more for a prod surface.

Subject-alternative-name coverage on mariner-notifications's leaf was checked against the hostnames https://notifications.prod.mariner.internal actually answers for. A name not covered by the served certificate would surface as a verification failure in the capture, so SAN gaps tend to show up indirectly through the recorded verification outcome rather than as a separate graded axis.

For mariner-notifications, issuer trust is a policy question settled against the maintained anchor set rather than the popularity of a commercial authority. The specific issuer and key parameters of mariner-notifications's certificate of record are carried in the inventory database; what matters to the review is whether that issuer sits inside the governed anchor set, since a leaf that validates today but chains outside the set is still a rotation candidate on governance grounds.

Cipher-suite selection at mariner-notifications was inspected for obviously deprecated constructions. While suite negotiation is not itself a graded axis in this review, a modern protocol version on https://notifications.prod.mariner.internal strongly constrains the suite space, which is part of why the version allow-list does so much of the work and why a downgrade is treated as consequential rather than cosmetic.

Partner-facing exposure was a specific consideration for mariner-notifications where federated third parties consume it. Federation raises the stakes of a mutual-TLS gap because the counterparty's assurance depends on it, which is why a production federation surface is held to the client-authentication expectation without sympathy for integration convenience.

Early-data exposure for mariner-notifications was considered where 0-RTT resumption is enabled. Replayable early data is an application-layer hazard rather than a transport-policy axis, so it does not move mariner-notifications's disposition, but it is flagged for team-messaging as a design note to weigh against the latency benefit on the prod surface.

The mariner-notifications interconnect was modelled as part of the broader dependency graph. A weakness here propagates to every caller that trusts this endpoint, which is why the review resists the temptation to treat delivers transactional mail and push to end users as a low-stakes carve-out. The posture is assessed on its own merits and against the same bar as the busiest production path.

Certificate-transparency presence for mariner-notifications's leaf was checked as a tamper-evidence signal. CT inclusion does not by itself make a certificate compliant — it is neither a protocol version nor an issuer-trust decision — but its absence on a publicly reachable prod endpoint would be a flag worth a follow-up outside this review's transport remit.

Truststore management on the prod side of mariner-notifications matters for mutual TLS. Where the endpoint demands a client certificate, the set of client anchors it accepts is an operational concern for team-messaging; the review records only whether a client certificate was presented and validated, leaving truststore curation to the owning team's runbooks.

Mutual TLS expectations for mariner-notifications follow the environment. The production trust boundary requires a client certificate; a non-production surface is not penalised for the absence of one. Where mariner-notifications is expected to present a client certificate and the capture shows none, the gap is a protocol-level finding unless a waiver of the matching kind and scope is in force.

ALPN negotiation at mariner-notifications was noted to confirm the application protocol riding over the tunnel, but protocol-version policy is enforced at the TLS layer and does not bend to the application above it. A modern application protocol over a legacy transport is still a transport finding for mariner-notifications.

Finally, mariner-notifications was checked for consistency between its environment label and its exposure. A service labelled prod is assessed under the rules for that environment; the review does not reclassify a surface to soften a finding, and team-messaging retains the route to reclassification through inventory governance rather than through this review.

The harness recorded the mariner-notifications endpoint over successive sweeps; only the most recent capture per service is treated as authoritative, since earlier sweeps frequently predate a remediation or a re-issue. Reviewers are reminded that the captured negotiation outcomes, the chain-validation result, and the leaf fingerprint seen on the wire are held in the inventory database and must be read from there, not inferred from this narrative.

Revocation freshness was considered for mariner-notifications. The review notes whether the endpoint's stapled status was recent and whether the validating party had a live path to revocation information, but treats stapling hygiene as advisory this cycle; the governing chain question remains whether the presented chain validated to a trusted anchor at capture time.

Where mariner-notifications terminates TLS at a sidecar or a shared load balancer rather than in the application process, the review attributes the captured posture to the service as exposed on https://notifications.prod.mariner.internal. Termination topology is an implementation detail; the obligation to meet policy attaches to the exposed prod surface regardless of which component holds the key.

Encrypted-client-hello readiness for mariner-notifications was recorded as informational. ECH changes what an on-path observer can see about the handshake to https://notifications.prod.mariner.internal but does not alter any graded axis here; it neither relaxes the protocol floor nor changes how a client certificate or a chain is judged.

Ownership context: team-messaging maintains mariner-notifications and is the counterparty for any remediation. The review records owning teams so that rotation and re-issuance work lands with the group that can actually schedule a maintenance window on the prod surface, but ownership confers no relief from policy.

Cross-signing arrangements that touch mariner-notifications's issuer were enumerated to make sure the chain the review reasons about is the chain clients actually build. A leaf can validate via more than one path; the governed question for mariner-notifications is whether the issuer of record sits in the trust anchor set, independent of which cross-signed path a particular client happens to choose.

Renewal automation for mariner-notifications was reviewed at the level of 'does a pipeline exist', not 'did it run'. An ACME-style renewal loop lowers the operational cost of the rotation findings this review may raise, but the disposition is taken from the captured state of https://notifications.prod.mariner.internal, so a renewal that is configured but not yet effective does not pre-empt a near-expiry finding.

Certificate lifetime is the other half of hygiene. A leaf approaching its not-after boundary inside the rotation window is scheduled for replacement well ahead of the cliff, on the principle that a lapse on the prod surface is an availability incident as much as a security one. The window is uniform across services so that nothing in mariner-notifications's profile earns special treatment.

SNI and virtual-host disambiguation were verified for mariner-notifications so that the captured leaf is unambiguously the one https://notifications.prod.mariner.internal intends to serve. A mismatch between the requested name and the served certificate would itself be an integrity concern, which is one more reason the observed fingerprint is compared against the inventory of record rather than assumed.

The review explicitly separated configuration intent from observed behaviour for mariner-notifications. A configuration file may declare a strict posture, but if the captured evidence on https://notifications.prod.mariner.internal shows otherwise, the evidence governs the finding; conversely a permissive-looking configuration that nonetheless negotiated within policy is judged on what actually happened on the wire.

Within the review boundary, mariner-notifications (svc-012) delivers transactional mail and push to end users. It is owned by team-messaging and presents on https://notifications.prod.mariner.internal, which the inventory classifies as a prod surface. The transport posture of any prod endpoint is weighed against the operative policy rather than against historical convention, and the assessment proceeds from the evidence of record rather than from operator attestation.

### svc-013 — mariner-staging-portal

Partner-facing exposure was a specific consideration for mariner-staging-portal where federated third parties consume it. Federation raises the stakes of a mutual-TLS gap because the counterparty's assurance depends on it, which is why a production federation surface is held to the client-authentication expectation without sympathy for integration convenience.

Early-data exposure for mariner-staging-portal was considered where 0-RTT resumption is enabled. Replayable early data is an application-layer hazard rather than a transport-policy axis, so it does not move mariner-staging-portal's disposition, but it is flagged for team-web as a design note to weigh against the latency benefit on the staging surface.

Exception status. mariner-staging-portal (svc-013) carries no transport-security waiver of any kind in the register — no protocol exception, no mutual-TLS carve-out, and no chain exception. It is therefore assessed directly against the operative policy, with the captured evidence in the inventory database standing as the sole record of how the staging endpoint actually negotiated.

The mariner-staging-portal interconnect was modelled as part of the broader dependency graph. A weakness here propagates to every caller that trusts this endpoint, which is why the review resists the temptation to treat is the pre-production console used by release engineering as a low-stakes carve-out. The posture is assessed on its own merits and against the same bar as the busiest production path.

Certificate-transparency presence for mariner-staging-portal's leaf was checked as a tamper-evidence signal. CT inclusion does not by itself make a certificate compliant — it is neither a protocol version nor an issuer-trust decision — but its absence on a publicly reachable staging endpoint would be a flag worth a follow-up outside this review's transport remit.

Truststore management on the staging side of mariner-staging-portal matters for mutual TLS. Where the endpoint demands a client certificate, the set of client anchors it accepts is an operational concern for team-web; the review records only whether a client certificate was presented and validated, leaving truststore curation to the owning team's runbooks.

Mutual TLS expectations for mariner-staging-portal follow the environment. The production trust boundary requires a client certificate; a non-production surface is not penalised for the absence of one. Where mariner-staging-portal is expected to present a client certificate and the capture shows none, the gap is a protocol-level finding unless a waiver of the matching kind and scope is in force.

ALPN negotiation at mariner-staging-portal was noted to confirm the application protocol riding over the tunnel, but protocol-version policy is enforced at the TLS layer and does not bend to the application above it. A modern application protocol over a legacy transport is still a transport finding for mariner-staging-portal.

Finally, mariner-staging-portal was checked for consistency between its environment label and its exposure. A service labelled staging is assessed under the rules for that environment; the review does not reclassify a surface to soften a finding, and team-web retains the route to reclassification through inventory governance rather than through this review.

The harness recorded the mariner-staging-portal endpoint over successive sweeps; only the most recent capture per service is treated as authoritative, since earlier sweeps frequently predate a remediation or a re-issue. Reviewers are reminded that the captured negotiation outcomes, the chain-validation result, and the leaf fingerprint seen on the wire are held in the inventory database and must be read from there, not inferred from this narrative.

Revocation freshness was considered for mariner-staging-portal. The review notes whether the endpoint's stapled status was recent and whether the validating party had a live path to revocation information, but treats stapling hygiene as advisory this cycle; the governing chain question remains whether the presented chain validated to a trusted anchor at capture time.

Where mariner-staging-portal terminates TLS at a sidecar or a shared load balancer rather than in the application process, the review attributes the captured posture to the service as exposed on https://staging-portal.staging.mariner.internal. Termination topology is an implementation detail; the obligation to meet policy attaches to the exposed staging surface regardless of which component holds the key.

Encrypted-client-hello readiness for mariner-staging-portal was recorded as informational. ECH changes what an on-path observer can see about the handshake to https://staging-portal.staging.mariner.internal but does not alter any graded axis here; it neither relaxes the protocol floor nor changes how a client certificate or a chain is judged.

Ownership context: team-web maintains mariner-staging-portal and is the counterparty for any remediation. The review records owning teams so that rotation and re-issuance work lands with the group that can actually schedule a maintenance window on the staging surface, but ownership confers no relief from policy.

Cross-signing arrangements that touch mariner-staging-portal's issuer were enumerated to make sure the chain the review reasons about is the chain clients actually build. A leaf can validate via more than one path; the governed question for mariner-staging-portal is whether the issuer of record sits in the trust anchor set, independent of which cross-signed path a particular client happens to choose.

Renewal automation for mariner-staging-portal was reviewed at the level of 'does a pipeline exist', not 'did it run'. An ACME-style renewal loop lowers the operational cost of the rotation findings this review may raise, but the disposition is taken from the captured state of https://staging-portal.staging.mariner.internal, so a renewal that is configured but not yet effective does not pre-empt a near-expiry finding.

Certificate lifetime is the other half of hygiene. A leaf approaching its not-after boundary inside the rotation window is scheduled for replacement well ahead of the cliff, on the principle that a lapse on the staging surface is an availability incident as much as a security one. The window is uniform across services so that nothing in mariner-staging-portal's profile earns special treatment.

SNI and virtual-host disambiguation were verified for mariner-staging-portal so that the captured leaf is unambiguously the one https://staging-portal.staging.mariner.internal intends to serve. A mismatch between the requested name and the served certificate would itself be an integrity concern, which is one more reason the observed fingerprint is compared against the inventory of record rather than assumed.

The review explicitly separated configuration intent from observed behaviour for mariner-staging-portal. A configuration file may declare a strict posture, but if the captured evidence on https://staging-portal.staging.mariner.internal shows otherwise, the evidence governs the finding; conversely a permissive-looking configuration that nonetheless negotiated within policy is judged on what actually happened on the wire.

Within the review boundary, mariner-staging-portal (svc-013) is the pre-production console used by release engineering. It is owned by team-web and presents on https://staging-portal.staging.mariner.internal, which the inventory classifies as a staging surface. The transport posture of any staging endpoint is weighed against the operative policy rather than against historical convention, and the assessment proceeds from the evidence of record rather than from operator attestation.

Documentation for mariner-staging-portal was cross-checked against the configuration set. Where a policy value is needed — the rotation window, the protocol allow-list, the key floors, or the issuer anchor set — it is read from the validated configuration rather than from this prose, which paraphrases policy for the reader's convenience only.

For mesh participants such as mariner-staging-portal, certificate rotation is automated through the issuing control plane, which lowers the cost of a rotation finding but does not remove the obligation: an automated rotation that has not yet run still leaves a soon-to-expire leaf on https://staging-portal.staging.mariner.internal, and the review grades the state at capture time, not the intention encoded in automation.

Revocation-list distribution touching mariner-staging-portal's issuer was sanity-checked so that a client choosing CRL over stapled status still has a path. As with stapling, the review treats CRL reachability as advisory this cycle; the governing question for mariner-staging-portal remains whether the presented chain validated at capture time.

Evidence handling for mariner-staging-portal is deliberately conservative. When the fingerprint observed on the wire disagrees with the inventory of record, the review does not attempt to reconcile the two in the agent's favour; the disagreement is itself the finding, and it is escalated rather than waived, regardless of any paperwork that might otherwise have applied.

Key-ceremony provenance for mariner-staging-portal's material was reviewed at a high level. Where team-web can attest that the private key was generated and held in a hardware security module, the operational risk of the key is lower, but provenance does not raise an under-strength key above the floor or extend a certificate past its not-after date.

Wildcard usage at mariner-staging-portal was noted where present. A wildcard leaf broadens blast radius if its key is compromised, so although a wildcard is not itself a finding, it raises the priority of the hygiene rules for mariner-staging-portal — a near-expiry or under-strength wildcard is a rotation the review would rather see scheduled sooner than later.

Key strength for mariner-staging-portal is judged against the floor for its algorithm family. The review does not grade keys on a curve: a key below the floor is a rotation finding irrespective of the sensitivity of the workload, because under-strength material weakens the whole interconnect graph that mariner-staging-portal participates in.

Session resumption behaviour for mariner-staging-portal was characterised so that repeat captures could be compared fairly. Resumption can mask a renegotiated parameter, so the harness records full-handshake outcomes where it can; the authoritative capture for mariner-staging-portal is still the most recent row, and resumption never changes which row is current.

Audit retention for mariner-staging-portal's captures follows the standard schedule: every sweep is retained, and the review reads the latest. This matters when reconstructing a finding months later — the row that was current at review time is identifiable by its capture timestamp, and the reconstruction must use that row rather than whatever happens to be newest at reconstruction time.

Certificate pinning by clients of mariner-staging-portal was inventoried lightly, because pinning interacts badly with rotation: a pinned client can break when mariner-staging-portal legitimately rotates. The review's rotation findings therefore come with a reminder that any pin held against mariner-staging-portal's current leaf must be updated in lockstep with the re-issue.

Operationally, mariner-staging-portal has been stable, but stability is not conformance. The review separates 'has not failed yet' from 'meets policy today', and it is the latter that governs the finding. Where the captured evidence and the live configuration disagree, the captured evidence is taken as the ground truth.

Forward-looking, the review recorded whether mariner-staging-portal is on a path toward post-quantum-ready key exchange. This cycle treats PQC readiness as informational; it changes no disposition, but it is captured so that team-web can sequence the work against the rotation cadence the hygiene rules already impose.

Clock discipline was assumed but noted for mariner-staging-portal: certificate validity windows are only meaningful if the validating hosts agree on the time. The review reasons about not-after relative to a single fixed review date, which removes any ambiguity that wall-clock skew on individual probers might otherwise introduce into the near-expiry judgement.

The protocol floor matters for mariner-staging-portal because a single tolerated downgrade becomes a precedent. The review treats any negotiated version outside the allowed set as a finding in every environment, including development, so that a sandbox habit does not migrate into production by copy-paste.

Transport strictness headers on responses from mariner-staging-portal were observed where applicable. Strict-transport signalling reduces downgrade opportunity for browser clients but does not substitute for the server-side protocol floor; the review credits it as defence in depth and nothing more for a staging surface.

Subject-alternative-name coverage on mariner-staging-portal's leaf was checked against the hostnames https://staging-portal.staging.mariner.internal actually answers for. A name not covered by the served certificate would surface as a verification failure in the capture, so SAN gaps tend to show up indirectly through the recorded verification outcome rather than as a separate graded axis.

For mariner-staging-portal, issuer trust is a policy question settled against the maintained anchor set rather than the popularity of a commercial authority. The specific issuer and key parameters of mariner-staging-portal's certificate of record are carried in the inventory database; what matters to the review is whether that issuer sits inside the governed anchor set, since a leaf that validates today but chains outside the set is still a rotation candidate on governance grounds.

Cipher-suite selection at mariner-staging-portal was inspected for obviously deprecated constructions. While suite negotiation is not itself a graded axis in this review, a modern protocol version on https://staging-portal.staging.mariner.internal strongly constrains the suite space, which is part of why the version allow-list does so much of the work and why a downgrade is treated as consequential rather than cosmetic.

### svc-014 — mariner-reporting

Within the review boundary, mariner-reporting (svc-014) compiles scheduled analytical extracts for finance. It is owned by team-analytics and presents on https://reporting.prod.mariner.internal, which the inventory classifies as a prod surface. The transport posture of any prod endpoint is weighed against the operative policy rather than against historical convention, and the assessment proceeds from the evidence of record rather than from operator attestation.

Documentation for mariner-reporting was cross-checked against the configuration set. Where a policy value is needed — the rotation window, the protocol allow-list, the key floors, or the issuer anchor set — it is read from the validated configuration rather than from this prose, which paraphrases policy for the reader's convenience only.

For mesh participants such as mariner-reporting, certificate rotation is automated through the issuing control plane, which lowers the cost of a rotation finding but does not remove the obligation: an automated rotation that has not yet run still leaves a soon-to-expire leaf on https://reporting.prod.mariner.internal, and the review grades the state at capture time, not the intention encoded in automation.

Exception status. mariner-reporting (svc-014) carries no transport-security waiver of any kind in the register — no protocol exception, no mutual-TLS carve-out, and no chain exception. It is therefore assessed directly against the operative policy, with the captured evidence in the inventory database standing as the sole record of how the prod endpoint actually negotiated.

Revocation-list distribution touching mariner-reporting's issuer was sanity-checked so that a client choosing CRL over stapled status still has a path. As with stapling, the review treats CRL reachability as advisory this cycle; the governing question for mariner-reporting remains whether the presented chain validated at capture time.

Evidence handling for mariner-reporting is deliberately conservative. When the fingerprint observed on the wire disagrees with the inventory of record, the review does not attempt to reconcile the two in the agent's favour; the disagreement is itself the finding, and it is escalated rather than waived, regardless of any paperwork that might otherwise have applied.

Key-ceremony provenance for mariner-reporting's material was reviewed at a high level. Where team-analytics can attest that the private key was generated and held in a hardware security module, the operational risk of the key is lower, but provenance does not raise an under-strength key above the floor or extend a certificate past its not-after date.

Wildcard usage at mariner-reporting was noted where present. A wildcard leaf broadens blast radius if its key is compromised, so although a wildcard is not itself a finding, it raises the priority of the hygiene rules for mariner-reporting — a near-expiry or under-strength wildcard is a rotation the review would rather see scheduled sooner than later.

Key strength for mariner-reporting is judged against the floor for its algorithm family. The review does not grade keys on a curve: a key below the floor is a rotation finding irrespective of the sensitivity of the workload, because under-strength material weakens the whole interconnect graph that mariner-reporting participates in.

Session resumption behaviour for mariner-reporting was characterised so that repeat captures could be compared fairly. Resumption can mask a renegotiated parameter, so the harness records full-handshake outcomes where it can; the authoritative capture for mariner-reporting is still the most recent row, and resumption never changes which row is current.

Audit retention for mariner-reporting's captures follows the standard schedule: every sweep is retained, and the review reads the latest. This matters when reconstructing a finding months later — the row that was current at review time is identifiable by its capture timestamp, and the reconstruction must use that row rather than whatever happens to be newest at reconstruction time.

Certificate pinning by clients of mariner-reporting was inventoried lightly, because pinning interacts badly with rotation: a pinned client can break when mariner-reporting legitimately rotates. The review's rotation findings therefore come with a reminder that any pin held against mariner-reporting's current leaf must be updated in lockstep with the re-issue.

Operationally, mariner-reporting has been stable, but stability is not conformance. The review separates 'has not failed yet' from 'meets policy today', and it is the latter that governs the finding. Where the captured evidence and the live configuration disagree, the captured evidence is taken as the ground truth.

Forward-looking, the review recorded whether mariner-reporting is on a path toward post-quantum-ready key exchange. This cycle treats PQC readiness as informational; it changes no disposition, but it is captured so that team-analytics can sequence the work against the rotation cadence the hygiene rules already impose.

Clock discipline was assumed but noted for mariner-reporting: certificate validity windows are only meaningful if the validating hosts agree on the time. The review reasons about not-after relative to a single fixed review date, which removes any ambiguity that wall-clock skew on individual probers might otherwise introduce into the near-expiry judgement.

The protocol floor matters for mariner-reporting because a single tolerated downgrade becomes a precedent. The review treats any negotiated version outside the allowed set as a finding in every environment, including development, so that a sandbox habit does not migrate into production by copy-paste.

Transport strictness headers on responses from mariner-reporting were observed where applicable. Strict-transport signalling reduces downgrade opportunity for browser clients but does not substitute for the server-side protocol floor; the review credits it as defence in depth and nothing more for a prod surface.

Subject-alternative-name coverage on mariner-reporting's leaf was checked against the hostnames https://reporting.prod.mariner.internal actually answers for. A name not covered by the served certificate would surface as a verification failure in the capture, so SAN gaps tend to show up indirectly through the recorded verification outcome rather than as a separate graded axis.

For mariner-reporting, issuer trust is a policy question settled against the maintained anchor set rather than the popularity of a commercial authority. The specific issuer and key parameters of mariner-reporting's certificate of record are carried in the inventory database; what matters to the review is whether that issuer sits inside the governed anchor set, since a leaf that validates today but chains outside the set is still a rotation candidate on governance grounds.

Cipher-suite selection at mariner-reporting was inspected for obviously deprecated constructions. While suite negotiation is not itself a graded axis in this review, a modern protocol version on https://reporting.prod.mariner.internal strongly constrains the suite space, which is part of why the version allow-list does so much of the work and why a downgrade is treated as consequential rather than cosmetic.

Partner-facing exposure was a specific consideration for mariner-reporting where federated third parties consume it. Federation raises the stakes of a mutual-TLS gap because the counterparty's assurance depends on it, which is why a production federation surface is held to the client-authentication expectation without sympathy for integration convenience.

Early-data exposure for mariner-reporting was considered where 0-RTT resumption is enabled. Replayable early data is an application-layer hazard rather than a transport-policy axis, so it does not move mariner-reporting's disposition, but it is flagged for team-analytics as a design note to weigh against the latency benefit on the prod surface.

The mariner-reporting interconnect was modelled as part of the broader dependency graph. A weakness here propagates to every caller that trusts this endpoint, which is why the review resists the temptation to treat compiles scheduled analytical extracts for finance as a low-stakes carve-out. The posture is assessed on its own merits and against the same bar as the busiest production path.

Certificate-transparency presence for mariner-reporting's leaf was checked as a tamper-evidence signal. CT inclusion does not by itself make a certificate compliant — it is neither a protocol version nor an issuer-trust decision — but its absence on a publicly reachable prod endpoint would be a flag worth a follow-up outside this review's transport remit.

Truststore management on the prod side of mariner-reporting matters for mutual TLS. Where the endpoint demands a client certificate, the set of client anchors it accepts is an operational concern for team-analytics; the review records only whether a client certificate was presented and validated, leaving truststore curation to the owning team's runbooks.

Mutual TLS expectations for mariner-reporting follow the environment. The production trust boundary requires a client certificate; a non-production surface is not penalised for the absence of one. Where mariner-reporting is expected to present a client certificate and the capture shows none, the gap is a protocol-level finding unless a waiver of the matching kind and scope is in force.

ALPN negotiation at mariner-reporting was noted to confirm the application protocol riding over the tunnel, but protocol-version policy is enforced at the TLS layer and does not bend to the application above it. A modern application protocol over a legacy transport is still a transport finding for mariner-reporting.

Finally, mariner-reporting was checked for consistency between its environment label and its exposure. A service labelled prod is assessed under the rules for that environment; the review does not reclassify a surface to soften a finding, and team-analytics retains the route to reclassification through inventory governance rather than through this review.

The harness recorded the mariner-reporting endpoint over successive sweeps; only the most recent capture per service is treated as authoritative, since earlier sweeps frequently predate a remediation or a re-issue. Reviewers are reminded that the captured negotiation outcomes, the chain-validation result, and the leaf fingerprint seen on the wire are held in the inventory database and must be read from there, not inferred from this narrative.

Revocation freshness was considered for mariner-reporting. The review notes whether the endpoint's stapled status was recent and whether the validating party had a live path to revocation information, but treats stapling hygiene as advisory this cycle; the governing chain question remains whether the presented chain validated to a trusted anchor at capture time.

Where mariner-reporting terminates TLS at a sidecar or a shared load balancer rather than in the application process, the review attributes the captured posture to the service as exposed on https://reporting.prod.mariner.internal. Termination topology is an implementation detail; the obligation to meet policy attaches to the exposed prod surface regardless of which component holds the key.

Encrypted-client-hello readiness for mariner-reporting was recorded as informational. ECH changes what an on-path observer can see about the handshake to https://reporting.prod.mariner.internal but does not alter any graded axis here; it neither relaxes the protocol floor nor changes how a client certificate or a chain is judged.

Ownership context: team-analytics maintains mariner-reporting and is the counterparty for any remediation. The review records owning teams so that rotation and re-issuance work lands with the group that can actually schedule a maintenance window on the prod surface, but ownership confers no relief from policy.

Cross-signing arrangements that touch mariner-reporting's issuer were enumerated to make sure the chain the review reasons about is the chain clients actually build. A leaf can validate via more than one path; the governed question for mariner-reporting is whether the issuer of record sits in the trust anchor set, independent of which cross-signed path a particular client happens to choose.

Renewal automation for mariner-reporting was reviewed at the level of 'does a pipeline exist', not 'did it run'. An ACME-style renewal loop lowers the operational cost of the rotation findings this review may raise, but the disposition is taken from the captured state of https://reporting.prod.mariner.internal, so a renewal that is configured but not yet effective does not pre-empt a near-expiry finding.

Certificate lifetime is the other half of hygiene. A leaf approaching its not-after boundary inside the rotation window is scheduled for replacement well ahead of the cliff, on the principle that a lapse on the prod surface is an availability incident as much as a security one. The window is uniform across services so that nothing in mariner-reporting's profile earns special treatment.

SNI and virtual-host disambiguation were verified for mariner-reporting so that the captured leaf is unambiguously the one https://reporting.prod.mariner.internal intends to serve. A mismatch between the requested name and the served certificate would itself be an integrity concern, which is one more reason the observed fingerprint is compared against the inventory of record rather than assumed.

The review explicitly separated configuration intent from observed behaviour for mariner-reporting. A configuration file may declare a strict posture, but if the captured evidence on https://reporting.prod.mariner.internal shows otherwise, the evidence governs the finding; conversely a permissive-looking configuration that nonetheless negotiated within policy is judged on what actually happened on the wire.

### svc-015 — mariner-legacy-soap

Cipher-suite selection at mariner-legacy-soap was inspected for obviously deprecated constructions. While suite negotiation is not itself a graded axis in this review, a modern protocol version on https://legacy-soap.prod.mariner.internal strongly constrains the suite space, which is part of why the version allow-list does so much of the work and why a downgrade is treated as consequential rather than cosmetic.

Exception status. mariner-legacy-soap (svc-015) carries no transport-security waiver of any kind in the register — no protocol exception, no mutual-TLS carve-out, and no chain exception. It is therefore assessed directly against the operative policy, with the captured evidence in the inventory database standing as the sole record of how the prod endpoint actually negotiated.

Partner-facing exposure was a specific consideration for mariner-legacy-soap where federated third parties consume it. Federation raises the stakes of a mutual-TLS gap because the counterparty's assurance depends on it, which is why a production federation surface is held to the client-authentication expectation without sympathy for integration convenience.

Early-data exposure for mariner-legacy-soap was considered where 0-RTT resumption is enabled. Replayable early data is an application-layer hazard rather than a transport-policy axis, so it does not move mariner-legacy-soap's disposition, but it is flagged for team-integrations as a design note to weigh against the latency benefit on the prod surface.

The mariner-legacy-soap interconnect was modelled as part of the broader dependency graph. A weakness here propagates to every caller that trusts this endpoint, which is why the review resists the temptation to treat wraps a remaining SOAP integration kept alive for one partner as a low-stakes carve-out. The posture is assessed on its own merits and against the same bar as the busiest production path.

Certificate-transparency presence for mariner-legacy-soap's leaf was checked as a tamper-evidence signal. CT inclusion does not by itself make a certificate compliant — it is neither a protocol version nor an issuer-trust decision — but its absence on a publicly reachable prod endpoint would be a flag worth a follow-up outside this review's transport remit.

Truststore management on the prod side of mariner-legacy-soap matters for mutual TLS. Where the endpoint demands a client certificate, the set of client anchors it accepts is an operational concern for team-integrations; the review records only whether a client certificate was presented and validated, leaving truststore curation to the owning team's runbooks.

Mutual TLS expectations for mariner-legacy-soap follow the environment. The production trust boundary requires a client certificate; a non-production surface is not penalised for the absence of one. Where mariner-legacy-soap is expected to present a client certificate and the capture shows none, the gap is a protocol-level finding unless a waiver of the matching kind and scope is in force.

ALPN negotiation at mariner-legacy-soap was noted to confirm the application protocol riding over the tunnel, but protocol-version policy is enforced at the TLS layer and does not bend to the application above it. A modern application protocol over a legacy transport is still a transport finding for mariner-legacy-soap.

Finally, mariner-legacy-soap was checked for consistency between its environment label and its exposure. A service labelled prod is assessed under the rules for that environment; the review does not reclassify a surface to soften a finding, and team-integrations retains the route to reclassification through inventory governance rather than through this review.

The harness recorded the mariner-legacy-soap endpoint over successive sweeps; only the most recent capture per service is treated as authoritative, since earlier sweeps frequently predate a remediation or a re-issue. Reviewers are reminded that the captured negotiation outcomes, the chain-validation result, and the leaf fingerprint seen on the wire are held in the inventory database and must be read from there, not inferred from this narrative.

Revocation freshness was considered for mariner-legacy-soap. The review notes whether the endpoint's stapled status was recent and whether the validating party had a live path to revocation information, but treats stapling hygiene as advisory this cycle; the governing chain question remains whether the presented chain validated to a trusted anchor at capture time.

Where mariner-legacy-soap terminates TLS at a sidecar or a shared load balancer rather than in the application process, the review attributes the captured posture to the service as exposed on https://legacy-soap.prod.mariner.internal. Termination topology is an implementation detail; the obligation to meet policy attaches to the exposed prod surface regardless of which component holds the key.

Encrypted-client-hello readiness for mariner-legacy-soap was recorded as informational. ECH changes what an on-path observer can see about the handshake to https://legacy-soap.prod.mariner.internal but does not alter any graded axis here; it neither relaxes the protocol floor nor changes how a client certificate or a chain is judged.

Ownership context: team-integrations maintains mariner-legacy-soap and is the counterparty for any remediation. The review records owning teams so that rotation and re-issuance work lands with the group that can actually schedule a maintenance window on the prod surface, but ownership confers no relief from policy.

Cross-signing arrangements that touch mariner-legacy-soap's issuer were enumerated to make sure the chain the review reasons about is the chain clients actually build. A leaf can validate via more than one path; the governed question for mariner-legacy-soap is whether the issuer of record sits in the trust anchor set, independent of which cross-signed path a particular client happens to choose.

Renewal automation for mariner-legacy-soap was reviewed at the level of 'does a pipeline exist', not 'did it run'. An ACME-style renewal loop lowers the operational cost of the rotation findings this review may raise, but the disposition is taken from the captured state of https://legacy-soap.prod.mariner.internal, so a renewal that is configured but not yet effective does not pre-empt a near-expiry finding.

Certificate lifetime is the other half of hygiene. A leaf approaching its not-after boundary inside the rotation window is scheduled for replacement well ahead of the cliff, on the principle that a lapse on the prod surface is an availability incident as much as a security one. The window is uniform across services so that nothing in mariner-legacy-soap's profile earns special treatment.

SNI and virtual-host disambiguation were verified for mariner-legacy-soap so that the captured leaf is unambiguously the one https://legacy-soap.prod.mariner.internal intends to serve. A mismatch between the requested name and the served certificate would itself be an integrity concern, which is one more reason the observed fingerprint is compared against the inventory of record rather than assumed.

The review explicitly separated configuration intent from observed behaviour for mariner-legacy-soap. A configuration file may declare a strict posture, but if the captured evidence on https://legacy-soap.prod.mariner.internal shows otherwise, the evidence governs the finding; conversely a permissive-looking configuration that nonetheless negotiated within policy is judged on what actually happened on the wire.

Within the review boundary, mariner-legacy-soap (svc-015) wraps a remaining SOAP integration kept alive for one partner. It is owned by team-integrations and presents on https://legacy-soap.prod.mariner.internal, which the inventory classifies as a prod surface. The transport posture of any prod endpoint is weighed against the operative policy rather than against historical convention, and the assessment proceeds from the evidence of record rather than from operator attestation.

Documentation for mariner-legacy-soap was cross-checked against the configuration set. Where a policy value is needed — the rotation window, the protocol allow-list, the key floors, or the issuer anchor set — it is read from the validated configuration rather than from this prose, which paraphrases policy for the reader's convenience only.

For mesh participants such as mariner-legacy-soap, certificate rotation is automated through the issuing control plane, which lowers the cost of a rotation finding but does not remove the obligation: an automated rotation that has not yet run still leaves a soon-to-expire leaf on https://legacy-soap.prod.mariner.internal, and the review grades the state at capture time, not the intention encoded in automation.

Revocation-list distribution touching mariner-legacy-soap's issuer was sanity-checked so that a client choosing CRL over stapled status still has a path. As with stapling, the review treats CRL reachability as advisory this cycle; the governing question for mariner-legacy-soap remains whether the presented chain validated at capture time.

Evidence handling for mariner-legacy-soap is deliberately conservative. When the fingerprint observed on the wire disagrees with the inventory of record, the review does not attempt to reconcile the two in the agent's favour; the disagreement is itself the finding, and it is escalated rather than waived, regardless of any paperwork that might otherwise have applied.

Key-ceremony provenance for mariner-legacy-soap's material was reviewed at a high level. Where team-integrations can attest that the private key was generated and held in a hardware security module, the operational risk of the key is lower, but provenance does not raise an under-strength key above the floor or extend a certificate past its not-after date.

Wildcard usage at mariner-legacy-soap was noted where present. A wildcard leaf broadens blast radius if its key is compromised, so although a wildcard is not itself a finding, it raises the priority of the hygiene rules for mariner-legacy-soap — a near-expiry or under-strength wildcard is a rotation the review would rather see scheduled sooner than later.

Key strength for mariner-legacy-soap is judged against the floor for its algorithm family. The review does not grade keys on a curve: a key below the floor is a rotation finding irrespective of the sensitivity of the workload, because under-strength material weakens the whole interconnect graph that mariner-legacy-soap participates in.

Session resumption behaviour for mariner-legacy-soap was characterised so that repeat captures could be compared fairly. Resumption can mask a renegotiated parameter, so the harness records full-handshake outcomes where it can; the authoritative capture for mariner-legacy-soap is still the most recent row, and resumption never changes which row is current.

Audit retention for mariner-legacy-soap's captures follows the standard schedule: every sweep is retained, and the review reads the latest. This matters when reconstructing a finding months later — the row that was current at review time is identifiable by its capture timestamp, and the reconstruction must use that row rather than whatever happens to be newest at reconstruction time.

Certificate pinning by clients of mariner-legacy-soap was inventoried lightly, because pinning interacts badly with rotation: a pinned client can break when mariner-legacy-soap legitimately rotates. The review's rotation findings therefore come with a reminder that any pin held against mariner-legacy-soap's current leaf must be updated in lockstep with the re-issue.

Operationally, mariner-legacy-soap has been stable, but stability is not conformance. The review separates 'has not failed yet' from 'meets policy today', and it is the latter that governs the finding. Where the captured evidence and the live configuration disagree, the captured evidence is taken as the ground truth.

Forward-looking, the review recorded whether mariner-legacy-soap is on a path toward post-quantum-ready key exchange. This cycle treats PQC readiness as informational; it changes no disposition, but it is captured so that team-integrations can sequence the work against the rotation cadence the hygiene rules already impose.

Clock discipline was assumed but noted for mariner-legacy-soap: certificate validity windows are only meaningful if the validating hosts agree on the time. The review reasons about not-after relative to a single fixed review date, which removes any ambiguity that wall-clock skew on individual probers might otherwise introduce into the near-expiry judgement.

The protocol floor matters for mariner-legacy-soap because a single tolerated downgrade becomes a precedent. The review treats any negotiated version outside the allowed set as a finding in every environment, including development, so that a sandbox habit does not migrate into production by copy-paste.

Transport strictness headers on responses from mariner-legacy-soap were observed where applicable. Strict-transport signalling reduces downgrade opportunity for browser clients but does not substitute for the server-side protocol floor; the review credits it as defence in depth and nothing more for a prod surface.

Subject-alternative-name coverage on mariner-legacy-soap's leaf was checked against the hostnames https://legacy-soap.prod.mariner.internal actually answers for. A name not covered by the served certificate would surface as a verification failure in the capture, so SAN gaps tend to show up indirectly through the recorded verification outcome rather than as a separate graded axis.

For mariner-legacy-soap, issuer trust is a policy question settled against the maintained anchor set rather than the popularity of a commercial authority. The specific issuer and key parameters of mariner-legacy-soap's certificate of record are carried in the inventory database; what matters to the review is whether that issuer sits inside the governed anchor set, since a leaf that validates today but chains outside the set is still a rotation candidate on governance grounds.

### svc-016 — mariner-iot-bridge

The review explicitly separated configuration intent from observed behaviour for mariner-iot-bridge. A configuration file may declare a strict posture, but if the captured evidence on https://iot-bridge.dev.mariner.internal shows otherwise, the evidence governs the finding; conversely a permissive-looking configuration that nonetheless negotiated within policy is judged on what actually happened on the wire.

Within the review boundary, mariner-iot-bridge (svc-016) relays device-originated telemetry from the field. It is owned by team-iot and presents on https://iot-bridge.dev.mariner.internal, which the inventory classifies as a dev surface. The transport posture of any dev endpoint is weighed against the operative policy rather than against historical convention, and the assessment proceeds from the evidence of record rather than from operator attestation.

Exception status. mariner-iot-bridge (svc-016) carries no transport-security waiver of any kind in the register — no protocol exception, no mutual-TLS carve-out, and no chain exception. It is therefore assessed directly against the operative policy, with the captured evidence in the inventory database standing as the sole record of how the dev endpoint actually negotiated.

Documentation for mariner-iot-bridge was cross-checked against the configuration set. Where a policy value is needed — the rotation window, the protocol allow-list, the key floors, or the issuer anchor set — it is read from the validated configuration rather than from this prose, which paraphrases policy for the reader's convenience only.

For mesh participants such as mariner-iot-bridge, certificate rotation is automated through the issuing control plane, which lowers the cost of a rotation finding but does not remove the obligation: an automated rotation that has not yet run still leaves a soon-to-expire leaf on https://iot-bridge.dev.mariner.internal, and the review grades the state at capture time, not the intention encoded in automation.

Revocation-list distribution touching mariner-iot-bridge's issuer was sanity-checked so that a client choosing CRL over stapled status still has a path. As with stapling, the review treats CRL reachability as advisory this cycle; the governing question for mariner-iot-bridge remains whether the presented chain validated at capture time.

Evidence handling for mariner-iot-bridge is deliberately conservative. When the fingerprint observed on the wire disagrees with the inventory of record, the review does not attempt to reconcile the two in the agent's favour; the disagreement is itself the finding, and it is escalated rather than waived, regardless of any paperwork that might otherwise have applied.

Key-ceremony provenance for mariner-iot-bridge's material was reviewed at a high level. Where team-iot can attest that the private key was generated and held in a hardware security module, the operational risk of the key is lower, but provenance does not raise an under-strength key above the floor or extend a certificate past its not-after date.

Wildcard usage at mariner-iot-bridge was noted where present. A wildcard leaf broadens blast radius if its key is compromised, so although a wildcard is not itself a finding, it raises the priority of the hygiene rules for mariner-iot-bridge — a near-expiry or under-strength wildcard is a rotation the review would rather see scheduled sooner than later.

Key strength for mariner-iot-bridge is judged against the floor for its algorithm family. The review does not grade keys on a curve: a key below the floor is a rotation finding irrespective of the sensitivity of the workload, because under-strength material weakens the whole interconnect graph that mariner-iot-bridge participates in.

Session resumption behaviour for mariner-iot-bridge was characterised so that repeat captures could be compared fairly. Resumption can mask a renegotiated parameter, so the harness records full-handshake outcomes where it can; the authoritative capture for mariner-iot-bridge is still the most recent row, and resumption never changes which row is current.

Audit retention for mariner-iot-bridge's captures follows the standard schedule: every sweep is retained, and the review reads the latest. This matters when reconstructing a finding months later — the row that was current at review time is identifiable by its capture timestamp, and the reconstruction must use that row rather than whatever happens to be newest at reconstruction time.

Certificate pinning by clients of mariner-iot-bridge was inventoried lightly, because pinning interacts badly with rotation: a pinned client can break when mariner-iot-bridge legitimately rotates. The review's rotation findings therefore come with a reminder that any pin held against mariner-iot-bridge's current leaf must be updated in lockstep with the re-issue.

Operationally, mariner-iot-bridge has been stable, but stability is not conformance. The review separates 'has not failed yet' from 'meets policy today', and it is the latter that governs the finding. Where the captured evidence and the live configuration disagree, the captured evidence is taken as the ground truth.

Forward-looking, the review recorded whether mariner-iot-bridge is on a path toward post-quantum-ready key exchange. This cycle treats PQC readiness as informational; it changes no disposition, but it is captured so that team-iot can sequence the work against the rotation cadence the hygiene rules already impose.

Clock discipline was assumed but noted for mariner-iot-bridge: certificate validity windows are only meaningful if the validating hosts agree on the time. The review reasons about not-after relative to a single fixed review date, which removes any ambiguity that wall-clock skew on individual probers might otherwise introduce into the near-expiry judgement.

The protocol floor matters for mariner-iot-bridge because a single tolerated downgrade becomes a precedent. The review treats any negotiated version outside the allowed set as a finding in every environment, including development, so that a sandbox habit does not migrate into production by copy-paste.

Transport strictness headers on responses from mariner-iot-bridge were observed where applicable. Strict-transport signalling reduces downgrade opportunity for browser clients but does not substitute for the server-side protocol floor; the review credits it as defence in depth and nothing more for a dev surface.

Subject-alternative-name coverage on mariner-iot-bridge's leaf was checked against the hostnames https://iot-bridge.dev.mariner.internal actually answers for. A name not covered by the served certificate would surface as a verification failure in the capture, so SAN gaps tend to show up indirectly through the recorded verification outcome rather than as a separate graded axis.

For mariner-iot-bridge, issuer trust is a policy question settled against the maintained anchor set rather than the popularity of a commercial authority. The specific issuer and key parameters of mariner-iot-bridge's certificate of record are carried in the inventory database; what matters to the review is whether that issuer sits inside the governed anchor set, since a leaf that validates today but chains outside the set is still a rotation candidate on governance grounds.

Cipher-suite selection at mariner-iot-bridge was inspected for obviously deprecated constructions. While suite negotiation is not itself a graded axis in this review, a modern protocol version on https://iot-bridge.dev.mariner.internal strongly constrains the suite space, which is part of why the version allow-list does so much of the work and why a downgrade is treated as consequential rather than cosmetic.

Partner-facing exposure was a specific consideration for mariner-iot-bridge where federated third parties consume it. Federation raises the stakes of a mutual-TLS gap because the counterparty's assurance depends on it, which is why a production federation surface is held to the client-authentication expectation without sympathy for integration convenience.

Early-data exposure for mariner-iot-bridge was considered where 0-RTT resumption is enabled. Replayable early data is an application-layer hazard rather than a transport-policy axis, so it does not move mariner-iot-bridge's disposition, but it is flagged for team-iot as a design note to weigh against the latency benefit on the dev surface.

The mariner-iot-bridge interconnect was modelled as part of the broader dependency graph. A weakness here propagates to every caller that trusts this endpoint, which is why the review resists the temptation to treat relays device-originated telemetry from the field as a low-stakes carve-out. The posture is assessed on its own merits and against the same bar as the busiest production path.

Certificate-transparency presence for mariner-iot-bridge's leaf was checked as a tamper-evidence signal. CT inclusion does not by itself make a certificate compliant — it is neither a protocol version nor an issuer-trust decision — but its absence on a publicly reachable dev endpoint would be a flag worth a follow-up outside this review's transport remit.

Truststore management on the dev side of mariner-iot-bridge matters for mutual TLS. Where the endpoint demands a client certificate, the set of client anchors it accepts is an operational concern for team-iot; the review records only whether a client certificate was presented and validated, leaving truststore curation to the owning team's runbooks.

Mutual TLS expectations for mariner-iot-bridge follow the environment. The production trust boundary requires a client certificate; a non-production surface is not penalised for the absence of one. Where mariner-iot-bridge is expected to present a client certificate and the capture shows none, the gap is a protocol-level finding unless a waiver of the matching kind and scope is in force.

ALPN negotiation at mariner-iot-bridge was noted to confirm the application protocol riding over the tunnel, but protocol-version policy is enforced at the TLS layer and does not bend to the application above it. A modern application protocol over a legacy transport is still a transport finding for mariner-iot-bridge.

Finally, mariner-iot-bridge was checked for consistency between its environment label and its exposure. A service labelled dev is assessed under the rules for that environment; the review does not reclassify a surface to soften a finding, and team-iot retains the route to reclassification through inventory governance rather than through this review.

The harness recorded the mariner-iot-bridge endpoint over successive sweeps; only the most recent capture per service is treated as authoritative, since earlier sweeps frequently predate a remediation or a re-issue. Reviewers are reminded that the captured negotiation outcomes, the chain-validation result, and the leaf fingerprint seen on the wire are held in the inventory database and must be read from there, not inferred from this narrative.

Revocation freshness was considered for mariner-iot-bridge. The review notes whether the endpoint's stapled status was recent and whether the validating party had a live path to revocation information, but treats stapling hygiene as advisory this cycle; the governing chain question remains whether the presented chain validated to a trusted anchor at capture time.

Where mariner-iot-bridge terminates TLS at a sidecar or a shared load balancer rather than in the application process, the review attributes the captured posture to the service as exposed on https://iot-bridge.dev.mariner.internal. Termination topology is an implementation detail; the obligation to meet policy attaches to the exposed dev surface regardless of which component holds the key.

Encrypted-client-hello readiness for mariner-iot-bridge was recorded as informational. ECH changes what an on-path observer can see about the handshake to https://iot-bridge.dev.mariner.internal but does not alter any graded axis here; it neither relaxes the protocol floor nor changes how a client certificate or a chain is judged.

Ownership context: team-iot maintains mariner-iot-bridge and is the counterparty for any remediation. The review records owning teams so that rotation and re-issuance work lands with the group that can actually schedule a maintenance window on the dev surface, but ownership confers no relief from policy.

Cross-signing arrangements that touch mariner-iot-bridge's issuer were enumerated to make sure the chain the review reasons about is the chain clients actually build. A leaf can validate via more than one path; the governed question for mariner-iot-bridge is whether the issuer of record sits in the trust anchor set, independent of which cross-signed path a particular client happens to choose.

Renewal automation for mariner-iot-bridge was reviewed at the level of 'does a pipeline exist', not 'did it run'. An ACME-style renewal loop lowers the operational cost of the rotation findings this review may raise, but the disposition is taken from the captured state of https://iot-bridge.dev.mariner.internal, so a renewal that is configured but not yet effective does not pre-empt a near-expiry finding.

Certificate lifetime is the other half of hygiene. A leaf approaching its not-after boundary inside the rotation window is scheduled for replacement well ahead of the cliff, on the principle that a lapse on the dev surface is an availability incident as much as a security one. The window is uniform across services so that nothing in mariner-iot-bridge's profile earns special treatment.

SNI and virtual-host disambiguation were verified for mariner-iot-bridge so that the captured leaf is unambiguously the one https://iot-bridge.dev.mariner.internal intends to serve. A mismatch between the requested name and the served certificate would itself be an integrity concern, which is one more reason the observed fingerprint is compared against the inventory of record rather than assumed.

### svc-017 — mariner-cdn-origin

For mariner-cdn-origin, issuer trust is a policy question settled against the maintained anchor set rather than the popularity of a commercial authority. The specific issuer and key parameters of mariner-cdn-origin's certificate of record are carried in the inventory database; what matters to the review is whether that issuer sits inside the governed anchor set, since a leaf that validates today but chains outside the set is still a rotation candidate on governance grounds.

Cipher-suite selection at mariner-cdn-origin was inspected for obviously deprecated constructions. While suite negotiation is not itself a graded axis in this review, a modern protocol version on https://cdn-origin.prod.mariner.internal strongly constrains the suite space, which is part of why the version allow-list does so much of the work and why a downgrade is treated as consequential rather than cosmetic.

Partner-facing exposure was a specific consideration for mariner-cdn-origin where federated third parties consume it. Federation raises the stakes of a mutual-TLS gap because the counterparty's assurance depends on it, which is why a production federation surface is held to the client-authentication expectation without sympathy for integration convenience.

Exception status. mariner-cdn-origin (svc-017) carries no transport-security waiver of any kind in the register — no protocol exception, no mutual-TLS carve-out, and no chain exception. It is therefore assessed directly against the operative policy, with the captured evidence in the inventory database standing as the sole record of how the prod endpoint actually negotiated.

Early-data exposure for mariner-cdn-origin was considered where 0-RTT resumption is enabled. Replayable early data is an application-layer hazard rather than a transport-policy axis, so it does not move mariner-cdn-origin's disposition, but it is flagged for team-edge as a design note to weigh against the latency benefit on the prod surface.

The mariner-cdn-origin interconnect was modelled as part of the broader dependency graph. A weakness here propagates to every caller that trusts this endpoint, which is why the review resists the temptation to treat is the shielded origin behind the content delivery tier as a low-stakes carve-out. The posture is assessed on its own merits and against the same bar as the busiest production path.

Certificate-transparency presence for mariner-cdn-origin's leaf was checked as a tamper-evidence signal. CT inclusion does not by itself make a certificate compliant — it is neither a protocol version nor an issuer-trust decision — but its absence on a publicly reachable prod endpoint would be a flag worth a follow-up outside this review's transport remit.

Truststore management on the prod side of mariner-cdn-origin matters for mutual TLS. Where the endpoint demands a client certificate, the set of client anchors it accepts is an operational concern for team-edge; the review records only whether a client certificate was presented and validated, leaving truststore curation to the owning team's runbooks.

Mutual TLS expectations for mariner-cdn-origin follow the environment. The production trust boundary requires a client certificate; a non-production surface is not penalised for the absence of one. Where mariner-cdn-origin is expected to present a client certificate and the capture shows none, the gap is a protocol-level finding unless a waiver of the matching kind and scope is in force.

ALPN negotiation at mariner-cdn-origin was noted to confirm the application protocol riding over the tunnel, but protocol-version policy is enforced at the TLS layer and does not bend to the application above it. A modern application protocol over a legacy transport is still a transport finding for mariner-cdn-origin.

Finally, mariner-cdn-origin was checked for consistency between its environment label and its exposure. A service labelled prod is assessed under the rules for that environment; the review does not reclassify a surface to soften a finding, and team-edge retains the route to reclassification through inventory governance rather than through this review.

The harness recorded the mariner-cdn-origin endpoint over successive sweeps; only the most recent capture per service is treated as authoritative, since earlier sweeps frequently predate a remediation or a re-issue. Reviewers are reminded that the captured negotiation outcomes, the chain-validation result, and the leaf fingerprint seen on the wire are held in the inventory database and must be read from there, not inferred from this narrative.

Revocation freshness was considered for mariner-cdn-origin. The review notes whether the endpoint's stapled status was recent and whether the validating party had a live path to revocation information, but treats stapling hygiene as advisory this cycle; the governing chain question remains whether the presented chain validated to a trusted anchor at capture time.

Where mariner-cdn-origin terminates TLS at a sidecar or a shared load balancer rather than in the application process, the review attributes the captured posture to the service as exposed on https://cdn-origin.prod.mariner.internal. Termination topology is an implementation detail; the obligation to meet policy attaches to the exposed prod surface regardless of which component holds the key.

Encrypted-client-hello readiness for mariner-cdn-origin was recorded as informational. ECH changes what an on-path observer can see about the handshake to https://cdn-origin.prod.mariner.internal but does not alter any graded axis here; it neither relaxes the protocol floor nor changes how a client certificate or a chain is judged.

Ownership context: team-edge maintains mariner-cdn-origin and is the counterparty for any remediation. The review records owning teams so that rotation and re-issuance work lands with the group that can actually schedule a maintenance window on the prod surface, but ownership confers no relief from policy.

Cross-signing arrangements that touch mariner-cdn-origin's issuer were enumerated to make sure the chain the review reasons about is the chain clients actually build. A leaf can validate via more than one path; the governed question for mariner-cdn-origin is whether the issuer of record sits in the trust anchor set, independent of which cross-signed path a particular client happens to choose.

Renewal automation for mariner-cdn-origin was reviewed at the level of 'does a pipeline exist', not 'did it run'. An ACME-style renewal loop lowers the operational cost of the rotation findings this review may raise, but the disposition is taken from the captured state of https://cdn-origin.prod.mariner.internal, so a renewal that is configured but not yet effective does not pre-empt a near-expiry finding.

Certificate lifetime is the other half of hygiene. A leaf approaching its not-after boundary inside the rotation window is scheduled for replacement well ahead of the cliff, on the principle that a lapse on the prod surface is an availability incident as much as a security one. The window is uniform across services so that nothing in mariner-cdn-origin's profile earns special treatment.

SNI and virtual-host disambiguation were verified for mariner-cdn-origin so that the captured leaf is unambiguously the one https://cdn-origin.prod.mariner.internal intends to serve. A mismatch between the requested name and the served certificate would itself be an integrity concern, which is one more reason the observed fingerprint is compared against the inventory of record rather than assumed.

The review explicitly separated configuration intent from observed behaviour for mariner-cdn-origin. A configuration file may declare a strict posture, but if the captured evidence on https://cdn-origin.prod.mariner.internal shows otherwise, the evidence governs the finding; conversely a permissive-looking configuration that nonetheless negotiated within policy is judged on what actually happened on the wire.

Within the review boundary, mariner-cdn-origin (svc-017) is the shielded origin behind the content delivery tier. It is owned by team-edge and presents on https://cdn-origin.prod.mariner.internal, which the inventory classifies as a prod surface. The transport posture of any prod endpoint is weighed against the operative policy rather than against historical convention, and the assessment proceeds from the evidence of record rather than from operator attestation.

Documentation for mariner-cdn-origin was cross-checked against the configuration set. Where a policy value is needed — the rotation window, the protocol allow-list, the key floors, or the issuer anchor set — it is read from the validated configuration rather than from this prose, which paraphrases policy for the reader's convenience only.

For mesh participants such as mariner-cdn-origin, certificate rotation is automated through the issuing control plane, which lowers the cost of a rotation finding but does not remove the obligation: an automated rotation that has not yet run still leaves a soon-to-expire leaf on https://cdn-origin.prod.mariner.internal, and the review grades the state at capture time, not the intention encoded in automation.

Revocation-list distribution touching mariner-cdn-origin's issuer was sanity-checked so that a client choosing CRL over stapled status still has a path. As with stapling, the review treats CRL reachability as advisory this cycle; the governing question for mariner-cdn-origin remains whether the presented chain validated at capture time.

Evidence handling for mariner-cdn-origin is deliberately conservative. When the fingerprint observed on the wire disagrees with the inventory of record, the review does not attempt to reconcile the two in the agent's favour; the disagreement is itself the finding, and it is escalated rather than waived, regardless of any paperwork that might otherwise have applied.

Key-ceremony provenance for mariner-cdn-origin's material was reviewed at a high level. Where team-edge can attest that the private key was generated and held in a hardware security module, the operational risk of the key is lower, but provenance does not raise an under-strength key above the floor or extend a certificate past its not-after date.

Wildcard usage at mariner-cdn-origin was noted where present. A wildcard leaf broadens blast radius if its key is compromised, so although a wildcard is not itself a finding, it raises the priority of the hygiene rules for mariner-cdn-origin — a near-expiry or under-strength wildcard is a rotation the review would rather see scheduled sooner than later.

Key strength for mariner-cdn-origin is judged against the floor for its algorithm family. The review does not grade keys on a curve: a key below the floor is a rotation finding irrespective of the sensitivity of the workload, because under-strength material weakens the whole interconnect graph that mariner-cdn-origin participates in.

Session resumption behaviour for mariner-cdn-origin was characterised so that repeat captures could be compared fairly. Resumption can mask a renegotiated parameter, so the harness records full-handshake outcomes where it can; the authoritative capture for mariner-cdn-origin is still the most recent row, and resumption never changes which row is current.

Audit retention for mariner-cdn-origin's captures follows the standard schedule: every sweep is retained, and the review reads the latest. This matters when reconstructing a finding months later — the row that was current at review time is identifiable by its capture timestamp, and the reconstruction must use that row rather than whatever happens to be newest at reconstruction time.

Certificate pinning by clients of mariner-cdn-origin was inventoried lightly, because pinning interacts badly with rotation: a pinned client can break when mariner-cdn-origin legitimately rotates. The review's rotation findings therefore come with a reminder that any pin held against mariner-cdn-origin's current leaf must be updated in lockstep with the re-issue.

Operationally, mariner-cdn-origin has been stable, but stability is not conformance. The review separates 'has not failed yet' from 'meets policy today', and it is the latter that governs the finding. Where the captured evidence and the live configuration disagree, the captured evidence is taken as the ground truth.

Forward-looking, the review recorded whether mariner-cdn-origin is on a path toward post-quantum-ready key exchange. This cycle treats PQC readiness as informational; it changes no disposition, but it is captured so that team-edge can sequence the work against the rotation cadence the hygiene rules already impose.

Clock discipline was assumed but noted for mariner-cdn-origin: certificate validity windows are only meaningful if the validating hosts agree on the time. The review reasons about not-after relative to a single fixed review date, which removes any ambiguity that wall-clock skew on individual probers might otherwise introduce into the near-expiry judgement.

The protocol floor matters for mariner-cdn-origin because a single tolerated downgrade becomes a precedent. The review treats any negotiated version outside the allowed set as a finding in every environment, including development, so that a sandbox habit does not migrate into production by copy-paste.

Transport strictness headers on responses from mariner-cdn-origin were observed where applicable. Strict-transport signalling reduces downgrade opportunity for browser clients but does not substitute for the server-side protocol floor; the review credits it as defence in depth and nothing more for a prod surface.

Subject-alternative-name coverage on mariner-cdn-origin's leaf was checked against the hostnames https://cdn-origin.prod.mariner.internal actually answers for. A name not covered by the served certificate would surface as a verification failure in the capture, so SAN gaps tend to show up indirectly through the recorded verification outcome rather than as a separate graded axis.

### svc-018 — mariner-docs-site

SNI and virtual-host disambiguation were verified for mariner-docs-site so that the captured leaf is unambiguously the one https://docs-site.staging.mariner.internal intends to serve. A mismatch between the requested name and the served certificate would itself be an integrity concern, which is one more reason the observed fingerprint is compared against the inventory of record rather than assumed.

Exception status. mariner-docs-site (svc-018) carries no transport-security waiver of any kind in the register — no protocol exception, no mutual-TLS carve-out, and no chain exception. It is therefore assessed directly against the operative policy, with the captured evidence in the inventory database standing as the sole record of how the staging endpoint actually negotiated.

The review explicitly separated configuration intent from observed behaviour for mariner-docs-site. A configuration file may declare a strict posture, but if the captured evidence on https://docs-site.staging.mariner.internal shows otherwise, the evidence governs the finding; conversely a permissive-looking configuration that nonetheless negotiated within policy is judged on what actually happened on the wire.

Within the review boundary, mariner-docs-site (svc-018) publishes versioned product documentation. It is owned by team-docs and presents on https://docs-site.staging.mariner.internal, which the inventory classifies as a staging surface. The transport posture of any staging endpoint is weighed against the operative policy rather than against historical convention, and the assessment proceeds from the evidence of record rather than from operator attestation.

Documentation for mariner-docs-site was cross-checked against the configuration set. Where a policy value is needed — the rotation window, the protocol allow-list, the key floors, or the issuer anchor set — it is read from the validated configuration rather than from this prose, which paraphrases policy for the reader's convenience only.

For mesh participants such as mariner-docs-site, certificate rotation is automated through the issuing control plane, which lowers the cost of a rotation finding but does not remove the obligation: an automated rotation that has not yet run still leaves a soon-to-expire leaf on https://docs-site.staging.mariner.internal, and the review grades the state at capture time, not the intention encoded in automation.

Revocation-list distribution touching mariner-docs-site's issuer was sanity-checked so that a client choosing CRL over stapled status still has a path. As with stapling, the review treats CRL reachability as advisory this cycle; the governing question for mariner-docs-site remains whether the presented chain validated at capture time.

Evidence handling for mariner-docs-site is deliberately conservative. When the fingerprint observed on the wire disagrees with the inventory of record, the review does not attempt to reconcile the two in the agent's favour; the disagreement is itself the finding, and it is escalated rather than waived, regardless of any paperwork that might otherwise have applied.

Key-ceremony provenance for mariner-docs-site's material was reviewed at a high level. Where team-docs can attest that the private key was generated and held in a hardware security module, the operational risk of the key is lower, but provenance does not raise an under-strength key above the floor or extend a certificate past its not-after date.

Wildcard usage at mariner-docs-site was noted where present. A wildcard leaf broadens blast radius if its key is compromised, so although a wildcard is not itself a finding, it raises the priority of the hygiene rules for mariner-docs-site — a near-expiry or under-strength wildcard is a rotation the review would rather see scheduled sooner than later.

Key strength for mariner-docs-site is judged against the floor for its algorithm family. The review does not grade keys on a curve: a key below the floor is a rotation finding irrespective of the sensitivity of the workload, because under-strength material weakens the whole interconnect graph that mariner-docs-site participates in.

Session resumption behaviour for mariner-docs-site was characterised so that repeat captures could be compared fairly. Resumption can mask a renegotiated parameter, so the harness records full-handshake outcomes where it can; the authoritative capture for mariner-docs-site is still the most recent row, and resumption never changes which row is current.

Audit retention for mariner-docs-site's captures follows the standard schedule: every sweep is retained, and the review reads the latest. This matters when reconstructing a finding months later — the row that was current at review time is identifiable by its capture timestamp, and the reconstruction must use that row rather than whatever happens to be newest at reconstruction time.

Certificate pinning by clients of mariner-docs-site was inventoried lightly, because pinning interacts badly with rotation: a pinned client can break when mariner-docs-site legitimately rotates. The review's rotation findings therefore come with a reminder that any pin held against mariner-docs-site's current leaf must be updated in lockstep with the re-issue.

Operationally, mariner-docs-site has been stable, but stability is not conformance. The review separates 'has not failed yet' from 'meets policy today', and it is the latter that governs the finding. Where the captured evidence and the live configuration disagree, the captured evidence is taken as the ground truth.

Forward-looking, the review recorded whether mariner-docs-site is on a path toward post-quantum-ready key exchange. This cycle treats PQC readiness as informational; it changes no disposition, but it is captured so that team-docs can sequence the work against the rotation cadence the hygiene rules already impose.

Clock discipline was assumed but noted for mariner-docs-site: certificate validity windows are only meaningful if the validating hosts agree on the time. The review reasons about not-after relative to a single fixed review date, which removes any ambiguity that wall-clock skew on individual probers might otherwise introduce into the near-expiry judgement.

The protocol floor matters for mariner-docs-site because a single tolerated downgrade becomes a precedent. The review treats any negotiated version outside the allowed set as a finding in every environment, including development, so that a sandbox habit does not migrate into production by copy-paste.

Transport strictness headers on responses from mariner-docs-site were observed where applicable. Strict-transport signalling reduces downgrade opportunity for browser clients but does not substitute for the server-side protocol floor; the review credits it as defence in depth and nothing more for a staging surface.

Subject-alternative-name coverage on mariner-docs-site's leaf was checked against the hostnames https://docs-site.staging.mariner.internal actually answers for. A name not covered by the served certificate would surface as a verification failure in the capture, so SAN gaps tend to show up indirectly through the recorded verification outcome rather than as a separate graded axis.

For mariner-docs-site, issuer trust is a policy question settled against the maintained anchor set rather than the popularity of a commercial authority. The specific issuer and key parameters of mariner-docs-site's certificate of record are carried in the inventory database; what matters to the review is whether that issuer sits inside the governed anchor set, since a leaf that validates today but chains outside the set is still a rotation candidate on governance grounds.

Cipher-suite selection at mariner-docs-site was inspected for obviously deprecated constructions. While suite negotiation is not itself a graded axis in this review, a modern protocol version on https://docs-site.staging.mariner.internal strongly constrains the suite space, which is part of why the version allow-list does so much of the work and why a downgrade is treated as consequential rather than cosmetic.

Partner-facing exposure was a specific consideration for mariner-docs-site where federated third parties consume it. Federation raises the stakes of a mutual-TLS gap because the counterparty's assurance depends on it, which is why a production federation surface is held to the client-authentication expectation without sympathy for integration convenience.

Early-data exposure for mariner-docs-site was considered where 0-RTT resumption is enabled. Replayable early data is an application-layer hazard rather than a transport-policy axis, so it does not move mariner-docs-site's disposition, but it is flagged for team-docs as a design note to weigh against the latency benefit on the staging surface.

The mariner-docs-site interconnect was modelled as part of the broader dependency graph. A weakness here propagates to every caller that trusts this endpoint, which is why the review resists the temptation to treat publishes versioned product documentation as a low-stakes carve-out. The posture is assessed on its own merits and against the same bar as the busiest production path.

Certificate-transparency presence for mariner-docs-site's leaf was checked as a tamper-evidence signal. CT inclusion does not by itself make a certificate compliant — it is neither a protocol version nor an issuer-trust decision — but its absence on a publicly reachable staging endpoint would be a flag worth a follow-up outside this review's transport remit.

Truststore management on the staging side of mariner-docs-site matters for mutual TLS. Where the endpoint demands a client certificate, the set of client anchors it accepts is an operational concern for team-docs; the review records only whether a client certificate was presented and validated, leaving truststore curation to the owning team's runbooks.

Mutual TLS expectations for mariner-docs-site follow the environment. The production trust boundary requires a client certificate; a non-production surface is not penalised for the absence of one. Where mariner-docs-site is expected to present a client certificate and the capture shows none, the gap is a protocol-level finding unless a waiver of the matching kind and scope is in force.

ALPN negotiation at mariner-docs-site was noted to confirm the application protocol riding over the tunnel, but protocol-version policy is enforced at the TLS layer and does not bend to the application above it. A modern application protocol over a legacy transport is still a transport finding for mariner-docs-site.

Finally, mariner-docs-site was checked for consistency between its environment label and its exposure. A service labelled staging is assessed under the rules for that environment; the review does not reclassify a surface to soften a finding, and team-docs retains the route to reclassification through inventory governance rather than through this review.

The harness recorded the mariner-docs-site endpoint over successive sweeps; only the most recent capture per service is treated as authoritative, since earlier sweeps frequently predate a remediation or a re-issue. Reviewers are reminded that the captured negotiation outcomes, the chain-validation result, and the leaf fingerprint seen on the wire are held in the inventory database and must be read from there, not inferred from this narrative.

Revocation freshness was considered for mariner-docs-site. The review notes whether the endpoint's stapled status was recent and whether the validating party had a live path to revocation information, but treats stapling hygiene as advisory this cycle; the governing chain question remains whether the presented chain validated to a trusted anchor at capture time.

Where mariner-docs-site terminates TLS at a sidecar or a shared load balancer rather than in the application process, the review attributes the captured posture to the service as exposed on https://docs-site.staging.mariner.internal. Termination topology is an implementation detail; the obligation to meet policy attaches to the exposed staging surface regardless of which component holds the key.

Encrypted-client-hello readiness for mariner-docs-site was recorded as informational. ECH changes what an on-path observer can see about the handshake to https://docs-site.staging.mariner.internal but does not alter any graded axis here; it neither relaxes the protocol floor nor changes how a client certificate or a chain is judged.

Ownership context: team-docs maintains mariner-docs-site and is the counterparty for any remediation. The review records owning teams so that rotation and re-issuance work lands with the group that can actually schedule a maintenance window on the staging surface, but ownership confers no relief from policy.

Cross-signing arrangements that touch mariner-docs-site's issuer were enumerated to make sure the chain the review reasons about is the chain clients actually build. A leaf can validate via more than one path; the governed question for mariner-docs-site is whether the issuer of record sits in the trust anchor set, independent of which cross-signed path a particular client happens to choose.

Renewal automation for mariner-docs-site was reviewed at the level of 'does a pipeline exist', not 'did it run'. An ACME-style renewal loop lowers the operational cost of the rotation findings this review may raise, but the disposition is taken from the captured state of https://docs-site.staging.mariner.internal, so a renewal that is configured but not yet effective does not pre-empt a near-expiry finding.

Certificate lifetime is the other half of hygiene. A leaf approaching its not-after boundary inside the rotation window is scheduled for replacement well ahead of the cliff, on the principle that a lapse on the staging surface is an availability incident as much as a security one. The window is uniform across services so that nothing in mariner-docs-site's profile earns special treatment.

### svc-019 — mariner-grpc-mesh

Subject-alternative-name coverage on mariner-grpc-mesh's leaf was checked against the hostnames https://grpc-mesh.prod.mariner.internal actually answers for. A name not covered by the served certificate would surface as a verification failure in the capture, so SAN gaps tend to show up indirectly through the recorded verification outcome rather than as a separate graded axis.

For mariner-grpc-mesh, issuer trust is a policy question settled against the maintained anchor set rather than the popularity of a commercial authority. The specific issuer and key parameters of mariner-grpc-mesh's certificate of record are carried in the inventory database; what matters to the review is whether that issuer sits inside the governed anchor set, since a leaf that validates today but chains outside the set is still a rotation candidate on governance grounds.

Exception status. mariner-grpc-mesh (svc-019) holds waiver WV-2026-019, a transport-protocol exception scoped to the service's entire footprint across every environment. The register shows it granted on 2026-03-01 with a nominal expiry of 2026-07-10. The register carries WV-2026-019 as granted and in force as written; whether it still provides cover at review time is a separate question, settled by reading the policy review date against the recorded expiry, and by checking that the scope actually reaches the prod surface under assessment.

Cipher-suite selection at mariner-grpc-mesh was inspected for obviously deprecated constructions. While suite negotiation is not itself a graded axis in this review, a modern protocol version on https://grpc-mesh.prod.mariner.internal strongly constrains the suite space, which is part of why the version allow-list does so much of the work and why a downgrade is treated as consequential rather than cosmetic.

Partner-facing exposure was a specific consideration for mariner-grpc-mesh where federated third parties consume it. Federation raises the stakes of a mutual-TLS gap because the counterparty's assurance depends on it, which is why a production federation surface is held to the client-authentication expectation without sympathy for integration convenience.

Early-data exposure for mariner-grpc-mesh was considered where 0-RTT resumption is enabled. Replayable early data is an application-layer hazard rather than a transport-policy axis, so it does not move mariner-grpc-mesh's disposition, but it is flagged for team-platform as a design note to weigh against the latency benefit on the prod surface.

The mariner-grpc-mesh interconnect was modelled as part of the broader dependency graph. A weakness here propagates to every caller that trusts this endpoint, which is why the review resists the temptation to treat carries internal service-to-service RPC over the mesh as a low-stakes carve-out. The posture is assessed on its own merits and against the same bar as the busiest production path.

Certificate-transparency presence for mariner-grpc-mesh's leaf was checked as a tamper-evidence signal. CT inclusion does not by itself make a certificate compliant — it is neither a protocol version nor an issuer-trust decision — but its absence on a publicly reachable prod endpoint would be a flag worth a follow-up outside this review's transport remit.

Truststore management on the prod side of mariner-grpc-mesh matters for mutual TLS. Where the endpoint demands a client certificate, the set of client anchors it accepts is an operational concern for team-platform; the review records only whether a client certificate was presented and validated, leaving truststore curation to the owning team's runbooks.

Mutual TLS expectations for mariner-grpc-mesh follow the environment. The production trust boundary requires a client certificate; a non-production surface is not penalised for the absence of one. Where mariner-grpc-mesh is expected to present a client certificate and the capture shows none, the gap is a protocol-level finding unless a waiver of the matching kind and scope is in force.

ALPN negotiation at mariner-grpc-mesh was noted to confirm the application protocol riding over the tunnel, but protocol-version policy is enforced at the TLS layer and does not bend to the application above it. A modern application protocol over a legacy transport is still a transport finding for mariner-grpc-mesh.

Finally, mariner-grpc-mesh was checked for consistency between its environment label and its exposure. A service labelled prod is assessed under the rules for that environment; the review does not reclassify a surface to soften a finding, and team-platform retains the route to reclassification through inventory governance rather than through this review.

The harness recorded the mariner-grpc-mesh endpoint over successive sweeps; only the most recent capture per service is treated as authoritative, since earlier sweeps frequently predate a remediation or a re-issue. Reviewers are reminded that the captured negotiation outcomes, the chain-validation result, and the leaf fingerprint seen on the wire are held in the inventory database and must be read from there, not inferred from this narrative.

Revocation freshness was considered for mariner-grpc-mesh. The review notes whether the endpoint's stapled status was recent and whether the validating party had a live path to revocation information, but treats stapling hygiene as advisory this cycle; the governing chain question remains whether the presented chain validated to a trusted anchor at capture time.

Where mariner-grpc-mesh terminates TLS at a sidecar or a shared load balancer rather than in the application process, the review attributes the captured posture to the service as exposed on https://grpc-mesh.prod.mariner.internal. Termination topology is an implementation detail; the obligation to meet policy attaches to the exposed prod surface regardless of which component holds the key.

Encrypted-client-hello readiness for mariner-grpc-mesh was recorded as informational. ECH changes what an on-path observer can see about the handshake to https://grpc-mesh.prod.mariner.internal but does not alter any graded axis here; it neither relaxes the protocol floor nor changes how a client certificate or a chain is judged.

Ownership context: team-platform maintains mariner-grpc-mesh and is the counterparty for any remediation. The review records owning teams so that rotation and re-issuance work lands with the group that can actually schedule a maintenance window on the prod surface, but ownership confers no relief from policy.

Cross-signing arrangements that touch mariner-grpc-mesh's issuer were enumerated to make sure the chain the review reasons about is the chain clients actually build. A leaf can validate via more than one path; the governed question for mariner-grpc-mesh is whether the issuer of record sits in the trust anchor set, independent of which cross-signed path a particular client happens to choose.

Renewal automation for mariner-grpc-mesh was reviewed at the level of 'does a pipeline exist', not 'did it run'. An ACME-style renewal loop lowers the operational cost of the rotation findings this review may raise, but the disposition is taken from the captured state of https://grpc-mesh.prod.mariner.internal, so a renewal that is configured but not yet effective does not pre-empt a near-expiry finding.

Certificate lifetime is the other half of hygiene. A leaf approaching its not-after boundary inside the rotation window is scheduled for replacement well ahead of the cliff, on the principle that a lapse on the prod surface is an availability incident as much as a security one. The window is uniform across services so that nothing in mariner-grpc-mesh's profile earns special treatment.

SNI and virtual-host disambiguation were verified for mariner-grpc-mesh so that the captured leaf is unambiguously the one https://grpc-mesh.prod.mariner.internal intends to serve. A mismatch between the requested name and the served certificate would itself be an integrity concern, which is one more reason the observed fingerprint is compared against the inventory of record rather than assumed.

The review explicitly separated configuration intent from observed behaviour for mariner-grpc-mesh. A configuration file may declare a strict posture, but if the captured evidence on https://grpc-mesh.prod.mariner.internal shows otherwise, the evidence governs the finding; conversely a permissive-looking configuration that nonetheless negotiated within policy is judged on what actually happened on the wire.

Within the review boundary, mariner-grpc-mesh (svc-019) carries internal service-to-service RPC over the mesh. It is owned by team-platform and presents on https://grpc-mesh.prod.mariner.internal, which the inventory classifies as a prod surface. The transport posture of any prod endpoint is weighed against the operative policy rather than against historical convention, and the assessment proceeds from the evidence of record rather than from operator attestation.

Documentation for mariner-grpc-mesh was cross-checked against the configuration set. Where a policy value is needed — the rotation window, the protocol allow-list, the key floors, or the issuer anchor set — it is read from the validated configuration rather than from this prose, which paraphrases policy for the reader's convenience only.

For mesh participants such as mariner-grpc-mesh, certificate rotation is automated through the issuing control plane, which lowers the cost of a rotation finding but does not remove the obligation: an automated rotation that has not yet run still leaves a soon-to-expire leaf on https://grpc-mesh.prod.mariner.internal, and the review grades the state at capture time, not the intention encoded in automation.

Revocation-list distribution touching mariner-grpc-mesh's issuer was sanity-checked so that a client choosing CRL over stapled status still has a path. As with stapling, the review treats CRL reachability as advisory this cycle; the governing question for mariner-grpc-mesh remains whether the presented chain validated at capture time.

Evidence handling for mariner-grpc-mesh is deliberately conservative. When the fingerprint observed on the wire disagrees with the inventory of record, the review does not attempt to reconcile the two in the agent's favour; the disagreement is itself the finding, and it is escalated rather than waived, regardless of any paperwork that might otherwise have applied.

Key-ceremony provenance for mariner-grpc-mesh's material was reviewed at a high level. Where team-platform can attest that the private key was generated and held in a hardware security module, the operational risk of the key is lower, but provenance does not raise an under-strength key above the floor or extend a certificate past its not-after date.

Wildcard usage at mariner-grpc-mesh was noted where present. A wildcard leaf broadens blast radius if its key is compromised, so although a wildcard is not itself a finding, it raises the priority of the hygiene rules for mariner-grpc-mesh — a near-expiry or under-strength wildcard is a rotation the review would rather see scheduled sooner than later.

Key strength for mariner-grpc-mesh is judged against the floor for its algorithm family. The review does not grade keys on a curve: a key below the floor is a rotation finding irrespective of the sensitivity of the workload, because under-strength material weakens the whole interconnect graph that mariner-grpc-mesh participates in.

Session resumption behaviour for mariner-grpc-mesh was characterised so that repeat captures could be compared fairly. Resumption can mask a renegotiated parameter, so the harness records full-handshake outcomes where it can; the authoritative capture for mariner-grpc-mesh is still the most recent row, and resumption never changes which row is current.

Audit retention for mariner-grpc-mesh's captures follows the standard schedule: every sweep is retained, and the review reads the latest. This matters when reconstructing a finding months later — the row that was current at review time is identifiable by its capture timestamp, and the reconstruction must use that row rather than whatever happens to be newest at reconstruction time.

Certificate pinning by clients of mariner-grpc-mesh was inventoried lightly, because pinning interacts badly with rotation: a pinned client can break when mariner-grpc-mesh legitimately rotates. The review's rotation findings therefore come with a reminder that any pin held against mariner-grpc-mesh's current leaf must be updated in lockstep with the re-issue.

Operationally, mariner-grpc-mesh has been stable, but stability is not conformance. The review separates 'has not failed yet' from 'meets policy today', and it is the latter that governs the finding. Where the captured evidence and the live configuration disagree, the captured evidence is taken as the ground truth.

Forward-looking, the review recorded whether mariner-grpc-mesh is on a path toward post-quantum-ready key exchange. This cycle treats PQC readiness as informational; it changes no disposition, but it is captured so that team-platform can sequence the work against the rotation cadence the hygiene rules already impose.

Clock discipline was assumed but noted for mariner-grpc-mesh: certificate validity windows are only meaningful if the validating hosts agree on the time. The review reasons about not-after relative to a single fixed review date, which removes any ambiguity that wall-clock skew on individual probers might otherwise introduce into the near-expiry judgement.

The protocol floor matters for mariner-grpc-mesh because a single tolerated downgrade becomes a precedent. The review treats any negotiated version outside the allowed set as a finding in every environment, including development, so that a sandbox habit does not migrate into production by copy-paste.

Transport strictness headers on responses from mariner-grpc-mesh were observed where applicable. Strict-transport signalling reduces downgrade opportunity for browser clients but does not substitute for the server-side protocol floor; the review credits it as defence in depth and nothing more for a prod surface.

### svc-020 — mariner-webhook-relay

Certificate lifetime is the other half of hygiene. A leaf approaching its not-after boundary inside the rotation window is scheduled for replacement well ahead of the cliff, on the principle that a lapse on the prod surface is an availability incident as much as a security one. The window is uniform across services so that nothing in mariner-webhook-relay's profile earns special treatment.

SNI and virtual-host disambiguation were verified for mariner-webhook-relay so that the captured leaf is unambiguously the one https://webhook-relay.prod.mariner.internal intends to serve. A mismatch between the requested name and the served certificate would itself be an integrity concern, which is one more reason the observed fingerprint is compared against the inventory of record rather than assumed.

The review explicitly separated configuration intent from observed behaviour for mariner-webhook-relay. A configuration file may declare a strict posture, but if the captured evidence on https://webhook-relay.prod.mariner.internal shows otherwise, the evidence governs the finding; conversely a permissive-looking configuration that nonetheless negotiated within policy is judged on what actually happened on the wire.

Exception status. mariner-webhook-relay (svc-020) holds waiver WV-2026-020, a mutual-TLS exception scoped to the production listener only. The register shows it granted on 2026-03-10 with a nominal expiry of 2026-07-05. The register carries WV-2026-020 as granted and in force as written; whether it still provides cover at review time is a separate question, settled by reading the policy review date against the recorded expiry, and by checking that the scope actually reaches the prod surface under assessment.

Within the review boundary, mariner-webhook-relay (svc-020) fans outbound event callbacks to subscriber endpoints. It is owned by team-integrations and presents on https://webhook-relay.prod.mariner.internal, which the inventory classifies as a prod surface. The transport posture of any prod endpoint is weighed against the operative policy rather than against historical convention, and the assessment proceeds from the evidence of record rather than from operator attestation.

Documentation for mariner-webhook-relay was cross-checked against the configuration set. Where a policy value is needed — the rotation window, the protocol allow-list, the key floors, or the issuer anchor set — it is read from the validated configuration rather than from this prose, which paraphrases policy for the reader's convenience only.

For mesh participants such as mariner-webhook-relay, certificate rotation is automated through the issuing control plane, which lowers the cost of a rotation finding but does not remove the obligation: an automated rotation that has not yet run still leaves a soon-to-expire leaf on https://webhook-relay.prod.mariner.internal, and the review grades the state at capture time, not the intention encoded in automation.

Revocation-list distribution touching mariner-webhook-relay's issuer was sanity-checked so that a client choosing CRL over stapled status still has a path. As with stapling, the review treats CRL reachability as advisory this cycle; the governing question for mariner-webhook-relay remains whether the presented chain validated at capture time.

Evidence handling for mariner-webhook-relay is deliberately conservative. When the fingerprint observed on the wire disagrees with the inventory of record, the review does not attempt to reconcile the two in the agent's favour; the disagreement is itself the finding, and it is escalated rather than waived, regardless of any paperwork that might otherwise have applied.

Key-ceremony provenance for mariner-webhook-relay's material was reviewed at a high level. Where team-integrations can attest that the private key was generated and held in a hardware security module, the operational risk of the key is lower, but provenance does not raise an under-strength key above the floor or extend a certificate past its not-after date.

Wildcard usage at mariner-webhook-relay was noted where present. A wildcard leaf broadens blast radius if its key is compromised, so although a wildcard is not itself a finding, it raises the priority of the hygiene rules for mariner-webhook-relay — a near-expiry or under-strength wildcard is a rotation the review would rather see scheduled sooner than later.

Key strength for mariner-webhook-relay is judged against the floor for its algorithm family. The review does not grade keys on a curve: a key below the floor is a rotation finding irrespective of the sensitivity of the workload, because under-strength material weakens the whole interconnect graph that mariner-webhook-relay participates in.

Session resumption behaviour for mariner-webhook-relay was characterised so that repeat captures could be compared fairly. Resumption can mask a renegotiated parameter, so the harness records full-handshake outcomes where it can; the authoritative capture for mariner-webhook-relay is still the most recent row, and resumption never changes which row is current.

Audit retention for mariner-webhook-relay's captures follows the standard schedule: every sweep is retained, and the review reads the latest. This matters when reconstructing a finding months later — the row that was current at review time is identifiable by its capture timestamp, and the reconstruction must use that row rather than whatever happens to be newest at reconstruction time.

Certificate pinning by clients of mariner-webhook-relay was inventoried lightly, because pinning interacts badly with rotation: a pinned client can break when mariner-webhook-relay legitimately rotates. The review's rotation findings therefore come with a reminder that any pin held against mariner-webhook-relay's current leaf must be updated in lockstep with the re-issue.

Operationally, mariner-webhook-relay has been stable, but stability is not conformance. The review separates 'has not failed yet' from 'meets policy today', and it is the latter that governs the finding. Where the captured evidence and the live configuration disagree, the captured evidence is taken as the ground truth.

Forward-looking, the review recorded whether mariner-webhook-relay is on a path toward post-quantum-ready key exchange. This cycle treats PQC readiness as informational; it changes no disposition, but it is captured so that team-integrations can sequence the work against the rotation cadence the hygiene rules already impose.

Clock discipline was assumed but noted for mariner-webhook-relay: certificate validity windows are only meaningful if the validating hosts agree on the time. The review reasons about not-after relative to a single fixed review date, which removes any ambiguity that wall-clock skew on individual probers might otherwise introduce into the near-expiry judgement.

The protocol floor matters for mariner-webhook-relay because a single tolerated downgrade becomes a precedent. The review treats any negotiated version outside the allowed set as a finding in every environment, including development, so that a sandbox habit does not migrate into production by copy-paste.

Transport strictness headers on responses from mariner-webhook-relay were observed where applicable. Strict-transport signalling reduces downgrade opportunity for browser clients but does not substitute for the server-side protocol floor; the review credits it as defence in depth and nothing more for a prod surface.

Subject-alternative-name coverage on mariner-webhook-relay's leaf was checked against the hostnames https://webhook-relay.prod.mariner.internal actually answers for. A name not covered by the served certificate would surface as a verification failure in the capture, so SAN gaps tend to show up indirectly through the recorded verification outcome rather than as a separate graded axis.

For mariner-webhook-relay, issuer trust is a policy question settled against the maintained anchor set rather than the popularity of a commercial authority. The specific issuer and key parameters of mariner-webhook-relay's certificate of record are carried in the inventory database; what matters to the review is whether that issuer sits inside the governed anchor set, since a leaf that validates today but chains outside the set is still a rotation candidate on governance grounds.

Cipher-suite selection at mariner-webhook-relay was inspected for obviously deprecated constructions. While suite negotiation is not itself a graded axis in this review, a modern protocol version on https://webhook-relay.prod.mariner.internal strongly constrains the suite space, which is part of why the version allow-list does so much of the work and why a downgrade is treated as consequential rather than cosmetic.

Partner-facing exposure was a specific consideration for mariner-webhook-relay where federated third parties consume it. Federation raises the stakes of a mutual-TLS gap because the counterparty's assurance depends on it, which is why a production federation surface is held to the client-authentication expectation without sympathy for integration convenience.

Early-data exposure for mariner-webhook-relay was considered where 0-RTT resumption is enabled. Replayable early data is an application-layer hazard rather than a transport-policy axis, so it does not move mariner-webhook-relay's disposition, but it is flagged for team-integrations as a design note to weigh against the latency benefit on the prod surface.

The mariner-webhook-relay interconnect was modelled as part of the broader dependency graph. A weakness here propagates to every caller that trusts this endpoint, which is why the review resists the temptation to treat fans outbound event callbacks to subscriber endpoints as a low-stakes carve-out. The posture is assessed on its own merits and against the same bar as the busiest production path.

Certificate-transparency presence for mariner-webhook-relay's leaf was checked as a tamper-evidence signal. CT inclusion does not by itself make a certificate compliant — it is neither a protocol version nor an issuer-trust decision — but its absence on a publicly reachable prod endpoint would be a flag worth a follow-up outside this review's transport remit.

Truststore management on the prod side of mariner-webhook-relay matters for mutual TLS. Where the endpoint demands a client certificate, the set of client anchors it accepts is an operational concern for team-integrations; the review records only whether a client certificate was presented and validated, leaving truststore curation to the owning team's runbooks.

Mutual TLS expectations for mariner-webhook-relay follow the environment. The production trust boundary requires a client certificate; a non-production surface is not penalised for the absence of one. Where mariner-webhook-relay is expected to present a client certificate and the capture shows none, the gap is a protocol-level finding unless a waiver of the matching kind and scope is in force.

ALPN negotiation at mariner-webhook-relay was noted to confirm the application protocol riding over the tunnel, but protocol-version policy is enforced at the TLS layer and does not bend to the application above it. A modern application protocol over a legacy transport is still a transport finding for mariner-webhook-relay.

Finally, mariner-webhook-relay was checked for consistency between its environment label and its exposure. A service labelled prod is assessed under the rules for that environment; the review does not reclassify a surface to soften a finding, and team-integrations retains the route to reclassification through inventory governance rather than through this review.

The harness recorded the mariner-webhook-relay endpoint over successive sweeps; only the most recent capture per service is treated as authoritative, since earlier sweeps frequently predate a remediation or a re-issue. Reviewers are reminded that the captured negotiation outcomes, the chain-validation result, and the leaf fingerprint seen on the wire are held in the inventory database and must be read from there, not inferred from this narrative.

Revocation freshness was considered for mariner-webhook-relay. The review notes whether the endpoint's stapled status was recent and whether the validating party had a live path to revocation information, but treats stapling hygiene as advisory this cycle; the governing chain question remains whether the presented chain validated to a trusted anchor at capture time.

Where mariner-webhook-relay terminates TLS at a sidecar or a shared load balancer rather than in the application process, the review attributes the captured posture to the service as exposed on https://webhook-relay.prod.mariner.internal. Termination topology is an implementation detail; the obligation to meet policy attaches to the exposed prod surface regardless of which component holds the key.

Encrypted-client-hello readiness for mariner-webhook-relay was recorded as informational. ECH changes what an on-path observer can see about the handshake to https://webhook-relay.prod.mariner.internal but does not alter any graded axis here; it neither relaxes the protocol floor nor changes how a client certificate or a chain is judged.

Ownership context: team-integrations maintains mariner-webhook-relay and is the counterparty for any remediation. The review records owning teams so that rotation and re-issuance work lands with the group that can actually schedule a maintenance window on the prod surface, but ownership confers no relief from policy.

Cross-signing arrangements that touch mariner-webhook-relay's issuer were enumerated to make sure the chain the review reasons about is the chain clients actually build. A leaf can validate via more than one path; the governed question for mariner-webhook-relay is whether the issuer of record sits in the trust anchor set, independent of which cross-signed path a particular client happens to choose.

Renewal automation for mariner-webhook-relay was reviewed at the level of 'does a pipeline exist', not 'did it run'. An ACME-style renewal loop lowers the operational cost of the rotation findings this review may raise, but the disposition is taken from the captured state of https://webhook-relay.prod.mariner.internal, so a renewal that is configured but not yet effective does not pre-empt a near-expiry finding.

### svc-021 — mariner-ml-gateway

Transport strictness headers on responses from mariner-ml-gateway were observed where applicable. Strict-transport signalling reduces downgrade opportunity for browser clients but does not substitute for the server-side protocol floor; the review credits it as defence in depth and nothing more for a prod surface.

Exception status. mariner-ml-gateway (svc-021) holds waiver WV-2026-021, a transport-protocol exception scoped to the service's entire footprint across every environment. The register shows it granted on 2026-02-15 with a nominal expiry of 2026-12-15. The register carries WV-2026-021 as granted and in force as written; whether it still provides cover at review time is a separate question, settled by reading the policy review date against the recorded expiry, and by checking that the scope actually reaches the prod surface under assessment.

Subject-alternative-name coverage on mariner-ml-gateway's leaf was checked against the hostnames https://ml-gateway.prod.mariner.internal actually answers for. A name not covered by the served certificate would surface as a verification failure in the capture, so SAN gaps tend to show up indirectly through the recorded verification outcome rather than as a separate graded axis.

For mariner-ml-gateway, issuer trust is a policy question settled against the maintained anchor set rather than the popularity of a commercial authority. The specific issuer and key parameters of mariner-ml-gateway's certificate of record are carried in the inventory database; what matters to the review is whether that issuer sits inside the governed anchor set, since a leaf that validates today but chains outside the set is still a rotation candidate on governance grounds.

Cipher-suite selection at mariner-ml-gateway was inspected for obviously deprecated constructions. While suite negotiation is not itself a graded axis in this review, a modern protocol version on https://ml-gateway.prod.mariner.internal strongly constrains the suite space, which is part of why the version allow-list does so much of the work and why a downgrade is treated as consequential rather than cosmetic.

Partner-facing exposure was a specific consideration for mariner-ml-gateway where federated third parties consume it. Federation raises the stakes of a mutual-TLS gap because the counterparty's assurance depends on it, which is why a production federation surface is held to the client-authentication expectation without sympathy for integration convenience.

Early-data exposure for mariner-ml-gateway was considered where 0-RTT resumption is enabled. Replayable early data is an application-layer hazard rather than a transport-policy axis, so it does not move mariner-ml-gateway's disposition, but it is flagged for team-ml as a design note to weigh against the latency benefit on the prod surface.

The mariner-ml-gateway interconnect was modelled as part of the broader dependency graph. A weakness here propagates to every caller that trusts this endpoint, which is why the review resists the temptation to treat fronts model-inference traffic for product surfaces as a low-stakes carve-out. The posture is assessed on its own merits and against the same bar as the busiest production path.

Certificate-transparency presence for mariner-ml-gateway's leaf was checked as a tamper-evidence signal. CT inclusion does not by itself make a certificate compliant — it is neither a protocol version nor an issuer-trust decision — but its absence on a publicly reachable prod endpoint would be a flag worth a follow-up outside this review's transport remit.

Truststore management on the prod side of mariner-ml-gateway matters for mutual TLS. Where the endpoint demands a client certificate, the set of client anchors it accepts is an operational concern for team-ml; the review records only whether a client certificate was presented and validated, leaving truststore curation to the owning team's runbooks.

Mutual TLS expectations for mariner-ml-gateway follow the environment. The production trust boundary requires a client certificate; a non-production surface is not penalised for the absence of one. Where mariner-ml-gateway is expected to present a client certificate and the capture shows none, the gap is a protocol-level finding unless a waiver of the matching kind and scope is in force.

ALPN negotiation at mariner-ml-gateway was noted to confirm the application protocol riding over the tunnel, but protocol-version policy is enforced at the TLS layer and does not bend to the application above it. A modern application protocol over a legacy transport is still a transport finding for mariner-ml-gateway.

Finally, mariner-ml-gateway was checked for consistency between its environment label and its exposure. A service labelled prod is assessed under the rules for that environment; the review does not reclassify a surface to soften a finding, and team-ml retains the route to reclassification through inventory governance rather than through this review.

The harness recorded the mariner-ml-gateway endpoint over successive sweeps; only the most recent capture per service is treated as authoritative, since earlier sweeps frequently predate a remediation or a re-issue. Reviewers are reminded that the captured negotiation outcomes, the chain-validation result, and the leaf fingerprint seen on the wire are held in the inventory database and must be read from there, not inferred from this narrative.

Revocation freshness was considered for mariner-ml-gateway. The review notes whether the endpoint's stapled status was recent and whether the validating party had a live path to revocation information, but treats stapling hygiene as advisory this cycle; the governing chain question remains whether the presented chain validated to a trusted anchor at capture time.

Where mariner-ml-gateway terminates TLS at a sidecar or a shared load balancer rather than in the application process, the review attributes the captured posture to the service as exposed on https://ml-gateway.prod.mariner.internal. Termination topology is an implementation detail; the obligation to meet policy attaches to the exposed prod surface regardless of which component holds the key.

Encrypted-client-hello readiness for mariner-ml-gateway was recorded as informational. ECH changes what an on-path observer can see about the handshake to https://ml-gateway.prod.mariner.internal but does not alter any graded axis here; it neither relaxes the protocol floor nor changes how a client certificate or a chain is judged.

Ownership context: team-ml maintains mariner-ml-gateway and is the counterparty for any remediation. The review records owning teams so that rotation and re-issuance work lands with the group that can actually schedule a maintenance window on the prod surface, but ownership confers no relief from policy.

Cross-signing arrangements that touch mariner-ml-gateway's issuer were enumerated to make sure the chain the review reasons about is the chain clients actually build. A leaf can validate via more than one path; the governed question for mariner-ml-gateway is whether the issuer of record sits in the trust anchor set, independent of which cross-signed path a particular client happens to choose.

Renewal automation for mariner-ml-gateway was reviewed at the level of 'does a pipeline exist', not 'did it run'. An ACME-style renewal loop lowers the operational cost of the rotation findings this review may raise, but the disposition is taken from the captured state of https://ml-gateway.prod.mariner.internal, so a renewal that is configured but not yet effective does not pre-empt a near-expiry finding.

Certificate lifetime is the other half of hygiene. A leaf approaching its not-after boundary inside the rotation window is scheduled for replacement well ahead of the cliff, on the principle that a lapse on the prod surface is an availability incident as much as a security one. The window is uniform across services so that nothing in mariner-ml-gateway's profile earns special treatment.

SNI and virtual-host disambiguation were verified for mariner-ml-gateway so that the captured leaf is unambiguously the one https://ml-gateway.prod.mariner.internal intends to serve. A mismatch between the requested name and the served certificate would itself be an integrity concern, which is one more reason the observed fingerprint is compared against the inventory of record rather than assumed.

The review explicitly separated configuration intent from observed behaviour for mariner-ml-gateway. A configuration file may declare a strict posture, but if the captured evidence on https://ml-gateway.prod.mariner.internal shows otherwise, the evidence governs the finding; conversely a permissive-looking configuration that nonetheless negotiated within policy is judged on what actually happened on the wire.

Within the review boundary, mariner-ml-gateway (svc-021) fronts model-inference traffic for product surfaces. It is owned by team-ml and presents on https://ml-gateway.prod.mariner.internal, which the inventory classifies as a prod surface. The transport posture of any prod endpoint is weighed against the operative policy rather than against historical convention, and the assessment proceeds from the evidence of record rather than from operator attestation.

Documentation for mariner-ml-gateway was cross-checked against the configuration set. Where a policy value is needed — the rotation window, the protocol allow-list, the key floors, or the issuer anchor set — it is read from the validated configuration rather than from this prose, which paraphrases policy for the reader's convenience only.

For mesh participants such as mariner-ml-gateway, certificate rotation is automated through the issuing control plane, which lowers the cost of a rotation finding but does not remove the obligation: an automated rotation that has not yet run still leaves a soon-to-expire leaf on https://ml-gateway.prod.mariner.internal, and the review grades the state at capture time, not the intention encoded in automation.

Revocation-list distribution touching mariner-ml-gateway's issuer was sanity-checked so that a client choosing CRL over stapled status still has a path. As with stapling, the review treats CRL reachability as advisory this cycle; the governing question for mariner-ml-gateway remains whether the presented chain validated at capture time.

Evidence handling for mariner-ml-gateway is deliberately conservative. When the fingerprint observed on the wire disagrees with the inventory of record, the review does not attempt to reconcile the two in the agent's favour; the disagreement is itself the finding, and it is escalated rather than waived, regardless of any paperwork that might otherwise have applied.

Key-ceremony provenance for mariner-ml-gateway's material was reviewed at a high level. Where team-ml can attest that the private key was generated and held in a hardware security module, the operational risk of the key is lower, but provenance does not raise an under-strength key above the floor or extend a certificate past its not-after date.

Wildcard usage at mariner-ml-gateway was noted where present. A wildcard leaf broadens blast radius if its key is compromised, so although a wildcard is not itself a finding, it raises the priority of the hygiene rules for mariner-ml-gateway — a near-expiry or under-strength wildcard is a rotation the review would rather see scheduled sooner than later.

Key strength for mariner-ml-gateway is judged against the floor for its algorithm family. The review does not grade keys on a curve: a key below the floor is a rotation finding irrespective of the sensitivity of the workload, because under-strength material weakens the whole interconnect graph that mariner-ml-gateway participates in.

Session resumption behaviour for mariner-ml-gateway was characterised so that repeat captures could be compared fairly. Resumption can mask a renegotiated parameter, so the harness records full-handshake outcomes where it can; the authoritative capture for mariner-ml-gateway is still the most recent row, and resumption never changes which row is current.

Audit retention for mariner-ml-gateway's captures follows the standard schedule: every sweep is retained, and the review reads the latest. This matters when reconstructing a finding months later — the row that was current at review time is identifiable by its capture timestamp, and the reconstruction must use that row rather than whatever happens to be newest at reconstruction time.

Certificate pinning by clients of mariner-ml-gateway was inventoried lightly, because pinning interacts badly with rotation: a pinned client can break when mariner-ml-gateway legitimately rotates. The review's rotation findings therefore come with a reminder that any pin held against mariner-ml-gateway's current leaf must be updated in lockstep with the re-issue.

Operationally, mariner-ml-gateway has been stable, but stability is not conformance. The review separates 'has not failed yet' from 'meets policy today', and it is the latter that governs the finding. Where the captured evidence and the live configuration disagree, the captured evidence is taken as the ground truth.

Forward-looking, the review recorded whether mariner-ml-gateway is on a path toward post-quantum-ready key exchange. This cycle treats PQC readiness as informational; it changes no disposition, but it is captured so that team-ml can sequence the work against the rotation cadence the hygiene rules already impose.

Clock discipline was assumed but noted for mariner-ml-gateway: certificate validity windows are only meaningful if the validating hosts agree on the time. The review reasons about not-after relative to a single fixed review date, which removes any ambiguity that wall-clock skew on individual probers might otherwise introduce into the near-expiry judgement.

The protocol floor matters for mariner-ml-gateway because a single tolerated downgrade becomes a precedent. The review treats any negotiated version outside the allowed set as a finding in every environment, including development, so that a sandbox habit does not migrate into production by copy-paste.

### svc-022 — mariner-vault-proxy

Renewal automation for mariner-vault-proxy was reviewed at the level of 'does a pipeline exist', not 'did it run'. An ACME-style renewal loop lowers the operational cost of the rotation findings this review may raise, but the disposition is taken from the captured state of https://vault-proxy.prod.mariner.internal, so a renewal that is configured but not yet effective does not pre-empt a near-expiry finding.

Certificate lifetime is the other half of hygiene. A leaf approaching its not-after boundary inside the rotation window is scheduled for replacement well ahead of the cliff, on the principle that a lapse on the prod surface is an availability incident as much as a security one. The window is uniform across services so that nothing in mariner-vault-proxy's profile earns special treatment.

Exception status. mariner-vault-proxy (svc-022) holds waiver WV-2026-022, a mutual-TLS exception scoped to the production listener only. The register shows it granted on 2026-01-10 with a nominal expiry of 2026-11-01. The register carries WV-2026-022 as granted and in force as written; whether it still provides cover at review time is a separate question, settled by reading the policy review date against the recorded expiry, and by checking that the scope actually reaches the prod surface under assessment.

SNI and virtual-host disambiguation were verified for mariner-vault-proxy so that the captured leaf is unambiguously the one https://vault-proxy.prod.mariner.internal intends to serve. A mismatch between the requested name and the served certificate would itself be an integrity concern, which is one more reason the observed fingerprint is compared against the inventory of record rather than assumed.

The review explicitly separated configuration intent from observed behaviour for mariner-vault-proxy. A configuration file may declare a strict posture, but if the captured evidence on https://vault-proxy.prod.mariner.internal shows otherwise, the evidence governs the finding; conversely a permissive-looking configuration that nonetheless negotiated within policy is judged on what actually happened on the wire.

Within the review boundary, mariner-vault-proxy (svc-022) mediates secret retrieval for workloads. It is owned by team-security and presents on https://vault-proxy.prod.mariner.internal, which the inventory classifies as a prod surface. The transport posture of any prod endpoint is weighed against the operative policy rather than against historical convention, and the assessment proceeds from the evidence of record rather than from operator attestation.

Documentation for mariner-vault-proxy was cross-checked against the configuration set. Where a policy value is needed — the rotation window, the protocol allow-list, the key floors, or the issuer anchor set — it is read from the validated configuration rather than from this prose, which paraphrases policy for the reader's convenience only.

For mesh participants such as mariner-vault-proxy, certificate rotation is automated through the issuing control plane, which lowers the cost of a rotation finding but does not remove the obligation: an automated rotation that has not yet run still leaves a soon-to-expire leaf on https://vault-proxy.prod.mariner.internal, and the review grades the state at capture time, not the intention encoded in automation.

Revocation-list distribution touching mariner-vault-proxy's issuer was sanity-checked so that a client choosing CRL over stapled status still has a path. As with stapling, the review treats CRL reachability as advisory this cycle; the governing question for mariner-vault-proxy remains whether the presented chain validated at capture time.

Evidence handling for mariner-vault-proxy is deliberately conservative. When the fingerprint observed on the wire disagrees with the inventory of record, the review does not attempt to reconcile the two in the agent's favour; the disagreement is itself the finding, and it is escalated rather than waived, regardless of any paperwork that might otherwise have applied.

Key-ceremony provenance for mariner-vault-proxy's material was reviewed at a high level. Where team-security can attest that the private key was generated and held in a hardware security module, the operational risk of the key is lower, but provenance does not raise an under-strength key above the floor or extend a certificate past its not-after date.

Wildcard usage at mariner-vault-proxy was noted where present. A wildcard leaf broadens blast radius if its key is compromised, so although a wildcard is not itself a finding, it raises the priority of the hygiene rules for mariner-vault-proxy — a near-expiry or under-strength wildcard is a rotation the review would rather see scheduled sooner than later.

Key strength for mariner-vault-proxy is judged against the floor for its algorithm family. The review does not grade keys on a curve: a key below the floor is a rotation finding irrespective of the sensitivity of the workload, because under-strength material weakens the whole interconnect graph that mariner-vault-proxy participates in.

Session resumption behaviour for mariner-vault-proxy was characterised so that repeat captures could be compared fairly. Resumption can mask a renegotiated parameter, so the harness records full-handshake outcomes where it can; the authoritative capture for mariner-vault-proxy is still the most recent row, and resumption never changes which row is current.

Audit retention for mariner-vault-proxy's captures follows the standard schedule: every sweep is retained, and the review reads the latest. This matters when reconstructing a finding months later — the row that was current at review time is identifiable by its capture timestamp, and the reconstruction must use that row rather than whatever happens to be newest at reconstruction time.

Certificate pinning by clients of mariner-vault-proxy was inventoried lightly, because pinning interacts badly with rotation: a pinned client can break when mariner-vault-proxy legitimately rotates. The review's rotation findings therefore come with a reminder that any pin held against mariner-vault-proxy's current leaf must be updated in lockstep with the re-issue.

Operationally, mariner-vault-proxy has been stable, but stability is not conformance. The review separates 'has not failed yet' from 'meets policy today', and it is the latter that governs the finding. Where the captured evidence and the live configuration disagree, the captured evidence is taken as the ground truth.

Forward-looking, the review recorded whether mariner-vault-proxy is on a path toward post-quantum-ready key exchange. This cycle treats PQC readiness as informational; it changes no disposition, but it is captured so that team-security can sequence the work against the rotation cadence the hygiene rules already impose.

Clock discipline was assumed but noted for mariner-vault-proxy: certificate validity windows are only meaningful if the validating hosts agree on the time. The review reasons about not-after relative to a single fixed review date, which removes any ambiguity that wall-clock skew on individual probers might otherwise introduce into the near-expiry judgement.

The protocol floor matters for mariner-vault-proxy because a single tolerated downgrade becomes a precedent. The review treats any negotiated version outside the allowed set as a finding in every environment, including development, so that a sandbox habit does not migrate into production by copy-paste.

Transport strictness headers on responses from mariner-vault-proxy were observed where applicable. Strict-transport signalling reduces downgrade opportunity for browser clients but does not substitute for the server-side protocol floor; the review credits it as defence in depth and nothing more for a prod surface.

Subject-alternative-name coverage on mariner-vault-proxy's leaf was checked against the hostnames https://vault-proxy.prod.mariner.internal actually answers for. A name not covered by the served certificate would surface as a verification failure in the capture, so SAN gaps tend to show up indirectly through the recorded verification outcome rather than as a separate graded axis.

For mariner-vault-proxy, issuer trust is a policy question settled against the maintained anchor set rather than the popularity of a commercial authority. The specific issuer and key parameters of mariner-vault-proxy's certificate of record are carried in the inventory database; what matters to the review is whether that issuer sits inside the governed anchor set, since a leaf that validates today but chains outside the set is still a rotation candidate on governance grounds.

Cipher-suite selection at mariner-vault-proxy was inspected for obviously deprecated constructions. While suite negotiation is not itself a graded axis in this review, a modern protocol version on https://vault-proxy.prod.mariner.internal strongly constrains the suite space, which is part of why the version allow-list does so much of the work and why a downgrade is treated as consequential rather than cosmetic.

Partner-facing exposure was a specific consideration for mariner-vault-proxy where federated third parties consume it. Federation raises the stakes of a mutual-TLS gap because the counterparty's assurance depends on it, which is why a production federation surface is held to the client-authentication expectation without sympathy for integration convenience.

Early-data exposure for mariner-vault-proxy was considered where 0-RTT resumption is enabled. Replayable early data is an application-layer hazard rather than a transport-policy axis, so it does not move mariner-vault-proxy's disposition, but it is flagged for team-security as a design note to weigh against the latency benefit on the prod surface.

The mariner-vault-proxy interconnect was modelled as part of the broader dependency graph. A weakness here propagates to every caller that trusts this endpoint, which is why the review resists the temptation to treat mediates secret retrieval for workloads as a low-stakes carve-out. The posture is assessed on its own merits and against the same bar as the busiest production path.

Certificate-transparency presence for mariner-vault-proxy's leaf was checked as a tamper-evidence signal. CT inclusion does not by itself make a certificate compliant — it is neither a protocol version nor an issuer-trust decision — but its absence on a publicly reachable prod endpoint would be a flag worth a follow-up outside this review's transport remit.

Truststore management on the prod side of mariner-vault-proxy matters for mutual TLS. Where the endpoint demands a client certificate, the set of client anchors it accepts is an operational concern for team-security; the review records only whether a client certificate was presented and validated, leaving truststore curation to the owning team's runbooks.

Mutual TLS expectations for mariner-vault-proxy follow the environment. The production trust boundary requires a client certificate; a non-production surface is not penalised for the absence of one. Where mariner-vault-proxy is expected to present a client certificate and the capture shows none, the gap is a protocol-level finding unless a waiver of the matching kind and scope is in force.

ALPN negotiation at mariner-vault-proxy was noted to confirm the application protocol riding over the tunnel, but protocol-version policy is enforced at the TLS layer and does not bend to the application above it. A modern application protocol over a legacy transport is still a transport finding for mariner-vault-proxy.

Finally, mariner-vault-proxy was checked for consistency between its environment label and its exposure. A service labelled prod is assessed under the rules for that environment; the review does not reclassify a surface to soften a finding, and team-security retains the route to reclassification through inventory governance rather than through this review.

The harness recorded the mariner-vault-proxy endpoint over successive sweeps; only the most recent capture per service is treated as authoritative, since earlier sweeps frequently predate a remediation or a re-issue. Reviewers are reminded that the captured negotiation outcomes, the chain-validation result, and the leaf fingerprint seen on the wire are held in the inventory database and must be read from there, not inferred from this narrative.

Revocation freshness was considered for mariner-vault-proxy. The review notes whether the endpoint's stapled status was recent and whether the validating party had a live path to revocation information, but treats stapling hygiene as advisory this cycle; the governing chain question remains whether the presented chain validated to a trusted anchor at capture time.

Where mariner-vault-proxy terminates TLS at a sidecar or a shared load balancer rather than in the application process, the review attributes the captured posture to the service as exposed on https://vault-proxy.prod.mariner.internal. Termination topology is an implementation detail; the obligation to meet policy attaches to the exposed prod surface regardless of which component holds the key.

Encrypted-client-hello readiness for mariner-vault-proxy was recorded as informational. ECH changes what an on-path observer can see about the handshake to https://vault-proxy.prod.mariner.internal but does not alter any graded axis here; it neither relaxes the protocol floor nor changes how a client certificate or a chain is judged.

Ownership context: team-security maintains mariner-vault-proxy and is the counterparty for any remediation. The review records owning teams so that rotation and re-issuance work lands with the group that can actually schedule a maintenance window on the prod surface, but ownership confers no relief from policy.

Cross-signing arrangements that touch mariner-vault-proxy's issuer were enumerated to make sure the chain the review reasons about is the chain clients actually build. A leaf can validate via more than one path; the governed question for mariner-vault-proxy is whether the issuer of record sits in the trust anchor set, independent of which cross-signed path a particular client happens to choose.

### svc-023 — mariner-status-page

The protocol floor matters for mariner-status-page because a single tolerated downgrade becomes a precedent. The review treats any negotiated version outside the allowed set as a finding in every environment, including development, so that a sandbox habit does not migrate into production by copy-paste.

Transport strictness headers on responses from mariner-status-page were observed where applicable. Strict-transport signalling reduces downgrade opportunity for browser clients but does not substitute for the server-side protocol floor; the review credits it as defence in depth and nothing more for a prod surface.

Subject-alternative-name coverage on mariner-status-page's leaf was checked against the hostnames https://status-page.prod.mariner.internal actually answers for. A name not covered by the served certificate would surface as a verification failure in the capture, so SAN gaps tend to show up indirectly through the recorded verification outcome rather than as a separate graded axis.

Exception status. mariner-status-page (svc-023) carries no transport-security waiver of any kind in the register — no protocol exception, no mutual-TLS carve-out, and no chain exception. It is therefore assessed directly against the operative policy, with the captured evidence in the inventory database standing as the sole record of how the prod endpoint actually negotiated.

For mariner-status-page, issuer trust is a policy question settled against the maintained anchor set rather than the popularity of a commercial authority. The specific issuer and key parameters of mariner-status-page's certificate of record are carried in the inventory database; what matters to the review is whether that issuer sits inside the governed anchor set, since a leaf that validates today but chains outside the set is still a rotation candidate on governance grounds.

Cipher-suite selection at mariner-status-page was inspected for obviously deprecated constructions. While suite negotiation is not itself a graded axis in this review, a modern protocol version on https://status-page.prod.mariner.internal strongly constrains the suite space, which is part of why the version allow-list does so much of the work and why a downgrade is treated as consequential rather than cosmetic.

Partner-facing exposure was a specific consideration for mariner-status-page where federated third parties consume it. Federation raises the stakes of a mutual-TLS gap because the counterparty's assurance depends on it, which is why a production federation surface is held to the client-authentication expectation without sympathy for integration convenience.

Early-data exposure for mariner-status-page was considered where 0-RTT resumption is enabled. Replayable early data is an application-layer hazard rather than a transport-policy axis, so it does not move mariner-status-page's disposition, but it is flagged for team-sre as a design note to weigh against the latency benefit on the prod surface.

The mariner-status-page interconnect was modelled as part of the broader dependency graph. A weakness here propagates to every caller that trusts this endpoint, which is why the review resists the temptation to treat drives the public availability dashboard as a low-stakes carve-out. The posture is assessed on its own merits and against the same bar as the busiest production path.

Certificate-transparency presence for mariner-status-page's leaf was checked as a tamper-evidence signal. CT inclusion does not by itself make a certificate compliant — it is neither a protocol version nor an issuer-trust decision — but its absence on a publicly reachable prod endpoint would be a flag worth a follow-up outside this review's transport remit.

Truststore management on the prod side of mariner-status-page matters for mutual TLS. Where the endpoint demands a client certificate, the set of client anchors it accepts is an operational concern for team-sre; the review records only whether a client certificate was presented and validated, leaving truststore curation to the owning team's runbooks.

Mutual TLS expectations for mariner-status-page follow the environment. The production trust boundary requires a client certificate; a non-production surface is not penalised for the absence of one. Where mariner-status-page is expected to present a client certificate and the capture shows none, the gap is a protocol-level finding unless a waiver of the matching kind and scope is in force.

ALPN negotiation at mariner-status-page was noted to confirm the application protocol riding over the tunnel, but protocol-version policy is enforced at the TLS layer and does not bend to the application above it. A modern application protocol over a legacy transport is still a transport finding for mariner-status-page.

Finally, mariner-status-page was checked for consistency between its environment label and its exposure. A service labelled prod is assessed under the rules for that environment; the review does not reclassify a surface to soften a finding, and team-sre retains the route to reclassification through inventory governance rather than through this review.

The harness recorded the mariner-status-page endpoint over successive sweeps; only the most recent capture per service is treated as authoritative, since earlier sweeps frequently predate a remediation or a re-issue. Reviewers are reminded that the captured negotiation outcomes, the chain-validation result, and the leaf fingerprint seen on the wire are held in the inventory database and must be read from there, not inferred from this narrative.

Revocation freshness was considered for mariner-status-page. The review notes whether the endpoint's stapled status was recent and whether the validating party had a live path to revocation information, but treats stapling hygiene as advisory this cycle; the governing chain question remains whether the presented chain validated to a trusted anchor at capture time.

Where mariner-status-page terminates TLS at a sidecar or a shared load balancer rather than in the application process, the review attributes the captured posture to the service as exposed on https://status-page.prod.mariner.internal. Termination topology is an implementation detail; the obligation to meet policy attaches to the exposed prod surface regardless of which component holds the key.

Encrypted-client-hello readiness for mariner-status-page was recorded as informational. ECH changes what an on-path observer can see about the handshake to https://status-page.prod.mariner.internal but does not alter any graded axis here; it neither relaxes the protocol floor nor changes how a client certificate or a chain is judged.

Ownership context: team-sre maintains mariner-status-page and is the counterparty for any remediation. The review records owning teams so that rotation and re-issuance work lands with the group that can actually schedule a maintenance window on the prod surface, but ownership confers no relief from policy.

Cross-signing arrangements that touch mariner-status-page's issuer were enumerated to make sure the chain the review reasons about is the chain clients actually build. A leaf can validate via more than one path; the governed question for mariner-status-page is whether the issuer of record sits in the trust anchor set, independent of which cross-signed path a particular client happens to choose.

Renewal automation for mariner-status-page was reviewed at the level of 'does a pipeline exist', not 'did it run'. An ACME-style renewal loop lowers the operational cost of the rotation findings this review may raise, but the disposition is taken from the captured state of https://status-page.prod.mariner.internal, so a renewal that is configured but not yet effective does not pre-empt a near-expiry finding.

Certificate lifetime is the other half of hygiene. A leaf approaching its not-after boundary inside the rotation window is scheduled for replacement well ahead of the cliff, on the principle that a lapse on the prod surface is an availability incident as much as a security one. The window is uniform across services so that nothing in mariner-status-page's profile earns special treatment.

SNI and virtual-host disambiguation were verified for mariner-status-page so that the captured leaf is unambiguously the one https://status-page.prod.mariner.internal intends to serve. A mismatch between the requested name and the served certificate would itself be an integrity concern, which is one more reason the observed fingerprint is compared against the inventory of record rather than assumed.

The review explicitly separated configuration intent from observed behaviour for mariner-status-page. A configuration file may declare a strict posture, but if the captured evidence on https://status-page.prod.mariner.internal shows otherwise, the evidence governs the finding; conversely a permissive-looking configuration that nonetheless negotiated within policy is judged on what actually happened on the wire.

Within the review boundary, mariner-status-page (svc-023) drives the public availability dashboard. It is owned by team-sre and presents on https://status-page.prod.mariner.internal, which the inventory classifies as a prod surface. The transport posture of any prod endpoint is weighed against the operative policy rather than against historical convention, and the assessment proceeds from the evidence of record rather than from operator attestation.

Documentation for mariner-status-page was cross-checked against the configuration set. Where a policy value is needed — the rotation window, the protocol allow-list, the key floors, or the issuer anchor set — it is read from the validated configuration rather than from this prose, which paraphrases policy for the reader's convenience only.

For mesh participants such as mariner-status-page, certificate rotation is automated through the issuing control plane, which lowers the cost of a rotation finding but does not remove the obligation: an automated rotation that has not yet run still leaves a soon-to-expire leaf on https://status-page.prod.mariner.internal, and the review grades the state at capture time, not the intention encoded in automation.

Revocation-list distribution touching mariner-status-page's issuer was sanity-checked so that a client choosing CRL over stapled status still has a path. As with stapling, the review treats CRL reachability as advisory this cycle; the governing question for mariner-status-page remains whether the presented chain validated at capture time.

Evidence handling for mariner-status-page is deliberately conservative. When the fingerprint observed on the wire disagrees with the inventory of record, the review does not attempt to reconcile the two in the agent's favour; the disagreement is itself the finding, and it is escalated rather than waived, regardless of any paperwork that might otherwise have applied.

Key-ceremony provenance for mariner-status-page's material was reviewed at a high level. Where team-sre can attest that the private key was generated and held in a hardware security module, the operational risk of the key is lower, but provenance does not raise an under-strength key above the floor or extend a certificate past its not-after date.

Wildcard usage at mariner-status-page was noted where present. A wildcard leaf broadens blast radius if its key is compromised, so although a wildcard is not itself a finding, it raises the priority of the hygiene rules for mariner-status-page — a near-expiry or under-strength wildcard is a rotation the review would rather see scheduled sooner than later.

Key strength for mariner-status-page is judged against the floor for its algorithm family. The review does not grade keys on a curve: a key below the floor is a rotation finding irrespective of the sensitivity of the workload, because under-strength material weakens the whole interconnect graph that mariner-status-page participates in.

Session resumption behaviour for mariner-status-page was characterised so that repeat captures could be compared fairly. Resumption can mask a renegotiated parameter, so the harness records full-handshake outcomes where it can; the authoritative capture for mariner-status-page is still the most recent row, and resumption never changes which row is current.

Audit retention for mariner-status-page's captures follows the standard schedule: every sweep is retained, and the review reads the latest. This matters when reconstructing a finding months later — the row that was current at review time is identifiable by its capture timestamp, and the reconstruction must use that row rather than whatever happens to be newest at reconstruction time.

Certificate pinning by clients of mariner-status-page was inventoried lightly, because pinning interacts badly with rotation: a pinned client can break when mariner-status-page legitimately rotates. The review's rotation findings therefore come with a reminder that any pin held against mariner-status-page's current leaf must be updated in lockstep with the re-issue.

Operationally, mariner-status-page has been stable, but stability is not conformance. The review separates 'has not failed yet' from 'meets policy today', and it is the latter that governs the finding. Where the captured evidence and the live configuration disagree, the captured evidence is taken as the ground truth.

Forward-looking, the review recorded whether mariner-status-page is on a path toward post-quantum-ready key exchange. This cycle treats PQC readiness as informational; it changes no disposition, but it is captured so that team-sre can sequence the work against the rotation cadence the hygiene rules already impose.

Clock discipline was assumed but noted for mariner-status-page: certificate validity windows are only meaningful if the validating hosts agree on the time. The review reasons about not-after relative to a single fixed review date, which removes any ambiguity that wall-clock skew on individual probers might otherwise introduce into the near-expiry judgement.

### svc-024 — mariner-feature-flags

Cross-signing arrangements that touch mariner-feature-flags's issuer were enumerated to make sure the chain the review reasons about is the chain clients actually build. A leaf can validate via more than one path; the governed question for mariner-feature-flags is whether the issuer of record sits in the trust anchor set, independent of which cross-signed path a particular client happens to choose.

Exception status. mariner-feature-flags (svc-024) carries no transport-security waiver of any kind in the register — no protocol exception, no mutual-TLS carve-out, and no chain exception. It is therefore assessed directly against the operative policy, with the captured evidence in the inventory database standing as the sole record of how the staging endpoint actually negotiated.

Renewal automation for mariner-feature-flags was reviewed at the level of 'does a pipeline exist', not 'did it run'. An ACME-style renewal loop lowers the operational cost of the rotation findings this review may raise, but the disposition is taken from the captured state of https://feature-flags.staging.mariner.internal, so a renewal that is configured but not yet effective does not pre-empt a near-expiry finding.

Certificate lifetime is the other half of hygiene. A leaf approaching its not-after boundary inside the rotation window is scheduled for replacement well ahead of the cliff, on the principle that a lapse on the staging surface is an availability incident as much as a security one. The window is uniform across services so that nothing in mariner-feature-flags's profile earns special treatment.

SNI and virtual-host disambiguation were verified for mariner-feature-flags so that the captured leaf is unambiguously the one https://feature-flags.staging.mariner.internal intends to serve. A mismatch between the requested name and the served certificate would itself be an integrity concern, which is one more reason the observed fingerprint is compared against the inventory of record rather than assumed.

The review explicitly separated configuration intent from observed behaviour for mariner-feature-flags. A configuration file may declare a strict posture, but if the captured evidence on https://feature-flags.staging.mariner.internal shows otherwise, the evidence governs the finding; conversely a permissive-looking configuration that nonetheless negotiated within policy is judged on what actually happened on the wire.

Within the review boundary, mariner-feature-flags (svc-024) evaluates rollout cohorts for product experiments. It is owned by team-platform and presents on https://feature-flags.staging.mariner.internal, which the inventory classifies as a staging surface. The transport posture of any staging endpoint is weighed against the operative policy rather than against historical convention, and the assessment proceeds from the evidence of record rather than from operator attestation.

Documentation for mariner-feature-flags was cross-checked against the configuration set. Where a policy value is needed — the rotation window, the protocol allow-list, the key floors, or the issuer anchor set — it is read from the validated configuration rather than from this prose, which paraphrases policy for the reader's convenience only.

For mesh participants such as mariner-feature-flags, certificate rotation is automated through the issuing control plane, which lowers the cost of a rotation finding but does not remove the obligation: an automated rotation that has not yet run still leaves a soon-to-expire leaf on https://feature-flags.staging.mariner.internal, and the review grades the state at capture time, not the intention encoded in automation.

Revocation-list distribution touching mariner-feature-flags's issuer was sanity-checked so that a client choosing CRL over stapled status still has a path. As with stapling, the review treats CRL reachability as advisory this cycle; the governing question for mariner-feature-flags remains whether the presented chain validated at capture time.

Evidence handling for mariner-feature-flags is deliberately conservative. When the fingerprint observed on the wire disagrees with the inventory of record, the review does not attempt to reconcile the two in the agent's favour; the disagreement is itself the finding, and it is escalated rather than waived, regardless of any paperwork that might otherwise have applied.

Key-ceremony provenance for mariner-feature-flags's material was reviewed at a high level. Where team-platform can attest that the private key was generated and held in a hardware security module, the operational risk of the key is lower, but provenance does not raise an under-strength key above the floor or extend a certificate past its not-after date.

Wildcard usage at mariner-feature-flags was noted where present. A wildcard leaf broadens blast radius if its key is compromised, so although a wildcard is not itself a finding, it raises the priority of the hygiene rules for mariner-feature-flags — a near-expiry or under-strength wildcard is a rotation the review would rather see scheduled sooner than later.

Key strength for mariner-feature-flags is judged against the floor for its algorithm family. The review does not grade keys on a curve: a key below the floor is a rotation finding irrespective of the sensitivity of the workload, because under-strength material weakens the whole interconnect graph that mariner-feature-flags participates in.

Session resumption behaviour for mariner-feature-flags was characterised so that repeat captures could be compared fairly. Resumption can mask a renegotiated parameter, so the harness records full-handshake outcomes where it can; the authoritative capture for mariner-feature-flags is still the most recent row, and resumption never changes which row is current.

Audit retention for mariner-feature-flags's captures follows the standard schedule: every sweep is retained, and the review reads the latest. This matters when reconstructing a finding months later — the row that was current at review time is identifiable by its capture timestamp, and the reconstruction must use that row rather than whatever happens to be newest at reconstruction time.

Certificate pinning by clients of mariner-feature-flags was inventoried lightly, because pinning interacts badly with rotation: a pinned client can break when mariner-feature-flags legitimately rotates. The review's rotation findings therefore come with a reminder that any pin held against mariner-feature-flags's current leaf must be updated in lockstep with the re-issue.

Operationally, mariner-feature-flags has been stable, but stability is not conformance. The review separates 'has not failed yet' from 'meets policy today', and it is the latter that governs the finding. Where the captured evidence and the live configuration disagree, the captured evidence is taken as the ground truth.

Forward-looking, the review recorded whether mariner-feature-flags is on a path toward post-quantum-ready key exchange. This cycle treats PQC readiness as informational; it changes no disposition, but it is captured so that team-platform can sequence the work against the rotation cadence the hygiene rules already impose.

Clock discipline was assumed but noted for mariner-feature-flags: certificate validity windows are only meaningful if the validating hosts agree on the time. The review reasons about not-after relative to a single fixed review date, which removes any ambiguity that wall-clock skew on individual probers might otherwise introduce into the near-expiry judgement.

The protocol floor matters for mariner-feature-flags because a single tolerated downgrade becomes a precedent. The review treats any negotiated version outside the allowed set as a finding in every environment, including development, so that a sandbox habit does not migrate into production by copy-paste.

Transport strictness headers on responses from mariner-feature-flags were observed where applicable. Strict-transport signalling reduces downgrade opportunity for browser clients but does not substitute for the server-side protocol floor; the review credits it as defence in depth and nothing more for a staging surface.

Subject-alternative-name coverage on mariner-feature-flags's leaf was checked against the hostnames https://feature-flags.staging.mariner.internal actually answers for. A name not covered by the served certificate would surface as a verification failure in the capture, so SAN gaps tend to show up indirectly through the recorded verification outcome rather than as a separate graded axis.

For mariner-feature-flags, issuer trust is a policy question settled against the maintained anchor set rather than the popularity of a commercial authority. The specific issuer and key parameters of mariner-feature-flags's certificate of record are carried in the inventory database; what matters to the review is whether that issuer sits inside the governed anchor set, since a leaf that validates today but chains outside the set is still a rotation candidate on governance grounds.

Cipher-suite selection at mariner-feature-flags was inspected for obviously deprecated constructions. While suite negotiation is not itself a graded axis in this review, a modern protocol version on https://feature-flags.staging.mariner.internal strongly constrains the suite space, which is part of why the version allow-list does so much of the work and why a downgrade is treated as consequential rather than cosmetic.

Partner-facing exposure was a specific consideration for mariner-feature-flags where federated third parties consume it. Federation raises the stakes of a mutual-TLS gap because the counterparty's assurance depends on it, which is why a production federation surface is held to the client-authentication expectation without sympathy for integration convenience.

Early-data exposure for mariner-feature-flags was considered where 0-RTT resumption is enabled. Replayable early data is an application-layer hazard rather than a transport-policy axis, so it does not move mariner-feature-flags's disposition, but it is flagged for team-platform as a design note to weigh against the latency benefit on the staging surface.

The mariner-feature-flags interconnect was modelled as part of the broader dependency graph. A weakness here propagates to every caller that trusts this endpoint, which is why the review resists the temptation to treat evaluates rollout cohorts for product experiments as a low-stakes carve-out. The posture is assessed on its own merits and against the same bar as the busiest production path.

Certificate-transparency presence for mariner-feature-flags's leaf was checked as a tamper-evidence signal. CT inclusion does not by itself make a certificate compliant — it is neither a protocol version nor an issuer-trust decision — but its absence on a publicly reachable staging endpoint would be a flag worth a follow-up outside this review's transport remit.

Truststore management on the staging side of mariner-feature-flags matters for mutual TLS. Where the endpoint demands a client certificate, the set of client anchors it accepts is an operational concern for team-platform; the review records only whether a client certificate was presented and validated, leaving truststore curation to the owning team's runbooks.

Mutual TLS expectations for mariner-feature-flags follow the environment. The production trust boundary requires a client certificate; a non-production surface is not penalised for the absence of one. Where mariner-feature-flags is expected to present a client certificate and the capture shows none, the gap is a protocol-level finding unless a waiver of the matching kind and scope is in force.

ALPN negotiation at mariner-feature-flags was noted to confirm the application protocol riding over the tunnel, but protocol-version policy is enforced at the TLS layer and does not bend to the application above it. A modern application protocol over a legacy transport is still a transport finding for mariner-feature-flags.

Finally, mariner-feature-flags was checked for consistency between its environment label and its exposure. A service labelled staging is assessed under the rules for that environment; the review does not reclassify a surface to soften a finding, and team-platform retains the route to reclassification through inventory governance rather than through this review.

The harness recorded the mariner-feature-flags endpoint over successive sweeps; only the most recent capture per service is treated as authoritative, since earlier sweeps frequently predate a remediation or a re-issue. Reviewers are reminded that the captured negotiation outcomes, the chain-validation result, and the leaf fingerprint seen on the wire are held in the inventory database and must be read from there, not inferred from this narrative.

Revocation freshness was considered for mariner-feature-flags. The review notes whether the endpoint's stapled status was recent and whether the validating party had a live path to revocation information, but treats stapling hygiene as advisory this cycle; the governing chain question remains whether the presented chain validated to a trusted anchor at capture time.

Where mariner-feature-flags terminates TLS at a sidecar or a shared load balancer rather than in the application process, the review attributes the captured posture to the service as exposed on https://feature-flags.staging.mariner.internal. Termination topology is an implementation detail; the obligation to meet policy attaches to the exposed staging surface regardless of which component holds the key.

Encrypted-client-hello readiness for mariner-feature-flags was recorded as informational. ECH changes what an on-path observer can see about the handshake to https://feature-flags.staging.mariner.internal but does not alter any graded axis here; it neither relaxes the protocol floor nor changes how a client certificate or a chain is judged.

Ownership context: team-platform maintains mariner-feature-flags and is the counterparty for any remediation. The review records owning teams so that rotation and re-issuance work lands with the group that can actually schedule a maintenance window on the staging surface, but ownership confers no relief from policy.

### svc-025 — mariner-batch-scheduler

Clock discipline was assumed but noted for mariner-batch-scheduler: certificate validity windows are only meaningful if the validating hosts agree on the time. The review reasons about not-after relative to a single fixed review date, which removes any ambiguity that wall-clock skew on individual probers might otherwise introduce into the near-expiry judgement.

The protocol floor matters for mariner-batch-scheduler because a single tolerated downgrade becomes a precedent. The review treats any negotiated version outside the allowed set as a finding in every environment, including development, so that a sandbox habit does not migrate into production by copy-paste.

Exception status. mariner-batch-scheduler (svc-025) holds waiver WV-2026-025, a transport-protocol exception scoped to the service's entire footprint across every environment. The register shows it granted on 2026-03-05 with a nominal expiry of 2026-07-12. The register carries WV-2026-025 as granted and in force as written; whether it still provides cover at review time is a separate question, settled by reading the policy review date against the recorded expiry, and by checking that the scope actually reaches the prod surface under assessment.

Transport strictness headers on responses from mariner-batch-scheduler were observed where applicable. Strict-transport signalling reduces downgrade opportunity for browser clients but does not substitute for the server-side protocol floor; the review credits it as defence in depth and nothing more for a prod surface.

Subject-alternative-name coverage on mariner-batch-scheduler's leaf was checked against the hostnames https://batch-scheduler.prod.mariner.internal actually answers for. A name not covered by the served certificate would surface as a verification failure in the capture, so SAN gaps tend to show up indirectly through the recorded verification outcome rather than as a separate graded axis.

For mariner-batch-scheduler, issuer trust is a policy question settled against the maintained anchor set rather than the popularity of a commercial authority. The specific issuer and key parameters of mariner-batch-scheduler's certificate of record are carried in the inventory database; what matters to the review is whether that issuer sits inside the governed anchor set, since a leaf that validates today but chains outside the set is still a rotation candidate on governance grounds.

Cipher-suite selection at mariner-batch-scheduler was inspected for obviously deprecated constructions. While suite negotiation is not itself a graded axis in this review, a modern protocol version on https://batch-scheduler.prod.mariner.internal strongly constrains the suite space, which is part of why the version allow-list does so much of the work and why a downgrade is treated as consequential rather than cosmetic.

Partner-facing exposure was a specific consideration for mariner-batch-scheduler where federated third parties consume it. Federation raises the stakes of a mutual-TLS gap because the counterparty's assurance depends on it, which is why a production federation surface is held to the client-authentication expectation without sympathy for integration convenience.

Early-data exposure for mariner-batch-scheduler was considered where 0-RTT resumption is enabled. Replayable early data is an application-layer hazard rather than a transport-policy axis, so it does not move mariner-batch-scheduler's disposition, but it is flagged for team-batch as a design note to weigh against the latency benefit on the prod surface.

The mariner-batch-scheduler interconnect was modelled as part of the broader dependency graph. A weakness here propagates to every caller that trusts this endpoint, which is why the review resists the temptation to treat dispatches and tracks recurring batch jobs across the fleet as a low-stakes carve-out. The posture is assessed on its own merits and against the same bar as the busiest production path.

Certificate-transparency presence for mariner-batch-scheduler's leaf was checked as a tamper-evidence signal. CT inclusion does not by itself make a certificate compliant — it is neither a protocol version nor an issuer-trust decision — but its absence on a publicly reachable prod endpoint would be a flag worth a follow-up outside this review's transport remit.

Truststore management on the prod side of mariner-batch-scheduler matters for mutual TLS. Where the endpoint demands a client certificate, the set of client anchors it accepts is an operational concern for team-batch; the review records only whether a client certificate was presented and validated, leaving truststore curation to the owning team's runbooks.

Mutual TLS expectations for mariner-batch-scheduler follow the environment. The production trust boundary requires a client certificate; a non-production surface is not penalised for the absence of one. Where mariner-batch-scheduler is expected to present a client certificate and the capture shows none, the gap is a protocol-level finding unless a waiver of the matching kind and scope is in force.

ALPN negotiation at mariner-batch-scheduler was noted to confirm the application protocol riding over the tunnel, but protocol-version policy is enforced at the TLS layer and does not bend to the application above it. A modern application protocol over a legacy transport is still a transport finding for mariner-batch-scheduler.

Finally, mariner-batch-scheduler was checked for consistency between its environment label and its exposure. A service labelled prod is assessed under the rules for that environment; the review does not reclassify a surface to soften a finding, and team-batch retains the route to reclassification through inventory governance rather than through this review.

The harness recorded the mariner-batch-scheduler endpoint over successive sweeps; only the most recent capture per service is treated as authoritative, since earlier sweeps frequently predate a remediation or a re-issue. Reviewers are reminded that the captured negotiation outcomes, the chain-validation result, and the leaf fingerprint seen on the wire are held in the inventory database and must be read from there, not inferred from this narrative.

Revocation freshness was considered for mariner-batch-scheduler. The review notes whether the endpoint's stapled status was recent and whether the validating party had a live path to revocation information, but treats stapling hygiene as advisory this cycle; the governing chain question remains whether the presented chain validated to a trusted anchor at capture time.

Where mariner-batch-scheduler terminates TLS at a sidecar or a shared load balancer rather than in the application process, the review attributes the captured posture to the service as exposed on https://batch-scheduler.prod.mariner.internal. Termination topology is an implementation detail; the obligation to meet policy attaches to the exposed prod surface regardless of which component holds the key.

Encrypted-client-hello readiness for mariner-batch-scheduler was recorded as informational. ECH changes what an on-path observer can see about the handshake to https://batch-scheduler.prod.mariner.internal but does not alter any graded axis here; it neither relaxes the protocol floor nor changes how a client certificate or a chain is judged.

Ownership context: team-batch maintains mariner-batch-scheduler and is the counterparty for any remediation. The review records owning teams so that rotation and re-issuance work lands with the group that can actually schedule a maintenance window on the prod surface, but ownership confers no relief from policy.

Cross-signing arrangements that touch mariner-batch-scheduler's issuer were enumerated to make sure the chain the review reasons about is the chain clients actually build. A leaf can validate via more than one path; the governed question for mariner-batch-scheduler is whether the issuer of record sits in the trust anchor set, independent of which cross-signed path a particular client happens to choose.

Renewal automation for mariner-batch-scheduler was reviewed at the level of 'does a pipeline exist', not 'did it run'. An ACME-style renewal loop lowers the operational cost of the rotation findings this review may raise, but the disposition is taken from the captured state of https://batch-scheduler.prod.mariner.internal, so a renewal that is configured but not yet effective does not pre-empt a near-expiry finding.

Certificate lifetime is the other half of hygiene. A leaf approaching its not-after boundary inside the rotation window is scheduled for replacement well ahead of the cliff, on the principle that a lapse on the prod surface is an availability incident as much as a security one. The window is uniform across services so that nothing in mariner-batch-scheduler's profile earns special treatment.

SNI and virtual-host disambiguation were verified for mariner-batch-scheduler so that the captured leaf is unambiguously the one https://batch-scheduler.prod.mariner.internal intends to serve. A mismatch between the requested name and the served certificate would itself be an integrity concern, which is one more reason the observed fingerprint is compared against the inventory of record rather than assumed.

The review explicitly separated configuration intent from observed behaviour for mariner-batch-scheduler. A configuration file may declare a strict posture, but if the captured evidence on https://batch-scheduler.prod.mariner.internal shows otherwise, the evidence governs the finding; conversely a permissive-looking configuration that nonetheless negotiated within policy is judged on what actually happened on the wire.

Within the review boundary, mariner-batch-scheduler (svc-025) dispatches and tracks recurring batch jobs across the fleet. It is owned by team-batch and presents on https://batch-scheduler.prod.mariner.internal, which the inventory classifies as a prod surface. The transport posture of any prod endpoint is weighed against the operative policy rather than against historical convention, and the assessment proceeds from the evidence of record rather than from operator attestation.

Documentation for mariner-batch-scheduler was cross-checked against the configuration set. Where a policy value is needed — the rotation window, the protocol allow-list, the key floors, or the issuer anchor set — it is read from the validated configuration rather than from this prose, which paraphrases policy for the reader's convenience only.

For mesh participants such as mariner-batch-scheduler, certificate rotation is automated through the issuing control plane, which lowers the cost of a rotation finding but does not remove the obligation: an automated rotation that has not yet run still leaves a soon-to-expire leaf on https://batch-scheduler.prod.mariner.internal, and the review grades the state at capture time, not the intention encoded in automation.

Revocation-list distribution touching mariner-batch-scheduler's issuer was sanity-checked so that a client choosing CRL over stapled status still has a path. As with stapling, the review treats CRL reachability as advisory this cycle; the governing question for mariner-batch-scheduler remains whether the presented chain validated at capture time.

Evidence handling for mariner-batch-scheduler is deliberately conservative. When the fingerprint observed on the wire disagrees with the inventory of record, the review does not attempt to reconcile the two in the agent's favour; the disagreement is itself the finding, and it is escalated rather than waived, regardless of any paperwork that might otherwise have applied.

Key-ceremony provenance for mariner-batch-scheduler's material was reviewed at a high level. Where team-batch can attest that the private key was generated and held in a hardware security module, the operational risk of the key is lower, but provenance does not raise an under-strength key above the floor or extend a certificate past its not-after date.

Wildcard usage at mariner-batch-scheduler was noted where present. A wildcard leaf broadens blast radius if its key is compromised, so although a wildcard is not itself a finding, it raises the priority of the hygiene rules for mariner-batch-scheduler — a near-expiry or under-strength wildcard is a rotation the review would rather see scheduled sooner than later.

Key strength for mariner-batch-scheduler is judged against the floor for its algorithm family. The review does not grade keys on a curve: a key below the floor is a rotation finding irrespective of the sensitivity of the workload, because under-strength material weakens the whole interconnect graph that mariner-batch-scheduler participates in.

Session resumption behaviour for mariner-batch-scheduler was characterised so that repeat captures could be compared fairly. Resumption can mask a renegotiated parameter, so the harness records full-handshake outcomes where it can; the authoritative capture for mariner-batch-scheduler is still the most recent row, and resumption never changes which row is current.

Audit retention for mariner-batch-scheduler's captures follows the standard schedule: every sweep is retained, and the review reads the latest. This matters when reconstructing a finding months later — the row that was current at review time is identifiable by its capture timestamp, and the reconstruction must use that row rather than whatever happens to be newest at reconstruction time.

Certificate pinning by clients of mariner-batch-scheduler was inventoried lightly, because pinning interacts badly with rotation: a pinned client can break when mariner-batch-scheduler legitimately rotates. The review's rotation findings therefore come with a reminder that any pin held against mariner-batch-scheduler's current leaf must be updated in lockstep with the re-issue.

Operationally, mariner-batch-scheduler has been stable, but stability is not conformance. The review separates 'has not failed yet' from 'meets policy today', and it is the latter that governs the finding. Where the captured evidence and the live configuration disagree, the captured evidence is taken as the ground truth.

Forward-looking, the review recorded whether mariner-batch-scheduler is on a path toward post-quantum-ready key exchange. This cycle treats PQC readiness as informational; it changes no disposition, but it is captured so that team-batch can sequence the work against the rotation cadence the hygiene rules already impose.

### svc-026 — mariner-export-gateway

Ownership context: team-data maintains mariner-export-gateway and is the counterparty for any remediation. The review records owning teams so that rotation and re-issuance work lands with the group that can actually schedule a maintenance window on the prod surface, but ownership confers no relief from policy.

Cross-signing arrangements that touch mariner-export-gateway's issuer were enumerated to make sure the chain the review reasons about is the chain clients actually build. A leaf can validate via more than one path; the governed question for mariner-export-gateway is whether the issuer of record sits in the trust anchor set, independent of which cross-signed path a particular client happens to choose.

Renewal automation for mariner-export-gateway was reviewed at the level of 'does a pipeline exist', not 'did it run'. An ACME-style renewal loop lowers the operational cost of the rotation findings this review may raise, but the disposition is taken from the captured state of https://export-gateway.prod.mariner.internal, so a renewal that is configured but not yet effective does not pre-empt a near-expiry finding.

Exception status. mariner-export-gateway (svc-026) holds waiver WV-2026-026, a mutual-TLS exception scoped to the production listener only. The register shows it granted on 2026-02-20 with a nominal expiry of 2026-07-08. The register carries WV-2026-026 as granted and in force as written; whether it still provides cover at review time is a separate question, settled by reading the policy review date against the recorded expiry, and by checking that the scope actually reaches the prod surface under assessment.

Certificate lifetime is the other half of hygiene. A leaf approaching its not-after boundary inside the rotation window is scheduled for replacement well ahead of the cliff, on the principle that a lapse on the prod surface is an availability incident as much as a security one. The window is uniform across services so that nothing in mariner-export-gateway's profile earns special treatment.

SNI and virtual-host disambiguation were verified for mariner-export-gateway so that the captured leaf is unambiguously the one https://export-gateway.prod.mariner.internal intends to serve. A mismatch between the requested name and the served certificate would itself be an integrity concern, which is one more reason the observed fingerprint is compared against the inventory of record rather than assumed.

The review explicitly separated configuration intent from observed behaviour for mariner-export-gateway. A configuration file may declare a strict posture, but if the captured evidence on https://export-gateway.prod.mariner.internal shows otherwise, the evidence governs the finding; conversely a permissive-looking configuration that nonetheless negotiated within policy is judged on what actually happened on the wire.

Within the review boundary, mariner-export-gateway (svc-026) streams bulk data extracts to downstream consumers. It is owned by team-data and presents on https://export-gateway.prod.mariner.internal, which the inventory classifies as a prod surface. The transport posture of any prod endpoint is weighed against the operative policy rather than against historical convention, and the assessment proceeds from the evidence of record rather than from operator attestation.

Documentation for mariner-export-gateway was cross-checked against the configuration set. Where a policy value is needed — the rotation window, the protocol allow-list, the key floors, or the issuer anchor set — it is read from the validated configuration rather than from this prose, which paraphrases policy for the reader's convenience only.

For mesh participants such as mariner-export-gateway, certificate rotation is automated through the issuing control plane, which lowers the cost of a rotation finding but does not remove the obligation: an automated rotation that has not yet run still leaves a soon-to-expire leaf on https://export-gateway.prod.mariner.internal, and the review grades the state at capture time, not the intention encoded in automation.

Revocation-list distribution touching mariner-export-gateway's issuer was sanity-checked so that a client choosing CRL over stapled status still has a path. As with stapling, the review treats CRL reachability as advisory this cycle; the governing question for mariner-export-gateway remains whether the presented chain validated at capture time.

Evidence handling for mariner-export-gateway is deliberately conservative. When the fingerprint observed on the wire disagrees with the inventory of record, the review does not attempt to reconcile the two in the agent's favour; the disagreement is itself the finding, and it is escalated rather than waived, regardless of any paperwork that might otherwise have applied.

Key-ceremony provenance for mariner-export-gateway's material was reviewed at a high level. Where team-data can attest that the private key was generated and held in a hardware security module, the operational risk of the key is lower, but provenance does not raise an under-strength key above the floor or extend a certificate past its not-after date.

Wildcard usage at mariner-export-gateway was noted where present. A wildcard leaf broadens blast radius if its key is compromised, so although a wildcard is not itself a finding, it raises the priority of the hygiene rules for mariner-export-gateway — a near-expiry or under-strength wildcard is a rotation the review would rather see scheduled sooner than later.

Key strength for mariner-export-gateway is judged against the floor for its algorithm family. The review does not grade keys on a curve: a key below the floor is a rotation finding irrespective of the sensitivity of the workload, because under-strength material weakens the whole interconnect graph that mariner-export-gateway participates in.

Session resumption behaviour for mariner-export-gateway was characterised so that repeat captures could be compared fairly. Resumption can mask a renegotiated parameter, so the harness records full-handshake outcomes where it can; the authoritative capture for mariner-export-gateway is still the most recent row, and resumption never changes which row is current.

Audit retention for mariner-export-gateway's captures follows the standard schedule: every sweep is retained, and the review reads the latest. This matters when reconstructing a finding months later — the row that was current at review time is identifiable by its capture timestamp, and the reconstruction must use that row rather than whatever happens to be newest at reconstruction time.

Certificate pinning by clients of mariner-export-gateway was inventoried lightly, because pinning interacts badly with rotation: a pinned client can break when mariner-export-gateway legitimately rotates. The review's rotation findings therefore come with a reminder that any pin held against mariner-export-gateway's current leaf must be updated in lockstep with the re-issue.

Operationally, mariner-export-gateway has been stable, but stability is not conformance. The review separates 'has not failed yet' from 'meets policy today', and it is the latter that governs the finding. Where the captured evidence and the live configuration disagree, the captured evidence is taken as the ground truth.

Forward-looking, the review recorded whether mariner-export-gateway is on a path toward post-quantum-ready key exchange. This cycle treats PQC readiness as informational; it changes no disposition, but it is captured so that team-data can sequence the work against the rotation cadence the hygiene rules already impose.

Clock discipline was assumed but noted for mariner-export-gateway: certificate validity windows are only meaningful if the validating hosts agree on the time. The review reasons about not-after relative to a single fixed review date, which removes any ambiguity that wall-clock skew on individual probers might otherwise introduce into the near-expiry judgement.

The protocol floor matters for mariner-export-gateway because a single tolerated downgrade becomes a precedent. The review treats any negotiated version outside the allowed set as a finding in every environment, including development, so that a sandbox habit does not migrate into production by copy-paste.

Transport strictness headers on responses from mariner-export-gateway were observed where applicable. Strict-transport signalling reduces downgrade opportunity for browser clients but does not substitute for the server-side protocol floor; the review credits it as defence in depth and nothing more for a prod surface.

Subject-alternative-name coverage on mariner-export-gateway's leaf was checked against the hostnames https://export-gateway.prod.mariner.internal actually answers for. A name not covered by the served certificate would surface as a verification failure in the capture, so SAN gaps tend to show up indirectly through the recorded verification outcome rather than as a separate graded axis.

For mariner-export-gateway, issuer trust is a policy question settled against the maintained anchor set rather than the popularity of a commercial authority. The specific issuer and key parameters of mariner-export-gateway's certificate of record are carried in the inventory database; what matters to the review is whether that issuer sits inside the governed anchor set, since a leaf that validates today but chains outside the set is still a rotation candidate on governance grounds.

Cipher-suite selection at mariner-export-gateway was inspected for obviously deprecated constructions. While suite negotiation is not itself a graded axis in this review, a modern protocol version on https://export-gateway.prod.mariner.internal strongly constrains the suite space, which is part of why the version allow-list does so much of the work and why a downgrade is treated as consequential rather than cosmetic.

Partner-facing exposure was a specific consideration for mariner-export-gateway where federated third parties consume it. Federation raises the stakes of a mutual-TLS gap because the counterparty's assurance depends on it, which is why a production federation surface is held to the client-authentication expectation without sympathy for integration convenience.

Early-data exposure for mariner-export-gateway was considered where 0-RTT resumption is enabled. Replayable early data is an application-layer hazard rather than a transport-policy axis, so it does not move mariner-export-gateway's disposition, but it is flagged for team-data as a design note to weigh against the latency benefit on the prod surface.

The mariner-export-gateway interconnect was modelled as part of the broader dependency graph. A weakness here propagates to every caller that trusts this endpoint, which is why the review resists the temptation to treat streams bulk data extracts to downstream consumers as a low-stakes carve-out. The posture is assessed on its own merits and against the same bar as the busiest production path.

Certificate-transparency presence for mariner-export-gateway's leaf was checked as a tamper-evidence signal. CT inclusion does not by itself make a certificate compliant — it is neither a protocol version nor an issuer-trust decision — but its absence on a publicly reachable prod endpoint would be a flag worth a follow-up outside this review's transport remit.

Truststore management on the prod side of mariner-export-gateway matters for mutual TLS. Where the endpoint demands a client certificate, the set of client anchors it accepts is an operational concern for team-data; the review records only whether a client certificate was presented and validated, leaving truststore curation to the owning team's runbooks.

Mutual TLS expectations for mariner-export-gateway follow the environment. The production trust boundary requires a client certificate; a non-production surface is not penalised for the absence of one. Where mariner-export-gateway is expected to present a client certificate and the capture shows none, the gap is a protocol-level finding unless a waiver of the matching kind and scope is in force.

ALPN negotiation at mariner-export-gateway was noted to confirm the application protocol riding over the tunnel, but protocol-version policy is enforced at the TLS layer and does not bend to the application above it. A modern application protocol over a legacy transport is still a transport finding for mariner-export-gateway.

Finally, mariner-export-gateway was checked for consistency between its environment label and its exposure. A service labelled prod is assessed under the rules for that environment; the review does not reclassify a surface to soften a finding, and team-data retains the route to reclassification through inventory governance rather than through this review.

The harness recorded the mariner-export-gateway endpoint over successive sweeps; only the most recent capture per service is treated as authoritative, since earlier sweeps frequently predate a remediation or a re-issue. Reviewers are reminded that the captured negotiation outcomes, the chain-validation result, and the leaf fingerprint seen on the wire are held in the inventory database and must be read from there, not inferred from this narrative.

Revocation freshness was considered for mariner-export-gateway. The review notes whether the endpoint's stapled status was recent and whether the validating party had a live path to revocation information, but treats stapling hygiene as advisory this cycle; the governing chain question remains whether the presented chain validated to a trusted anchor at capture time.

Where mariner-export-gateway terminates TLS at a sidecar or a shared load balancer rather than in the application process, the review attributes the captured posture to the service as exposed on https://export-gateway.prod.mariner.internal. Termination topology is an implementation detail; the obligation to meet policy attaches to the exposed prod surface regardless of which component holds the key.

Encrypted-client-hello readiness for mariner-export-gateway was recorded as informational. ECH changes what an on-path observer can see about the handshake to https://export-gateway.prod.mariner.internal but does not alter any graded axis here; it neither relaxes the protocol floor nor changes how a client certificate or a chain is judged.

### svc-027 — mariner-archive-store

Forward-looking, the review recorded whether mariner-archive-store is on a path toward post-quantum-ready key exchange. This cycle treats PQC readiness as informational; it changes no disposition, but it is captured so that team-storage can sequence the work against the rotation cadence the hygiene rules already impose.

Exception status. mariner-archive-store (svc-027) holds waiver WV-2026-027, a transport-protocol exception scoped to the service's entire footprint across every environment. The register shows it granted on 2026-03-15 with a nominal expiry of 2026-07-05. The register carries WV-2026-027 as granted and in force as written; whether it still provides cover at review time is a separate question, settled by reading the policy review date against the recorded expiry, and by checking that the scope actually reaches the prod surface under assessment.

Clock discipline was assumed but noted for mariner-archive-store: certificate validity windows are only meaningful if the validating hosts agree on the time. The review reasons about not-after relative to a single fixed review date, which removes any ambiguity that wall-clock skew on individual probers might otherwise introduce into the near-expiry judgement.

The protocol floor matters for mariner-archive-store because a single tolerated downgrade becomes a precedent. The review treats any negotiated version outside the allowed set as a finding in every environment, including development, so that a sandbox habit does not migrate into production by copy-paste.

Transport strictness headers on responses from mariner-archive-store were observed where applicable. Strict-transport signalling reduces downgrade opportunity for browser clients but does not substitute for the server-side protocol floor; the review credits it as defence in depth and nothing more for a prod surface.

Subject-alternative-name coverage on mariner-archive-store's leaf was checked against the hostnames https://archive-store.prod.mariner.internal actually answers for. A name not covered by the served certificate would surface as a verification failure in the capture, so SAN gaps tend to show up indirectly through the recorded verification outcome rather than as a separate graded axis.

For mariner-archive-store, issuer trust is a policy question settled against the maintained anchor set rather than the popularity of a commercial authority. The specific issuer and key parameters of mariner-archive-store's certificate of record are carried in the inventory database; what matters to the review is whether that issuer sits inside the governed anchor set, since a leaf that validates today but chains outside the set is still a rotation candidate on governance grounds.

Cipher-suite selection at mariner-archive-store was inspected for obviously deprecated constructions. While suite negotiation is not itself a graded axis in this review, a modern protocol version on https://archive-store.prod.mariner.internal strongly constrains the suite space, which is part of why the version allow-list does so much of the work and why a downgrade is treated as consequential rather than cosmetic.

Partner-facing exposure was a specific consideration for mariner-archive-store where federated third parties consume it. Federation raises the stakes of a mutual-TLS gap because the counterparty's assurance depends on it, which is why a production federation surface is held to the client-authentication expectation without sympathy for integration convenience.

Early-data exposure for mariner-archive-store was considered where 0-RTT resumption is enabled. Replayable early data is an application-layer hazard rather than a transport-policy axis, so it does not move mariner-archive-store's disposition, but it is flagged for team-storage as a design note to weigh against the latency benefit on the prod surface.

The mariner-archive-store interconnect was modelled as part of the broader dependency graph. A weakness here propagates to every caller that trusts this endpoint, which is why the review resists the temptation to treat retains cold records under the long-term retention policy as a low-stakes carve-out. The posture is assessed on its own merits and against the same bar as the busiest production path.

Certificate-transparency presence for mariner-archive-store's leaf was checked as a tamper-evidence signal. CT inclusion does not by itself make a certificate compliant — it is neither a protocol version nor an issuer-trust decision — but its absence on a publicly reachable prod endpoint would be a flag worth a follow-up outside this review's transport remit.

Truststore management on the prod side of mariner-archive-store matters for mutual TLS. Where the endpoint demands a client certificate, the set of client anchors it accepts is an operational concern for team-storage; the review records only whether a client certificate was presented and validated, leaving truststore curation to the owning team's runbooks.

Mutual TLS expectations for mariner-archive-store follow the environment. The production trust boundary requires a client certificate; a non-production surface is not penalised for the absence of one. Where mariner-archive-store is expected to present a client certificate and the capture shows none, the gap is a protocol-level finding unless a waiver of the matching kind and scope is in force.

ALPN negotiation at mariner-archive-store was noted to confirm the application protocol riding over the tunnel, but protocol-version policy is enforced at the TLS layer and does not bend to the application above it. A modern application protocol over a legacy transport is still a transport finding for mariner-archive-store.

Finally, mariner-archive-store was checked for consistency between its environment label and its exposure. A service labelled prod is assessed under the rules for that environment; the review does not reclassify a surface to soften a finding, and team-storage retains the route to reclassification through inventory governance rather than through this review.

The harness recorded the mariner-archive-store endpoint over successive sweeps; only the most recent capture per service is treated as authoritative, since earlier sweeps frequently predate a remediation or a re-issue. Reviewers are reminded that the captured negotiation outcomes, the chain-validation result, and the leaf fingerprint seen on the wire are held in the inventory database and must be read from there, not inferred from this narrative.

Revocation freshness was considered for mariner-archive-store. The review notes whether the endpoint's stapled status was recent and whether the validating party had a live path to revocation information, but treats stapling hygiene as advisory this cycle; the governing chain question remains whether the presented chain validated to a trusted anchor at capture time.

Where mariner-archive-store terminates TLS at a sidecar or a shared load balancer rather than in the application process, the review attributes the captured posture to the service as exposed on https://archive-store.prod.mariner.internal. Termination topology is an implementation detail; the obligation to meet policy attaches to the exposed prod surface regardless of which component holds the key.

Encrypted-client-hello readiness for mariner-archive-store was recorded as informational. ECH changes what an on-path observer can see about the handshake to https://archive-store.prod.mariner.internal but does not alter any graded axis here; it neither relaxes the protocol floor nor changes how a client certificate or a chain is judged.

Ownership context: team-storage maintains mariner-archive-store and is the counterparty for any remediation. The review records owning teams so that rotation and re-issuance work lands with the group that can actually schedule a maintenance window on the prod surface, but ownership confers no relief from policy.

Cross-signing arrangements that touch mariner-archive-store's issuer were enumerated to make sure the chain the review reasons about is the chain clients actually build. A leaf can validate via more than one path; the governed question for mariner-archive-store is whether the issuer of record sits in the trust anchor set, independent of which cross-signed path a particular client happens to choose.

Renewal automation for mariner-archive-store was reviewed at the level of 'does a pipeline exist', not 'did it run'. An ACME-style renewal loop lowers the operational cost of the rotation findings this review may raise, but the disposition is taken from the captured state of https://archive-store.prod.mariner.internal, so a renewal that is configured but not yet effective does not pre-empt a near-expiry finding.

Certificate lifetime is the other half of hygiene. A leaf approaching its not-after boundary inside the rotation window is scheduled for replacement well ahead of the cliff, on the principle that a lapse on the prod surface is an availability incident as much as a security one. The window is uniform across services so that nothing in mariner-archive-store's profile earns special treatment.

SNI and virtual-host disambiguation were verified for mariner-archive-store so that the captured leaf is unambiguously the one https://archive-store.prod.mariner.internal intends to serve. A mismatch between the requested name and the served certificate would itself be an integrity concern, which is one more reason the observed fingerprint is compared against the inventory of record rather than assumed.

The review explicitly separated configuration intent from observed behaviour for mariner-archive-store. A configuration file may declare a strict posture, but if the captured evidence on https://archive-store.prod.mariner.internal shows otherwise, the evidence governs the finding; conversely a permissive-looking configuration that nonetheless negotiated within policy is judged on what actually happened on the wire.

Within the review boundary, mariner-archive-store (svc-027) retains cold records under the long-term retention policy. It is owned by team-storage and presents on https://archive-store.prod.mariner.internal, which the inventory classifies as a prod surface. The transport posture of any prod endpoint is weighed against the operative policy rather than against historical convention, and the assessment proceeds from the evidence of record rather than from operator attestation.

Documentation for mariner-archive-store was cross-checked against the configuration set. Where a policy value is needed — the rotation window, the protocol allow-list, the key floors, or the issuer anchor set — it is read from the validated configuration rather than from this prose, which paraphrases policy for the reader's convenience only.

For mesh participants such as mariner-archive-store, certificate rotation is automated through the issuing control plane, which lowers the cost of a rotation finding but does not remove the obligation: an automated rotation that has not yet run still leaves a soon-to-expire leaf on https://archive-store.prod.mariner.internal, and the review grades the state at capture time, not the intention encoded in automation.

Revocation-list distribution touching mariner-archive-store's issuer was sanity-checked so that a client choosing CRL over stapled status still has a path. As with stapling, the review treats CRL reachability as advisory this cycle; the governing question for mariner-archive-store remains whether the presented chain validated at capture time.

Evidence handling for mariner-archive-store is deliberately conservative. When the fingerprint observed on the wire disagrees with the inventory of record, the review does not attempt to reconcile the two in the agent's favour; the disagreement is itself the finding, and it is escalated rather than waived, regardless of any paperwork that might otherwise have applied.

Key-ceremony provenance for mariner-archive-store's material was reviewed at a high level. Where team-storage can attest that the private key was generated and held in a hardware security module, the operational risk of the key is lower, but provenance does not raise an under-strength key above the floor or extend a certificate past its not-after date.

Wildcard usage at mariner-archive-store was noted where present. A wildcard leaf broadens blast radius if its key is compromised, so although a wildcard is not itself a finding, it raises the priority of the hygiene rules for mariner-archive-store — a near-expiry or under-strength wildcard is a rotation the review would rather see scheduled sooner than later.

Key strength for mariner-archive-store is judged against the floor for its algorithm family. The review does not grade keys on a curve: a key below the floor is a rotation finding irrespective of the sensitivity of the workload, because under-strength material weakens the whole interconnect graph that mariner-archive-store participates in.

Session resumption behaviour for mariner-archive-store was characterised so that repeat captures could be compared fairly. Resumption can mask a renegotiated parameter, so the harness records full-handshake outcomes where it can; the authoritative capture for mariner-archive-store is still the most recent row, and resumption never changes which row is current.

Audit retention for mariner-archive-store's captures follows the standard schedule: every sweep is retained, and the review reads the latest. This matters when reconstructing a finding months later — the row that was current at review time is identifiable by its capture timestamp, and the reconstruction must use that row rather than whatever happens to be newest at reconstruction time.

Certificate pinning by clients of mariner-archive-store was inventoried lightly, because pinning interacts badly with rotation: a pinned client can break when mariner-archive-store legitimately rotates. The review's rotation findings therefore come with a reminder that any pin held against mariner-archive-store's current leaf must be updated in lockstep with the re-issue.

Operationally, mariner-archive-store has been stable, but stability is not conformance. The review separates 'has not failed yet' from 'meets policy today', and it is the latter that governs the finding. Where the captured evidence and the live configuration disagree, the captured evidence is taken as the ground truth.

### svc-028 — mariner-quota-service

Encrypted-client-hello readiness for mariner-quota-service was recorded as informational. ECH changes what an on-path observer can see about the handshake to https://quota-service.prod.mariner.internal but does not alter any graded axis here; it neither relaxes the protocol floor nor changes how a client certificate or a chain is judged.

Ownership context: team-platform maintains mariner-quota-service and is the counterparty for any remediation. The review records owning teams so that rotation and re-issuance work lands with the group that can actually schedule a maintenance window on the prod surface, but ownership confers no relief from policy.

Exception status. mariner-quota-service (svc-028) holds waiver WV-2026-028, a mutual-TLS exception scoped to the service's entire footprint across every environment. The register shows it granted on 2026-02-01 with a nominal expiry of 2026-12-01. The register carries WV-2026-028 as granted and in force as written; whether it still provides cover at review time is a separate question, settled by reading the policy review date against the recorded expiry, and by checking that the scope actually reaches the prod surface under assessment.

Cross-signing arrangements that touch mariner-quota-service's issuer were enumerated to make sure the chain the review reasons about is the chain clients actually build. A leaf can validate via more than one path; the governed question for mariner-quota-service is whether the issuer of record sits in the trust anchor set, independent of which cross-signed path a particular client happens to choose.

Renewal automation for mariner-quota-service was reviewed at the level of 'does a pipeline exist', not 'did it run'. An ACME-style renewal loop lowers the operational cost of the rotation findings this review may raise, but the disposition is taken from the captured state of https://quota-service.prod.mariner.internal, so a renewal that is configured but not yet effective does not pre-empt a near-expiry finding.

Certificate lifetime is the other half of hygiene. A leaf approaching its not-after boundary inside the rotation window is scheduled for replacement well ahead of the cliff, on the principle that a lapse on the prod surface is an availability incident as much as a security one. The window is uniform across services so that nothing in mariner-quota-service's profile earns special treatment.

SNI and virtual-host disambiguation were verified for mariner-quota-service so that the captured leaf is unambiguously the one https://quota-service.prod.mariner.internal intends to serve. A mismatch between the requested name and the served certificate would itself be an integrity concern, which is one more reason the observed fingerprint is compared against the inventory of record rather than assumed.

The review explicitly separated configuration intent from observed behaviour for mariner-quota-service. A configuration file may declare a strict posture, but if the captured evidence on https://quota-service.prod.mariner.internal shows otherwise, the evidence governs the finding; conversely a permissive-looking configuration that nonetheless negotiated within policy is judged on what actually happened on the wire.

Within the review boundary, mariner-quota-service (svc-028) enforces per-tenant rate and usage quotas at the edge. It is owned by team-platform and presents on https://quota-service.prod.mariner.internal, which the inventory classifies as a prod surface. The transport posture of any prod endpoint is weighed against the operative policy rather than against historical convention, and the assessment proceeds from the evidence of record rather than from operator attestation.

Documentation for mariner-quota-service was cross-checked against the configuration set. Where a policy value is needed — the rotation window, the protocol allow-list, the key floors, or the issuer anchor set — it is read from the validated configuration rather than from this prose, which paraphrases policy for the reader's convenience only.

For mesh participants such as mariner-quota-service, certificate rotation is automated through the issuing control plane, which lowers the cost of a rotation finding but does not remove the obligation: an automated rotation that has not yet run still leaves a soon-to-expire leaf on https://quota-service.prod.mariner.internal, and the review grades the state at capture time, not the intention encoded in automation.

Revocation-list distribution touching mariner-quota-service's issuer was sanity-checked so that a client choosing CRL over stapled status still has a path. As with stapling, the review treats CRL reachability as advisory this cycle; the governing question for mariner-quota-service remains whether the presented chain validated at capture time.

Evidence handling for mariner-quota-service is deliberately conservative. When the fingerprint observed on the wire disagrees with the inventory of record, the review does not attempt to reconcile the two in the agent's favour; the disagreement is itself the finding, and it is escalated rather than waived, regardless of any paperwork that might otherwise have applied.

Key-ceremony provenance for mariner-quota-service's material was reviewed at a high level. Where team-platform can attest that the private key was generated and held in a hardware security module, the operational risk of the key is lower, but provenance does not raise an under-strength key above the floor or extend a certificate past its not-after date.

Wildcard usage at mariner-quota-service was noted where present. A wildcard leaf broadens blast radius if its key is compromised, so although a wildcard is not itself a finding, it raises the priority of the hygiene rules for mariner-quota-service — a near-expiry or under-strength wildcard is a rotation the review would rather see scheduled sooner than later.

Key strength for mariner-quota-service is judged against the floor for its algorithm family. The review does not grade keys on a curve: a key below the floor is a rotation finding irrespective of the sensitivity of the workload, because under-strength material weakens the whole interconnect graph that mariner-quota-service participates in.

Session resumption behaviour for mariner-quota-service was characterised so that repeat captures could be compared fairly. Resumption can mask a renegotiated parameter, so the harness records full-handshake outcomes where it can; the authoritative capture for mariner-quota-service is still the most recent row, and resumption never changes which row is current.

Audit retention for mariner-quota-service's captures follows the standard schedule: every sweep is retained, and the review reads the latest. This matters when reconstructing a finding months later — the row that was current at review time is identifiable by its capture timestamp, and the reconstruction must use that row rather than whatever happens to be newest at reconstruction time.

Certificate pinning by clients of mariner-quota-service was inventoried lightly, because pinning interacts badly with rotation: a pinned client can break when mariner-quota-service legitimately rotates. The review's rotation findings therefore come with a reminder that any pin held against mariner-quota-service's current leaf must be updated in lockstep with the re-issue.

Operationally, mariner-quota-service has been stable, but stability is not conformance. The review separates 'has not failed yet' from 'meets policy today', and it is the latter that governs the finding. Where the captured evidence and the live configuration disagree, the captured evidence is taken as the ground truth.

Forward-looking, the review recorded whether mariner-quota-service is on a path toward post-quantum-ready key exchange. This cycle treats PQC readiness as informational; it changes no disposition, but it is captured so that team-platform can sequence the work against the rotation cadence the hygiene rules already impose.

Clock discipline was assumed but noted for mariner-quota-service: certificate validity windows are only meaningful if the validating hosts agree on the time. The review reasons about not-after relative to a single fixed review date, which removes any ambiguity that wall-clock skew on individual probers might otherwise introduce into the near-expiry judgement.

The protocol floor matters for mariner-quota-service because a single tolerated downgrade becomes a precedent. The review treats any negotiated version outside the allowed set as a finding in every environment, including development, so that a sandbox habit does not migrate into production by copy-paste.

Transport strictness headers on responses from mariner-quota-service were observed where applicable. Strict-transport signalling reduces downgrade opportunity for browser clients but does not substitute for the server-side protocol floor; the review credits it as defence in depth and nothing more for a prod surface.

Subject-alternative-name coverage on mariner-quota-service's leaf was checked against the hostnames https://quota-service.prod.mariner.internal actually answers for. A name not covered by the served certificate would surface as a verification failure in the capture, so SAN gaps tend to show up indirectly through the recorded verification outcome rather than as a separate graded axis.

For mariner-quota-service, issuer trust is a policy question settled against the maintained anchor set rather than the popularity of a commercial authority. The specific issuer and key parameters of mariner-quota-service's certificate of record are carried in the inventory database; what matters to the review is whether that issuer sits inside the governed anchor set, since a leaf that validates today but chains outside the set is still a rotation candidate on governance grounds.

Cipher-suite selection at mariner-quota-service was inspected for obviously deprecated constructions. While suite negotiation is not itself a graded axis in this review, a modern protocol version on https://quota-service.prod.mariner.internal strongly constrains the suite space, which is part of why the version allow-list does so much of the work and why a downgrade is treated as consequential rather than cosmetic.

Partner-facing exposure was a specific consideration for mariner-quota-service where federated third parties consume it. Federation raises the stakes of a mutual-TLS gap because the counterparty's assurance depends on it, which is why a production federation surface is held to the client-authentication expectation without sympathy for integration convenience.

Early-data exposure for mariner-quota-service was considered where 0-RTT resumption is enabled. Replayable early data is an application-layer hazard rather than a transport-policy axis, so it does not move mariner-quota-service's disposition, but it is flagged for team-platform as a design note to weigh against the latency benefit on the prod surface.

The mariner-quota-service interconnect was modelled as part of the broader dependency graph. A weakness here propagates to every caller that trusts this endpoint, which is why the review resists the temptation to treat enforces per-tenant rate and usage quotas at the edge as a low-stakes carve-out. The posture is assessed on its own merits and against the same bar as the busiest production path.

Certificate-transparency presence for mariner-quota-service's leaf was checked as a tamper-evidence signal. CT inclusion does not by itself make a certificate compliant — it is neither a protocol version nor an issuer-trust decision — but its absence on a publicly reachable prod endpoint would be a flag worth a follow-up outside this review's transport remit.

Truststore management on the prod side of mariner-quota-service matters for mutual TLS. Where the endpoint demands a client certificate, the set of client anchors it accepts is an operational concern for team-platform; the review records only whether a client certificate was presented and validated, leaving truststore curation to the owning team's runbooks.

Mutual TLS expectations for mariner-quota-service follow the environment. The production trust boundary requires a client certificate; a non-production surface is not penalised for the absence of one. Where mariner-quota-service is expected to present a client certificate and the capture shows none, the gap is a protocol-level finding unless a waiver of the matching kind and scope is in force.

ALPN negotiation at mariner-quota-service was noted to confirm the application protocol riding over the tunnel, but protocol-version policy is enforced at the TLS layer and does not bend to the application above it. A modern application protocol over a legacy transport is still a transport finding for mariner-quota-service.

Finally, mariner-quota-service was checked for consistency between its environment label and its exposure. A service labelled prod is assessed under the rules for that environment; the review does not reclassify a surface to soften a finding, and team-platform retains the route to reclassification through inventory governance rather than through this review.

The harness recorded the mariner-quota-service endpoint over successive sweeps; only the most recent capture per service is treated as authoritative, since earlier sweeps frequently predate a remediation or a re-issue. Reviewers are reminded that the captured negotiation outcomes, the chain-validation result, and the leaf fingerprint seen on the wire are held in the inventory database and must be read from there, not inferred from this narrative.

Revocation freshness was considered for mariner-quota-service. The review notes whether the endpoint's stapled status was recent and whether the validating party had a live path to revocation information, but treats stapling hygiene as advisory this cycle; the governing chain question remains whether the presented chain validated to a trusted anchor at capture time.

Where mariner-quota-service terminates TLS at a sidecar or a shared load balancer rather than in the application process, the review attributes the captured posture to the service as exposed on https://quota-service.prod.mariner.internal. Termination topology is an implementation detail; the obligation to meet policy attaches to the exposed prod surface regardless of which component holds the key.

### svc-029 — mariner-rate-limiter

Operationally, mariner-rate-limiter has been stable, but stability is not conformance. The review separates 'has not failed yet' from 'meets policy today', and it is the latter that governs the finding. Where the captured evidence and the live configuration disagree, the captured evidence is taken as the ground truth.

Forward-looking, the review recorded whether mariner-rate-limiter is on a path toward post-quantum-ready key exchange. This cycle treats PQC readiness as informational; it changes no disposition, but it is captured so that team-edge can sequence the work against the rotation cadence the hygiene rules already impose.

Clock discipline was assumed but noted for mariner-rate-limiter: certificate validity windows are only meaningful if the validating hosts agree on the time. The review reasons about not-after relative to a single fixed review date, which removes any ambiguity that wall-clock skew on individual probers might otherwise introduce into the near-expiry judgement.

Exception status. mariner-rate-limiter (svc-029) holds waiver WV-2026-029, a transport-protocol exception scoped to the staging surface only. The register shows it granted on 2026-02-01 with a nominal expiry of 2026-12-01. The register carries WV-2026-029 as granted and in force as written; whether it still provides cover at review time is a separate question, settled by reading the policy review date against the recorded expiry, and by checking that the scope actually reaches the prod surface under assessment.

The protocol floor matters for mariner-rate-limiter because a single tolerated downgrade becomes a precedent. The review treats any negotiated version outside the allowed set as a finding in every environment, including development, so that a sandbox habit does not migrate into production by copy-paste.

Transport strictness headers on responses from mariner-rate-limiter were observed where applicable. Strict-transport signalling reduces downgrade opportunity for browser clients but does not substitute for the server-side protocol floor; the review credits it as defence in depth and nothing more for a prod surface.

Subject-alternative-name coverage on mariner-rate-limiter's leaf was checked against the hostnames https://rate-limiter.prod.mariner.internal actually answers for. A name not covered by the served certificate would surface as a verification failure in the capture, so SAN gaps tend to show up indirectly through the recorded verification outcome rather than as a separate graded axis.

For mariner-rate-limiter, issuer trust is a policy question settled against the maintained anchor set rather than the popularity of a commercial authority. The specific issuer and key parameters of mariner-rate-limiter's certificate of record are carried in the inventory database; what matters to the review is whether that issuer sits inside the governed anchor set, since a leaf that validates today but chains outside the set is still a rotation candidate on governance grounds.

Cipher-suite selection at mariner-rate-limiter was inspected for obviously deprecated constructions. While suite negotiation is not itself a graded axis in this review, a modern protocol version on https://rate-limiter.prod.mariner.internal strongly constrains the suite space, which is part of why the version allow-list does so much of the work and why a downgrade is treated as consequential rather than cosmetic.

Partner-facing exposure was a specific consideration for mariner-rate-limiter where federated third parties consume it. Federation raises the stakes of a mutual-TLS gap because the counterparty's assurance depends on it, which is why a production federation surface is held to the client-authentication expectation without sympathy for integration convenience.

Early-data exposure for mariner-rate-limiter was considered where 0-RTT resumption is enabled. Replayable early data is an application-layer hazard rather than a transport-policy axis, so it does not move mariner-rate-limiter's disposition, but it is flagged for team-edge as a design note to weigh against the latency benefit on the prod surface.

The mariner-rate-limiter interconnect was modelled as part of the broader dependency graph. A weakness here propagates to every caller that trusts this endpoint, which is why the review resists the temptation to treat shapes inbound request bursts ahead of the mesh as a low-stakes carve-out. The posture is assessed on its own merits and against the same bar as the busiest production path.

Certificate-transparency presence for mariner-rate-limiter's leaf was checked as a tamper-evidence signal. CT inclusion does not by itself make a certificate compliant — it is neither a protocol version nor an issuer-trust decision — but its absence on a publicly reachable prod endpoint would be a flag worth a follow-up outside this review's transport remit.

Truststore management on the prod side of mariner-rate-limiter matters for mutual TLS. Where the endpoint demands a client certificate, the set of client anchors it accepts is an operational concern for team-edge; the review records only whether a client certificate was presented and validated, leaving truststore curation to the owning team's runbooks.

Mutual TLS expectations for mariner-rate-limiter follow the environment. The production trust boundary requires a client certificate; a non-production surface is not penalised for the absence of one. Where mariner-rate-limiter is expected to present a client certificate and the capture shows none, the gap is a protocol-level finding unless a waiver of the matching kind and scope is in force.

ALPN negotiation at mariner-rate-limiter was noted to confirm the application protocol riding over the tunnel, but protocol-version policy is enforced at the TLS layer and does not bend to the application above it. A modern application protocol over a legacy transport is still a transport finding for mariner-rate-limiter.

Finally, mariner-rate-limiter was checked for consistency between its environment label and its exposure. A service labelled prod is assessed under the rules for that environment; the review does not reclassify a surface to soften a finding, and team-edge retains the route to reclassification through inventory governance rather than through this review.

The harness recorded the mariner-rate-limiter endpoint over successive sweeps; only the most recent capture per service is treated as authoritative, since earlier sweeps frequently predate a remediation or a re-issue. Reviewers are reminded that the captured negotiation outcomes, the chain-validation result, and the leaf fingerprint seen on the wire are held in the inventory database and must be read from there, not inferred from this narrative.

Revocation freshness was considered for mariner-rate-limiter. The review notes whether the endpoint's stapled status was recent and whether the validating party had a live path to revocation information, but treats stapling hygiene as advisory this cycle; the governing chain question remains whether the presented chain validated to a trusted anchor at capture time.

Where mariner-rate-limiter terminates TLS at a sidecar or a shared load balancer rather than in the application process, the review attributes the captured posture to the service as exposed on https://rate-limiter.prod.mariner.internal. Termination topology is an implementation detail; the obligation to meet policy attaches to the exposed prod surface regardless of which component holds the key.

Encrypted-client-hello readiness for mariner-rate-limiter was recorded as informational. ECH changes what an on-path observer can see about the handshake to https://rate-limiter.prod.mariner.internal but does not alter any graded axis here; it neither relaxes the protocol floor nor changes how a client certificate or a chain is judged.

Ownership context: team-edge maintains mariner-rate-limiter and is the counterparty for any remediation. The review records owning teams so that rotation and re-issuance work lands with the group that can actually schedule a maintenance window on the prod surface, but ownership confers no relief from policy.

Cross-signing arrangements that touch mariner-rate-limiter's issuer were enumerated to make sure the chain the review reasons about is the chain clients actually build. A leaf can validate via more than one path; the governed question for mariner-rate-limiter is whether the issuer of record sits in the trust anchor set, independent of which cross-signed path a particular client happens to choose.

Renewal automation for mariner-rate-limiter was reviewed at the level of 'does a pipeline exist', not 'did it run'. An ACME-style renewal loop lowers the operational cost of the rotation findings this review may raise, but the disposition is taken from the captured state of https://rate-limiter.prod.mariner.internal, so a renewal that is configured but not yet effective does not pre-empt a near-expiry finding.

Certificate lifetime is the other half of hygiene. A leaf approaching its not-after boundary inside the rotation window is scheduled for replacement well ahead of the cliff, on the principle that a lapse on the prod surface is an availability incident as much as a security one. The window is uniform across services so that nothing in mariner-rate-limiter's profile earns special treatment.

SNI and virtual-host disambiguation were verified for mariner-rate-limiter so that the captured leaf is unambiguously the one https://rate-limiter.prod.mariner.internal intends to serve. A mismatch between the requested name and the served certificate would itself be an integrity concern, which is one more reason the observed fingerprint is compared against the inventory of record rather than assumed.

The review explicitly separated configuration intent from observed behaviour for mariner-rate-limiter. A configuration file may declare a strict posture, but if the captured evidence on https://rate-limiter.prod.mariner.internal shows otherwise, the evidence governs the finding; conversely a permissive-looking configuration that nonetheless negotiated within policy is judged on what actually happened on the wire.

Within the review boundary, mariner-rate-limiter (svc-029) shapes inbound request bursts ahead of the mesh. It is owned by team-edge and presents on https://rate-limiter.prod.mariner.internal, which the inventory classifies as a prod surface. The transport posture of any prod endpoint is weighed against the operative policy rather than against historical convention, and the assessment proceeds from the evidence of record rather than from operator attestation.

Documentation for mariner-rate-limiter was cross-checked against the configuration set. Where a policy value is needed — the rotation window, the protocol allow-list, the key floors, or the issuer anchor set — it is read from the validated configuration rather than from this prose, which paraphrases policy for the reader's convenience only.

For mesh participants such as mariner-rate-limiter, certificate rotation is automated through the issuing control plane, which lowers the cost of a rotation finding but does not remove the obligation: an automated rotation that has not yet run still leaves a soon-to-expire leaf on https://rate-limiter.prod.mariner.internal, and the review grades the state at capture time, not the intention encoded in automation.

Revocation-list distribution touching mariner-rate-limiter's issuer was sanity-checked so that a client choosing CRL over stapled status still has a path. As with stapling, the review treats CRL reachability as advisory this cycle; the governing question for mariner-rate-limiter remains whether the presented chain validated at capture time.

Evidence handling for mariner-rate-limiter is deliberately conservative. When the fingerprint observed on the wire disagrees with the inventory of record, the review does not attempt to reconcile the two in the agent's favour; the disagreement is itself the finding, and it is escalated rather than waived, regardless of any paperwork that might otherwise have applied.

Key-ceremony provenance for mariner-rate-limiter's material was reviewed at a high level. Where team-edge can attest that the private key was generated and held in a hardware security module, the operational risk of the key is lower, but provenance does not raise an under-strength key above the floor or extend a certificate past its not-after date.

Wildcard usage at mariner-rate-limiter was noted where present. A wildcard leaf broadens blast radius if its key is compromised, so although a wildcard is not itself a finding, it raises the priority of the hygiene rules for mariner-rate-limiter — a near-expiry or under-strength wildcard is a rotation the review would rather see scheduled sooner than later.

Key strength for mariner-rate-limiter is judged against the floor for its algorithm family. The review does not grade keys on a curve: a key below the floor is a rotation finding irrespective of the sensitivity of the workload, because under-strength material weakens the whole interconnect graph that mariner-rate-limiter participates in.

Session resumption behaviour for mariner-rate-limiter was characterised so that repeat captures could be compared fairly. Resumption can mask a renegotiated parameter, so the harness records full-handshake outcomes where it can; the authoritative capture for mariner-rate-limiter is still the most recent row, and resumption never changes which row is current.

Audit retention for mariner-rate-limiter's captures follows the standard schedule: every sweep is retained, and the review reads the latest. This matters when reconstructing a finding months later — the row that was current at review time is identifiable by its capture timestamp, and the reconstruction must use that row rather than whatever happens to be newest at reconstruction time.

Certificate pinning by clients of mariner-rate-limiter was inventoried lightly, because pinning interacts badly with rotation: a pinned client can break when mariner-rate-limiter legitimately rotates. The review's rotation findings therefore come with a reminder that any pin held against mariner-rate-limiter's current leaf must be updated in lockstep with the re-issue.

### svc-030 — mariner-session-store

Where mariner-session-store terminates TLS at a sidecar or a shared load balancer rather than in the application process, the review attributes the captured posture to the service as exposed on https://session-store.prod.mariner.internal. Termination topology is an implementation detail; the obligation to meet policy attaches to the exposed prod surface regardless of which component holds the key.

Exception status. mariner-session-store (svc-030) holds waiver WV-2026-030, a transport-protocol exception scoped to the service's entire footprint across every environment. The register shows it granted on 2026-01-01 with a nominal expiry of 2026-12-20. The register carries WV-2026-030 as granted and in force as written; whether it still provides cover at review time is a separate question, settled by reading the policy review date against the recorded expiry, and by checking that the scope actually reaches the prod surface under assessment.

Encrypted-client-hello readiness for mariner-session-store was recorded as informational. ECH changes what an on-path observer can see about the handshake to https://session-store.prod.mariner.internal but does not alter any graded axis here; it neither relaxes the protocol floor nor changes how a client certificate or a chain is judged.

Ownership context: team-identity maintains mariner-session-store and is the counterparty for any remediation. The review records owning teams so that rotation and re-issuance work lands with the group that can actually schedule a maintenance window on the prod surface, but ownership confers no relief from policy.

Cross-signing arrangements that touch mariner-session-store's issuer were enumerated to make sure the chain the review reasons about is the chain clients actually build. A leaf can validate via more than one path; the governed question for mariner-session-store is whether the issuer of record sits in the trust anchor set, independent of which cross-signed path a particular client happens to choose.

Renewal automation for mariner-session-store was reviewed at the level of 'does a pipeline exist', not 'did it run'. An ACME-style renewal loop lowers the operational cost of the rotation findings this review may raise, but the disposition is taken from the captured state of https://session-store.prod.mariner.internal, so a renewal that is configured but not yet effective does not pre-empt a near-expiry finding.

Certificate lifetime is the other half of hygiene. A leaf approaching its not-after boundary inside the rotation window is scheduled for replacement well ahead of the cliff, on the principle that a lapse on the prod surface is an availability incident as much as a security one. The window is uniform across services so that nothing in mariner-session-store's profile earns special treatment.

SNI and virtual-host disambiguation were verified for mariner-session-store so that the captured leaf is unambiguously the one https://session-store.prod.mariner.internal intends to serve. A mismatch between the requested name and the served certificate would itself be an integrity concern, which is one more reason the observed fingerprint is compared against the inventory of record rather than assumed.

The review explicitly separated configuration intent from observed behaviour for mariner-session-store. A configuration file may declare a strict posture, but if the captured evidence on https://session-store.prod.mariner.internal shows otherwise, the evidence governs the finding; conversely a permissive-looking configuration that nonetheless negotiated within policy is judged on what actually happened on the wire.

Within the review boundary, mariner-session-store (svc-030) persists short-lived session state for the auth tier. It is owned by team-identity and presents on https://session-store.prod.mariner.internal, which the inventory classifies as a prod surface. The transport posture of any prod endpoint is weighed against the operative policy rather than against historical convention, and the assessment proceeds from the evidence of record rather than from operator attestation.

Documentation for mariner-session-store was cross-checked against the configuration set. Where a policy value is needed — the rotation window, the protocol allow-list, the key floors, or the issuer anchor set — it is read from the validated configuration rather than from this prose, which paraphrases policy for the reader's convenience only.

For mesh participants such as mariner-session-store, certificate rotation is automated through the issuing control plane, which lowers the cost of a rotation finding but does not remove the obligation: an automated rotation that has not yet run still leaves a soon-to-expire leaf on https://session-store.prod.mariner.internal, and the review grades the state at capture time, not the intention encoded in automation.

Revocation-list distribution touching mariner-session-store's issuer was sanity-checked so that a client choosing CRL over stapled status still has a path. As with stapling, the review treats CRL reachability as advisory this cycle; the governing question for mariner-session-store remains whether the presented chain validated at capture time.

Evidence handling for mariner-session-store is deliberately conservative. When the fingerprint observed on the wire disagrees with the inventory of record, the review does not attempt to reconcile the two in the agent's favour; the disagreement is itself the finding, and it is escalated rather than waived, regardless of any paperwork that might otherwise have applied.

Key-ceremony provenance for mariner-session-store's material was reviewed at a high level. Where team-identity can attest that the private key was generated and held in a hardware security module, the operational risk of the key is lower, but provenance does not raise an under-strength key above the floor or extend a certificate past its not-after date.

Wildcard usage at mariner-session-store was noted where present. A wildcard leaf broadens blast radius if its key is compromised, so although a wildcard is not itself a finding, it raises the priority of the hygiene rules for mariner-session-store — a near-expiry or under-strength wildcard is a rotation the review would rather see scheduled sooner than later.

Key strength for mariner-session-store is judged against the floor for its algorithm family. The review does not grade keys on a curve: a key below the floor is a rotation finding irrespective of the sensitivity of the workload, because under-strength material weakens the whole interconnect graph that mariner-session-store participates in.

Session resumption behaviour for mariner-session-store was characterised so that repeat captures could be compared fairly. Resumption can mask a renegotiated parameter, so the harness records full-handshake outcomes where it can; the authoritative capture for mariner-session-store is still the most recent row, and resumption never changes which row is current.

Audit retention for mariner-session-store's captures follows the standard schedule: every sweep is retained, and the review reads the latest. This matters when reconstructing a finding months later — the row that was current at review time is identifiable by its capture timestamp, and the reconstruction must use that row rather than whatever happens to be newest at reconstruction time.

Certificate pinning by clients of mariner-session-store was inventoried lightly, because pinning interacts badly with rotation: a pinned client can break when mariner-session-store legitimately rotates. The review's rotation findings therefore come with a reminder that any pin held against mariner-session-store's current leaf must be updated in lockstep with the re-issue.

Operationally, mariner-session-store has been stable, but stability is not conformance. The review separates 'has not failed yet' from 'meets policy today', and it is the latter that governs the finding. Where the captured evidence and the live configuration disagree, the captured evidence is taken as the ground truth.

Forward-looking, the review recorded whether mariner-session-store is on a path toward post-quantum-ready key exchange. This cycle treats PQC readiness as informational; it changes no disposition, but it is captured so that team-identity can sequence the work against the rotation cadence the hygiene rules already impose.

Clock discipline was assumed but noted for mariner-session-store: certificate validity windows are only meaningful if the validating hosts agree on the time. The review reasons about not-after relative to a single fixed review date, which removes any ambiguity that wall-clock skew on individual probers might otherwise introduce into the near-expiry judgement.

The protocol floor matters for mariner-session-store because a single tolerated downgrade becomes a precedent. The review treats any negotiated version outside the allowed set as a finding in every environment, including development, so that a sandbox habit does not migrate into production by copy-paste.

Transport strictness headers on responses from mariner-session-store were observed where applicable. Strict-transport signalling reduces downgrade opportunity for browser clients but does not substitute for the server-side protocol floor; the review credits it as defence in depth and nothing more for a prod surface.

Subject-alternative-name coverage on mariner-session-store's leaf was checked against the hostnames https://session-store.prod.mariner.internal actually answers for. A name not covered by the served certificate would surface as a verification failure in the capture, so SAN gaps tend to show up indirectly through the recorded verification outcome rather than as a separate graded axis.

For mariner-session-store, issuer trust is a policy question settled against the maintained anchor set rather than the popularity of a commercial authority. The specific issuer and key parameters of mariner-session-store's certificate of record are carried in the inventory database; what matters to the review is whether that issuer sits inside the governed anchor set, since a leaf that validates today but chains outside the set is still a rotation candidate on governance grounds.

Cipher-suite selection at mariner-session-store was inspected for obviously deprecated constructions. While suite negotiation is not itself a graded axis in this review, a modern protocol version on https://session-store.prod.mariner.internal strongly constrains the suite space, which is part of why the version allow-list does so much of the work and why a downgrade is treated as consequential rather than cosmetic.

Partner-facing exposure was a specific consideration for mariner-session-store where federated third parties consume it. Federation raises the stakes of a mutual-TLS gap because the counterparty's assurance depends on it, which is why a production federation surface is held to the client-authentication expectation without sympathy for integration convenience.

Early-data exposure for mariner-session-store was considered where 0-RTT resumption is enabled. Replayable early data is an application-layer hazard rather than a transport-policy axis, so it does not move mariner-session-store's disposition, but it is flagged for team-identity as a design note to weigh against the latency benefit on the prod surface.

The mariner-session-store interconnect was modelled as part of the broader dependency graph. A weakness here propagates to every caller that trusts this endpoint, which is why the review resists the temptation to treat persists short-lived session state for the auth tier as a low-stakes carve-out. The posture is assessed on its own merits and against the same bar as the busiest production path.

Certificate-transparency presence for mariner-session-store's leaf was checked as a tamper-evidence signal. CT inclusion does not by itself make a certificate compliant — it is neither a protocol version nor an issuer-trust decision — but its absence on a publicly reachable prod endpoint would be a flag worth a follow-up outside this review's transport remit.

Truststore management on the prod side of mariner-session-store matters for mutual TLS. Where the endpoint demands a client certificate, the set of client anchors it accepts is an operational concern for team-identity; the review records only whether a client certificate was presented and validated, leaving truststore curation to the owning team's runbooks.

Mutual TLS expectations for mariner-session-store follow the environment. The production trust boundary requires a client certificate; a non-production surface is not penalised for the absence of one. Where mariner-session-store is expected to present a client certificate and the capture shows none, the gap is a protocol-level finding unless a waiver of the matching kind and scope is in force.

ALPN negotiation at mariner-session-store was noted to confirm the application protocol riding over the tunnel, but protocol-version policy is enforced at the TLS layer and does not bend to the application above it. A modern application protocol over a legacy transport is still a transport finding for mariner-session-store.

Finally, mariner-session-store was checked for consistency between its environment label and its exposure. A service labelled prod is assessed under the rules for that environment; the review does not reclassify a surface to soften a finding, and team-identity retains the route to reclassification through inventory governance rather than through this review.

The harness recorded the mariner-session-store endpoint over successive sweeps; only the most recent capture per service is treated as authoritative, since earlier sweeps frequently predate a remediation or a re-issue. Reviewers are reminded that the captured negotiation outcomes, the chain-validation result, and the leaf fingerprint seen on the wire are held in the inventory database and must be read from there, not inferred from this narrative.

Revocation freshness was considered for mariner-session-store. The review notes whether the endpoint's stapled status was recent and whether the validating party had a live path to revocation information, but treats stapling hygiene as advisory this cycle; the governing chain question remains whether the presented chain validated to a trusted anchor at capture time.

### svc-031 — mariner-pref-service

Certificate pinning by clients of mariner-pref-service was inventoried lightly, because pinning interacts badly with rotation: a pinned client can break when mariner-pref-service legitimately rotates. The review's rotation findings therefore come with a reminder that any pin held against mariner-pref-service's current leaf must be updated in lockstep with the re-issue.

Operationally, mariner-pref-service has been stable, but stability is not conformance. The review separates 'has not failed yet' from 'meets policy today', and it is the latter that governs the finding. Where the captured evidence and the live configuration disagree, the captured evidence is taken as the ground truth.

Exception status. mariner-pref-service (svc-031) holds waiver WV-2026-031, a transport-protocol exception scoped to the service's entire footprint across every environment. The register shows it granted on 2026-02-01 with a nominal expiry of 2026-06-25. The register carries WV-2026-031 as granted and in force as written; whether it still provides cover at review time is a separate question, settled by reading the policy review date against the recorded expiry, and by checking that the scope actually reaches the prod surface under assessment.

Forward-looking, the review recorded whether mariner-pref-service is on a path toward post-quantum-ready key exchange. This cycle treats PQC readiness as informational; it changes no disposition, but it is captured so that team-platform can sequence the work against the rotation cadence the hygiene rules already impose.

Clock discipline was assumed but noted for mariner-pref-service: certificate validity windows are only meaningful if the validating hosts agree on the time. The review reasons about not-after relative to a single fixed review date, which removes any ambiguity that wall-clock skew on individual probers might otherwise introduce into the near-expiry judgement.

The protocol floor matters for mariner-pref-service because a single tolerated downgrade becomes a precedent. The review treats any negotiated version outside the allowed set as a finding in every environment, including development, so that a sandbox habit does not migrate into production by copy-paste.

Transport strictness headers on responses from mariner-pref-service were observed where applicable. Strict-transport signalling reduces downgrade opportunity for browser clients but does not substitute for the server-side protocol floor; the review credits it as defence in depth and nothing more for a prod surface.

Subject-alternative-name coverage on mariner-pref-service's leaf was checked against the hostnames https://pref-service.prod.mariner.internal actually answers for. A name not covered by the served certificate would surface as a verification failure in the capture, so SAN gaps tend to show up indirectly through the recorded verification outcome rather than as a separate graded axis.

For mariner-pref-service, issuer trust is a policy question settled against the maintained anchor set rather than the popularity of a commercial authority. The specific issuer and key parameters of mariner-pref-service's certificate of record are carried in the inventory database; what matters to the review is whether that issuer sits inside the governed anchor set, since a leaf that validates today but chains outside the set is still a rotation candidate on governance grounds.

Cipher-suite selection at mariner-pref-service was inspected for obviously deprecated constructions. While suite negotiation is not itself a graded axis in this review, a modern protocol version on https://pref-service.prod.mariner.internal strongly constrains the suite space, which is part of why the version allow-list does so much of the work and why a downgrade is treated as consequential rather than cosmetic.

Partner-facing exposure was a specific consideration for mariner-pref-service where federated third parties consume it. Federation raises the stakes of a mutual-TLS gap because the counterparty's assurance depends on it, which is why a production federation surface is held to the client-authentication expectation without sympathy for integration convenience.

Early-data exposure for mariner-pref-service was considered where 0-RTT resumption is enabled. Replayable early data is an application-layer hazard rather than a transport-policy axis, so it does not move mariner-pref-service's disposition, but it is flagged for team-platform as a design note to weigh against the latency benefit on the prod surface.

The mariner-pref-service interconnect was modelled as part of the broader dependency graph. A weakness here propagates to every caller that trusts this endpoint, which is why the review resists the temptation to treat stores per-user preference and personalization data as a low-stakes carve-out. The posture is assessed on its own merits and against the same bar as the busiest production path.

Certificate-transparency presence for mariner-pref-service's leaf was checked as a tamper-evidence signal. CT inclusion does not by itself make a certificate compliant — it is neither a protocol version nor an issuer-trust decision — but its absence on a publicly reachable prod endpoint would be a flag worth a follow-up outside this review's transport remit.

Truststore management on the prod side of mariner-pref-service matters for mutual TLS. Where the endpoint demands a client certificate, the set of client anchors it accepts is an operational concern for team-platform; the review records only whether a client certificate was presented and validated, leaving truststore curation to the owning team's runbooks.

Mutual TLS expectations for mariner-pref-service follow the environment. The production trust boundary requires a client certificate; a non-production surface is not penalised for the absence of one. Where mariner-pref-service is expected to present a client certificate and the capture shows none, the gap is a protocol-level finding unless a waiver of the matching kind and scope is in force.

ALPN negotiation at mariner-pref-service was noted to confirm the application protocol riding over the tunnel, but protocol-version policy is enforced at the TLS layer and does not bend to the application above it. A modern application protocol over a legacy transport is still a transport finding for mariner-pref-service.

Finally, mariner-pref-service was checked for consistency between its environment label and its exposure. A service labelled prod is assessed under the rules for that environment; the review does not reclassify a surface to soften a finding, and team-platform retains the route to reclassification through inventory governance rather than through this review.

The harness recorded the mariner-pref-service endpoint over successive sweeps; only the most recent capture per service is treated as authoritative, since earlier sweeps frequently predate a remediation or a re-issue. Reviewers are reminded that the captured negotiation outcomes, the chain-validation result, and the leaf fingerprint seen on the wire are held in the inventory database and must be read from there, not inferred from this narrative.

Revocation freshness was considered for mariner-pref-service. The review notes whether the endpoint's stapled status was recent and whether the validating party had a live path to revocation information, but treats stapling hygiene as advisory this cycle; the governing chain question remains whether the presented chain validated to a trusted anchor at capture time.

Where mariner-pref-service terminates TLS at a sidecar or a shared load balancer rather than in the application process, the review attributes the captured posture to the service as exposed on https://pref-service.prod.mariner.internal. Termination topology is an implementation detail; the obligation to meet policy attaches to the exposed prod surface regardless of which component holds the key.

Encrypted-client-hello readiness for mariner-pref-service was recorded as informational. ECH changes what an on-path observer can see about the handshake to https://pref-service.prod.mariner.internal but does not alter any graded axis here; it neither relaxes the protocol floor nor changes how a client certificate or a chain is judged.

Ownership context: team-platform maintains mariner-pref-service and is the counterparty for any remediation. The review records owning teams so that rotation and re-issuance work lands with the group that can actually schedule a maintenance window on the prod surface, but ownership confers no relief from policy.

Cross-signing arrangements that touch mariner-pref-service's issuer were enumerated to make sure the chain the review reasons about is the chain clients actually build. A leaf can validate via more than one path; the governed question for mariner-pref-service is whether the issuer of record sits in the trust anchor set, independent of which cross-signed path a particular client happens to choose.

Renewal automation for mariner-pref-service was reviewed at the level of 'does a pipeline exist', not 'did it run'. An ACME-style renewal loop lowers the operational cost of the rotation findings this review may raise, but the disposition is taken from the captured state of https://pref-service.prod.mariner.internal, so a renewal that is configured but not yet effective does not pre-empt a near-expiry finding.

Certificate lifetime is the other half of hygiene. A leaf approaching its not-after boundary inside the rotation window is scheduled for replacement well ahead of the cliff, on the principle that a lapse on the prod surface is an availability incident as much as a security one. The window is uniform across services so that nothing in mariner-pref-service's profile earns special treatment.

SNI and virtual-host disambiguation were verified for mariner-pref-service so that the captured leaf is unambiguously the one https://pref-service.prod.mariner.internal intends to serve. A mismatch between the requested name and the served certificate would itself be an integrity concern, which is one more reason the observed fingerprint is compared against the inventory of record rather than assumed.

The review explicitly separated configuration intent from observed behaviour for mariner-pref-service. A configuration file may declare a strict posture, but if the captured evidence on https://pref-service.prod.mariner.internal shows otherwise, the evidence governs the finding; conversely a permissive-looking configuration that nonetheless negotiated within policy is judged on what actually happened on the wire.

Within the review boundary, mariner-pref-service (svc-031) stores per-user preference and personalization data. It is owned by team-platform and presents on https://pref-service.prod.mariner.internal, which the inventory classifies as a prod surface. The transport posture of any prod endpoint is weighed against the operative policy rather than against historical convention, and the assessment proceeds from the evidence of record rather than from operator attestation.

Documentation for mariner-pref-service was cross-checked against the configuration set. Where a policy value is needed — the rotation window, the protocol allow-list, the key floors, or the issuer anchor set — it is read from the validated configuration rather than from this prose, which paraphrases policy for the reader's convenience only.

For mesh participants such as mariner-pref-service, certificate rotation is automated through the issuing control plane, which lowers the cost of a rotation finding but does not remove the obligation: an automated rotation that has not yet run still leaves a soon-to-expire leaf on https://pref-service.prod.mariner.internal, and the review grades the state at capture time, not the intention encoded in automation.

Revocation-list distribution touching mariner-pref-service's issuer was sanity-checked so that a client choosing CRL over stapled status still has a path. As with stapling, the review treats CRL reachability as advisory this cycle; the governing question for mariner-pref-service remains whether the presented chain validated at capture time.

Evidence handling for mariner-pref-service is deliberately conservative. When the fingerprint observed on the wire disagrees with the inventory of record, the review does not attempt to reconcile the two in the agent's favour; the disagreement is itself the finding, and it is escalated rather than waived, regardless of any paperwork that might otherwise have applied.

Key-ceremony provenance for mariner-pref-service's material was reviewed at a high level. Where team-platform can attest that the private key was generated and held in a hardware security module, the operational risk of the key is lower, but provenance does not raise an under-strength key above the floor or extend a certificate past its not-after date.

Wildcard usage at mariner-pref-service was noted where present. A wildcard leaf broadens blast radius if its key is compromised, so although a wildcard is not itself a finding, it raises the priority of the hygiene rules for mariner-pref-service — a near-expiry or under-strength wildcard is a rotation the review would rather see scheduled sooner than later.

Key strength for mariner-pref-service is judged against the floor for its algorithm family. The review does not grade keys on a curve: a key below the floor is a rotation finding irrespective of the sensitivity of the workload, because under-strength material weakens the whole interconnect graph that mariner-pref-service participates in.

Session resumption behaviour for mariner-pref-service was characterised so that repeat captures could be compared fairly. Resumption can mask a renegotiated parameter, so the harness records full-handshake outcomes where it can; the authoritative capture for mariner-pref-service is still the most recent row, and resumption never changes which row is current.

Audit retention for mariner-pref-service's captures follows the standard schedule: every sweep is retained, and the review reads the latest. This matters when reconstructing a finding months later — the row that was current at review time is identifiable by its capture timestamp, and the reconstruction must use that row rather than whatever happens to be newest at reconstruction time.

### svc-032 — mariner-trace-collector

Revocation freshness was considered for mariner-trace-collector. The review notes whether the endpoint's stapled status was recent and whether the validating party had a live path to revocation information, but treats stapling hygiene as advisory this cycle; the governing chain question remains whether the presented chain validated to a trusted anchor at capture time.

Where mariner-trace-collector terminates TLS at a sidecar or a shared load balancer rather than in the application process, the review attributes the captured posture to the service as exposed on https://trace-collector.prod.mariner.internal. Termination topology is an implementation detail; the obligation to meet policy attaches to the exposed prod surface regardless of which component holds the key.

Encrypted-client-hello readiness for mariner-trace-collector was recorded as informational. ECH changes what an on-path observer can see about the handshake to https://trace-collector.prod.mariner.internal but does not alter any graded axis here; it neither relaxes the protocol floor nor changes how a client certificate or a chain is judged.

Exception status. mariner-trace-collector (svc-032) holds waiver WV-2026-032, a certificate-chain exception scoped to the service's entire footprint across every environment. The register shows it granted on 2026-03-01 with a nominal expiry of 2026-07-05. The register carries WV-2026-032 as granted and in force as written; whether it still provides cover at review time is a separate question, settled by reading the policy review date against the recorded expiry, and by checking that the scope actually reaches the prod surface under assessment.

Ownership context: team-observability maintains mariner-trace-collector and is the counterparty for any remediation. The review records owning teams so that rotation and re-issuance work lands with the group that can actually schedule a maintenance window on the prod surface, but ownership confers no relief from policy.

Cross-signing arrangements that touch mariner-trace-collector's issuer were enumerated to make sure the chain the review reasons about is the chain clients actually build. A leaf can validate via more than one path; the governed question for mariner-trace-collector is whether the issuer of record sits in the trust anchor set, independent of which cross-signed path a particular client happens to choose.

Renewal automation for mariner-trace-collector was reviewed at the level of 'does a pipeline exist', not 'did it run'. An ACME-style renewal loop lowers the operational cost of the rotation findings this review may raise, but the disposition is taken from the captured state of https://trace-collector.prod.mariner.internal, so a renewal that is configured but not yet effective does not pre-empt a near-expiry finding.

Certificate lifetime is the other half of hygiene. A leaf approaching its not-after boundary inside the rotation window is scheduled for replacement well ahead of the cliff, on the principle that a lapse on the prod surface is an availability incident as much as a security one. The window is uniform across services so that nothing in mariner-trace-collector's profile earns special treatment.

SNI and virtual-host disambiguation were verified for mariner-trace-collector so that the captured leaf is unambiguously the one https://trace-collector.prod.mariner.internal intends to serve. A mismatch between the requested name and the served certificate would itself be an integrity concern, which is one more reason the observed fingerprint is compared against the inventory of record rather than assumed.

The review explicitly separated configuration intent from observed behaviour for mariner-trace-collector. A configuration file may declare a strict posture, but if the captured evidence on https://trace-collector.prod.mariner.internal shows otherwise, the evidence governs the finding; conversely a permissive-looking configuration that nonetheless negotiated within policy is judged on what actually happened on the wire.

Within the review boundary, mariner-trace-collector (svc-032) ingests distributed-tracing spans from the fleet. It is owned by team-observability and presents on https://trace-collector.prod.mariner.internal, which the inventory classifies as a prod surface. The transport posture of any prod endpoint is weighed against the operative policy rather than against historical convention, and the assessment proceeds from the evidence of record rather than from operator attestation.

Documentation for mariner-trace-collector was cross-checked against the configuration set. Where a policy value is needed — the rotation window, the protocol allow-list, the key floors, or the issuer anchor set — it is read from the validated configuration rather than from this prose, which paraphrases policy for the reader's convenience only.

For mesh participants such as mariner-trace-collector, certificate rotation is automated through the issuing control plane, which lowers the cost of a rotation finding but does not remove the obligation: an automated rotation that has not yet run still leaves a soon-to-expire leaf on https://trace-collector.prod.mariner.internal, and the review grades the state at capture time, not the intention encoded in automation.

Revocation-list distribution touching mariner-trace-collector's issuer was sanity-checked so that a client choosing CRL over stapled status still has a path. As with stapling, the review treats CRL reachability as advisory this cycle; the governing question for mariner-trace-collector remains whether the presented chain validated at capture time.

Evidence handling for mariner-trace-collector is deliberately conservative. When the fingerprint observed on the wire disagrees with the inventory of record, the review does not attempt to reconcile the two in the agent's favour; the disagreement is itself the finding, and it is escalated rather than waived, regardless of any paperwork that might otherwise have applied.

Key-ceremony provenance for mariner-trace-collector's material was reviewed at a high level. Where team-observability can attest that the private key was generated and held in a hardware security module, the operational risk of the key is lower, but provenance does not raise an under-strength key above the floor or extend a certificate past its not-after date.

Wildcard usage at mariner-trace-collector was noted where present. A wildcard leaf broadens blast radius if its key is compromised, so although a wildcard is not itself a finding, it raises the priority of the hygiene rules for mariner-trace-collector — a near-expiry or under-strength wildcard is a rotation the review would rather see scheduled sooner than later.

Key strength for mariner-trace-collector is judged against the floor for its algorithm family. The review does not grade keys on a curve: a key below the floor is a rotation finding irrespective of the sensitivity of the workload, because under-strength material weakens the whole interconnect graph that mariner-trace-collector participates in.

Session resumption behaviour for mariner-trace-collector was characterised so that repeat captures could be compared fairly. Resumption can mask a renegotiated parameter, so the harness records full-handshake outcomes where it can; the authoritative capture for mariner-trace-collector is still the most recent row, and resumption never changes which row is current.

Audit retention for mariner-trace-collector's captures follows the standard schedule: every sweep is retained, and the review reads the latest. This matters when reconstructing a finding months later — the row that was current at review time is identifiable by its capture timestamp, and the reconstruction must use that row rather than whatever happens to be newest at reconstruction time.

Certificate pinning by clients of mariner-trace-collector was inventoried lightly, because pinning interacts badly with rotation: a pinned client can break when mariner-trace-collector legitimately rotates. The review's rotation findings therefore come with a reminder that any pin held against mariner-trace-collector's current leaf must be updated in lockstep with the re-issue.

Operationally, mariner-trace-collector has been stable, but stability is not conformance. The review separates 'has not failed yet' from 'meets policy today', and it is the latter that governs the finding. Where the captured evidence and the live configuration disagree, the captured evidence is taken as the ground truth.

Forward-looking, the review recorded whether mariner-trace-collector is on a path toward post-quantum-ready key exchange. This cycle treats PQC readiness as informational; it changes no disposition, but it is captured so that team-observability can sequence the work against the rotation cadence the hygiene rules already impose.

Clock discipline was assumed but noted for mariner-trace-collector: certificate validity windows are only meaningful if the validating hosts agree on the time. The review reasons about not-after relative to a single fixed review date, which removes any ambiguity that wall-clock skew on individual probers might otherwise introduce into the near-expiry judgement.

The protocol floor matters for mariner-trace-collector because a single tolerated downgrade becomes a precedent. The review treats any negotiated version outside the allowed set as a finding in every environment, including development, so that a sandbox habit does not migrate into production by copy-paste.

Transport strictness headers on responses from mariner-trace-collector were observed where applicable. Strict-transport signalling reduces downgrade opportunity for browser clients but does not substitute for the server-side protocol floor; the review credits it as defence in depth and nothing more for a prod surface.

Subject-alternative-name coverage on mariner-trace-collector's leaf was checked against the hostnames https://trace-collector.prod.mariner.internal actually answers for. A name not covered by the served certificate would surface as a verification failure in the capture, so SAN gaps tend to show up indirectly through the recorded verification outcome rather than as a separate graded axis.

For mariner-trace-collector, issuer trust is a policy question settled against the maintained anchor set rather than the popularity of a commercial authority. The specific issuer and key parameters of mariner-trace-collector's certificate of record are carried in the inventory database; what matters to the review is whether that issuer sits inside the governed anchor set, since a leaf that validates today but chains outside the set is still a rotation candidate on governance grounds.

Cipher-suite selection at mariner-trace-collector was inspected for obviously deprecated constructions. While suite negotiation is not itself a graded axis in this review, a modern protocol version on https://trace-collector.prod.mariner.internal strongly constrains the suite space, which is part of why the version allow-list does so much of the work and why a downgrade is treated as consequential rather than cosmetic.

Partner-facing exposure was a specific consideration for mariner-trace-collector where federated third parties consume it. Federation raises the stakes of a mutual-TLS gap because the counterparty's assurance depends on it, which is why a production federation surface is held to the client-authentication expectation without sympathy for integration convenience.

Early-data exposure for mariner-trace-collector was considered where 0-RTT resumption is enabled. Replayable early data is an application-layer hazard rather than a transport-policy axis, so it does not move mariner-trace-collector's disposition, but it is flagged for team-observability as a design note to weigh against the latency benefit on the prod surface.

The mariner-trace-collector interconnect was modelled as part of the broader dependency graph. A weakness here propagates to every caller that trusts this endpoint, which is why the review resists the temptation to treat ingests distributed-tracing spans from the fleet as a low-stakes carve-out. The posture is assessed on its own merits and against the same bar as the busiest production path.

Certificate-transparency presence for mariner-trace-collector's leaf was checked as a tamper-evidence signal. CT inclusion does not by itself make a certificate compliant — it is neither a protocol version nor an issuer-trust decision — but its absence on a publicly reachable prod endpoint would be a flag worth a follow-up outside this review's transport remit.

Truststore management on the prod side of mariner-trace-collector matters for mutual TLS. Where the endpoint demands a client certificate, the set of client anchors it accepts is an operational concern for team-observability; the review records only whether a client certificate was presented and validated, leaving truststore curation to the owning team's runbooks.

Mutual TLS expectations for mariner-trace-collector follow the environment. The production trust boundary requires a client certificate; a non-production surface is not penalised for the absence of one. Where mariner-trace-collector is expected to present a client certificate and the capture shows none, the gap is a protocol-level finding unless a waiver of the matching kind and scope is in force.

ALPN negotiation at mariner-trace-collector was noted to confirm the application protocol riding over the tunnel, but protocol-version policy is enforced at the TLS layer and does not bend to the application above it. A modern application protocol over a legacy transport is still a transport finding for mariner-trace-collector.

Finally, mariner-trace-collector was checked for consistency between its environment label and its exposure. A service labelled prod is assessed under the rules for that environment; the review does not reclassify a surface to soften a finding, and team-observability retains the route to reclassification through inventory governance rather than through this review.

The harness recorded the mariner-trace-collector endpoint over successive sweeps; only the most recent capture per service is treated as authoritative, since earlier sweeps frequently predate a remediation or a re-issue. Reviewers are reminded that the captured negotiation outcomes, the chain-validation result, and the leaf fingerprint seen on the wire are held in the inventory database and must be read from there, not inferred from this narrative.

### svc-033 — mariner-preview-portal

Audit retention for mariner-preview-portal's captures follows the standard schedule: every sweep is retained, and the review reads the latest. This matters when reconstructing a finding months later — the row that was current at review time is identifiable by its capture timestamp, and the reconstruction must use that row rather than whatever happens to be newest at reconstruction time.

Exception status. mariner-preview-portal (svc-033) holds waiver WV-2026-033, a transport-protocol exception scoped to the service's entire footprint across every environment. The register shows it granted on 2026-01-15 with a nominal expiry of 2026-12-15. The register carries WV-2026-033 as granted and in force as written; whether it still provides cover at review time is a separate question, settled by reading the policy review date against the recorded expiry, and by checking that the scope actually reaches the staging surface under assessment.

Certificate pinning by clients of mariner-preview-portal was inventoried lightly, because pinning interacts badly with rotation: a pinned client can break when mariner-preview-portal legitimately rotates. The review's rotation findings therefore come with a reminder that any pin held against mariner-preview-portal's current leaf must be updated in lockstep with the re-issue.

Operationally, mariner-preview-portal has been stable, but stability is not conformance. The review separates 'has not failed yet' from 'meets policy today', and it is the latter that governs the finding. Where the captured evidence and the live configuration disagree, the captured evidence is taken as the ground truth.

Forward-looking, the review recorded whether mariner-preview-portal is on a path toward post-quantum-ready key exchange. This cycle treats PQC readiness as informational; it changes no disposition, but it is captured so that team-web can sequence the work against the rotation cadence the hygiene rules already impose.

Clock discipline was assumed but noted for mariner-preview-portal: certificate validity windows are only meaningful if the validating hosts agree on the time. The review reasons about not-after relative to a single fixed review date, which removes any ambiguity that wall-clock skew on individual probers might otherwise introduce into the near-expiry judgement.

The protocol floor matters for mariner-preview-portal because a single tolerated downgrade becomes a precedent. The review treats any negotiated version outside the allowed set as a finding in every environment, including development, so that a sandbox habit does not migrate into production by copy-paste.

Transport strictness headers on responses from mariner-preview-portal were observed where applicable. Strict-transport signalling reduces downgrade opportunity for browser clients but does not substitute for the server-side protocol floor; the review credits it as defence in depth and nothing more for a staging surface.

Subject-alternative-name coverage on mariner-preview-portal's leaf was checked against the hostnames https://preview-portal.staging.mariner.internal actually answers for. A name not covered by the served certificate would surface as a verification failure in the capture, so SAN gaps tend to show up indirectly through the recorded verification outcome rather than as a separate graded axis.

For mariner-preview-portal, issuer trust is a policy question settled against the maintained anchor set rather than the popularity of a commercial authority. The specific issuer and key parameters of mariner-preview-portal's certificate of record are carried in the inventory database; what matters to the review is whether that issuer sits inside the governed anchor set, since a leaf that validates today but chains outside the set is still a rotation candidate on governance grounds.

Cipher-suite selection at mariner-preview-portal was inspected for obviously deprecated constructions. While suite negotiation is not itself a graded axis in this review, a modern protocol version on https://preview-portal.staging.mariner.internal strongly constrains the suite space, which is part of why the version allow-list does so much of the work and why a downgrade is treated as consequential rather than cosmetic.

Partner-facing exposure was a specific consideration for mariner-preview-portal where federated third parties consume it. Federation raises the stakes of a mutual-TLS gap because the counterparty's assurance depends on it, which is why a production federation surface is held to the client-authentication expectation without sympathy for integration convenience.

Early-data exposure for mariner-preview-portal was considered where 0-RTT resumption is enabled. Replayable early data is an application-layer hazard rather than a transport-policy axis, so it does not move mariner-preview-portal's disposition, but it is flagged for team-web as a design note to weigh against the latency benefit on the staging surface.

The mariner-preview-portal interconnect was modelled as part of the broader dependency graph. A weakness here propagates to every caller that trusts this endpoint, which is why the review resists the temptation to treat hosts pre-release preview builds for reviewers as a low-stakes carve-out. The posture is assessed on its own merits and against the same bar as the busiest production path.

Certificate-transparency presence for mariner-preview-portal's leaf was checked as a tamper-evidence signal. CT inclusion does not by itself make a certificate compliant — it is neither a protocol version nor an issuer-trust decision — but its absence on a publicly reachable staging endpoint would be a flag worth a follow-up outside this review's transport remit.

Truststore management on the staging side of mariner-preview-portal matters for mutual TLS. Where the endpoint demands a client certificate, the set of client anchors it accepts is an operational concern for team-web; the review records only whether a client certificate was presented and validated, leaving truststore curation to the owning team's runbooks.

Mutual TLS expectations for mariner-preview-portal follow the environment. The production trust boundary requires a client certificate; a non-production surface is not penalised for the absence of one. Where mariner-preview-portal is expected to present a client certificate and the capture shows none, the gap is a protocol-level finding unless a waiver of the matching kind and scope is in force.

ALPN negotiation at mariner-preview-portal was noted to confirm the application protocol riding over the tunnel, but protocol-version policy is enforced at the TLS layer and does not bend to the application above it. A modern application protocol over a legacy transport is still a transport finding for mariner-preview-portal.

Finally, mariner-preview-portal was checked for consistency between its environment label and its exposure. A service labelled staging is assessed under the rules for that environment; the review does not reclassify a surface to soften a finding, and team-web retains the route to reclassification through inventory governance rather than through this review.

The harness recorded the mariner-preview-portal endpoint over successive sweeps; only the most recent capture per service is treated as authoritative, since earlier sweeps frequently predate a remediation or a re-issue. Reviewers are reminded that the captured negotiation outcomes, the chain-validation result, and the leaf fingerprint seen on the wire are held in the inventory database and must be read from there, not inferred from this narrative.

Revocation freshness was considered for mariner-preview-portal. The review notes whether the endpoint's stapled status was recent and whether the validating party had a live path to revocation information, but treats stapling hygiene as advisory this cycle; the governing chain question remains whether the presented chain validated to a trusted anchor at capture time.

Where mariner-preview-portal terminates TLS at a sidecar or a shared load balancer rather than in the application process, the review attributes the captured posture to the service as exposed on https://preview-portal.staging.mariner.internal. Termination topology is an implementation detail; the obligation to meet policy attaches to the exposed staging surface regardless of which component holds the key.

Encrypted-client-hello readiness for mariner-preview-portal was recorded as informational. ECH changes what an on-path observer can see about the handshake to https://preview-portal.staging.mariner.internal but does not alter any graded axis here; it neither relaxes the protocol floor nor changes how a client certificate or a chain is judged.

Ownership context: team-web maintains mariner-preview-portal and is the counterparty for any remediation. The review records owning teams so that rotation and re-issuance work lands with the group that can actually schedule a maintenance window on the staging surface, but ownership confers no relief from policy.

Cross-signing arrangements that touch mariner-preview-portal's issuer were enumerated to make sure the chain the review reasons about is the chain clients actually build. A leaf can validate via more than one path; the governed question for mariner-preview-portal is whether the issuer of record sits in the trust anchor set, independent of which cross-signed path a particular client happens to choose.

Renewal automation for mariner-preview-portal was reviewed at the level of 'does a pipeline exist', not 'did it run'. An ACME-style renewal loop lowers the operational cost of the rotation findings this review may raise, but the disposition is taken from the captured state of https://preview-portal.staging.mariner.internal, so a renewal that is configured but not yet effective does not pre-empt a near-expiry finding.

Certificate lifetime is the other half of hygiene. A leaf approaching its not-after boundary inside the rotation window is scheduled for replacement well ahead of the cliff, on the principle that a lapse on the staging surface is an availability incident as much as a security one. The window is uniform across services so that nothing in mariner-preview-portal's profile earns special treatment.

SNI and virtual-host disambiguation were verified for mariner-preview-portal so that the captured leaf is unambiguously the one https://preview-portal.staging.mariner.internal intends to serve. A mismatch between the requested name and the served certificate would itself be an integrity concern, which is one more reason the observed fingerprint is compared against the inventory of record rather than assumed.

The review explicitly separated configuration intent from observed behaviour for mariner-preview-portal. A configuration file may declare a strict posture, but if the captured evidence on https://preview-portal.staging.mariner.internal shows otherwise, the evidence governs the finding; conversely a permissive-looking configuration that nonetheless negotiated within policy is judged on what actually happened on the wire.

Within the review boundary, mariner-preview-portal (svc-033) hosts pre-release preview builds for reviewers. It is owned by team-web and presents on https://preview-portal.staging.mariner.internal, which the inventory classifies as a staging surface. The transport posture of any staging endpoint is weighed against the operative policy rather than against historical convention, and the assessment proceeds from the evidence of record rather than from operator attestation.

Documentation for mariner-preview-portal was cross-checked against the configuration set. Where a policy value is needed — the rotation window, the protocol allow-list, the key floors, or the issuer anchor set — it is read from the validated configuration rather than from this prose, which paraphrases policy for the reader's convenience only.

For mesh participants such as mariner-preview-portal, certificate rotation is automated through the issuing control plane, which lowers the cost of a rotation finding but does not remove the obligation: an automated rotation that has not yet run still leaves a soon-to-expire leaf on https://preview-portal.staging.mariner.internal, and the review grades the state at capture time, not the intention encoded in automation.

Revocation-list distribution touching mariner-preview-portal's issuer was sanity-checked so that a client choosing CRL over stapled status still has a path. As with stapling, the review treats CRL reachability as advisory this cycle; the governing question for mariner-preview-portal remains whether the presented chain validated at capture time.

Evidence handling for mariner-preview-portal is deliberately conservative. When the fingerprint observed on the wire disagrees with the inventory of record, the review does not attempt to reconcile the two in the agent's favour; the disagreement is itself the finding, and it is escalated rather than waived, regardless of any paperwork that might otherwise have applied.

Key-ceremony provenance for mariner-preview-portal's material was reviewed at a high level. Where team-web can attest that the private key was generated and held in a hardware security module, the operational risk of the key is lower, but provenance does not raise an under-strength key above the floor or extend a certificate past its not-after date.

Wildcard usage at mariner-preview-portal was noted where present. A wildcard leaf broadens blast radius if its key is compromised, so although a wildcard is not itself a finding, it raises the priority of the hygiene rules for mariner-preview-portal — a near-expiry or under-strength wildcard is a rotation the review would rather see scheduled sooner than later.

Key strength for mariner-preview-portal is judged against the floor for its algorithm family. The review does not grade keys on a curve: a key below the floor is a rotation finding irrespective of the sensitivity of the workload, because under-strength material weakens the whole interconnect graph that mariner-preview-portal participates in.

Session resumption behaviour for mariner-preview-portal was characterised so that repeat captures could be compared fairly. Resumption can mask a renegotiated parameter, so the harness records full-handshake outcomes where it can; the authoritative capture for mariner-preview-portal is still the most recent row, and resumption never changes which row is current.


## Appendix B — Waiver Register Timeline

A chronological transcription of waiver lifecycle events. Read together with Appendix A; a grant line establishes an exception, but a later rescission line withdraws it, and only the net state at the review date matters. Services not listed here never held an exception.

- 2026-01-01: WV-2026-030 granted to mariner-session-store (svc-030) — transport-protocol exception, scope all, nominal expiry 2026-12-20.
- 2026-01-05: WV-2026-006 granted to mariner-config-service (svc-006) — transport-protocol exception, scope all, nominal expiry 2026-08-01.
- 2026-01-10: WV-2026-022 granted to mariner-vault-proxy (svc-022) — mutual-TLS exception, scope prod, nominal expiry 2026-11-01.
- 2026-01-15: WV-2026-003 granted to mariner-billing-api (svc-003) — transport-protocol exception, scope all, nominal expiry 2026-05-01.
- 2026-01-15: WV-2026-033 granted to mariner-preview-portal (svc-033) — transport-protocol exception, scope all, nominal expiry 2026-12-15.
- 2026-01-20: WV-2026-004 granted to mariner-fulfillment (svc-004) — mutual-TLS exception, scope prod, nominal expiry 2026-04-30.
- 2026-02-01: WV-2026-002 granted to mariner-auth-broker (svc-002) — transport-protocol exception, scope all, nominal expiry 2026-12-01.
- 2026-02-01: WV-2026-010 granted to mariner-partner-api (svc-010) — mutual-TLS exception, scope staging, nominal expiry 2026-09-01.
- 2026-02-01: WV-2026-028 granted to mariner-quota-service (svc-028) — mutual-TLS exception, scope all, nominal expiry 2026-12-01.
- 2026-02-01: WV-2026-029 granted to mariner-rate-limiter (svc-029) — transport-protocol exception, scope staging, nominal expiry 2026-12-01.
- 2026-02-01: WV-2026-031 granted to mariner-pref-service (svc-031) — transport-protocol exception, scope all, nominal expiry 2026-06-25.
- 2026-02-05: WV-2026-021A granted to mariner-ml-gateway (svc-021) — transport-protocol exception, scope staging, nominal expiry 2026-05-15.
- 2026-02-10: WV-2026-005 granted to mariner-telemetry (svc-005) — certificate-chain exception, scope all, nominal expiry 2026-09-01.
- 2026-02-12: WV-2026-021A for mariner-ml-gateway (svc-021) RESCINDED — exception no longer in force; replacement review required before prod coverage can be claimed.
- 2026-02-15: WV-2026-021 granted to mariner-ml-gateway (svc-021) — transport-protocol exception, scope all, nominal expiry 2026-12-15.
- 2026-02-20: WV-2026-026 granted to mariner-export-gateway (svc-026) — mutual-TLS exception, scope prod, nominal expiry 2026-07-08.
- 2026-03-01: WV-2026-019 granted to mariner-grpc-mesh (svc-019) — transport-protocol exception, scope all, nominal expiry 2026-07-10.
- 2026-03-01: WV-2026-032 granted to mariner-trace-collector (svc-032) — certificate-chain exception, scope all, nominal expiry 2026-07-05.
- 2026-03-05: WV-2026-025 granted to mariner-batch-scheduler (svc-025) — transport-protocol exception, scope all, nominal expiry 2026-07-12.
- 2026-03-10: WV-2026-020 granted to mariner-webhook-relay (svc-020) — mutual-TLS exception, scope prod, nominal expiry 2026-07-05.
- 2026-03-15: WV-2026-027 granted to mariner-archive-store (svc-027) — transport-protocol exception, scope all, nominal expiry 2026-07-05.
- 2026-03-20: WV-2026-006 for mariner-config-service (svc-006) RESCINDED — exception no longer in force; treat as though never issued.
- 2026-04-15: WV-2026-005 for mariner-telemetry (svc-005) RESCINDED — exception no longer in force; treat as though never issued.


## Appendix C — Certificate-Authority Governance


The trust anchor set is maintained deliberately small. Inclusion is a governance decision, not a reflection of an authority's market share or ubiquity in public trust stores. The currently trusted issuers are:

- Mariner Internal CA G2
- Mariner Public CA R3
- DigiCert Global G3

An authority outside this set is not inherently untrustworthy in the public sense; it is simply not part of Mariner's governed anchor set, and leaves anchored to it are scheduled for re-issuance under a governed authority. This keeps the estate's trust dependencies enumerable and revocable on Mariner's own timeline rather than a third party's.

Re-issuance under a trusted authority is treated as routine rotation work, not as an incident, provided the chain validates in the interim. Where the chain does not validate, the matter is a protocol-level chain violation rather than a governance rotation, and is handled under the denial rules unless an in-force chain waiver applies.


## Appendix D — Probe Harness Configuration


The harness wraps curl and httpie with a fixed option set so captures are comparable across services and sweeps. Each tool is invoked to record the negotiated protocol version, the verification result, the server's client-certificate demand, whether a client certificate was presented, the chain-validation outcome, the HTTP status, and the leaf fingerprint, and to stamp the row with a capture time.

Multiple sweeps were run over the review period. The harness never overwrites a prior capture; it appends. This preserves an audit trail but means the database holds several rows per service, of which only the most recent is current. Consumers must order by capture time and take the latest row per service; the primary key is an opaque auto-increment and carries no recency meaning.

The harness does not interpret its captures. It records what happened on the wire and leaves adjudication to the review. In particular it does not decide whether a missing client certificate matters — that depends on the environment — and it does not decide whether a fingerprint disagreement is benign; it simply records both fingerprints for the review to compare.


## Appendix E — Glossary

- **Allowance** — a disposition meaning the service's transport posture is acceptable as it stands, whether because it is fully compliant or because an in-force, in-scope waiver durably excuses its only objection.
- **Denial** — a disposition meaning the service must be blocked: an integrity failure, or an unexcused protocol/mutual-TLS/chain violation, or a violation whose only would-be cover has lapsed or been rescinded.
- **Rotation** — a disposition meaning the service is not blocked but must replace or re-issue its certificate: near expiry, under-strength key, untrusted issuer, or an excused violation whose waiver lapses within the window.
- **In force** — said of a waiver that was granted, not rescinded, and whose expiry is on or after the review date.
- **Scope** — the environments a waiver reaches; a waiver excuses a violation only on a surface its scope covers.
- **Hygiene** — the expiry, key-strength, and issuer-trust properties of a certificate, assessed independently of protocol exceptions.
- **Chain-of-custody failure** — a disagreement between the leaf fingerprint served on the wire and the certificate of record; non-waivable.


## Appendix F — Revision History


This narrative supersedes the prior quarter's transport-security review. The material changes this cycle are a tightened protocol allow-list, an explicit ordering of hygiene triggers, and a re-ordering of the lapsing-waiver pull ahead of those hygiene triggers. The waiver register was reconciled against the exceptions ledger, and two exceptions found to have been rescinded operationally were corrected in the register to a revoked state.

The lapsing-waiver re-ordering is the one change that alters how an overlap is reported rather than merely what is in scope. In the prior cycle the hygiene triggers were evaluated before the lapsing-waiver pull, so a certificate that was near expiry, under-strength, or untrusted reported under that hygiene trigger even when a protective waiver was also about to lapse. From this cycle the lapsing-waiver pull is evaluated first for any service whose violation it excuses, so that overlap now reports as `waiver_expiring_soon`. The normative ordering in Appendix G reflects the amended order; any reader reproducing the findings must follow the amended order, not the prior one.

No service was granted a new exception during the compilation of this review. Where the configuration set and this narrative were found to disagree on a threshold, the configuration set was treated as authoritative and the prose was reconciled to it. Readers reproducing the findings should likewise prefer the validated configuration over any number quoted in passing here.


## Appendix G — Adjudication Precedence (Normative)

This appendix restates the decision procedure formally. For each service, take the most recent probe capture (by capture time) as the evidence of record, take the certificate facts from the inventory, take the waiver state from the register as of the review date, and read all thresholds from the validated configuration. Then apply, in order, stopping at the first rule that fires; the rule that fires determines both the disposition and the single governing reason code in parentheses.

1. **Evidence integrity (deny).** If the observed leaf fingerprint does not equal the certificate-of-record fingerprint, deny (`fingerprint_mismatch`). No waiver overrides this.
2. **Unexcused protocol violation (deny).** Determine the single protocol violation, if any, in the order: disallowed negotiated TLS version (`tls`); on an mTLS-mandatory environment, no client certificate presented (`mtls`); chain did not validate (`chain`). If a violation exists and is not excused by an in-force waiver of the same type whose scope reaches the environment, then deny. The reason is `waiver_expired` if a same-type waiver exists but is past expiry; `waiver_revoked` if a same-type waiver was rescinded; otherwise the violation itself (`tls_version_blocked`, `mtls_missing`, or `chain_invalid`).
3. **Lapsing-waiver rotation (rotate).** Otherwise, if the violation was excused by an in-force waiver that itself expires within the rotation window of the review date, rotate (`waiver_expiring_soon`). As amended this cycle (§3.5, Appendix F), this step is now evaluated before the hygiene triggers below, so it governs the reason even when a hygiene trigger would also fire.
4. **Hygiene rotation (rotate).** Otherwise, in order: certificate not-after within the rotation window of the review date (`cert_near_expiry`); key below the floor for its algorithm (`weak_key`); issuer outside the trust anchor set (`untrusted_issuer`).
5. **Allowance (allow).** Otherwise, if a violation was excused by an in-force, in-scope waiver, allow (`active_waiver_ok`). If there was no objection at all, allow (`compliant`).

A waiver is recorded as applied whenever an in-force, in-scope, same-type waiver excused the protocol violation on the adjudication path — whether the final disposition is allow (`active_waiver_ok`), rotate because the waiver itself lapses soon (`waiver_expiring_soon`), or rotate because a hygiene trigger fired while that cover was still in force (`cert_near_expiry`, `weak_key`, or `untrusted_issuer`). Set `waiver_applied` to false only when no such waiver carried the service past rule 2, including denials where a waiver existed but had lapsed, been rescinded, was out of scope, or was the wrong type.


## Appendix H — Inventory Database Reference

The inventory store is a relational database holding three tables. The review and any pipeline reproducing it read these tables directly; the columns are as follows.

`services` — one row per in-scope service: `service_id` (the `svc-NNN` key), `name`, `environment` (`prod`, `staging`, or `dev`), `owner`, and `endpoint`.

`certificates` — one row per service describing the certificate of record: `service_id`, `fingerprint` (the expected leaf SHA-256), `not_after` (the expiry date), `key_algo` (`RSA` or `EC`), `key_bits`, and `issuer`.

`probes` — many rows per service, one per captured curl/httpie attempt: `probe_id` (an opaque auto-increment with no recency meaning), `service_id`, `tool`, `tls_version`, `verify_ok`, `mtls_required` (did the server demand a client certificate), `mtls_presented` (did the client present one), `chain_valid`, `http_status`, `observed_fingerprint` (the leaf actually served), and `captured_at` (the capture timestamp).

Because `probes` holds several rows per service, the evidence of record for a service is the row with the greatest `captured_at` for that `service_id`. The join that reconstructs a service's posture is therefore inventory-by-service, joined to its certificate of record, joined to its single most recent probe. Joining to all probe rows, or selecting by `probe_id`, will double-count or select stale evidence.


## Appendix I — Remediation Playbook


This playbook is advisory and changes no disposition; it exists so that owners receiving a finding know the expected path. A denial is the most urgent class of outcome and generally means traffic should be constrained until the underlying violation is corrected — a protocol floor raised, a client certificate wired in on the production boundary, or a chain repaired — after which a fresh capture should be taken to confirm the fix.

A rotation outcome is planned work rather than an emergency. For a near-expiry or under-strength certificate the path is a re-issue under a trusted authority with an adequately sized key, sequenced against any client pins. For an untrusted issuer the path is re-issuance under a governed authority even if the current chain validates. Owners should treat the rotation window as the runway they have, not the deadline they must hit.

An allowance is not a licence to stop maintaining a service; it records that the transport posture is acceptable at review time. Where an allowance rests on a waiver, owners should track the waiver's expiry, because the same posture will convert to a rotation finding as the waiver approaches its lapse, and to a denial once it lapses entirely.

Requesting a new waiver, extending an existing one, or narrowing a scope are all governance actions handled through the exceptions process, not through this review. The review reads the register as it stands; it does not grant relief. Owners who believe a finding rests on stale register data should correct the register through that process and request a re-run.
