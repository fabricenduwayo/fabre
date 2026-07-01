# Lab Access Hardening Standard (LAHS)

| Field | Value |
|---|---|
| Document | LAHS |
| Status | In force |
| Edition | 2026.1 |
| Owner | Laboratory Security Engineering |
| Classification | Internal |


## 1. Purpose and scope

This Standard defines the configuration baseline that the lab access gateway's setup auditor enforces. It is the single source of truth for how a host inventory is parsed, normalized, and evaluated into a set of remediation patches. The auditor must agree with this Standard for every host it evaluates.

Adversaries routinely probe for misconfigurations of this control when establishing persistence on laboratory infrastructure. Operational experience shows that small deviations here cascade into larger exposure during incident response. Inconsistent application of this requirement across hosts complicates evidence collection and weakens attestations. Inconsistent application of this requirement across hosts complicates evidence collection and weakens attestations.

### 1.4 Precedence of amendments

This Standard is maintained as a body of numbered controls followed by an authoritative list of amendments in **Appendix G**. Where the body of a control and an amendment in Appendix G disagree, **the amendment in Appendix G governs**. Implementers must therefore read both the relevant control and any amendment that references it before encoding behavior. Amendments that state they do not affect auditor behavior may be noted and disregarded for implementation.


## 2. Definitions


**Account.** An entry in the host `passwd` data with a name, user id, primary group id, and login shell. The control supports reproducible builds of the host baseline and simplifies forensic comparison.


**Disabled account.** An account meeting the criteria of control AC-ACCT-LOCK as amended. Operational experience shows that small deviations here cascade into larger exposure during incident response. The control exists to keep remediation deterministic so that repeated audits converge on a stable state.


**Effective group members.** The membership computed under control AC-GROUP-EFFECTIVE. Adversaries routinely probe for misconfigurations of this control when establishing persistence on laboratory infrastructure. Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment.


**Passwordless sudo.** Sudo authority obtained without a password challenge, as determined under AC-SUDO-NOPASSWD as amended. Operational experience shows that small deviations here cascade into larger exposure during incident response.


**Exempt account.** An account excused from passwordless-sudo remediation under AC-EXEMPT as amended. Consistent enforcement reduces the mean time to detect anomalous access across the estate. Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment.


**Effective sshd value.** The value computed under HD-SSHD-DROPIN as amended. This requirement aligns the gateway with the principle of least privilege mandated by the governing security policy.


**Patch.** A single remediation action proposed by the auditor. Consistent enforcement reduces the mean time to detect anomalous access across the estate.


**Normalized inventory.** The intermediate representation produced after parsing, on which the policy rules operate. Operational experience shows that small deviations here cascade into larger exposure during incident response.


## 3. Access Control

The control exists to keep remediation deterministic so that repeated audits converge on a stable state. Operational experience shows that small deviations here cascade into larger exposure during incident response. Operational experience shows that small deviations here cascade into larger exposure during incident response. Adversaries routinely probe for misconfigurations of this control when establishing persistence on laboratory infrastructure. Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment.


Retain the prior configuration so that a rollback can be performed without rebuilding the host. Retain the prior configuration so that a rollback can be performed without rebuilding the host. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. Changes should be staged in a non-production environment and validated against the verification procedure below.


### AC-001 — Restricted package provenance

**Domain:** Access Control  **Severity:** Moderate  **Applies to:** all managed hosts

**Rationale.** This requirement aligns the gateway with the principle of least privilege mandated by the governing security policy. Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment. The control supports reproducible builds of the host baseline and simplifies forensic comparison.

**Requirement.** Changes should be staged in a non-production environment and validated against the verification procedure below. The host shall maintain the configuration described in this control at all times, and the setup auditor shall treat any deviation as reportable. This requirement aligns the gateway with the principle of least privilege mandated by the governing security policy.

**Implementation guidance.** Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. Prefer explicit values over relying on compiled-in defaults, which may vary between distributions. Operators should prefer configuration that is idempotent so that re-running the auditor produces no further changes. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies.

**Verification.** Automated property checks generate varied host states to confirm the control behaves consistently. Automated property checks generate varied host states to confirm the control behaves consistently. Evidence is the auditor's proposed patch set; a compliant host yields an empty set for this control. Evidence is the auditor's proposed patch set; a compliant host yields an empty set for this control.

**References.** Baseline Configuration Guide BCG-2.0; Governing Security Policy GSP-2024 §5.6; Prior assessment finding AF-5; Prior assessment finding AF-9

**Revision history.**
- 2022-05: editorial revision to AC-001; clarified scope and wording.
- 2022-11: editorial revision to AC-001; clarified scope and wording.
- 2023-01: editorial revision to AC-001; clarified scope and wording.


### AC-ACCT-LOCK — Disabled account determination

**Domain:** Access Control  **Severity:** High  **Applies to:** all managed hosts

**Rationale.** Disabled accounts must not retain a foothold on the host. The auditor classifies each account as enabled or disabled from the parsed account data.

**Requirement.** An account shall be considered **disabled** when either condition holds:

1. its `shadow` password field is empty, or is exactly one of `!`, `*`, or `!!`, or begins with the character `!` (a locked password hash); or
2. its login shell, taken from the seventh field of the `passwd` entry, is one of the non-interactive shells enumerated in control AC-ACCT-SHELL.

A disabled account that still possesses authorized SSH keys is reportable under AC-KEY-REVOKE. *(See Appendix G for amendments to the locked-password value set.)*

**Implementation guidance.** The shadow field is the second colon-separated field of the entry. Comparison of the special tokens is exact except for the leading-`!` rule, which matches any value whose first character is `!`.

**Verification.** The auditor proposes key revocation for disabled accounts that retain keys; a compliant host has no such accounts.

**References.** Governing Security Policy GSP-2024 §4.1; Baseline Configuration Guide BCG-3.2

**Revision history.**
- 2023-02: initial publication of AC-ACCT-LOCK.
- 2024-06: clarified the leading-`!` matching rule.


### AC-002 — Hardened filesystem mount option

**Domain:** Access Control  **Severity:** High  **Applies to:** tier-1 laboratory hosts

**Rationale.** Consistent enforcement reduces the mean time to detect anomalous access across the estate. The control exists to keep remediation deterministic so that repeated audits converge on a stable state. The control supports reproducible builds of the host baseline and simplifies forensic comparison.

**Requirement.** Coordinate with the accounts team before altering anything that affects service-account behavior. The host shall maintain the configuration described in this control at all times, and the setup auditor shall treat any deviation as reportable. Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment.

**Implementation guidance.** Changes should be staged in a non-production environment and validated against the verification procedure below. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. Changes should be staged in a non-production environment and validated against the verification procedure below. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. Coordinate with the accounts team before altering anything that affects service-account behavior. Document any approved deviation in the exceptions register with a scheduled review date.

**Verification.** Assessors may re-run the audit after applying patches to confirm the host has converged. Verification is performed by the setup auditor, which compares the host state to the normalized policy expectation. Verification is performed by the setup auditor, which compares the host state to the normalized policy expectation.

**References.** Governing Security Policy GSP-2024 §9.1; Lab Operations Runbook ROB-2; Prior assessment finding AF-4; Governing Security Policy GSP-2024 §9.3

**Revision history.**
- 2022-04: editorial revision to AC-002; clarified scope and wording.
- 2024-08: editorial revision to AC-002; clarified scope and wording.


### AC-003 — Verified filesystem mount option

**Domain:** Access Control  **Severity:** Low  **Applies to:** all managed hosts

**Rationale.** Operational experience shows that small deviations here cascade into larger exposure during incident response. Consistent enforcement reduces the mean time to detect anomalous access across the estate. Inconsistent application of this requirement across hosts complicates evidence collection and weakens attestations. Operational experience shows that small deviations here cascade into larger exposure during incident response.

**Requirement.** Operators should prefer configuration that is idempotent so that re-running the auditor produces no further changes. The host shall maintain the configuration described in this control at all times, and the setup auditor shall treat any deviation as reportable. This requirement aligns the gateway with the principle of least privilege mandated by the governing security policy.

**Implementation guidance.** Operators should prefer configuration that is idempotent so that re-running the auditor produces no further changes. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. Retain the prior configuration so that a rollback can be performed without rebuilding the host. Changes should be staged in a non-production environment and validated against the verification procedure below. Changes should be staged in a non-production environment and validated against the verification procedure below. Document any approved deviation in the exceptions register with a scheduled review date.

**Verification.** Verification is performed by the setup auditor, which compares the host state to the normalized policy expectation. Evidence is the auditor's proposed patch set; a compliant host yields an empty set for this control. Verification is performed by the setup auditor, which compares the host state to the normalized policy expectation. Verification is performed by the setup auditor, which compares the host state to the normalized policy expectation. Assessors may re-run the audit after applying patches to confirm the host has converged.

**References.** Vendor hardening note VHN-3-6; Prior assessment finding AF-3; Lab Operations Runbook ROB-1; Prior assessment finding AF-4

**Revision history.**
- 2022-06: editorial revision to AC-003; clarified scope and wording.
- 2023-03: editorial revision to AC-003; clarified scope and wording.


### AC-004 — Standard banner presentation

**Domain:** Access Control  **Severity:** Critical  **Applies to:** shared interactive hosts

**Rationale.** Consistent enforcement reduces the mean time to detect anomalous access across the estate. Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment. Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment.

**Requirement.** Changes should be staged in a non-production environment and validated against the verification procedure below. The host shall maintain the configuration described in this control at all times, and the setup auditor shall treat any deviation as reportable. Operational experience shows that small deviations here cascade into larger exposure during incident response.

**Implementation guidance.** Prefer explicit values over relying on compiled-in defaults, which may vary between distributions. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. Document any approved deviation in the exceptions register with a scheduled review date. Document any approved deviation in the exceptions register with a scheduled review date. Document any approved deviation in the exceptions register with a scheduled review date. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies.

**Verification.** Verification is performed by the setup auditor, which compares the host state to the normalized policy expectation. The verifier records the before and after state for inclusion in the assessment package. Evidence is the auditor's proposed patch set; a compliant host yields an empty set for this control. Verification is performed by the setup auditor, which compares the host state to the normalized policy expectation.

**References.** Vendor hardening note VHN-1-8; Vendor hardening note VHN-8-5; Baseline Configuration Guide BCG-6.8; Prior assessment finding AF-7

**Revision history.**
- 2024-02: editorial revision to AC-004; clarified scope and wording.
- 2023-01: editorial revision to AC-004; clarified scope and wording.
- 2025-01: editorial revision to AC-004; clarified scope and wording.
- 2022-11: editorial revision to AC-004; clarified scope and wording.


### AC-005 — Verified core dump handling

**Domain:** Access Control  **Severity:** Critical  **Applies to:** service-account-bearing hosts

**Rationale.** Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment. Consistent enforcement reduces the mean time to detect anomalous access across the estate. Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment.

**Requirement.** Prefer explicit values over relying on compiled-in defaults, which may vary between distributions. The host shall maintain the configuration described in this control at all times, and the setup auditor shall treat any deviation as reportable. Consistent enforcement reduces the mean time to detect anomalous access across the estate.

**Implementation guidance.** Retain the prior configuration so that a rollback can be performed without rebuilding the host. Coordinate with the accounts team before altering anything that affects service-account behavior. Retain the prior configuration so that a rollback can be performed without rebuilding the host. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. Prefer explicit values over relying on compiled-in defaults, which may vary between distributions. Operators should prefer configuration that is idempotent so that re-running the auditor produces no further changes. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. Changes should be staged in a non-production environment and validated against the verification procedure below.

**Verification.** The verifier records the before and after state for inclusion in the assessment package. Evidence is the auditor's proposed patch set; a compliant host yields an empty set for this control. Assessors may re-run the audit after applying patches to confirm the host has converged. The verifier records the before and after state for inclusion in the assessment package. Assessors may re-run the audit after applying patches to confirm the host has converged.

**References.** Baseline Configuration Guide BCG-8.8; Governing Security Policy GSP-2024 §4.2; Prior assessment finding AF-1; Baseline Configuration Guide BCG-6.0

**Revision history.**
- 2025-01: editorial revision to AC-005; clarified scope and wording.
- 2023-10: editorial revision to AC-005; clarified scope and wording.
- 2025-08: editorial revision to AC-005; clarified scope and wording.
- 2024-07: editorial revision to AC-005; clarified scope and wording.


### AC-006 — Standard credential rotation

**Domain:** Access Control  **Severity:** Low  **Applies to:** service-account-bearing hosts

**Rationale.** The control exists to keep remediation deterministic so that repeated audits converge on a stable state. This requirement aligns the gateway with the principle of least privilege mandated by the governing security policy. Adversaries routinely probe for misconfigurations of this control when establishing persistence on laboratory infrastructure. Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment.

**Requirement.** Changes should be staged in a non-production environment and validated against the verification procedure below. The host shall maintain the configuration described in this control at all times, and the setup auditor shall treat any deviation as reportable. Adversaries routinely probe for misconfigurations of this control when establishing persistence on laboratory infrastructure.

**Implementation guidance.** Coordinate with the accounts team before altering anything that affects service-account behavior. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. Document any approved deviation in the exceptions register with a scheduled review date. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. Changes should be staged in a non-production environment and validated against the verification procedure below. Retain the prior configuration so that a rollback can be performed without rebuilding the host. Coordinate with the accounts team before altering anything that affects service-account behavior. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner.

**Verification.** Verification is performed by the setup auditor, which compares the host state to the normalized policy expectation. Automated property checks generate varied host states to confirm the control behaves consistently. Assessors may re-run the audit after applying patches to confirm the host has converged. Assessors may re-run the audit after applying patches to confirm the host has converged.

**References.** Governing Security Policy GSP-2024 §2.4; Prior assessment finding AF-5

**Revision history.**
- 2024-05: editorial revision to AC-006; clarified scope and wording.
- 2025-05: editorial revision to AC-006; clarified scope and wording.
- 2025-03: editorial revision to AC-006; clarified scope and wording.
- 2024-08: editorial revision to AC-006; clarified scope and wording.


### AC-007 — Restricted console access

**Domain:** Access Control  **Severity:** Critical  **Applies to:** service-account-bearing hosts

**Rationale.** Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment. Operational experience shows that small deviations here cascade into larger exposure during incident response. Operational experience shows that small deviations here cascade into larger exposure during incident response. Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment.

**Requirement.** Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. The host shall maintain the configuration described in this control at all times, and the setup auditor shall treat any deviation as reportable. This requirement aligns the gateway with the principle of least privilege mandated by the governing security policy.

**Implementation guidance.** Document any approved deviation in the exceptions register with a scheduled review date. Operators should prefer configuration that is idempotent so that re-running the auditor produces no further changes. Operators should prefer configuration that is idempotent so that re-running the auditor produces no further changes. Retain the prior configuration so that a rollback can be performed without rebuilding the host. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. Coordinate with the accounts team before altering anything that affects service-account behavior.

**Verification.** Automated property checks generate varied host states to confirm the control behaves consistently. Automated property checks generate varied host states to confirm the control behaves consistently. Evidence is the auditor's proposed patch set; a compliant host yields an empty set for this control. Automated property checks generate varied host states to confirm the control behaves consistently. Assessors may re-run the audit after applying patches to confirm the host has converged.

**References.** Vendor hardening note VHN-7-6; Lab Operations Runbook ROB-6; Lab Operations Runbook ROB-5; Vendor hardening note VHN-4-5

**Revision history.**
- 2025-06: editorial revision to AC-007; clarified scope and wording.
- 2023-11: editorial revision to AC-007; clarified scope and wording.
- 2025-09: editorial revision to AC-007; clarified scope and wording.


### AC-008 — Controlled banner presentation

**Domain:** Access Control  **Severity:** Moderate  **Applies to:** service-account-bearing hosts

**Rationale.** Adversaries routinely probe for misconfigurations of this control when establishing persistence on laboratory infrastructure. Operational experience shows that small deviations here cascade into larger exposure during incident response. Adversaries routinely probe for misconfigurations of this control when establishing persistence on laboratory infrastructure. Operational experience shows that small deviations here cascade into larger exposure during incident response.

**Requirement.** Operators should prefer configuration that is idempotent so that re-running the auditor produces no further changes. The host shall maintain the configuration described in this control at all times, and the setup auditor shall treat any deviation as reportable. This requirement aligns the gateway with the principle of least privilege mandated by the governing security policy.

**Implementation guidance.** When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. Changes should be staged in a non-production environment and validated against the verification procedure below. Prefer explicit values over relying on compiled-in defaults, which may vary between distributions. Changes should be staged in a non-production environment and validated against the verification procedure below. Prefer explicit values over relying on compiled-in defaults, which may vary between distributions. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. Retain the prior configuration so that a rollback can be performed without rebuilding the host.

**Verification.** Automated property checks generate varied host states to confirm the control behaves consistently. Verification is performed by the setup auditor, which compares the host state to the normalized policy expectation. Assessors may re-run the audit after applying patches to confirm the host has converged.

**References.** Baseline Configuration Guide BCG-7.2; Prior assessment finding AF-1; Prior assessment finding AF-4; Lab Operations Runbook ROB-9

**Revision history.**
- 2022-06: editorial revision to AC-008; clarified scope and wording.
- 2023-06: editorial revision to AC-008; clarified scope and wording.


### AC-009 — Verified interface configuration

**Domain:** Access Control  **Severity:** Critical  **Applies to:** all managed hosts

**Rationale.** Inconsistent application of this requirement across hosts complicates evidence collection and weakens attestations. Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment. The control supports reproducible builds of the host baseline and simplifies forensic comparison.

**Requirement.** Coordinate with the accounts team before altering anything that affects service-account behavior. The host shall maintain the configuration described in this control at all times, and the setup auditor shall treat any deviation as reportable. The control exists to keep remediation deterministic so that repeated audits converge on a stable state.

**Implementation guidance.** Prefer explicit values over relying on compiled-in defaults, which may vary between distributions. Document any approved deviation in the exceptions register with a scheduled review date. Prefer explicit values over relying on compiled-in defaults, which may vary between distributions. Retain the prior configuration so that a rollback can be performed without rebuilding the host. Coordinate with the accounts team before altering anything that affects service-account behavior. Operators should prefer configuration that is idempotent so that re-running the auditor produces no further changes. Prefer explicit values over relying on compiled-in defaults, which may vary between distributions.

**Verification.** Verification is performed by the setup auditor, which compares the host state to the normalized policy expectation. Verification is performed by the setup auditor, which compares the host state to the normalized policy expectation. The verifier records the before and after state for inclusion in the assessment package.

**References.** Lab Operations Runbook ROB-3; Governing Security Policy GSP-2024 §3.8; Vendor hardening note VHN-6-4; Prior assessment finding AF-3

**Revision history.**
- 2024-08: editorial revision to AC-009; clarified scope and wording.
- 2025-09: editorial revision to AC-009; clarified scope and wording.
- 2024-12: editorial revision to AC-009; clarified scope and wording.


### AC-010 — Hardened module loading

**Domain:** Access Control  **Severity:** Low  **Applies to:** tier-1 laboratory hosts

**Rationale.** Inconsistent application of this requirement across hosts complicates evidence collection and weakens attestations. Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment. The control supports reproducible builds of the host baseline and simplifies forensic comparison. Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment. Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment.

**Requirement.** Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. The host shall maintain the configuration described in this control at all times, and the setup auditor shall treat any deviation as reportable. Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment.

**Implementation guidance.** Changes should be staged in a non-production environment and validated against the verification procedure below. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. Retain the prior configuration so that a rollback can be performed without rebuilding the host. Document any approved deviation in the exceptions register with a scheduled review date. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. Coordinate with the accounts team before altering anything that affects service-account behavior.

**Verification.** Assessors may re-run the audit after applying patches to confirm the host has converged. Automated property checks generate varied host states to confirm the control behaves consistently. Assessors may re-run the audit after applying patches to confirm the host has converged.

**References.** Baseline Configuration Guide BCG-1.4; Prior assessment finding AF-3; Lab Operations Runbook ROB-5

**Revision history.**
- 2024-10: editorial revision to AC-010; clarified scope and wording.
- 2024-04: editorial revision to AC-010; clarified scope and wording.


### AC-ACCT-SHELL — Non-interactive login shells

**Domain:** Access Control  **Severity:** Moderate  **Applies to:** all managed hosts

**Rationale.** Accounts assigned a non-interactive shell cannot be used for interactive logon and are therefore treated as disabled for access purposes.

**Requirement.** The following login shells shall be recognized as non-interactive (the **base set**):

- `/usr/sbin/nologin`
- `/sbin/nologin`
- `/bin/false`
- `/usr/bin/false`

An account whose login shell is any value in the recognized non-interactive set is disabled per AC-ACCT-LOCK. *(The recognized set is extended by Appendix G.)*

**Implementation guidance.** Compare the shell string exactly. Do not canonicalize symlinks; the literal value in `passwd` governs.

**Verification.** Covered jointly with AC-ACCT-LOCK.

**References.** Baseline Configuration Guide BCG-3.3; Vendor hardening note VHN-2-7

**Revision history.**
- 2023-02: initial publication.
- 2025-01: editorial alignment with AC-ACCT-LOCK.


### AC-011 — Verified umask default

**Domain:** Access Control  **Severity:** Moderate  **Applies to:** gateway and bastion hosts

**Rationale.** The control exists to keep remediation deterministic so that repeated audits converge on a stable state. Operational experience shows that small deviations here cascade into larger exposure during incident response. This requirement aligns the gateway with the principle of least privilege mandated by the governing security policy. Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment. Inconsistent application of this requirement across hosts complicates evidence collection and weakens attestations.

**Requirement.** Changes should be staged in a non-production environment and validated against the verification procedure below. The host shall maintain the configuration described in this control at all times, and the setup auditor shall treat any deviation as reportable. Operational experience shows that small deviations here cascade into larger exposure during incident response.

**Implementation guidance.** Prefer explicit values over relying on compiled-in defaults, which may vary between distributions. Coordinate with the accounts team before altering anything that affects service-account behavior. Retain the prior configuration so that a rollback can be performed without rebuilding the host. Changes should be staged in a non-production environment and validated against the verification procedure below. Document any approved deviation in the exceptions register with a scheduled review date. Document any approved deviation in the exceptions register with a scheduled review date. Changes should be staged in a non-production environment and validated against the verification procedure below. Coordinate with the accounts team before altering anything that affects service-account behavior.

**Verification.** Evidence is the auditor's proposed patch set; a compliant host yields an empty set for this control. Evidence is the auditor's proposed patch set; a compliant host yields an empty set for this control. Automated property checks generate varied host states to confirm the control behaves consistently.

**References.** Vendor hardening note VHN-2-5; Vendor hardening note VHN-3-8; Vendor hardening note VHN-6-3; Lab Operations Runbook ROB-5

**Revision history.**
- 2025-05: editorial revision to AC-011; clarified scope and wording.
- 2022-12: editorial revision to AC-011; clarified scope and wording.
- 2025-02: editorial revision to AC-011; clarified scope and wording.
- 2024-05: editorial revision to AC-011; clarified scope and wording.


### AC-GROUP-EFFECTIVE — Effective group membership

**Domain:** Access Control  **Severity:** High  **Applies to:** all managed hosts

**Rationale.** Privilege frequently flows through group membership. The auditor must compute membership the way the operating system resolves it, not merely from the textual member list.

**Requirement.** The **effective members** of a group shall be the union of:

1. the comma-separated members listed in the fourth field of the group's `group` entry; and
2. every account whose **primary** group id (the fourth field of its `passwd` entry) equals the group's group id.

Primary-group membership is authoritative even when the account does not appear in the group's textual member list. Failure to include primary-group members is a frequent source of missed privilege.

**Implementation guidance.** Resolve the group id from the third field of the `group` entry and scan all parsed accounts for a matching primary group id.

**Verification.** Exercised by sudo evaluation (AC-SUDO-NOPASSWD) over generated hosts.

**References.** Governing Security Policy GSP-2024 §4.2; Lab Operations Runbook ROB-5

**Revision history.**
- 2023-05: initial publication.
- 2024-09: emphasized primary-group authority after assessment finding AF-41.


### AC-SUDO-NOPASSWD — Passwordless sudo determination

**Domain:** Access Control  **Severity:** Critical  **Applies to:** gateway and bastion hosts

**Rationale.** Passwordless sudo on a gateway materially raises the blast radius of a single compromised credential. The auditor identifies principals that obtain passwordless sudo and proposes that a password be required.

**Requirement.** The `sudoers` content shall be parsed line by line, joining lines that end in a backslash and ignoring blank lines and lines whose first non-whitespace character is `#`.

- `User_Alias NAME = m1, m2, ...` declares an alias. Members may be users, `%group` references, other aliases, or any of these negated with a leading `!`. An alias resolves to the union of its positive members minus the union of its negated members, evaluated recursively.
- `Host_Alias`, `Runas_Alias`, `Cmnd_Alias`, and `Defaults` lines are not relevant to this control and are ignored.
- Every other line is a user specification: a single principal token, then whitespace, then the remainder of the rule. The principal is a user, a `%group`, an alias, or one of those negated with `!`. A principal of `ALL` is ignored.

A user specification **grants passwordless sudo** when the remainder of the rule contains the `NOPASSWD` tag. Processing specifications top to bottom, a grant adds its resolved principal to the passwordless set and a grant with a negated principal removes its resolved principal. Negations shall be honored. *(Appendix G narrows which grants qualify as passwordless.)*

**Implementation guidance.** Resolve `%group` principals through AC-GROUP-EFFECTIVE. Resolve aliases recursively, guarding against self-reference.

**Verification.** The auditor proposes `sudoers.require_password` for each qualifying principal that is neither disabled nor exempt (AC-EXEMPT).

**References.** Governing Security Policy GSP-2024 §4.4; Prior assessment finding AF-58

**Revision history.**
- 2023-07: initial publication.
- 2024-03: added explicit negation handling after AF-58.


### AC-KEY-REVOKE — Revocation of keys for disabled accounts

**Domain:** Access Control  **Severity:** High  **Applies to:** all managed hosts

**Rationale.** A disabled account that retains authorized keys remains a usable entry point and must be remediated.

**Requirement.** An account is deemed to **possess keys** when its `authorized_keys` content contains at least one line that is neither blank nor a comment (a line whose first non-whitespace character is `#`). For every account that possesses keys and is disabled per AC-ACCT-LOCK, the auditor shall propose `ssh.revoke_keys` for that account.

**Implementation guidance.** Whitespace-only lines and comment lines do not constitute possession of keys.

**Verification.** A compliant host has no disabled account that possesses keys.

**References.** Baseline Configuration Guide BCG-4.1

**Revision history.**
- 2023-04: initial publication.


### AC-EXEMPT — Service-account exemptions

**Domain:** Access Control  **Severity:** Moderate  **Applies to:** service-account-bearing hosts

**Rationale.** A small number of managed service accounts are governed by a separate lifecycle and are exempt from the passwordless-sudo remediation so that automation is not disrupted.

**Requirement.** An account shall be treated as **exempt** from AC-SUDO-NOPASSWD remediation when either:

