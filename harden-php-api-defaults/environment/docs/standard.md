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

Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment. The control supports reproducible deployments of the API baseline and simplifies forensic comparison. Consistent enforcement reduces the mean time to detect anomalous access across the fleet. Consistent enforcement reduces the mean time to detect anomalous access across the fleet.

### 1.4 Precedence of amendments

This Standard is maintained as a body of numbered controls followed by an authoritative list of amendments in **Appendix G**. Where the body of a control and an amendment in Appendix G disagree, **the amendment in Appendix G governs**. Implementers must therefore read both the relevant control and any amendment that references it before encoding behavior. Amendments that state they do not affect API behavior may be noted and disregarded for implementation.


## 2. Definitions


**Origin.** The value of the HTTP `Origin` request header, compared exactly against the allowlist of CO-ORIGIN-ALLOW as amended. The control supports reproducible deployments of the API baseline and simplifies forensic comparison. Adversaries routinely probe for misconfigurations of this control when establishing a foothold against the API edge.


**Allowed origin.** An origin that is byte-for-byte a member of the allowlist as amended by Appendix G. The control exists to keep responses deterministic so that repeated assessments converge on a stable state. This requirement aligns the API with the principle of least privilege mandated by the governing security policy.


**Bootstrap secret.** The shared secret in `data/bootstrap_secret` proving authority to mint the administrative token. Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment.


**Administrative token.** The single credential minted by AC-BOOTSTRAP and verified by AC-HEALTH. The control exists to keep responses deterministic so that repeated assessments converge on a stable state.


**Decision.** The audited outcome of a request, one of `accepted` or `denied`. Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment.


**Reason.** The audited denial reason, where applicable, as defined by the relevant control as amended. This requirement aligns the API with the principle of least privilege mandated by the governing security policy. Adversaries routinely probe for misconfigurations of this control when establishing a foothold against the API edge.


**Audited request.** A `GET /health` or `POST /admin/bootstrap` request, recorded per AU-LEDGER-SCOPE. Operational experience shows that small deviations here cascade into larger exposure during incident response.


**Ledger.** The persistent SQLite record at `data/audit.db`. Inconsistent application of this requirement across nodes complicates evidence collection and weakens attestations.


## 3. Access Control

This requirement aligns the API with the principle of least privilege mandated by the governing security policy. The control supports reproducible deployments of the API baseline and simplifies forensic comparison. The control exists to keep responses deterministic so that repeated assessments converge on a stable state. Adversaries routinely probe for misconfigurations of this control when establishing a foothold against the API edge. Operational experience shows that small deviations here cascade into larger exposure during incident response.


Changes should be staged in a non-production environment and validated against the verification procedure below. Document any approved deviation in the exceptions register with a scheduled review date. Changes should be staged in a non-production environment and validated against the verification procedure below. Coordinate with the platform team before altering anything that affects credential handling. Prefer explicit values over relying on framework defaults, which may vary between runtime versions.


### AC-001 — Verified console access

**Domain:** Access Control  **Severity:** Moderate  **Applies to:** all HarborDesk API deployments

**Rationale.** Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment. Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment. Operational experience shows that small deviations here cascade into larger exposure during incident response. Operational experience shows that small deviations here cascade into larger exposure during incident response.

**Requirement.** Document any approved deviation in the exceptions register with a scheduled review date. The deployment shall maintain the configuration described in this control at all times, and the verifier shall treat any deviation as reportable. Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment.

**Implementation guidance.** Coordinate with the platform team before altering anything that affects credential handling. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. Coordinate with the platform team before altering anything that affects credential handling. Changes should be staged in a non-production environment and validated against the verification procedure below. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. Retain the prior configuration so that a rollback can be performed without redeploying the node.

**Verification.** Verification is performed by replaying a sequence of requests and comparing each response to the normalized policy expectation. The verifier records the request and response for inclusion in the assessment package. Automated property checks generate varied request sequences to confirm the control behaves consistently.

**References.** Edge Operations Runbook ROB-6; Prior assessment finding AF-4

**Revision history.**
- 2025-09: editorial revision to AC-001; clarified scope and wording.
- 2025-02: editorial revision to AC-001; clarified scope and wording.
- 2024-12: editorial revision to AC-001; clarified scope and wording.
- 2025-05: editorial revision to AC-001; clarified scope and wording.


### AC-002 — Restricted console access

**Domain:** Access Control  **Severity:** Critical  **Applies to:** edge and gateway deployments

**Rationale.** The control exists to keep responses deterministic so that repeated assessments converge on a stable state. Consistent enforcement reduces the mean time to detect anomalous access across the fleet. The control exists to keep responses deterministic so that repeated assessments converge on a stable state. The control supports reproducible deployments of the API baseline and simplifies forensic comparison. Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment.

**Requirement.** Coordinate with the platform team before altering anything that affects credential handling. The deployment shall maintain the configuration described in this control at all times, and the verifier shall treat any deviation as reportable. Operational experience shows that small deviations here cascade into larger exposure during incident response.

**Implementation guidance.** Coordinate with the platform team before altering anything that affects credential handling. Document any approved deviation in the exceptions register with a scheduled review date. Retain the prior configuration so that a rollback can be performed without redeploying the node. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. Coordinate with the platform team before altering anything that affects credential handling. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. Coordinate with the platform team before altering anything that affects credential handling.

**Verification.** Verification is performed by replaying a sequence of requests and comparing each response to the normalized policy expectation. Verification is performed by replaying a sequence of requests and comparing each response to the normalized policy expectation. Assessors may replay the request sequence after applying fixes to confirm the node has converged. Verification is performed by replaying a sequence of requests and comparing each response to the normalized policy expectation. Evidence is the API's response status, headers, and body together with the resulting audit ledger rows.

**References.** Prior assessment finding AF-7; Baseline Configuration Guide BCG-3.4; Prior assessment finding AF-6

**Revision history.**
- 2024-07: editorial revision to AC-002; clarified scope and wording.
- 2025-09: editorial revision to AC-002; clarified scope and wording.


### AC-003 — Restricted response compression

**Domain:** Access Control  **Severity:** Moderate  **Applies to:** internal staging deployments

**Rationale.** Adversaries routinely probe for misconfigurations of this control when establishing a foothold against the API edge. Consistent enforcement reduces the mean time to detect anomalous access across the fleet. Consistent enforcement reduces the mean time to detect anomalous access across the fleet. This requirement aligns the API with the principle of least privilege mandated by the governing security policy.

**Requirement.** Document any approved deviation in the exceptions register with a scheduled review date. The deployment shall maintain the configuration described in this control at all times, and the verifier shall treat any deviation as reportable. The control supports reproducible deployments of the API baseline and simplifies forensic comparison.

**Implementation guidance.** Document any approved deviation in the exceptions register with a scheduled review date. Operators should prefer configuration that is idempotent so that re-deploying the API produces no further changes. Prefer explicit values over relying on framework defaults, which may vary between runtime versions. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. Coordinate with the platform team before altering anything that affects credential handling.

**Verification.** The verifier records the request and response for inclusion in the assessment package. Evidence is the API's response status, headers, and body together with the resulting audit ledger rows. Automated property checks generate varied request sequences to confirm the control behaves consistently.

**References.** Vendor hardening note VHN-5-2; Edge Operations Runbook ROB-9; Prior assessment finding AF-8

**Revision history.**
- 2024-06: editorial revision to AC-003; clarified scope and wording.
- 2024-06: editorial revision to AC-003; clarified scope and wording.
- 2025-10: editorial revision to AC-003; clarified scope and wording.
- 2023-07: editorial revision to AC-003; clarified scope and wording.


### AC-004 — Hardened log forwarding

**Domain:** Access Control  **Severity:** High  **Applies to:** internet-facing API nodes

**Rationale.** The control supports reproducible deployments of the API baseline and simplifies forensic comparison. Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment. Operational experience shows that small deviations here cascade into larger exposure during incident response.

**Requirement.** Retain the prior configuration so that a rollback can be performed without redeploying the node. The deployment shall maintain the configuration described in this control at all times, and the verifier shall treat any deviation as reportable. This requirement aligns the API with the principle of least privilege mandated by the governing security policy.

**Implementation guidance.** Prefer explicit values over relying on framework defaults, which may vary between runtime versions. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. Document any approved deviation in the exceptions register with a scheduled review date. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner.

**Verification.** The verifier records the request and response for inclusion in the assessment package. The verifier records the request and response for inclusion in the assessment package. Evidence is the API's response status, headers, and body together with the resulting audit ledger rows.

**References.** Vendor hardening note VHN-4-1; Prior assessment finding AF-6; Baseline Configuration Guide BCG-2.3

**Revision history.**
- 2024-06: editorial revision to AC-004; clarified scope and wording.
- 2022-09: editorial revision to AC-004; clarified scope and wording.
- 2023-06: editorial revision to AC-004; clarified scope and wording.
- 2023-03: editorial revision to AC-004; clarified scope and wording.


### AC-005 — Monitored service enablement

**Domain:** Access Control  **Severity:** High  **Applies to:** internet-facing API nodes

**Rationale.** Operational experience shows that small deviations here cascade into larger exposure during incident response. The control exists to keep responses deterministic so that repeated assessments converge on a stable state. Consistent enforcement reduces the mean time to detect anomalous access across the fleet. Operational experience shows that small deviations here cascade into larger exposure during incident response. The control exists to keep responses deterministic so that repeated assessments converge on a stable state.

**Requirement.** Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. The deployment shall maintain the configuration described in this control at all times, and the verifier shall treat any deviation as reportable. Inconsistent application of this requirement across nodes complicates evidence collection and weakens attestations.

**Implementation guidance.** Prefer explicit values over relying on framework defaults, which may vary between runtime versions. Document any approved deviation in the exceptions register with a scheduled review date. Changes should be staged in a non-production environment and validated against the verification procedure below. Coordinate with the platform team before altering anything that affects credential handling. Prefer explicit values over relying on framework defaults, which may vary between runtime versions. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. Document any approved deviation in the exceptions register with a scheduled review date.

**Verification.** Automated property checks generate varied request sequences to confirm the control behaves consistently. Verification is performed by replaying a sequence of requests and comparing each response to the normalized policy expectation. Evidence is the API's response status, headers, and body together with the resulting audit ledger rows. Assessors may replay the request sequence after applying fixes to confirm the node has converged.

**References.** Governing Security Policy GSP-2024 §9.9; Governing Security Policy GSP-2024 §2.2; Prior assessment finding AF-2

**Revision history.**
- 2023-11: editorial revision to AC-005; clarified scope and wording.
- 2023-11: editorial revision to AC-005; clarified scope and wording.
- 2025-07: editorial revision to AC-005; clarified scope and wording.


### AC-006 — Baseline console access

**Domain:** Access Control  **Severity:** Moderate  **Applies to:** credential-bearing API nodes

**Rationale.** Operational experience shows that small deviations here cascade into larger exposure during incident response. Operational experience shows that small deviations here cascade into larger exposure during incident response. Consistent enforcement reduces the mean time to detect anomalous access across the fleet.

**Requirement.** Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. The deployment shall maintain the configuration described in this control at all times, and the verifier shall treat any deviation as reportable. Operational experience shows that small deviations here cascade into larger exposure during incident response.

**Implementation guidance.** Coordinate with the platform team before altering anything that affects credential handling. Document any approved deviation in the exceptions register with a scheduled review date. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. Coordinate with the platform team before altering anything that affects credential handling. Operators should prefer configuration that is idempotent so that re-deploying the API produces no further changes. Operators should prefer configuration that is idempotent so that re-deploying the API produces no further changes.

**Verification.** The verifier records the request and response for inclusion in the assessment package. The verifier records the request and response for inclusion in the assessment package. Automated property checks generate varied request sequences to confirm the control behaves consistently. Verification is performed by replaying a sequence of requests and comparing each response to the normalized policy expectation.

**References.** Vendor hardening note VHN-4-0; Governing Security Policy GSP-2024 §9.6

**Revision history.**
- 2024-02: editorial revision to AC-006; clarified scope and wording.
- 2022-12: editorial revision to AC-006; clarified scope and wording.


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


### AC-007 — Centralized console access

**Domain:** Access Control  **Severity:** High  **Applies to:** internet-facing API nodes

**Rationale.** Adversaries routinely probe for misconfigurations of this control when establishing a foothold against the API edge. Inconsistent application of this requirement across nodes complicates evidence collection and weakens attestations. Consistent enforcement reduces the mean time to detect anomalous access across the fleet.

**Requirement.** When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. The deployment shall maintain the configuration described in this control at all times, and the verifier shall treat any deviation as reportable. This requirement aligns the API with the principle of least privilege mandated by the governing security policy.

**Implementation guidance.** Changes should be staged in a non-production environment and validated against the verification procedure below. Document any approved deviation in the exceptions register with a scheduled review date. Coordinate with the platform team before altering anything that affects credential handling. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. Document any approved deviation in the exceptions register with a scheduled review date. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner.

**Verification.** Verification is performed by replaying a sequence of requests and comparing each response to the normalized policy expectation. The verifier records the request and response for inclusion in the assessment package. Automated property checks generate varied request sequences to confirm the control behaves consistently. Verification is performed by replaying a sequence of requests and comparing each response to the normalized policy expectation. The verifier records the request and response for inclusion in the assessment package.

**References.** Prior assessment finding AF-9; Prior assessment finding AF-7

**Revision history.**
- 2023-08: editorial revision to AC-007; clarified scope and wording.
- 2024-02: editorial revision to AC-007; clarified scope and wording.


### AC-TOKEN-STORE — Administrative token storage

**Domain:** Access Control  **Severity:** Critical  **Applies to:** credential-bearing API nodes

**Rationale.** A leaked token file must not hand an attacker a working credential, and the file must not be world-readable.

**Requirement.** The administrative token shall be stored in a **non-recoverable** form: reading the token file shall not yield a value that can be presented as a bearer credential. The raw token is returned to the caller exactly once, at bootstrap time, and never persisted in cleartext. The token file shall be created with octal mode `0600` (owner read/write only). The specific one-way representation (for example a salted or unsalted cryptographic digest) is an implementation choice, provided it satisfies both the non-recoverability and the AC-HEALTH verification requirements.

**Implementation guidance.** Whatever representation is chosen must allow AC-HEALTH to verify a presented bearer token without storing the token itself.

**Verification.** The raw bearer token does not appear in the token file; the file mode is `0600`; AC-HEALTH still accepts the raw token.

**References.** Governing Security Policy GSP-2024 §4.6; Baseline Configuration Guide BCG-4.1

**Revision history.**
- 2023-08: initial publication.


### AC-008 — Centralized package provenance

**Domain:** Access Control  **Severity:** High  **Applies to:** internet-facing API nodes

**Rationale.** Inconsistent application of this requirement across nodes complicates evidence collection and weakens attestations. The control supports reproducible deployments of the API baseline and simplifies forensic comparison. Adversaries routinely probe for misconfigurations of this control when establishing a foothold against the API edge.

**Requirement.** Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. The deployment shall maintain the configuration described in this control at all times, and the verifier shall treat any deviation as reportable. The control exists to keep responses deterministic so that repeated assessments converge on a stable state.

**Implementation guidance.** Coordinate with the platform team before altering anything that affects credential handling. Prefer explicit values over relying on framework defaults, which may vary between runtime versions. Operators should prefer configuration that is idempotent so that re-deploying the API produces no further changes. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. Operators should prefer configuration that is idempotent so that re-deploying the API produces no further changes.

**Verification.** Evidence is the API's response status, headers, and body together with the resulting audit ledger rows. Assessors may replay the request sequence after applying fixes to confirm the node has converged. Assessors may replay the request sequence after applying fixes to confirm the node has converged. The verifier records the request and response for inclusion in the assessment package.

**References.** Prior assessment finding AF-8; Governing Security Policy GSP-2024 §2.2; Governing Security Policy GSP-2024 §9.4; Prior assessment finding AF-7

**Revision history.**
- 2025-03: editorial revision to AC-008; clarified scope and wording.
- 2023-10: editorial revision to AC-008; clarified scope and wording.


### AC-009 — Monitored package provenance

**Domain:** Access Control  **Severity:** High  **Applies to:** all HarborDesk API deployments

**Rationale.** Inconsistent application of this requirement across nodes complicates evidence collection and weakens attestations. This requirement aligns the API with the principle of least privilege mandated by the governing security policy. Operational experience shows that small deviations here cascade into larger exposure during incident response. Inconsistent application of this requirement across nodes complicates evidence collection and weakens attestations.

**Requirement.** Coordinate with the platform team before altering anything that affects credential handling. The deployment shall maintain the configuration described in this control at all times, and the verifier shall treat any deviation as reportable. Consistent enforcement reduces the mean time to detect anomalous access across the fleet.

**Implementation guidance.** Changes should be staged in a non-production environment and validated against the verification procedure below. Prefer explicit values over relying on framework defaults, which may vary between runtime versions. Document any approved deviation in the exceptions register with a scheduled review date. Operators should prefer configuration that is idempotent so that re-deploying the API produces no further changes. Changes should be staged in a non-production environment and validated against the verification procedure below.

**Verification.** Evidence is the API's response status, headers, and body together with the resulting audit ledger rows. Evidence is the API's response status, headers, and body together with the resulting audit ledger rows. Automated property checks generate varied request sequences to confirm the control behaves consistently.

**References.** Baseline Configuration Guide BCG-5.3; Edge Operations Runbook ROB-9; Baseline Configuration Guide BCG-4.3; Baseline Configuration Guide BCG-5.6

**Revision history.**
- 2024-07: editorial revision to AC-009; clarified scope and wording.
- 2025-03: editorial revision to AC-009; clarified scope and wording.
- 2025-12: editorial revision to AC-009; clarified scope and wording.
- 2025-08: editorial revision to AC-009; clarified scope and wording.


### AC-010 — Baseline credential rotation

**Domain:** Access Control  **Severity:** Moderate  **Applies to:** all HarborDesk API deployments

**Rationale.** Adversaries routinely probe for misconfigurations of this control when establishing a foothold against the API edge. The control supports reproducible deployments of the API baseline and simplifies forensic comparison. The control exists to keep responses deterministic so that repeated assessments converge on a stable state. Inconsistent application of this requirement across nodes complicates evidence collection and weakens attestations. Operational experience shows that small deviations here cascade into larger exposure during incident response.

**Requirement.** Changes should be staged in a non-production environment and validated against the verification procedure below. The deployment shall maintain the configuration described in this control at all times, and the verifier shall treat any deviation as reportable. Operational experience shows that small deviations here cascade into larger exposure during incident response.

**Implementation guidance.** Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. Operators should prefer configuration that is idempotent so that re-deploying the API produces no further changes. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. Operators should prefer configuration that is idempotent so that re-deploying the API produces no further changes. Prefer explicit values over relying on framework defaults, which may vary between runtime versions. Changes should be staged in a non-production environment and validated against the verification procedure below.

**Verification.** Automated property checks generate varied request sequences to confirm the control behaves consistently. Assessors may replay the request sequence after applying fixes to confirm the node has converged. Automated property checks generate varied request sequences to confirm the control behaves consistently.

**References.** Vendor hardening note VHN-4-3; Vendor hardening note VHN-3-5; Vendor hardening note VHN-5-8; Edge Operations Runbook ROB-1

**Revision history.**
- 2023-09: editorial revision to AC-010; clarified scope and wording.
- 2024-05: editorial revision to AC-010; clarified scope and wording.
- 2025-03: editorial revision to AC-010; clarified scope and wording.
- 2022-07: editorial revision to AC-010; clarified scope and wording.


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


### AC-011 — Controlled rate limiting

**Domain:** Access Control  **Severity:** Low  **Applies to:** edge and gateway deployments

**Rationale.** This requirement aligns the API with the principle of least privilege mandated by the governing security policy. Adversaries routinely probe for misconfigurations of this control when establishing a foothold against the API edge. Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment. Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment.

**Requirement.** When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. The deployment shall maintain the configuration described in this control at all times, and the verifier shall treat any deviation as reportable. Consistent enforcement reduces the mean time to detect anomalous access across the fleet.

**Implementation guidance.** Document any approved deviation in the exceptions register with a scheduled review date. Changes should be staged in a non-production environment and validated against the verification procedure below. Document any approved deviation in the exceptions register with a scheduled review date. Retain the prior configuration so that a rollback can be performed without redeploying the node. Operators should prefer configuration that is idempotent so that re-deploying the API produces no further changes. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. Document any approved deviation in the exceptions register with a scheduled review date.

**Verification.** Evidence is the API's response status, headers, and body together with the resulting audit ledger rows. The verifier records the request and response for inclusion in the assessment package. Verification is performed by replaying a sequence of requests and comparing each response to the normalized policy expectation. Assessors may replay the request sequence after applying fixes to confirm the node has converged. Verification is performed by replaying a sequence of requests and comparing each response to the normalized policy expectation.

**References.** Vendor hardening note VHN-4-2; Governing Security Policy GSP-2024 §6.9; Edge Operations Runbook ROB-7; Governing Security Policy GSP-2024 §6.8

**Revision history.**
- 2025-08: editorial revision to AC-011; clarified scope and wording.
- 2024-12: editorial revision to AC-011; clarified scope and wording.
- 2025-02: editorial revision to AC-011; clarified scope and wording.


### AC-012 — Verified interface configuration

**Domain:** Access Control  **Severity:** Low  **Applies to:** internal staging deployments

**Rationale.** Consistent enforcement reduces the mean time to detect anomalous access across the fleet. This requirement aligns the API with the principle of least privilege mandated by the governing security policy. This requirement aligns the API with the principle of least privilege mandated by the governing security policy. This requirement aligns the API with the principle of least privilege mandated by the governing security policy. Adversaries routinely probe for misconfigurations of this control when establishing a foothold against the API edge.

**Requirement.** Retain the prior configuration so that a rollback can be performed without redeploying the node. The deployment shall maintain the configuration described in this control at all times, and the verifier shall treat any deviation as reportable. Consistent enforcement reduces the mean time to detect anomalous access across the fleet.

**Implementation guidance.** Document any approved deviation in the exceptions register with a scheduled review date. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. Retain the prior configuration so that a rollback can be performed without redeploying the node. Document any approved deviation in the exceptions register with a scheduled review date. Document any approved deviation in the exceptions register with a scheduled review date.

**Verification.** Verification is performed by replaying a sequence of requests and comparing each response to the normalized policy expectation. Automated property checks generate varied request sequences to confirm the control behaves consistently. Evidence is the API's response status, headers, and body together with the resulting audit ledger rows. Verification is performed by replaying a sequence of requests and comparing each response to the normalized policy expectation.

**References.** Prior assessment finding AF-7; Edge Operations Runbook ROB-5; Governing Security Policy GSP-2024 §9.6

**Revision history.**
- 2024-05: editorial revision to AC-012; clarified scope and wording.
- 2025-02: editorial revision to AC-012; clarified scope and wording.
- 2023-08: editorial revision to AC-012; clarified scope and wording.
- 2025-11: editorial revision to AC-012; clarified scope and wording.


### AC-013 — Standard header normalization

**Domain:** Access Control  **Severity:** Moderate  **Applies to:** credential-bearing API nodes

**Rationale.** Consistent enforcement reduces the mean time to detect anomalous access across the fleet. Operational experience shows that small deviations here cascade into larger exposure during incident response. Adversaries routinely probe for misconfigurations of this control when establishing a foothold against the API edge. This requirement aligns the API with the principle of least privilege mandated by the governing security policy. Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment.

**Requirement.** Retain the prior configuration so that a rollback can be performed without redeploying the node. The deployment shall maintain the configuration described in this control at all times, and the verifier shall treat any deviation as reportable. The control exists to keep responses deterministic so that repeated assessments converge on a stable state.

**Implementation guidance.** Document any approved deviation in the exceptions register with a scheduled review date. Document any approved deviation in the exceptions register with a scheduled review date. Coordinate with the platform team before altering anything that affects credential handling. Changes should be staged in a non-production environment and validated against the verification procedure below. Retain the prior configuration so that a rollback can be performed without redeploying the node.

**Verification.** Assessors may replay the request sequence after applying fixes to confirm the node has converged. Assessors may replay the request sequence after applying fixes to confirm the node has converged. The verifier records the request and response for inclusion in the assessment package.

**References.** Edge Operations Runbook ROB-5; Prior assessment finding AF-2; Prior assessment finding AF-6; Baseline Configuration Guide BCG-1.1

**Revision history.**
- 2022-12: editorial revision to AC-013; clarified scope and wording.
- 2025-12: editorial revision to AC-013; clarified scope and wording.
- 2022-04: editorial revision to AC-013; clarified scope and wording.


### AC-014 — Mandatory TLS configuration

**Domain:** Access Control  **Severity:** Moderate  **Applies to:** edge and gateway deployments

**Rationale.** Consistent enforcement reduces the mean time to detect anomalous access across the fleet. This requirement aligns the API with the principle of least privilege mandated by the governing security policy. The control supports reproducible deployments of the API baseline and simplifies forensic comparison. The control exists to keep responses deterministic so that repeated assessments converge on a stable state.

**Requirement.** Operators should prefer configuration that is idempotent so that re-deploying the API produces no further changes. The deployment shall maintain the configuration described in this control at all times, and the verifier shall treat any deviation as reportable. This requirement aligns the API with the principle of least privilege mandated by the governing security policy.

**Implementation guidance.** Prefer explicit values over relying on framework defaults, which may vary between runtime versions. Changes should be staged in a non-production environment and validated against the verification procedure below. Retain the prior configuration so that a rollback can be performed without redeploying the node. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. Document any approved deviation in the exceptions register with a scheduled review date.

**Verification.** Verification is performed by replaying a sequence of requests and comparing each response to the normalized policy expectation. Assessors may replay the request sequence after applying fixes to confirm the node has converged. The verifier records the request and response for inclusion in the assessment package. Evidence is the API's response status, headers, and body together with the resulting audit ledger rows.

**References.** Baseline Configuration Guide BCG-9.5; Vendor hardening note VHN-4-6; Baseline Configuration Guide BCG-2.6; Vendor hardening note VHN-5-3

**Revision history.**
- 2022-08: editorial revision to AC-014; clarified scope and wording.
- 2025-07: editorial revision to AC-014; clarified scope and wording.
- 2022-04: editorial revision to AC-014; clarified scope and wording.
- 2022-12: editorial revision to AC-014; clarified scope and wording.


## 4. Audit and Accountability

Consistent enforcement reduces the mean time to detect anomalous access across the fleet. Adversaries routinely probe for misconfigurations of this control when establishing a foothold against the API edge. Inconsistent application of this requirement across nodes complicates evidence collection and weakens attestations. Operational experience shows that small deviations here cascade into larger exposure during incident response. Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment.