1. its user name appears in the exempt-account roster, which in the body of this Standard contains the single entry `svc_monitor`; or
2. its user id is less than or equal to the **service-account user-id ceiling**, which in the body of this Standard is `999`.

Exempt accounts are never the target of a `sudoers.require_password` patch. *(Both the roster and the ceiling are amended in Appendix G.)*

**Implementation guidance.** The user id is the third field of the `passwd` entry. The ceiling comparison is inclusive.

**Verification.** The auditor must not propose a password requirement for any exempt account, even where that account holds passwordless sudo.

**References.** Governing Security Policy GSP-2024 §4.5; Lab Operations Runbook ROB-8

**Revision history.**
- 2023-08: initial publication with ceiling 999 and roster {svc_monitor}.


## 4. Audit and Accountability

Consistent enforcement reduces the mean time to detect anomalous access across the estate. Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment. Consistent enforcement reduces the mean time to detect anomalous access across the estate. Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment.


When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. Changes should be staged in a non-production environment and validated against the verification procedure below. Prefer explicit values over relying on compiled-in defaults, which may vary between distributions. Coordinate with the accounts team before altering anything that affects service-account behavior.


### AU-001 — Hardened package provenance

**Domain:** Audit and Accountability  **Severity:** High  **Applies to:** gateway and bastion hosts

**Rationale.** Adversaries routinely probe for misconfigurations of this control when establishing persistence on laboratory infrastructure. Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment. Adversaries routinely probe for misconfigurations of this control when establishing persistence on laboratory infrastructure.

**Requirement.** Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. The host shall maintain the configuration described in this control at all times, and the setup auditor shall treat any deviation as reportable. Adversaries routinely probe for misconfigurations of this control when establishing persistence on laboratory infrastructure.

**Implementation guidance.** When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. Changes should be staged in a non-production environment and validated against the verification procedure below. Changes should be staged in a non-production environment and validated against the verification procedure below. Prefer explicit values over relying on compiled-in defaults, which may vary between distributions. Coordinate with the accounts team before altering anything that affects service-account behavior. Document any approved deviation in the exceptions register with a scheduled review date.

**Verification.** Verification is performed by the setup auditor, which compares the host state to the normalized policy expectation. Evidence is the auditor's proposed patch set; a compliant host yields an empty set for this control. The verifier records the before and after state for inclusion in the assessment package. Assessors may re-run the audit after applying patches to confirm the host has converged. Verification is performed by the setup auditor, which compares the host state to the normalized policy expectation.

**References.** Governing Security Policy GSP-2024 §3.9; Governing Security Policy GSP-2024 §5.6; Prior assessment finding AF-3; Vendor hardening note VHN-2-4

**Revision history.**
- 2022-11: editorial revision to AU-001; clarified scope and wording.
- 2025-11: editorial revision to AU-001; clarified scope and wording.
- 2024-12: editorial revision to AU-001; clarified scope and wording.
- 2023-08: editorial revision to AU-001; clarified scope and wording.


### AU-002 — Standard package provenance

**Domain:** Audit and Accountability  **Severity:** High  **Applies to:** all managed hosts

**Rationale.** This requirement aligns the gateway with the principle of least privilege mandated by the governing security policy. Adversaries routinely probe for misconfigurations of this control when establishing persistence on laboratory infrastructure. The control supports reproducible builds of the host baseline and simplifies forensic comparison. The control exists to keep remediation deterministic so that repeated audits converge on a stable state.

**Requirement.** Prefer explicit values over relying on compiled-in defaults, which may vary between distributions. The host shall maintain the configuration described in this control at all times, and the setup auditor shall treat any deviation as reportable. Inconsistent application of this requirement across hosts complicates evidence collection and weakens attestations.

**Implementation guidance.** Changes should be staged in a non-production environment and validated against the verification procedure below. Changes should be staged in a non-production environment and validated against the verification procedure below. Retain the prior configuration so that a rollback can be performed without rebuilding the host. Changes should be staged in a non-production environment and validated against the verification procedure below. Changes should be staged in a non-production environment and validated against the verification procedure below. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. Prefer explicit values over relying on compiled-in defaults, which may vary between distributions.

**Verification.** Automated property checks generate varied host states to confirm the control behaves consistently. Automated property checks generate varied host states to confirm the control behaves consistently. The verifier records the before and after state for inclusion in the assessment package.

**References.** Governing Security Policy GSP-2024 §5.0; Baseline Configuration Guide BCG-2.9

**Revision history.**
- 2022-04: editorial revision to AU-002; clarified scope and wording.
- 2024-12: editorial revision to AU-002; clarified scope and wording.


### AU-LEDGER — Audit ledger schema and durability

**Domain:** Audit and Accountability  **Severity:** High  **Applies to:** all managed hosts

**Rationale.** The auditor keeps a persistent ledger of the patches it proposes so that operators have a durable record of remediation across runs. A ledger that silently stops recording is itself a reportable failure.

**Requirement.** The auditor shall maintain a persistent JSON ledger. The **current ledger schema is version 2**: the ledger is a JSON object carrying a `schema` field whose value is the integer `2`, and an `entries` field whose value is a JSON array. Each element of `entries` is one proposed patch object, in the same shape the auditor returns from an audit. For every audited request, the auditor shall append each patch it emits to the `entries` array and persist the result.

The on-disk ledger that ships with the host predates the current schema: it is in the **legacy schema 1** layout, a JSON object whose `schema` is `1` (or absent) and whose records are stored under an `audits` array rather than `entries`. The auditor shall **migrate the legacy ledger forward** to schema 2 — moving every existing record from `audits` into `entries` unchanged and setting `schema` to `2` — and then append new patches. Migration shall **preserve every pre-existing record**; a reconciliation that discards history, or that downgrades the in-code schema to keep writing under `audits`, is non-compliant.

**Implementation guidance.** Ledger writes shall be durable: a write that fails is a defect to be fixed, not silently swallowed. The legacy file on disk is authoritative only as to the *records it already holds*, not as to the schema the auditor must write.

**Verification.** After an audit, the ledger is a schema-2 object whose `entries` array contains the pre-existing legacy records plus every patch emitted by the audit.

**References.** Governing Security Policy GSP-2024 §3.4; Prior assessment finding AF-22

**Revision history.**
- 2023-06: initial publication (schema 1).
- 2025-10: schema 2 introduced; records moved from `audits` to `entries`.


### AU-003 — Approved boot integrity

**Domain:** Audit and Accountability  **Severity:** Moderate  **Applies to:** gateway and bastion hosts

**Rationale.** Consistent enforcement reduces the mean time to detect anomalous access across the estate. The control exists to keep remediation deterministic so that repeated audits converge on a stable state. The control exists to keep remediation deterministic so that repeated audits converge on a stable state.

**Requirement.** Changes should be staged in a non-production environment and validated against the verification procedure below. The host shall maintain the configuration described in this control at all times, and the setup auditor shall treat any deviation as reportable. Consistent enforcement reduces the mean time to detect anomalous access across the estate.

**Implementation guidance.** Changes should be staged in a non-production environment and validated against the verification procedure below. Coordinate with the accounts team before altering anything that affects service-account behavior. Prefer explicit values over relying on compiled-in defaults, which may vary between distributions. Retain the prior configuration so that a rollback can be performed without rebuilding the host. Operators should prefer configuration that is idempotent so that re-running the auditor produces no further changes. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. Retain the prior configuration so that a rollback can be performed without rebuilding the host. Document any approved deviation in the exceptions register with a scheduled review date.

**Verification.** Evidence is the auditor's proposed patch set; a compliant host yields an empty set for this control. Evidence is the auditor's proposed patch set; a compliant host yields an empty set for this control. Verification is performed by the setup auditor, which compares the host state to the normalized policy expectation. The verifier records the before and after state for inclusion in the assessment package. Verification is performed by the setup auditor, which compares the host state to the normalized policy expectation.

**References.** Vendor hardening note VHN-1-2; Governing Security Policy GSP-2024 §5.6; Governing Security Policy GSP-2024 §7.3

**Revision history.**
- 2024-03: editorial revision to AU-003; clarified scope and wording.
- 2024-02: editorial revision to AU-003; clarified scope and wording.


### AU-004 — Hardened credential rotation

**Domain:** Audit and Accountability  **Severity:** Critical  **Applies to:** tier-1 laboratory hosts

**Rationale.** This requirement aligns the gateway with the principle of least privilege mandated by the governing security policy. Inconsistent application of this requirement across hosts complicates evidence collection and weakens attestations. The control exists to keep remediation deterministic so that repeated audits converge on a stable state. Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment. Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment.

**Requirement.** Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. The host shall maintain the configuration described in this control at all times, and the setup auditor shall treat any deviation as reportable. Consistent enforcement reduces the mean time to detect anomalous access across the estate.

**Implementation guidance.** Changes should be staged in a non-production environment and validated against the verification procedure below. Coordinate with the accounts team before altering anything that affects service-account behavior. Document any approved deviation in the exceptions register with a scheduled review date. Coordinate with the accounts team before altering anything that affects service-account behavior. Changes should be staged in a non-production environment and validated against the verification procedure below. Retain the prior configuration so that a rollback can be performed without rebuilding the host. Changes should be staged in a non-production environment and validated against the verification procedure below. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies.

**Verification.** Assessors may re-run the audit after applying patches to confirm the host has converged. Verification is performed by the setup auditor, which compares the host state to the normalized policy expectation. Verification is performed by the setup auditor, which compares the host state to the normalized policy expectation.

**References.** Vendor hardening note VHN-9-7; Vendor hardening note VHN-3-1; Governing Security Policy GSP-2024 §8.8; Lab Operations Runbook ROB-4

**Revision history.**
- 2022-07: editorial revision to AU-004; clarified scope and wording.
- 2025-06: editorial revision to AU-004; clarified scope and wording.
- 2024-02: editorial revision to AU-004; clarified scope and wording.


### AU-005 — Verified log forwarding

**Domain:** Audit and Accountability  **Severity:** Critical  **Applies to:** all managed hosts

**Rationale.** Consistent enforcement reduces the mean time to detect anomalous access across the estate. Adversaries routinely probe for misconfigurations of this control when establishing persistence on laboratory infrastructure. The control supports reproducible builds of the host baseline and simplifies forensic comparison. The control exists to keep remediation deterministic so that repeated audits converge on a stable state.

**Requirement.** Retain the prior configuration so that a rollback can be performed without rebuilding the host. The host shall maintain the configuration described in this control at all times, and the setup auditor shall treat any deviation as reportable. The control exists to keep remediation deterministic so that repeated audits converge on a stable state.

**Implementation guidance.** Coordinate with the accounts team before altering anything that affects service-account behavior. Document any approved deviation in the exceptions register with a scheduled review date. Prefer explicit values over relying on compiled-in defaults, which may vary between distributions. Document any approved deviation in the exceptions register with a scheduled review date. Retain the prior configuration so that a rollback can be performed without rebuilding the host.

**Verification.** Verification is performed by the setup auditor, which compares the host state to the normalized policy expectation. Verification is performed by the setup auditor, which compares the host state to the normalized policy expectation. Evidence is the auditor's proposed patch set; a compliant host yields an empty set for this control. Assessors may re-run the audit after applying patches to confirm the host has converged.

**References.** Prior assessment finding AF-5; Lab Operations Runbook ROB-6

**Revision history.**
- 2022-05: editorial revision to AU-005; clarified scope and wording.
- 2025-09: editorial revision to AU-005; clarified scope and wording.


### AU-006 — Centralized console access

**Domain:** Audit and Accountability  **Severity:** Low  **Applies to:** gateway and bastion hosts

**Rationale.** Consistent enforcement reduces the mean time to detect anomalous access across the estate. Inconsistent application of this requirement across hosts complicates evidence collection and weakens attestations. Inconsistent application of this requirement across hosts complicates evidence collection and weakens attestations.

**Requirement.** Coordinate with the accounts team before altering anything that affects service-account behavior. The host shall maintain the configuration described in this control at all times, and the setup auditor shall treat any deviation as reportable. The control exists to keep remediation deterministic so that repeated audits converge on a stable state.

**Implementation guidance.** When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. Coordinate with the accounts team before altering anything that affects service-account behavior. Prefer explicit values over relying on compiled-in defaults, which may vary between distributions. Coordinate with the accounts team before altering anything that affects service-account behavior. Coordinate with the accounts team before altering anything that affects service-account behavior. Retain the prior configuration so that a rollback can be performed without rebuilding the host.

**Verification.** Automated property checks generate varied host states to confirm the control behaves consistently. Verification is performed by the setup auditor, which compares the host state to the normalized policy expectation. Assessors may re-run the audit after applying patches to confirm the host has converged.

**References.** Lab Operations Runbook ROB-2; Governing Security Policy GSP-2024 §9.0

**Revision history.**
- 2022-01: editorial revision to AU-006; clarified scope and wording.
- 2022-04: editorial revision to AU-006; clarified scope and wording.


### AU-007 — Controlled umask default

**Domain:** Audit and Accountability  **Severity:** Critical  **Applies to:** shared interactive hosts

**Rationale.** Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment. Adversaries routinely probe for misconfigurations of this control when establishing persistence on laboratory infrastructure. Consistent enforcement reduces the mean time to detect anomalous access across the estate.

**Requirement.** Changes should be staged in a non-production environment and validated against the verification procedure below. The host shall maintain the configuration described in this control at all times, and the setup auditor shall treat any deviation as reportable. Operational experience shows that small deviations here cascade into larger exposure during incident response.

**Implementation guidance.** Prefer explicit values over relying on compiled-in defaults, which may vary between distributions. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. Coordinate with the accounts team before altering anything that affects service-account behavior. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. Retain the prior configuration so that a rollback can be performed without rebuilding the host. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. Changes should be staged in a non-production environment and validated against the verification procedure below. Coordinate with the accounts team before altering anything that affects service-account behavior.

**Verification.** Verification is performed by the setup auditor, which compares the host state to the normalized policy expectation. The verifier records the before and after state for inclusion in the assessment package. The verifier records the before and after state for inclusion in the assessment package.

**References.** Baseline Configuration Guide BCG-3.7; Governing Security Policy GSP-2024 §5.3

**Revision history.**
- 2025-04: editorial revision to AU-007; clarified scope and wording.
- 2025-02: editorial revision to AU-007; clarified scope and wording.
- 2024-03: editorial revision to AU-007; clarified scope and wording.
- 2025-10: editorial revision to AU-007; clarified scope and wording.


### AU-008 — Verified package provenance

**Domain:** Audit and Accountability  **Severity:** Critical  **Applies to:** all managed hosts

**Rationale.** Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment. Adversaries routinely probe for misconfigurations of this control when establishing persistence on laboratory infrastructure. Consistent enforcement reduces the mean time to detect anomalous access across the estate.

**Requirement.** Document any approved deviation in the exceptions register with a scheduled review date. The host shall maintain the configuration described in this control at all times, and the setup auditor shall treat any deviation as reportable. Operational experience shows that small deviations here cascade into larger exposure during incident response.

**Implementation guidance.** When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. Changes should be staged in a non-production environment and validated against the verification procedure below. Operators should prefer configuration that is idempotent so that re-running the auditor produces no further changes. Changes should be staged in a non-production environment and validated against the verification procedure below.

**Verification.** Evidence is the auditor's proposed patch set; a compliant host yields an empty set for this control. Automated property checks generate varied host states to confirm the control behaves consistently. Assessors may re-run the audit after applying patches to confirm the host has converged. The verifier records the before and after state for inclusion in the assessment package. Verification is performed by the setup auditor, which compares the host state to the normalized policy expectation.

**References.** Governing Security Policy GSP-2024 §3.3; Vendor hardening note VHN-8-6; Prior assessment finding AF-4

**Revision history.**
- 2022-05: editorial revision to AU-008; clarified scope and wording.
- 2025-06: editorial revision to AU-008; clarified scope and wording.


### AU-009 — Controlled boot integrity

**Domain:** Audit and Accountability  **Severity:** High  **Applies to:** tier-1 laboratory hosts

**Rationale.** Inconsistent application of this requirement across hosts complicates evidence collection and weakens attestations. Inconsistent application of this requirement across hosts complicates evidence collection and weakens attestations. Consistent enforcement reduces the mean time to detect anomalous access across the estate. The control exists to keep remediation deterministic so that repeated audits converge on a stable state.

**Requirement.** Changes should be staged in a non-production environment and validated against the verification procedure below. The host shall maintain the configuration described in this control at all times, and the setup auditor shall treat any deviation as reportable. The control supports reproducible builds of the host baseline and simplifies forensic comparison.

**Implementation guidance.** Changes should be staged in a non-production environment and validated against the verification procedure below. Operators should prefer configuration that is idempotent so that re-running the auditor produces no further changes. Coordinate with the accounts team before altering anything that affects service-account behavior. Changes should be staged in a non-production environment and validated against the verification procedure below. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. Document any approved deviation in the exceptions register with a scheduled review date. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner.

**Verification.** Automated property checks generate varied host states to confirm the control behaves consistently. Automated property checks generate varied host states to confirm the control behaves consistently. Evidence is the auditor's proposed patch set; a compliant host yields an empty set for this control. The verifier records the before and after state for inclusion in the assessment package. Verification is performed by the setup auditor, which compares the host state to the normalized policy expectation.

**References.** Lab Operations Runbook ROB-7; Prior assessment finding AF-3; Vendor hardening note VHN-8-6; Vendor hardening note VHN-4-5

**Revision history.**
- 2023-01: editorial revision to AU-009; clarified scope and wording.
- 2022-04: editorial revision to AU-009; clarified scope and wording.
- 2024-04: editorial revision to AU-009; clarified scope and wording.
- 2024-01: editorial revision to AU-009; clarified scope and wording.


### AU-010 — Mandatory package provenance

**Domain:** Audit and Accountability  **Severity:** High  **Applies to:** service-account-bearing hosts

**Rationale.** Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment. Inconsistent application of this requirement across hosts complicates evidence collection and weakens attestations. Inconsistent application of this requirement across hosts complicates evidence collection and weakens attestations.

**Requirement.** Document any approved deviation in the exceptions register with a scheduled review date. The host shall maintain the configuration described in this control at all times, and the setup auditor shall treat any deviation as reportable. Operational experience shows that small deviations here cascade into larger exposure during incident response.

**Implementation guidance.** Operators should prefer configuration that is idempotent so that re-running the auditor produces no further changes. Retain the prior configuration so that a rollback can be performed without rebuilding the host. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. Changes should be staged in a non-production environment and validated against the verification procedure below. Operators should prefer configuration that is idempotent so that re-running the auditor produces no further changes.

**Verification.** The verifier records the before and after state for inclusion in the assessment package. Evidence is the auditor's proposed patch set; a compliant host yields an empty set for this control. The verifier records the before and after state for inclusion in the assessment package.

**References.** Governing Security Policy GSP-2024 §2.2; Governing Security Policy GSP-2024 §5.0; Governing Security Policy GSP-2024 §4.4

**Revision history.**
- 2023-02: editorial revision to AU-010; clarified scope and wording.
- 2023-12: editorial revision to AU-010; clarified scope and wording.
- 2023-10: editorial revision to AU-010; clarified scope and wording.
- 2025-04: editorial revision to AU-010; clarified scope and wording.


### AU-011 — Controlled console access

**Domain:** Audit and Accountability  **Severity:** Critical  **Applies to:** service-account-bearing hosts

**Rationale.** Operational experience shows that small deviations here cascade into larger exposure during incident response. Inconsistent application of this requirement across hosts complicates evidence collection and weakens attestations. Consistent enforcement reduces the mean time to detect anomalous access across the estate. The control exists to keep remediation deterministic so that repeated audits converge on a stable state.

**Requirement.** Prefer explicit values over relying on compiled-in defaults, which may vary between distributions. The host shall maintain the configuration described in this control at all times, and the setup auditor shall treat any deviation as reportable. Inconsistent application of this requirement across hosts complicates evidence collection and weakens attestations.

**Implementation guidance.** Document any approved deviation in the exceptions register with a scheduled review date. Prefer explicit values over relying on compiled-in defaults, which may vary between distributions. Operators should prefer configuration that is idempotent so that re-running the auditor produces no further changes. Prefer explicit values over relying on compiled-in defaults, which may vary between distributions. Changes should be staged in a non-production environment and validated against the verification procedure below.

**Verification.** Automated property checks generate varied host states to confirm the control behaves consistently. Verification is performed by the setup auditor, which compares the host state to the normalized policy expectation. Automated property checks generate varied host states to confirm the control behaves consistently. Evidence is the auditor's proposed patch set; a compliant host yields an empty set for this control. Assessors may re-run the audit after applying patches to confirm the host has converged.

**References.** Vendor hardening note VHN-9-1; Baseline Configuration Guide BCG-2.3; Prior assessment finding AF-5

**Revision history.**
- 2022-10: editorial revision to AU-011; clarified scope and wording.
- 2023-11: editorial revision to AU-011; clarified scope and wording.
- 2025-07: editorial revision to AU-011; clarified scope and wording.
- 2023-11: editorial revision to AU-011; clarified scope and wording.


### AU-012 — Controlled session timeout

**Domain:** Audit and Accountability  **Severity:** Moderate  **Applies to:** all managed hosts

**Rationale.** Inconsistent application of this requirement across hosts complicates evidence collection and weakens attestations. The control supports reproducible builds of the host baseline and simplifies forensic comparison. This requirement aligns the gateway with the principle of least privilege mandated by the governing security policy. This requirement aligns the gateway with the principle of least privilege mandated by the governing security policy.

**Requirement.** When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. The host shall maintain the configuration described in this control at all times, and the setup auditor shall treat any deviation as reportable. The control supports reproducible builds of the host baseline and simplifies forensic comparison.

**Implementation guidance.** Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. Document any approved deviation in the exceptions register with a scheduled review date. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. Operators should prefer configuration that is idempotent so that re-running the auditor produces no further changes. Operators should prefer configuration that is idempotent so that re-running the auditor produces no further changes. Operators should prefer configuration that is idempotent so that re-running the auditor produces no further changes.

**Verification.** Verification is performed by the setup auditor, which compares the host state to the normalized policy expectation. The verifier records the before and after state for inclusion in the assessment package. The verifier records the before and after state for inclusion in the assessment package. Assessors may re-run the audit after applying patches to confirm the host has converged.

**References.** Vendor hardening note VHN-3-4; Lab Operations Runbook ROB-8; Governing Security Policy GSP-2024 §8.1

**Revision history.**
- 2022-08: editorial revision to AU-012; clarified scope and wording.
- 2025-08: editorial revision to AU-012; clarified scope and wording.
- 2023-04: editorial revision to AU-012; clarified scope and wording.
- 2025-06: editorial revision to AU-012; clarified scope and wording.


### AU-013 — Centralized banner presentation

**Domain:** Audit and Accountability  **Severity:** Critical  **Applies to:** gateway and bastion hosts

**Rationale.** The control exists to keep remediation deterministic so that repeated audits converge on a stable state. Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment. The control supports reproducible builds of the host baseline and simplifies forensic comparison.

**Requirement.** Coordinate with the accounts team before altering anything that affects service-account behavior. The host shall maintain the configuration described in this control at all times, and the setup auditor shall treat any deviation as reportable. Operational experience shows that small deviations here cascade into larger exposure during incident response.

**Implementation guidance.** Changes should be staged in a non-production environment and validated against the verification procedure below. Retain the prior configuration so that a rollback can be performed without rebuilding the host. Coordinate with the accounts team before altering anything that affects service-account behavior. Retain the prior configuration so that a rollback can be performed without rebuilding the host. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner.

**Verification.** Evidence is the auditor's proposed patch set; a compliant host yields an empty set for this control. Assessors may re-run the audit after applying patches to confirm the host has converged. Evidence is the auditor's proposed patch set; a compliant host yields an empty set for this control.

**References.** Prior assessment finding AF-5; Governing Security Policy GSP-2024 §3.0

**Revision history.**
- 2022-10: editorial revision to AU-013; clarified scope and wording.
- 2024-10: editorial revision to AU-013; clarified scope and wording.
- 2022-06: editorial revision to AU-013; clarified scope and wording.
- 2024-03: editorial revision to AU-013; clarified scope and wording.


## 5. Configuration Management

The control supports reproducible builds of the host baseline and simplifies forensic comparison. Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment. This requirement aligns the gateway with the principle of least privilege mandated by the governing security policy. This requirement aligns the gateway with the principle of least privilege mandated by the governing security policy. Inconsistent application of this requirement across hosts complicates evidence collection and weakens attestations. This requirement aligns the gateway with the principle of least privilege mandated by the governing security policy.


Coordinate with the accounts team before altering anything that affects service-account behavior. Prefer explicit values over relying on compiled-in defaults, which may vary between distributions. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. Prefer explicit values over relying on compiled-in defaults, which may vary between distributions. Operators should prefer configuration that is idempotent so that re-running the auditor produces no further changes. Changes should be staged in a non-production environment and validated against the verification procedure below.


### CM-001 — Baseline umask default

**Domain:** Configuration Management  **Severity:** Moderate  **Applies to:** gateway and bastion hosts

**Rationale.** This requirement aligns the gateway with the principle of least privilege mandated by the governing security policy. The control exists to keep remediation deterministic so that repeated audits converge on a stable state. Operational experience shows that small deviations here cascade into larger exposure during incident response. Adversaries routinely probe for misconfigurations of this control when establishing persistence on laboratory infrastructure.

**Requirement.** Operators should prefer configuration that is idempotent so that re-running the auditor produces no further changes. The host shall maintain the configuration described in this control at all times, and the setup auditor shall treat any deviation as reportable. The control supports reproducible builds of the host baseline and simplifies forensic comparison.

**Implementation guidance.** Changes should be staged in a non-production environment and validated against the verification procedure below. Document any approved deviation in the exceptions register with a scheduled review date. Prefer explicit values over relying on compiled-in defaults, which may vary between distributions. Retain the prior configuration so that a rollback can be performed without rebuilding the host. Operators should prefer configuration that is idempotent so that re-running the auditor produces no further changes.

**Verification.** Verification is performed by the setup auditor, which compares the host state to the normalized policy expectation. Automated property checks generate varied host states to confirm the control behaves consistently. Evidence is the auditor's proposed patch set; a compliant host yields an empty set for this control.

**References.** Prior assessment finding AF-3; Vendor hardening note VHN-7-4; Vendor hardening note VHN-6-4

**Revision history.**
- 2023-08: editorial revision to CM-001; clarified scope and wording.
- 2025-11: editorial revision to CM-001; clarified scope and wording.
- 2025-09: editorial revision to CM-001; clarified scope and wording.
- 2023-02: editorial revision to CM-001; clarified scope and wording.


### CM-002 — Centralized filesystem mount option

**Domain:** Configuration Management  **Severity:** High  **Applies to:** tier-1 laboratory hosts

**Rationale.** Operational experience shows that small deviations here cascade into larger exposure during incident response. Consistent enforcement reduces the mean time to detect anomalous access across the estate. Consistent enforcement reduces the mean time to detect anomalous access across the estate. Consistent enforcement reduces the mean time to detect anomalous access across the estate.