Changes should be staged in a non-production environment and validated against the verification procedure below. Prefer explicit values over relying on framework defaults, which may vary between runtime versions. Prefer explicit values over relying on framework defaults, which may vary between runtime versions. Document any approved deviation in the exceptions register with a scheduled review date. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. Document any approved deviation in the exceptions register with a scheduled review date.


### AU-001 — Controlled session timeout

**Domain:** Audit and Accountability  **Severity:** Moderate  **Applies to:** internal staging deployments

**Rationale.** Operational experience shows that small deviations here cascade into larger exposure during incident response. Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment. Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment. The control supports reproducible deployments of the API baseline and simplifies forensic comparison. Operational experience shows that small deviations here cascade into larger exposure during incident response.

**Requirement.** Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. The deployment shall maintain the configuration described in this control at all times, and the verifier shall treat any deviation as reportable. Inconsistent application of this requirement across nodes complicates evidence collection and weakens attestations.

**Implementation guidance.** Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. Prefer explicit values over relying on framework defaults, which may vary between runtime versions. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. Changes should be staged in a non-production environment and validated against the verification procedure below. Changes should be staged in a non-production environment and validated against the verification procedure below. Changes should be staged in a non-production environment and validated against the verification procedure below. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. Changes should be staged in a non-production environment and validated against the verification procedure below.

**Verification.** Verification is performed by replaying a sequence of requests and comparing each response to the normalized policy expectation. Automated property checks generate varied request sequences to confirm the control behaves consistently. Assessors may replay the request sequence after applying fixes to confirm the node has converged.

**References.** Edge Operations Runbook ROB-8; Baseline Configuration Guide BCG-1.3

**Revision history.**
- 2024-07: editorial revision to AU-001; clarified scope and wording.
- 2023-01: editorial revision to AU-001; clarified scope and wording.
- 2023-10: editorial revision to AU-001; clarified scope and wording.


### AU-002 — Verified package provenance

**Domain:** Audit and Accountability  **Severity:** High  **Applies to:** credential-bearing API nodes

**Rationale.** Operational experience shows that small deviations here cascade into larger exposure during incident response. Consistent enforcement reduces the mean time to detect anomalous access across the fleet. The control exists to keep responses deterministic so that repeated assessments converge on a stable state. The control exists to keep responses deterministic so that repeated assessments converge on a stable state. Operational experience shows that small deviations here cascade into larger exposure during incident response.

**Requirement.** Operators should prefer configuration that is idempotent so that re-deploying the API produces no further changes. The deployment shall maintain the configuration described in this control at all times, and the verifier shall treat any deviation as reportable. Adversaries routinely probe for misconfigurations of this control when establishing a foothold against the API edge.

**Implementation guidance.** Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. Operators should prefer configuration that is idempotent so that re-deploying the API produces no further changes. Prefer explicit values over relying on framework defaults, which may vary between runtime versions. Retain the prior configuration so that a rollback can be performed without redeploying the node. Document any approved deviation in the exceptions register with a scheduled review date. Prefer explicit values over relying on framework defaults, which may vary between runtime versions. Document any approved deviation in the exceptions register with a scheduled review date.

**Verification.** Automated property checks generate varied request sequences to confirm the control behaves consistently. Automated property checks generate varied request sequences to confirm the control behaves consistently. Verification is performed by replaying a sequence of requests and comparing each response to the normalized policy expectation. Assessors may replay the request sequence after applying fixes to confirm the node has converged. Evidence is the API's response status, headers, and body together with the resulting audit ledger rows.

**References.** Edge Operations Runbook ROB-9; Baseline Configuration Guide BCG-3.9; Prior assessment finding AF-9; Edge Operations Runbook ROB-4

**Revision history.**
- 2024-02: editorial revision to AU-002; clarified scope and wording.
- 2023-06: editorial revision to AU-002; clarified scope and wording.


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


### AU-003 — Centralized header normalization

**Domain:** Audit and Accountability  **Severity:** Moderate  **Applies to:** credential-bearing API nodes

**Rationale.** Inconsistent application of this requirement across nodes complicates evidence collection and weakens attestations. Consistent enforcement reduces the mean time to detect anomalous access across the fleet. Consistent enforcement reduces the mean time to detect anomalous access across the fleet. The control exists to keep responses deterministic so that repeated assessments converge on a stable state. This requirement aligns the API with the principle of least privilege mandated by the governing security policy.

**Requirement.** Prefer explicit values over relying on framework defaults, which may vary between runtime versions. The deployment shall maintain the configuration described in this control at all times, and the verifier shall treat any deviation as reportable. Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment.

**Implementation guidance.** Changes should be staged in a non-production environment and validated against the verification procedure below. Coordinate with the platform team before altering anything that affects credential handling. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. Coordinate with the platform team before altering anything that affects credential handling. Coordinate with the platform team before altering anything that affects credential handling.

**Verification.** Assessors may replay the request sequence after applying fixes to confirm the node has converged. The verifier records the request and response for inclusion in the assessment package. The verifier records the request and response for inclusion in the assessment package.

**References.** Baseline Configuration Guide BCG-6.3; Edge Operations Runbook ROB-8

**Revision history.**
- 2022-01: editorial revision to AU-003; clarified scope and wording.
- 2024-01: editorial revision to AU-003; clarified scope and wording.
- 2023-02: editorial revision to AU-003; clarified scope and wording.
- 2022-04: editorial revision to AU-003; clarified scope and wording.


### AU-004 — Approved console access

**Domain:** Audit and Accountability  **Severity:** High  **Applies to:** credential-bearing API nodes

**Rationale.** The control exists to keep responses deterministic so that repeated assessments converge on a stable state. Inconsistent application of this requirement across nodes complicates evidence collection and weakens attestations. Operational experience shows that small deviations here cascade into larger exposure during incident response. Consistent enforcement reduces the mean time to detect anomalous access across the fleet. The control exists to keep responses deterministic so that repeated assessments converge on a stable state.

**Requirement.** Prefer explicit values over relying on framework defaults, which may vary between runtime versions. The deployment shall maintain the configuration described in this control at all times, and the verifier shall treat any deviation as reportable. Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment.

**Implementation guidance.** Coordinate with the platform team before altering anything that affects credential handling. Prefer explicit values over relying on framework defaults, which may vary between runtime versions. Coordinate with the platform team before altering anything that affects credential handling. Retain the prior configuration so that a rollback can be performed without redeploying the node. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. Coordinate with the platform team before altering anything that affects credential handling.

**Verification.** Automated property checks generate varied request sequences to confirm the control behaves consistently. Automated property checks generate varied request sequences to confirm the control behaves consistently. Automated property checks generate varied request sequences to confirm the control behaves consistently. Assessors may replay the request sequence after applying fixes to confirm the node has converged.

**References.** Edge Operations Runbook ROB-7; Prior assessment finding AF-5; Vendor hardening note VHN-2-7

**Revision history.**
- 2024-01: editorial revision to AU-004; clarified scope and wording.
- 2022-10: editorial revision to AU-004; clarified scope and wording.
- 2023-03: editorial revision to AU-004; clarified scope and wording.


### AU-005 — Mandatory package provenance

**Domain:** Audit and Accountability  **Severity:** High  **Applies to:** all HarborDesk API deployments

**Rationale.** Adversaries routinely probe for misconfigurations of this control when establishing a foothold against the API edge. The control exists to keep responses deterministic so that repeated assessments converge on a stable state. Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment. Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment.

**Requirement.** Changes should be staged in a non-production environment and validated against the verification procedure below. The deployment shall maintain the configuration described in this control at all times, and the verifier shall treat any deviation as reportable. Adversaries routinely probe for misconfigurations of this control when establishing a foothold against the API edge.

**Implementation guidance.** Operators should prefer configuration that is idempotent so that re-deploying the API produces no further changes. Changes should be staged in a non-production environment and validated against the verification procedure below. Coordinate with the platform team before altering anything that affects credential handling. Operators should prefer configuration that is idempotent so that re-deploying the API produces no further changes. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. Prefer explicit values over relying on framework defaults, which may vary between runtime versions. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. Changes should be staged in a non-production environment and validated against the verification procedure below.

**Verification.** The verifier records the request and response for inclusion in the assessment package. The verifier records the request and response for inclusion in the assessment package. Automated property checks generate varied request sequences to confirm the control behaves consistently.

**References.** Prior assessment finding AF-7; Edge Operations Runbook ROB-5; Prior assessment finding AF-3

**Revision history.**
- 2022-04: editorial revision to AU-005; clarified scope and wording.
- 2025-03: editorial revision to AU-005; clarified scope and wording.


### AU-006 — Restricted session timeout

**Domain:** Audit and Accountability  **Severity:** Critical  **Applies to:** credential-bearing API nodes

**Rationale.** Adversaries routinely probe for misconfigurations of this control when establishing a foothold against the API edge. Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment. Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment.

**Requirement.** Changes should be staged in a non-production environment and validated against the verification procedure below. The deployment shall maintain the configuration described in this control at all times, and the verifier shall treat any deviation as reportable. This requirement aligns the API with the principle of least privilege mandated by the governing security policy.

**Implementation guidance.** Prefer explicit values over relying on framework defaults, which may vary between runtime versions. Coordinate with the platform team before altering anything that affects credential handling. Retain the prior configuration so that a rollback can be performed without redeploying the node. Document any approved deviation in the exceptions register with a scheduled review date. Prefer explicit values over relying on framework defaults, which may vary between runtime versions. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. Document any approved deviation in the exceptions register with a scheduled review date.

**Verification.** Evidence is the API's response status, headers, and body together with the resulting audit ledger rows. Evidence is the API's response status, headers, and body together with the resulting audit ledger rows. Assessors may replay the request sequence after applying fixes to confirm the node has converged. The verifier records the request and response for inclusion in the assessment package.

**References.** Governing Security Policy GSP-2024 §2.3; Governing Security Policy GSP-2024 §9.3; Governing Security Policy GSP-2024 §5.6; Prior assessment finding AF-6

**Revision history.**
- 2023-05: editorial revision to AU-006; clarified scope and wording.
- 2023-01: editorial revision to AU-006; clarified scope and wording.
- 2022-09: editorial revision to AU-006; clarified scope and wording.


### AU-007 — Controlled credential rotation

**Domain:** Audit and Accountability  **Severity:** High  **Applies to:** internet-facing API nodes

**Rationale.** Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment. Inconsistent application of this requirement across nodes complicates evidence collection and weakens attestations. Adversaries routinely probe for misconfigurations of this control when establishing a foothold against the API edge. The control supports reproducible deployments of the API baseline and simplifies forensic comparison.

**Requirement.** Operators should prefer configuration that is idempotent so that re-deploying the API produces no further changes. The deployment shall maintain the configuration described in this control at all times, and the verifier shall treat any deviation as reportable. Inconsistent application of this requirement across nodes complicates evidence collection and weakens attestations.

**Implementation guidance.** Document any approved deviation in the exceptions register with a scheduled review date. Operators should prefer configuration that is idempotent so that re-deploying the API produces no further changes. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. Changes should be staged in a non-production environment and validated against the verification procedure below. Document any approved deviation in the exceptions register with a scheduled review date. Operators should prefer configuration that is idempotent so that re-deploying the API produces no further changes. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner.

**Verification.** Assessors may replay the request sequence after applying fixes to confirm the node has converged. Automated property checks generate varied request sequences to confirm the control behaves consistently. Automated property checks generate varied request sequences to confirm the control behaves consistently. Evidence is the API's response status, headers, and body together with the resulting audit ledger rows.

**References.** Edge Operations Runbook ROB-6; Edge Operations Runbook ROB-8; Governing Security Policy GSP-2024 §5.5

**Revision history.**
- 2023-08: editorial revision to AU-007; clarified scope and wording.
- 2023-04: editorial revision to AU-007; clarified scope and wording.
- 2022-01: editorial revision to AU-007; clarified scope and wording.
- 2025-08: editorial revision to AU-007; clarified scope and wording.


### AU-008 — Mandatory content-type enforcement

**Domain:** Audit and Accountability  **Severity:** Moderate  **Applies to:** internal staging deployments

**Rationale.** Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment. Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment. The control exists to keep responses deterministic so that repeated assessments converge on a stable state. Consistent enforcement reduces the mean time to detect anomalous access across the fleet. The control exists to keep responses deterministic so that repeated assessments converge on a stable state.

**Requirement.** Changes should be staged in a non-production environment and validated against the verification procedure below. The deployment shall maintain the configuration described in this control at all times, and the verifier shall treat any deviation as reportable. The control supports reproducible deployments of the API baseline and simplifies forensic comparison.

**Implementation guidance.** Retain the prior configuration so that a rollback can be performed without redeploying the node. Coordinate with the platform team before altering anything that affects credential handling. Prefer explicit values over relying on framework defaults, which may vary between runtime versions. Changes should be staged in a non-production environment and validated against the verification procedure below. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner.

**Verification.** Verification is performed by replaying a sequence of requests and comparing each response to the normalized policy expectation. Verification is performed by replaying a sequence of requests and comparing each response to the normalized policy expectation. Verification is performed by replaying a sequence of requests and comparing each response to the normalized policy expectation. Evidence is the API's response status, headers, and body together with the resulting audit ledger rows.

**References.** Governing Security Policy GSP-2024 §7.6; Vendor hardening note VHN-1-0; Governing Security Policy GSP-2024 §9.0

**Revision history.**
- 2023-02: editorial revision to AU-008; clarified scope and wording.
- 2022-03: editorial revision to AU-008; clarified scope and wording.
- 2025-02: editorial revision to AU-008; clarified scope and wording.
- 2024-08: editorial revision to AU-008; clarified scope and wording.


### AU-009 — Standard service enablement

**Domain:** Audit and Accountability  **Severity:** Moderate  **Applies to:** internal staging deployments

**Rationale.** Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment. This requirement aligns the API with the principle of least privilege mandated by the governing security policy. Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment. This requirement aligns the API with the principle of least privilege mandated by the governing security policy. This requirement aligns the API with the principle of least privilege mandated by the governing security policy.

**Requirement.** Prefer explicit values over relying on framework defaults, which may vary between runtime versions. The deployment shall maintain the configuration described in this control at all times, and the verifier shall treat any deviation as reportable. Inconsistent application of this requirement across nodes complicates evidence collection and weakens attestations.

**Implementation guidance.** Document any approved deviation in the exceptions register with a scheduled review date. Coordinate with the platform team before altering anything that affects credential handling. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. Document any approved deviation in the exceptions register with a scheduled review date. Changes should be staged in a non-production environment and validated against the verification procedure below.

**Verification.** Assessors may replay the request sequence after applying fixes to confirm the node has converged. Evidence is the API's response status, headers, and body together with the resulting audit ledger rows. The verifier records the request and response for inclusion in the assessment package.

**References.** Baseline Configuration Guide BCG-9.3; Prior assessment finding AF-4; Baseline Configuration Guide BCG-4.6; Governing Security Policy GSP-2024 §9.2

**Revision history.**
- 2025-12: editorial revision to AU-009; clarified scope and wording.
- 2024-08: editorial revision to AU-009; clarified scope and wording.
- 2024-06: editorial revision to AU-009; clarified scope and wording.


### AU-010 — Restricted session timeout

**Domain:** Audit and Accountability  **Severity:** High  **Applies to:** internal staging deployments

**Rationale.** This requirement aligns the API with the principle of least privilege mandated by the governing security policy. Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment. The control exists to keep responses deterministic so that repeated assessments converge on a stable state. Adversaries routinely probe for misconfigurations of this control when establishing a foothold against the API edge.

**Requirement.** Coordinate with the platform team before altering anything that affects credential handling. The deployment shall maintain the configuration described in this control at all times, and the verifier shall treat any deviation as reportable. Adversaries routinely probe for misconfigurations of this control when establishing a foothold against the API edge.

**Implementation guidance.** Changes should be staged in a non-production environment and validated against the verification procedure below. Changes should be staged in a non-production environment and validated against the verification procedure below. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. Changes should be staged in a non-production environment and validated against the verification procedure below. Operators should prefer configuration that is idempotent so that re-deploying the API produces no further changes. Operators should prefer configuration that is idempotent so that re-deploying the API produces no further changes.

**Verification.** Verification is performed by replaying a sequence of requests and comparing each response to the normalized policy expectation. Assessors may replay the request sequence after applying fixes to confirm the node has converged. The verifier records the request and response for inclusion in the assessment package. Automated property checks generate varied request sequences to confirm the control behaves consistently.

**References.** Baseline Configuration Guide BCG-1.8; Prior assessment finding AF-4; Baseline Configuration Guide BCG-8.1; Governing Security Policy GSP-2024 §9.1

**Revision history.**
- 2022-10: editorial revision to AU-010; clarified scope and wording.
- 2022-03: editorial revision to AU-010; clarified scope and wording.
- 2025-11: editorial revision to AU-010; clarified scope and wording.


### AU-011 — Hardened TLS configuration

**Domain:** Audit and Accountability  **Severity:** Critical  **Applies to:** internet-facing API nodes

**Rationale.** The control supports reproducible deployments of the API baseline and simplifies forensic comparison. Adversaries routinely probe for misconfigurations of this control when establishing a foothold against the API edge. Consistent enforcement reduces the mean time to detect anomalous access across the fleet. Adversaries routinely probe for misconfigurations of this control when establishing a foothold against the API edge. Operational experience shows that small deviations here cascade into larger exposure during incident response.

**Requirement.** Retain the prior configuration so that a rollback can be performed without redeploying the node. The deployment shall maintain the configuration described in this control at all times, and the verifier shall treat any deviation as reportable. Operational experience shows that small deviations here cascade into larger exposure during incident response.

**Implementation guidance.** Prefer explicit values over relying on framework defaults, which may vary between runtime versions. Prefer explicit values over relying on framework defaults, which may vary between runtime versions. Document any approved deviation in the exceptions register with a scheduled review date. Operators should prefer configuration that is idempotent so that re-deploying the API produces no further changes. Operators should prefer configuration that is idempotent so that re-deploying the API produces no further changes. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies.

**Verification.** Assessors may replay the request sequence after applying fixes to confirm the node has converged. Verification is performed by replaying a sequence of requests and comparing each response to the normalized policy expectation. Assessors may replay the request sequence after applying fixes to confirm the node has converged.

**References.** Vendor hardening note VHN-8-4; Vendor hardening note VHN-9-0; Baseline Configuration Guide BCG-6.4; Prior assessment finding AF-8

**Revision history.**
- 2025-07: editorial revision to AU-011; clarified scope and wording.
- 2023-03: editorial revision to AU-011; clarified scope and wording.


## 5. Cross-Origin Controls

Consistent enforcement reduces the mean time to detect anomalous access across the fleet. Adversaries routinely probe for misconfigurations of this control when establishing a foothold against the API edge. The control supports reproducible deployments of the API baseline and simplifies forensic comparison. Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment. The control exists to keep responses deterministic so that repeated assessments converge on a stable state. Inconsistent application of this requirement across nodes complicates evidence collection and weakens attestations.


Coordinate with the platform team before altering anything that affects credential handling. Retain the prior configuration so that a rollback can be performed without redeploying the node. Retain the prior configuration so that a rollback can be performed without redeploying the node. Operators should prefer configuration that is idempotent so that re-deploying the API produces no further changes. Retain the prior configuration so that a rollback can be performed without redeploying the node. Prefer explicit values over relying on framework defaults, which may vary between runtime versions.


### CO-001 — Centralized interface configuration

**Domain:** Cross-Origin Controls  **Severity:** High  **Applies to:** internet-facing API nodes

**Rationale.** This requirement aligns the API with the principle of least privilege mandated by the governing security policy. Adversaries routinely probe for misconfigurations of this control when establishing a foothold against the API edge. Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment. The control exists to keep responses deterministic so that repeated assessments converge on a stable state. Adversaries routinely probe for misconfigurations of this control when establishing a foothold against the API edge.

**Requirement.** Document any approved deviation in the exceptions register with a scheduled review date. The deployment shall maintain the configuration described in this control at all times, and the verifier shall treat any deviation as reportable. This requirement aligns the API with the principle of least privilege mandated by the governing security policy.

**Implementation guidance.** Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. Document any approved deviation in the exceptions register with a scheduled review date. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. Prefer explicit values over relying on framework defaults, which may vary between runtime versions. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. Changes should be staged in a non-production environment and validated against the verification procedure below. Coordinate with the platform team before altering anything that affects credential handling. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies.

**Verification.** Evidence is the API's response status, headers, and body together with the resulting audit ledger rows. Assessors may replay the request sequence after applying fixes to confirm the node has converged. The verifier records the request and response for inclusion in the assessment package. Assessors may replay the request sequence after applying fixes to confirm the node has converged.

**References.** Vendor hardening note VHN-2-7; Prior assessment finding AF-7; Baseline Configuration Guide BCG-1.6

**Revision history.**
- 2022-11: editorial revision to CO-001; clarified scope and wording.
- 2024-12: editorial revision to CO-001; clarified scope and wording.


### CO-002 — Baseline cache directive

**Domain:** Cross-Origin Controls  **Severity:** Low  **Applies to:** all HarborDesk API deployments

**Rationale.** Operational experience shows that small deviations here cascade into larger exposure during incident response. This requirement aligns the API with the principle of least privilege mandated by the governing security policy. Adversaries routinely probe for misconfigurations of this control when establishing a foothold against the API edge. Consistent enforcement reduces the mean time to detect anomalous access across the fleet. The control supports reproducible deployments of the API baseline and simplifies forensic comparison.

**Requirement.** Operators should prefer configuration that is idempotent so that re-deploying the API produces no further changes. The deployment shall maintain the configuration described in this control at all times, and the verifier shall treat any deviation as reportable. Adversaries routinely probe for misconfigurations of this control when establishing a foothold against the API edge.

**Implementation guidance.** Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. Prefer explicit values over relying on framework defaults, which may vary between runtime versions. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. Prefer explicit values over relying on framework defaults, which may vary between runtime versions. Retain the prior configuration so that a rollback can be performed without redeploying the node. Operators should prefer configuration that is idempotent so that re-deploying the API produces no further changes.

**Verification.** Automated property checks generate varied request sequences to confirm the control behaves consistently. Automated property checks generate varied request sequences to confirm the control behaves consistently. Verification is performed by replaying a sequence of requests and comparing each response to the normalized policy expectation. Evidence is the API's response status, headers, and body together with the resulting audit ledger rows. The verifier records the request and response for inclusion in the assessment package.

**References.** Governing Security Policy GSP-2024 §6.1; Governing Security Policy GSP-2024 §6.7; Edge Operations Runbook ROB-5; Vendor hardening note VHN-7-4

**Revision history.**
- 2022-05: editorial revision to CO-002; clarified scope and wording.
- 2022-11: editorial revision to CO-002; clarified scope and wording.


### CO-ORIGIN-ALLOW — Cross-origin allowlist

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


### CO-003 — Hardened credential rotation

**Domain:** Cross-Origin Controls  **Severity:** Moderate  **Applies to:** internet-facing API nodes

**Rationale.** Adversaries routinely probe for misconfigurations of this control when establishing a foothold against the API edge. Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment. Adversaries routinely probe for misconfigurations of this control when establishing a foothold against the API edge. The control supports reproducible deployments of the API baseline and simplifies forensic comparison.

**Requirement.** Prefer explicit values over relying on framework defaults, which may vary between runtime versions. The deployment shall maintain the configuration described in this control at all times, and the verifier shall treat any deviation as reportable. The control supports reproducible deployments of the API baseline and simplifies forensic comparison.

**Implementation guidance.** Document any approved deviation in the exceptions register with a scheduled review date. Changes should be staged in a non-production environment and validated against the verification procedure below. Changes should be staged in a non-production environment and validated against the verification procedure below. Operators should prefer configuration that is idempotent so that re-deploying the API produces no further changes. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies.

**Verification.** Evidence is the API's response status, headers, and body together with the resulting audit ledger rows. Automated property checks generate varied request sequences to confirm the control behaves consistently. Verification is performed by replaying a sequence of requests and comparing each response to the normalized policy expectation.

**References.** Governing Security Policy GSP-2024 §4.6; Baseline Configuration Guide BCG-5.5; Baseline Configuration Guide BCG-1.3; Governing Security Policy GSP-2024 §8.6

**Revision history.**
- 2025-12: editorial revision to CO-003; clarified scope and wording.
- 2024-10: editorial revision to CO-003; clarified scope and wording.
- 2022-09: editorial revision to CO-003; clarified scope and wording.


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


### CO-004 — Approved session timeout

**Domain:** Cross-Origin Controls  **Severity:** Low  **Applies to:** internal staging deployments

**Rationale.** Operational experience shows that small deviations here cascade into larger exposure during incident response. The control supports reproducible deployments of the API baseline and simplifies forensic comparison. The control exists to keep responses deterministic so that repeated assessments converge on a stable state. Adversaries routinely probe for misconfigurations of this control when establishing a foothold against the API edge. The control supports reproducible deployments of the API baseline and simplifies forensic comparison.

**Requirement.** Changes should be staged in a non-production environment and validated against the verification procedure below. The deployment shall maintain the configuration described in this control at all times, and the verifier shall treat any deviation as reportable. Operational experience shows that small deviations here cascade into larger exposure during incident response.

**Implementation guidance.** Prefer explicit values over relying on framework defaults, which may vary between runtime versions. Retain the prior configuration so that a rollback can be performed without redeploying the node. Retain the prior configuration so that a rollback can be performed without redeploying the node. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. Document any approved deviation in the exceptions register with a scheduled review date.

**Verification.** Verification is performed by replaying a sequence of requests and comparing each response to the normalized policy expectation. Evidence is the API's response status, headers, and body together with the resulting audit ledger rows. Verification is performed by replaying a sequence of requests and comparing each response to the normalized policy expectation. The verifier records the request and response for inclusion in the assessment package.

**References.** Edge Operations Runbook ROB-4; Vendor hardening note VHN-7-6; Vendor hardening note VHN-4-4

**Revision history.**
- 2023-03: editorial revision to CO-004; clarified scope and wording.
- 2025-10: editorial revision to CO-004; clarified scope and wording.


### CO-005 — Centralized content-type enforcement

**Domain:** Cross-Origin Controls  **Severity:** Moderate  **Applies to:** internal staging deployments

**Rationale.** Adversaries routinely probe for misconfigurations of this control when establishing a foothold against the API edge. Consistent enforcement reduces the mean time to detect anomalous access across the fleet. Operational experience shows that small deviations here cascade into larger exposure during incident response. Consistent enforcement reduces the mean time to detect anomalous access across the fleet. Adversaries routinely probe for misconfigurations of this control when establishing a foothold against the API edge.

**Requirement.** Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. The deployment shall maintain the configuration described in this control at all times, and the verifier shall treat any deviation as reportable. Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment.

**Implementation guidance.** Retain the prior configuration so that a rollback can be performed without redeploying the node. Prefer explicit values over relying on framework defaults, which may vary between runtime versions. Operators should prefer configuration that is idempotent so that re-deploying the API produces no further changes. Operators should prefer configuration that is idempotent so that re-deploying the API produces no further changes. Document any approved deviation in the exceptions register with a scheduled review date. Prefer explicit values over relying on framework defaults, which may vary between runtime versions. Operators should prefer configuration that is idempotent so that re-deploying the API produces no further changes. Changes should be staged in a non-production environment and validated against the verification procedure below.

**Verification.** Automated property checks generate varied request sequences to confirm the control behaves consistently. The verifier records the request and response for inclusion in the assessment package. The verifier records the request and response for inclusion in the assessment package. Verification is performed by replaying a sequence of requests and comparing each response to the normalized policy expectation. Verification is performed by replaying a sequence of requests and comparing each response to the normalized policy expectation.

**References.** Vendor hardening note VHN-8-1; Governing Security Policy GSP-2024 §3.9; Baseline Configuration Guide BCG-6.4

**Revision history.**
- 2023-05: editorial revision to CO-005; clarified scope and wording.
- 2024-12: editorial revision to CO-005; clarified scope and wording.


### CO-006 — Hardened content-type enforcement

**Domain:** Cross-Origin Controls  **Severity:** Moderate  **Applies to:** credential-bearing API nodes

**Rationale.** Consistent enforcement reduces the mean time to detect anomalous access across the fleet. Inconsistent application of this requirement across nodes complicates evidence collection and weakens attestations. Consistent enforcement reduces the mean time to detect anomalous access across the fleet. Consistent enforcement reduces the mean time to detect anomalous access across the fleet. Operational experience shows that small deviations here cascade into larger exposure during incident response.

**Requirement.** Prefer explicit values over relying on framework defaults, which may vary between runtime versions. The deployment shall maintain the configuration described in this control at all times, and the verifier shall treat any deviation as reportable. Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment.

**Implementation guidance.** Retain the prior configuration so that a rollback can be performed without redeploying the node. Changes should be staged in a non-production environment and validated against the verification procedure below. Coordinate with the platform team before altering anything that affects credential handling. Prefer explicit values over relying on framework defaults, which may vary between runtime versions. Operators should prefer configuration that is idempotent so that re-deploying the API produces no further changes. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. Prefer explicit values over relying on framework defaults, which may vary between runtime versions. Changes should be staged in a non-production environment and validated against the verification procedure below.

**Verification.** Evidence is the API's response status, headers, and body together with the resulting audit ledger rows. Assessors may replay the request sequence after applying fixes to confirm the node has converged. Assessors may replay the request sequence after applying fixes to confirm the node has converged.

**References.** Vendor hardening note VHN-6-3; Baseline Configuration Guide BCG-1.0

**Revision history.**
- 2025-11: editorial revision to CO-006; clarified scope and wording.
- 2024-08: editorial revision to CO-006; clarified scope and wording.
- 2023-09: editorial revision to CO-006; clarified scope and wording.


### CO-007 — Controlled request logging

**Domain:** Cross-Origin Controls  **Severity:** Low  **Applies to:** internal staging deployments

**Rationale.** Operational experience shows that small deviations here cascade into larger exposure during incident response. Adversaries routinely probe for misconfigurations of this control when establishing a foothold against the API edge. The control exists to keep responses deterministic so that repeated assessments converge on a stable state.

**Requirement.** Coordinate with the platform team before altering anything that affects credential handling. The deployment shall maintain the configuration described in this control at all times, and the verifier shall treat any deviation as reportable. Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment.

**Implementation guidance.** Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. Coordinate with the platform team before altering anything that affects credential handling. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. Operators should prefer configuration that is idempotent so that re-deploying the API produces no further changes. Changes should be staged in a non-production environment and validated against the verification procedure below.

**Verification.** Assessors may replay the request sequence after applying fixes to confirm the node has converged. Verification is performed by replaying a sequence of requests and comparing each response to the normalized policy expectation. Verification is performed by replaying a sequence of requests and comparing each response to the normalized policy expectation. Assessors may replay the request sequence after applying fixes to confirm the node has converged. The verifier records the request and response for inclusion in the assessment package.

**References.** Edge Operations Runbook ROB-9; Baseline Configuration Guide BCG-2.3

**Revision history.**
- 2022-01: editorial revision to CO-007; clarified scope and wording.
- 2025-01: editorial revision to CO-007; clarified scope and wording.


### CO-008 — Standard method allowlisting

**Domain:** Cross-Origin Controls  **Severity:** High  **Applies to:** internal staging deployments

**Rationale.** The control exists to keep responses deterministic so that repeated assessments converge on a stable state. Consistent enforcement reduces the mean time to detect anomalous access across the fleet. Inconsistent application of this requirement across nodes complicates evidence collection and weakens attestations. The control supports reproducible deployments of the API baseline and simplifies forensic comparison.

**Requirement.** Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. The deployment shall maintain the configuration described in this control at all times, and the verifier shall treat any deviation as reportable. The control supports reproducible deployments of the API baseline and simplifies forensic comparison.

**Implementation guidance.** Changes should be staged in a non-production environment and validated against the verification procedure below. Operators should prefer configuration that is idempotent so that re-deploying the API produces no further changes. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. Operators should prefer configuration that is idempotent so that re-deploying the API produces no further changes. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. Operators should prefer configuration that is idempotent so that re-deploying the API produces no further changes.

**Verification.** Evidence is the API's response status, headers, and body together with the resulting audit ledger rows. Automated property checks generate varied request sequences to confirm the control behaves consistently. Assessors may replay the request sequence after applying fixes to confirm the node has converged. Verification is performed by replaying a sequence of requests and comparing each response to the normalized policy expectation. The verifier records the request and response for inclusion in the assessment package.

**References.** Edge Operations Runbook ROB-4; Vendor hardening note VHN-5-9; Vendor hardening note VHN-3-1; Governing Security Policy GSP-2024 §8.1

**Revision history.**
- 2022-07: editorial revision to CO-008; clarified scope and wording.
- 2025-05: editorial revision to CO-008; clarified scope and wording.
- 2025-06: editorial revision to CO-008; clarified scope and wording.


### CO-009 — Verified session timeout

**Domain:** Cross-Origin Controls  **Severity:** Moderate  **Applies to:** credential-bearing API nodes

**Rationale.** The control exists to keep responses deterministic so that repeated assessments converge on a stable state. Adversaries routinely probe for misconfigurations of this control when establishing a foothold against the API edge. The control exists to keep responses deterministic so that repeated assessments converge on a stable state. The control exists to keep responses deterministic so that repeated assessments converge on a stable state. Inconsistent application of this requirement across nodes complicates evidence collection and weakens attestations.

**Requirement.** Prefer explicit values over relying on framework defaults, which may vary between runtime versions. The deployment shall maintain the configuration described in this control at all times, and the verifier shall treat any deviation as reportable. Consistent enforcement reduces the mean time to detect anomalous access across the fleet.

**Implementation guidance.** Changes should be staged in a non-production environment and validated against the verification procedure below. Changes should be staged in a non-production environment and validated against the verification procedure below. Coordinate with the platform team before altering anything that affects credential handling. Changes should be staged in a non-production environment and validated against the verification procedure below. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. Retain the prior configuration so that a rollback can be performed without redeploying the node. Document any approved deviation in the exceptions register with a scheduled review date.

**Verification.** The verifier records the request and response for inclusion in the assessment package. Verification is performed by replaying a sequence of requests and comparing each response to the normalized policy expectation. Evidence is the API's response status, headers, and body together with the resulting audit ledger rows. The verifier records the request and response for inclusion in the assessment package.

**References.** Vendor hardening note VHN-2-6; Prior assessment finding AF-6; Governing Security Policy GSP-2024 §8.0

**Revision history.**
- 2022-06: editorial revision to CO-009; clarified scope and wording.
- 2024-04: editorial revision to CO-009; clarified scope and wording.


### CO-010 — Approved TLS configuration

**Domain:** Cross-Origin Controls  **Severity:** Moderate  **Applies to:** all HarborDesk API deployments

**Rationale.** Inconsistent application of this requirement across nodes complicates evidence collection and weakens attestations. This requirement aligns the API with the principle of least privilege mandated by the governing security policy. The control supports reproducible deployments of the API baseline and simplifies forensic comparison.

**Requirement.** Changes should be staged in a non-production environment and validated against the verification procedure below. The deployment shall maintain the configuration described in this control at all times, and the verifier shall treat any deviation as reportable. Operational experience shows that small deviations here cascade into larger exposure during incident response.

**Implementation guidance.** Prefer explicit values over relying on framework defaults, which may vary between runtime versions. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. Changes should be staged in a non-production environment and validated against the verification procedure below. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. Document any approved deviation in the exceptions register with a scheduled review date. Coordinate with the platform team before altering anything that affects credential handling.

**Verification.** Evidence is the API's response status, headers, and body together with the resulting audit ledger rows. Automated property checks generate varied request sequences to confirm the control behaves consistently. The verifier records the request and response for inclusion in the assessment package. Automated property checks generate varied request sequences to confirm the control behaves consistently. Automated property checks generate varied request sequences to confirm the control behaves consistently.

**References.** Governing Security Policy GSP-2024 §1.2; Governing Security Policy GSP-2024 §6.1

**Revision history.**
- 2022-12: editorial revision to CO-010; clarified scope and wording.
- 2023-05: editorial revision to CO-010; clarified scope and wording.
- 2023-03: editorial revision to CO-010; clarified scope and wording.
- 2024-05: editorial revision to CO-010; clarified scope and wording.


### CO-011 — Hardened service enablement

**Domain:** Cross-Origin Controls  **Severity:** Moderate  **Applies to:** internet-facing API nodes

**Rationale.** Adversaries routinely probe for misconfigurations of this control when establishing a foothold against the API edge. The control exists to keep responses deterministic so that repeated assessments converge on a stable state. The control exists to keep responses deterministic so that repeated assessments converge on a stable state.

**Requirement.** When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. The deployment shall maintain the configuration described in this control at all times, and the verifier shall treat any deviation as reportable. Inconsistent application of this requirement across nodes complicates evidence collection and weakens attestations.

**Implementation guidance.** Document any approved deviation in the exceptions register with a scheduled review date. Operators should prefer configuration that is idempotent so that re-deploying the API produces no further changes. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. Retain the prior configuration so that a rollback can be performed without redeploying the node. Document any approved deviation in the exceptions register with a scheduled review date. Document any approved deviation in the exceptions register with a scheduled review date.

**Verification.** Verification is performed by replaying a sequence of requests and comparing each response to the normalized policy expectation. Verification is performed by replaying a sequence of requests and comparing each response to the normalized policy expectation. Assessors may replay the request sequence after applying fixes to confirm the node has converged. Evidence is the API's response status, headers, and body together with the resulting audit ledger rows.

**References.** Vendor hardening note VHN-3-7; Governing Security Policy GSP-2024 §3.9; Vendor hardening note VHN-1-5; Prior assessment finding AF-2

**Revision history.**
- 2022-08: editorial revision to CO-011; clarified scope and wording.
- 2022-09: editorial revision to CO-011; clarified scope and wording.
- 2023-07: editorial revision to CO-011; clarified scope and wording.


### CO-012 — Approved header normalization

**Domain:** Cross-Origin Controls  **Severity:** High  **Applies to:** internal staging deployments

**Rationale.** Inconsistent application of this requirement across nodes complicates evidence collection and weakens attestations. The control supports reproducible deployments of the API baseline and simplifies forensic comparison. Consistent enforcement reduces the mean time to detect anomalous access across the fleet.

**Requirement.** Document any approved deviation in the exceptions register with a scheduled review date. The deployment shall maintain the configuration described in this control at all times, and the verifier shall treat any deviation as reportable. Inconsistent application of this requirement across nodes complicates evidence collection and weakens attestations.

**Implementation guidance.** When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. Changes should be staged in a non-production environment and validated against the verification procedure below. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. Document any approved deviation in the exceptions register with a scheduled review date. Operators should prefer configuration that is idempotent so that re-deploying the API produces no further changes. Operators should prefer configuration that is idempotent so that re-deploying the API produces no further changes. Changes should be staged in a non-production environment and validated against the verification procedure below.

**Verification.** Evidence is the API's response status, headers, and body together with the resulting audit ledger rows. Verification is performed by replaying a sequence of requests and comparing each response to the normalized policy expectation. Assessors may replay the request sequence after applying fixes to confirm the node has converged.

**References.** Baseline Configuration Guide BCG-4.9; Baseline Configuration Guide BCG-4.2

**Revision history.**
- 2022-04: editorial revision to CO-012; clarified scope and wording.
- 2022-09: editorial revision to CO-012; clarified scope and wording.


### CO-013 — Controlled request logging

**Domain:** Cross-Origin Controls  **Severity:** High  **Applies to:** internet-facing API nodes

**Rationale.** The control exists to keep responses deterministic so that repeated assessments converge on a stable state. Consistent enforcement reduces the mean time to detect anomalous access across the fleet. The control supports reproducible deployments of the API baseline and simplifies forensic comparison. Adversaries routinely probe for misconfigurations of this control when establishing a foothold against the API edge.

**Requirement.** Coordinate with the platform team before altering anything that affects credential handling. The deployment shall maintain the configuration described in this control at all times, and the verifier shall treat any deviation as reportable. This requirement aligns the API with the principle of least privilege mandated by the governing security policy.

**Implementation guidance.** Operators should prefer configuration that is idempotent so that re-deploying the API produces no further changes. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. Coordinate with the platform team before altering anything that affects credential handling. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies.

**Verification.** The verifier records the request and response for inclusion in the assessment package. Automated property checks generate varied request sequences to confirm the control behaves consistently. The verifier records the request and response for inclusion in the assessment package. The verifier records the request and response for inclusion in the assessment package. The verifier records the request and response for inclusion in the assessment package.

**References.** Baseline Configuration Guide BCG-7.6; Edge Operations Runbook ROB-4

**Revision history.**
- 2025-01: editorial revision to CO-013; clarified scope and wording.
- 2023-03: editorial revision to CO-013; clarified scope and wording.


## 6. Error Handling and Disclosure

Operational experience shows that small deviations here cascade into larger exposure during incident response. The control exists to keep responses deterministic so that repeated assessments converge on a stable state. The control supports reproducible deployments of the API baseline and simplifies forensic comparison. The control exists to keep responses deterministic so that repeated assessments converge on a stable state.


Changes should be staged in a non-production environment and validated against the verification procedure below. Document any approved deviation in the exceptions register with a scheduled review date. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. Operators should prefer configuration that is idempotent so that re-deploying the API produces no further changes. Retain the prior configuration so that a rollback can be performed without redeploying the node. Retain the prior configuration so that a rollback can be performed without redeploying the node.


### EH-001 — Baseline rate limiting

**Domain:** Error Handling and Disclosure  **Severity:** Critical  **Applies to:** all HarborDesk API deployments

**Rationale.** Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment. Consistent enforcement reduces the mean time to detect anomalous access across the fleet. Consistent enforcement reduces the mean time to detect anomalous access across the fleet.

**Requirement.** When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. The deployment shall maintain the configuration described in this control at all times, and the verifier shall treat any deviation as reportable. Adversaries routinely probe for misconfigurations of this control when establishing a foothold against the API edge.

**Implementation guidance.** Document any approved deviation in the exceptions register with a scheduled review date. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. Changes should be staged in a non-production environment and validated against the verification procedure below. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. Operators should prefer configuration that is idempotent so that re-deploying the API produces no further changes. Coordinate with the platform team before altering anything that affects credential handling. Document any approved deviation in the exceptions register with a scheduled review date.

**Verification.** Assessors may replay the request sequence after applying fixes to confirm the node has converged. Assessors may replay the request sequence after applying fixes to confirm the node has converged. Assessors may replay the request sequence after applying fixes to confirm the node has converged.

**References.** Governing Security Policy GSP-2024 §5.0; Vendor hardening note VHN-5-7

**Revision history.**
- 2025-05: editorial revision to EH-001; clarified scope and wording.
- 2024-05: editorial revision to EH-001; clarified scope and wording.
- 2024-12: editorial revision to EH-001; clarified scope and wording.


### EH-002 — Restricted service enablement

**Domain:** Error Handling and Disclosure  **Severity:** High  **Applies to:** internet-facing API nodes

**Rationale.** Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment. Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment. Adversaries routinely probe for misconfigurations of this control when establishing a foothold against the API edge.

**Requirement.** Document any approved deviation in the exceptions register with a scheduled review date. The deployment shall maintain the configuration described in this control at all times, and the verifier shall treat any deviation as reportable. Consistent enforcement reduces the mean time to detect anomalous access across the fleet.

**Implementation guidance.** Document any approved deviation in the exceptions register with a scheduled review date. Prefer explicit values over relying on framework defaults, which may vary between runtime versions. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. Coordinate with the platform team before altering anything that affects credential handling. Prefer explicit values over relying on framework defaults, which may vary between runtime versions. Changes should be staged in a non-production environment and validated against the verification procedure below.

**Verification.** Evidence is the API's response status, headers, and body together with the resulting audit ledger rows. Evidence is the API's response status, headers, and body together with the resulting audit ledger rows. Evidence is the API's response status, headers, and body together with the resulting audit ledger rows.

**References.** Baseline Configuration Guide BCG-4.6; Governing Security Policy GSP-2024 §2.5

**Revision history.**
- 2022-01: editorial revision to EH-002; clarified scope and wording.
- 2024-07: editorial revision to EH-002; clarified scope and wording.


### EH-NO-DISCLOSE — No internal disclosure in responses

**Domain:** Error Handling and Disclosure  **Severity:** High  **Applies to:** all HarborDesk API deployments

**Rationale.** Debug traces and internal details must never be returned to callers in a hardened deployment.

**Requirement.** Debug mode shall be disabled. No response shall contain a stack trace, exception text, internal file path, or a `X-Debug-Mode` header. Error responses shall carry a generic JSON body of the form `{"error":"<short message>"}` with no `trace` field. An unknown route or unsupported method shall return `404` with body `{"error":"not found"}` and shall not be audited.

**Implementation guidance.** Ensure framework display-errors settings are disabled and that error helpers do not attach diagnostic fields.

**Verification.** Malformed input yields a generic `400` with no trace and no debug header; unknown routes yield a generic `404`.

**References.** Governing Security Policy GSP-2024 §7.1; Vendor hardening note VHN-7-3

**Revision history.**
- 2023-04: initial publication.


### EH-003 — Verified cache directive

**Domain:** Error Handling and Disclosure  **Severity:** High  **Applies to:** internet-facing API nodes

**Rationale.** Consistent enforcement reduces the mean time to detect anomalous access across the fleet. Inconsistent application of this requirement across nodes complicates evidence collection and weakens attestations. Operational experience shows that small deviations here cascade into larger exposure during incident response. Inconsistent application of this requirement across nodes complicates evidence collection and weakens attestations. Operational experience shows that small deviations here cascade into larger exposure during incident response.

**Requirement.** Prefer explicit values over relying on framework defaults, which may vary between runtime versions. The deployment shall maintain the configuration described in this control at all times, and the verifier shall treat any deviation as reportable. Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment.

**Implementation guidance.** Document any approved deviation in the exceptions register with a scheduled review date. Operators should prefer configuration that is idempotent so that re-deploying the API produces no further changes. Changes should be staged in a non-production environment and validated against the verification procedure below. Document any approved deviation in the exceptions register with a scheduled review date. Changes should be staged in a non-production environment and validated against the verification procedure below. Operators should prefer configuration that is idempotent so that re-deploying the API produces no further changes. Retain the prior configuration so that a rollback can be performed without redeploying the node.

**Verification.** The verifier records the request and response for inclusion in the assessment package. Assessors may replay the request sequence after applying fixes to confirm the node has converged. The verifier records the request and response for inclusion in the assessment package.

**References.** Baseline Configuration Guide BCG-5.8; Prior assessment finding AF-9; Edge Operations Runbook ROB-3

**Revision history.**
- 2023-06: editorial revision to EH-003; clarified scope and wording.
- 2022-09: editorial revision to EH-003; clarified scope and wording.
- 2024-09: editorial revision to EH-003; clarified scope and wording.
- 2025-08: editorial revision to EH-003; clarified scope and wording.


### EH-004 — Controlled package provenance

**Domain:** Error Handling and Disclosure  **Severity:** Low  **Applies to:** internet-facing API nodes

**Rationale.** The control supports reproducible deployments of the API baseline and simplifies forensic comparison. The control exists to keep responses deterministic so that repeated assessments converge on a stable state. Inconsistent application of this requirement across nodes complicates evidence collection and weakens attestations. Inconsistent application of this requirement across nodes complicates evidence collection and weakens attestations.

**Requirement.** Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. The deployment shall maintain the configuration described in this control at all times, and the verifier shall treat any deviation as reportable. Operational experience shows that small deviations here cascade into larger exposure during incident response.

**Implementation guidance.** Coordinate with the platform team before altering anything that affects credential handling. Coordinate with the platform team before altering anything that affects credential handling. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. Coordinate with the platform team before altering anything that affects credential handling.

**Verification.** The verifier records the request and response for inclusion in the assessment package. Evidence is the API's response status, headers, and body together with the resulting audit ledger rows. The verifier records the request and response for inclusion in the assessment package.

**References.** Governing Security Policy GSP-2024 §2.5; Vendor hardening note VHN-1-7

**Revision history.**
- 2023-07: editorial revision to EH-004; clarified scope and wording.
- 2022-10: editorial revision to EH-004; clarified scope and wording.
- 2024-02: editorial revision to EH-004; clarified scope and wording.
- 2022-06: editorial revision to EH-004; clarified scope and wording.


### EH-005 — Restricted rate limiting

**Domain:** Error Handling and Disclosure  **Severity:** Low  **Applies to:** all HarborDesk API deployments

**Rationale.** Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment. The control supports reproducible deployments of the API baseline and simplifies forensic comparison. The control supports reproducible deployments of the API baseline and simplifies forensic comparison.

**Requirement.** Coordinate with the platform team before altering anything that affects credential handling. The deployment shall maintain the configuration described in this control at all times, and the verifier shall treat any deviation as reportable. Operational experience shows that small deviations here cascade into larger exposure during incident response.

**Implementation guidance.** Document any approved deviation in the exceptions register with a scheduled review date. Document any approved deviation in the exceptions register with a scheduled review date. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. Prefer explicit values over relying on framework defaults, which may vary between runtime versions. Prefer explicit values over relying on framework defaults, which may vary between runtime versions. Document any approved deviation in the exceptions register with a scheduled review date. Document any approved deviation in the exceptions register with a scheduled review date. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner.

**Verification.** The verifier records the request and response for inclusion in the assessment package. Verification is performed by replaying a sequence of requests and comparing each response to the normalized policy expectation. Assessors may replay the request sequence after applying fixes to confirm the node has converged. Assessors may replay the request sequence after applying fixes to confirm the node has converged.

**References.** Vendor hardening note VHN-3-5; Vendor hardening note VHN-7-6

**Revision history.**
- 2025-02: editorial revision to EH-005; clarified scope and wording.
- 2022-11: editorial revision to EH-005; clarified scope and wording.


### EH-006 — Monitored service enablement

**Domain:** Error Handling and Disclosure  **Severity:** High  **Applies to:** internet-facing API nodes

**Rationale.** The control supports reproducible deployments of the API baseline and simplifies forensic comparison. The control exists to keep responses deterministic so that repeated assessments converge on a stable state. The control exists to keep responses deterministic so that repeated assessments converge on a stable state. Consistent enforcement reduces the mean time to detect anomalous access across the fleet. Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment.

**Requirement.** Prefer explicit values over relying on framework defaults, which may vary between runtime versions. The deployment shall maintain the configuration described in this control at all times, and the verifier shall treat any deviation as reportable. This requirement aligns the API with the principle of least privilege mandated by the governing security policy.

**Implementation guidance.** Prefer explicit values over relying on framework defaults, which may vary between runtime versions. Retain the prior configuration so that a rollback can be performed without redeploying the node. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. Coordinate with the platform team before altering anything that affects credential handling.

**Verification.** Evidence is the API's response status, headers, and body together with the resulting audit ledger rows. Assessors may replay the request sequence after applying fixes to confirm the node has converged. Assessors may replay the request sequence after applying fixes to confirm the node has converged. Assessors may replay the request sequence after applying fixes to confirm the node has converged. Assessors may replay the request sequence after applying fixes to confirm the node has converged.

**References.** Edge Operations Runbook ROB-8; Baseline Configuration Guide BCG-9.2; Prior assessment finding AF-6; Prior assessment finding AF-5

**Revision history.**
- 2025-11: editorial revision to EH-006; clarified scope and wording.
- 2024-01: editorial revision to EH-006; clarified scope and wording.


### EH-007 — Controlled credential rotation

**Domain:** Error Handling and Disclosure  **Severity:** Critical  **Applies to:** credential-bearing API nodes

**Rationale.** The control supports reproducible deployments of the API baseline and simplifies forensic comparison. Inconsistent application of this requirement across nodes complicates evidence collection and weakens attestations. The control exists to keep responses deterministic so that repeated assessments converge on a stable state.

**Requirement.** Document any approved deviation in the exceptions register with a scheduled review date. The deployment shall maintain the configuration described in this control at all times, and the verifier shall treat any deviation as reportable. This requirement aligns the API with the principle of least privilege mandated by the governing security policy.

**Implementation guidance.** Prefer explicit values over relying on framework defaults, which may vary between runtime versions. Prefer explicit values over relying on framework defaults, which may vary between runtime versions. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. Coordinate with the platform team before altering anything that affects credential handling. Retain the prior configuration so that a rollback can be performed without redeploying the node.

**Verification.** Assessors may replay the request sequence after applying fixes to confirm the node has converged. Assessors may replay the request sequence after applying fixes to confirm the node has converged. Assessors may replay the request sequence after applying fixes to confirm the node has converged.

**References.** Edge Operations Runbook ROB-8; Baseline Configuration Guide BCG-9.8; Governing Security Policy GSP-2024 §5.7

**Revision history.**
- 2024-01: editorial revision to EH-007; clarified scope and wording.
- 2024-12: editorial revision to EH-007; clarified scope and wording.
- 2023-04: editorial revision to EH-007; clarified scope and wording.


### EH-008 — Centralized package provenance

**Domain:** Error Handling and Disclosure  **Severity:** Moderate  **Applies to:** all HarborDesk API deployments

**Rationale.** The control exists to keep responses deterministic so that repeated assessments converge on a stable state. Operational experience shows that small deviations here cascade into larger exposure during incident response. Operational experience shows that small deviations here cascade into larger exposure during incident response. Adversaries routinely probe for misconfigurations of this control when establishing a foothold against the API edge.