**Requirement.** When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. The host shall maintain the configuration described in this control at all times, and the setup auditor shall treat any deviation as reportable. The control supports reproducible builds of the host baseline and simplifies forensic comparison.

**Implementation guidance.** Changes should be staged in a non-production environment and validated against the verification procedure below. Retain the prior configuration so that a rollback can be performed without rebuilding the host. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner.

**Verification.** Assessors may re-run the audit after applying patches to confirm the host has converged. Evidence is the auditor's proposed patch set; a compliant host yields an empty set for this control. Assessors may re-run the audit after applying patches to confirm the host has converged.

**References.** Vendor hardening note VHN-1-7; Governing Security Policy GSP-2024 §7.6; Baseline Configuration Guide BCG-7.5; Lab Operations Runbook ROB-1

**Revision history.**
- 2022-12: editorial revision to CM-002; clarified scope and wording.
- 2022-11: editorial revision to CM-002; clarified scope and wording.
- 2025-06: editorial revision to CM-002; clarified scope and wording.


### CM-003 — Mandatory service enablement

**Domain:** Configuration Management  **Severity:** High  **Applies to:** tier-1 laboratory hosts

**Rationale.** Adversaries routinely probe for misconfigurations of this control when establishing persistence on laboratory infrastructure. This requirement aligns the gateway with the principle of least privilege mandated by the governing security policy. The control exists to keep remediation deterministic so that repeated audits converge on a stable state.

**Requirement.** Coordinate with the accounts team before altering anything that affects service-account behavior. The host shall maintain the configuration described in this control at all times, and the setup auditor shall treat any deviation as reportable. Consistent enforcement reduces the mean time to detect anomalous access across the estate.

**Implementation guidance.** When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. Prefer explicit values over relying on compiled-in defaults, which may vary between distributions. Changes should be staged in a non-production environment and validated against the verification procedure below. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. Prefer explicit values over relying on compiled-in defaults, which may vary between distributions. Retain the prior configuration so that a rollback can be performed without rebuilding the host. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. Coordinate with the accounts team before altering anything that affects service-account behavior.

**Verification.** The verifier records the before and after state for inclusion in the assessment package. Verification is performed by the setup auditor, which compares the host state to the normalized policy expectation. Automated property checks generate varied host states to confirm the control behaves consistently. Verification is performed by the setup auditor, which compares the host state to the normalized policy expectation. Automated property checks generate varied host states to confirm the control behaves consistently.

**References.** Prior assessment finding AF-8; Baseline Configuration Guide BCG-2.0; Baseline Configuration Guide BCG-8.2

**Revision history.**
- 2022-02: editorial revision to CM-003; clarified scope and wording.
- 2022-03: editorial revision to CM-003; clarified scope and wording.
- 2023-02: editorial revision to CM-003; clarified scope and wording.
- 2025-10: editorial revision to CM-003; clarified scope and wording.


### CM-004 — Controlled session timeout

**Domain:** Configuration Management  **Severity:** Low  **Applies to:** service-account-bearing hosts

**Rationale.** The control exists to keep remediation deterministic so that repeated audits converge on a stable state. The control supports reproducible builds of the host baseline and simplifies forensic comparison. The control supports reproducible builds of the host baseline and simplifies forensic comparison. The control exists to keep remediation deterministic so that repeated audits converge on a stable state. Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment.

**Requirement.** Prefer explicit values over relying on compiled-in defaults, which may vary between distributions. The host shall maintain the configuration described in this control at all times, and the setup auditor shall treat any deviation as reportable. This requirement aligns the gateway with the principle of least privilege mandated by the governing security policy.

**Implementation guidance.** Document any approved deviation in the exceptions register with a scheduled review date. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. Operators should prefer configuration that is idempotent so that re-running the auditor produces no further changes. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. Prefer explicit values over relying on compiled-in defaults, which may vary between distributions. Coordinate with the accounts team before altering anything that affects service-account behavior.

**Verification.** Evidence is the auditor's proposed patch set; a compliant host yields an empty set for this control. Automated property checks generate varied host states to confirm the control behaves consistently. Evidence is the auditor's proposed patch set; a compliant host yields an empty set for this control. The verifier records the before and after state for inclusion in the assessment package. Verification is performed by the setup auditor, which compares the host state to the normalized policy expectation.

**References.** Vendor hardening note VHN-8-3; Vendor hardening note VHN-4-1

**Revision history.**
- 2024-03: editorial revision to CM-004; clarified scope and wording.
- 2023-02: editorial revision to CM-004; clarified scope and wording.
- 2025-04: editorial revision to CM-004; clarified scope and wording.


### CM-005 — Hardened filesystem mount option

**Domain:** Configuration Management  **Severity:** Moderate  **Applies to:** service-account-bearing hosts

**Rationale.** The control exists to keep remediation deterministic so that repeated audits converge on a stable state. The control exists to keep remediation deterministic so that repeated audits converge on a stable state. Inconsistent application of this requirement across hosts complicates evidence collection and weakens attestations. Consistent enforcement reduces the mean time to detect anomalous access across the estate.

**Requirement.** Coordinate with the accounts team before altering anything that affects service-account behavior. The host shall maintain the configuration described in this control at all times, and the setup auditor shall treat any deviation as reportable. Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment.

**Implementation guidance.** Operators should prefer configuration that is idempotent so that re-running the auditor produces no further changes. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. Retain the prior configuration so that a rollback can be performed without rebuilding the host. Changes should be staged in a non-production environment and validated against the verification procedure below. Retain the prior configuration so that a rollback can be performed without rebuilding the host. Retain the prior configuration so that a rollback can be performed without rebuilding the host.

**Verification.** Evidence is the auditor's proposed patch set; a compliant host yields an empty set for this control. The verifier records the before and after state for inclusion in the assessment package. Verification is performed by the setup auditor, which compares the host state to the normalized policy expectation. Assessors may re-run the audit after applying patches to confirm the host has converged.

**References.** Prior assessment finding AF-9; Vendor hardening note VHN-9-8; Governing Security Policy GSP-2024 §8.0

**Revision history.**
- 2022-04: editorial revision to CM-005; clarified scope and wording.
- 2024-02: editorial revision to CM-005; clarified scope and wording.


### CM-006 — Restricted module loading

**Domain:** Configuration Management  **Severity:** Low  **Applies to:** service-account-bearing hosts

**Rationale.** Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment. The control supports reproducible builds of the host baseline and simplifies forensic comparison. Consistent enforcement reduces the mean time to detect anomalous access across the estate.

**Requirement.** Retain the prior configuration so that a rollback can be performed without rebuilding the host. The host shall maintain the configuration described in this control at all times, and the setup auditor shall treat any deviation as reportable. This requirement aligns the gateway with the principle of least privilege mandated by the governing security policy.

**Implementation guidance.** Prefer explicit values over relying on compiled-in defaults, which may vary between distributions. Retain the prior configuration so that a rollback can be performed without rebuilding the host. Document any approved deviation in the exceptions register with a scheduled review date. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. Operators should prefer configuration that is idempotent so that re-running the auditor produces no further changes.

**Verification.** Automated property checks generate varied host states to confirm the control behaves consistently. Verification is performed by the setup auditor, which compares the host state to the normalized policy expectation. The verifier records the before and after state for inclusion in the assessment package.

**References.** Prior assessment finding AF-3; Vendor hardening note VHN-3-1

**Revision history.**
- 2025-11: editorial revision to CM-006; clarified scope and wording.
- 2024-09: editorial revision to CM-006; clarified scope and wording.
- 2022-02: editorial revision to CM-006; clarified scope and wording.
- 2022-08: editorial revision to CM-006; clarified scope and wording.


### CM-007 — Monitored umask default

**Domain:** Configuration Management  **Severity:** Moderate  **Applies to:** service-account-bearing hosts

**Rationale.** This requirement aligns the gateway with the principle of least privilege mandated by the governing security policy. Adversaries routinely probe for misconfigurations of this control when establishing persistence on laboratory infrastructure. Inconsistent application of this requirement across hosts complicates evidence collection and weakens attestations.

**Requirement.** When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. The host shall maintain the configuration described in this control at all times, and the setup auditor shall treat any deviation as reportable. Inconsistent application of this requirement across hosts complicates evidence collection and weakens attestations.

**Implementation guidance.** Retain the prior configuration so that a rollback can be performed without rebuilding the host. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. Operators should prefer configuration that is idempotent so that re-running the auditor produces no further changes. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies.

**Verification.** Verification is performed by the setup auditor, which compares the host state to the normalized policy expectation. The verifier records the before and after state for inclusion in the assessment package. Verification is performed by the setup auditor, which compares the host state to the normalized policy expectation. Evidence is the auditor's proposed patch set; a compliant host yields an empty set for this control. Evidence is the auditor's proposed patch set; a compliant host yields an empty set for this control.

**References.** Governing Security Policy GSP-2024 §2.0; Lab Operations Runbook ROB-4

**Revision history.**
- 2024-06: editorial revision to CM-007; clarified scope and wording.
- 2023-08: editorial revision to CM-007; clarified scope and wording.


### CM-008 — Hardened kernel parameter

**Domain:** Configuration Management  **Severity:** Low  **Applies to:** gateway and bastion hosts

**Rationale.** Adversaries routinely probe for misconfigurations of this control when establishing persistence on laboratory infrastructure. The control exists to keep remediation deterministic so that repeated audits converge on a stable state. Inconsistent application of this requirement across hosts complicates evidence collection and weakens attestations.

**Requirement.** Operators should prefer configuration that is idempotent so that re-running the auditor produces no further changes. The host shall maintain the configuration described in this control at all times, and the setup auditor shall treat any deviation as reportable. Operational experience shows that small deviations here cascade into larger exposure during incident response.

**Implementation guidance.** Retain the prior configuration so that a rollback can be performed without rebuilding the host. Prefer explicit values over relying on compiled-in defaults, which may vary between distributions. Prefer explicit values over relying on compiled-in defaults, which may vary between distributions. Document any approved deviation in the exceptions register with a scheduled review date. Prefer explicit values over relying on compiled-in defaults, which may vary between distributions. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. Operators should prefer configuration that is idempotent so that re-running the auditor produces no further changes.

**Verification.** Assessors may re-run the audit after applying patches to confirm the host has converged. Assessors may re-run the audit after applying patches to confirm the host has converged. Automated property checks generate varied host states to confirm the control behaves consistently. Automated property checks generate varied host states to confirm the control behaves consistently. Evidence is the auditor's proposed patch set; a compliant host yields an empty set for this control.

**References.** Prior assessment finding AF-2; Baseline Configuration Guide BCG-3.2; Governing Security Policy GSP-2024 §4.4; Vendor hardening note VHN-5-4

**Revision history.**
- 2023-02: editorial revision to CM-008; clarified scope and wording.
- 2024-04: editorial revision to CM-008; clarified scope and wording.
- 2023-10: editorial revision to CM-008; clarified scope and wording.
- 2023-05: editorial revision to CM-008; clarified scope and wording.


### CM-009 — Monitored core dump handling

**Domain:** Configuration Management  **Severity:** Moderate  **Applies to:** shared interactive hosts

**Rationale.** Inconsistent application of this requirement across hosts complicates evidence collection and weakens attestations. The control supports reproducible builds of the host baseline and simplifies forensic comparison. Adversaries routinely probe for misconfigurations of this control when establishing persistence on laboratory infrastructure. This requirement aligns the gateway with the principle of least privilege mandated by the governing security policy.

**Requirement.** Operators should prefer configuration that is idempotent so that re-running the auditor produces no further changes. The host shall maintain the configuration described in this control at all times, and the setup auditor shall treat any deviation as reportable. The control exists to keep remediation deterministic so that repeated audits converge on a stable state.

**Implementation guidance.** Changes should be staged in a non-production environment and validated against the verification procedure below. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. Coordinate with the accounts team before altering anything that affects service-account behavior. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. Document any approved deviation in the exceptions register with a scheduled review date. Retain the prior configuration so that a rollback can be performed without rebuilding the host. Coordinate with the accounts team before altering anything that affects service-account behavior. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies.

**Verification.** Assessors may re-run the audit after applying patches to confirm the host has converged. Evidence is the auditor's proposed patch set; a compliant host yields an empty set for this control. The verifier records the before and after state for inclusion in the assessment package. Verification is performed by the setup auditor, which compares the host state to the normalized policy expectation. Verification is performed by the setup auditor, which compares the host state to the normalized policy expectation.

**References.** Lab Operations Runbook ROB-5; Vendor hardening note VHN-4-7; Governing Security Policy GSP-2024 §6.6

**Revision history.**
- 2023-11: editorial revision to CM-009; clarified scope and wording.
- 2024-01: editorial revision to CM-009; clarified scope and wording.
- 2023-02: editorial revision to CM-009; clarified scope and wording.


### CM-010 — Monitored log forwarding

**Domain:** Configuration Management  **Severity:** Moderate  **Applies to:** all managed hosts

**Rationale.** The control supports reproducible builds of the host baseline and simplifies forensic comparison. Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment. Operational experience shows that small deviations here cascade into larger exposure during incident response. Consistent enforcement reduces the mean time to detect anomalous access across the estate.

**Requirement.** When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. The host shall maintain the configuration described in this control at all times, and the setup auditor shall treat any deviation as reportable. This requirement aligns the gateway with the principle of least privilege mandated by the governing security policy.

**Implementation guidance.** When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. Prefer explicit values over relying on compiled-in defaults, which may vary between distributions. Coordinate with the accounts team before altering anything that affects service-account behavior. Operators should prefer configuration that is idempotent so that re-running the auditor produces no further changes. Operators should prefer configuration that is idempotent so that re-running the auditor produces no further changes. Changes should be staged in a non-production environment and validated against the verification procedure below. Document any approved deviation in the exceptions register with a scheduled review date.

**Verification.** The verifier records the before and after state for inclusion in the assessment package. Automated property checks generate varied host states to confirm the control behaves consistently. Assessors may re-run the audit after applying patches to confirm the host has converged.

**References.** Governing Security Policy GSP-2024 §5.9; Baseline Configuration Guide BCG-7.8; Lab Operations Runbook ROB-1

**Revision history.**
- 2025-04: editorial revision to CM-010; clarified scope and wording.
- 2023-05: editorial revision to CM-010; clarified scope and wording.


### CM-011 — Monitored service enablement

**Domain:** Configuration Management  **Severity:** Low  **Applies to:** shared interactive hosts

**Rationale.** Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment. Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment. Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment.

**Requirement.** Changes should be staged in a non-production environment and validated against the verification procedure below. The host shall maintain the configuration described in this control at all times, and the setup auditor shall treat any deviation as reportable. Inconsistent application of this requirement across hosts complicates evidence collection and weakens attestations.

**Implementation guidance.** Changes should be staged in a non-production environment and validated against the verification procedure below. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. Document any approved deviation in the exceptions register with a scheduled review date. Document any approved deviation in the exceptions register with a scheduled review date. Prefer explicit values over relying on compiled-in defaults, which may vary between distributions. Prefer explicit values over relying on compiled-in defaults, which may vary between distributions. Operators should prefer configuration that is idempotent so that re-running the auditor produces no further changes.

**Verification.** Verification is performed by the setup auditor, which compares the host state to the normalized policy expectation. Automated property checks generate varied host states to confirm the control behaves consistently. Evidence is the auditor's proposed patch set; a compliant host yields an empty set for this control. Evidence is the auditor's proposed patch set; a compliant host yields an empty set for this control. Assessors may re-run the audit after applying patches to confirm the host has converged.

**References.** Prior assessment finding AF-4; Baseline Configuration Guide BCG-9.9; Prior assessment finding AF-6; Lab Operations Runbook ROB-3

**Revision history.**
- 2024-02: editorial revision to CM-011; clarified scope and wording.
- 2023-04: editorial revision to CM-011; clarified scope and wording.


### CM-012 — Approved module loading

**Domain:** Configuration Management  **Severity:** Low  **Applies to:** service-account-bearing hosts

**Rationale.** Adversaries routinely probe for misconfigurations of this control when establishing persistence on laboratory infrastructure. Adversaries routinely probe for misconfigurations of this control when establishing persistence on laboratory infrastructure. Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment. Adversaries routinely probe for misconfigurations of this control when establishing persistence on laboratory infrastructure.

**Requirement.** When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. The host shall maintain the configuration described in this control at all times, and the setup auditor shall treat any deviation as reportable. Operational experience shows that small deviations here cascade into larger exposure during incident response.

**Implementation guidance.** Changes should be staged in a non-production environment and validated against the verification procedure below. Document any approved deviation in the exceptions register with a scheduled review date. Retain the prior configuration so that a rollback can be performed without rebuilding the host. Changes should be staged in a non-production environment and validated against the verification procedure below. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. Coordinate with the accounts team before altering anything that affects service-account behavior. Coordinate with the accounts team before altering anything that affects service-account behavior.

**Verification.** Evidence is the auditor's proposed patch set; a compliant host yields an empty set for this control. Automated property checks generate varied host states to confirm the control behaves consistently. Verification is performed by the setup auditor, which compares the host state to the normalized policy expectation.

**References.** Baseline Configuration Guide BCG-4.6; Baseline Configuration Guide BCG-5.2; Baseline Configuration Guide BCG-4.5; Prior assessment finding AF-4

**Revision history.**
- 2025-05: editorial revision to CM-012; clarified scope and wording.
- 2023-02: editorial revision to CM-012; clarified scope and wording.
- 2022-09: editorial revision to CM-012; clarified scope and wording.


### CM-013 — Centralized log forwarding

**Domain:** Configuration Management  **Severity:** High  **Applies to:** tier-1 laboratory hosts

**Rationale.** Adversaries routinely probe for misconfigurations of this control when establishing persistence on laboratory infrastructure. Consistent enforcement reduces the mean time to detect anomalous access across the estate. The control exists to keep remediation deterministic so that repeated audits converge on a stable state. Operational experience shows that small deviations here cascade into larger exposure during incident response. Operational experience shows that small deviations here cascade into larger exposure during incident response.

**Requirement.** When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. The host shall maintain the configuration described in this control at all times, and the setup auditor shall treat any deviation as reportable. This requirement aligns the gateway with the principle of least privilege mandated by the governing security policy.

**Implementation guidance.** When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. Document any approved deviation in the exceptions register with a scheduled review date. Prefer explicit values over relying on compiled-in defaults, which may vary between distributions. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. Document any approved deviation in the exceptions register with a scheduled review date.

**Verification.** The verifier records the before and after state for inclusion in the assessment package. Assessors may re-run the audit after applying patches to confirm the host has converged. Assessors may re-run the audit after applying patches to confirm the host has converged.

**References.** Governing Security Policy GSP-2024 §6.8; Governing Security Policy GSP-2024 §5.5; Prior assessment finding AF-3

**Revision history.**
- 2024-09: editorial revision to CM-013; clarified scope and wording.
- 2022-02: editorial revision to CM-013; clarified scope and wording.


### CM-014 — Restricted module loading

**Domain:** Configuration Management  **Severity:** High  **Applies to:** shared interactive hosts

**Rationale.** This requirement aligns the gateway with the principle of least privilege mandated by the governing security policy. The control exists to keep remediation deterministic so that repeated audits converge on a stable state. Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment. Consistent enforcement reduces the mean time to detect anomalous access across the estate.

**Requirement.** Prefer explicit values over relying on compiled-in defaults, which may vary between distributions. The host shall maintain the configuration described in this control at all times, and the setup auditor shall treat any deviation as reportable. The control supports reproducible builds of the host baseline and simplifies forensic comparison.

**Implementation guidance.** When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. Prefer explicit values over relying on compiled-in defaults, which may vary between distributions. Coordinate with the accounts team before altering anything that affects service-account behavior. Changes should be staged in a non-production environment and validated against the verification procedure below. Changes should be staged in a non-production environment and validated against the verification procedure below. Document any approved deviation in the exceptions register with a scheduled review date. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner.

**Verification.** Evidence is the auditor's proposed patch set; a compliant host yields an empty set for this control. Assessors may re-run the audit after applying patches to confirm the host has converged. Evidence is the auditor's proposed patch set; a compliant host yields an empty set for this control.

**References.** Governing Security Policy GSP-2024 §1.9; Lab Operations Runbook ROB-8; Vendor hardening note VHN-2-4

**Revision history.**
- 2022-04: editorial revision to CM-014; clarified scope and wording.
- 2024-11: editorial revision to CM-014; clarified scope and wording.
- 2025-10: editorial revision to CM-014; clarified scope and wording.


## 6. System Hardening

Operational experience shows that small deviations here cascade into larger exposure during incident response. Adversaries routinely probe for misconfigurations of this control when establishing persistence on laboratory infrastructure. Inconsistent application of this requirement across hosts complicates evidence collection and weakens attestations. Adversaries routinely probe for misconfigurations of this control when establishing persistence on laboratory infrastructure. Adversaries routinely probe for misconfigurations of this control when establishing persistence on laboratory infrastructure. Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment.


Prefer explicit values over relying on compiled-in defaults, which may vary between distributions. Coordinate with the accounts team before altering anything that affects service-account behavior. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. Prefer explicit values over relying on compiled-in defaults, which may vary between distributions. Coordinate with the accounts team before altering anything that affects service-account behavior. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies.


### HD-001 — Baseline log forwarding

**Domain:** System Hardening  **Severity:** High  **Applies to:** all managed hosts

**Rationale.** Inconsistent application of this requirement across hosts complicates evidence collection and weakens attestations. Operational experience shows that small deviations here cascade into larger exposure during incident response. Adversaries routinely probe for misconfigurations of this control when establishing persistence on laboratory infrastructure.

**Requirement.** When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. The host shall maintain the configuration described in this control at all times, and the setup auditor shall treat any deviation as reportable. This requirement aligns the gateway with the principle of least privilege mandated by the governing security policy.

**Implementation guidance.** Coordinate with the accounts team before altering anything that affects service-account behavior. Coordinate with the accounts team before altering anything that affects service-account behavior. Prefer explicit values over relying on compiled-in defaults, which may vary between distributions. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. Operators should prefer configuration that is idempotent so that re-running the auditor produces no further changes.

**Verification.** Verification is performed by the setup auditor, which compares the host state to the normalized policy expectation. The verifier records the before and after state for inclusion in the assessment package. Evidence is the auditor's proposed patch set; a compliant host yields an empty set for this control.

**References.** Governing Security Policy GSP-2024 §7.1; Lab Operations Runbook ROB-3; Lab Operations Runbook ROB-4; Baseline Configuration Guide BCG-9.1

**Revision history.**
- 2024-08: editorial revision to HD-001; clarified scope and wording.
- 2023-10: editorial revision to HD-001; clarified scope and wording.


### HD-SSHD-DROPIN — Effective sshd drop-in settings

**Domain:** System Hardening  **Severity:** Critical  **Applies to:** gateway and bastion hosts

**Rationale.** The OpenSSH daemon reads drop-in fragments in a defined order, and only the effective value matters for hardening. The auditor must compute the effective value exactly as the daemon would.

**Requirement.** Drop-in fragments shall be concatenated in ascending filename order. Scanning the concatenated text top to bottom, everything from the first line whose first token is `Match` (compared case-insensitively) onward is a conditional block and shall be ignored for the purpose of this control. Among the remaining global lines, a setting takes the form `Keyword value`; keywords are compared case-insensitively and the **first** occurrence of a keyword establishes the effective value (consistent with OpenSSH first-match semantics). A keyword that never appears in a global line has no effective value.

The auditor evaluates `PermitRootLogin` and `PasswordAuthentication`. For each, when the effective value is absent or is not an accepted value, the auditor shall propose `systemd.set_dropin` with unit `sshd`, the keyword, and value `no`. In the body of this Standard the only accepted value for either keyword is `no`. *(Appendix G broadens the accepted values for one keyword.)*

*(Appendix G replaces the conditional-block handling of this control with context-based evaluation; see the amendment referencing HD-SSHD-DROPIN.)*

**Implementation guidance.** Do not let a later fragment or a value inside a `Match` block override an earlier global value; first global occurrence wins, subject to the conditional-block evaluation defined in Appendix G.

**Verification.** A compliant host has accepted effective values for both keywords and yields no `systemd.set_dropin` patch.

**References.** Governing Security Policy GSP-2024 §6.2; Vendor hardening note VHN-5-1

**Revision history.**
- 2023-09: initial publication.
- 2024-11: clarified Match-block exclusion and first-match semantics.


### HD-002 — Hardened banner presentation

**Domain:** System Hardening  **Severity:** High  **Applies to:** service-account-bearing hosts

**Rationale.** Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment. Adversaries routinely probe for misconfigurations of this control when establishing persistence on laboratory infrastructure. This requirement aligns the gateway with the principle of least privilege mandated by the governing security policy.

**Requirement.** Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. The host shall maintain the configuration described in this control at all times, and the setup auditor shall treat any deviation as reportable. Inconsistent application of this requirement across hosts complicates evidence collection and weakens attestations.

**Implementation guidance.** Changes should be staged in a non-production environment and validated against the verification procedure below. Document any approved deviation in the exceptions register with a scheduled review date. Retain the prior configuration so that a rollback can be performed without rebuilding the host. Operators should prefer configuration that is idempotent so that re-running the auditor produces no further changes. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. Operators should prefer configuration that is idempotent so that re-running the auditor produces no further changes.

**Verification.** Evidence is the auditor's proposed patch set; a compliant host yields an empty set for this control. Automated property checks generate varied host states to confirm the control behaves consistently. Assessors may re-run the audit after applying patches to confirm the host has converged. Evidence is the auditor's proposed patch set; a compliant host yields an empty set for this control. Automated property checks generate varied host states to confirm the control behaves consistently.

**References.** Prior assessment finding AF-6; Lab Operations Runbook ROB-4; Lab Operations Runbook ROB-7

**Revision history.**
- 2025-09: editorial revision to HD-002; clarified scope and wording.
- 2022-01: editorial revision to HD-002; clarified scope and wording.
- 2025-12: editorial revision to HD-002; clarified scope and wording.
- 2022-08: editorial revision to HD-002; clarified scope and wording.


### HD-SSHD-KBDINT — Effective keyboard-interactive authentication

**Domain:** System Hardening  **Severity:** High  **Applies to:** gateway and bastion hosts

**Rationale.** Keyboard-interactive authentication can silently re-enable password-style prompts even where `PasswordAuthentication` is disabled, so its effective value must be controlled with the same rigor as the other sshd keywords.

**Requirement.** In addition to the keywords in HD-SSHD-DROPIN, the auditor shall evaluate `KbdInteractiveAuthentication`. Its effective value is computed using the **same** drop-in precedence rules as HD-SSHD-DROPIN: fragments concatenated in ascending filename order, everything from the first `Match` line onward ignored, and the first global occurrence of the keyword establishing the effective value (keywords compared case-insensitively). When the effective value is absent, or is any value other than an accepted value, the auditor shall propose `systemd.set_dropin` with unit `sshd`, key `KbdInteractiveAuthentication`, and value `no`. The only accepted value is `no`. *(Appendix G adds a deprecated alias keyword for this control.)*

**Implementation guidance.** Reuse the precedence machinery from HD-SSHD-DROPIN; this keyword is evaluated independently of the others.