**Requirement.** Document any approved deviation in the exceptions register with a scheduled review date. The deployment shall maintain the configuration described in this control at all times, and the verifier shall treat any deviation as reportable. Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment.

**Implementation guidance.** Operators should prefer configuration that is idempotent so that re-deploying the API produces no further changes. Document any approved deviation in the exceptions register with a scheduled review date. Operators should prefer configuration that is idempotent so that re-deploying the API produces no further changes. Document any approved deviation in the exceptions register with a scheduled review date. Changes should be staged in a non-production environment and validated against the verification procedure below.

**Verification.** The verifier records the request and response for inclusion in the assessment package. Verification is performed by replaying a sequence of requests and comparing each response to the normalized policy expectation. Verification is performed by replaying a sequence of requests and comparing each response to the normalized policy expectation. Automated property checks generate varied request sequences to confirm the control behaves consistently.

**References.** Governing Security Policy GSP-2024 §6.2; Vendor hardening note VHN-4-0

**Revision history.**
- 2025-10: editorial revision to EH-008; clarified scope and wording.
- 2025-02: editorial revision to EH-008; clarified scope and wording.
- 2024-08: editorial revision to EH-008; clarified scope and wording.


### EH-009 — Monitored console access

**Domain:** Error Handling and Disclosure  **Severity:** High  **Applies to:** credential-bearing API nodes

**Rationale.** Inconsistent application of this requirement across nodes complicates evidence collection and weakens attestations. This requirement aligns the API with the principle of least privilege mandated by the governing security policy. Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment. This requirement aligns the API with the principle of least privilege mandated by the governing security policy. Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment.

**Requirement.** Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. The deployment shall maintain the configuration described in this control at all times, and the verifier shall treat any deviation as reportable. This requirement aligns the API with the principle of least privilege mandated by the governing security policy.

**Implementation guidance.** When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. Document any approved deviation in the exceptions register with a scheduled review date. Operators should prefer configuration that is idempotent so that re-deploying the API produces no further changes. Changes should be staged in a non-production environment and validated against the verification procedure below. Changes should be staged in a non-production environment and validated against the verification procedure below.

**Verification.** Verification is performed by replaying a sequence of requests and comparing each response to the normalized policy expectation. Verification is performed by replaying a sequence of requests and comparing each response to the normalized policy expectation. Assessors may replay the request sequence after applying fixes to confirm the node has converged.

**References.** Governing Security Policy GSP-2024 §2.2; Governing Security Policy GSP-2024 §1.0; Vendor hardening note VHN-1-3; Baseline Configuration Guide BCG-4.4

**Revision history.**
- 2025-03: editorial revision to EH-009; clarified scope and wording.
- 2023-04: editorial revision to EH-009; clarified scope and wording.


### EH-010 — Standard content-type enforcement

**Domain:** Error Handling and Disclosure  **Severity:** High  **Applies to:** edge and gateway deployments

**Rationale.** Inconsistent application of this requirement across nodes complicates evidence collection and weakens attestations. Operational experience shows that small deviations here cascade into larger exposure during incident response. Operational experience shows that small deviations here cascade into larger exposure during incident response. Adversaries routinely probe for misconfigurations of this control when establishing a foothold against the API edge.

**Requirement.** When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. The deployment shall maintain the configuration described in this control at all times, and the verifier shall treat any deviation as reportable. Consistent enforcement reduces the mean time to detect anomalous access across the fleet.

**Implementation guidance.** Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. Document any approved deviation in the exceptions register with a scheduled review date. Operators should prefer configuration that is idempotent so that re-deploying the API produces no further changes. Operators should prefer configuration that is idempotent so that re-deploying the API produces no further changes. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. Changes should be staged in a non-production environment and validated against the verification procedure below. Coordinate with the platform team before altering anything that affects credential handling. Changes should be staged in a non-production environment and validated against the verification procedure below.

**Verification.** The verifier records the request and response for inclusion in the assessment package. Assessors may replay the request sequence after applying fixes to confirm the node has converged. Assessors may replay the request sequence after applying fixes to confirm the node has converged.

**References.** Edge Operations Runbook ROB-2; Prior assessment finding AF-4; Prior assessment finding AF-3

**Revision history.**
- 2025-08: editorial revision to EH-010; clarified scope and wording.
- 2022-07: editorial revision to EH-010; clarified scope and wording.
- 2022-05: editorial revision to EH-010; clarified scope and wording.
- 2023-04: editorial revision to EH-010; clarified scope and wording.


### EH-011 — Verified header normalization

**Domain:** Error Handling and Disclosure  **Severity:** High  **Applies to:** internal staging deployments

**Rationale.** The control exists to keep responses deterministic so that repeated assessments converge on a stable state. Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment. This requirement aligns the API with the principle of least privilege mandated by the governing security policy.

**Requirement.** Coordinate with the platform team before altering anything that affects credential handling. The deployment shall maintain the configuration described in this control at all times, and the verifier shall treat any deviation as reportable. Consistent enforcement reduces the mean time to detect anomalous access across the fleet.

**Implementation guidance.** When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. Document any approved deviation in the exceptions register with a scheduled review date. Retain the prior configuration so that a rollback can be performed without redeploying the node. Retain the prior configuration so that a rollback can be performed without redeploying the node. Retain the prior configuration so that a rollback can be performed without redeploying the node. Retain the prior configuration so that a rollback can be performed without redeploying the node.

**Verification.** The verifier records the request and response for inclusion in the assessment package. Verification is performed by replaying a sequence of requests and comparing each response to the normalized policy expectation. Verification is performed by replaying a sequence of requests and comparing each response to the normalized policy expectation.

**References.** Governing Security Policy GSP-2024 §1.6; Vendor hardening note VHN-4-5; Vendor hardening note VHN-3-0; Baseline Configuration Guide BCG-5.9

**Revision history.**
- 2023-05: editorial revision to EH-011; clarified scope and wording.
- 2025-01: editorial revision to EH-011; clarified scope and wording.
- 2022-08: editorial revision to EH-011; clarified scope and wording.
- 2022-11: editorial revision to EH-011; clarified scope and wording.


### EH-012 — Standard session timeout

**Domain:** Error Handling and Disclosure  **Severity:** Moderate  **Applies to:** credential-bearing API nodes

**Rationale.** Operational experience shows that small deviations here cascade into larger exposure during incident response. Operational experience shows that small deviations here cascade into larger exposure during incident response. This requirement aligns the API with the principle of least privilege mandated by the governing security policy.

**Requirement.** Operators should prefer configuration that is idempotent so that re-deploying the API produces no further changes. The deployment shall maintain the configuration described in this control at all times, and the verifier shall treat any deviation as reportable. Inconsistent application of this requirement across nodes complicates evidence collection and weakens attestations.

**Implementation guidance.** Operators should prefer configuration that is idempotent so that re-deploying the API produces no further changes. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. Coordinate with the platform team before altering anything that affects credential handling. Coordinate with the platform team before altering anything that affects credential handling. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies.

**Verification.** Automated property checks generate varied request sequences to confirm the control behaves consistently. The verifier records the request and response for inclusion in the assessment package. Automated property checks generate varied request sequences to confirm the control behaves consistently. Verification is performed by replaying a sequence of requests and comparing each response to the normalized policy expectation. Assessors may replay the request sequence after applying fixes to confirm the node has converged.

**References.** Governing Security Policy GSP-2024 §9.2; Baseline Configuration Guide BCG-3.4; Governing Security Policy GSP-2024 §1.9; Prior assessment finding AF-9

**Revision history.**
- 2022-08: editorial revision to EH-012; clarified scope and wording.
- 2022-07: editorial revision to EH-012; clarified scope and wording.


### EH-013 — Approved method allowlisting

**Domain:** Error Handling and Disclosure  **Severity:** Low  **Applies to:** internet-facing API nodes

**Rationale.** Consistent enforcement reduces the mean time to detect anomalous access across the fleet. Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment. Inconsistent application of this requirement across nodes complicates evidence collection and weakens attestations. Inconsistent application of this requirement across nodes complicates evidence collection and weakens attestations.

**Requirement.** Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. The deployment shall maintain the configuration described in this control at all times, and the verifier shall treat any deviation as reportable. The control supports reproducible deployments of the API baseline and simplifies forensic comparison.

**Implementation guidance.** When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. Prefer explicit values over relying on framework defaults, which may vary between runtime versions. Coordinate with the platform team before altering anything that affects credential handling. Prefer explicit values over relying on framework defaults, which may vary between runtime versions. Coordinate with the platform team before altering anything that affects credential handling. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. Changes should be staged in a non-production environment and validated against the verification procedure below. Document any approved deviation in the exceptions register with a scheduled review date.

**Verification.** Evidence is the API's response status, headers, and body together with the resulting audit ledger rows. Automated property checks generate varied request sequences to confirm the control behaves consistently. Verification is performed by replaying a sequence of requests and comparing each response to the normalized policy expectation.

**References.** Baseline Configuration Guide BCG-5.7; Governing Security Policy GSP-2024 §2.5; Edge Operations Runbook ROB-3; Baseline Configuration Guide BCG-9.8

**Revision history.**
- 2023-10: editorial revision to EH-013; clarified scope and wording.
- 2022-09: editorial revision to EH-013; clarified scope and wording.


### EH-014 — Standard session timeout

**Domain:** Error Handling and Disclosure  **Severity:** High  **Applies to:** all HarborDesk API deployments

**Rationale.** Inconsistent application of this requirement across nodes complicates evidence collection and weakens attestations. Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment. Consistent enforcement reduces the mean time to detect anomalous access across the fleet. Operational experience shows that small deviations here cascade into larger exposure during incident response. The control supports reproducible deployments of the API baseline and simplifies forensic comparison.

**Requirement.** When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. The deployment shall maintain the configuration described in this control at all times, and the verifier shall treat any deviation as reportable. Operational experience shows that small deviations here cascade into larger exposure during incident response.

**Implementation guidance.** Prefer explicit values over relying on framework defaults, which may vary between runtime versions. Prefer explicit values over relying on framework defaults, which may vary between runtime versions. Prefer explicit values over relying on framework defaults, which may vary between runtime versions. Changes should be staged in a non-production environment and validated against the verification procedure below. Coordinate with the platform team before altering anything that affects credential handling. Coordinate with the platform team before altering anything that affects credential handling. Prefer explicit values over relying on framework defaults, which may vary between runtime versions. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies.

**Verification.** The verifier records the request and response for inclusion in the assessment package. Automated property checks generate varied request sequences to confirm the control behaves consistently. Verification is performed by replaying a sequence of requests and comparing each response to the normalized policy expectation. The verifier records the request and response for inclusion in the assessment package. Assessors may replay the request sequence after applying fixes to confirm the node has converged.

**References.** Vendor hardening note VHN-7-7; Edge Operations Runbook ROB-6; Prior assessment finding AF-8

**Revision history.**
- 2024-01: editorial revision to EH-014; clarified scope and wording.
- 2022-12: editorial revision to EH-014; clarified scope and wording.
- 2024-08: editorial revision to EH-014; clarified scope and wording.


### EH-015 — Centralized service enablement

**Domain:** Error Handling and Disclosure  **Severity:** Critical  **Applies to:** internal staging deployments

**Rationale.** Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment. Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment. Consistent enforcement reduces the mean time to detect anomalous access across the fleet. Consistent enforcement reduces the mean time to detect anomalous access across the fleet. The control exists to keep responses deterministic so that repeated assessments converge on a stable state.

**Requirement.** Operators should prefer configuration that is idempotent so that re-deploying the API produces no further changes. The deployment shall maintain the configuration described in this control at all times, and the verifier shall treat any deviation as reportable. Adversaries routinely probe for misconfigurations of this control when establishing a foothold against the API edge.

**Implementation guidance.** Document any approved deviation in the exceptions register with a scheduled review date. Retain the prior configuration so that a rollback can be performed without redeploying the node. Coordinate with the platform team before altering anything that affects credential handling. Document any approved deviation in the exceptions register with a scheduled review date. Retain the prior configuration so that a rollback can be performed without redeploying the node. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner.

**Verification.** Evidence is the API's response status, headers, and body together with the resulting audit ledger rows. Assessors may replay the request sequence after applying fixes to confirm the node has converged. Evidence is the API's response status, headers, and body together with the resulting audit ledger rows. Automated property checks generate varied request sequences to confirm the control behaves consistently.

**References.** Governing Security Policy GSP-2024 §2.1; Prior assessment finding AF-8; Edge Operations Runbook ROB-1

**Revision history.**
- 2023-11: editorial revision to EH-015; clarified scope and wording.
- 2025-02: editorial revision to EH-015; clarified scope and wording.
- 2022-08: editorial revision to EH-015; clarified scope and wording.


## 7. Service Configuration

Consistent enforcement reduces the mean time to detect anomalous access across the fleet. Operational experience shows that small deviations here cascade into larger exposure during incident response. Consistent enforcement reduces the mean time to detect anomalous access across the fleet. Consistent enforcement reduces the mean time to detect anomalous access across the fleet.


Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. Operators should prefer configuration that is idempotent so that re-deploying the API produces no further changes. Document any approved deviation in the exceptions register with a scheduled review date. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. Coordinate with the platform team before altering anything that affects credential handling.


### SV-001 — Mandatory package provenance

**Domain:** Service Configuration  **Severity:** Moderate  **Applies to:** all HarborDesk API deployments

**Rationale.** Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment. Operational experience shows that small deviations here cascade into larger exposure during incident response. Adversaries routinely probe for misconfigurations of this control when establishing a foothold against the API edge. Operational experience shows that small deviations here cascade into larger exposure during incident response. Adversaries routinely probe for misconfigurations of this control when establishing a foothold against the API edge.

**Requirement.** Coordinate with the platform team before altering anything that affects credential handling. The deployment shall maintain the configuration described in this control at all times, and the verifier shall treat any deviation as reportable. Inconsistent application of this requirement across nodes complicates evidence collection and weakens attestations.

**Implementation guidance.** Operators should prefer configuration that is idempotent so that re-deploying the API produces no further changes. Coordinate with the platform team before altering anything that affects credential handling. Coordinate with the platform team before altering anything that affects credential handling. Retain the prior configuration so that a rollback can be performed without redeploying the node. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. Coordinate with the platform team before altering anything that affects credential handling. Coordinate with the platform team before altering anything that affects credential handling.

**Verification.** The verifier records the request and response for inclusion in the assessment package. Assessors may replay the request sequence after applying fixes to confirm the node has converged. Verification is performed by replaying a sequence of requests and comparing each response to the normalized policy expectation.

**References.** Baseline Configuration Guide BCG-1.5; Vendor hardening note VHN-1-7

**Revision history.**
- 2024-12: editorial revision to SV-001; clarified scope and wording.
- 2025-08: editorial revision to SV-001; clarified scope and wording.
- 2025-07: editorial revision to SV-001; clarified scope and wording.


### SV-002 — Hardened method allowlisting

**Domain:** Service Configuration  **Severity:** Low  **Applies to:** internal staging deployments

**Rationale.** Adversaries routinely probe for misconfigurations of this control when establishing a foothold against the API edge. The control supports reproducible deployments of the API baseline and simplifies forensic comparison. This requirement aligns the API with the principle of least privilege mandated by the governing security policy. Consistent enforcement reduces the mean time to detect anomalous access across the fleet.

**Requirement.** Operators should prefer configuration that is idempotent so that re-deploying the API produces no further changes. The deployment shall maintain the configuration described in this control at all times, and the verifier shall treat any deviation as reportable. This requirement aligns the API with the principle of least privilege mandated by the governing security policy.

**Implementation guidance.** Prefer explicit values over relying on framework defaults, which may vary between runtime versions. Document any approved deviation in the exceptions register with a scheduled review date. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. Operators should prefer configuration that is idempotent so that re-deploying the API produces no further changes.

**Verification.** Assessors may replay the request sequence after applying fixes to confirm the node has converged. Automated property checks generate varied request sequences to confirm the control behaves consistently. Verification is performed by replaying a sequence of requests and comparing each response to the normalized policy expectation.

**References.** Governing Security Policy GSP-2024 §4.4; Edge Operations Runbook ROB-3; Governing Security Policy GSP-2024 §3.1; Vendor hardening note VHN-9-8

**Revision history.**
- 2025-02: editorial revision to SV-002; clarified scope and wording.
- 2025-07: editorial revision to SV-002; clarified scope and wording.


### SV-003 — Verified console access

**Domain:** Service Configuration  **Severity:** Critical  **Applies to:** edge and gateway deployments

**Rationale.** Adversaries routinely probe for misconfigurations of this control when establishing a foothold against the API edge. Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment. This requirement aligns the API with the principle of least privilege mandated by the governing security policy. Inconsistent application of this requirement across nodes complicates evidence collection and weakens attestations. This requirement aligns the API with the principle of least privilege mandated by the governing security policy.

**Requirement.** Retain the prior configuration so that a rollback can be performed without redeploying the node. The deployment shall maintain the configuration described in this control at all times, and the verifier shall treat any deviation as reportable. Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment.

**Implementation guidance.** Operators should prefer configuration that is idempotent so that re-deploying the API produces no further changes. Operators should prefer configuration that is idempotent so that re-deploying the API produces no further changes. Retain the prior configuration so that a rollback can be performed without redeploying the node. Prefer explicit values over relying on framework defaults, which may vary between runtime versions. Operators should prefer configuration that is idempotent so that re-deploying the API produces no further changes. Retain the prior configuration so that a rollback can be performed without redeploying the node. Changes should be staged in a non-production environment and validated against the verification procedure below. Operators should prefer configuration that is idempotent so that re-deploying the API produces no further changes.

**Verification.** Evidence is the API's response status, headers, and body together with the resulting audit ledger rows. Evidence is the API's response status, headers, and body together with the resulting audit ledger rows. Evidence is the API's response status, headers, and body together with the resulting audit ledger rows.

**References.** Baseline Configuration Guide BCG-3.7; Prior assessment finding AF-5

**Revision history.**
- 2022-03: editorial revision to SV-003; clarified scope and wording.
- 2025-11: editorial revision to SV-003; clarified scope and wording.
- 2023-11: editorial revision to SV-003; clarified scope and wording.
- 2024-06: editorial revision to SV-003; clarified scope and wording.


### SV-004 — Restricted credential rotation

**Domain:** Service Configuration  **Severity:** High  **Applies to:** all HarborDesk API deployments

**Rationale.** Operational experience shows that small deviations here cascade into larger exposure during incident response. The control exists to keep responses deterministic so that repeated assessments converge on a stable state. The control exists to keep responses deterministic so that repeated assessments converge on a stable state. Adversaries routinely probe for misconfigurations of this control when establishing a foothold against the API edge.

**Requirement.** Operators should prefer configuration that is idempotent so that re-deploying the API produces no further changes. The deployment shall maintain the configuration described in this control at all times, and the verifier shall treat any deviation as reportable. Adversaries routinely probe for misconfigurations of this control when establishing a foothold against the API edge.

**Implementation guidance.** Changes should be staged in a non-production environment and validated against the verification procedure below. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. Document any approved deviation in the exceptions register with a scheduled review date. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies.

**Verification.** Assessors may replay the request sequence after applying fixes to confirm the node has converged. Automated property checks generate varied request sequences to confirm the control behaves consistently. Verification is performed by replaying a sequence of requests and comparing each response to the normalized policy expectation. Automated property checks generate varied request sequences to confirm the control behaves consistently. Assessors may replay the request sequence after applying fixes to confirm the node has converged.

**References.** Baseline Configuration Guide BCG-1.1; Baseline Configuration Guide BCG-8.2; Baseline Configuration Guide BCG-9.1

**Revision history.**
- 2024-04: editorial revision to SV-004; clarified scope and wording.
- 2022-12: editorial revision to SV-004; clarified scope and wording.
- 2022-11: editorial revision to SV-004; clarified scope and wording.


### SV-005 — Approved package provenance

**Domain:** Service Configuration  **Severity:** Moderate  **Applies to:** credential-bearing API nodes

**Rationale.** This requirement aligns the API with the principle of least privilege mandated by the governing security policy. Operational experience shows that small deviations here cascade into larger exposure during incident response. The control exists to keep responses deterministic so that repeated assessments converge on a stable state. Inconsistent application of this requirement across nodes complicates evidence collection and weakens attestations.

**Requirement.** Retain the prior configuration so that a rollback can be performed without redeploying the node. The deployment shall maintain the configuration described in this control at all times, and the verifier shall treat any deviation as reportable. Adversaries routinely probe for misconfigurations of this control when establishing a foothold against the API edge.

**Implementation guidance.** Prefer explicit values over relying on framework defaults, which may vary between runtime versions. Retain the prior configuration so that a rollback can be performed without redeploying the node. Retain the prior configuration so that a rollback can be performed without redeploying the node. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. Document any approved deviation in the exceptions register with a scheduled review date.

**Verification.** The verifier records the request and response for inclusion in the assessment package. Evidence is the API's response status, headers, and body together with the resulting audit ledger rows. Evidence is the API's response status, headers, and body together with the resulting audit ledger rows. The verifier records the request and response for inclusion in the assessment package.

**References.** Governing Security Policy GSP-2024 §3.5; Vendor hardening note VHN-2-9; Vendor hardening note VHN-8-2

**Revision history.**
- 2025-11: editorial revision to SV-005; clarified scope and wording.
- 2024-04: editorial revision to SV-005; clarified scope and wording.
- 2023-10: editorial revision to SV-005; clarified scope and wording.


### SV-006 — Approved credential rotation

**Domain:** Service Configuration  **Severity:** High  **Applies to:** edge and gateway deployments

**Rationale.** The control supports reproducible deployments of the API baseline and simplifies forensic comparison. Operational experience shows that small deviations here cascade into larger exposure during incident response. Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment. Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment. This requirement aligns the API with the principle of least privilege mandated by the governing security policy.

**Requirement.** Coordinate with the platform team before altering anything that affects credential handling. The deployment shall maintain the configuration described in this control at all times, and the verifier shall treat any deviation as reportable. Inconsistent application of this requirement across nodes complicates evidence collection and weakens attestations.

**Implementation guidance.** Operators should prefer configuration that is idempotent so that re-deploying the API produces no further changes. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. Operators should prefer configuration that is idempotent so that re-deploying the API produces no further changes. Coordinate with the platform team before altering anything that affects credential handling. Coordinate with the platform team before altering anything that affects credential handling.

**Verification.** The verifier records the request and response for inclusion in the assessment package. Assessors may replay the request sequence after applying fixes to confirm the node has converged. Evidence is the API's response status, headers, and body together with the resulting audit ledger rows.

**References.** Vendor hardening note VHN-6-9; Baseline Configuration Guide BCG-2.7; Prior assessment finding AF-4; Governing Security Policy GSP-2024 §1.2

**Revision history.**
- 2024-09: editorial revision to SV-006; clarified scope and wording.
- 2022-02: editorial revision to SV-006; clarified scope and wording.
- 2023-10: editorial revision to SV-006; clarified scope and wording.
- 2022-02: editorial revision to SV-006; clarified scope and wording.


### SV-007 — Hardened content-type enforcement

**Domain:** Service Configuration  **Severity:** High  **Applies to:** internet-facing API nodes

**Rationale.** Operational experience shows that small deviations here cascade into larger exposure during incident response. Inconsistent application of this requirement across nodes complicates evidence collection and weakens attestations. Operational experience shows that small deviations here cascade into larger exposure during incident response. The control exists to keep responses deterministic so that repeated assessments converge on a stable state. Operational experience shows that small deviations here cascade into larger exposure during incident response.

**Requirement.** Document any approved deviation in the exceptions register with a scheduled review date. The deployment shall maintain the configuration described in this control at all times, and the verifier shall treat any deviation as reportable. Inconsistent application of this requirement across nodes complicates evidence collection and weakens attestations.

**Implementation guidance.** Operators should prefer configuration that is idempotent so that re-deploying the API produces no further changes. Changes should be staged in a non-production environment and validated against the verification procedure below. Coordinate with the platform team before altering anything that affects credential handling. Coordinate with the platform team before altering anything that affects credential handling. Retain the prior configuration so that a rollback can be performed without redeploying the node.

**Verification.** The verifier records the request and response for inclusion in the assessment package. Automated property checks generate varied request sequences to confirm the control behaves consistently. The verifier records the request and response for inclusion in the assessment package. Automated property checks generate varied request sequences to confirm the control behaves consistently. Automated property checks generate varied request sequences to confirm the control behaves consistently.

**References.** Edge Operations Runbook ROB-6; Governing Security Policy GSP-2024 §2.8; Governing Security Policy GSP-2024 §6.4; Governing Security Policy GSP-2024 §9.4

**Revision history.**
- 2025-07: editorial revision to SV-007; clarified scope and wording.
- 2023-07: editorial revision to SV-007; clarified scope and wording.
- 2025-04: editorial revision to SV-007; clarified scope and wording.
- 2024-11: editorial revision to SV-007; clarified scope and wording.


### SV-008 — Baseline package provenance

**Domain:** Service Configuration  **Severity:** Moderate  **Applies to:** all HarborDesk API deployments

**Rationale.** This requirement aligns the API with the principle of least privilege mandated by the governing security policy. Operational experience shows that small deviations here cascade into larger exposure during incident response. The control exists to keep responses deterministic so that repeated assessments converge on a stable state. The control exists to keep responses deterministic so that repeated assessments converge on a stable state.

**Requirement.** Coordinate with the platform team before altering anything that affects credential handling. The deployment shall maintain the configuration described in this control at all times, and the verifier shall treat any deviation as reportable. The control supports reproducible deployments of the API baseline and simplifies forensic comparison.

**Implementation guidance.** Document any approved deviation in the exceptions register with a scheduled review date. Coordinate with the platform team before altering anything that affects credential handling. Prefer explicit values over relying on framework defaults, which may vary between runtime versions. Prefer explicit values over relying on framework defaults, which may vary between runtime versions. Document any approved deviation in the exceptions register with a scheduled review date. Changes should be staged in a non-production environment and validated against the verification procedure below. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner.

**Verification.** The verifier records the request and response for inclusion in the assessment package. Evidence is the API's response status, headers, and body together with the resulting audit ledger rows. Verification is performed by replaying a sequence of requests and comparing each response to the normalized policy expectation.

**References.** Edge Operations Runbook ROB-9; Baseline Configuration Guide BCG-4.8; Vendor hardening note VHN-4-0; Governing Security Policy GSP-2024 §1.8

**Revision history.**
- 2022-03: editorial revision to SV-008; clarified scope and wording.
- 2024-09: editorial revision to SV-008; clarified scope and wording.
- 2024-12: editorial revision to SV-008; clarified scope and wording.


### SV-009 — Controlled rate limiting

**Domain:** Service Configuration  **Severity:** Critical  **Applies to:** internet-facing API nodes

**Rationale.** Consistent enforcement reduces the mean time to detect anomalous access across the fleet. Inconsistent application of this requirement across nodes complicates evidence collection and weakens attestations. This requirement aligns the API with the principle of least privilege mandated by the governing security policy. The control exists to keep responses deterministic so that repeated assessments converge on a stable state.

**Requirement.** When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. The deployment shall maintain the configuration described in this control at all times, and the verifier shall treat any deviation as reportable. The control exists to keep responses deterministic so that repeated assessments converge on a stable state.

**Implementation guidance.** Prefer explicit values over relying on framework defaults, which may vary between runtime versions. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. Operators should prefer configuration that is idempotent so that re-deploying the API produces no further changes. Operators should prefer configuration that is idempotent so that re-deploying the API produces no further changes. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. Prefer explicit values over relying on framework defaults, which may vary between runtime versions. Document any approved deviation in the exceptions register with a scheduled review date. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies.

**Verification.** Assessors may replay the request sequence after applying fixes to confirm the node has converged. The verifier records the request and response for inclusion in the assessment package. Assessors may replay the request sequence after applying fixes to confirm the node has converged.

**References.** Baseline Configuration Guide BCG-2.6; Baseline Configuration Guide BCG-1.5; Prior assessment finding AF-1

**Revision history.**
- 2023-06: editorial revision to SV-009; clarified scope and wording.
- 2024-07: editorial revision to SV-009; clarified scope and wording.
- 2024-10: editorial revision to SV-009; clarified scope and wording.
- 2025-09: editorial revision to SV-009; clarified scope and wording.


### SV-010 — Monitored interface configuration

**Domain:** Service Configuration  **Severity:** Moderate  **Applies to:** all HarborDesk API deployments

**Rationale.** The control supports reproducible deployments of the API baseline and simplifies forensic comparison. Adversaries routinely probe for misconfigurations of this control when establishing a foothold against the API edge. The control supports reproducible deployments of the API baseline and simplifies forensic comparison. This requirement aligns the API with the principle of least privilege mandated by the governing security policy.

**Requirement.** Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. The deployment shall maintain the configuration described in this control at all times, and the verifier shall treat any deviation as reportable. Operational experience shows that small deviations here cascade into larger exposure during incident response.

**Implementation guidance.** Operators should prefer configuration that is idempotent so that re-deploying the API produces no further changes. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. Retain the prior configuration so that a rollback can be performed without redeploying the node. Operators should prefer configuration that is idempotent so that re-deploying the API produces no further changes. Retain the prior configuration so that a rollback can be performed without redeploying the node. Changes should be staged in a non-production environment and validated against the verification procedure below. Coordinate with the platform team before altering anything that affects credential handling. Prefer explicit values over relying on framework defaults, which may vary between runtime versions.

**Verification.** Verification is performed by replaying a sequence of requests and comparing each response to the normalized policy expectation. Automated property checks generate varied request sequences to confirm the control behaves consistently. Evidence is the API's response status, headers, and body together with the resulting audit ledger rows.

**References.** Edge Operations Runbook ROB-9; Governing Security Policy GSP-2024 §3.6

**Revision history.**
- 2023-08: editorial revision to SV-010; clarified scope and wording.
- 2022-02: editorial revision to SV-010; clarified scope and wording.
- 2023-07: editorial revision to SV-010; clarified scope and wording.


### SV-011 — Hardened response compression

**Domain:** Service Configuration  **Severity:** Low  **Applies to:** internet-facing API nodes

**Rationale.** Consistent enforcement reduces the mean time to detect anomalous access across the fleet. Inconsistent application of this requirement across nodes complicates evidence collection and weakens attestations. Operational experience shows that small deviations here cascade into larger exposure during incident response.

**Requirement.** When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. The deployment shall maintain the configuration described in this control at all times, and the verifier shall treat any deviation as reportable. The control exists to keep responses deterministic so that repeated assessments converge on a stable state.

**Implementation guidance.** Changes should be staged in a non-production environment and validated against the verification procedure below. Changes should be staged in a non-production environment and validated against the verification procedure below. Changes should be staged in a non-production environment and validated against the verification procedure below. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. Document any approved deviation in the exceptions register with a scheduled review date.

**Verification.** Assessors may replay the request sequence after applying fixes to confirm the node has converged. Verification is performed by replaying a sequence of requests and comparing each response to the normalized policy expectation. Automated property checks generate varied request sequences to confirm the control behaves consistently.

**References.** Governing Security Policy GSP-2024 §8.7; Baseline Configuration Guide BCG-1.2; Governing Security Policy GSP-2024 §6.1

**Revision history.**
- 2023-09: editorial revision to SV-011; clarified scope and wording.
- 2025-09: editorial revision to SV-011; clarified scope and wording.


### SV-012 — Centralized cache directive

**Domain:** Service Configuration  **Severity:** High  **Applies to:** edge and gateway deployments

**Rationale.** This requirement aligns the API with the principle of least privilege mandated by the governing security policy. Adversaries routinely probe for misconfigurations of this control when establishing a foothold against the API edge. The control exists to keep responses deterministic so that repeated assessments converge on a stable state.

**Requirement.** Operators should prefer configuration that is idempotent so that re-deploying the API produces no further changes. The deployment shall maintain the configuration described in this control at all times, and the verifier shall treat any deviation as reportable. Inconsistent application of this requirement across nodes complicates evidence collection and weakens attestations.

**Implementation guidance.** Coordinate with the platform team before altering anything that affects credential handling. Coordinate with the platform team before altering anything that affects credential handling. Retain the prior configuration so that a rollback can be performed without redeploying the node. Changes should be staged in a non-production environment and validated against the verification procedure below. Prefer explicit values over relying on framework defaults, which may vary between runtime versions. Operators should prefer configuration that is idempotent so that re-deploying the API produces no further changes.

**Verification.** Assessors may replay the request sequence after applying fixes to confirm the node has converged. Assessors may replay the request sequence after applying fixes to confirm the node has converged. Automated property checks generate varied request sequences to confirm the control behaves consistently.

**References.** Baseline Configuration Guide BCG-3.0; Governing Security Policy GSP-2024 §9.0

**Revision history.**
- 2025-09: editorial revision to SV-012; clarified scope and wording.
- 2024-12: editorial revision to SV-012; clarified scope and wording.
- 2022-12: editorial revision to SV-012; clarified scope and wording.
- 2024-02: editorial revision to SV-012; clarified scope and wording.


### SV-013 — Controlled method allowlisting

**Domain:** Service Configuration  **Severity:** Critical  **Applies to:** all HarborDesk API deployments

**Rationale.** Adversaries routinely probe for misconfigurations of this control when establishing a foothold against the API edge. Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment. Inconsistent application of this requirement across nodes complicates evidence collection and weakens attestations.

**Requirement.** Coordinate with the platform team before altering anything that affects credential handling. The deployment shall maintain the configuration described in this control at all times, and the verifier shall treat any deviation as reportable. The control supports reproducible deployments of the API baseline and simplifies forensic comparison.

**Implementation guidance.** Coordinate with the platform team before altering anything that affects credential handling. Coordinate with the platform team before altering anything that affects credential handling. Document any approved deviation in the exceptions register with a scheduled review date. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. Changes should be staged in a non-production environment and validated against the verification procedure below. Document any approved deviation in the exceptions register with a scheduled review date. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner.

**Verification.** Automated property checks generate varied request sequences to confirm the control behaves consistently. Evidence is the API's response status, headers, and body together with the resulting audit ledger rows. Automated property checks generate varied request sequences to confirm the control behaves consistently.

**References.** Baseline Configuration Guide BCG-1.1; Prior assessment finding AF-5; Edge Operations Runbook ROB-2; Baseline Configuration Guide BCG-4.4

**Revision history.**
- 2024-12: editorial revision to SV-013; clarified scope and wording.
- 2024-05: editorial revision to SV-013; clarified scope and wording.
- 2022-04: editorial revision to SV-013; clarified scope and wording.


### SV-014 — Verified request logging

**Domain:** Service Configuration  **Severity:** Moderate  **Applies to:** credential-bearing API nodes

**Rationale.** This requirement aligns the API with the principle of least privilege mandated by the governing security policy. The control supports reproducible deployments of the API baseline and simplifies forensic comparison. The control exists to keep responses deterministic so that repeated assessments converge on a stable state. The control supports reproducible deployments of the API baseline and simplifies forensic comparison. The control supports reproducible deployments of the API baseline and simplifies forensic comparison.

**Requirement.** Prefer explicit values over relying on framework defaults, which may vary between runtime versions. The deployment shall maintain the configuration described in this control at all times, and the verifier shall treat any deviation as reportable. This requirement aligns the API with the principle of least privilege mandated by the governing security policy.

**Implementation guidance.** Prefer explicit values over relying on framework defaults, which may vary between runtime versions. Operators should prefer configuration that is idempotent so that re-deploying the API produces no further changes. Document any approved deviation in the exceptions register with a scheduled review date. Document any approved deviation in the exceptions register with a scheduled review date. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. Coordinate with the platform team before altering anything that affects credential handling.

**Verification.** Evidence is the API's response status, headers, and body together with the resulting audit ledger rows. Verification is performed by replaying a sequence of requests and comparing each response to the normalized policy expectation. The verifier records the request and response for inclusion in the assessment package. The verifier records the request and response for inclusion in the assessment package. Evidence is the API's response status, headers, and body together with the resulting audit ledger rows.

**References.** Vendor hardening note VHN-6-8; Baseline Configuration Guide BCG-2.5

**Revision history.**
- 2023-02: editorial revision to SV-014; clarified scope and wording.
- 2022-12: editorial revision to SV-014; clarified scope and wording.
- 2022-10: editorial revision to SV-014; clarified scope and wording.
- 2025-04: editorial revision to SV-014; clarified scope and wording.


### SV-015 — Verified interface configuration

**Domain:** Service Configuration  **Severity:** Critical  **Applies to:** all HarborDesk API deployments

**Rationale.** Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment. Operational experience shows that small deviations here cascade into larger exposure during incident response. Adversaries routinely probe for misconfigurations of this control when establishing a foothold against the API edge. Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment.

**Requirement.** Document any approved deviation in the exceptions register with a scheduled review date. The deployment shall maintain the configuration described in this control at all times, and the verifier shall treat any deviation as reportable. Consistent enforcement reduces the mean time to detect anomalous access across the fleet.

**Implementation guidance.** Document any approved deviation in the exceptions register with a scheduled review date. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. Operators should prefer configuration that is idempotent so that re-deploying the API produces no further changes. Retain the prior configuration so that a rollback can be performed without redeploying the node. Coordinate with the platform team before altering anything that affects credential handling.

**Verification.** The verifier records the request and response for inclusion in the assessment package. Assessors may replay the request sequence after applying fixes to confirm the node has converged. Verification is performed by replaying a sequence of requests and comparing each response to the normalized policy expectation. Assessors may replay the request sequence after applying fixes to confirm the node has converged. Evidence is the API's response status, headers, and body together with the resulting audit ledger rows.

**References.** Edge Operations Runbook ROB-8; Prior assessment finding AF-5; Governing Security Policy GSP-2024 §6.3; Vendor hardening note VHN-5-7

**Revision history.**
- 2023-07: editorial revision to SV-015; clarified scope and wording.
- 2023-11: editorial revision to SV-015; clarified scope and wording.


## 8. Maintenance

Consistent enforcement reduces the mean time to detect anomalous access across the fleet. Consistent enforcement reduces the mean time to detect anomalous access across the fleet. This requirement aligns the API with the principle of least privilege mandated by the governing security policy. Adversaries routinely probe for misconfigurations of this control when establishing a foothold against the API edge. The control exists to keep responses deterministic so that repeated assessments converge on a stable state. The control exists to keep responses deterministic so that repeated assessments converge on a stable state.


Prefer explicit values over relying on framework defaults, which may vary between runtime versions. Operators should prefer configuration that is idempotent so that re-deploying the API produces no further changes. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. Operators should prefer configuration that is idempotent so that re-deploying the API produces no further changes. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies.


### MA-001 — Centralized rate limiting

**Domain:** Maintenance  **Severity:** Low  **Applies to:** edge and gateway deployments

**Rationale.** The control exists to keep responses deterministic so that repeated assessments converge on a stable state. Operational experience shows that small deviations here cascade into larger exposure during incident response. Inconsistent application of this requirement across nodes complicates evidence collection and weakens attestations. Operational experience shows that small deviations here cascade into larger exposure during incident response.

**Requirement.** Operators should prefer configuration that is idempotent so that re-deploying the API produces no further changes. The deployment shall maintain the configuration described in this control at all times, and the verifier shall treat any deviation as reportable. Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment.

**Implementation guidance.** Changes should be staged in a non-production environment and validated against the verification procedure below. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. Coordinate with the platform team before altering anything that affects credential handling. Document any approved deviation in the exceptions register with a scheduled review date. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies.

**Verification.** Assessors may replay the request sequence after applying fixes to confirm the node has converged. Automated property checks generate varied request sequences to confirm the control behaves consistently. Evidence is the API's response status, headers, and body together with the resulting audit ledger rows. Automated property checks generate varied request sequences to confirm the control behaves consistently.

**References.** Vendor hardening note VHN-4-0; Baseline Configuration Guide BCG-4.8

**Revision history.**
- 2022-03: editorial revision to MA-001; clarified scope and wording.
- 2024-06: editorial revision to MA-001; clarified scope and wording.
- 2024-04: editorial revision to MA-001; clarified scope and wording.


### MA-002 — Controlled rate limiting

**Domain:** Maintenance  **Severity:** High  **Applies to:** internal staging deployments

**Rationale.** The control supports reproducible deployments of the API baseline and simplifies forensic comparison. The control supports reproducible deployments of the API baseline and simplifies forensic comparison. Inconsistent application of this requirement across nodes complicates evidence collection and weakens attestations.

**Requirement.** Prefer explicit values over relying on framework defaults, which may vary between runtime versions. The deployment shall maintain the configuration described in this control at all times, and the verifier shall treat any deviation as reportable. Consistent enforcement reduces the mean time to detect anomalous access across the fleet.

**Implementation guidance.** Coordinate with the platform team before altering anything that affects credential handling. Operators should prefer configuration that is idempotent so that re-deploying the API produces no further changes. Prefer explicit values over relying on framework defaults, which may vary between runtime versions. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. Changes should be staged in a non-production environment and validated against the verification procedure below.

**Verification.** Assessors may replay the request sequence after applying fixes to confirm the node has converged. Evidence is the API's response status, headers, and body together with the resulting audit ledger rows. Assessors may replay the request sequence after applying fixes to confirm the node has converged. Verification is performed by replaying a sequence of requests and comparing each response to the normalized policy expectation.

**References.** Vendor hardening note VHN-2-6; Prior assessment finding AF-3; Prior assessment finding AF-8

**Revision history.**
- 2025-01: editorial revision to MA-002; clarified scope and wording.
- 2024-08: editorial revision to MA-002; clarified scope and wording.


### MA-003 — Baseline service enablement

**Domain:** Maintenance  **Severity:** Low  **Applies to:** internet-facing API nodes

**Rationale.** Inconsistent application of this requirement across nodes complicates evidence collection and weakens attestations. Consistent enforcement reduces the mean time to detect anomalous access across the fleet. This requirement aligns the API with the principle of least privilege mandated by the governing security policy. Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment.

**Requirement.** Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. The deployment shall maintain the configuration described in this control at all times, and the verifier shall treat any deviation as reportable. The control supports reproducible deployments of the API baseline and simplifies forensic comparison.

**Implementation guidance.** Operators should prefer configuration that is idempotent so that re-deploying the API produces no further changes. Prefer explicit values over relying on framework defaults, which may vary between runtime versions. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. Document any approved deviation in the exceptions register with a scheduled review date. Prefer explicit values over relying on framework defaults, which may vary between runtime versions.

**Verification.** Assessors may replay the request sequence after applying fixes to confirm the node has converged. Automated property checks generate varied request sequences to confirm the control behaves consistently. Automated property checks generate varied request sequences to confirm the control behaves consistently. The verifier records the request and response for inclusion in the assessment package.

**References.** Prior assessment finding AF-7; Baseline Configuration Guide BCG-8.8; Prior assessment finding AF-5

**Revision history.**
- 2024-11: editorial revision to MA-003; clarified scope and wording.
- 2023-09: editorial revision to MA-003; clarified scope and wording.
- 2022-11: editorial revision to MA-003; clarified scope and wording.
- 2025-06: editorial revision to MA-003; clarified scope and wording.


### MA-004 — Mandatory service enablement

**Domain:** Maintenance  **Severity:** Low  **Applies to:** internal staging deployments

**Rationale.** Consistent enforcement reduces the mean time to detect anomalous access across the fleet. Inconsistent application of this requirement across nodes complicates evidence collection and weakens attestations. This requirement aligns the API with the principle of least privilege mandated by the governing security policy.

**Requirement.** Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. The deployment shall maintain the configuration described in this control at all times, and the verifier shall treat any deviation as reportable. This requirement aligns the API with the principle of least privilege mandated by the governing security policy.

**Implementation guidance.** Coordinate with the platform team before altering anything that affects credential handling. Retain the prior configuration so that a rollback can be performed without redeploying the node. Prefer explicit values over relying on framework defaults, which may vary between runtime versions. Document any approved deviation in the exceptions register with a scheduled review date. Prefer explicit values over relying on framework defaults, which may vary between runtime versions. Operators should prefer configuration that is idempotent so that re-deploying the API produces no further changes. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies.

**Verification.** Assessors may replay the request sequence after applying fixes to confirm the node has converged. The verifier records the request and response for inclusion in the assessment package. Verification is performed by replaying a sequence of requests and comparing each response to the normalized policy expectation.

**References.** Edge Operations Runbook ROB-6; Baseline Configuration Guide BCG-2.3; Governing Security Policy GSP-2024 §9.1; Governing Security Policy GSP-2024 §9.3

**Revision history.**
- 2024-08: editorial revision to MA-004; clarified scope and wording.
- 2023-04: editorial revision to MA-004; clarified scope and wording.


### MA-005 — Approved response compression

**Domain:** Maintenance  **Severity:** Low  **Applies to:** credential-bearing API nodes

**Rationale.** Adversaries routinely probe for misconfigurations of this control when establishing a foothold against the API edge. The control supports reproducible deployments of the API baseline and simplifies forensic comparison. Inconsistent application of this requirement across nodes complicates evidence collection and weakens attestations. Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment. This requirement aligns the API with the principle of least privilege mandated by the governing security policy.

**Requirement.** Changes should be staged in a non-production environment and validated against the verification procedure below. The deployment shall maintain the configuration described in this control at all times, and the verifier shall treat any deviation as reportable. Consistent enforcement reduces the mean time to detect anomalous access across the fleet.

**Implementation guidance.** Prefer explicit values over relying on framework defaults, which may vary between runtime versions. Changes should be staged in a non-production environment and validated against the verification procedure below. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. Prefer explicit values over relying on framework defaults, which may vary between runtime versions. Coordinate with the platform team before altering anything that affects credential handling. Document any approved deviation in the exceptions register with a scheduled review date. Retain the prior configuration so that a rollback can be performed without redeploying the node.

**Verification.** The verifier records the request and response for inclusion in the assessment package. The verifier records the request and response for inclusion in the assessment package. Evidence is the API's response status, headers, and body together with the resulting audit ledger rows. The verifier records the request and response for inclusion in the assessment package.

**References.** Governing Security Policy GSP-2024 §3.7; Vendor hardening note VHN-1-5

**Revision history.**
- 2025-03: editorial revision to MA-005; clarified scope and wording.
- 2023-08: editorial revision to MA-005; clarified scope and wording.


### MA-006 — Verified console access

**Domain:** Maintenance  **Severity:** High  **Applies to:** edge and gateway deployments

**Rationale.** Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment. Consistent enforcement reduces the mean time to detect anomalous access across the fleet. Consistent enforcement reduces the mean time to detect anomalous access across the fleet.

**Requirement.** Coordinate with the platform team before altering anything that affects credential handling. The deployment shall maintain the configuration described in this control at all times, and the verifier shall treat any deviation as reportable. Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment.

**Implementation guidance.** Changes should be staged in a non-production environment and validated against the verification procedure below. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. Operators should prefer configuration that is idempotent so that re-deploying the API produces no further changes. Coordinate with the platform team before altering anything that affects credential handling. Retain the prior configuration so that a rollback can be performed without redeploying the node. Retain the prior configuration so that a rollback can be performed without redeploying the node.

**Verification.** The verifier records the request and response for inclusion in the assessment package. Assessors may replay the request sequence after applying fixes to confirm the node has converged. Verification is performed by replaying a sequence of requests and comparing each response to the normalized policy expectation. Evidence is the API's response status, headers, and body together with the resulting audit ledger rows. Verification is performed by replaying a sequence of requests and comparing each response to the normalized policy expectation.

**References.** Baseline Configuration Guide BCG-2.9; Baseline Configuration Guide BCG-3.7; Edge Operations Runbook ROB-1; Prior assessment finding AF-8

**Revision history.**
- 2024-01: editorial revision to MA-006; clarified scope and wording.
- 2022-03: editorial revision to MA-006; clarified scope and wording.
- 2023-09: editorial revision to MA-006; clarified scope and wording.
- 2024-07: editorial revision to MA-006; clarified scope and wording.


### MA-007 — Monitored request logging

**Domain:** Maintenance  **Severity:** High  **Applies to:** all HarborDesk API deployments

**Rationale.** The control exists to keep responses deterministic so that repeated assessments converge on a stable state. This requirement aligns the API with the principle of least privilege mandated by the governing security policy. Consistent enforcement reduces the mean time to detect anomalous access across the fleet.

**Requirement.** Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. The deployment shall maintain the configuration described in this control at all times, and the verifier shall treat any deviation as reportable. Operational experience shows that small deviations here cascade into larger exposure during incident response.

**Implementation guidance.** Changes should be staged in a non-production environment and validated against the verification procedure below. Coordinate with the platform team before altering anything that affects credential handling. Document any approved deviation in the exceptions register with a scheduled review date. Retain the prior configuration so that a rollback can be performed without redeploying the node. Coordinate with the platform team before altering anything that affects credential handling. Operators should prefer configuration that is idempotent so that re-deploying the API produces no further changes. Operators should prefer configuration that is idempotent so that re-deploying the API produces no further changes.

**Verification.** Assessors may replay the request sequence after applying fixes to confirm the node has converged. Evidence is the API's response status, headers, and body together with the resulting audit ledger rows. Automated property checks generate varied request sequences to confirm the control behaves consistently. Evidence is the API's response status, headers, and body together with the resulting audit ledger rows. Automated property checks generate varied request sequences to confirm the control behaves consistently.

**References.** Governing Security Policy GSP-2024 §4.3; Vendor hardening note VHN-4-0; Baseline Configuration Guide BCG-3.7; Governing Security Policy GSP-2024 §4.8

**Revision history.**
- 2023-01: editorial revision to MA-007; clarified scope and wording.
- 2022-01: editorial revision to MA-007; clarified scope and wording.
- 2023-08: editorial revision to MA-007; clarified scope and wording.


### MA-008 — Hardened credential rotation

**Domain:** Maintenance  **Severity:** Low  **Applies to:** internet-facing API nodes

**Rationale.** Adversaries routinely probe for misconfigurations of this control when establishing a foothold against the API edge. Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment. Adversaries routinely probe for misconfigurations of this control when establishing a foothold against the API edge.

**Requirement.** Coordinate with the platform team before altering anything that affects credential handling. The deployment shall maintain the configuration described in this control at all times, and the verifier shall treat any deviation as reportable. Adversaries routinely probe for misconfigurations of this control when establishing a foothold against the API edge.

**Implementation guidance.** Coordinate with the platform team before altering anything that affects credential handling. Retain the prior configuration so that a rollback can be performed without redeploying the node. Changes should be staged in a non-production environment and validated against the verification procedure below. Coordinate with the platform team before altering anything that affects credential handling. Changes should be staged in a non-production environment and validated against the verification procedure below. Changes should be staged in a non-production environment and validated against the verification procedure below.

**Verification.** Verification is performed by replaying a sequence of requests and comparing each response to the normalized policy expectation. The verifier records the request and response for inclusion in the assessment package. Verification is performed by replaying a sequence of requests and comparing each response to the normalized policy expectation. Evidence is the API's response status, headers, and body together with the resulting audit ledger rows. Automated property checks generate varied request sequences to confirm the control behaves consistently.

**References.** Edge Operations Runbook ROB-1; Vendor hardening note VHN-4-4; Governing Security Policy GSP-2024 §6.1

**Revision history.**
- 2024-11: editorial revision to MA-008; clarified scope and wording.
- 2025-12: editorial revision to MA-008; clarified scope and wording.
- 2024-10: editorial revision to MA-008; clarified scope and wording.
- 2023-04: editorial revision to MA-008; clarified scope and wording.


### MA-009 — Controlled package provenance

**Domain:** Maintenance  **Severity:** Critical  **Applies to:** edge and gateway deployments

**Rationale.** Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment. Inconsistent application of this requirement across nodes complicates evidence collection and weakens attestations. Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment. Adversaries routinely probe for misconfigurations of this control when establishing a foothold against the API edge.

**Requirement.** Changes should be staged in a non-production environment and validated against the verification procedure below. The deployment shall maintain the configuration described in this control at all times, and the verifier shall treat any deviation as reportable. The control supports reproducible deployments of the API baseline and simplifies forensic comparison.

**Implementation guidance.** Retain the prior configuration so that a rollback can be performed without redeploying the node. Retain the prior configuration so that a rollback can be performed without redeploying the node. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner.

**Verification.** The verifier records the request and response for inclusion in the assessment package. Verification is performed by replaying a sequence of requests and comparing each response to the normalized policy expectation. Automated property checks generate varied request sequences to confirm the control behaves consistently. The verifier records the request and response for inclusion in the assessment package. The verifier records the request and response for inclusion in the assessment package.

**References.** Edge Operations Runbook ROB-3; Baseline Configuration Guide BCG-9.6; Governing Security Policy GSP-2024 §1.1; Governing Security Policy GSP-2024 §3.7

**Revision history.**
- 2024-11: editorial revision to MA-009; clarified scope and wording.
- 2024-04: editorial revision to MA-009; clarified scope and wording.
- 2022-12: editorial revision to MA-009; clarified scope and wording.
- 2023-09: editorial revision to MA-009; clarified scope and wording.


### MA-010 — Centralized package provenance

**Domain:** Maintenance  **Severity:** Low  **Applies to:** edge and gateway deployments