**Verification.** A compliant host has an effective `KbdInteractiveAuthentication` of `no` and yields no patch for this keyword.

**References.** Governing Security Policy GSP-2024 §6.3; Vendor hardening note VHN-6-2

**Revision history.**
- 2025-03: initial publication.


### HD-003 — Approved console access

**Domain:** System Hardening  **Severity:** Moderate  **Applies to:** shared interactive hosts

**Rationale.** Operational experience shows that small deviations here cascade into larger exposure during incident response. Consistent enforcement reduces the mean time to detect anomalous access across the estate. This requirement aligns the gateway with the principle of least privilege mandated by the governing security policy. Adversaries routinely probe for misconfigurations of this control when establishing persistence on laboratory infrastructure.

**Requirement.** Changes should be staged in a non-production environment and validated against the verification procedure below. The host shall maintain the configuration described in this control at all times, and the setup auditor shall treat any deviation as reportable. Operational experience shows that small deviations here cascade into larger exposure during incident response.

**Implementation guidance.** Changes should be staged in a non-production environment and validated against the verification procedure below. Changes should be staged in a non-production environment and validated against the verification procedure below. Retain the prior configuration so that a rollback can be performed without rebuilding the host. Retain the prior configuration so that a rollback can be performed without rebuilding the host. Coordinate with the accounts team before altering anything that affects service-account behavior. Operators should prefer configuration that is idempotent so that re-running the auditor produces no further changes.

**Verification.** Assessors may re-run the audit after applying patches to confirm the host has converged. Verification is performed by the setup auditor, which compares the host state to the normalized policy expectation. Assessors may re-run the audit after applying patches to confirm the host has converged. Evidence is the auditor's proposed patch set; a compliant host yields an empty set for this control. Automated property checks generate varied host states to confirm the control behaves consistently.

**References.** Baseline Configuration Guide BCG-3.4; Baseline Configuration Guide BCG-5.2

**Revision history.**
- 2024-05: editorial revision to HD-003; clarified scope and wording.
- 2025-08: editorial revision to HD-003; clarified scope and wording.
- 2025-08: editorial revision to HD-003; clarified scope and wording.
- 2022-12: editorial revision to HD-003; clarified scope and wording.


### HD-004 — Baseline credential rotation

**Domain:** System Hardening  **Severity:** Low  **Applies to:** all managed hosts

**Rationale.** The control exists to keep remediation deterministic so that repeated audits converge on a stable state. Consistent enforcement reduces the mean time to detect anomalous access across the estate. Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment. The control exists to keep remediation deterministic so that repeated audits converge on a stable state.

**Requirement.** When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. The host shall maintain the configuration described in this control at all times, and the setup auditor shall treat any deviation as reportable. This requirement aligns the gateway with the principle of least privilege mandated by the governing security policy.

**Implementation guidance.** Operators should prefer configuration that is idempotent so that re-running the auditor produces no further changes. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. Coordinate with the accounts team before altering anything that affects service-account behavior. Coordinate with the accounts team before altering anything that affects service-account behavior. Operators should prefer configuration that is idempotent so that re-running the auditor produces no further changes.

**Verification.** The verifier records the before and after state for inclusion in the assessment package. The verifier records the before and after state for inclusion in the assessment package. Assessors may re-run the audit after applying patches to confirm the host has converged. Evidence is the auditor's proposed patch set; a compliant host yields an empty set for this control.

**References.** Governing Security Policy GSP-2024 §5.5; Baseline Configuration Guide BCG-1.8

**Revision history.**
- 2025-03: editorial revision to HD-004; clarified scope and wording.
- 2022-05: editorial revision to HD-004; clarified scope and wording.


### HD-005 — Approved service enablement

**Domain:** System Hardening  **Severity:** Critical  **Applies to:** gateway and bastion hosts

**Rationale.** Operational experience shows that small deviations here cascade into larger exposure during incident response. This requirement aligns the gateway with the principle of least privilege mandated by the governing security policy. This requirement aligns the gateway with the principle of least privilege mandated by the governing security policy. The control supports reproducible builds of the host baseline and simplifies forensic comparison.

**Requirement.** When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. The host shall maintain the configuration described in this control at all times, and the setup auditor shall treat any deviation as reportable. This requirement aligns the gateway with the principle of least privilege mandated by the governing security policy.

**Implementation guidance.** Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. Document any approved deviation in the exceptions register with a scheduled review date. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. Retain the prior configuration so that a rollback can be performed without rebuilding the host.

**Verification.** Assessors may re-run the audit after applying patches to confirm the host has converged. Assessors may re-run the audit after applying patches to confirm the host has converged. Verification is performed by the setup auditor, which compares the host state to the normalized policy expectation. Automated property checks generate varied host states to confirm the control behaves consistently. Verification is performed by the setup auditor, which compares the host state to the normalized policy expectation.

**References.** Lab Operations Runbook ROB-7; Vendor hardening note VHN-1-2; Prior assessment finding AF-1; Lab Operations Runbook ROB-4

**Revision history.**
- 2024-03: editorial revision to HD-005; clarified scope and wording.
- 2024-10: editorial revision to HD-005; clarified scope and wording.


### HD-006 — Restricted filesystem mount option

**Domain:** System Hardening  **Severity:** Low  **Applies to:** gateway and bastion hosts

**Rationale.** Inconsistent application of this requirement across hosts complicates evidence collection and weakens attestations. The control exists to keep remediation deterministic so that repeated audits converge on a stable state. Operational experience shows that small deviations here cascade into larger exposure during incident response. This requirement aligns the gateway with the principle of least privilege mandated by the governing security policy.

**Requirement.** Prefer explicit values over relying on compiled-in defaults, which may vary between distributions. The host shall maintain the configuration described in this control at all times, and the setup auditor shall treat any deviation as reportable. The control exists to keep remediation deterministic so that repeated audits converge on a stable state.

**Implementation guidance.** Retain the prior configuration so that a rollback can be performed without rebuilding the host. Operators should prefer configuration that is idempotent so that re-running the auditor produces no further changes. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. Operators should prefer configuration that is idempotent so that re-running the auditor produces no further changes. Prefer explicit values over relying on compiled-in defaults, which may vary between distributions. Changes should be staged in a non-production environment and validated against the verification procedure below. Retain the prior configuration so that a rollback can be performed without rebuilding the host.

**Verification.** Evidence is the auditor's proposed patch set; a compliant host yields an empty set for this control. Evidence is the auditor's proposed patch set; a compliant host yields an empty set for this control. The verifier records the before and after state for inclusion in the assessment package. Evidence is the auditor's proposed patch set; a compliant host yields an empty set for this control.

**References.** Prior assessment finding AF-1; Lab Operations Runbook ROB-3; Governing Security Policy GSP-2024 §1.5

**Revision history.**
- 2025-03: editorial revision to HD-006; clarified scope and wording.
- 2023-12: editorial revision to HD-006; clarified scope and wording.


### HD-007 — Hardened service enablement

**Domain:** System Hardening  **Severity:** High  **Applies to:** service-account-bearing hosts

**Rationale.** This requirement aligns the gateway with the principle of least privilege mandated by the governing security policy. The control exists to keep remediation deterministic so that repeated audits converge on a stable state. Inconsistent application of this requirement across hosts complicates evidence collection and weakens attestations. The control exists to keep remediation deterministic so that repeated audits converge on a stable state. The control supports reproducible builds of the host baseline and simplifies forensic comparison.

**Requirement.** Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. The host shall maintain the configuration described in this control at all times, and the setup auditor shall treat any deviation as reportable. Consistent enforcement reduces the mean time to detect anomalous access across the estate.

**Implementation guidance.** When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. Changes should be staged in a non-production environment and validated against the verification procedure below. Prefer explicit values over relying on compiled-in defaults, which may vary between distributions. Coordinate with the accounts team before altering anything that affects service-account behavior. Coordinate with the accounts team before altering anything that affects service-account behavior. Coordinate with the accounts team before altering anything that affects service-account behavior. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner.

**Verification.** The verifier records the before and after state for inclusion in the assessment package. The verifier records the before and after state for inclusion in the assessment package. Evidence is the auditor's proposed patch set; a compliant host yields an empty set for this control. The verifier records the before and after state for inclusion in the assessment package.

**References.** Baseline Configuration Guide BCG-5.2; Baseline Configuration Guide BCG-3.4; Prior assessment finding AF-7

**Revision history.**
- 2024-02: editorial revision to HD-007; clarified scope and wording.
- 2023-10: editorial revision to HD-007; clarified scope and wording.
- 2024-08: editorial revision to HD-007; clarified scope and wording.


### HD-008 — Standard credential rotation

**Domain:** System Hardening  **Severity:** High  **Applies to:** service-account-bearing hosts

**Rationale.** The control exists to keep remediation deterministic so that repeated audits converge on a stable state. Inconsistent application of this requirement across hosts complicates evidence collection and weakens attestations. Operational experience shows that small deviations here cascade into larger exposure during incident response.

**Requirement.** Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. The host shall maintain the configuration described in this control at all times, and the setup auditor shall treat any deviation as reportable. Operational experience shows that small deviations here cascade into larger exposure during incident response.

**Implementation guidance.** When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. Operators should prefer configuration that is idempotent so that re-running the auditor produces no further changes. Document any approved deviation in the exceptions register with a scheduled review date. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. Coordinate with the accounts team before altering anything that affects service-account behavior. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. Changes should be staged in a non-production environment and validated against the verification procedure below.

**Verification.** Verification is performed by the setup auditor, which compares the host state to the normalized policy expectation. Automated property checks generate varied host states to confirm the control behaves consistently. The verifier records the before and after state for inclusion in the assessment package. Evidence is the auditor's proposed patch set; a compliant host yields an empty set for this control. Evidence is the auditor's proposed patch set; a compliant host yields an empty set for this control.

**References.** Prior assessment finding AF-9; Prior assessment finding AF-7; Governing Security Policy GSP-2024 §9.3

**Revision history.**
- 2022-05: editorial revision to HD-008; clarified scope and wording.
- 2022-07: editorial revision to HD-008; clarified scope and wording.


### HD-009 — Mandatory service enablement

**Domain:** System Hardening  **Severity:** Moderate  **Applies to:** gateway and bastion hosts

**Rationale.** This requirement aligns the gateway with the principle of least privilege mandated by the governing security policy. This requirement aligns the gateway with the principle of least privilege mandated by the governing security policy. Inconsistent application of this requirement across hosts complicates evidence collection and weakens attestations. Operational experience shows that small deviations here cascade into larger exposure during incident response.

**Requirement.** Retain the prior configuration so that a rollback can be performed without rebuilding the host. The host shall maintain the configuration described in this control at all times, and the setup auditor shall treat any deviation as reportable. Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment.

**Implementation guidance.** Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. Changes should be staged in a non-production environment and validated against the verification procedure below. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. Coordinate with the accounts team before altering anything that affects service-account behavior. Retain the prior configuration so that a rollback can be performed without rebuilding the host. Coordinate with the accounts team before altering anything that affects service-account behavior. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner.

**Verification.** Evidence is the auditor's proposed patch set; a compliant host yields an empty set for this control. Automated property checks generate varied host states to confirm the control behaves consistently. The verifier records the before and after state for inclusion in the assessment package. Evidence is the auditor's proposed patch set; a compliant host yields an empty set for this control.

**References.** Baseline Configuration Guide BCG-2.4; Vendor hardening note VHN-3-6; Baseline Configuration Guide BCG-7.2; Baseline Configuration Guide BCG-6.9

**Revision history.**
- 2024-09: editorial revision to HD-009; clarified scope and wording.
- 2022-07: editorial revision to HD-009; clarified scope and wording.


### HD-010 — Hardened filesystem mount option

**Domain:** System Hardening  **Severity:** High  **Applies to:** gateway and bastion hosts

**Rationale.** Adversaries routinely probe for misconfigurations of this control when establishing persistence on laboratory infrastructure. This requirement aligns the gateway with the principle of least privilege mandated by the governing security policy. The control supports reproducible builds of the host baseline and simplifies forensic comparison.

**Requirement.** Prefer explicit values over relying on compiled-in defaults, which may vary between distributions. The host shall maintain the configuration described in this control at all times, and the setup auditor shall treat any deviation as reportable. Consistent enforcement reduces the mean time to detect anomalous access across the estate.

**Implementation guidance.** When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. Prefer explicit values over relying on compiled-in defaults, which may vary between distributions. Operators should prefer configuration that is idempotent so that re-running the auditor produces no further changes. Operators should prefer configuration that is idempotent so that re-running the auditor produces no further changes. Document any approved deviation in the exceptions register with a scheduled review date.

**Verification.** Evidence is the auditor's proposed patch set; a compliant host yields an empty set for this control. Automated property checks generate varied host states to confirm the control behaves consistently. Evidence is the auditor's proposed patch set; a compliant host yields an empty set for this control.

**References.** Prior assessment finding AF-8; Vendor hardening note VHN-1-4; Baseline Configuration Guide BCG-8.9

**Revision history.**
- 2023-02: editorial revision to HD-010; clarified scope and wording.
- 2022-12: editorial revision to HD-010; clarified scope and wording.
- 2025-01: editorial revision to HD-010; clarified scope and wording.
- 2023-06: editorial revision to HD-010; clarified scope and wording.


### HD-011 — Restricted umask default

**Domain:** System Hardening  **Severity:** High  **Applies to:** service-account-bearing hosts

**Rationale.** Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment. The control exists to keep remediation deterministic so that repeated audits converge on a stable state. The control supports reproducible builds of the host baseline and simplifies forensic comparison.

**Requirement.** Operators should prefer configuration that is idempotent so that re-running the auditor produces no further changes. The host shall maintain the configuration described in this control at all times, and the setup auditor shall treat any deviation as reportable. Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment.

**Implementation guidance.** Changes should be staged in a non-production environment and validated against the verification procedure below. Document any approved deviation in the exceptions register with a scheduled review date. Operators should prefer configuration that is idempotent so that re-running the auditor produces no further changes. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner.

**Verification.** Evidence is the auditor's proposed patch set; a compliant host yields an empty set for this control. Automated property checks generate varied host states to confirm the control behaves consistently. The verifier records the before and after state for inclusion in the assessment package. Automated property checks generate varied host states to confirm the control behaves consistently.

**References.** Vendor hardening note VHN-3-4; Baseline Configuration Guide BCG-4.2; Baseline Configuration Guide BCG-4.0

**Revision history.**
- 2023-03: editorial revision to HD-011; clarified scope and wording.
- 2022-04: editorial revision to HD-011; clarified scope and wording.
- 2023-11: editorial revision to HD-011; clarified scope and wording.


## 7. Logging and Telemetry

Operational experience shows that small deviations here cascade into larger exposure during incident response. Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment. Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment. This requirement aligns the gateway with the principle of least privilege mandated by the governing security policy. This requirement aligns the gateway with the principle of least privilege mandated by the governing security policy.


Operators should prefer configuration that is idempotent so that re-running the auditor produces no further changes. Operators should prefer configuration that is idempotent so that re-running the auditor produces no further changes. Coordinate with the accounts team before altering anything that affects service-account behavior. Operators should prefer configuration that is idempotent so that re-running the auditor produces no further changes.


### LG-001 — Centralized module loading

**Domain:** Logging and Telemetry  **Severity:** Low  **Applies to:** shared interactive hosts

**Rationale.** Operational experience shows that small deviations here cascade into larger exposure during incident response. Consistent enforcement reduces the mean time to detect anomalous access across the estate. Operational experience shows that small deviations here cascade into larger exposure during incident response. The control exists to keep remediation deterministic so that repeated audits converge on a stable state.

**Requirement.** Retain the prior configuration so that a rollback can be performed without rebuilding the host. The host shall maintain the configuration described in this control at all times, and the setup auditor shall treat any deviation as reportable. Adversaries routinely probe for misconfigurations of this control when establishing persistence on laboratory infrastructure.

**Implementation guidance.** Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. Document any approved deviation in the exceptions register with a scheduled review date. Document any approved deviation in the exceptions register with a scheduled review date. Document any approved deviation in the exceptions register with a scheduled review date. Coordinate with the accounts team before altering anything that affects service-account behavior.

**Verification.** Automated property checks generate varied host states to confirm the control behaves consistently. Verification is performed by the setup auditor, which compares the host state to the normalized policy expectation. Verification is performed by the setup auditor, which compares the host state to the normalized policy expectation.

**References.** Lab Operations Runbook ROB-2; Governing Security Policy GSP-2024 §3.3; Prior assessment finding AF-7; Baseline Configuration Guide BCG-4.4

**Revision history.**
- 2023-06: editorial revision to LG-001; clarified scope and wording.
- 2024-08: editorial revision to LG-001; clarified scope and wording.
- 2023-11: editorial revision to LG-001; clarified scope and wording.
- 2022-02: editorial revision to LG-001; clarified scope and wording.


### LG-002 — Controlled kernel parameter

**Domain:** Logging and Telemetry  **Severity:** Low  **Applies to:** shared interactive hosts

**Rationale.** Operational experience shows that small deviations here cascade into larger exposure during incident response. This requirement aligns the gateway with the principle of least privilege mandated by the governing security policy. Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment. Operational experience shows that small deviations here cascade into larger exposure during incident response. Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment.

**Requirement.** Prefer explicit values over relying on compiled-in defaults, which may vary between distributions. The host shall maintain the configuration described in this control at all times, and the setup auditor shall treat any deviation as reportable. This requirement aligns the gateway with the principle of least privilege mandated by the governing security policy.

**Implementation guidance.** When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. Coordinate with the accounts team before altering anything that affects service-account behavior. Prefer explicit values over relying on compiled-in defaults, which may vary between distributions. Retain the prior configuration so that a rollback can be performed without rebuilding the host. Changes should be staged in a non-production environment and validated against the verification procedure below. Changes should be staged in a non-production environment and validated against the verification procedure below. Changes should be staged in a non-production environment and validated against the verification procedure below. Coordinate with the accounts team before altering anything that affects service-account behavior.

**Verification.** Verification is performed by the setup auditor, which compares the host state to the normalized policy expectation. Evidence is the auditor's proposed patch set; a compliant host yields an empty set for this control. Evidence is the auditor's proposed patch set; a compliant host yields an empty set for this control.

**References.** Governing Security Policy GSP-2024 §9.5; Baseline Configuration Guide BCG-4.0; Lab Operations Runbook ROB-2; Governing Security Policy GSP-2024 §9.2

**Revision history.**
- 2022-04: editorial revision to LG-002; clarified scope and wording.
- 2025-03: editorial revision to LG-002; clarified scope and wording.
- 2025-12: editorial revision to LG-002; clarified scope and wording.
- 2024-09: editorial revision to LG-002; clarified scope and wording.


### LG-003 — Standard credential rotation

**Domain:** Logging and Telemetry  **Severity:** Moderate  **Applies to:** gateway and bastion hosts

**Rationale.** The control exists to keep remediation deterministic so that repeated audits converge on a stable state. The control exists to keep remediation deterministic so that repeated audits converge on a stable state. Operational experience shows that small deviations here cascade into larger exposure during incident response.

**Requirement.** When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. The host shall maintain the configuration described in this control at all times, and the setup auditor shall treat any deviation as reportable. Consistent enforcement reduces the mean time to detect anomalous access across the estate.

**Implementation guidance.** Retain the prior configuration so that a rollback can be performed without rebuilding the host. Changes should be staged in a non-production environment and validated against the verification procedure below. Changes should be staged in a non-production environment and validated against the verification procedure below. Document any approved deviation in the exceptions register with a scheduled review date. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. Prefer explicit values over relying on compiled-in defaults, which may vary between distributions. Retain the prior configuration so that a rollback can be performed without rebuilding the host.

**Verification.** Verification is performed by the setup auditor, which compares the host state to the normalized policy expectation. Verification is performed by the setup auditor, which compares the host state to the normalized policy expectation. Automated property checks generate varied host states to confirm the control behaves consistently. Automated property checks generate varied host states to confirm the control behaves consistently.

**References.** Lab Operations Runbook ROB-3; Baseline Configuration Guide BCG-7.9; Vendor hardening note VHN-8-6; Lab Operations Runbook ROB-7

**Revision history.**
- 2023-09: editorial revision to LG-003; clarified scope and wording.
- 2022-12: editorial revision to LG-003; clarified scope and wording.
- 2025-12: editorial revision to LG-003; clarified scope and wording.
- 2024-04: editorial revision to LG-003; clarified scope and wording.


### LG-004 — Restricted interface configuration

**Domain:** Logging and Telemetry  **Severity:** Moderate  **Applies to:** gateway and bastion hosts

**Rationale.** Operational experience shows that small deviations here cascade into larger exposure during incident response. Inconsistent application of this requirement across hosts complicates evidence collection and weakens attestations. Operational experience shows that small deviations here cascade into larger exposure during incident response.

**Requirement.** Retain the prior configuration so that a rollback can be performed without rebuilding the host. The host shall maintain the configuration described in this control at all times, and the setup auditor shall treat any deviation as reportable. Consistent enforcement reduces the mean time to detect anomalous access across the estate.

**Implementation guidance.** Prefer explicit values over relying on compiled-in defaults, which may vary between distributions. Coordinate with the accounts team before altering anything that affects service-account behavior. Operators should prefer configuration that is idempotent so that re-running the auditor produces no further changes. Coordinate with the accounts team before altering anything that affects service-account behavior. Document any approved deviation in the exceptions register with a scheduled review date. Retain the prior configuration so that a rollback can be performed without rebuilding the host. Document any approved deviation in the exceptions register with a scheduled review date.

**Verification.** Automated property checks generate varied host states to confirm the control behaves consistently. Evidence is the auditor's proposed patch set; a compliant host yields an empty set for this control. Automated property checks generate varied host states to confirm the control behaves consistently.

**References.** Lab Operations Runbook ROB-9; Governing Security Policy GSP-2024 §4.8

**Revision history.**
- 2023-08: editorial revision to LG-004; clarified scope and wording.
- 2023-11: editorial revision to LG-004; clarified scope and wording.


### LG-005 — Centralized banner presentation

**Domain:** Logging and Telemetry  **Severity:** Critical  **Applies to:** gateway and bastion hosts

**Rationale.** Operational experience shows that small deviations here cascade into larger exposure during incident response. Consistent enforcement reduces the mean time to detect anomalous access across the estate. Inconsistent application of this requirement across hosts complicates evidence collection and weakens attestations.

**Requirement.** Prefer explicit values over relying on compiled-in defaults, which may vary between distributions. The host shall maintain the configuration described in this control at all times, and the setup auditor shall treat any deviation as reportable. Consistent enforcement reduces the mean time to detect anomalous access across the estate.

**Implementation guidance.** Coordinate with the accounts team before altering anything that affects service-account behavior. Prefer explicit values over relying on compiled-in defaults, which may vary between distributions. Retain the prior configuration so that a rollback can be performed without rebuilding the host. Document any approved deviation in the exceptions register with a scheduled review date. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. Document any approved deviation in the exceptions register with a scheduled review date. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner.

**Verification.** Verification is performed by the setup auditor, which compares the host state to the normalized policy expectation. Verification is performed by the setup auditor, which compares the host state to the normalized policy expectation. Verification is performed by the setup auditor, which compares the host state to the normalized policy expectation.

**References.** Governing Security Policy GSP-2024 §4.5; Baseline Configuration Guide BCG-7.9; Baseline Configuration Guide BCG-8.7

**Revision history.**
- 2024-06: editorial revision to LG-005; clarified scope and wording.
- 2022-11: editorial revision to LG-005; clarified scope and wording.
- 2022-08: editorial revision to LG-005; clarified scope and wording.


### LG-006 — Monitored console access

**Domain:** Logging and Telemetry  **Severity:** Moderate  **Applies to:** service-account-bearing hosts

**Rationale.** Consistent enforcement reduces the mean time to detect anomalous access across the estate. Consistent enforcement reduces the mean time to detect anomalous access across the estate. Consistent enforcement reduces the mean time to detect anomalous access across the estate. Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment.

**Requirement.** Operators should prefer configuration that is idempotent so that re-running the auditor produces no further changes. The host shall maintain the configuration described in this control at all times, and the setup auditor shall treat any deviation as reportable. Consistent enforcement reduces the mean time to detect anomalous access across the estate.

**Implementation guidance.** Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. Changes should be staged in a non-production environment and validated against the verification procedure below. Coordinate with the accounts team before altering anything that affects service-account behavior. Changes should be staged in a non-production environment and validated against the verification procedure below. Changes should be staged in a non-production environment and validated against the verification procedure below.

**Verification.** Assessors may re-run the audit after applying patches to confirm the host has converged. The verifier records the before and after state for inclusion in the assessment package. The verifier records the before and after state for inclusion in the assessment package. Assessors may re-run the audit after applying patches to confirm the host has converged. Evidence is the auditor's proposed patch set; a compliant host yields an empty set for this control.

**References.** Vendor hardening note VHN-6-6; Vendor hardening note VHN-8-4

**Revision history.**
- 2023-11: editorial revision to LG-006; clarified scope and wording.
- 2022-07: editorial revision to LG-006; clarified scope and wording.
- 2022-12: editorial revision to LG-006; clarified scope and wording.
- 2023-02: editorial revision to LG-006; clarified scope and wording.


### LG-007 — Restricted filesystem mount option

**Domain:** Logging and Telemetry  **Severity:** Critical  **Applies to:** shared interactive hosts

**Rationale.** The control exists to keep remediation deterministic so that repeated audits converge on a stable state. Adversaries routinely probe for misconfigurations of this control when establishing persistence on laboratory infrastructure. Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment. Adversaries routinely probe for misconfigurations of this control when establishing persistence on laboratory infrastructure.

**Requirement.** Prefer explicit values over relying on compiled-in defaults, which may vary between distributions. The host shall maintain the configuration described in this control at all times, and the setup auditor shall treat any deviation as reportable. Operational experience shows that small deviations here cascade into larger exposure during incident response.

**Implementation guidance.** Prefer explicit values over relying on compiled-in defaults, which may vary between distributions. Operators should prefer configuration that is idempotent so that re-running the auditor produces no further changes. Prefer explicit values over relying on compiled-in defaults, which may vary between distributions. Coordinate with the accounts team before altering anything that affects service-account behavior. Changes should be staged in a non-production environment and validated against the verification procedure below. Changes should be staged in a non-production environment and validated against the verification procedure below. Coordinate with the accounts team before altering anything that affects service-account behavior.

**Verification.** The verifier records the before and after state for inclusion in the assessment package. Evidence is the auditor's proposed patch set; a compliant host yields an empty set for this control. Verification is performed by the setup auditor, which compares the host state to the normalized policy expectation. Automated property checks generate varied host states to confirm the control behaves consistently. Evidence is the auditor's proposed patch set; a compliant host yields an empty set for this control.

**References.** Lab Operations Runbook ROB-3; Baseline Configuration Guide BCG-6.5; Baseline Configuration Guide BCG-4.7

**Revision history.**
- 2025-08: editorial revision to LG-007; clarified scope and wording.
- 2022-01: editorial revision to LG-007; clarified scope and wording.


### LG-008 — Centralized banner presentation