**Rationale.** The control supports reproducible deployments of the API baseline and simplifies forensic comparison. Consistent enforcement reduces the mean time to detect anomalous access across the fleet. The control supports reproducible deployments of the API baseline and simplifies forensic comparison. The control supports reproducible deployments of the API baseline and simplifies forensic comparison. The control supports reproducible deployments of the API baseline and simplifies forensic comparison.

**Requirement.** Changes should be staged in a non-production environment and validated against the verification procedure below. The deployment shall maintain the configuration described in this control at all times, and the verifier shall treat any deviation as reportable. Consistent enforcement reduces the mean time to detect anomalous access across the fleet.

**Implementation guidance.** Coordinate with the platform team before altering anything that affects credential handling. Document any approved deviation in the exceptions register with a scheduled review date. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. Operators should prefer configuration that is idempotent so that re-deploying the API produces no further changes. Coordinate with the platform team before altering anything that affects credential handling. Changes should be staged in a non-production environment and validated against the verification procedure below. Document any approved deviation in the exceptions register with a scheduled review date. Prefer explicit values over relying on framework defaults, which may vary between runtime versions.

**Verification.** Verification is performed by replaying a sequence of requests and comparing each response to the normalized policy expectation. The verifier records the request and response for inclusion in the assessment package. The verifier records the request and response for inclusion in the assessment package. Automated property checks generate varied request sequences to confirm the control behaves consistently.

**References.** Baseline Configuration Guide BCG-6.2; Baseline Configuration Guide BCG-4.3; Vendor hardening note VHN-8-3

**Revision history.**
- 2023-04: editorial revision to MA-010; clarified scope and wording.
- 2022-10: editorial revision to MA-010; clarified scope and wording.
- 2025-09: editorial revision to MA-010; clarified scope and wording.
- 2024-09: editorial revision to MA-010; clarified scope and wording.


### MA-011 — Restricted log forwarding

**Domain:** Maintenance  **Severity:** Moderate  **Applies to:** all HarborDesk API deployments

**Rationale.** Consistent enforcement reduces the mean time to detect anomalous access across the fleet. The control supports reproducible deployments of the API baseline and simplifies forensic comparison. The control supports reproducible deployments of the API baseline and simplifies forensic comparison. Operational experience shows that small deviations here cascade into larger exposure during incident response. Inconsistent application of this requirement across nodes complicates evidence collection and weakens attestations.

**Requirement.** Operators should prefer configuration that is idempotent so that re-deploying the API produces no further changes. The deployment shall maintain the configuration described in this control at all times, and the verifier shall treat any deviation as reportable. This requirement aligns the API with the principle of least privilege mandated by the governing security policy.

**Implementation guidance.** Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. Changes should be staged in a non-production environment and validated against the verification procedure below. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner.

**Verification.** Evidence is the API's response status, headers, and body together with the resulting audit ledger rows. The verifier records the request and response for inclusion in the assessment package. Automated property checks generate varied request sequences to confirm the control behaves consistently.

**References.** Baseline Configuration Guide BCG-1.1; Governing Security Policy GSP-2024 §7.1; Prior assessment finding AF-3

**Revision history.**
- 2024-05: editorial revision to MA-011; clarified scope and wording.
- 2025-06: editorial revision to MA-011; clarified scope and wording.
- 2022-12: editorial revision to MA-011; clarified scope and wording.
- 2022-01: editorial revision to MA-011; clarified scope and wording.


### MA-012 — Standard package provenance

**Domain:** Maintenance  **Severity:** High  **Applies to:** all HarborDesk API deployments

**Rationale.** Adversaries routinely probe for misconfigurations of this control when establishing a foothold against the API edge. Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment. Adversaries routinely probe for misconfigurations of this control when establishing a foothold against the API edge. Consistent enforcement reduces the mean time to detect anomalous access across the fleet. Operational experience shows that small deviations here cascade into larger exposure during incident response.

**Requirement.** Operators should prefer configuration that is idempotent so that re-deploying the API produces no further changes. The deployment shall maintain the configuration described in this control at all times, and the verifier shall treat any deviation as reportable. Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment.

**Implementation guidance.** Operators should prefer configuration that is idempotent so that re-deploying the API produces no further changes. Changes should be staged in a non-production environment and validated against the verification procedure below. Document any approved deviation in the exceptions register with a scheduled review date. Operators should prefer configuration that is idempotent so that re-deploying the API produces no further changes. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. Coordinate with the platform team before altering anything that affects credential handling.

**Verification.** Evidence is the API's response status, headers, and body together with the resulting audit ledger rows. Evidence is the API's response status, headers, and body together with the resulting audit ledger rows. The verifier records the request and response for inclusion in the assessment package.

**References.** Prior assessment finding AF-6; Baseline Configuration Guide BCG-3.1; Baseline Configuration Guide BCG-1.3; Governing Security Policy GSP-2024 §9.7

**Revision history.**
- 2025-08: editorial revision to MA-012; clarified scope and wording.
- 2022-10: editorial revision to MA-012; clarified scope and wording.
- 2025-10: editorial revision to MA-012; clarified scope and wording.
- 2024-01: editorial revision to MA-012; clarified scope and wording.


### MA-013 — Verified content-type enforcement

**Domain:** Maintenance  **Severity:** High  **Applies to:** all HarborDesk API deployments

**Rationale.** Consistent enforcement reduces the mean time to detect anomalous access across the fleet. This requirement aligns the API with the principle of least privilege mandated by the governing security policy. This requirement aligns the API with the principle of least privilege mandated by the governing security policy.

**Requirement.** Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. The deployment shall maintain the configuration described in this control at all times, and the verifier shall treat any deviation as reportable. Consistent enforcement reduces the mean time to detect anomalous access across the fleet.

**Implementation guidance.** Coordinate with the platform team before altering anything that affects credential handling. Changes should be staged in a non-production environment and validated against the verification procedure below. Coordinate with the platform team before altering anything that affects credential handling. Operators should prefer configuration that is idempotent so that re-deploying the API produces no further changes. Document any approved deviation in the exceptions register with a scheduled review date. Retain the prior configuration so that a rollback can be performed without redeploying the node.

**Verification.** Verification is performed by replaying a sequence of requests and comparing each response to the normalized policy expectation. Assessors may replay the request sequence after applying fixes to confirm the node has converged. Automated property checks generate varied request sequences to confirm the control behaves consistently. Automated property checks generate varied request sequences to confirm the control behaves consistently. Verification is performed by replaying a sequence of requests and comparing each response to the normalized policy expectation.

**References.** Governing Security Policy GSP-2024 §6.2; Governing Security Policy GSP-2024 §5.6; Governing Security Policy GSP-2024 §2.3; Edge Operations Runbook ROB-9

**Revision history.**
- 2022-06: editorial revision to MA-013; clarified scope and wording.
- 2024-05: editorial revision to MA-013; clarified scope and wording.
- 2022-06: editorial revision to MA-013; clarified scope and wording.


### MA-014 — Baseline interface configuration

**Domain:** Maintenance  **Severity:** High  **Applies to:** credential-bearing API nodes

**Rationale.** Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment. Operational experience shows that small deviations here cascade into larger exposure during incident response. Adversaries routinely probe for misconfigurations of this control when establishing a foothold against the API edge. This requirement aligns the API with the principle of least privilege mandated by the governing security policy. Adversaries routinely probe for misconfigurations of this control when establishing a foothold against the API edge.

**Requirement.** Changes should be staged in a non-production environment and validated against the verification procedure below. The deployment shall maintain the configuration described in this control at all times, and the verifier shall treat any deviation as reportable. Inconsistent application of this requirement across nodes complicates evidence collection and weakens attestations.

**Implementation guidance.** When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. Operators should prefer configuration that is idempotent so that re-deploying the API produces no further changes. Document any approved deviation in the exceptions register with a scheduled review date. Prefer explicit values over relying on framework defaults, which may vary between runtime versions. Document any approved deviation in the exceptions register with a scheduled review date.

**Verification.** Evidence is the API's response status, headers, and body together with the resulting audit ledger rows. Verification is performed by replaying a sequence of requests and comparing each response to the normalized policy expectation. Assessors may replay the request sequence after applying fixes to confirm the node has converged. Evidence is the API's response status, headers, and body together with the resulting audit ledger rows. Verification is performed by replaying a sequence of requests and comparing each response to the normalized policy expectation.

**References.** Governing Security Policy GSP-2024 §7.9; Baseline Configuration Guide BCG-9.4

**Revision history.**
- 2022-06: editorial revision to MA-014; clarified scope and wording.
- 2023-12: editorial revision to MA-014; clarified scope and wording.
- 2025-01: editorial revision to MA-014; clarified scope and wording.


## 9. Network Controls

Operational experience shows that small deviations here cascade into larger exposure during incident response. Consistent enforcement reduces the mean time to detect anomalous access across the fleet. Adversaries routinely probe for misconfigurations of this control when establishing a foothold against the API edge. The control supports reproducible deployments of the API baseline and simplifies forensic comparison. This requirement aligns the API with the principle of least privilege mandated by the governing security policy.


Changes should be staged in a non-production environment and validated against the verification procedure below. Document any approved deviation in the exceptions register with a scheduled review date. Document any approved deviation in the exceptions register with a scheduled review date. Retain the prior configuration so that a rollback can be performed without redeploying the node.


### NW-001 — Approved rate limiting

**Domain:** Network Controls  **Severity:** Moderate  **Applies to:** credential-bearing API nodes

**Rationale.** Adversaries routinely probe for misconfigurations of this control when establishing a foothold against the API edge. This requirement aligns the API with the principle of least privilege mandated by the governing security policy. Adversaries routinely probe for misconfigurations of this control when establishing a foothold against the API edge. Adversaries routinely probe for misconfigurations of this control when establishing a foothold against the API edge.

**Requirement.** Document any approved deviation in the exceptions register with a scheduled review date. The deployment shall maintain the configuration described in this control at all times, and the verifier shall treat any deviation as reportable. Adversaries routinely probe for misconfigurations of this control when establishing a foothold against the API edge.

**Implementation guidance.** Changes should be staged in a non-production environment and validated against the verification procedure below. Changes should be staged in a non-production environment and validated against the verification procedure below. Document any approved deviation in the exceptions register with a scheduled review date. Prefer explicit values over relying on framework defaults, which may vary between runtime versions. Coordinate with the platform team before altering anything that affects credential handling.

**Verification.** The verifier records the request and response for inclusion in the assessment package. Verification is performed by replaying a sequence of requests and comparing each response to the normalized policy expectation. The verifier records the request and response for inclusion in the assessment package.

**References.** Vendor hardening note VHN-9-4; Vendor hardening note VHN-7-2; Prior assessment finding AF-8

**Revision history.**
- 2024-02: editorial revision to NW-001; clarified scope and wording.
- 2025-11: editorial revision to NW-001; clarified scope and wording.


### NW-002 — Baseline credential rotation

**Domain:** Network Controls  **Severity:** Low  **Applies to:** credential-bearing API nodes

**Rationale.** Operational experience shows that small deviations here cascade into larger exposure during incident response. The control exists to keep responses deterministic so that repeated assessments converge on a stable state. Consistent enforcement reduces the mean time to detect anomalous access across the fleet. This requirement aligns the API with the principle of least privilege mandated by the governing security policy. This requirement aligns the API with the principle of least privilege mandated by the governing security policy.

**Requirement.** Prefer explicit values over relying on framework defaults, which may vary between runtime versions. The deployment shall maintain the configuration described in this control at all times, and the verifier shall treat any deviation as reportable. Inconsistent application of this requirement across nodes complicates evidence collection and weakens attestations.

**Implementation guidance.** Coordinate with the platform team before altering anything that affects credential handling. Changes should be staged in a non-production environment and validated against the verification procedure below. Operators should prefer configuration that is idempotent so that re-deploying the API produces no further changes. Coordinate with the platform team before altering anything that affects credential handling. Operators should prefer configuration that is idempotent so that re-deploying the API produces no further changes. Prefer explicit values over relying on framework defaults, which may vary between runtime versions. Coordinate with the platform team before altering anything that affects credential handling.

**Verification.** Evidence is the API's response status, headers, and body together with the resulting audit ledger rows. Verification is performed by replaying a sequence of requests and comparing each response to the normalized policy expectation. Assessors may replay the request sequence after applying fixes to confirm the node has converged.

**References.** Vendor hardening note VHN-9-3; Edge Operations Runbook ROB-3

**Revision history.**
- 2024-07: editorial revision to NW-002; clarified scope and wording.
- 2024-09: editorial revision to NW-002; clarified scope and wording.


### NW-003 — Standard console access

**Domain:** Network Controls  **Severity:** Critical  **Applies to:** edge and gateway deployments

**Rationale.** The control exists to keep responses deterministic so that repeated assessments converge on a stable state. This requirement aligns the API with the principle of least privilege mandated by the governing security policy. The control exists to keep responses deterministic so that repeated assessments converge on a stable state.

**Requirement.** Prefer explicit values over relying on framework defaults, which may vary between runtime versions. The deployment shall maintain the configuration described in this control at all times, and the verifier shall treat any deviation as reportable. The control exists to keep responses deterministic so that repeated assessments converge on a stable state.

**Implementation guidance.** Coordinate with the platform team before altering anything that affects credential handling. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. Retain the prior configuration so that a rollback can be performed without redeploying the node. Prefer explicit values over relying on framework defaults, which may vary between runtime versions. Operators should prefer configuration that is idempotent so that re-deploying the API produces no further changes.

**Verification.** Automated property checks generate varied request sequences to confirm the control behaves consistently. Assessors may replay the request sequence after applying fixes to confirm the node has converged. Verification is performed by replaying a sequence of requests and comparing each response to the normalized policy expectation. Automated property checks generate varied request sequences to confirm the control behaves consistently. Verification is performed by replaying a sequence of requests and comparing each response to the normalized policy expectation.

**References.** Edge Operations Runbook ROB-2; Edge Operations Runbook ROB-3; Prior assessment finding AF-1; Baseline Configuration Guide BCG-6.6

**Revision history.**
- 2025-05: editorial revision to NW-003; clarified scope and wording.
- 2023-01: editorial revision to NW-003; clarified scope and wording.
- 2024-12: editorial revision to NW-003; clarified scope and wording.


### NW-004 — Baseline response compression

**Domain:** Network Controls  **Severity:** Low  **Applies to:** internet-facing API nodes

**Rationale.** This requirement aligns the API with the principle of least privilege mandated by the governing security policy. This requirement aligns the API with the principle of least privilege mandated by the governing security policy. Adversaries routinely probe for misconfigurations of this control when establishing a foothold against the API edge. This requirement aligns the API with the principle of least privilege mandated by the governing security policy. The control exists to keep responses deterministic so that repeated assessments converge on a stable state.

**Requirement.** Changes should be staged in a non-production environment and validated against the verification procedure below. The deployment shall maintain the configuration described in this control at all times, and the verifier shall treat any deviation as reportable. Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment.

**Implementation guidance.** Operators should prefer configuration that is idempotent so that re-deploying the API produces no further changes. Retain the prior configuration so that a rollback can be performed without redeploying the node. Changes should be staged in a non-production environment and validated against the verification procedure below. Prefer explicit values over relying on framework defaults, which may vary between runtime versions. Coordinate with the platform team before altering anything that affects credential handling. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner.

**Verification.** Verification is performed by replaying a sequence of requests and comparing each response to the normalized policy expectation. Automated property checks generate varied request sequences to confirm the control behaves consistently. Verification is performed by replaying a sequence of requests and comparing each response to the normalized policy expectation. Verification is performed by replaying a sequence of requests and comparing each response to the normalized policy expectation.

**References.** Edge Operations Runbook ROB-1; Governing Security Policy GSP-2024 §9.3

**Revision history.**
- 2024-04: editorial revision to NW-004; clarified scope and wording.
- 2024-10: editorial revision to NW-004; clarified scope and wording.
- 2025-04: editorial revision to NW-004; clarified scope and wording.


### NW-005 — Monitored method allowlisting

**Domain:** Network Controls  **Severity:** Moderate  **Applies to:** all HarborDesk API deployments

**Rationale.** Operational experience shows that small deviations here cascade into larger exposure during incident response. Operational experience shows that small deviations here cascade into larger exposure during incident response. Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment.

**Requirement.** Document any approved deviation in the exceptions register with a scheduled review date. The deployment shall maintain the configuration described in this control at all times, and the verifier shall treat any deviation as reportable. Operational experience shows that small deviations here cascade into larger exposure during incident response.

**Implementation guidance.** Document any approved deviation in the exceptions register with a scheduled review date. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. Changes should be staged in a non-production environment and validated against the verification procedure below. Operators should prefer configuration that is idempotent so that re-deploying the API produces no further changes.

**Verification.** Assessors may replay the request sequence after applying fixes to confirm the node has converged. Assessors may replay the request sequence after applying fixes to confirm the node has converged. Verification is performed by replaying a sequence of requests and comparing each response to the normalized policy expectation. Automated property checks generate varied request sequences to confirm the control behaves consistently.

**References.** Baseline Configuration Guide BCG-2.7; Vendor hardening note VHN-2-7

**Revision history.**
- 2025-03: editorial revision to NW-005; clarified scope and wording.
- 2023-03: editorial revision to NW-005; clarified scope and wording.
- 2024-12: editorial revision to NW-005; clarified scope and wording.


### NW-006 — Hardened log forwarding

**Domain:** Network Controls  **Severity:** High  **Applies to:** credential-bearing API nodes

**Rationale.** The control supports reproducible deployments of the API baseline and simplifies forensic comparison. Inconsistent application of this requirement across nodes complicates evidence collection and weakens attestations. This requirement aligns the API with the principle of least privilege mandated by the governing security policy. Operational experience shows that small deviations here cascade into larger exposure during incident response.

**Requirement.** Prefer explicit values over relying on framework defaults, which may vary between runtime versions. The deployment shall maintain the configuration described in this control at all times, and the verifier shall treat any deviation as reportable. The control supports reproducible deployments of the API baseline and simplifies forensic comparison.

**Implementation guidance.** Changes should be staged in a non-production environment and validated against the verification procedure below. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. Changes should be staged in a non-production environment and validated against the verification procedure below. Coordinate with the platform team before altering anything that affects credential handling. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies.

**Verification.** Verification is performed by replaying a sequence of requests and comparing each response to the normalized policy expectation. Assessors may replay the request sequence after applying fixes to confirm the node has converged. The verifier records the request and response for inclusion in the assessment package. Verification is performed by replaying a sequence of requests and comparing each response to the normalized policy expectation.

**References.** Vendor hardening note VHN-8-8; Prior assessment finding AF-3

**Revision history.**
- 2024-03: editorial revision to NW-006; clarified scope and wording.
- 2022-05: editorial revision to NW-006; clarified scope and wording.
- 2023-02: editorial revision to NW-006; clarified scope and wording.
- 2025-09: editorial revision to NW-006; clarified scope and wording.


### NW-007 — Restricted package provenance

**Domain:** Network Controls  **Severity:** Low  **Applies to:** all HarborDesk API deployments

**Rationale.** This requirement aligns the API with the principle of least privilege mandated by the governing security policy. The control exists to keep responses deterministic so that repeated assessments converge on a stable state. Operational experience shows that small deviations here cascade into larger exposure during incident response. This requirement aligns the API with the principle of least privilege mandated by the governing security policy.

**Requirement.** Document any approved deviation in the exceptions register with a scheduled review date. The deployment shall maintain the configuration described in this control at all times, and the verifier shall treat any deviation as reportable. The control supports reproducible deployments of the API baseline and simplifies forensic comparison.

**Implementation guidance.** Changes should be staged in a non-production environment and validated against the verification procedure below. Changes should be staged in a non-production environment and validated against the verification procedure below. Operators should prefer configuration that is idempotent so that re-deploying the API produces no further changes. Document any approved deviation in the exceptions register with a scheduled review date. Retain the prior configuration so that a rollback can be performed without redeploying the node. Prefer explicit values over relying on framework defaults, which may vary between runtime versions.

**Verification.** The verifier records the request and response for inclusion in the assessment package. Evidence is the API's response status, headers, and body together with the resulting audit ledger rows. Evidence is the API's response status, headers, and body together with the resulting audit ledger rows. The verifier records the request and response for inclusion in the assessment package. Evidence is the API's response status, headers, and body together with the resulting audit ledger rows.

**References.** Governing Security Policy GSP-2024 §5.5; Baseline Configuration Guide BCG-2.4; Edge Operations Runbook ROB-2

**Revision history.**
- 2025-10: editorial revision to NW-007; clarified scope and wording.
- 2022-03: editorial revision to NW-007; clarified scope and wording.


### NW-008 — Verified method allowlisting

**Domain:** Network Controls  **Severity:** High  **Applies to:** internal staging deployments

**Rationale.** Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment. The control supports reproducible deployments of the API baseline and simplifies forensic comparison. Adversaries routinely probe for misconfigurations of this control when establishing a foothold against the API edge.

**Requirement.** Retain the prior configuration so that a rollback can be performed without redeploying the node. The deployment shall maintain the configuration described in this control at all times, and the verifier shall treat any deviation as reportable. This requirement aligns the API with the principle of least privilege mandated by the governing security policy.

**Implementation guidance.** Retain the prior configuration so that a rollback can be performed without redeploying the node. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. Retain the prior configuration so that a rollback can be performed without redeploying the node. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. Prefer explicit values over relying on framework defaults, which may vary between runtime versions. Retain the prior configuration so that a rollback can be performed without redeploying the node. Changes should be staged in a non-production environment and validated against the verification procedure below.

**Verification.** Automated property checks generate varied request sequences to confirm the control behaves consistently. The verifier records the request and response for inclusion in the assessment package. Verification is performed by replaying a sequence of requests and comparing each response to the normalized policy expectation. Verification is performed by replaying a sequence of requests and comparing each response to the normalized policy expectation. Assessors may replay the request sequence after applying fixes to confirm the node has converged.

**References.** Baseline Configuration Guide BCG-6.9; Prior assessment finding AF-3

**Revision history.**
- 2024-03: editorial revision to NW-008; clarified scope and wording.
- 2025-09: editorial revision to NW-008; clarified scope and wording.
- 2022-01: editorial revision to NW-008; clarified scope and wording.


### NW-009 — Centralized service enablement

**Domain:** Network Controls  **Severity:** High  **Applies to:** edge and gateway deployments

**Rationale.** Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment. The control supports reproducible deployments of the API baseline and simplifies forensic comparison. Adversaries routinely probe for misconfigurations of this control when establishing a foothold against the API edge. The control exists to keep responses deterministic so that repeated assessments converge on a stable state. This requirement aligns the API with the principle of least privilege mandated by the governing security policy.

**Requirement.** When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. The deployment shall maintain the configuration described in this control at all times, and the verifier shall treat any deviation as reportable. Operational experience shows that small deviations here cascade into larger exposure during incident response.

**Implementation guidance.** Changes should be staged in a non-production environment and validated against the verification procedure below. Prefer explicit values over relying on framework defaults, which may vary between runtime versions. Prefer explicit values over relying on framework defaults, which may vary between runtime versions. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. Operators should prefer configuration that is idempotent so that re-deploying the API produces no further changes.

**Verification.** Verification is performed by replaying a sequence of requests and comparing each response to the normalized policy expectation. Assessors may replay the request sequence after applying fixes to confirm the node has converged. Verification is performed by replaying a sequence of requests and comparing each response to the normalized policy expectation. Automated property checks generate varied request sequences to confirm the control behaves consistently. Assessors may replay the request sequence after applying fixes to confirm the node has converged.

**References.** Prior assessment finding AF-9; Prior assessment finding AF-7; Vendor hardening note VHN-1-6

**Revision history.**
- 2025-08: editorial revision to NW-009; clarified scope and wording.
- 2023-09: editorial revision to NW-009; clarified scope and wording.


### NW-010 — Hardened credential rotation

**Domain:** Network Controls  **Severity:** Moderate  **Applies to:** all HarborDesk API deployments

**Rationale.** Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment. Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment. Inconsistent application of this requirement across nodes complicates evidence collection and weakens attestations. This requirement aligns the API with the principle of least privilege mandated by the governing security policy. Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment.

**Requirement.** Coordinate with the platform team before altering anything that affects credential handling. The deployment shall maintain the configuration described in this control at all times, and the verifier shall treat any deviation as reportable. The control supports reproducible deployments of the API baseline and simplifies forensic comparison.

**Implementation guidance.** Operators should prefer configuration that is idempotent so that re-deploying the API produces no further changes. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. Coordinate with the platform team before altering anything that affects credential handling. Coordinate with the platform team before altering anything that affects credential handling. Prefer explicit values over relying on framework defaults, which may vary between runtime versions. Document any approved deviation in the exceptions register with a scheduled review date. Document any approved deviation in the exceptions register with a scheduled review date.

**Verification.** Automated property checks generate varied request sequences to confirm the control behaves consistently. The verifier records the request and response for inclusion in the assessment package. Evidence is the API's response status, headers, and body together with the resulting audit ledger rows. The verifier records the request and response for inclusion in the assessment package.

**References.** Prior assessment finding AF-9; Baseline Configuration Guide BCG-1.1

**Revision history.**
- 2025-01: editorial revision to NW-010; clarified scope and wording.
- 2024-12: editorial revision to NW-010; clarified scope and wording.
- 2025-04: editorial revision to NW-010; clarified scope and wording.
- 2023-09: editorial revision to NW-010; clarified scope and wording.


### NW-011 — Hardened interface configuration

**Domain:** Network Controls  **Severity:** Low  **Applies to:** credential-bearing API nodes

**Rationale.** Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment. The control supports reproducible deployments of the API baseline and simplifies forensic comparison. This requirement aligns the API with the principle of least privilege mandated by the governing security policy.

**Requirement.** Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. The deployment shall maintain the configuration described in this control at all times, and the verifier shall treat any deviation as reportable. Consistent enforcement reduces the mean time to detect anomalous access across the fleet.

**Implementation guidance.** When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. Operators should prefer configuration that is idempotent so that re-deploying the API produces no further changes. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. Document any approved deviation in the exceptions register with a scheduled review date. Retain the prior configuration so that a rollback can be performed without redeploying the node. Changes should be staged in a non-production environment and validated against the verification procedure below. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies.

**Verification.** Assessors may replay the request sequence after applying fixes to confirm the node has converged. Automated property checks generate varied request sequences to confirm the control behaves consistently. Evidence is the API's response status, headers, and body together with the resulting audit ledger rows. Verification is performed by replaying a sequence of requests and comparing each response to the normalized policy expectation. Evidence is the API's response status, headers, and body together with the resulting audit ledger rows.

**References.** Governing Security Policy GSP-2024 §3.2; Edge Operations Runbook ROB-6

**Revision history.**
- 2023-11: editorial revision to NW-011; clarified scope and wording.
- 2023-03: editorial revision to NW-011; clarified scope and wording.
- 2023-12: editorial revision to NW-011; clarified scope and wording.
- 2023-03: editorial revision to NW-011; clarified scope and wording.