**Domain:** Logging and Telemetry  **Severity:** Critical  **Applies to:** shared interactive hosts

**Rationale.** Adversaries routinely probe for misconfigurations of this control when establishing persistence on laboratory infrastructure. Adversaries routinely probe for misconfigurations of this control when establishing persistence on laboratory infrastructure. Consistent enforcement reduces the mean time to detect anomalous access across the estate. The control supports reproducible builds of the host baseline and simplifies forensic comparison. Consistent enforcement reduces the mean time to detect anomalous access across the estate.

**Requirement.** Changes should be staged in a non-production environment and validated against the verification procedure below. The host shall maintain the configuration described in this control at all times, and the setup auditor shall treat any deviation as reportable. The control supports reproducible builds of the host baseline and simplifies forensic comparison.

**Implementation guidance.** Operators should prefer configuration that is idempotent so that re-running the auditor produces no further changes. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. Document any approved deviation in the exceptions register with a scheduled review date. Coordinate with the accounts team before altering anything that affects service-account behavior. Coordinate with the accounts team before altering anything that affects service-account behavior. Retain the prior configuration so that a rollback can be performed without rebuilding the host. Coordinate with the accounts team before altering anything that affects service-account behavior. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies.

**Verification.** Assessors may re-run the audit after applying patches to confirm the host has converged. Verification is performed by the setup auditor, which compares the host state to the normalized policy expectation. Assessors may re-run the audit after applying patches to confirm the host has converged.

**References.** Baseline Configuration Guide BCG-3.4; Vendor hardening note VHN-8-1; Governing Security Policy GSP-2024 §3.5

**Revision history.**
- 2025-12: editorial revision to LG-008; clarified scope and wording.
- 2023-10: editorial revision to LG-008; clarified scope and wording.
- 2022-05: editorial revision to LG-008; clarified scope and wording.
- 2024-12: editorial revision to LG-008; clarified scope and wording.


### LG-009 — Baseline session timeout

**Domain:** Logging and Telemetry  **Severity:** Low  **Applies to:** shared interactive hosts

**Rationale.** Inconsistent application of this requirement across hosts complicates evidence collection and weakens attestations. Consistent enforcement reduces the mean time to detect anomalous access across the estate. Consistent enforcement reduces the mean time to detect anomalous access across the estate.

**Requirement.** Coordinate with the accounts team before altering anything that affects service-account behavior. The host shall maintain the configuration described in this control at all times, and the setup auditor shall treat any deviation as reportable. The control supports reproducible builds of the host baseline and simplifies forensic comparison.

**Implementation guidance.** Prefer explicit values over relying on compiled-in defaults, which may vary between distributions. Retain the prior configuration so that a rollback can be performed without rebuilding the host. Operators should prefer configuration that is idempotent so that re-running the auditor produces no further changes. Retain the prior configuration so that a rollback can be performed without rebuilding the host. Retain the prior configuration so that a rollback can be performed without rebuilding the host.

**Verification.** Automated property checks generate varied host states to confirm the control behaves consistently. Assessors may re-run the audit after applying patches to confirm the host has converged. The verifier records the before and after state for inclusion in the assessment package.

**References.** Prior assessment finding AF-4; Governing Security Policy GSP-2024 §7.7

**Revision history.**
- 2022-07: editorial revision to LG-009; clarified scope and wording.
- 2022-02: editorial revision to LG-009; clarified scope and wording.
- 2025-11: editorial revision to LG-009; clarified scope and wording.
- 2023-05: editorial revision to LG-009; clarified scope and wording.


### LG-010 — Monitored umask default

**Domain:** Logging and Telemetry  **Severity:** Moderate  **Applies to:** service-account-bearing hosts

**Rationale.** The control supports reproducible builds of the host baseline and simplifies forensic comparison. Inconsistent application of this requirement across hosts complicates evidence collection and weakens attestations. Consistent enforcement reduces the mean time to detect anomalous access across the estate. Inconsistent application of this requirement across hosts complicates evidence collection and weakens attestations. Inconsistent application of this requirement across hosts complicates evidence collection and weakens attestations.

**Requirement.** Changes should be staged in a non-production environment and validated against the verification procedure below. The host shall maintain the configuration described in this control at all times, and the setup auditor shall treat any deviation as reportable. Operational experience shows that small deviations here cascade into larger exposure during incident response.

**Implementation guidance.** Coordinate with the accounts team before altering anything that affects service-account behavior. Prefer explicit values over relying on compiled-in defaults, which may vary between distributions. Operators should prefer configuration that is idempotent so that re-running the auditor produces no further changes. Operators should prefer configuration that is idempotent so that re-running the auditor produces no further changes. Document any approved deviation in the exceptions register with a scheduled review date. Document any approved deviation in the exceptions register with a scheduled review date.

**Verification.** Evidence is the auditor's proposed patch set; a compliant host yields an empty set for this control. Automated property checks generate varied host states to confirm the control behaves consistently. Automated property checks generate varied host states to confirm the control behaves consistently. Verification is performed by the setup auditor, which compares the host state to the normalized policy expectation. Assessors may re-run the audit after applying patches to confirm the host has converged.

**References.** Prior assessment finding AF-6; Vendor hardening note VHN-6-3; Prior assessment finding AF-8; Baseline Configuration Guide BCG-9.3

**Revision history.**
- 2024-01: editorial revision to LG-010; clarified scope and wording.
- 2022-08: editorial revision to LG-010; clarified scope and wording.
- 2024-01: editorial revision to LG-010; clarified scope and wording.


### LG-011 — Mandatory log forwarding

**Domain:** Logging and Telemetry  **Severity:** Low  **Applies to:** shared interactive hosts

**Rationale.** The control exists to keep remediation deterministic so that repeated audits converge on a stable state. The control exists to keep remediation deterministic so that repeated audits converge on a stable state. The control supports reproducible builds of the host baseline and simplifies forensic comparison. This requirement aligns the gateway with the principle of least privilege mandated by the governing security policy. Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment.

**Requirement.** Coordinate with the accounts team before altering anything that affects service-account behavior. The host shall maintain the configuration described in this control at all times, and the setup auditor shall treat any deviation as reportable. Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment.

**Implementation guidance.** Prefer explicit values over relying on compiled-in defaults, which may vary between distributions. Prefer explicit values over relying on compiled-in defaults, which may vary between distributions. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. Changes should be staged in a non-production environment and validated against the verification procedure below. Document any approved deviation in the exceptions register with a scheduled review date.

**Verification.** Evidence is the auditor's proposed patch set; a compliant host yields an empty set for this control. Assessors may re-run the audit after applying patches to confirm the host has converged. Evidence is the auditor's proposed patch set; a compliant host yields an empty set for this control. Verification is performed by the setup auditor, which compares the host state to the normalized policy expectation.

**References.** Vendor hardening note VHN-4-4; Prior assessment finding AF-7

**Revision history.**
- 2022-12: editorial revision to LG-011; clarified scope and wording.
- 2024-09: editorial revision to LG-011; clarified scope and wording.
- 2025-09: editorial revision to LG-011; clarified scope and wording.
- 2025-01: editorial revision to LG-011; clarified scope and wording.


### LG-012 — Mandatory module loading

**Domain:** Logging and Telemetry  **Severity:** Moderate  **Applies to:** tier-1 laboratory hosts

**Rationale.** The control supports reproducible builds of the host baseline and simplifies forensic comparison. Adversaries routinely probe for misconfigurations of this control when establishing persistence on laboratory infrastructure. Inconsistent application of this requirement across hosts complicates evidence collection and weakens attestations.

**Requirement.** Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. The host shall maintain the configuration described in this control at all times, and the setup auditor shall treat any deviation as reportable. Consistent enforcement reduces the mean time to detect anomalous access across the estate.

**Implementation guidance.** Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. Prefer explicit values over relying on compiled-in defaults, which may vary between distributions. Changes should be staged in a non-production environment and validated against the verification procedure below. Changes should be staged in a non-production environment and validated against the verification procedure below. Retain the prior configuration so that a rollback can be performed without rebuilding the host. Document any approved deviation in the exceptions register with a scheduled review date. Coordinate with the accounts team before altering anything that affects service-account behavior.

**Verification.** Assessors may re-run the audit after applying patches to confirm the host has converged. Assessors may re-run the audit after applying patches to confirm the host has converged. Automated property checks generate varied host states to confirm the control behaves consistently.

**References.** Prior assessment finding AF-5; Baseline Configuration Guide BCG-2.5; Lab Operations Runbook ROB-6; Lab Operations Runbook ROB-1

**Revision history.**
- 2022-06: editorial revision to LG-012; clarified scope and wording.
- 2022-09: editorial revision to LG-012; clarified scope and wording.
- 2025-10: editorial revision to LG-012; clarified scope and wording.
- 2025-11: editorial revision to LG-012; clarified scope and wording.


## 8. Maintenance

Inconsistent application of this requirement across hosts complicates evidence collection and weakens attestations. This requirement aligns the gateway with the principle of least privilege mandated by the governing security policy. Inconsistent application of this requirement across hosts complicates evidence collection and weakens attestations. This requirement aligns the gateway with the principle of least privilege mandated by the governing security policy. Inconsistent application of this requirement across hosts complicates evidence collection and weakens attestations. Consistent enforcement reduces the mean time to detect anomalous access across the estate.


Retain the prior configuration so that a rollback can be performed without rebuilding the host. Changes should be staged in a non-production environment and validated against the verification procedure below. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. Document any approved deviation in the exceptions register with a scheduled review date.


### MA-001 — Restricted module loading

**Domain:** Maintenance  **Severity:** High  **Applies to:** gateway and bastion hosts

**Rationale.** Operational experience shows that small deviations here cascade into larger exposure during incident response. Adversaries routinely probe for misconfigurations of this control when establishing persistence on laboratory infrastructure. This requirement aligns the gateway with the principle of least privilege mandated by the governing security policy. The control exists to keep remediation deterministic so that repeated audits converge on a stable state. Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment.

**Requirement.** Changes should be staged in a non-production environment and validated against the verification procedure below. The host shall maintain the configuration described in this control at all times, and the setup auditor shall treat any deviation as reportable. Consistent enforcement reduces the mean time to detect anomalous access across the estate.

**Implementation guidance.** Retain the prior configuration so that a rollback can be performed without rebuilding the host. Document any approved deviation in the exceptions register with a scheduled review date. Changes should be staged in a non-production environment and validated against the verification procedure below. Coordinate with the accounts team before altering anything that affects service-account behavior. Coordinate with the accounts team before altering anything that affects service-account behavior.

**Verification.** Automated property checks generate varied host states to confirm the control behaves consistently. Verification is performed by the setup auditor, which compares the host state to the normalized policy expectation. The verifier records the before and after state for inclusion in the assessment package. Verification is performed by the setup auditor, which compares the host state to the normalized policy expectation.

**References.** Lab Operations Runbook ROB-9; Baseline Configuration Guide BCG-9.6; Baseline Configuration Guide BCG-1.7; Lab Operations Runbook ROB-2

**Revision history.**
- 2025-12: editorial revision to MA-001; clarified scope and wording.
- 2024-09: editorial revision to MA-001; clarified scope and wording.


### MA-002 — Controlled banner presentation

**Domain:** Maintenance  **Severity:** Critical  **Applies to:** service-account-bearing hosts

**Rationale.** The control supports reproducible builds of the host baseline and simplifies forensic comparison. Operational experience shows that small deviations here cascade into larger exposure during incident response. This requirement aligns the gateway with the principle of least privilege mandated by the governing security policy.

**Requirement.** Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. The host shall maintain the configuration described in this control at all times, and the setup auditor shall treat any deviation as reportable. Consistent enforcement reduces the mean time to detect anomalous access across the estate.

**Implementation guidance.** Coordinate with the accounts team before altering anything that affects service-account behavior. Prefer explicit values over relying on compiled-in defaults, which may vary between distributions. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. Operators should prefer configuration that is idempotent so that re-running the auditor produces no further changes. Document any approved deviation in the exceptions register with a scheduled review date. Changes should be staged in a non-production environment and validated against the verification procedure below.

**Verification.** Automated property checks generate varied host states to confirm the control behaves consistently. Automated property checks generate varied host states to confirm the control behaves consistently. Verification is performed by the setup auditor, which compares the host state to the normalized policy expectation.

**References.** Governing Security Policy GSP-2024 §3.5; Vendor hardening note VHN-6-2; Prior assessment finding AF-1

**Revision history.**
- 2025-02: editorial revision to MA-002; clarified scope and wording.
- 2025-01: editorial revision to MA-002; clarified scope and wording.
- 2024-10: editorial revision to MA-002; clarified scope and wording.
- 2022-09: editorial revision to MA-002; clarified scope and wording.


### MA-003 — Baseline umask default

**Domain:** Maintenance  **Severity:** Moderate  **Applies to:** service-account-bearing hosts

**Rationale.** This requirement aligns the gateway with the principle of least privilege mandated by the governing security policy. Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment. Consistent enforcement reduces the mean time to detect anomalous access across the estate. Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment.

**Requirement.** Operators should prefer configuration that is idempotent so that re-running the auditor produces no further changes. The host shall maintain the configuration described in this control at all times, and the setup auditor shall treat any deviation as reportable. The control supports reproducible builds of the host baseline and simplifies forensic comparison.

**Implementation guidance.** Changes should be staged in a non-production environment and validated against the verification procedure below. Changes should be staged in a non-production environment and validated against the verification procedure below. Document any approved deviation in the exceptions register with a scheduled review date. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. Coordinate with the accounts team before altering anything that affects service-account behavior. Changes should be staged in a non-production environment and validated against the verification procedure below. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. Document any approved deviation in the exceptions register with a scheduled review date.

**Verification.** The verifier records the before and after state for inclusion in the assessment package. Verification is performed by the setup auditor, which compares the host state to the normalized policy expectation. Assessors may re-run the audit after applying patches to confirm the host has converged.

**References.** Baseline Configuration Guide BCG-7.9; Governing Security Policy GSP-2024 §1.1; Baseline Configuration Guide BCG-5.7

**Revision history.**
- 2024-10: editorial revision to MA-003; clarified scope and wording.
- 2023-08: editorial revision to MA-003; clarified scope and wording.


### MA-004 — Monitored boot integrity

**Domain:** Maintenance  **Severity:** Low  **Applies to:** tier-1 laboratory hosts

**Rationale.** Operational experience shows that small deviations here cascade into larger exposure during incident response. Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment. This requirement aligns the gateway with the principle of least privilege mandated by the governing security policy. Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment. Consistent enforcement reduces the mean time to detect anomalous access across the estate.

**Requirement.** Coordinate with the accounts team before altering anything that affects service-account behavior. The host shall maintain the configuration described in this control at all times, and the setup auditor shall treat any deviation as reportable. The control supports reproducible builds of the host baseline and simplifies forensic comparison.

**Implementation guidance.** Prefer explicit values over relying on compiled-in defaults, which may vary between distributions. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. Changes should be staged in a non-production environment and validated against the verification procedure below. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. Prefer explicit values over relying on compiled-in defaults, which may vary between distributions.

**Verification.** Automated property checks generate varied host states to confirm the control behaves consistently. Evidence is the auditor's proposed patch set; a compliant host yields an empty set for this control. Verification is performed by the setup auditor, which compares the host state to the normalized policy expectation. The verifier records the before and after state for inclusion in the assessment package. The verifier records the before and after state for inclusion in the assessment package.

**References.** Lab Operations Runbook ROB-9; Lab Operations Runbook ROB-6; Baseline Configuration Guide BCG-8.7; Lab Operations Runbook ROB-4

**Revision history.**
- 2025-02: editorial revision to MA-004; clarified scope and wording.
- 2023-11: editorial revision to MA-004; clarified scope and wording.
- 2024-05: editorial revision to MA-004; clarified scope and wording.


### MA-005 — Approved package provenance

**Domain:** Maintenance  **Severity:** Critical  **Applies to:** all managed hosts

**Rationale.** Operational experience shows that small deviations here cascade into larger exposure during incident response. The control supports reproducible builds of the host baseline and simplifies forensic comparison. Operational experience shows that small deviations here cascade into larger exposure during incident response.

**Requirement.** Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. The host shall maintain the configuration described in this control at all times, and the setup auditor shall treat any deviation as reportable. The control exists to keep remediation deterministic so that repeated audits converge on a stable state.

**Implementation guidance.** Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. Document any approved deviation in the exceptions register with a scheduled review date. Document any approved deviation in the exceptions register with a scheduled review date.

**Verification.** Assessors may re-run the audit after applying patches to confirm the host has converged. Automated property checks generate varied host states to confirm the control behaves consistently. The verifier records the before and after state for inclusion in the assessment package. The verifier records the before and after state for inclusion in the assessment package. The verifier records the before and after state for inclusion in the assessment package.

**References.** Baseline Configuration Guide BCG-8.1; Vendor hardening note VHN-8-8; Vendor hardening note VHN-7-9

**Revision history.**
- 2025-01: editorial revision to MA-005; clarified scope and wording.
- 2025-01: editorial revision to MA-005; clarified scope and wording.


### MA-006 — Hardened session timeout

**Domain:** Maintenance  **Severity:** High  **Applies to:** gateway and bastion hosts

**Rationale.** Adversaries routinely probe for misconfigurations of this control when establishing persistence on laboratory infrastructure. The control exists to keep remediation deterministic so that repeated audits converge on a stable state. Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment. The control exists to keep remediation deterministic so that repeated audits converge on a stable state. Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment.

**Requirement.** Prefer explicit values over relying on compiled-in defaults, which may vary between distributions. The host shall maintain the configuration described in this control at all times, and the setup auditor shall treat any deviation as reportable. Operational experience shows that small deviations here cascade into larger exposure during incident response.

**Implementation guidance.** Retain the prior configuration so that a rollback can be performed without rebuilding the host. Document any approved deviation in the exceptions register with a scheduled review date. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. Coordinate with the accounts team before altering anything that affects service-account behavior. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner.

**Verification.** Evidence is the auditor's proposed patch set; a compliant host yields an empty set for this control. Assessors may re-run the audit after applying patches to confirm the host has converged. Assessors may re-run the audit after applying patches to confirm the host has converged. The verifier records the before and after state for inclusion in the assessment package. Assessors may re-run the audit after applying patches to confirm the host has converged.

**References.** Prior assessment finding AF-2; Prior assessment finding AF-4; Vendor hardening note VHN-5-4; Baseline Configuration Guide BCG-3.7

**Revision history.**
- 2022-06: editorial revision to MA-006; clarified scope and wording.
- 2022-12: editorial revision to MA-006; clarified scope and wording.
- 2023-03: editorial revision to MA-006; clarified scope and wording.


### MA-007 — Approved interface configuration

**Domain:** Maintenance  **Severity:** Low  **Applies to:** service-account-bearing hosts

**Rationale.** Operational experience shows that small deviations here cascade into larger exposure during incident response. This requirement aligns the gateway with the principle of least privilege mandated by the governing security policy. Consistent enforcement reduces the mean time to detect anomalous access across the estate.

**Requirement.** When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. The host shall maintain the configuration described in this control at all times, and the setup auditor shall treat any deviation as reportable. Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment.

**Implementation guidance.** Changes should be staged in a non-production environment and validated against the verification procedure below. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. Document any approved deviation in the exceptions register with a scheduled review date. Changes should be staged in a non-production environment and validated against the verification procedure below. Operators should prefer configuration that is idempotent so that re-running the auditor produces no further changes. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. Changes should be staged in a non-production environment and validated against the verification procedure below.

**Verification.** Automated property checks generate varied host states to confirm the control behaves consistently. Evidence is the auditor's proposed patch set; a compliant host yields an empty set for this control. The verifier records the before and after state for inclusion in the assessment package. Evidence is the auditor's proposed patch set; a compliant host yields an empty set for this control.

**References.** Baseline Configuration Guide BCG-2.6; Governing Security Policy GSP-2024 §5.7

**Revision history.**
- 2024-06: editorial revision to MA-007; clarified scope and wording.
- 2023-09: editorial revision to MA-007; clarified scope and wording.
- 2023-09: editorial revision to MA-007; clarified scope and wording.


### MA-008 — Restricted log forwarding

**Domain:** Maintenance  **Severity:** Critical  **Applies to:** shared interactive hosts

**Rationale.** The control exists to keep remediation deterministic so that repeated audits converge on a stable state. Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment. Operational experience shows that small deviations here cascade into larger exposure during incident response. Consistent enforcement reduces the mean time to detect anomalous access across the estate. This requirement aligns the gateway with the principle of least privilege mandated by the governing security policy.

**Requirement.** Changes should be staged in a non-production environment and validated against the verification procedure below. The host shall maintain the configuration described in this control at all times, and the setup auditor shall treat any deviation as reportable. The control supports reproducible builds of the host baseline and simplifies forensic comparison.

**Implementation guidance.** Coordinate with the accounts team before altering anything that affects service-account behavior. Changes should be staged in a non-production environment and validated against the verification procedure below. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. Coordinate with the accounts team before altering anything that affects service-account behavior. Document any approved deviation in the exceptions register with a scheduled review date.

**Verification.** The verifier records the before and after state for inclusion in the assessment package. Assessors may re-run the audit after applying patches to confirm the host has converged. Assessors may re-run the audit after applying patches to confirm the host has converged.

**References.** Vendor hardening note VHN-6-2; Baseline Configuration Guide BCG-6.0; Prior assessment finding AF-3

**Revision history.**
- 2024-02: editorial revision to MA-008; clarified scope and wording.
- 2024-07: editorial revision to MA-008; clarified scope and wording.


### MA-009 — Mandatory interface configuration

**Domain:** Maintenance  **Severity:** High  **Applies to:** gateway and bastion hosts

**Rationale.** The control supports reproducible builds of the host baseline and simplifies forensic comparison. Consistent enforcement reduces the mean time to detect anomalous access across the estate. Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment.

**Requirement.** Operators should prefer configuration that is idempotent so that re-running the auditor produces no further changes. The host shall maintain the configuration described in this control at all times, and the setup auditor shall treat any deviation as reportable. Adversaries routinely probe for misconfigurations of this control when establishing persistence on laboratory infrastructure.

**Implementation guidance.** Prefer explicit values over relying on compiled-in defaults, which may vary between distributions. Document any approved deviation in the exceptions register with a scheduled review date. Coordinate with the accounts team before altering anything that affects service-account behavior. Operators should prefer configuration that is idempotent so that re-running the auditor produces no further changes. Changes should be staged in a non-production environment and validated against the verification procedure below. Document any approved deviation in the exceptions register with a scheduled review date. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies.

**Verification.** Verification is performed by the setup auditor, which compares the host state to the normalized policy expectation. Assessors may re-run the audit after applying patches to confirm the host has converged. Automated property checks generate varied host states to confirm the control behaves consistently. Verification is performed by the setup auditor, which compares the host state to the normalized policy expectation. Evidence is the auditor's proposed patch set; a compliant host yields an empty set for this control.

**References.** Vendor hardening note VHN-2-0; Prior assessment finding AF-2

**Revision history.**
- 2022-10: editorial revision to MA-009; clarified scope and wording.
- 2024-12: editorial revision to MA-009; clarified scope and wording.
- 2023-01: editorial revision to MA-009; clarified scope and wording.
- 2024-02: editorial revision to MA-009; clarified scope and wording.


### MA-010 — Approved module loading

**Domain:** Maintenance  **Severity:** High  **Applies to:** tier-1 laboratory hosts

**Rationale.** Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment. The control supports reproducible builds of the host baseline and simplifies forensic comparison. The control supports reproducible builds of the host baseline and simplifies forensic comparison. Adversaries routinely probe for misconfigurations of this control when establishing persistence on laboratory infrastructure.

**Requirement.** Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. The host shall maintain the configuration described in this control at all times, and the setup auditor shall treat any deviation as reportable. Adversaries routinely probe for misconfigurations of this control when establishing persistence on laboratory infrastructure.

**Implementation guidance.** When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. Changes should be staged in a non-production environment and validated against the verification procedure below. Coordinate with the accounts team before altering anything that affects service-account behavior. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. Coordinate with the accounts team before altering anything that affects service-account behavior. Coordinate with the accounts team before altering anything that affects service-account behavior. Operators should prefer configuration that is idempotent so that re-running the auditor produces no further changes.

**Verification.** Automated property checks generate varied host states to confirm the control behaves consistently. Verification is performed by the setup auditor, which compares the host state to the normalized policy expectation. Automated property checks generate varied host states to confirm the control behaves consistently. Verification is performed by the setup auditor, which compares the host state to the normalized policy expectation. The verifier records the before and after state for inclusion in the assessment package.

**References.** Vendor hardening note VHN-4-0; Lab Operations Runbook ROB-7; Prior assessment finding AF-2; Lab Operations Runbook ROB-2

**Revision history.**
- 2023-09: editorial revision to MA-010; clarified scope and wording.
- 2024-01: editorial revision to MA-010; clarified scope and wording.


### MA-011 — Standard interface configuration

**Domain:** Maintenance  **Severity:** High  **Applies to:** shared interactive hosts

**Rationale.** This requirement aligns the gateway with the principle of least privilege mandated by the governing security policy. Adversaries routinely probe for misconfigurations of this control when establishing persistence on laboratory infrastructure. Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment. Operational experience shows that small deviations here cascade into larger exposure during incident response. Inconsistent application of this requirement across hosts complicates evidence collection and weakens attestations.

**Requirement.** Prefer explicit values over relying on compiled-in defaults, which may vary between distributions. The host shall maintain the configuration described in this control at all times, and the setup auditor shall treat any deviation as reportable. Inconsistent application of this requirement across hosts complicates evidence collection and weakens attestations.

**Implementation guidance.** Coordinate with the accounts team before altering anything that affects service-account behavior. Document any approved deviation in the exceptions register with a scheduled review date. Prefer explicit values over relying on compiled-in defaults, which may vary between distributions. Operators should prefer configuration that is idempotent so that re-running the auditor produces no further changes. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. Coordinate with the accounts team before altering anything that affects service-account behavior.

**Verification.** Evidence is the auditor's proposed patch set; a compliant host yields an empty set for this control. Assessors may re-run the audit after applying patches to confirm the host has converged. Evidence is the auditor's proposed patch set; a compliant host yields an empty set for this control.

**References.** Lab Operations Runbook ROB-8; Vendor hardening note VHN-9-4; Governing Security Policy GSP-2024 §5.6

**Revision history.**
- 2025-12: editorial revision to MA-011; clarified scope and wording.
- 2024-08: editorial revision to MA-011; clarified scope and wording.
- 2022-04: editorial revision to MA-011; clarified scope and wording.
- 2022-11: editorial revision to MA-011; clarified scope and wording.


### MA-012 — Mandatory boot integrity

**Domain:** Maintenance  **Severity:** High  **Applies to:** tier-1 laboratory hosts

**Rationale.** Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment. Adversaries routinely probe for misconfigurations of this control when establishing persistence on laboratory infrastructure. Operational experience shows that small deviations here cascade into larger exposure during incident response. Consistent enforcement reduces the mean time to detect anomalous access across the estate. The control supports reproducible builds of the host baseline and simplifies forensic comparison.

**Requirement.** Operators should prefer configuration that is idempotent so that re-running the auditor produces no further changes. The host shall maintain the configuration described in this control at all times, and the setup auditor shall treat any deviation as reportable. Adversaries routinely probe for misconfigurations of this control when establishing persistence on laboratory infrastructure.

**Implementation guidance.** Operators should prefer configuration that is idempotent so that re-running the auditor produces no further changes. Document any approved deviation in the exceptions register with a scheduled review date. Retain the prior configuration so that a rollback can be performed without rebuilding the host. Document any approved deviation in the exceptions register with a scheduled review date. Document any approved deviation in the exceptions register with a scheduled review date. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies.

**Verification.** Evidence is the auditor's proposed patch set; a compliant host yields an empty set for this control. Assessors may re-run the audit after applying patches to confirm the host has converged. Automated property checks generate varied host states to confirm the control behaves consistently. Verification is performed by the setup auditor, which compares the host state to the normalized policy expectation. Assessors may re-run the audit after applying patches to confirm the host has converged.

**References.** Governing Security Policy GSP-2024 §1.3; Vendor hardening note VHN-4-8; Governing Security Policy GSP-2024 §9.4; Vendor hardening note VHN-3-0

**Revision history.**
- 2022-08: editorial revision to MA-012; clarified scope and wording.
- 2025-11: editorial revision to MA-012; clarified scope and wording.
- 2023-03: editorial revision to MA-012; clarified scope and wording.
- 2025-09: editorial revision to MA-012; clarified scope and wording.


### MA-013 — Verified session timeout

**Domain:** Maintenance  **Severity:** High  **Applies to:** tier-1 laboratory hosts

**Rationale.** Consistent enforcement reduces the mean time to detect anomalous access across the estate. Inconsistent application of this requirement across hosts complicates evidence collection and weakens attestations. Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment. Inconsistent application of this requirement across hosts complicates evidence collection and weakens attestations.

**Requirement.** Prefer explicit values over relying on compiled-in defaults, which may vary between distributions. The host shall maintain the configuration described in this control at all times, and the setup auditor shall treat any deviation as reportable. Operational experience shows that small deviations here cascade into larger exposure during incident response.

**Implementation guidance.** Retain the prior configuration so that a rollback can be performed without rebuilding the host. Prefer explicit values over relying on compiled-in defaults, which may vary between distributions. Changes should be staged in a non-production environment and validated against the verification procedure below. Document any approved deviation in the exceptions register with a scheduled review date. Operators should prefer configuration that is idempotent so that re-running the auditor produces no further changes. Operators should prefer configuration that is idempotent so that re-running the auditor produces no further changes. Changes should be staged in a non-production environment and validated against the verification procedure below. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies.

**Verification.** Assessors may re-run the audit after applying patches to confirm the host has converged. The verifier records the before and after state for inclusion in the assessment package. Assessors may re-run the audit after applying patches to confirm the host has converged. Evidence is the auditor's proposed patch set; a compliant host yields an empty set for this control. The verifier records the before and after state for inclusion in the assessment package.

**References.** Lab Operations Runbook ROB-5; Vendor hardening note VHN-6-5; Vendor hardening note VHN-4-3; Lab Operations Runbook ROB-2

**Revision history.**
- 2022-01: editorial revision to MA-013; clarified scope and wording.
- 2023-02: editorial revision to MA-013; clarified scope and wording.
- 2022-04: editorial revision to MA-013; clarified scope and wording.


### MA-014 — Verified console access

**Domain:** Maintenance  **Severity:** Moderate  **Applies to:** shared interactive hosts

**Rationale.** Operational experience shows that small deviations here cascade into larger exposure during incident response. Operational experience shows that small deviations here cascade into larger exposure during incident response. Operational experience shows that small deviations here cascade into larger exposure during incident response. Consistent enforcement reduces the mean time to detect anomalous access across the estate. Inconsistent application of this requirement across hosts complicates evidence collection and weakens attestations.

**Requirement.** Retain the prior configuration so that a rollback can be performed without rebuilding the host. The host shall maintain the configuration described in this control at all times, and the setup auditor shall treat any deviation as reportable. Consistent enforcement reduces the mean time to detect anomalous access across the estate.

**Implementation guidance.** When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. Prefer explicit values over relying on compiled-in defaults, which may vary between distributions. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. Prefer explicit values over relying on compiled-in defaults, which may vary between distributions.

**Verification.** Verification is performed by the setup auditor, which compares the host state to the normalized policy expectation. Verification is performed by the setup auditor, which compares the host state to the normalized policy expectation. Automated property checks generate varied host states to confirm the control behaves consistently. Verification is performed by the setup auditor, which compares the host state to the normalized policy expectation. Automated property checks generate varied host states to confirm the control behaves consistently.

**References.** Baseline Configuration Guide BCG-7.9; Baseline Configuration Guide BCG-1.1

**Revision history.**
- 2024-04: editorial revision to MA-014; clarified scope and wording.
- 2024-06: editorial revision to MA-014; clarified scope and wording.


## 9. Network Controls

Inconsistent application of this requirement across hosts complicates evidence collection and weakens attestations. This requirement aligns the gateway with the principle of least privilege mandated by the governing security policy. The control exists to keep remediation deterministic so that repeated audits converge on a stable state. Adversaries routinely probe for misconfigurations of this control when establishing persistence on laboratory infrastructure. This requirement aligns the gateway with the principle of least privilege mandated by the governing security policy.


Prefer explicit values over relying on compiled-in defaults, which may vary between distributions. Document any approved deviation in the exceptions register with a scheduled review date. Coordinate with the accounts team before altering anything that affects service-account behavior. Operators should prefer configuration that is idempotent so that re-running the auditor produces no further changes.


### NW-001 — Centralized kernel parameter

**Domain:** Network Controls  **Severity:** High  **Applies to:** gateway and bastion hosts

**Rationale.** Inconsistent application of this requirement across hosts complicates evidence collection and weakens attestations. Adversaries routinely probe for misconfigurations of this control when establishing persistence on laboratory infrastructure. Adversaries routinely probe for misconfigurations of this control when establishing persistence on laboratory infrastructure.

**Requirement.** When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. The host shall maintain the configuration described in this control at all times, and the setup auditor shall treat any deviation as reportable. Operational experience shows that small deviations here cascade into larger exposure during incident response.

**Implementation guidance.** When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. Changes should be staged in a non-production environment and validated against the verification procedure below. Retain the prior configuration so that a rollback can be performed without rebuilding the host. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. Coordinate with the accounts team before altering anything that affects service-account behavior. Coordinate with the accounts team before altering anything that affects service-account behavior.

**Verification.** Assessors may re-run the audit after applying patches to confirm the host has converged. The verifier records the before and after state for inclusion in the assessment package. Assessors may re-run the audit after applying patches to confirm the host has converged.

**References.** Vendor hardening note VHN-7-9; Vendor hardening note VHN-2-3

**Revision history.**
- 2023-09: editorial revision to NW-001; clarified scope and wording.
- 2025-02: editorial revision to NW-001; clarified scope and wording.


### NW-002 — Restricted log forwarding

**Domain:** Network Controls  **Severity:** Moderate  **Applies to:** service-account-bearing hosts

**Rationale.** Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment. The control supports reproducible builds of the host baseline and simplifies forensic comparison. The control exists to keep remediation deterministic so that repeated audits converge on a stable state. Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment. Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment.

**Requirement.** Retain the prior configuration so that a rollback can be performed without rebuilding the host. The host shall maintain the configuration described in this control at all times, and the setup auditor shall treat any deviation as reportable. Consistent enforcement reduces the mean time to detect anomalous access across the estate.

**Implementation guidance.** Coordinate with the accounts team before altering anything that affects service-account behavior. Document any approved deviation in the exceptions register with a scheduled review date. Changes should be staged in a non-production environment and validated against the verification procedure below. Prefer explicit values over relying on compiled-in defaults, which may vary between distributions. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. Operators should prefer configuration that is idempotent so that re-running the auditor produces no further changes. Document any approved deviation in the exceptions register with a scheduled review date.

**Verification.** Verification is performed by the setup auditor, which compares the host state to the normalized policy expectation. Verification is performed by the setup auditor, which compares the host state to the normalized policy expectation. Verification is performed by the setup auditor, which compares the host state to the normalized policy expectation. The verifier records the before and after state for inclusion in the assessment package. Evidence is the auditor's proposed patch set; a compliant host yields an empty set for this control.

**References.** Lab Operations Runbook ROB-2; Governing Security Policy GSP-2024 §6.3; Vendor hardening note VHN-4-7

**Revision history.**
- 2022-12: editorial revision to NW-002; clarified scope and wording.
- 2023-09: editorial revision to NW-002; clarified scope and wording.
- 2025-10: editorial revision to NW-002; clarified scope and wording.
- 2024-03: editorial revision to NW-002; clarified scope and wording.


### NW-003 — Controlled console access

**Domain:** Network Controls  **Severity:** Moderate  **Applies to:** tier-1 laboratory hosts

**Rationale.** Adversaries routinely probe for misconfigurations of this control when establishing persistence on laboratory infrastructure. Consistent enforcement reduces the mean time to detect anomalous access across the estate. Adversaries routinely probe for misconfigurations of this control when establishing persistence on laboratory infrastructure. Inconsistent application of this requirement across hosts complicates evidence collection and weakens attestations.

**Requirement.** Document any approved deviation in the exceptions register with a scheduled review date. The host shall maintain the configuration described in this control at all times, and the setup auditor shall treat any deviation as reportable. Operational experience shows that small deviations here cascade into larger exposure during incident response.

**Implementation guidance.** Prefer explicit values over relying on compiled-in defaults, which may vary between distributions. Changes should be staged in a non-production environment and validated against the verification procedure below. Document any approved deviation in the exceptions register with a scheduled review date. Operators should prefer configuration that is idempotent so that re-running the auditor produces no further changes. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. Document any approved deviation in the exceptions register with a scheduled review date. Retain the prior configuration so that a rollback can be performed without rebuilding the host.

**Verification.** Evidence is the auditor's proposed patch set; a compliant host yields an empty set for this control. Automated property checks generate varied host states to confirm the control behaves consistently. The verifier records the before and after state for inclusion in the assessment package. Verification is performed by the setup auditor, which compares the host state to the normalized policy expectation.

**References.** Baseline Configuration Guide BCG-3.8; Governing Security Policy GSP-2024 §6.6

**Revision history.**
- 2025-06: editorial revision to NW-003; clarified scope and wording.
- 2023-02: editorial revision to NW-003; clarified scope and wording.
- 2025-07: editorial revision to NW-003; clarified scope and wording.


### NW-004 — Baseline boot integrity

**Domain:** Network Controls  **Severity:** Critical  **Applies to:** shared interactive hosts

**Rationale.** The control supports reproducible builds of the host baseline and simplifies forensic comparison. Operational experience shows that small deviations here cascade into larger exposure during incident response. The control supports reproducible builds of the host baseline and simplifies forensic comparison.

**Requirement.** Operators should prefer configuration that is idempotent so that re-running the auditor produces no further changes. The host shall maintain the configuration described in this control at all times, and the setup auditor shall treat any deviation as reportable. Adversaries routinely probe for misconfigurations of this control when establishing persistence on laboratory infrastructure.

**Implementation guidance.** Prefer explicit values over relying on compiled-in defaults, which may vary between distributions. Document any approved deviation in the exceptions register with a scheduled review date. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. Coordinate with the accounts team before altering anything that affects service-account behavior. Prefer explicit values over relying on compiled-in defaults, which may vary between distributions. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies.

**Verification.** Verification is performed by the setup auditor, which compares the host state to the normalized policy expectation. Evidence is the auditor's proposed patch set; a compliant host yields an empty set for this control. The verifier records the before and after state for inclusion in the assessment package. Assessors may re-run the audit after applying patches to confirm the host has converged.

**References.** Governing Security Policy GSP-2024 §3.6; Governing Security Policy GSP-2024 §7.0

**Revision history.**
- 2022-08: editorial revision to NW-004; clarified scope and wording.
- 2025-05: editorial revision to NW-004; clarified scope and wording.
- 2022-09: editorial revision to NW-004; clarified scope and wording.
- 2024-07: editorial revision to NW-004; clarified scope and wording.


### NW-005 — Monitored umask default

**Domain:** Network Controls  **Severity:** Moderate  **Applies to:** gateway and bastion hosts

**Rationale.** Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment. Adversaries routinely probe for misconfigurations of this control when establishing persistence on laboratory infrastructure. The control exists to keep remediation deterministic so that repeated audits converge on a stable state. Operational experience shows that small deviations here cascade into larger exposure during incident response.

**Requirement.** Operators should prefer configuration that is idempotent so that re-running the auditor produces no further changes. The host shall maintain the configuration described in this control at all times, and the setup auditor shall treat any deviation as reportable. Operational experience shows that small deviations here cascade into larger exposure during incident response.

**Implementation guidance.** Prefer explicit values over relying on compiled-in defaults, which may vary between distributions. Retain the prior configuration so that a rollback can be performed without rebuilding the host. Operators should prefer configuration that is idempotent so that re-running the auditor produces no further changes. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. Retain the prior configuration so that a rollback can be performed without rebuilding the host. Retain the prior configuration so that a rollback can be performed without rebuilding the host. Operators should prefer configuration that is idempotent so that re-running the auditor produces no further changes. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies.

**Verification.** The verifier records the before and after state for inclusion in the assessment package. The verifier records the before and after state for inclusion in the assessment package. Verification is performed by the setup auditor, which compares the host state to the normalized policy expectation. Assessors may re-run the audit after applying patches to confirm the host has converged. Assessors may re-run the audit after applying patches to confirm the host has converged.

**References.** Prior assessment finding AF-2; Prior assessment finding AF-3; Baseline Configuration Guide BCG-6.1

**Revision history.**
- 2022-08: editorial revision to NW-005; clarified scope and wording.
- 2024-03: editorial revision to NW-005; clarified scope and wording.


### NW-006 — Standard credential rotation

**Domain:** Network Controls  **Severity:** Critical  **Applies to:** service-account-bearing hosts

**Rationale.** Inconsistent application of this requirement across hosts complicates evidence collection and weakens attestations. Operational experience shows that small deviations here cascade into larger exposure during incident response. Operational experience shows that small deviations here cascade into larger exposure during incident response. Consistent enforcement reduces the mean time to detect anomalous access across the estate.

**Requirement.** Changes should be staged in a non-production environment and validated against the verification procedure below. The host shall maintain the configuration described in this control at all times, and the setup auditor shall treat any deviation as reportable. The control supports reproducible builds of the host baseline and simplifies forensic comparison.

**Implementation guidance.** Operators should prefer configuration that is idempotent so that re-running the auditor produces no further changes. Changes should be staged in a non-production environment and validated against the verification procedure below. Retain the prior configuration so that a rollback can be performed without rebuilding the host. Operators should prefer configuration that is idempotent so that re-running the auditor produces no further changes. Prefer explicit values over relying on compiled-in defaults, which may vary between distributions.

**Verification.** Evidence is the auditor's proposed patch set; a compliant host yields an empty set for this control. The verifier records the before and after state for inclusion in the assessment package. Automated property checks generate varied host states to confirm the control behaves consistently. Evidence is the auditor's proposed patch set; a compliant host yields an empty set for this control. Evidence is the auditor's proposed patch set; a compliant host yields an empty set for this control.

**References.** Baseline Configuration Guide BCG-3.3; Vendor hardening note VHN-4-2; Lab Operations Runbook ROB-2; Lab Operations Runbook ROB-1

**Revision history.**
- 2025-02: editorial revision to NW-006; clarified scope and wording.
- 2025-04: editorial revision to NW-006; clarified scope and wording.
- 2025-03: editorial revision to NW-006; clarified scope and wording.
- 2025-10: editorial revision to NW-006; clarified scope and wording.


### NW-007 — Controlled time synchronization

**Domain:** Network Controls  **Severity:** Low  **Applies to:** gateway and bastion hosts

**Rationale.** This requirement aligns the gateway with the principle of least privilege mandated by the governing security policy. Consistent enforcement reduces the mean time to detect anomalous access across the estate. Adversaries routinely probe for misconfigurations of this control when establishing persistence on laboratory infrastructure. The control exists to keep remediation deterministic so that repeated audits converge on a stable state.

**Requirement.** Document any approved deviation in the exceptions register with a scheduled review date. The host shall maintain the configuration described in this control at all times, and the setup auditor shall treat any deviation as reportable. Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment.

**Implementation guidance.** When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. Prefer explicit values over relying on compiled-in defaults, which may vary between distributions. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. Coordinate with the accounts team before altering anything that affects service-account behavior. Operators should prefer configuration that is idempotent so that re-running the auditor produces no further changes. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. Retain the prior configuration so that a rollback can be performed without rebuilding the host. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner.

**Verification.** The verifier records the before and after state for inclusion in the assessment package. Automated property checks generate varied host states to confirm the control behaves consistently. Evidence is the auditor's proposed patch set; a compliant host yields an empty set for this control. The verifier records the before and after state for inclusion in the assessment package. Assessors may re-run the audit after applying patches to confirm the host has converged.

**References.** Vendor hardening note VHN-5-0; Governing Security Policy GSP-2024 §5.9; Governing Security Policy GSP-2024 §5.4; Vendor hardening note VHN-3-1

**Revision history.**
- 2023-08: editorial revision to NW-007; clarified scope and wording.
- 2024-12: editorial revision to NW-007; clarified scope and wording.
- 2023-10: editorial revision to NW-007; clarified scope and wording.
- 2024-10: editorial revision to NW-007; clarified scope and wording.


### NW-008 — Mandatory core dump handling

**Domain:** Network Controls  **Severity:** Low  **Applies to:** shared interactive hosts

**Rationale.** Operational experience shows that small deviations here cascade into larger exposure during incident response. Operational experience shows that small deviations here cascade into larger exposure during incident response. The control exists to keep remediation deterministic so that repeated audits converge on a stable state. Inconsistent application of this requirement across hosts complicates evidence collection and weakens attestations.

**Requirement.** Changes should be staged in a non-production environment and validated against the verification procedure below. The host shall maintain the configuration described in this control at all times, and the setup auditor shall treat any deviation as reportable. Inconsistent application of this requirement across hosts complicates evidence collection and weakens attestations.

**Implementation guidance.** Changes should be staged in a non-production environment and validated against the verification procedure below. Prefer explicit values over relying on compiled-in defaults, which may vary between distributions. Operators should prefer configuration that is idempotent so that re-running the auditor produces no further changes. Prefer explicit values over relying on compiled-in defaults, which may vary between distributions. Operators should prefer configuration that is idempotent so that re-running the auditor produces no further changes. Changes should be staged in a non-production environment and validated against the verification procedure below. Changes should be staged in a non-production environment and validated against the verification procedure below.

**Verification.** Evidence is the auditor's proposed patch set; a compliant host yields an empty set for this control. Evidence is the auditor's proposed patch set; a compliant host yields an empty set for this control. The verifier records the before and after state for inclusion in the assessment package.

**References.** Governing Security Policy GSP-2024 §5.9; Lab Operations Runbook ROB-7; Vendor hardening note VHN-6-6; Vendor hardening note VHN-5-3

**Revision history.**
- 2024-09: editorial revision to NW-008; clarified scope and wording.
- 2025-04: editorial revision to NW-008; clarified scope and wording.


### NW-009 — Mandatory package provenance

**Domain:** Network Controls  **Severity:** Low  **Applies to:** gateway and bastion hosts

**Rationale.** Operational experience shows that small deviations here cascade into larger exposure during incident response. The control exists to keep remediation deterministic so that repeated audits converge on a stable state. The control supports reproducible builds of the host baseline and simplifies forensic comparison.

**Requirement.** Coordinate with the accounts team before altering anything that affects service-account behavior. The host shall maintain the configuration described in this control at all times, and the setup auditor shall treat any deviation as reportable. Operational experience shows that small deviations here cascade into larger exposure during incident response.

**Implementation guidance.** Changes should be staged in a non-production environment and validated against the verification procedure below. Coordinate with the accounts team before altering anything that affects service-account behavior. Coordinate with the accounts team before altering anything that affects service-account behavior. Retain the prior configuration so that a rollback can be performed without rebuilding the host. Changes should be staged in a non-production environment and validated against the verification procedure below. Prefer explicit values over relying on compiled-in defaults, which may vary between distributions. Coordinate with the accounts team before altering anything that affects service-account behavior.

**Verification.** Verification is performed by the setup auditor, which compares the host state to the normalized policy expectation. The verifier records the before and after state for inclusion in the assessment package. Assessors may re-run the audit after applying patches to confirm the host has converged. Verification is performed by the setup auditor, which compares the host state to the normalized policy expectation.

**References.** Governing Security Policy GSP-2024 §7.2; Prior assessment finding AF-4; Baseline Configuration Guide BCG-8.7

**Revision history.**
- 2022-09: editorial revision to NW-009; clarified scope and wording.
- 2024-05: editorial revision to NW-009; clarified scope and wording.


### NW-010 — Approved module loading

**Domain:** Network Controls  **Severity:** Critical  **Applies to:** all managed hosts

**Rationale.** The control supports reproducible builds of the host baseline and simplifies forensic comparison. Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment. The control exists to keep remediation deterministic so that repeated audits converge on a stable state. Adversaries routinely probe for misconfigurations of this control when establishing persistence on laboratory infrastructure.

**Requirement.** Coordinate with the accounts team before altering anything that affects service-account behavior. The host shall maintain the configuration described in this control at all times, and the setup auditor shall treat any deviation as reportable. Operational experience shows that small deviations here cascade into larger exposure during incident response.

**Implementation guidance.** Retain the prior configuration so that a rollback can be performed without rebuilding the host. Operators should prefer configuration that is idempotent so that re-running the auditor produces no further changes. Prefer explicit values over relying on compiled-in defaults, which may vary between distributions. Retain the prior configuration so that a rollback can be performed without rebuilding the host. Operators should prefer configuration that is idempotent so that re-running the auditor produces no further changes. Document any approved deviation in the exceptions register with a scheduled review date.

**Verification.** Evidence is the auditor's proposed patch set; a compliant host yields an empty set for this control. Assessors may re-run the audit after applying patches to confirm the host has converged. Verification is performed by the setup auditor, which compares the host state to the normalized policy expectation. Assessors may re-run the audit after applying patches to confirm the host has converged.

**References.** Prior assessment finding AF-6; Vendor hardening note VHN-1-9; Lab Operations Runbook ROB-8; Vendor hardening note VHN-7-8

**Revision history.**
- 2024-10: editorial revision to NW-010; clarified scope and wording.
- 2022-03: editorial revision to NW-010; clarified scope and wording.


### NW-011 — Restricted log forwarding

**Domain:** Network Controls  **Severity:** Low  **Applies to:** shared interactive hosts

**Rationale.** The control supports reproducible builds of the host baseline and simplifies forensic comparison. Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment. The control supports reproducible builds of the host baseline and simplifies forensic comparison. Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment. This requirement aligns the gateway with the principle of least privilege mandated by the governing security policy.

**Requirement.** When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. The host shall maintain the configuration described in this control at all times, and the setup auditor shall treat any deviation as reportable. The control exists to keep remediation deterministic so that repeated audits converge on a stable state.

**Implementation guidance.** Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. Document any approved deviation in the exceptions register with a scheduled review date. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies.

**Verification.** Verification is performed by the setup auditor, which compares the host state to the normalized policy expectation. Verification is performed by the setup auditor, which compares the host state to the normalized policy expectation. The verifier records the before and after state for inclusion in the assessment package.

**References.** Baseline Configuration Guide BCG-9.9; Prior assessment finding AF-1; Governing Security Policy GSP-2024 §3.3; Prior assessment finding AF-1

**Revision history.**
- 2024-09: editorial revision to NW-011; clarified scope and wording.
- 2024-01: editorial revision to NW-011; clarified scope and wording.
- 2022-01: editorial revision to NW-011; clarified scope and wording.
- 2022-12: editorial revision to NW-011; clarified scope and wording.


### NW-012 — Controlled module loading

**Domain:** Network Controls  **Severity:** Low  **Applies to:** all managed hosts

**Rationale.** Consistent enforcement reduces the mean time to detect anomalous access across the estate. Consistent enforcement reduces the mean time to detect anomalous access across the estate. Inconsistent application of this requirement across hosts complicates evidence collection and weakens attestations. The control exists to keep remediation deterministic so that repeated audits converge on a stable state. Operational experience shows that small deviations here cascade into larger exposure during incident response.

**Requirement.** Changes should be staged in a non-production environment and validated against the verification procedure below. The host shall maintain the configuration described in this control at all times, and the setup auditor shall treat any deviation as reportable. Consistent enforcement reduces the mean time to detect anomalous access across the estate.

**Implementation guidance.** Changes should be staged in a non-production environment and validated against the verification procedure below. Operators should prefer configuration that is idempotent so that re-running the auditor produces no further changes. Operators should prefer configuration that is idempotent so that re-running the auditor produces no further changes. Retain the prior configuration so that a rollback can be performed without rebuilding the host. Retain the prior configuration so that a rollback can be performed without rebuilding the host.

**Verification.** Assessors may re-run the audit after applying patches to confirm the host has converged. Assessors may re-run the audit after applying patches to confirm the host has converged. Automated property checks generate varied host states to confirm the control behaves consistently.

**References.** Vendor hardening note VHN-4-8; Lab Operations Runbook ROB-1

**Revision history.**
- 2025-10: editorial revision to NW-012; clarified scope and wording.
- 2022-04: editorial revision to NW-012; clarified scope and wording.
- 2022-09: editorial revision to NW-012; clarified scope and wording.


### NW-013 — Mandatory console access

**Domain:** Network Controls  **Severity:** Moderate  **Applies to:** service-account-bearing hosts

**Rationale.** Consistent enforcement reduces the mean time to detect anomalous access across the estate. Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment. Inconsistent application of this requirement across hosts complicates evidence collection and weakens attestations. Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment.

**Requirement.** When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. The host shall maintain the configuration described in this control at all times, and the setup auditor shall treat any deviation as reportable. The control exists to keep remediation deterministic so that repeated audits converge on a stable state.

**Implementation guidance.** Coordinate with the accounts team before altering anything that affects service-account behavior. Changes should be staged in a non-production environment and validated against the verification procedure below. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. Retain the prior configuration so that a rollback can be performed without rebuilding the host. Operators should prefer configuration that is idempotent so that re-running the auditor produces no further changes. Coordinate with the accounts team before altering anything that affects service-account behavior. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies.

**Verification.** The verifier records the before and after state for inclusion in the assessment package. The verifier records the before and after state for inclusion in the assessment package. The verifier records the before and after state for inclusion in the assessment package. Verification is performed by the setup auditor, which compares the host state to the normalized policy expectation.

**References.** Lab Operations Runbook ROB-2; Lab Operations Runbook ROB-9

**Revision history.**
- 2023-03: editorial revision to NW-013; clarified scope and wording.
- 2023-10: editorial revision to NW-013; clarified scope and wording.


## 10. Incident Response