### NW-012 — Mandatory interface configuration

**Domain:** Network Controls  **Severity:** Moderate  **Applies to:** edge and gateway deployments

**Rationale.** Inconsistent application of this requirement across nodes complicates evidence collection and weakens attestations. The control supports reproducible deployments of the API baseline and simplifies forensic comparison. Adversaries routinely probe for misconfigurations of this control when establishing a foothold against the API edge.

**Requirement.** Document any approved deviation in the exceptions register with a scheduled review date. The deployment shall maintain the configuration described in this control at all times, and the verifier shall treat any deviation as reportable. Consistent enforcement reduces the mean time to detect anomalous access across the fleet.

**Implementation guidance.** Operators should prefer configuration that is idempotent so that re-deploying the API produces no further changes. Retain the prior configuration so that a rollback can be performed without redeploying the node. Prefer explicit values over relying on framework defaults, which may vary between runtime versions. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. Retain the prior configuration so that a rollback can be performed without redeploying the node. Coordinate with the platform team before altering anything that affects credential handling.

**Verification.** The verifier records the request and response for inclusion in the assessment package. Assessors may replay the request sequence after applying fixes to confirm the node has converged. Evidence is the API's response status, headers, and body together with the resulting audit ledger rows. Automated property checks generate varied request sequences to confirm the control behaves consistently.

**References.** Prior assessment finding AF-5; Governing Security Policy GSP-2024 §5.0; Prior assessment finding AF-1

**Revision history.**
- 2025-11: editorial revision to NW-012; clarified scope and wording.
- 2023-07: editorial revision to NW-012; clarified scope and wording.
- 2022-04: editorial revision to NW-012; clarified scope and wording.
- 2024-11: editorial revision to NW-012; clarified scope and wording.


### NW-013 — Restricted log forwarding

**Domain:** Network Controls  **Severity:** Low  **Applies to:** internal staging deployments

**Rationale.** The control supports reproducible deployments of the API baseline and simplifies forensic comparison. This requirement aligns the API with the principle of least privilege mandated by the governing security policy. Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment. The control supports reproducible deployments of the API baseline and simplifies forensic comparison. Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment.

**Requirement.** Operators should prefer configuration that is idempotent so that re-deploying the API produces no further changes. The deployment shall maintain the configuration described in this control at all times, and the verifier shall treat any deviation as reportable. The control supports reproducible deployments of the API baseline and simplifies forensic comparison.

**Implementation guidance.** When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. Coordinate with the platform team before altering anything that affects credential handling. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. Document any approved deviation in the exceptions register with a scheduled review date. Operators should prefer configuration that is idempotent so that re-deploying the API produces no further changes.

**Verification.** Evidence is the API's response status, headers, and body together with the resulting audit ledger rows. Assessors may replay the request sequence after applying fixes to confirm the node has converged. The verifier records the request and response for inclusion in the assessment package.

**References.** Edge Operations Runbook ROB-3; Vendor hardening note VHN-8-1; Baseline Configuration Guide BCG-4.1

**Revision history.**
- 2024-01: editorial revision to NW-013; clarified scope and wording.
- 2025-01: editorial revision to NW-013; clarified scope and wording.


### NW-014 — Centralized session timeout

**Domain:** Network Controls  **Severity:** Low  **Applies to:** internal staging deployments

**Rationale.** This requirement aligns the API with the principle of least privilege mandated by the governing security policy. The control supports reproducible deployments of the API baseline and simplifies forensic comparison. Consistent enforcement reduces the mean time to detect anomalous access across the fleet. Consistent enforcement reduces the mean time to detect anomalous access across the fleet. Consistent enforcement reduces the mean time to detect anomalous access across the fleet.

**Requirement.** When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. The deployment shall maintain the configuration described in this control at all times, and the verifier shall treat any deviation as reportable. Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment.

**Implementation guidance.** When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. Document any approved deviation in the exceptions register with a scheduled review date. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. Document any approved deviation in the exceptions register with a scheduled review date.

**Verification.** The verifier records the request and response for inclusion in the assessment package. Assessors may replay the request sequence after applying fixes to confirm the node has converged. Verification is performed by replaying a sequence of requests and comparing each response to the normalized policy expectation. Automated property checks generate varied request sequences to confirm the control behaves consistently.

**References.** Baseline Configuration Guide BCG-2.6; Prior assessment finding AF-1; Governing Security Policy GSP-2024 §9.8

**Revision history.**
- 2023-04: editorial revision to NW-014; clarified scope and wording.
- 2023-07: editorial revision to NW-014; clarified scope and wording.
- 2022-11: editorial revision to NW-014; clarified scope and wording.
- 2023-02: editorial revision to NW-014; clarified scope and wording.


## 10. Incident Response

Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment. Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment. Consistent enforcement reduces the mean time to detect anomalous access across the fleet. Inconsistent application of this requirement across nodes complicates evidence collection and weakens attestations. Consistent enforcement reduces the mean time to detect anomalous access across the fleet.


Prefer explicit values over relying on framework defaults, which may vary between runtime versions. Operators should prefer configuration that is idempotent so that re-deploying the API produces no further changes. Prefer explicit values over relying on framework defaults, which may vary between runtime versions. Retain the prior configuration so that a rollback can be performed without redeploying the node.


### IR-001 — Baseline cache directive

**Domain:** Incident Response  **Severity:** Low  **Applies to:** internet-facing API nodes

**Rationale.** The control exists to keep responses deterministic so that repeated assessments converge on a stable state. Operational experience shows that small deviations here cascade into larger exposure during incident response. Inconsistent application of this requirement across nodes complicates evidence collection and weakens attestations. Consistent enforcement reduces the mean time to detect anomalous access across the fleet. Adversaries routinely probe for misconfigurations of this control when establishing a foothold against the API edge.

**Requirement.** Coordinate with the platform team before altering anything that affects credential handling. The deployment shall maintain the configuration described in this control at all times, and the verifier shall treat any deviation as reportable. Adversaries routinely probe for misconfigurations of this control when establishing a foothold against the API edge.

**Implementation guidance.** Retain the prior configuration so that a rollback can be performed without redeploying the node. Document any approved deviation in the exceptions register with a scheduled review date. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. Coordinate with the platform team before altering anything that affects credential handling. Document any approved deviation in the exceptions register with a scheduled review date. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. Retain the prior configuration so that a rollback can be performed without redeploying the node.

**Verification.** Assessors may replay the request sequence after applying fixes to confirm the node has converged. Evidence is the API's response status, headers, and body together with the resulting audit ledger rows. Evidence is the API's response status, headers, and body together with the resulting audit ledger rows. The verifier records the request and response for inclusion in the assessment package. Verification is performed by replaying a sequence of requests and comparing each response to the normalized policy expectation.

**References.** Prior assessment finding AF-4; Vendor hardening note VHN-3-3; Governing Security Policy GSP-2024 §2.3

**Revision history.**
- 2022-05: editorial revision to IR-001; clarified scope and wording.
- 2025-02: editorial revision to IR-001; clarified scope and wording.


### IR-002 — Mandatory console access

**Domain:** Incident Response  **Severity:** Moderate  **Applies to:** internet-facing API nodes

**Rationale.** Adversaries routinely probe for misconfigurations of this control when establishing a foothold against the API edge. Consistent enforcement reduces the mean time to detect anomalous access across the fleet. Operational experience shows that small deviations here cascade into larger exposure during incident response. Adversaries routinely probe for misconfigurations of this control when establishing a foothold against the API edge.

**Requirement.** When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. The deployment shall maintain the configuration described in this control at all times, and the verifier shall treat any deviation as reportable. The control supports reproducible deployments of the API baseline and simplifies forensic comparison.

**Implementation guidance.** Retain the prior configuration so that a rollback can be performed without redeploying the node. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. Operators should prefer configuration that is idempotent so that re-deploying the API produces no further changes. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. Prefer explicit values over relying on framework defaults, which may vary between runtime versions.

**Verification.** Evidence is the API's response status, headers, and body together with the resulting audit ledger rows. Verification is performed by replaying a sequence of requests and comparing each response to the normalized policy expectation. The verifier records the request and response for inclusion in the assessment package.

**References.** Prior assessment finding AF-2; Baseline Configuration Guide BCG-2.0; Baseline Configuration Guide BCG-2.7; Baseline Configuration Guide BCG-6.8

**Revision history.**
- 2022-09: editorial revision to IR-002; clarified scope and wording.
- 2023-02: editorial revision to IR-002; clarified scope and wording.
- 2022-09: editorial revision to IR-002; clarified scope and wording.


### IR-003 — Mandatory request logging

**Domain:** Incident Response  **Severity:** High  **Applies to:** all HarborDesk API deployments

**Rationale.** Adversaries routinely probe for misconfigurations of this control when establishing a foothold against the API edge. Operational experience shows that small deviations here cascade into larger exposure during incident response. Adversaries routinely probe for misconfigurations of this control when establishing a foothold against the API edge. Consistent enforcement reduces the mean time to detect anomalous access across the fleet.

**Requirement.** Coordinate with the platform team before altering anything that affects credential handling. The deployment shall maintain the configuration described in this control at all times, and the verifier shall treat any deviation as reportable. Operational experience shows that small deviations here cascade into larger exposure during incident response.

**Implementation guidance.** Coordinate with the platform team before altering anything that affects credential handling. Prefer explicit values over relying on framework defaults, which may vary between runtime versions. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. Document any approved deviation in the exceptions register with a scheduled review date. Retain the prior configuration so that a rollback can be performed without redeploying the node. Changes should be staged in a non-production environment and validated against the verification procedure below. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner.

**Verification.** Assessors may replay the request sequence after applying fixes to confirm the node has converged. Evidence is the API's response status, headers, and body together with the resulting audit ledger rows. Evidence is the API's response status, headers, and body together with the resulting audit ledger rows. Verification is performed by replaying a sequence of requests and comparing each response to the normalized policy expectation. Verification is performed by replaying a sequence of requests and comparing each response to the normalized policy expectation.

**References.** Edge Operations Runbook ROB-3; Edge Operations Runbook ROB-9; Baseline Configuration Guide BCG-4.5

**Revision history.**
- 2022-04: editorial revision to IR-003; clarified scope and wording.
- 2024-07: editorial revision to IR-003; clarified scope and wording.
- 2025-01: editorial revision to IR-003; clarified scope and wording.
- 2023-05: editorial revision to IR-003; clarified scope and wording.


### IR-004 — Monitored log forwarding

**Domain:** Incident Response  **Severity:** Critical  **Applies to:** internet-facing API nodes

**Rationale.** This requirement aligns the API with the principle of least privilege mandated by the governing security policy. Adversaries routinely probe for misconfigurations of this control when establishing a foothold against the API edge. This requirement aligns the API with the principle of least privilege mandated by the governing security policy. Consistent enforcement reduces the mean time to detect anomalous access across the fleet. Inconsistent application of this requirement across nodes complicates evidence collection and weakens attestations.

**Requirement.** Changes should be staged in a non-production environment and validated against the verification procedure below. The deployment shall maintain the configuration described in this control at all times, and the verifier shall treat any deviation as reportable. Adversaries routinely probe for misconfigurations of this control when establishing a foothold against the API edge.

**Implementation guidance.** Retain the prior configuration so that a rollback can be performed without redeploying the node. Prefer explicit values over relying on framework defaults, which may vary between runtime versions. Changes should be staged in a non-production environment and validated against the verification procedure below. Operators should prefer configuration that is idempotent so that re-deploying the API produces no further changes. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. Retain the prior configuration so that a rollback can be performed without redeploying the node. Coordinate with the platform team before altering anything that affects credential handling. Changes should be staged in a non-production environment and validated against the verification procedure below.

**Verification.** Automated property checks generate varied request sequences to confirm the control behaves consistently. Automated property checks generate varied request sequences to confirm the control behaves consistently. Evidence is the API's response status, headers, and body together with the resulting audit ledger rows. The verifier records the request and response for inclusion in the assessment package.

**References.** Edge Operations Runbook ROB-5; Governing Security Policy GSP-2024 §5.8

**Revision history.**
- 2025-12: editorial revision to IR-004; clarified scope and wording.
- 2023-01: editorial revision to IR-004; clarified scope and wording.
- 2023-01: editorial revision to IR-004; clarified scope and wording.


### IR-005 — Mandatory cache directive

**Domain:** Incident Response  **Severity:** Critical  **Applies to:** internal staging deployments

**Rationale.** Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment. Operational experience shows that small deviations here cascade into larger exposure during incident response. This requirement aligns the API with the principle of least privilege mandated by the governing security policy.

**Requirement.** Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. The deployment shall maintain the configuration described in this control at all times, and the verifier shall treat any deviation as reportable. This requirement aligns the API with the principle of least privilege mandated by the governing security policy.

**Implementation guidance.** Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. Coordinate with the platform team before altering anything that affects credential handling. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. Retain the prior configuration so that a rollback can be performed without redeploying the node. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner.

**Verification.** Evidence is the API's response status, headers, and body together with the resulting audit ledger rows. The verifier records the request and response for inclusion in the assessment package. Evidence is the API's response status, headers, and body together with the resulting audit ledger rows. Verification is performed by replaying a sequence of requests and comparing each response to the normalized policy expectation.

**References.** Vendor hardening note VHN-4-9; Governing Security Policy GSP-2024 §8.5; Governing Security Policy GSP-2024 §6.1

**Revision history.**
- 2023-01: editorial revision to IR-005; clarified scope and wording.
- 2025-09: editorial revision to IR-005; clarified scope and wording.
- 2024-08: editorial revision to IR-005; clarified scope and wording.
- 2022-02: editorial revision to IR-005; clarified scope and wording.


### IR-006 — Standard package provenance

**Domain:** Incident Response  **Severity:** Moderate  **Applies to:** all HarborDesk API deployments

**Rationale.** Operational experience shows that small deviations here cascade into larger exposure during incident response. This requirement aligns the API with the principle of least privilege mandated by the governing security policy. Adversaries routinely probe for misconfigurations of this control when establishing a foothold against the API edge. Operational experience shows that small deviations here cascade into larger exposure during incident response.

**Requirement.** Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. The deployment shall maintain the configuration described in this control at all times, and the verifier shall treat any deviation as reportable. Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment.

**Implementation guidance.** Prefer explicit values over relying on framework defaults, which may vary between runtime versions. Operators should prefer configuration that is idempotent so that re-deploying the API produces no further changes. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. Document any approved deviation in the exceptions register with a scheduled review date. Prefer explicit values over relying on framework defaults, which may vary between runtime versions. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner.

**Verification.** Evidence is the API's response status, headers, and body together with the resulting audit ledger rows. Evidence is the API's response status, headers, and body together with the resulting audit ledger rows. Automated property checks generate varied request sequences to confirm the control behaves consistently. Evidence is the API's response status, headers, and body together with the resulting audit ledger rows.

**References.** Prior assessment finding AF-4; Vendor hardening note VHN-9-5; Baseline Configuration Guide BCG-2.2; Baseline Configuration Guide BCG-8.5

**Revision history.**
- 2022-08: editorial revision to IR-006; clarified scope and wording.
- 2023-09: editorial revision to IR-006; clarified scope and wording.
- 2022-11: editorial revision to IR-006; clarified scope and wording.
- 2023-04: editorial revision to IR-006; clarified scope and wording.


### IR-007 — Monitored content-type enforcement

**Domain:** Incident Response  **Severity:** Low  **Applies to:** edge and gateway deployments

**Rationale.** Consistent enforcement reduces the mean time to detect anomalous access across the fleet. The control exists to keep responses deterministic so that repeated assessments converge on a stable state. Consistent enforcement reduces the mean time to detect anomalous access across the fleet.

**Requirement.** Operators should prefer configuration that is idempotent so that re-deploying the API produces no further changes. The deployment shall maintain the configuration described in this control at all times, and the verifier shall treat any deviation as reportable. Consistent enforcement reduces the mean time to detect anomalous access across the fleet.

**Implementation guidance.** Changes should be staged in a non-production environment and validated against the verification procedure below. Retain the prior configuration so that a rollback can be performed without redeploying the node. Prefer explicit values over relying on framework defaults, which may vary between runtime versions. Retain the prior configuration so that a rollback can be performed without redeploying the node. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. Document any approved deviation in the exceptions register with a scheduled review date. Coordinate with the platform team before altering anything that affects credential handling.

**Verification.** Assessors may replay the request sequence after applying fixes to confirm the node has converged. Verification is performed by replaying a sequence of requests and comparing each response to the normalized policy expectation. Assessors may replay the request sequence after applying fixes to confirm the node has converged. The verifier records the request and response for inclusion in the assessment package.

**References.** Baseline Configuration Guide BCG-2.1; Governing Security Policy GSP-2024 §8.3; Governing Security Policy GSP-2024 §8.7; Governing Security Policy GSP-2024 §7.7

**Revision history.**
- 2025-10: editorial revision to IR-007; clarified scope and wording.
- 2024-08: editorial revision to IR-007; clarified scope and wording.
- 2022-07: editorial revision to IR-007; clarified scope and wording.
- 2022-12: editorial revision to IR-007; clarified scope and wording.


### IR-008 — Monitored response compression

**Domain:** Incident Response  **Severity:** High  **Applies to:** internet-facing API nodes

**Rationale.** Adversaries routinely probe for misconfigurations of this control when establishing a foothold against the API edge. Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment. Adversaries routinely probe for misconfigurations of this control when establishing a foothold against the API edge. Operational experience shows that small deviations here cascade into larger exposure during incident response.

**Requirement.** Coordinate with the platform team before altering anything that affects credential handling. The deployment shall maintain the configuration described in this control at all times, and the verifier shall treat any deviation as reportable. Consistent enforcement reduces the mean time to detect anomalous access across the fleet.

**Implementation guidance.** Document any approved deviation in the exceptions register with a scheduled review date. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. Operators should prefer configuration that is idempotent so that re-deploying the API produces no further changes. Retain the prior configuration so that a rollback can be performed without redeploying the node. Changes should be staged in a non-production environment and validated against the verification procedure below.

**Verification.** Evidence is the API's response status, headers, and body together with the resulting audit ledger rows. Automated property checks generate varied request sequences to confirm the control behaves consistently. Evidence is the API's response status, headers, and body together with the resulting audit ledger rows. Verification is performed by replaying a sequence of requests and comparing each response to the normalized policy expectation. Verification is performed by replaying a sequence of requests and comparing each response to the normalized policy expectation.

**References.** Vendor hardening note VHN-2-2; Prior assessment finding AF-6; Vendor hardening note VHN-8-3

**Revision history.**
- 2025-04: editorial revision to IR-008; clarified scope and wording.
- 2025-02: editorial revision to IR-008; clarified scope and wording.


### IR-009 — Centralized package provenance

**Domain:** Incident Response  **Severity:** Moderate  **Applies to:** credential-bearing API nodes

**Rationale.** Adversaries routinely probe for misconfigurations of this control when establishing a foothold against the API edge. The control supports reproducible deployments of the API baseline and simplifies forensic comparison. The control exists to keep responses deterministic so that repeated assessments converge on a stable state. Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment.

**Requirement.** Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. The deployment shall maintain the configuration described in this control at all times, and the verifier shall treat any deviation as reportable. This requirement aligns the API with the principle of least privilege mandated by the governing security policy.

**Implementation guidance.** Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. Retain the prior configuration so that a rollback can be performed without redeploying the node. Operators should prefer configuration that is idempotent so that re-deploying the API produces no further changes. Changes should be staged in a non-production environment and validated against the verification procedure below. Coordinate with the platform team before altering anything that affects credential handling. Operators should prefer configuration that is idempotent so that re-deploying the API produces no further changes. Retain the prior configuration so that a rollback can be performed without redeploying the node.

**Verification.** Assessors may replay the request sequence after applying fixes to confirm the node has converged. Evidence is the API's response status, headers, and body together with the resulting audit ledger rows. Verification is performed by replaying a sequence of requests and comparing each response to the normalized policy expectation.

**References.** Governing Security Policy GSP-2024 §4.1; Baseline Configuration Guide BCG-5.4; Prior assessment finding AF-4

**Revision history.**
- 2022-10: editorial revision to IR-009; clarified scope and wording.
- 2025-05: editorial revision to IR-009; clarified scope and wording.
- 2024-05: editorial revision to IR-009; clarified scope and wording.


### IR-010 — Hardened package provenance

**Domain:** Incident Response  **Severity:** Low  **Applies to:** all HarborDesk API deployments

**Rationale.** Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment. The control supports reproducible deployments of the API baseline and simplifies forensic comparison. This requirement aligns the API with the principle of least privilege mandated by the governing security policy.

**Requirement.** Coordinate with the platform team before altering anything that affects credential handling. The deployment shall maintain the configuration described in this control at all times, and the verifier shall treat any deviation as reportable. Operational experience shows that small deviations here cascade into larger exposure during incident response.

**Implementation guidance.** Retain the prior configuration so that a rollback can be performed without redeploying the node. Changes should be staged in a non-production environment and validated against the verification procedure below. Document any approved deviation in the exceptions register with a scheduled review date. Coordinate with the platform team before altering anything that affects credential handling. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. Prefer explicit values over relying on framework defaults, which may vary between runtime versions.

**Verification.** Assessors may replay the request sequence after applying fixes to confirm the node has converged. The verifier records the request and response for inclusion in the assessment package. Evidence is the API's response status, headers, and body together with the resulting audit ledger rows. Assessors may replay the request sequence after applying fixes to confirm the node has converged. Automated property checks generate varied request sequences to confirm the control behaves consistently.

**References.** Governing Security Policy GSP-2024 §6.9; Prior assessment finding AF-2; Vendor hardening note VHN-9-4

**Revision history.**
- 2025-10: editorial revision to IR-010; clarified scope and wording.
- 2025-06: editorial revision to IR-010; clarified scope and wording.
- 2024-03: editorial revision to IR-010; clarified scope and wording.
- 2023-06: editorial revision to IR-010; clarified scope and wording.


### IR-011 — Mandatory log forwarding

**Domain:** Incident Response  **Severity:** High  **Applies to:** edge and gateway deployments

**Rationale.** Operational experience shows that small deviations here cascade into larger exposure during incident response. Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment. Inconsistent application of this requirement across nodes complicates evidence collection and weakens attestations. Consistent enforcement reduces the mean time to detect anomalous access across the fleet. This requirement aligns the API with the principle of least privilege mandated by the governing security policy.

**Requirement.** Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. The deployment shall maintain the configuration described in this control at all times, and the verifier shall treat any deviation as reportable. Operational experience shows that small deviations here cascade into larger exposure during incident response.

**Implementation guidance.** Prefer explicit values over relying on framework defaults, which may vary between runtime versions. Retain the prior configuration so that a rollback can be performed without redeploying the node. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. Document any approved deviation in the exceptions register with a scheduled review date. Retain the prior configuration so that a rollback can be performed without redeploying the node. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. Prefer explicit values over relying on framework defaults, which may vary between runtime versions.

**Verification.** Evidence is the API's response status, headers, and body together with the resulting audit ledger rows. Verification is performed by replaying a sequence of requests and comparing each response to the normalized policy expectation. The verifier records the request and response for inclusion in the assessment package. Verification is performed by replaying a sequence of requests and comparing each response to the normalized policy expectation. Evidence is the API's response status, headers, and body together with the resulting audit ledger rows.

**References.** Edge Operations Runbook ROB-6; Prior assessment finding AF-1; Prior assessment finding AF-1

**Revision history.**
- 2025-10: editorial revision to IR-011; clarified scope and wording.
- 2024-05: editorial revision to IR-011; clarified scope and wording.


### IR-012 — Restricted console access

**Domain:** Incident Response  **Severity:** Low  **Applies to:** edge and gateway deployments

**Rationale.** Adversaries routinely probe for misconfigurations of this control when establishing a foothold against the API edge. Operational experience shows that small deviations here cascade into larger exposure during incident response. This requirement aligns the API with the principle of least privilege mandated by the governing security policy.

**Requirement.** Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. The deployment shall maintain the configuration described in this control at all times, and the verifier shall treat any deviation as reportable. This requirement aligns the API with the principle of least privilege mandated by the governing security policy.

**Implementation guidance.** Changes should be staged in a non-production environment and validated against the verification procedure below. Document any approved deviation in the exceptions register with a scheduled review date. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. Retain the prior configuration so that a rollback can be performed without redeploying the node. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. Document any approved deviation in the exceptions register with a scheduled review date. Changes should be staged in a non-production environment and validated against the verification procedure below.

**Verification.** Automated property checks generate varied request sequences to confirm the control behaves consistently. Automated property checks generate varied request sequences to confirm the control behaves consistently. Assessors may replay the request sequence after applying fixes to confirm the node has converged.

**References.** Baseline Configuration Guide BCG-2.3; Governing Security Policy GSP-2024 §4.6; Vendor hardening note VHN-2-7; Baseline Configuration Guide BCG-5.5

**Revision history.**
- 2023-02: editorial revision to IR-012; clarified scope and wording.
- 2023-01: editorial revision to IR-012; clarified scope and wording.
- 2024-10: editorial revision to IR-012; clarified scope and wording.


## Appendix A. Deployment classification


- **SV-648**: Coordinate with the platform team before altering anything that affects credential handling. Prefer explicit values over relying on framework defaults, which may vary between runtime versions.

- **SV-740**: When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. Changes should be staged in a non-production environment and validated against the verification procedure below. Prefer explicit values over relying on framework defaults, which may vary between runtime versions.

- **GW-292**: When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. Coordinate with the platform team before altering anything that affects credential handling. Prefer explicit values over relying on framework defaults, which may vary between runtime versions.

- **ED-433**: Retain the prior configuration so that a rollback can be performed without redeploying the node. Changes should be staged in a non-production environment and validated against the verification procedure below.

- **DC-191**: Retain the prior configuration so that a rollback can be performed without redeploying the node. Changes should be staged in a non-production environment and validated against the verification procedure below.

- **ED-107**: Coordinate with the platform team before altering anything that affects credential handling. Prefer explicit values over relying on framework defaults, which may vary between runtime versions.

- **DC-302**: Changes should be staged in a non-production environment and validated against the verification procedure below. Prefer explicit values over relying on framework defaults, which may vary between runtime versions.

- **SV-820**: Coordinate with the platform team before altering anything that affects credential handling. Changes should be staged in a non-production environment and validated against the verification procedure below.

- **GW-515**: Document any approved deviation in the exceptions register with a scheduled review date. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies.

- **ED-612**: Retain the prior configuration so that a rollback can be performed without redeploying the node. Document any approved deviation in the exceptions register with a scheduled review date. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies.


## Appendix C. Banner and cipher wording