This requirement aligns the gateway with the principle of least privilege mandated by the governing security policy. Adversaries routinely probe for misconfigurations of this control when establishing persistence on laboratory infrastructure. This requirement aligns the gateway with the principle of least privilege mandated by the governing security policy. Consistent enforcement reduces the mean time to detect anomalous access across the estate. The control supports reproducible builds of the host baseline and simplifies forensic comparison. Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment.


Retain the prior configuration so that a rollback can be performed without rebuilding the host. Retain the prior configuration so that a rollback can be performed without rebuilding the host. Operators should prefer configuration that is idempotent so that re-running the auditor produces no further changes. Changes should be staged in a non-production environment and validated against the verification procedure below.


### IR-001 — Monitored module loading

**Domain:** Incident Response  **Severity:** Critical  **Applies to:** shared interactive hosts

**Rationale.** The control exists to keep remediation deterministic so that repeated audits converge on a stable state. Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment. Operational experience shows that small deviations here cascade into larger exposure during incident response.

**Requirement.** Document any approved deviation in the exceptions register with a scheduled review date. The host shall maintain the configuration described in this control at all times, and the setup auditor shall treat any deviation as reportable. Consistent enforcement reduces the mean time to detect anomalous access across the estate.

**Implementation guidance.** Changes should be staged in a non-production environment and validated against the verification procedure below. Coordinate with the accounts team before altering anything that affects service-account behavior. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. Document any approved deviation in the exceptions register with a scheduled review date. Document any approved deviation in the exceptions register with a scheduled review date.

**Verification.** Verification is performed by the setup auditor, which compares the host state to the normalized policy expectation. Assessors may re-run the audit after applying patches to confirm the host has converged. Verification is performed by the setup auditor, which compares the host state to the normalized policy expectation. The verifier records the before and after state for inclusion in the assessment package. Verification is performed by the setup auditor, which compares the host state to the normalized policy expectation.

**References.** Vendor hardening note VHN-6-2; Vendor hardening note VHN-6-9; Lab Operations Runbook ROB-6

**Revision history.**
- 2023-01: editorial revision to IR-001; clarified scope and wording.
- 2023-02: editorial revision to IR-001; clarified scope and wording.
- 2022-12: editorial revision to IR-001; clarified scope and wording.


### IR-002 — Baseline kernel parameter

**Domain:** Incident Response  **Severity:** High  **Applies to:** gateway and bastion hosts

**Rationale.** The control supports reproducible builds of the host baseline and simplifies forensic comparison. Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment. Operational experience shows that small deviations here cascade into larger exposure during incident response.

**Requirement.** Changes should be staged in a non-production environment and validated against the verification procedure below. The host shall maintain the configuration described in this control at all times, and the setup auditor shall treat any deviation as reportable. Consistent enforcement reduces the mean time to detect anomalous access across the estate.

**Implementation guidance.** Changes should be staged in a non-production environment and validated against the verification procedure below. Operators should prefer configuration that is idempotent so that re-running the auditor produces no further changes. Changes should be staged in a non-production environment and validated against the verification procedure below. Changes should be staged in a non-production environment and validated against the verification procedure below. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. Retain the prior configuration so that a rollback can be performed without rebuilding the host.

**Verification.** Verification is performed by the setup auditor, which compares the host state to the normalized policy expectation. Verification is performed by the setup auditor, which compares the host state to the normalized policy expectation. Evidence is the auditor's proposed patch set; a compliant host yields an empty set for this control. Assessors may re-run the audit after applying patches to confirm the host has converged.

**References.** Prior assessment finding AF-6; Baseline Configuration Guide BCG-5.9

**Revision history.**
- 2025-08: editorial revision to IR-002; clarified scope and wording.
- 2025-09: editorial revision to IR-002; clarified scope and wording.


### IR-003 — Baseline session timeout

**Domain:** Incident Response  **Severity:** High  **Applies to:** gateway and bastion hosts

**Rationale.** This requirement aligns the gateway with the principle of least privilege mandated by the governing security policy. Consistent enforcement reduces the mean time to detect anomalous access across the estate. Operational experience shows that small deviations here cascade into larger exposure during incident response. Inconsistent application of this requirement across hosts complicates evidence collection and weakens attestations.

**Requirement.** Document any approved deviation in the exceptions register with a scheduled review date. The host shall maintain the configuration described in this control at all times, and the setup auditor shall treat any deviation as reportable. Consistent enforcement reduces the mean time to detect anomalous access across the estate.

**Implementation guidance.** Retain the prior configuration so that a rollback can be performed without rebuilding the host. Coordinate with the accounts team before altering anything that affects service-account behavior. Coordinate with the accounts team before altering anything that affects service-account behavior. Retain the prior configuration so that a rollback can be performed without rebuilding the host. Document any approved deviation in the exceptions register with a scheduled review date.

**Verification.** Automated property checks generate varied host states to confirm the control behaves consistently. Evidence is the auditor's proposed patch set; a compliant host yields an empty set for this control. Assessors may re-run the audit after applying patches to confirm the host has converged. Automated property checks generate varied host states to confirm the control behaves consistently.

**References.** Vendor hardening note VHN-1-1; Vendor hardening note VHN-2-7; Governing Security Policy GSP-2024 §2.2; Lab Operations Runbook ROB-3

**Revision history.**
- 2025-07: editorial revision to IR-003; clarified scope and wording.
- 2024-11: editorial revision to IR-003; clarified scope and wording.


### IR-004 — Monitored log forwarding

**Domain:** Incident Response  **Severity:** Moderate  **Applies to:** gateway and bastion hosts

**Rationale.** Inconsistent application of this requirement across hosts complicates evidence collection and weakens attestations. Consistent enforcement reduces the mean time to detect anomalous access across the estate. The control supports reproducible builds of the host baseline and simplifies forensic comparison.

**Requirement.** Coordinate with the accounts team before altering anything that affects service-account behavior. The host shall maintain the configuration described in this control at all times, and the setup auditor shall treat any deviation as reportable. Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment.

**Implementation guidance.** Prefer explicit values over relying on compiled-in defaults, which may vary between distributions. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. Retain the prior configuration so that a rollback can be performed without rebuilding the host. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner.

**Verification.** Evidence is the auditor's proposed patch set; a compliant host yields an empty set for this control. Evidence is the auditor's proposed patch set; a compliant host yields an empty set for this control. The verifier records the before and after state for inclusion in the assessment package. Assessors may re-run the audit after applying patches to confirm the host has converged.

**References.** Prior assessment finding AF-7; Baseline Configuration Guide BCG-6.6; Lab Operations Runbook ROB-1

**Revision history.**
- 2025-09: editorial revision to IR-004; clarified scope and wording.
- 2023-04: editorial revision to IR-004; clarified scope and wording.
- 2024-04: editorial revision to IR-004; clarified scope and wording.


### IR-005 — Baseline banner presentation

**Domain:** Incident Response  **Severity:** Low  **Applies to:** all managed hosts

**Rationale.** This requirement aligns the gateway with the principle of least privilege mandated by the governing security policy. Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment. Operational experience shows that small deviations here cascade into larger exposure during incident response. Inconsistent application of this requirement across hosts complicates evidence collection and weakens attestations.

**Requirement.** Prefer explicit values over relying on compiled-in defaults, which may vary between distributions. The host shall maintain the configuration described in this control at all times, and the setup auditor shall treat any deviation as reportable. The control exists to keep remediation deterministic so that repeated audits converge on a stable state.

**Implementation guidance.** Changes should be staged in a non-production environment and validated against the verification procedure below. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. Operators should prefer configuration that is idempotent so that re-running the auditor produces no further changes. Document any approved deviation in the exceptions register with a scheduled review date. Document any approved deviation in the exceptions register with a scheduled review date. Prefer explicit values over relying on compiled-in defaults, which may vary between distributions. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies.

**Verification.** Verification is performed by the setup auditor, which compares the host state to the normalized policy expectation. Verification is performed by the setup auditor, which compares the host state to the normalized policy expectation. The verifier records the before and after state for inclusion in the assessment package. Assessors may re-run the audit after applying patches to confirm the host has converged.

**References.** Governing Security Policy GSP-2024 §5.3; Governing Security Policy GSP-2024 §3.8; Baseline Configuration Guide BCG-2.0

**Revision history.**
- 2022-11: editorial revision to IR-005; clarified scope and wording.
- 2024-05: editorial revision to IR-005; clarified scope and wording.


### IR-006 — Hardened package provenance

**Domain:** Incident Response  **Severity:** High  **Applies to:** tier-1 laboratory hosts

**Rationale.** The control exists to keep remediation deterministic so that repeated audits converge on a stable state. This requirement aligns the gateway with the principle of least privilege mandated by the governing security policy. The control supports reproducible builds of the host baseline and simplifies forensic comparison.

**Requirement.** Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. The host shall maintain the configuration described in this control at all times, and the setup auditor shall treat any deviation as reportable. Operational experience shows that small deviations here cascade into larger exposure during incident response.

**Implementation guidance.** When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. Operators should prefer configuration that is idempotent so that re-running the auditor produces no further changes. Retain the prior configuration so that a rollback can be performed without rebuilding the host. Operators should prefer configuration that is idempotent so that re-running the auditor produces no further changes. Changes should be staged in a non-production environment and validated against the verification procedure below. Changes should be staged in a non-production environment and validated against the verification procedure below.

**Verification.** The verifier records the before and after state for inclusion in the assessment package. Automated property checks generate varied host states to confirm the control behaves consistently. Verification is performed by the setup auditor, which compares the host state to the normalized policy expectation. The verifier records the before and after state for inclusion in the assessment package. Evidence is the auditor's proposed patch set; a compliant host yields an empty set for this control.

**References.** Vendor hardening note VHN-3-1; Lab Operations Runbook ROB-2

**Revision history.**
- 2022-01: editorial revision to IR-006; clarified scope and wording.
- 2024-03: editorial revision to IR-006; clarified scope and wording.
- 2023-11: editorial revision to IR-006; clarified scope and wording.
- 2024-06: editorial revision to IR-006; clarified scope and wording.


### IR-007 — Approved console access

**Domain:** Incident Response  **Severity:** High  **Applies to:** service-account-bearing hosts

**Rationale.** Inconsistent application of this requirement across hosts complicates evidence collection and weakens attestations. The control exists to keep remediation deterministic so that repeated audits converge on a stable state. Operational experience shows that small deviations here cascade into larger exposure during incident response.

**Requirement.** Operators should prefer configuration that is idempotent so that re-running the auditor produces no further changes. The host shall maintain the configuration described in this control at all times, and the setup auditor shall treat any deviation as reportable. Consistent enforcement reduces the mean time to detect anomalous access across the estate.

**Implementation guidance.** Prefer explicit values over relying on compiled-in defaults, which may vary between distributions. Retain the prior configuration so that a rollback can be performed without rebuilding the host. Operators should prefer configuration that is idempotent so that re-running the auditor produces no further changes. Operators should prefer configuration that is idempotent so that re-running the auditor produces no further changes. Document any approved deviation in the exceptions register with a scheduled review date. Retain the prior configuration so that a rollback can be performed without rebuilding the host. Document any approved deviation in the exceptions register with a scheduled review date.

**Verification.** Verification is performed by the setup auditor, which compares the host state to the normalized policy expectation. The verifier records the before and after state for inclusion in the assessment package. The verifier records the before and after state for inclusion in the assessment package.

**References.** Prior assessment finding AF-6; Governing Security Policy GSP-2024 §8.0; Governing Security Policy GSP-2024 §7.3

**Revision history.**
- 2025-12: editorial revision to IR-007; clarified scope and wording.
- 2023-04: editorial revision to IR-007; clarified scope and wording.


### IR-008 — Baseline umask default

**Domain:** Incident Response  **Severity:** High  **Applies to:** all managed hosts

**Rationale.** Inconsistent application of this requirement across hosts complicates evidence collection and weakens attestations. Inconsistent application of this requirement across hosts complicates evidence collection and weakens attestations. Adversaries routinely probe for misconfigurations of this control when establishing persistence on laboratory infrastructure. Inconsistent application of this requirement across hosts complicates evidence collection and weakens attestations. Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment.

**Requirement.** Retain the prior configuration so that a rollback can be performed without rebuilding the host. The host shall maintain the configuration described in this control at all times, and the setup auditor shall treat any deviation as reportable. The control exists to keep remediation deterministic so that repeated audits converge on a stable state.

**Implementation guidance.** When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. Operators should prefer configuration that is idempotent so that re-running the auditor produces no further changes. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. Operators should prefer configuration that is idempotent so that re-running the auditor produces no further changes. Operators should prefer configuration that is idempotent so that re-running the auditor produces no further changes. Operators should prefer configuration that is idempotent so that re-running the auditor produces no further changes. Document any approved deviation in the exceptions register with a scheduled review date.

**Verification.** Verification is performed by the setup auditor, which compares the host state to the normalized policy expectation. Verification is performed by the setup auditor, which compares the host state to the normalized policy expectation. Automated property checks generate varied host states to confirm the control behaves consistently.

**References.** Prior assessment finding AF-9; Baseline Configuration Guide BCG-5.3; Governing Security Policy GSP-2024 §1.1

**Revision history.**
- 2025-09: editorial revision to IR-008; clarified scope and wording.
- 2024-11: editorial revision to IR-008; clarified scope and wording.


### IR-009 — Baseline interface configuration

**Domain:** Incident Response  **Severity:** Low  **Applies to:** service-account-bearing hosts

**Rationale.** Inconsistent application of this requirement across hosts complicates evidence collection and weakens attestations. The control exists to keep remediation deterministic so that repeated audits converge on a stable state. Operational experience shows that small deviations here cascade into larger exposure during incident response. The control supports reproducible builds of the host baseline and simplifies forensic comparison. The control exists to keep remediation deterministic so that repeated audits converge on a stable state.

**Requirement.** Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. The host shall maintain the configuration described in this control at all times, and the setup auditor shall treat any deviation as reportable. The control supports reproducible builds of the host baseline and simplifies forensic comparison.

**Implementation guidance.** Document any approved deviation in the exceptions register with a scheduled review date. Prefer explicit values over relying on compiled-in defaults, which may vary between distributions. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. Changes should be staged in a non-production environment and validated against the verification procedure below. Retain the prior configuration so that a rollback can be performed without rebuilding the host. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. Operators should prefer configuration that is idempotent so that re-running the auditor produces no further changes.

**Verification.** The verifier records the before and after state for inclusion in the assessment package. Evidence is the auditor's proposed patch set; a compliant host yields an empty set for this control. Assessors may re-run the audit after applying patches to confirm the host has converged. Evidence is the auditor's proposed patch set; a compliant host yields an empty set for this control.

**References.** Governing Security Policy GSP-2024 §6.9; Lab Operations Runbook ROB-6; Governing Security Policy GSP-2024 §3.8; Prior assessment finding AF-4

**Revision history.**
- 2025-05: editorial revision to IR-009; clarified scope and wording.
- 2025-05: editorial revision to IR-009; clarified scope and wording.
- 2022-03: editorial revision to IR-009; clarified scope and wording.
- 2023-08: editorial revision to IR-009; clarified scope and wording.


### IR-010 — Centralized package provenance

**Domain:** Incident Response  **Severity:** Low  **Applies to:** all managed hosts

**Rationale.** The control exists to keep remediation deterministic so that repeated audits converge on a stable state. Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment. Operational experience shows that small deviations here cascade into larger exposure during incident response. The control supports reproducible builds of the host baseline and simplifies forensic comparison.

**Requirement.** Coordinate with the accounts team before altering anything that affects service-account behavior. The host shall maintain the configuration described in this control at all times, and the setup auditor shall treat any deviation as reportable. Consistent enforcement reduces the mean time to detect anomalous access across the estate.

**Implementation guidance.** Coordinate with the accounts team before altering anything that affects service-account behavior. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. Operators should prefer configuration that is idempotent so that re-running the auditor produces no further changes. Retain the prior configuration so that a rollback can be performed without rebuilding the host. Prefer explicit values over relying on compiled-in defaults, which may vary between distributions. Coordinate with the accounts team before altering anything that affects service-account behavior. Retain the prior configuration so that a rollback can be performed without rebuilding the host. Document any approved deviation in the exceptions register with a scheduled review date.

**Verification.** Assessors may re-run the audit after applying patches to confirm the host has converged. Automated property checks generate varied host states to confirm the control behaves consistently. Evidence is the auditor's proposed patch set; a compliant host yields an empty set for this control. Evidence is the auditor's proposed patch set; a compliant host yields an empty set for this control.

**References.** Baseline Configuration Guide BCG-1.2; Lab Operations Runbook ROB-7; Vendor hardening note VHN-4-8

**Revision history.**
- 2022-03: editorial revision to IR-010; clarified scope and wording.
- 2022-05: editorial revision to IR-010; clarified scope and wording.


### IR-011 — Mandatory interface configuration

**Domain:** Incident Response  **Severity:** Moderate  **Applies to:** gateway and bastion hosts

**Rationale.** Consistent enforcement reduces the mean time to detect anomalous access across the estate. This requirement aligns the gateway with the principle of least privilege mandated by the governing security policy. The control exists to keep remediation deterministic so that repeated audits converge on a stable state.

**Requirement.** Operators should prefer configuration that is idempotent so that re-running the auditor produces no further changes. The host shall maintain the configuration described in this control at all times, and the setup auditor shall treat any deviation as reportable. This requirement aligns the gateway with the principle of least privilege mandated by the governing security policy.

**Implementation guidance.** Coordinate with the accounts team before altering anything that affects service-account behavior. Retain the prior configuration so that a rollback can be performed without rebuilding the host. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. Coordinate with the accounts team before altering anything that affects service-account behavior. Retain the prior configuration so that a rollback can be performed without rebuilding the host.

**Verification.** Assessors may re-run the audit after applying patches to confirm the host has converged. Verification is performed by the setup auditor, which compares the host state to the normalized policy expectation. Evidence is the auditor's proposed patch set; a compliant host yields an empty set for this control. Evidence is the auditor's proposed patch set; a compliant host yields an empty set for this control.

**References.** Lab Operations Runbook ROB-1; Vendor hardening note VHN-9-4

**Revision history.**
- 2024-09: editorial revision to IR-011; clarified scope and wording.
- 2022-01: editorial revision to IR-011; clarified scope and wording.
- 2024-04: editorial revision to IR-011; clarified scope and wording.


### IR-012 — Controlled credential rotation

**Domain:** Incident Response  **Severity:** High  **Applies to:** all managed hosts

**Rationale.** Inconsistent application of this requirement across hosts complicates evidence collection and weakens attestations. The control supports reproducible builds of the host baseline and simplifies forensic comparison. Operational experience shows that small deviations here cascade into larger exposure during incident response. This requirement aligns the gateway with the principle of least privilege mandated by the governing security policy. Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment.

**Requirement.** Prefer explicit values over relying on compiled-in defaults, which may vary between distributions. The host shall maintain the configuration described in this control at all times, and the setup auditor shall treat any deviation as reportable. Inconsistent application of this requirement across hosts complicates evidence collection and weakens attestations.

**Implementation guidance.** Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. Document any approved deviation in the exceptions register with a scheduled review date. Retain the prior configuration so that a rollback can be performed without rebuilding the host. Prefer explicit values over relying on compiled-in defaults, which may vary between distributions. Changes should be staged in a non-production environment and validated against the verification procedure below.

**Verification.** Assessors may re-run the audit after applying patches to confirm the host has converged. Automated property checks generate varied host states to confirm the control behaves consistently. Assessors may re-run the audit after applying patches to confirm the host has converged.

**References.** Prior assessment finding AF-5; Prior assessment finding AF-6; Governing Security Policy GSP-2024 §2.9

**Revision history.**
- 2024-04: editorial revision to IR-012; clarified scope and wording.
- 2023-12: editorial revision to IR-012; clarified scope and wording.
- 2022-12: editorial revision to IR-012; clarified scope and wording.
- 2023-10: editorial revision to IR-012; clarified scope and wording.


### IR-013 — Mandatory core dump handling

**Domain:** Incident Response  **Severity:** Low  **Applies to:** tier-1 laboratory hosts

**Rationale.** This requirement aligns the gateway with the principle of least privilege mandated by the governing security policy. Consistent enforcement reduces the mean time to detect anomalous access across the estate. Consistent enforcement reduces the mean time to detect anomalous access across the estate.

**Requirement.** Document any approved deviation in the exceptions register with a scheduled review date. The host shall maintain the configuration described in this control at all times, and the setup auditor shall treat any deviation as reportable. The control exists to keep remediation deterministic so that repeated audits converge on a stable state.

**Implementation guidance.** Retain the prior configuration so that a rollback can be performed without rebuilding the host. Operators should prefer configuration that is idempotent so that re-running the auditor produces no further changes. Prefer explicit values over relying on compiled-in defaults, which may vary between distributions. Operators should prefer configuration that is idempotent so that re-running the auditor produces no further changes. Prefer explicit values over relying on compiled-in defaults, which may vary between distributions. Coordinate with the accounts team before altering anything that affects service-account behavior. Document any approved deviation in the exceptions register with a scheduled review date.

**Verification.** The verifier records the before and after state for inclusion in the assessment package. Evidence is the auditor's proposed patch set; a compliant host yields an empty set for this control. The verifier records the before and after state for inclusion in the assessment package.

**References.** Prior assessment finding AF-9; Baseline Configuration Guide BCG-9.0; Baseline Configuration Guide BCG-9.4

**Revision history.**
- 2024-05: editorial revision to IR-013; clarified scope and wording.
- 2024-07: editorial revision to IR-013; clarified scope and wording.
- 2022-01: editorial revision to IR-013; clarified scope and wording.
- 2024-01: editorial revision to IR-013; clarified scope and wording.


## Appendix A. Host classification


- **SV-725**: Document any approved deviation in the exceptions register with a scheduled review date. Prefer explicit values over relying on compiled-in defaults, which may vary between distributions. Document any approved deviation in the exceptions register with a scheduled review date.

- **GW-335**: Operators should prefer configuration that is idempotent so that re-running the auditor produces no further changes. Document any approved deviation in the exceptions register with a scheduled review date.

- **GW-480**: Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. Prefer explicit values over relying on compiled-in defaults, which may vary between distributions.

- **GW-496**: Document any approved deviation in the exceptions register with a scheduled review date. Coordinate with the accounts team before altering anything that affects service-account behavior. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies.

- **HC-619**: Operators should prefer configuration that is idempotent so that re-running the auditor produces no further changes. Operators should prefer configuration that is idempotent so that re-running the auditor produces no further changes.

- **SV-634**: Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner.

- **SV-849**: Document any approved deviation in the exceptions register with a scheduled review date. Operators should prefer configuration that is idempotent so that re-running the auditor produces no further changes. Changes should be staged in a non-production environment and validated against the verification procedure below.

- **SV-107**: Coordinate with the accounts team before altering anything that affects service-account behavior. Changes should be staged in a non-production environment and validated against the verification procedure below.

- **GW-469**: Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. Retain the prior configuration so that a rollback can be performed without rebuilding the host. Document any approved deviation in the exceptions register with a scheduled review date.

- **SV-589**: When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. Prefer explicit values over relying on compiled-in defaults, which may vary between distributions.

- **TL-176**: Changes should be staged in a non-production environment and validated against the verification procedure below. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner.

- **HC-739**: Prefer explicit values over relying on compiled-in defaults, which may vary between distributions. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies.


## Appendix C. Banner wording

Operators should prefer configuration that is idempotent so that re-running the auditor produces no further changes. Operators should prefer configuration that is idempotent so that re-running the auditor produces no further changes. Retain the prior configuration so that a rollback can be performed without rebuilding the host. Retain the prior configuration so that a rollback can be performed without rebuilding the host. Document any approved deviation in the exceptions register with a scheduled review date. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner.


## Appendix B. Control rationale narratives


### Narrative XB-61

This requirement aligns the gateway with the principle of least privilege mandated by the governing security policy. Adversaries routinely probe for misconfigurations of this control when establishing persistence on laboratory infrastructure. The control exists to keep remediation deterministic so that repeated audits converge on a stable state. The control exists to keep remediation deterministic so that repeated audits converge on a stable state. The control supports reproducible builds of the host baseline and simplifies forensic comparison. This requirement aligns the gateway with the principle of least privilege mandated by the governing security policy.

### Narrative XB-55

Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment. The control supports reproducible builds of the host baseline and simplifies forensic comparison. Retain the prior configuration so that a rollback can be performed without rebuilding the host. Coordinate with the accounts team before altering anything that affects service-account behavior. Retain the prior configuration so that a rollback can be performed without rebuilding the host. The control exists to keep remediation deterministic so that repeated audits converge on a stable state. Inconsistent application of this requirement across hosts complicates evidence collection and weakens attestations. Retain the prior configuration so that a rollback can be performed without rebuilding the host. Adversaries routinely probe for misconfigurations of this control when establishing persistence on laboratory infrastructure. Coordinate with the accounts team before altering anything that affects service-account behavior.

### Narrative XB-47

Inconsistent application of this requirement across hosts complicates evidence collection and weakens attestations. Retain the prior configuration so that a rollback can be performed without rebuilding the host. Consistent enforcement reduces the mean time to detect anomalous access across the estate. The control supports reproducible builds of the host baseline and simplifies forensic comparison. Operators should prefer configuration that is idempotent so that re-running the auditor produces no further changes. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. Changes should be staged in a non-production environment and validated against the verification procedure below.

### Narrative RB-67

Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. Changes should be staged in a non-production environment and validated against the verification procedure below. The control exists to keep remediation deterministic so that repeated audits converge on a stable state. Coordinate with the accounts team before altering anything that affects service-account behavior. Inconsistent application of this requirement across hosts complicates evidence collection and weakens attestations. Document any approved deviation in the exceptions register with a scheduled review date.

### Narrative NB-45

Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment. Retain the prior configuration so that a rollback can be performed without rebuilding the host. The control exists to keep remediation deterministic so that repeated audits converge on a stable state. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. Coordinate with the accounts team before altering anything that affects service-account behavior. Coordinate with the accounts team before altering anything that affects service-account behavior.

### Narrative NB-22

When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. Adversaries routinely probe for misconfigurations of this control when establishing persistence on laboratory infrastructure. Retain the prior configuration so that a rollback can be performed without rebuilding the host. Coordinate with the accounts team before altering anything that affects service-account behavior. Prefer explicit values over relying on compiled-in defaults, which may vary between distributions. The control exists to keep remediation deterministic so that repeated audits converge on a stable state. The control supports reproducible builds of the host baseline and simplifies forensic comparison. Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment. Inconsistent application of this requirement across hosts complicates evidence collection and weakens attestations.

### Narrative XB-31

Inconsistent application of this requirement across hosts complicates evidence collection and weakens attestations. The control supports reproducible builds of the host baseline and simplifies forensic comparison. Adversaries routinely probe for misconfigurations of this control when establishing persistence on laboratory infrastructure. Coordinate with the accounts team before altering anything that affects service-account behavior. This requirement aligns the gateway with the principle of least privilege mandated by the governing security policy. Coordinate with the accounts team before altering anything that affects service-account behavior. Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment. Adversaries routinely probe for misconfigurations of this control when establishing persistence on laboratory infrastructure. Coordinate with the accounts team before altering anything that affects service-account behavior. Operators should prefer configuration that is idempotent so that re-running the auditor produces no further changes.

### Narrative RB-39

Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment. Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment. Adversaries routinely probe for misconfigurations of this control when establishing persistence on laboratory infrastructure. Retain the prior configuration so that a rollback can be performed without rebuilding the host. Document any approved deviation in the exceptions register with a scheduled review date. Inconsistent application of this requirement across hosts complicates evidence collection and weakens attestations. Retain the prior configuration so that a rollback can be performed without rebuilding the host. Prefer explicit values over relying on compiled-in defaults, which may vary between distributions.

### Narrative RB-82

The control supports reproducible builds of the host baseline and simplifies forensic comparison. The control supports reproducible builds of the host baseline and simplifies forensic comparison. Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment. Operational experience shows that small deviations here cascade into larger exposure during incident response. Operational experience shows that small deviations here cascade into larger exposure during incident response. Inconsistent application of this requirement across hosts complicates evidence collection and weakens attestations. Operational experience shows that small deviations here cascade into larger exposure during incident response. The control supports reproducible builds of the host baseline and simplifies forensic comparison. This requirement aligns the gateway with the principle of least privilege mandated by the governing security policy. Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment.

### Narrative XB-18

Operational experience shows that small deviations here cascade into larger exposure during incident response. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. The control supports reproducible builds of the host baseline and simplifies forensic comparison. Document any approved deviation in the exceptions register with a scheduled review date. Inconsistent application of this requirement across hosts complicates evidence collection and weakens attestations. Document any approved deviation in the exceptions register with a scheduled review date. Consistent enforcement reduces the mean time to detect anomalous access across the estate. Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment.

### Narrative XB-22

Prefer explicit values over relying on compiled-in defaults, which may vary between distributions. Operational experience shows that small deviations here cascade into larger exposure during incident response. Document any approved deviation in the exceptions register with a scheduled review date. Operational experience shows that small deviations here cascade into larger exposure during incident response. Prefer explicit values over relying on compiled-in defaults, which may vary between distributions. Retain the prior configuration so that a rollback can be performed without rebuilding the host. Changes should be staged in a non-production environment and validated against the verification procedure below. Changes should be staged in a non-production environment and validated against the verification procedure below. Inconsistent application of this requirement across hosts complicates evidence collection and weakens attestations.

### Narrative XB-31

The control exists to keep remediation deterministic so that repeated audits converge on a stable state. Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment. The control exists to keep remediation deterministic so that repeated audits converge on a stable state. The control exists to keep remediation deterministic so that repeated audits converge on a stable state. Operational experience shows that small deviations here cascade into larger exposure during incident response. Changes should be staged in a non-production environment and validated against the verification procedure below. The control exists to keep remediation deterministic so that repeated audits converge on a stable state. Consistent enforcement reduces the mean time to detect anomalous access across the estate. Document any approved deviation in the exceptions register with a scheduled review date.

### Narrative RB-80

Coordinate with the accounts team before altering anything that affects service-account behavior. The control supports reproducible builds of the host baseline and simplifies forensic comparison. Coordinate with the accounts team before altering anything that affects service-account behavior. The control supports reproducible builds of the host baseline and simplifies forensic comparison. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. This requirement aligns the gateway with the principle of least privilege mandated by the governing security policy. Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment. Retain the prior configuration so that a rollback can be performed without rebuilding the host. Retain the prior configuration so that a rollback can be performed without rebuilding the host.

### Narrative NB-20

Inconsistent application of this requirement across hosts complicates evidence collection and weakens attestations. Adversaries routinely probe for misconfigurations of this control when establishing persistence on laboratory infrastructure. Document any approved deviation in the exceptions register with a scheduled review date. Operational experience shows that small deviations here cascade into larger exposure during incident response. Coordinate with the accounts team before altering anything that affects service-account behavior. Operational experience shows that small deviations here cascade into larger exposure during incident response. The control supports reproducible builds of the host baseline and simplifies forensic comparison. This requirement aligns the gateway with the principle of least privilege mandated by the governing security policy.


## Appendix D. Assessment procedures


- **Procedure 504.** Evidence is the auditor's proposed patch set; a compliant host yields an empty set for this control. Prefer explicit values over relying on compiled-in defaults, which may vary between distributions. Prefer explicit values over relying on compiled-in defaults, which may vary between distributions. Coordinate with the accounts team before altering anything that affects service-account behavior. Evidence is the auditor's proposed patch set; a compliant host yields an empty set for this control.

- **Procedure 993.** Verification is performed by the setup auditor, which compares the host state to the normalized policy expectation. Coordinate with the accounts team before altering anything that affects service-account behavior. Assessors may re-run the audit after applying patches to confirm the host has converged. Assessors may re-run the audit after applying patches to confirm the host has converged. Document any approved deviation in the exceptions register with a scheduled review date.

- **Procedure 561.** Changes should be staged in a non-production environment and validated against the verification procedure below. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. Verification is performed by the setup auditor, which compares the host state to the normalized policy expectation.

- **Procedure 661.** Prefer explicit values over relying on compiled-in defaults, which may vary between distributions. Changes should be staged in a non-production environment and validated against the verification procedure below. Evidence is the auditor's proposed patch set; a compliant host yields an empty set for this control.

- **Procedure 835.** Coordinate with the accounts team before altering anything that affects service-account behavior. Prefer explicit values over relying on compiled-in defaults, which may vary between distributions. Prefer explicit values over relying on compiled-in defaults, which may vary between distributions.

- **Procedure 830.** Operators should prefer configuration that is idempotent so that re-running the auditor produces no further changes. The verifier records the before and after state for inclusion in the assessment package. Prefer explicit values over relying on compiled-in defaults, which may vary between distributions.

- **Procedure 478.** Retain the prior configuration so that a rollback can be performed without rebuilding the host. Evidence is the auditor's proposed patch set; a compliant host yields an empty set for this control. Assessors may re-run the audit after applying patches to confirm the host has converged.

- **Procedure 950.** Retain the prior configuration so that a rollback can be performed without rebuilding the host. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. Document any approved deviation in the exceptions register with a scheduled review date.

- **Procedure 287.** Prefer explicit values over relying on compiled-in defaults, which may vary between distributions. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. Evidence is the auditor's proposed patch set; a compliant host yields an empty set for this control. Document any approved deviation in the exceptions register with a scheduled review date. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies.

- **Procedure 447.** Operators should prefer configuration that is idempotent so that re-running the auditor produces no further changes. Prefer explicit values over relying on compiled-in defaults, which may vary between distributions. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. Verification is performed by the setup auditor, which compares the host state to the normalized policy expectation. Assessors may re-run the audit after applying patches to confirm the host has converged.

- **Procedure 752.** Changes should be staged in a non-production environment and validated against the verification procedure below. Automated property checks generate varied host states to confirm the control behaves consistently. Operators should prefer configuration that is idempotent so that re-running the auditor produces no further changes. Coordinate with the accounts team before altering anything that affects service-account behavior.

- **Procedure 197.** Coordinate with the accounts team before altering anything that affects service-account behavior. Automated property checks generate varied host states to confirm the control behaves consistently. Retain the prior configuration so that a rollback can be performed without rebuilding the host. Changes should be staged in a non-production environment and validated against the verification procedure below. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies.

- **Procedure 480.** Document any approved deviation in the exceptions register with a scheduled review date. Retain the prior configuration so that a rollback can be performed without rebuilding the host. Verification is performed by the setup auditor, which compares the host state to the normalized policy expectation. Automated property checks generate varied host states to confirm the control behaves consistently. Document any approved deviation in the exceptions register with a scheduled review date.

- **Procedure 848.** Evidence is the auditor's proposed patch set; a compliant host yields an empty set for this control. Operators should prefer configuration that is idempotent so that re-running the auditor produces no further changes. Changes should be staged in a non-production environment and validated against the verification procedure below. Assessors may re-run the audit after applying patches to confirm the host has converged.

- **Procedure 203.** Changes should be staged in a non-production environment and validated against the verification procedure below. Prefer explicit values over relying on compiled-in defaults, which may vary between distributions. Retain the prior configuration so that a rollback can be performed without rebuilding the host.

- **Procedure 530.** Assessors may re-run the audit after applying patches to confirm the host has converged. Automated property checks generate varied host states to confirm the control behaves consistently. Verification is performed by the setup auditor, which compares the host state to the normalized policy expectation. Assessors may re-run the audit after applying patches to confirm the host has converged. Prefer explicit values over relying on compiled-in defaults, which may vary between distributions.


## Appendix E. Change log


- 2026-10-15: Prefer explicit values over relying on compiled-in defaults, which may vary between distributions.

- 2024-02-25: When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. Changes should be staged in a non-production environment and validated against the verification procedure below.

- 2024-09-04: When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. Retain the prior configuration so that a rollback can be performed without rebuilding the host.

- 2026-06-25: The control exists to keep remediation deterministic so that repeated audits converge on a stable state.

- 2024-11-23: Operational experience shows that small deviations here cascade into larger exposure during incident response. This requirement aligns the gateway with the principle of least privilege mandated by the governing security policy.

- 2026-08-09: Document any approved deviation in the exceptions register with a scheduled review date. Prefer explicit values over relying on compiled-in defaults, which may vary between distributions.

- 2024-05-27: Coordinate with the accounts team before altering anything that affects service-account behavior.

- 2026-04-17: Coordinate with the accounts team before altering anything that affects service-account behavior. Adversaries routinely probe for misconfigurations of this control when establishing persistence on laboratory infrastructure.

- 2026-04-20: Inconsistent application of this requirement across hosts complicates evidence collection and weakens attestations. The control supports reproducible builds of the host baseline and simplifies forensic comparison.

- 2024-10-28: The control supports reproducible builds of the host baseline and simplifies forensic comparison.

- 2024-05-13: Operators should prefer configuration that is idempotent so that re-running the auditor produces no further changes. Changes should be staged in a non-production environment and validated against the verification procedure below.

- 2023-09-12: Changes should be staged in a non-production environment and validated against the verification procedure below. Document any approved deviation in the exceptions register with a scheduled review date.

- 2023-04-22: Coordinate with the accounts team before altering anything that affects service-account behavior. Document any approved deviation in the exceptions register with a scheduled review date.

- 2024-07-23: Consistent enforcement reduces the mean time to detect anomalous access across the estate. The control exists to keep remediation deterministic so that repeated audits converge on a stable state.

- 2023-04-06: This requirement aligns the gateway with the principle of least privilege mandated by the governing security policy. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner.

- 2023-02-04: Retain the prior configuration so that a rollback can be performed without rebuilding the host. The control supports reproducible builds of the host baseline and simplifies forensic comparison.

- 2026-01-01: When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. Changes should be staged in a non-production environment and validated against the verification procedure below.

- 2024-03-23: Operational experience shows that small deviations here cascade into larger exposure during incident response. Prefer explicit values over relying on compiled-in defaults, which may vary between distributions.

- 2026-05-09: This requirement aligns the gateway with the principle of least privilege mandated by the governing security policy.

- 2025-08-18: Inconsistent application of this requirement across hosts complicates evidence collection and weakens attestations.

- 2024-08-01: When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner.

- 2024-07-14: Inconsistent application of this requirement across hosts complicates evidence collection and weakens attestations. Inconsistent application of this requirement across hosts complicates evidence collection and weakens attestations.

- 2026-03-16: Changes should be staged in a non-production environment and validated against the verification procedure below. Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment.

- 2024-02-25: Adversaries routinely probe for misconfigurations of this control when establishing persistence on laboratory infrastructure.

- 2024-11-21: This requirement aligns the gateway with the principle of least privilege mandated by the governing security policy. Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment.

- 2026-09-14: When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner.

- 2025-12-21: Coordinate with the accounts team before altering anything that affects service-account behavior. Consistent enforcement reduces the mean time to detect anomalous access across the estate.

- 2024-04-09: The control exists to keep remediation deterministic so that repeated audits converge on a stable state. Adversaries routinely probe for misconfigurations of this control when establishing persistence on laboratory infrastructure.

- 2023-01-17: Document any approved deviation in the exceptions register with a scheduled review date. Operators should prefer configuration that is idempotent so that re-running the auditor produces no further changes.

- 2024-09-02: Consistent enforcement reduces the mean time to detect anomalous access across the estate.

- 2024-11-06: Document any approved deviation in the exceptions register with a scheduled review date. Prefer explicit values over relying on compiled-in defaults, which may vary between distributions.

- 2023-04-27: Prefer explicit values over relying on compiled-in defaults, which may vary between distributions. Changes should be staged in a non-production environment and validated against the verification procedure below.

- 2023-01-05: Retain the prior configuration so that a rollback can be performed without rebuilding the host.

- 2024-01-01: When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. Consistent enforcement reduces the mean time to detect anomalous access across the estate.

- 2025-09-06: Retain the prior configuration so that a rollback can be performed without rebuilding the host.

- 2023-02-02: When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner.

- 2026-08-02: Retain the prior configuration so that a rollback can be performed without rebuilding the host.

- 2026-05-07: Consistent enforcement reduces the mean time to detect anomalous access across the estate. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner.

- 2024-05-25: Document any approved deviation in the exceptions register with a scheduled review date.

- 2025-06-08: Document any approved deviation in the exceptions register with a scheduled review date. Operational experience shows that small deviations here cascade into larger exposure during incident response.

- 2026-09-08: The control exists to keep remediation deterministic so that repeated audits converge on a stable state. Prefer explicit values over relying on compiled-in defaults, which may vary between distributions.

- 2023-06-11: The control exists to keep remediation deterministic so that repeated audits converge on a stable state. The control supports reproducible builds of the host baseline and simplifies forensic comparison.

- 2023-07-05: Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment.

- 2023-02-06: Where automation is used, ensure the tooling reads the canonical source files rather than cached copies.

- 2025-02-16: The control exists to keep remediation deterministic so that repeated audits converge on a stable state.

- 2026-09-07: Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. Inconsistent application of this requirement across hosts complicates evidence collection and weakens attestations.

- 2026-04-26: When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner.

- 2023-04-27: Changes should be staged in a non-production environment and validated against the verification procedure below. Changes should be staged in a non-production environment and validated against the verification procedure below.

- 2026-11-18: Where automation is used, ensure the tooling reads the canonical source files rather than cached copies. Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment.

- 2025-04-28: The control exists to keep remediation deterministic so that repeated audits converge on a stable state.

- 2023-09-12: Retain the prior configuration so that a rollback can be performed without rebuilding the host. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner.

- 2024-11-11: Prefer explicit values over relying on compiled-in defaults, which may vary between distributions. Retain the prior configuration so that a rollback can be performed without rebuilding the host.

- 2024-06-01: The control exists to keep remediation deterministic so that repeated audits converge on a stable state.

- 2023-01-28: Document any approved deviation in the exceptions register with a scheduled review date. Prefer explicit values over relying on compiled-in defaults, which may vary between distributions.

- 2023-03-15: Prefer explicit values over relying on compiled-in defaults, which may vary between distributions.

- 2024-01-12: Operators should prefer configuration that is idempotent so that re-running the auditor produces no further changes. Changes should be staged in a non-production environment and validated against the verification procedure below.

- 2025-01-21: This requirement aligns the gateway with the principle of least privilege mandated by the governing security policy. Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment.

- 2025-07-02: Document any approved deviation in the exceptions register with a scheduled review date. Changes should be staged in a non-production environment and validated against the verification procedure below.

- 2025-04-14: Retain the prior configuration so that a rollback can be performed without rebuilding the host.

- 2026-12-07: When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner. The control exists to keep remediation deterministic so that repeated audits converge on a stable state.

- 2025-03-19: The control supports reproducible builds of the host baseline and simplifies forensic comparison.

- 2024-08-24: Document any approved deviation in the exceptions register with a scheduled review date.

- 2025-06-11: Changes should be staged in a non-production environment and validated against the verification procedure below. Coordinate with the accounts team before altering anything that affects service-account behavior.

- 2025-05-25: Operational experience shows that small deviations here cascade into larger exposure during incident response.

- 2025-05-25: Consistent enforcement reduces the mean time to detect anomalous access across the estate.

- 2026-10-03: Retain the prior configuration so that a rollback can be performed without rebuilding the host.

- 2025-04-15: Coordinate with the accounts team before altering anything that affects service-account behavior.

- 2023-06-24: The control supports reproducible builds of the host baseline and simplifies forensic comparison. The control exists to keep remediation deterministic so that repeated audits converge on a stable state.

- 2024-02-26: Coordinate with the accounts team before altering anything that affects service-account behavior.

- 2026-09-16: Coordinate with the accounts team before altering anything that affects service-account behavior. Prefer explicit values over relying on compiled-in defaults, which may vary between distributions.

- 2024-08-15: Consistent enforcement reduces the mean time to detect anomalous access across the estate. This requirement aligns the gateway with the principle of least privilege mandated by the governing security policy.

- 2024-12-23: Inconsistent application of this requirement across hosts complicates evidence collection and weakens attestations. The control supports reproducible builds of the host baseline and simplifies forensic comparison.

- 2025-12-07: Operators should prefer configuration that is idempotent so that re-running the auditor produces no further changes.

- 2025-07-04: When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner.

- 2024-12-02: Consistent enforcement reduces the mean time to detect anomalous access across the estate.

- 2024-07-14: Adversaries routinely probe for misconfigurations of this control when establishing persistence on laboratory infrastructure.

- 2025-01-22: Retain the prior configuration so that a rollback can be performed without rebuilding the host. The control supports reproducible builds of the host baseline and simplifies forensic comparison.

- 2024-08-15: Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment.

- 2025-08-11: This requirement aligns the gateway with the principle of least privilege mandated by the governing security policy.

- 2024-03-18: Inconsistent application of this requirement across hosts complicates evidence collection and weakens attestations.

- 2025-09-04: Operators should prefer configuration that is idempotent so that re-running the auditor produces no further changes. Prefer explicit values over relying on compiled-in defaults, which may vary between distributions.

- 2025-05-27: Adversaries routinely probe for misconfigurations of this control when establishing persistence on laboratory infrastructure. Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment.

- 2024-08-18: Coordinate with the accounts team before altering anything that affects service-account behavior. Prefer explicit values over relying on compiled-in defaults, which may vary between distributions.

- 2025-02-09: Inconsistent application of this requirement across hosts complicates evidence collection and weakens attestations. Adversaries routinely probe for misconfigurations of this control when establishing persistence on laboratory infrastructure.

- 2023-06-26: Inconsistent application of this requirement across hosts complicates evidence collection and weakens attestations. Consistent enforcement reduces the mean time to detect anomalous access across the estate.

- 2023-04-27: The control exists to keep remediation deterministic so that repeated audits converge on a stable state. Retain the prior configuration so that a rollback can be performed without rebuilding the host.

- 2025-09-08: When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner.


## Appendix G. Amendments (authoritative)


The following amendments are in force and **supersede** the body of the referenced controls per section 1.4. They are listed in effective-date order.


### G-2026-17 — amends HD-SSHD-DROPIN / HD-SSHD-KBDINT

The instruction in HD-SSHD-DROPIN to ignore conditional blocks is superseded. The auditor evaluates the effective value of each sshd keyword for a fixed **audit connection context**: the connecting user is `root` and the source address is `198.51.100.10`. Drop-in fragments are still concatenated in ascending filename order and scanned top to bottom. Lines in global scope (before any `Match`) always apply. A `Match` line opens a conditional block that applies only when ALL of its criteria match the audit context; the supported criteria are: `User <list>` — a comma-separated list of patterns where `*` matches any user and an exact name matches that user, a pattern may be negated with a leading `!`, and a negated pattern that matches causes the criterion to fail, so the criterion matches when the connecting user `root` matches at least one non-negated pattern and no negated pattern; `Group <list>` — matches when `root` is an effective member (per AC-GROUP-EFFECTIVE) of at least one of the comma-separated groups; and `Address <list>` — a comma-separated list of exact IPv4 addresses or IPv4 CIDR ranges (`a.b.c.d/prefix`), matching when the source address `198.51.100.10` equals a listed address or falls within a listed range. `Match all` always applies. A block whose `Match` line contains any other criterion keyword does not apply. The effective value of a keyword is the FIRST occurrence, in concatenated order, that appears in global scope or within an applicable block; occurrences inside non-applicable blocks are skipped. This context evaluation governs HD-SSHD-KBDINT as well.


### G-2026-18 — amends AC-SUDO-NOPASSWD

AC-SUDO-NOPASSWD is host-scoped. Each user specification carries a host field — the token(s) between the principal and the first `=` — which is a comma-separated list of `ALL`, hostnames, or `Host_Alias` names, each optionally negated with a leading `!`. The auditor evaluates rules for the audit host whose hostname is `gw-lab-01`. A specification applies to this host only when its host field resolves to include `gw-lab-01`: `ALL` matches, an exact hostname equal to `gw-lab-01` matches, and a `Host_Alias NAME = ...` (whose members may be hostnames, `ALL`, other host aliases, or negated entries) is resolved recursively. A specification that does not apply to the audit host is ignored entirely and therefore does not participate in the last-match-wins ordering of G-2026-07 for its principal. `Defaults:<binder> !authenticate` overrides are not host-scoped and apply on every host.


### G-2026-09 — amends AC-SUDO-NOPASSWD

Sudoers include directives shall be resolved. A line beginning with `@includedir` or `#includedir` (the leading `#` here is a directive, not a comment) names a drop-in directory supplied in the snapshot under the `sudoers.d` map. Its files are spliced into the policy **in ascending filename order at the position of the directive**, and the resulting lines participate in alias resolution and in the last-match-wins ordering of G-2026-07 exactly as if they had appeared inline. A specification that follows the include directive in the main file is therefore later than any rule contributed by the included files.


### G-2026-12 — amends AU-RETENTION

Audit log retention is extended to 400 days for tier-1 hosts. This amendment does not affect auditor behavior.


### G-2026-05 — amends AC-SUDO-NOPASSWD

In addition to ordinary user specifications, a per-user or per-group `Defaults` override of the form `Defaults:<binder> !authenticate` grants passwordless sudo over the entire command set to `<binder>`, exactly as if that binder held a `NOPASSWD: ALL` user specification. `<binder>` may be a user, a `%group` reference (resolved through AC-GROUP-EFFECTIVE), or a negated principal. This overrides the body of AC-SUDO-NOPASSWD, which otherwise ignores all `Defaults` lines. The resulting principals are subject to the same disabled-account and AC-EXEMPT filtering as any other grant.


### G-2026-02 — amends AC-SUDO-NOPASSWD

A user specification qualifies as granting passwordless sudo only when the `NOPASSWD` tag applies to the entire command set, that is, only when the remainder of the rule contains `NOPASSWD: ALL` (whitespace around the colon is insignificant). Grants that attach `NOPASSWD` to specific commands do not qualify and shall not produce a `sudoers.require_password` patch.


### G-2026-14 — amends MA-PATCH-WINDOW

The maintenance window is shifted by one hour for the eastern region. This amendment does not affect auditor behavior.


### G-2026-10 — amends HD-SSHD-DROPIN

For PermitRootLogin, `without-password` is the deprecated spelling of `prohibit-password` and denotes the same effective setting; it is therefore accepted wherever `prohibit-password` is accepted. The accepted value set for the other keywords is unchanged.


### G-2026-15 — amends AC-SUDO-NOPASSWD

AC-SUDO-NOPASSWD is further narrowed so that a user specification grants reportable passwordless sudo only when the rule permits execution as the superuser. The optional Runas specification is the parenthesized list immediately following the `=` in the rule (for example `(ALL)`, `(root)`, `(www-data)`, or `(ALL:ALL)`); the runas *user* list is the portion before any `:` inside the parentheses. When no Runas specification is present the rule defaults to running as `root`. A `NOPASSWD: ALL` rule whose runas user list contains `root` or `ALL` qualifies; a `NOPASSWD: ALL` rule whose runas user list names only non-root principals does not qualify. Under the last-match-wins ordering of G-2026-07, such a non-qualifying line still names its principal and therefore sets that principal's effective state to not-passwordless, just as an ordinary non-NOPASSWD grant would.


### G-2026-11 — amends LG-BANNER-TEXT

The approved pre-authentication banner wording is updated; see Appendix C. This amendment does not affect auditor behavior.


### G-2026-07 — amends AC-SUDO-NOPASSWD

The accumulation model in the body of AC-SUDO-NOPASSWD is superseded by **last-match-wins** semantics, consistent with how sudo resolves privileges. Process user specifications and `Defaults:<binder> !authenticate` overrides in file order; for each principal, the effective passwordless state is established by the **last** line that names that principal. Consequently a later specification that grants the principal sudo without `NOPASSWD: ALL` revokes a passwordless grant made by an earlier line, and a later `NOPASSWD: ALL` line reinstates it. Group and alias principals are resolved as in the body, and the resulting state is applied to each resolved member.


### G-2026-16 — amends AC-ACCT-LOCK

AC-ACCT-LOCK is extended with an account-expiration criterion. An account is additionally disabled when the account-expiry field of its `shadow` entry — the eighth colon-separated field — is present, non-empty, and a base-ten integer strictly less than the assessment reference day `20620` (counted in days since 1970-01-01). An empty expiry field, or an integer value greater than or equal to `20620`, does not by itself disable the account. This criterion combines with the password-token and login-shell criteria: an account disabled by any one criterion is disabled.


### G-2026-04 — amends HD-SSHD-DROPIN

For `PermitRootLogin` only, the value `prohibit-password` (compared case-insensitively) is an accepted effective value in addition to `no`; an effective value of `prohibit-password` shall not produce a patch. The set of accepted values for `PasswordAuthentication` is unchanged and remains `no` only.


### G-2026-03 — amends AC-EXEMPT

The service-account user-id ceiling in AC-EXEMPT is lowered from `999` to `499`. The exempt-account roster is extended to add `svc_backup`, so the roster is `svc_monitor` and `svc_backup`.


### G-2026-06 — amends HD-SSHD-KBDINT

`ChallengeResponseAuthentication` is the deprecated spelling of `KbdInteractiveAuthentication` and denotes the same effective setting. When computing the effective value for HD-SSHD-KBDINT, occurrences of either keyword shall be treated as the same setting, so the first occurrence of either spelling in drop-in order establishes the effective value. The accepted value set is unchanged and remains `no` only.


### G-2026-13 — amends NW-NTP-SOURCES

The list of approved time sources is revised. This amendment does not affect auditor behavior.


### G-2026-01 — amends AC-ACCT-LOCK / AC-ACCT-SHELL

The locked-password value set in AC-ACCT-LOCK is extended to additionally include the literal value `*LK*`. Independently, the recognized non-interactive shell set in AC-ACCT-SHELL is extended to add `/usr/bin/git-shell` and `/bin/sync`. Accounts matching the extended criteria are disabled.


## Appendix H. Implementation checklist

Implementers should confirm that the auditor, after parsing a host snapshot, produces exactly the patch set implied by the controls above as amended by Appendix G. A host already in compliance must yield an empty patch set.