Prefer explicit values over relying on framework defaults, which may vary between runtime versions. Operators should prefer configuration that is idempotent so that re-deploying the API produces no further changes. Operators should prefer configuration that is idempotent so that re-deploying the API produces no further changes. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. Changes should be staged in a non-production environment and validated against the verification procedure below. Prefer explicit values over relying on framework defaults, which may vary between runtime versions.


## Appendix B. Control rationale narratives


### Narrative XB-35

Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. The control supports reproducible deployments of the API baseline and simplifies forensic comparison. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. This requirement aligns the API with the principle of least privilege mandated by the governing security policy. The control supports reproducible deployments of the API baseline and simplifies forensic comparison. Inconsistent application of this requirement across nodes complicates evidence collection and weakens attestations. This requirement aligns the API with the principle of least privilege mandated by the governing security policy.

### Narrative XB-44

Retain the prior configuration so that a rollback can be performed without redeploying the node. Retain the prior configuration so that a rollback can be performed without redeploying the node. Retain the prior configuration so that a rollback can be performed without redeploying the node. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. Adversaries routinely probe for misconfigurations of this control when establishing a foothold against the API edge. Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. Prefer explicit values over relying on framework defaults, which may vary between runtime versions. Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment.

### Narrative RB-75

Retain the prior configuration so that a rollback can be performed without redeploying the node. Adversaries routinely probe for misconfigurations of this control when establishing a foothold against the API edge. Retain the prior configuration so that a rollback can be performed without redeploying the node. The control supports reproducible deployments of the API baseline and simplifies forensic comparison. Adversaries routinely probe for misconfigurations of this control when establishing a foothold against the API edge. Operators should prefer configuration that is idempotent so that re-deploying the API produces no further changes. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner.

### Narrative RB-31

Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. Inconsistent application of this requirement across nodes complicates evidence collection and weakens attestations. Adversaries routinely probe for misconfigurations of this control when establishing a foothold against the API edge. Changes should be staged in a non-production environment and validated against the verification procedure below. Adversaries routinely probe for misconfigurations of this control when establishing a foothold against the API edge. Consistent enforcement reduces the mean time to detect anomalous access across the fleet. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner.

### Narrative RB-87

The control exists to keep responses deterministic so that repeated assessments converge on a stable state. This requirement aligns the API with the principle of least privilege mandated by the governing security policy. Retain the prior configuration so that a rollback can be performed without redeploying the node. The control exists to keep responses deterministic so that repeated assessments converge on a stable state. Changes should be staged in a non-production environment and validated against the verification procedure below. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. The control exists to keep responses deterministic so that repeated assessments converge on a stable state. Document any approved deviation in the exceptions register with a scheduled review date. Changes should be staged in a non-production environment and validated against the verification procedure below. Consistent enforcement reduces the mean time to detect anomalous access across the fleet.

### Narrative XB-47

Adversaries routinely probe for misconfigurations of this control when establishing a foothold against the API edge. Changes should be staged in a non-production environment and validated against the verification procedure below. Consistent enforcement reduces the mean time to detect anomalous access across the fleet. Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment. Retain the prior configuration so that a rollback can be performed without redeploying the node. Coordinate with the platform team before altering anything that affects credential handling. Consistent enforcement reduces the mean time to detect anomalous access across the fleet. Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment. The control supports reproducible deployments of the API baseline and simplifies forensic comparison.

### Narrative NB-33

The control supports reproducible deployments of the API baseline and simplifies forensic comparison. Adversaries routinely probe for misconfigurations of this control when establishing a foothold against the API edge. Adversaries routinely probe for misconfigurations of this control when establishing a foothold against the API edge. The control supports reproducible deployments of the API baseline and simplifies forensic comparison. Prefer explicit values over relying on framework defaults, which may vary between runtime versions. Operators should prefer configuration that is idempotent so that re-deploying the API produces no further changes. Consistent enforcement reduces the mean time to detect anomalous access across the fleet. Document any approved deviation in the exceptions register with a scheduled review date. Document any approved deviation in the exceptions register with a scheduled review date. Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment.

### Narrative RB-60

When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. Adversaries routinely probe for misconfigurations of this control when establishing a foothold against the API edge. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. Adversaries routinely probe for misconfigurations of this control when establishing a foothold against the API edge. The control supports reproducible deployments of the API baseline and simplifies forensic comparison. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. The control supports reproducible deployments of the API baseline and simplifies forensic comparison.

### Narrative XB-90

When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. Changes should be staged in a non-production environment and validated against the verification procedure below. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner.

### Narrative XB-70

Operators should prefer configuration that is idempotent so that re-deploying the API produces no further changes. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment. Document any approved deviation in the exceptions register with a scheduled review date. The control supports reproducible deployments of the API baseline and simplifies forensic comparison. The control supports reproducible deployments of the API baseline and simplifies forensic comparison. Consistent enforcement reduces the mean time to detect anomalous access across the fleet. This requirement aligns the API with the principle of least privilege mandated by the governing security policy. Operators should prefer configuration that is idempotent so that re-deploying the API produces no further changes.

### Narrative NB-26

Adversaries routinely probe for misconfigurations of this control when establishing a foothold against the API edge. This requirement aligns the API with the principle of least privilege mandated by the governing security policy. Operational experience shows that small deviations here cascade into larger exposure during incident response. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. This requirement aligns the API with the principle of least privilege mandated by the governing security policy. This requirement aligns the API with the principle of least privilege mandated by the governing security policy.

### Narrative RB-34

When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. Prefer explicit values over relying on framework defaults, which may vary between runtime versions. The control exists to keep responses deterministic so that repeated assessments converge on a stable state. The control exists to keep responses deterministic so that repeated assessments converge on a stable state. Document any approved deviation in the exceptions register with a scheduled review date. Adversaries routinely probe for misconfigurations of this control when establishing a foothold against the API edge.

### Narrative RB-79

Changes should be staged in a non-production environment and validated against the verification procedure below. Adversaries routinely probe for misconfigurations of this control when establishing a foothold against the API edge. Document any approved deviation in the exceptions register with a scheduled review date. Inconsistent application of this requirement across nodes complicates evidence collection and weakens attestations. Adversaries routinely probe for misconfigurations of this control when establishing a foothold against the API edge. The control exists to keep responses deterministic so that repeated assessments converge on a stable state. Inconsistent application of this requirement across nodes complicates evidence collection and weakens attestations.

### Narrative NB-37

Coordinate with the platform team before altering anything that affects credential handling. Operators should prefer configuration that is idempotent so that re-deploying the API produces no further changes. Operators should prefer configuration that is idempotent so that re-deploying the API produces no further changes. The control supports reproducible deployments of the API baseline and simplifies forensic comparison. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. Operational experience shows that small deviations here cascade into larger exposure during incident response. The control exists to keep responses deterministic so that repeated assessments converge on a stable state. Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment. Changes should be staged in a non-production environment and validated against the verification procedure below. Coordinate with the platform team before altering anything that affects credential handling.

### Narrative NB-55

Retain the prior configuration so that a rollback can be performed without redeploying the node. Inconsistent application of this requirement across nodes complicates evidence collection and weakens attestations. Adversaries routinely probe for misconfigurations of this control when establishing a foothold against the API edge. Prefer explicit values over relying on framework defaults, which may vary between runtime versions. Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment. Retain the prior configuration so that a rollback can be performed without redeploying the node.

### Narrative RB-29

Coordinate with the platform team before altering anything that affects credential handling. Coordinate with the platform team before altering anything that affects credential handling. Prefer explicit values over relying on framework defaults, which may vary between runtime versions. Coordinate with the platform team before altering anything that affects credential handling. Consistent enforcement reduces the mean time to detect anomalous access across the fleet. Document any approved deviation in the exceptions register with a scheduled review date. Prefer explicit values over relying on framework defaults, which may vary between runtime versions. Operational experience shows that small deviations here cascade into larger exposure during incident response. Operators should prefer configuration that is idempotent so that re-deploying the API produces no further changes.

### Narrative RB-56

Operational experience shows that small deviations here cascade into larger exposure during incident response. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. Prefer explicit values over relying on framework defaults, which may vary between runtime versions. Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment. Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment. Coordinate with the platform team before altering anything that affects credential handling. Document any approved deviation in the exceptions register with a scheduled review date. Operators should prefer configuration that is idempotent so that re-deploying the API produces no further changes. Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment. Operational experience shows that small deviations here cascade into larger exposure during incident response.

### Narrative RB-81

Retain the prior configuration so that a rollback can be performed without redeploying the node. Changes should be staged in a non-production environment and validated against the verification procedure below. Changes should be staged in a non-production environment and validated against the verification procedure below. This requirement aligns the API with the principle of least privilege mandated by the governing security policy. The control exists to keep responses deterministic so that repeated assessments converge on a stable state. Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment. Retain the prior configuration so that a rollback can be performed without redeploying the node. Inconsistent application of this requirement across nodes complicates evidence collection and weakens attestations. Consistent enforcement reduces the mean time to detect anomalous access across the fleet. Adversaries routinely probe for misconfigurations of this control when establishing a foothold against the API edge.

### Narrative XB-47

Inconsistent application of this requirement across nodes complicates evidence collection and weakens attestations. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. Consistent enforcement reduces the mean time to detect anomalous access across the fleet. Inconsistent application of this requirement across nodes complicates evidence collection and weakens attestations. Operators should prefer configuration that is idempotent so that re-deploying the API produces no further changes. Changes should be staged in a non-production environment and validated against the verification procedure below. The control supports reproducible deployments of the API baseline and simplifies forensic comparison. Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment. Coordinate with the platform team before altering anything that affects credential handling. Operational experience shows that small deviations here cascade into larger exposure during incident response.


## Appendix D. Assessment procedures


- **Procedure 199.** Automated property checks generate varied request sequences to confirm the control behaves consistently. The verifier records the request and response for inclusion in the assessment package. The verifier records the request and response for inclusion in the assessment package. Assessors may replay the request sequence after applying fixes to confirm the node has converged.

- **Procedure 342.** Automated property checks generate varied request sequences to confirm the control behaves consistently. The verifier records the request and response for inclusion in the assessment package. Operators should prefer configuration that is idempotent so that re-deploying the API produces no further changes. Changes should be staged in a non-production environment and validated against the verification procedure below.

- **Procedure 895.** Evidence is the API's response status, headers, and body together with the resulting audit ledger rows. Coordinate with the platform team before altering anything that affects credential handling. Prefer explicit values over relying on framework defaults, which may vary between runtime versions.

- **Procedure 860.** Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. Retain the prior configuration so that a rollback can be performed without redeploying the node. Evidence is the API's response status, headers, and body together with the resulting audit ledger rows.

- **Procedure 532.** Verification is performed by replaying a sequence of requests and comparing each response to the normalized policy expectation. Assessors may replay the request sequence after applying fixes to confirm the node has converged. Coordinate with the platform team before altering anything that affects credential handling.

- **Procedure 617.** Retain the prior configuration so that a rollback can be performed without redeploying the node. Assessors may replay the request sequence after applying fixes to confirm the node has converged. Automated property checks generate varied request sequences to confirm the control behaves consistently. The verifier records the request and response for inclusion in the assessment package.

- **Procedure 758.** Retain the prior configuration so that a rollback can be performed without redeploying the node. Coordinate with the platform team before altering anything that affects credential handling. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner.

- **Procedure 428.** When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. Evidence is the API's response status, headers, and body together with the resulting audit ledger rows. Retain the prior configuration so that a rollback can be performed without redeploying the node. Document any approved deviation in the exceptions register with a scheduled review date.

- **Procedure 164.** Coordinate with the platform team before altering anything that affects credential handling. Changes should be staged in a non-production environment and validated against the verification procedure below. Coordinate with the platform team before altering anything that affects credential handling. The verifier records the request and response for inclusion in the assessment package.

- **Procedure 610.** Automated property checks generate varied request sequences to confirm the control behaves consistently. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. Changes should be staged in a non-production environment and validated against the verification procedure below.

- **Procedure 974.** Automated property checks generate varied request sequences to confirm the control behaves consistently. Evidence is the API's response status, headers, and body together with the resulting audit ledger rows. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies.

- **Procedure 396.** The verifier records the request and response for inclusion in the assessment package. Coordinate with the platform team before altering anything that affects credential handling. Assessors may replay the request sequence after applying fixes to confirm the node has converged. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies.

- **Procedure 773.** When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. Prefer explicit values over relying on framework defaults, which may vary between runtime versions. Assessors may replay the request sequence after applying fixes to confirm the node has converged.

- **Procedure 655.** When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. Prefer explicit values over relying on framework defaults, which may vary between runtime versions. Assessors may replay the request sequence after applying fixes to confirm the node has converged. Evidence is the API's response status, headers, and body together with the resulting audit ledger rows.

- **Procedure 598.** The verifier records the request and response for inclusion in the assessment package. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. Document any approved deviation in the exceptions register with a scheduled review date. Coordinate with the platform team before altering anything that affects credential handling.

- **Procedure 466.** Document any approved deviation in the exceptions register with a scheduled review date. Operators should prefer configuration that is idempotent so that re-deploying the API produces no further changes. Changes should be staged in a non-production environment and validated against the verification procedure below. Operators should prefer configuration that is idempotent so that re-deploying the API produces no further changes.

- **Procedure 463.** Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. Changes should be staged in a non-production environment and validated against the verification procedure below. Verification is performed by replaying a sequence of requests and comparing each response to the normalized policy expectation.

- **Procedure 500.** When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. Prefer explicit values over relying on framework defaults, which may vary between runtime versions. Retain the prior configuration so that a rollback can be performed without redeploying the node.


## Appendix E. Change log


- 2026-01-23: Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment.

- 2025-09-01: Document any approved deviation in the exceptions register with a scheduled review date. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner.

- 2025-07-06: Coordinate with the platform team before altering anything that affects credential handling.

- 2024-08-09: Inconsistent application of this requirement across nodes complicates evidence collection and weakens attestations. Changes should be staged in a non-production environment and validated against the verification procedure below.

- 2026-02-09: Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. Prefer explicit values over relying on framework defaults, which may vary between runtime versions.

- 2024-12-22: Consistent enforcement reduces the mean time to detect anomalous access across the fleet.

- 2023-08-20: Document any approved deviation in the exceptions register with a scheduled review date. Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment.

- 2025-08-03: This requirement aligns the API with the principle of least privilege mandated by the governing security policy.

- 2025-02-19: Coordinate with the platform team before altering anything that affects credential handling.

- 2023-07-09: Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. The control exists to keep responses deterministic so that repeated assessments converge on a stable state.

- 2026-11-04: Operational experience shows that small deviations here cascade into larger exposure during incident response. Document any approved deviation in the exceptions register with a scheduled review date.

- 2025-08-27: This requirement aligns the API with the principle of least privilege mandated by the governing security policy.

- 2026-04-09: Consistent enforcement reduces the mean time to detect anomalous access across the fleet.

- 2024-02-20: This requirement aligns the API with the principle of least privilege mandated by the governing security policy. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner.

- 2023-03-18: Operators should prefer configuration that is idempotent so that re-deploying the API produces no further changes.

- 2023-11-01: Coordinate with the platform team before altering anything that affects credential handling.

- 2025-06-11: Operators should prefer configuration that is idempotent so that re-deploying the API produces no further changes.

- 2023-07-19: Prefer explicit values over relying on framework defaults, which may vary between runtime versions.

- 2023-10-18: Changes should be staged in a non-production environment and validated against the verification procedure below.

- 2025-03-25: Retain the prior configuration so that a rollback can be performed without redeploying the node. The control supports reproducible deployments of the API baseline and simplifies forensic comparison.

- 2025-01-27: This requirement aligns the API with the principle of least privilege mandated by the governing security policy.

- 2023-07-21: Operational experience shows that small deviations here cascade into larger exposure during incident response.

- 2023-08-07: The control supports reproducible deployments of the API baseline and simplifies forensic comparison.

- 2025-12-20: Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment. The control supports reproducible deployments of the API baseline and simplifies forensic comparison.

- 2026-12-04: Adversaries routinely probe for misconfigurations of this control when establishing a foothold against the API edge.

- 2023-03-13: Operators should prefer configuration that is idempotent so that re-deploying the API produces no further changes. Adversaries routinely probe for misconfigurations of this control when establishing a foothold against the API edge.

- 2025-02-16: Retain the prior configuration so that a rollback can be performed without redeploying the node. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner.

- 2024-02-10: The control exists to keep responses deterministic so that repeated assessments converge on a stable state. Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment.

- 2026-01-28: This requirement aligns the API with the principle of least privilege mandated by the governing security policy. Adversaries routinely probe for misconfigurations of this control when establishing a foothold against the API edge.

- 2023-03-26: When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. Inconsistent application of this requirement across nodes complicates evidence collection and weakens attestations.

- 2026-05-07: The control supports reproducible deployments of the API baseline and simplifies forensic comparison. Prefer explicit values over relying on framework defaults, which may vary between runtime versions.

- 2025-07-07: Coordinate with the platform team before altering anything that affects credential handling. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner.

- 2025-08-14: When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner.

- 2023-10-16: Operational experience shows that small deviations here cascade into larger exposure during incident response. Coordinate with the platform team before altering anything that affects credential handling.

- 2025-07-09: Operators should prefer configuration that is idempotent so that re-deploying the API produces no further changes. The control supports reproducible deployments of the API baseline and simplifies forensic comparison.

- 2026-09-06: Changes should be staged in a non-production environment and validated against the verification procedure below. This requirement aligns the API with the principle of least privilege mandated by the governing security policy.

- 2023-05-04: Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. Coordinate with the platform team before altering anything that affects credential handling.

- 2023-06-05: Changes should be staged in a non-production environment and validated against the verification procedure below. This requirement aligns the API with the principle of least privilege mandated by the governing security policy.

- 2023-03-24: The control exists to keep responses deterministic so that repeated assessments converge on a stable state.

- 2026-12-11: The control exists to keep responses deterministic so that repeated assessments converge on a stable state. Inconsistent application of this requirement across nodes complicates evidence collection and weakens attestations.

- 2025-08-19: Adversaries routinely probe for misconfigurations of this control when establishing a foothold against the API edge. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies.

- 2026-02-24: Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. Operators should prefer configuration that is idempotent so that re-deploying the API produces no further changes.

- 2023-12-24: Consistent enforcement reduces the mean time to detect anomalous access across the fleet.

- 2023-05-07: Consistent enforcement reduces the mean time to detect anomalous access across the fleet. This requirement aligns the API with the principle of least privilege mandated by the governing security policy.

- 2026-12-24: Changes should be staged in a non-production environment and validated against the verification procedure below. Consistent enforcement reduces the mean time to detect anomalous access across the fleet.

- 2025-07-15: Inconsistent application of this requirement across nodes complicates evidence collection and weakens attestations. Operational experience shows that small deviations here cascade into larger exposure during incident response.

- 2026-04-24: Document any approved deviation in the exceptions register with a scheduled review date. Operational experience shows that small deviations here cascade into larger exposure during incident response.

- 2023-08-22: When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. The control supports reproducible deployments of the API baseline and simplifies forensic comparison.

- 2024-10-08: Prefer explicit values over relying on framework defaults, which may vary between runtime versions. This requirement aligns the API with the principle of least privilege mandated by the governing security policy.

- 2023-04-08: Changes should be staged in a non-production environment and validated against the verification procedure below.

- 2023-09-16: When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. Changes should be staged in a non-production environment and validated against the verification procedure below.

- 2026-04-15: Prefer explicit values over relying on framework defaults, which may vary between runtime versions.

- 2023-06-23: Prefer explicit values over relying on framework defaults, which may vary between runtime versions.

- 2023-01-21: The control exists to keep responses deterministic so that repeated assessments converge on a stable state. The control exists to keep responses deterministic so that repeated assessments converge on a stable state.

- 2024-05-25: Inconsistent application of this requirement across nodes complicates evidence collection and weakens attestations. Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment.

- 2025-02-22: Retain the prior configuration so that a rollback can be performed without redeploying the node. Coordinate with the platform team before altering anything that affects credential handling.

- 2026-07-06: Prefer explicit values over relying on framework defaults, which may vary between runtime versions.

- 2025-12-03: Inconsistent application of this requirement across nodes complicates evidence collection and weakens attestations.

- 2025-06-24: Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment. Adversaries routinely probe for misconfigurations of this control when establishing a foothold against the API edge.

- 2026-03-25: Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. Prefer explicit values over relying on framework defaults, which may vary between runtime versions.

- 2023-07-27: Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment.

- 2026-12-17: Adversaries routinely probe for misconfigurations of this control when establishing a foothold against the API edge.

- 2023-02-04: The control exists to keep responses deterministic so that repeated assessments converge on a stable state.

- 2024-02-10: Document any approved deviation in the exceptions register with a scheduled review date. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies.

- 2024-07-13: This requirement aligns the API with the principle of least privilege mandated by the governing security policy. Operators should prefer configuration that is idempotent so that re-deploying the API produces no further changes.

- 2023-09-27: Consistent enforcement reduces the mean time to detect anomalous access across the fleet. Inconsistent application of this requirement across nodes complicates evidence collection and weakens attestations.

- 2025-02-15: Operational experience shows that small deviations here cascade into larger exposure during incident response. Operational experience shows that small deviations here cascade into larger exposure during incident response.

- 2025-02-17: Consistent enforcement reduces the mean time to detect anomalous access across the fleet.

- 2023-12-13: Operators should prefer configuration that is idempotent so that re-deploying the API produces no further changes.

- 2023-06-02: Retain the prior configuration so that a rollback can be performed without redeploying the node.

- 2024-07-22: Where automation is used, ensure the tooling reads the canonical source files rather than cached copies.

- 2026-02-06: Inconsistent application of this requirement across nodes complicates evidence collection and weakens attestations.

- 2026-08-25: This requirement aligns the API with the principle of least privilege mandated by the governing security policy.

- 2026-04-28: When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner.

- 2023-07-11: Coordinate with the platform team before altering anything that affects credential handling. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies.

- 2026-11-09: Inconsistent application of this requirement across nodes complicates evidence collection and weakens attestations. Adversaries routinely probe for misconfigurations of this control when establishing a foothold against the API edge.

- 2026-01-26: Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies.

- 2025-04-26: Coordinate with the platform team before altering anything that affects credential handling.

- 2026-09-24: Operational experience shows that small deviations here cascade into larger exposure during incident response.

- 2023-04-04: Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. Inconsistent application of this requirement across nodes complicates evidence collection and weakens attestations.

- 2026-11-19: Document any approved deviation in the exceptions register with a scheduled review date. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies.


## Appendix G. Amendments (authoritative)


The following amendments are in force and **supersede** the body of the referenced controls per section 1.4. They are listed in effective-date order.


### G-2026-10 — amends SV-BANNER

The approved service banner wording is updated. This amendment does not affect API behavior.


### G-2026-07 — amends NW-TLS-CIPHERS

The approved TLS cipher suite list is updated; see Appendix C. This amendment does not affect API behavior.


### G-2026-12 — amends AC-TOKEN-STORE

The on-disk administrative token representation shall be the lowercase hexadecimal SHA-256 digest of the raw bearer token (64 hex characters). AC-HEALTH shall verify a presented bearer by applying the same digest before comparison.


### G-2026-01 — amends CO-ORIGIN-ALLOW

The origin allowlist in CO-ORIGIN-ALLOW is extended to add the operations console origin `https://ops.harbordesk.internal`. The allowlist is therefore exactly `https://harbordesk.internal` and `https://ops.harbordesk.internal`. Exact-match semantics are unchanged: neither a trailing slash nor a differing port matches.


### G-2026-16 — amends AC-BOOTSTRAP

Before the case-insensitive comparison of G-2026-15, both the presented `X-Bootstrap-Secret` header value and the on-disk bootstrap secret file contents shall be trimmed of leading and trailing ASCII whitespace.


### G-2026-02 — amends CO-PREFLIGHT

The preflight cache lifetime in CO-PREFLIGHT is lowered from `600` to `300` seconds. The `Access-Control-Max-Age` header on an allowed-origin preflight shall therefore be `300`.


### G-2026-08 — amends MA-PATCH-WINDOW

The maintenance window is shifted by one hour for the eastern region. This amendment does not affect API behavior.


### G-2026-05 — amends AC-BOOTSTRAP

The evaluation order of AC-BOOTSTRAP is amended so that the already-bootstrapped check takes precedence over secret validation. After the malformed-input check, an existing administrative token shall cause an `already_bootstrapped` refusal **even when the presented bootstrap secret is absent or wrong**. Secret validation is reached only when no token yet exists.


### G-2026-04 — amends AC-HEALTH

The denial reason for a health request that presents no bearer credential is renamed from `missing_token` to `missing_credentials`. The status (`401`) and the `invalid_token` reason for a present-but-wrong credential are unchanged.


### G-2026-11 — amends CO-PREFLIGHT

The method, header, and max-age hint headers in CO-PREFLIGHT (`Access-Control-Allow-Methods`, `Access-Control-Allow-Headers`, and `Access-Control-Max-Age`) shall be emitted **only** on an `OPTIONS` preflight for an allowed origin. Non-preflight responses (including credentialed `GET` or `POST`) shall carry at most the grant headers of CO-ORIGIN-ALLOW and shall not include those preflight hints.


### G-2026-03 — amends AC-BOOTSTRAP

The refusal status for an already-bootstrapped node is changed from `403` to `409` (Conflict). The decision remains `denied` and the reason remains `already_bootstrapped`; only the HTTP status changes.


### G-2026-15 — amends AC-BOOTSTRAP

Bootstrap secret validation shall compare the presented `X-Bootstrap-Secret` header to the on-disk secret using a **case-insensitive** ASCII match. Letter case in the header value must not cause an otherwise-correct secret to be rejected.


### G-2026-09 — amends IR-CONTACT

The incident-response on-call rotation contact list is revised. This amendment does not affect API behavior.


### G-2026-06 — amends AU-LEDGER-SCOPE

Migration of the legacy ledger is made explicit. The on-disk ledger is in a legacy layout carrying a non-null `actor` column and lacking an `origin` column, which is why current writes fail. Reconciliation shall move the ledger to a layout that records the request `origin` for every audited row (including denials) and no longer requires `actor`, while carrying every pre-existing historical row forward unchanged. When a request carries no `Origin` header, the stored `origin` value for that audited row shall be SQL `NULL`, not an empty string.


### G-2026-13 — amends CO-ORIGIN-ALLOW

Cross-origin grant and preflight hint headers apply only to the current request. When a request carries no `Origin` header, the response shall include none of the headers defined by CO-ORIGIN-ALLOW or CO-PREFLIGHT, even if an earlier request in the same long-lived process carried an allowed origin.


## Appendix H. Implementation checklist

Implementers should confirm that the API, for every request it serves, produces exactly the response and audit row implied by the controls above as amended by Appendix G.

