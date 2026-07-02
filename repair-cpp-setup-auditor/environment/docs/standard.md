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

Most numbered controls in the body describe enterprise baselines that surround gateway access. Only the controls called out in Appendix H and their Appendix G amendments are implemented by the setup auditor.

### 1.4 Precedence of amendments

This Standard is maintained as a body of numbered controls followed by an authoritative list of amendments in **Appendix G**. Where the body of a control and an amendment in Appendix G disagree, **the amendment in Appendix G governs**. Implementers must therefore read both the relevant control and any amendment that references it before encoding behavior. Amendments that state they do not affect auditor behavior may be noted and disregarded for implementation.


## 2. Definitions


**Account.** An entry in the host `passwd` data with a name, user id, primary group id, and login shell.


**Disabled account.** An account meeting the criteria of control AC-ACCT-LOCK as amended.


**Effective group members.** The membership computed under control AC-GROUP-EFFECTIVE.


**Passwordless sudo.** Sudo authority obtained without a password challenge, as determined under AC-SUDO-NOPASSWD as amended.


**Exempt account.** An account excused from passwordless-sudo remediation under AC-EXEMPT as amended.


**Effective sshd value.** The value computed under HD-SSHD-DROPIN as amended.


**Patch.** A single remediation action proposed by the auditor.


**Normalized inventory.** The intermediate representation produced after parsing, on which the policy rules operate.


## 3. Access Control

The controls in this section apply to all managed hosts. Operational experience shows that small deviations here cascade into larger exposure during incident response.


### AC-001 — Hardened credential rotation

**Domain:** Access Control  **Severity:** Critical  **Applies to:** gateway and bastion hosts

**Rationale.** Inconsistent application of this requirement across hosts complicates evidence collection and weakens attestations.

**Requirement.** Interactive accounts shall be limited to approved shells and home-directory mount options.

**Implementation guidance.** Treat sudoers alias expansion as recursive and guard against self-referential alias loops.

**Verification.** Automated property checks generate varied host states to confirm the control behaves consistently.

**References.** Vendor hardening note VHN-2-0; Lab Operations Runbook ROB-7; Lab Operations Runbook ROB-1; Baseline Configuration Guide BCG-4.9

**Revision history.**
- 2022-07: editorial revision to AC-001; clarified scope and wording.
- 2025-04: editorial revision to AC-001; clarified scope and wording.


### AC-002 — Approved banner presentation

**Domain:** Access Control  **Severity:** Critical  **Applies to:** tier-1 laboratory hosts

**Rationale.** Consistent enforcement reduces the mean time to detect anomalous access across the estate.

**Requirement.** Privilege-bearing group memberships shall be reconciled against the quarterly access review export.

**Implementation guidance.** Treat sudoers alias expansion as recursive and guard against self-referential alias loops.

**Verification.** The verifier records the before and after state for inclusion in the assessment package.

**References.** Governing Security Policy GSP-2024 §3.5; Lab Operations Runbook ROB-1; Baseline Configuration Guide BCG-9.0; Prior assessment finding AF-3

**Revision history.**
- 2022-05: editorial revision to AC-002; clarified scope and wording.
- 2022-06: editorial revision to AC-002; clarified scope and wording.


### AC-003 — Approved module loading

**Domain:** Access Control  **Severity:** Moderate  **Applies to:** gateway and bastion hosts

**Rationale.** This requirement aligns the gateway with the principle of least privilege mandated by the governing security policy.

**Requirement.** Emergency break-glass accounts shall be disabled automatically when their waiver expires.

**Implementation guidance.** Treat sudoers alias expansion as recursive and guard against self-referential alias loops.

**Verification.** Automated property checks generate varied host states to confirm the control behaves consistently.

**References.** Governing Security Policy GSP-2024 §1.4; Prior assessment finding AF-8

**Revision history.**
- 2025-09: editorial revision to AC-003; clarified scope and wording.
- 2023-06: editorial revision to AC-003; clarified scope and wording.
- 2022-05: editorial revision to AC-003; clarified scope and wording.


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


### AC-004 — Restricted banner presentation

**Domain:** Access Control  **Severity:** High  **Applies to:** tier-1 laboratory hosts

**Rationale.** Consistent enforcement reduces the mean time to detect anomalous access across the estate.

**Requirement.** Interactive accounts shall be limited to approved shells and home-directory mount options.

**Implementation guidance.** Treat sudoers alias expansion as recursive and guard against self-referential alias loops.

**Verification.** Automated property checks generate varied host states to confirm the control behaves consistently.

**References.** Lab Operations Runbook ROB-8; Prior assessment finding AF-1

**Revision history.**
- 2023-10: editorial revision to AC-004; clarified scope and wording.
- 2023-11: editorial revision to AC-004; clarified scope and wording.
- 2022-03: editorial revision to AC-004; clarified scope and wording.
- 2024-07: editorial revision to AC-004; clarified scope and wording.


### AC-005 — Mandatory umask default

**Domain:** Access Control  **Severity:** Low  **Applies to:** service-account-bearing hosts

**Rationale.** Adversaries routinely probe for misconfigurations of this control when establishing persistence on laboratory infrastructure.

**Requirement.** Emergency break-glass accounts shall be disabled automatically when their waiver expires.

**Implementation guidance.** Validate `/etc/passwd`, `/etc/shadow`, and `/etc/group` together; partial reads miss effective membership.

**Verification.** Verification is performed by the setup auditor, which compares the host state to the normalized policy expectation.

**References.** Governing Security Policy GSP-2024 §3.7; Lab Operations Runbook ROB-6

**Revision history.**
- 2023-04: editorial revision to AC-005; clarified scope and wording.
- 2022-04: editorial revision to AC-005; clarified scope and wording.
- 2024-08: editorial revision to AC-005; clarified scope and wording.
- 2023-06: editorial revision to AC-005; clarified scope and wording.


### AC-006 — Mandatory time synchronization

**Domain:** Access Control  **Severity:** High  **Applies to:** shared interactive hosts

**Rationale.** Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment.

**Requirement.** Shared interactive accounts are prohibited except where explicitly registered in Appendix A.

**Implementation guidance.** Treat sudoers alias expansion as recursive and guard against self-referential alias loops.

**Verification.** Evidence is the auditor's proposed patch set; a compliant host yields an empty set for this control.

**References.** Baseline Configuration Guide BCG-1.8; Vendor hardening note VHN-9-9; Governing Security Policy GSP-2024 §2.7

**Revision history.**
- 2023-04: editorial revision to AC-006; clarified scope and wording.
- 2022-03: editorial revision to AC-006; clarified scope and wording.


### AC-007 — Approved kernel parameter

**Domain:** Access Control  **Severity:** Moderate  **Applies to:** tier-1 laboratory hosts

**Rationale.** Consistent enforcement reduces the mean time to detect anomalous access across the estate.

**Requirement.** Privilege-bearing group memberships shall be reconciled against the quarterly access review export.

**Implementation guidance.** Treat sudoers alias expansion as recursive and guard against self-referential alias loops.

**Verification.** Automated property checks generate varied host states to confirm the control behaves consistently.

**References.** Baseline Configuration Guide BCG-7.3; Vendor hardening note VHN-3-0

**Revision history.**
- 2023-03: editorial revision to AC-007; clarified scope and wording.
- 2023-08: editorial revision to AC-007; clarified scope and wording.
- 2022-07: editorial revision to AC-007; clarified scope and wording.


### AC-008 — Centralized umask default

**Domain:** Access Control  **Severity:** Moderate  **Applies to:** shared interactive hosts

**Rationale.** The control supports reproducible builds of the host baseline and simplifies forensic comparison.

**Requirement.** Privilege-bearing group memberships shall be reconciled against the quarterly access review export.

**Implementation guidance.** Validate `/etc/passwd`, `/etc/shadow`, and `/etc/group` together; partial reads miss effective membership.

**Verification.** Verification is performed by the setup auditor, which compares the host state to the normalized policy expectation.

**References.** Governing Security Policy GSP-2024 §6.3; Vendor hardening note VHN-4-3; Baseline Configuration Guide BCG-2.4

**Revision history.**
- 2023-02: editorial revision to AC-008; clarified scope and wording.
- 2022-09: editorial revision to AC-008; clarified scope and wording.


### AC-009 — Standard package provenance

**Domain:** Access Control  **Severity:** Critical  **Applies to:** shared interactive hosts

**Rationale.** The control supports reproducible builds of the host baseline and simplifies forensic comparison.

**Requirement.** Emergency break-glass accounts shall be disabled automatically when their waiver expires.

**Implementation guidance.** Treat sudoers alias expansion as recursive and guard against self-referential alias loops.

**Verification.** The verifier records the before and after state for inclusion in the assessment package.

**References.** Baseline Configuration Guide BCG-2.3; Governing Security Policy GSP-2024 §7.0; Governing Security Policy GSP-2024 §3.5; Vendor hardening note VHN-7-8

**Revision history.**
- 2022-09: editorial revision to AC-009; clarified scope and wording.
- 2023-01: editorial revision to AC-009; clarified scope and wording.


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


### AC-010 — Baseline session timeout

**Domain:** Access Control  **Severity:** Critical  **Applies to:** all managed hosts

**Rationale.** Inconsistent application of this requirement across hosts complicates evidence collection and weakens attestations.

**Requirement.** Shared interactive accounts are prohibited except where explicitly registered in Appendix A.

**Implementation guidance.** Treat sudoers alias expansion as recursive and guard against self-referential alias loops.

**Verification.** Automated property checks generate varied host states to confirm the control behaves consistently.

**References.** Baseline Configuration Guide BCG-9.2; Vendor hardening note VHN-9-2

**Revision history.**
- 2024-12: editorial revision to AC-010; clarified scope and wording.
- 2024-08: editorial revision to AC-010; clarified scope and wording.
- 2022-11: editorial revision to AC-010; clarified scope and wording.


### AC-011 — Restricted service enablement

**Domain:** Access Control  **Severity:** High  **Applies to:** all managed hosts

**Rationale.** The control supports reproducible builds of the host baseline and simplifies forensic comparison.

**Requirement.** Interactive accounts shall be limited to approved shells and home-directory mount options.

**Implementation guidance.** Validate `/etc/passwd`, `/etc/shadow`, and `/etc/group` together; partial reads miss effective membership.

**Verification.** Assessors may re-run the audit after applying patches to confirm the host has converged.

**References.** Lab Operations Runbook ROB-7; Baseline Configuration Guide BCG-7.7

**Revision history.**
- 2022-10: editorial revision to AC-011; clarified scope and wording.
- 2024-10: editorial revision to AC-011; clarified scope and wording.
- 2023-09: editorial revision to AC-011; clarified scope and wording.


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


### AC-012 — Monitored boot integrity

**Domain:** Access Control  **Severity:** Low  **Applies to:** shared interactive hosts

**Rationale.** Operational experience shows that small deviations here cascade into larger exposure during incident response.

**Requirement.** Interactive accounts shall be limited to approved shells and home-directory mount options.

**Implementation guidance.** Validate `/etc/passwd`, `/etc/shadow`, and `/etc/group` together; partial reads miss effective membership.

**Verification.** Evidence is the auditor's proposed patch set; a compliant host yields an empty set for this control.

**References.** Lab Operations Runbook ROB-2; Prior assessment finding AF-7

**Revision history.**
- 2022-07: editorial revision to AC-012; clarified scope and wording.
- 2024-11: editorial revision to AC-012; clarified scope and wording.
- 2024-01: editorial revision to AC-012; clarified scope and wording.


### AC-013 — Approved umask default

**Domain:** Access Control  **Severity:** High  **Applies to:** shared interactive hosts

**Rationale.** This requirement aligns the gateway with the principle of least privilege mandated by the governing security policy.

**Requirement.** Interactive accounts shall be limited to approved shells and home-directory mount options.

**Implementation guidance.** Treat sudoers alias expansion as recursive and guard against self-referential alias loops.

**Verification.** Automated property checks generate varied host states to confirm the control behaves consistently.

**References.** Prior assessment finding AF-5; Prior assessment finding AF-3; Baseline Configuration Guide BCG-8.7

**Revision history.**
- 2023-12: editorial revision to AC-013; clarified scope and wording.
- 2025-10: editorial revision to AC-013; clarified scope and wording.
- 2024-01: editorial revision to AC-013; clarified scope and wording.
- 2025-07: editorial revision to AC-013; clarified scope and wording.


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


### AC-014 — Verified log forwarding

**Domain:** Access Control  **Severity:** Critical  **Applies to:** tier-1 laboratory hosts

**Rationale.** Operational experience shows that small deviations here cascade into larger exposure during incident response.

**Requirement.** Privilege-bearing group memberships shall be reconciled against the quarterly access review export.

**Implementation guidance.** Validate `/etc/passwd`, `/etc/shadow`, and `/etc/group` together; partial reads miss effective membership.

**Verification.** Verification is performed by the setup auditor, which compares the host state to the normalized policy expectation.

**References.** Prior assessment finding AF-7; Prior assessment finding AF-6; Vendor hardening note VHN-7-6; Lab Operations Runbook ROB-6

**Revision history.**
- 2024-11: editorial revision to AC-014; clarified scope and wording.
- 2023-06: editorial revision to AC-014; clarified scope and wording.


### AC-015 — Controlled package provenance

**Domain:** Access Control  **Severity:** Critical  **Applies to:** all managed hosts

**Rationale.** Consistent enforcement reduces the mean time to detect anomalous access across the estate.

**Requirement.** Privilege-bearing group memberships shall be reconciled against the quarterly access review export.

**Implementation guidance.** Treat sudoers alias expansion as recursive and guard against self-referential alias loops.

**Verification.** The verifier records the before and after state for inclusion in the assessment package.

**References.** Vendor hardening note VHN-8-1; Prior assessment finding AF-2; Prior assessment finding AF-1; Baseline Configuration Guide BCG-6.2

**Revision history.**
- 2023-05: editorial revision to AC-015; clarified scope and wording.
- 2022-08: editorial revision to AC-015; clarified scope and wording.
- 2023-08: editorial revision to AC-015; clarified scope and wording.


### AC-KEY-REVOKE — Revocation of keys for disabled accounts

**Domain:** Access Control  **Severity:** High  **Applies to:** all managed hosts

**Rationale.** A disabled account that retains authorized keys remains a usable entry point and must be remediated.

**Requirement.** An account is deemed to **possess keys** when its `authorized_keys` content contains at least one line that is neither blank nor a comment (a line whose first non-whitespace character is `#`). For every account that possesses keys and is disabled per AC-ACCT-LOCK, the auditor shall propose `ssh.revoke_keys` for that account.

**Implementation guidance.** Whitespace-only lines and comment lines do not constitute possession of keys.

**Verification.** A compliant host has no disabled account that possesses keys.

**References.** Baseline Configuration Guide BCG-4.1

**Revision history.**
- 2023-04: initial publication.


### AC-016 — Verified core dump handling

**Domain:** Access Control  **Severity:** Critical  **Applies to:** all managed hosts

**Rationale.** Consistent enforcement reduces the mean time to detect anomalous access across the estate.

**Requirement.** Emergency break-glass accounts shall be disabled automatically when their waiver expires.

**Implementation guidance.** Treat sudoers alias expansion as recursive and guard against self-referential alias loops.

**Verification.** Evidence is the auditor's proposed patch set; a compliant host yields an empty set for this control.

**References.** Lab Operations Runbook ROB-2; Vendor hardening note VHN-5-2; Governing Security Policy GSP-2024 §6.2

**Revision history.**
- 2025-06: editorial revision to AC-016; clarified scope and wording.
- 2025-02: editorial revision to AC-016; clarified scope and wording.
- 2023-10: editorial revision to AC-016; clarified scope and wording.


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

The controls in this section apply to service-account-bearing hosts. Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment.


### AU-001 — Monitored boot integrity

**Domain:** Audit and Accountability  **Severity:** High  **Applies to:** service-account-bearing hosts

**Rationale.** The control exists to keep remediation deterministic so that repeated audits converge on a stable state.

**Requirement.** Local retention shall not truncate records needed for the current assessment cycle.

**Implementation guidance.** Separate durable audit storage from ephemeral container layers on gateway hosts.

**Verification.** Assessors may re-run the audit after applying patches to confirm the host has converged.

**References.** Prior assessment finding AF-7; Baseline Configuration Guide BCG-3.1; Governing Security Policy GSP-2024 §3.2

**Revision history.**
- 2022-12: editorial revision to AU-001; clarified scope and wording.
- 2023-09: editorial revision to AU-001; clarified scope and wording.
- 2024-05: editorial revision to AU-001; clarified scope and wording.
- 2025-03: editorial revision to AU-001; clarified scope and wording.


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


### AU-002 — Monitored package provenance

**Domain:** Audit and Accountability  **Severity:** High  **Applies to:** tier-1 laboratory hosts

**Rationale.** Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment.

**Requirement.** Local retention shall not truncate records needed for the current assessment cycle.

**Implementation guidance.** When migrating ledger formats, never discard historical rows during in-place upgrades.

**Verification.** The verifier records the before and after state for inclusion in the assessment package.

**References.** Baseline Configuration Guide BCG-1.7; Vendor hardening note VHN-1-0; Vendor hardening note VHN-2-0

**Revision history.**
- 2023-11: editorial revision to AU-002; clarified scope and wording.
- 2022-02: editorial revision to AU-002; clarified scope and wording.
- 2025-04: editorial revision to AU-002; clarified scope and wording.


### AU-003 — Baseline core dump handling

**Domain:** Audit and Accountability  **Severity:** Low  **Applies to:** tier-1 laboratory hosts

**Rationale.** Operational experience shows that small deviations here cascade into larger exposure during incident response.

**Requirement.** Local retention shall not truncate records needed for the current assessment cycle.

**Implementation guidance.** When migrating ledger formats, never discard historical rows during in-place upgrades.

**Verification.** Automated property checks generate varied host states to confirm the control behaves consistently.

**References.** Baseline Configuration Guide BCG-5.0; Baseline Configuration Guide BCG-8.9; Lab Operations Runbook ROB-8

**Revision history.**
- 2024-10: editorial revision to AU-003; clarified scope and wording.
- 2022-06: editorial revision to AU-003; clarified scope and wording.
- 2024-04: editorial revision to AU-003; clarified scope and wording.
- 2022-06: editorial revision to AU-003; clarified scope and wording.


### AU-004 — Restricted umask default

**Domain:** Audit and Accountability  **Severity:** High  **Applies to:** all managed hosts

**Rationale.** Inconsistent application of this requirement across hosts complicates evidence collection and weakens attestations.

**Requirement.** Security-relevant events shall be forwarded to the central collector with monotonic timestamps.

**Implementation guidance.** Separate durable audit storage from ephemeral container layers on gateway hosts.

**Verification.** Automated property checks generate varied host states to confirm the control behaves consistently.

**References.** Vendor hardening note VHN-7-6; Vendor hardening note VHN-5-8

**Revision history.**
- 2025-12: editorial revision to AU-004; clarified scope and wording.
- 2023-04: editorial revision to AU-004; clarified scope and wording.
- 2023-03: editorial revision to AU-004; clarified scope and wording.


### AU-005 — Controlled log forwarding

**Domain:** Audit and Accountability  **Severity:** Low  **Applies to:** tier-1 laboratory hosts

**Rationale.** Consistent enforcement reduces the mean time to detect anomalous access across the estate.

**Requirement.** Security-relevant events shall be forwarded to the central collector with monotonic timestamps.

**Implementation guidance.** Separate durable audit storage from ephemeral container layers on gateway hosts.

**Verification.** Automated property checks generate varied host states to confirm the control behaves consistently.

**References.** Vendor hardening note VHN-6-3; Lab Operations Runbook ROB-5; Vendor hardening note VHN-7-4; Vendor hardening note VHN-2-7

**Revision history.**
- 2024-05: editorial revision to AU-005; clarified scope and wording.
- 2022-03: editorial revision to AU-005; clarified scope and wording.


### AU-006 — Mandatory session timeout

**Domain:** Audit and Accountability  **Severity:** Moderate  **Applies to:** tier-1 laboratory hosts

**Rationale.** Operational experience shows that small deviations here cascade into larger exposure during incident response.

**Requirement.** Security-relevant events shall be forwarded to the central collector with monotonic timestamps.

**Implementation guidance.** Separate durable audit storage from ephemeral container layers on gateway hosts.

**Verification.** Assessors may re-run the audit after applying patches to confirm the host has converged.

**References.** Baseline Configuration Guide BCG-6.5; Lab Operations Runbook ROB-1; Governing Security Policy GSP-2024 §2.9

**Revision history.**
- 2022-03: editorial revision to AU-006; clarified scope and wording.
- 2024-11: editorial revision to AU-006; clarified scope and wording.


### AU-007 — Restricted session timeout

**Domain:** Audit and Accountability  **Severity:** Low  **Applies to:** gateway and bastion hosts

**Rationale.** Inconsistent application of this requirement across hosts complicates evidence collection and weakens attestations.

**Requirement.** Local retention shall not truncate records needed for the current assessment cycle.

**Implementation guidance.** When migrating ledger formats, never discard historical rows during in-place upgrades.

**Verification.** Evidence is the auditor's proposed patch set; a compliant host yields an empty set for this control.

**References.** Governing Security Policy GSP-2024 §3.9; Governing Security Policy GSP-2024 §5.6

**Revision history.**
- 2023-06: editorial revision to AU-007; clarified scope and wording.
- 2022-05: editorial revision to AU-007; clarified scope and wording.
- 2022-11: editorial revision to AU-007; clarified scope and wording.


### AU-008 — Controlled umask default

**Domain:** Audit and Accountability  **Severity:** Moderate  **Applies to:** shared interactive hosts

**Rationale.** Inconsistent application of this requirement across hosts complicates evidence collection and weakens attestations.

**Requirement.** Audit pipelines shall preserve ordering for correlated sign-in and privilege-use events.

**Implementation guidance.** When migrating ledger formats, never discard historical rows during in-place upgrades.

**Verification.** The verifier records the before and after state for inclusion in the assessment package.

**References.** Baseline Configuration Guide BCG-9.5; Governing Security Policy GSP-2024 §7.5; Vendor hardening note VHN-2-7

**Revision history.**
- 2024-05: editorial revision to AU-008; clarified scope and wording.
- 2024-11: editorial revision to AU-008; clarified scope and wording.


### AU-009 — Monitored session timeout

**Domain:** Audit and Accountability  **Severity:** Moderate  **Applies to:** gateway and bastion hosts

**Rationale.** This requirement aligns the gateway with the principle of least privilege mandated by the governing security policy.

**Requirement.** Audit pipelines shall preserve ordering for correlated sign-in and privilege-use events.

**Implementation guidance.** Separate durable audit storage from ephemeral container layers on gateway hosts.

**Verification.** Automated property checks generate varied host states to confirm the control behaves consistently.

**References.** Lab Operations Runbook ROB-7; Vendor hardening note VHN-1-1; Baseline Configuration Guide BCG-1.4

**Revision history.**
- 2022-12: editorial revision to AU-009; clarified scope and wording.
- 2022-04: editorial revision to AU-009; clarified scope and wording.


### AU-010 — Hardened boot integrity

**Domain:** Audit and Accountability  **Severity:** Low  **Applies to:** gateway and bastion hosts

**Rationale.** The control exists to keep remediation deterministic so that repeated audits converge on a stable state.

**Requirement.** Audit pipelines shall preserve ordering for correlated sign-in and privilege-use events.

**Implementation guidance.** Separate durable audit storage from ephemeral container layers on gateway hosts.

**Verification.** Verification is performed by the setup auditor, which compares the host state to the normalized policy expectation.

**References.** Lab Operations Runbook ROB-4; Lab Operations Runbook ROB-3

**Revision history.**
- 2025-05: editorial revision to AU-010; clarified scope and wording.
- 2025-01: editorial revision to AU-010; clarified scope and wording.


### AU-011 — Approved service enablement

**Domain:** Audit and Accountability  **Severity:** Low  **Applies to:** service-account-bearing hosts

**Rationale.** Adversaries routinely probe for misconfigurations of this control when establishing persistence on laboratory infrastructure.

**Requirement.** Security-relevant events shall be forwarded to the central collector with monotonic timestamps.

**Implementation guidance.** Separate durable audit storage from ephemeral container layers on gateway hosts.

**Verification.** Evidence is the auditor's proposed patch set; a compliant host yields an empty set for this control.

**References.** Vendor hardening note VHN-1-2; Governing Security Policy GSP-2024 §5.6; Governing Security Policy GSP-2024 §7.3

**Revision history.**
- 2024-03: editorial revision to AU-011; clarified scope and wording.
- 2024-02: editorial revision to AU-011; clarified scope and wording.


### AU-012 — Hardened credential rotation

**Domain:** Audit and Accountability  **Severity:** High  **Applies to:** tier-1 laboratory hosts

**Rationale.** The control exists to keep remediation deterministic so that repeated audits converge on a stable state.

**Requirement.** Local retention shall not truncate records needed for the current assessment cycle.

**Implementation guidance.** When migrating ledger formats, never discard historical rows during in-place upgrades.

**Verification.** The verifier records the before and after state for inclusion in the assessment package.

**References.** Vendor hardening note VHN-1-1; Lab Operations Runbook ROB-8

**Revision history.**
- 2025-04: editorial revision to AU-012; clarified scope and wording.
- 2025-03: editorial revision to AU-012; clarified scope and wording.
- 2025-03: editorial revision to AU-012; clarified scope and wording.
- 2022-02: editorial revision to AU-012; clarified scope and wording.


### AU-013 — Verified banner presentation

**Domain:** Audit and Accountability  **Severity:** Moderate  **Applies to:** all managed hosts

**Rationale.** Adversaries routinely probe for misconfigurations of this control when establishing persistence on laboratory infrastructure.

**Requirement.** Security-relevant events shall be forwarded to the central collector with monotonic timestamps.

**Implementation guidance.** When migrating ledger formats, never discard historical rows during in-place upgrades.

**Verification.** The verifier records the before and after state for inclusion in the assessment package.

**References.** Vendor hardening note VHN-4-3; Governing Security Policy GSP-2024 §5.0; Prior assessment finding AF-8

**Revision history.**
- 2024-02: editorial revision to AU-013; clarified scope and wording.
- 2024-04: editorial revision to AU-013; clarified scope and wording.
- 2025-02: editorial revision to AU-013; clarified scope and wording.
- 2024-03: editorial revision to AU-013; clarified scope and wording.


### AU-014 — Approved service enablement

**Domain:** Audit and Accountability  **Severity:** Low  **Applies to:** shared interactive hosts

**Rationale.** The control exists to keep remediation deterministic so that repeated audits converge on a stable state.

**Requirement.** Security-relevant events shall be forwarded to the central collector with monotonic timestamps.

**Implementation guidance.** When migrating ledger formats, never discard historical rows during in-place upgrades.

**Verification.** Evidence is the auditor's proposed patch set; a compliant host yields an empty set for this control.

**References.** Baseline Configuration Guide BCG-4.7; Prior assessment finding AF-2; Lab Operations Runbook ROB-6; Prior assessment finding AF-5

**Revision history.**
- 2024-12: editorial revision to AU-014; clarified scope and wording.
- 2022-03: editorial revision to AU-014; clarified scope and wording.


### AU-015 — Mandatory module loading

**Domain:** Audit and Accountability  **Severity:** Moderate  **Applies to:** all managed hosts

**Rationale.** The control exists to keep remediation deterministic so that repeated audits converge on a stable state.

**Requirement.** Local retention shall not truncate records needed for the current assessment cycle.

**Implementation guidance.** When migrating ledger formats, never discard historical rows during in-place upgrades.

**Verification.** The verifier records the before and after state for inclusion in the assessment package.

**References.** Lab Operations Runbook ROB-5; Prior assessment finding AF-4

**Revision history.**
- 2025-12: editorial revision to AU-015; clarified scope and wording.
- 2024-07: editorial revision to AU-015; clarified scope and wording.
- 2025-08: editorial revision to AU-015; clarified scope and wording.


### AU-016 — Restricted service enablement

**Domain:** Audit and Accountability  **Severity:** Moderate  **Applies to:** gateway and bastion hosts

**Rationale.** Adversaries routinely probe for misconfigurations of this control when establishing persistence on laboratory infrastructure.

**Requirement.** Audit pipelines shall preserve ordering for correlated sign-in and privilege-use events.

**Implementation guidance.** Separate durable audit storage from ephemeral container layers on gateway hosts.

**Verification.** Assessors may re-run the audit after applying patches to confirm the host has converged.

**References.** Vendor hardening note VHN-1-8; Governing Security Policy GSP-2024 §2.1; Governing Security Policy GSP-2024 §1.3; Prior assessment finding AF-8

**Revision history.**
- 2022-12: editorial revision to AU-016; clarified scope and wording.
- 2022-09: editorial revision to AU-016; clarified scope and wording.


### AU-017 — Restricted session timeout

**Domain:** Audit and Accountability  **Severity:** High  **Applies to:** all managed hosts

**Rationale.** Operational experience shows that small deviations here cascade into larger exposure during incident response.

**Requirement.** Audit pipelines shall preserve ordering for correlated sign-in and privilege-use events.

**Implementation guidance.** When migrating ledger formats, never discard historical rows during in-place upgrades.

**Verification.** Automated property checks generate varied host states to confirm the control behaves consistently.

**References.** Vendor hardening note VHN-6-7; Vendor hardening note VHN-2-9; Lab Operations Runbook ROB-7; Governing Security Policy GSP-2024 §9.3

**Revision history.**
- 2023-08: editorial revision to AU-017; clarified scope and wording.
- 2022-12: editorial revision to AU-017; clarified scope and wording.
- 2024-04: editorial revision to AU-017; clarified scope and wording.


## 5. Configuration Management

The controls in this section apply to shared interactive hosts. The control exists to keep remediation deterministic so that repeated audits converge on a stable state.


### CM-001 — Approved module loading

**Domain:** Configuration Management  **Severity:** High  **Applies to:** tier-1 laboratory hosts

**Rationale.** Operational experience shows that small deviations here cascade into larger exposure during incident response.

**Requirement.** Configuration files under management shall include a checksum in the host inventory.

**Implementation guidance.** Store rendered configuration in `/etc` only after the change ticket is approved.

**Verification.** Automated property checks generate varied host states to confirm the control behaves consistently.

**References.** Governing Security Policy GSP-2024 §9.0; Governing Security Policy GSP-2024 §3.8

**Revision history.**
- 2023-07: editorial revision to CM-001; clarified scope and wording.
- 2022-06: editorial revision to CM-001; clarified scope and wording.
- 2024-03: editorial revision to CM-001; clarified scope and wording.
- 2022-03: editorial revision to CM-001; clarified scope and wording.


### CM-002 — Centralized service enablement

**Domain:** Configuration Management  **Severity:** Low  **Applies to:** gateway and bastion hosts

**Rationale.** The control exists to keep remediation deterministic so that repeated audits converge on a stable state.

**Requirement.** Configuration files under management shall include a checksum in the host inventory.

**Implementation guidance.** Store rendered configuration in `/etc` only after the change ticket is approved.

**Verification.** Automated property checks generate varied host states to confirm the control behaves consistently.

**References.** Prior assessment finding AF-7; Lab Operations Runbook ROB-7; Vendor hardening note VHN-9-0; Baseline Configuration Guide BCG-8.5

**Revision history.**
- 2024-11: editorial revision to CM-002; clarified scope and wording.
- 2024-07: editorial revision to CM-002; clarified scope and wording.
- 2024-05: editorial revision to CM-002; clarified scope and wording.


### CM-003 — Monitored session timeout

**Domain:** Configuration Management  **Severity:** Moderate  **Applies to:** shared interactive hosts

**Rationale.** The control supports reproducible builds of the host baseline and simplifies forensic comparison.

**Requirement.** Drift detection jobs shall run before nightly backup windows on gateway hosts.

**Implementation guidance.** Store rendered configuration in `/etc` only after the change ticket is approved.

**Verification.** The verifier records the before and after state for inclusion in the assessment package.

**References.** Lab Operations Runbook ROB-1; Vendor hardening note VHN-3-8; Governing Security Policy GSP-2024 §6.3; Baseline Configuration Guide BCG-7.6

**Revision history.**
- 2022-11: editorial revision to CM-003; clarified scope and wording.
- 2023-07: editorial revision to CM-003; clarified scope and wording.


### CM-004 — Verified filesystem mount option

**Domain:** Configuration Management  **Severity:** Moderate  **Applies to:** tier-1 laboratory hosts

**Rationale.** The control exists to keep remediation deterministic so that repeated audits converge on a stable state.

**Requirement.** Baseline packages shall be installed only from the approved internal mirror.

**Implementation guidance.** Compare rendered files against the last known-good snapshot before closing a change.

**Verification.** Automated property checks generate varied host states to confirm the control behaves consistently.

**References.** Vendor hardening note VHN-1-3; Baseline Configuration Guide BCG-4.5

**Revision history.**
- 2022-06: editorial revision to CM-004; clarified scope and wording.
- 2024-10: editorial revision to CM-004; clarified scope and wording.


### CM-005 — Approved banner presentation

**Domain:** Configuration Management  **Severity:** Critical  **Applies to:** gateway and bastion hosts

**Rationale.** Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment.

**Requirement.** Configuration files under management shall include a checksum in the host inventory.

**Implementation guidance.** Compare rendered files against the last known-good snapshot before closing a change.

**Verification.** Evidence is the auditor's proposed patch set; a compliant host yields an empty set for this control.

**References.** Vendor hardening note VHN-2-5; Lab Operations Runbook ROB-1; Vendor hardening note VHN-4-8

**Revision history.**
- 2022-02: editorial revision to CM-005; clarified scope and wording.
- 2023-01: editorial revision to CM-005; clarified scope and wording.
- 2024-01: editorial revision to CM-005; clarified scope and wording.


### CM-006 — Approved interface configuration

**Domain:** Configuration Management  **Severity:** Low  **Applies to:** service-account-bearing hosts

**Rationale.** The control exists to keep remediation deterministic so that repeated audits converge on a stable state.

**Requirement.** Baseline packages shall be installed only from the approved internal mirror.

**Implementation guidance.** Compare rendered files against the last known-good snapshot before closing a change.

**Verification.** Evidence is the auditor's proposed patch set; a compliant host yields an empty set for this control.

**References.** Vendor hardening note VHN-4-9; Vendor hardening note VHN-8-3; Prior assessment finding AF-8; Baseline Configuration Guide BCG-7.4

**Revision history.**
- 2023-11: editorial revision to CM-006; clarified scope and wording.
- 2024-05: editorial revision to CM-006; clarified scope and wording.


### CM-007 — Mandatory log forwarding

**Domain:** Configuration Management  **Severity:** Moderate  **Applies to:** service-account-bearing hosts

**Rationale.** Operational experience shows that small deviations here cascade into larger exposure during incident response.

**Requirement.** Configuration files under management shall include a checksum in the host inventory.

**Implementation guidance.** Store rendered configuration in `/etc` only after the change ticket is approved.

**Verification.** Assessors may re-run the audit after applying patches to confirm the host has converged.

**References.** Prior assessment finding AF-3; Baseline Configuration Guide BCG-9.1

**Revision history.**
- 2022-04: editorial revision to CM-007; clarified scope and wording.
- 2025-05: editorial revision to CM-007; clarified scope and wording.
- 2025-11: editorial revision to CM-007; clarified scope and wording.


### CM-008 — Mandatory boot integrity

**Domain:** Configuration Management  **Severity:** Critical  **Applies to:** gateway and bastion hosts

**Rationale.** Operational experience shows that small deviations here cascade into larger exposure during incident response.

**Requirement.** Drift detection jobs shall run before nightly backup windows on gateway hosts.

**Implementation guidance.** Store rendered configuration in `/etc` only after the change ticket is approved.

**Verification.** Automated property checks generate varied host states to confirm the control behaves consistently.

**References.** Vendor hardening note VHN-4-0; Prior assessment finding AF-5

**Revision history.**
- 2024-06: editorial revision to CM-008; clarified scope and wording.
- 2024-08: editorial revision to CM-008; clarified scope and wording.
- 2023-02: editorial revision to CM-008; clarified scope and wording.
- 2023-06: editorial revision to CM-008; clarified scope and wording.


### CM-009 — Mandatory interface configuration

**Domain:** Configuration Management  **Severity:** Low  **Applies to:** service-account-bearing hosts

**Rationale.** This requirement aligns the gateway with the principle of least privilege mandated by the governing security policy.

**Requirement.** Baseline packages shall be installed only from the approved internal mirror.

**Implementation guidance.** Store rendered configuration in `/etc` only after the change ticket is approved.

**Verification.** Assessors may re-run the audit after applying patches to confirm the host has converged.

**References.** Vendor hardening note VHN-3-4; Lab Operations Runbook ROB-8; Governing Security Policy GSP-2024 §8.1

**Revision history.**
- 2022-08: editorial revision to CM-009; clarified scope and wording.
- 2025-08: editorial revision to CM-009; clarified scope and wording.
- 2023-04: editorial revision to CM-009; clarified scope and wording.
- 2025-06: editorial revision to CM-009; clarified scope and wording.


### CM-010 — Centralized banner presentation

**Domain:** Configuration Management  **Severity:** Low  **Applies to:** gateway and bastion hosts

**Rationale.** Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment.

**Requirement.** Drift detection jobs shall run before nightly backup windows on gateway hosts.

**Implementation guidance.** Compare rendered files against the last known-good snapshot before closing a change.

**Verification.** Evidence is the auditor's proposed patch set; a compliant host yields an empty set for this control.

**References.** Prior assessment finding AF-7; Lab Operations Runbook ROB-8; Prior assessment finding AF-9

**Revision history.**
- 2023-06: editorial revision to CM-010; clarified scope and wording.
- 2023-01: editorial revision to CM-010; clarified scope and wording.


### CM-011 — Standard kernel parameter

**Domain:** Configuration Management  **Severity:** Moderate  **Applies to:** all managed hosts

**Rationale.** Adversaries routinely probe for misconfigurations of this control when establishing persistence on laboratory infrastructure.

**Requirement.** Drift detection jobs shall run before nightly backup windows on gateway hosts.

**Implementation guidance.** Store rendered configuration in `/etc` only after the change ticket is approved.

**Verification.** Verification is performed by the setup auditor, which compares the host state to the normalized policy expectation.

**References.** Baseline Configuration Guide BCG-2.5; Vendor hardening note VHN-5-2; Prior assessment finding AF-1; Vendor hardening note VHN-6-8

**Revision history.**
- 2024-12: editorial revision to CM-011; clarified scope and wording.
- 2025-11: editorial revision to CM-011; clarified scope and wording.
- 2024-09: editorial revision to CM-011; clarified scope and wording.


### CM-012 — Verified kernel parameter

**Domain:** Configuration Management  **Severity:** Moderate  **Applies to:** gateway and bastion hosts

**Rationale.** Inconsistent application of this requirement across hosts complicates evidence collection and weakens attestations.

**Requirement.** Baseline packages shall be installed only from the approved internal mirror.

**Implementation guidance.** Store rendered configuration in `/etc` only after the change ticket is approved.

**Verification.** Automated property checks generate varied host states to confirm the control behaves consistently.

**References.** Vendor hardening note VHN-4-9; Prior assessment finding AF-9; Governing Security Policy GSP-2024 §8.8

**Revision history.**
- 2022-03: editorial revision to CM-012; clarified scope and wording.
- 2023-05: editorial revision to CM-012; clarified scope and wording.
- 2025-12: editorial revision to CM-012; clarified scope and wording.
- 2022-02: editorial revision to CM-012; clarified scope and wording.


### CM-013 — Approved filesystem mount option

**Domain:** Configuration Management  **Severity:** Moderate  **Applies to:** gateway and bastion hosts

**Rationale.** Operational experience shows that small deviations here cascade into larger exposure during incident response.

**Requirement.** Baseline packages shall be installed only from the approved internal mirror.

**Implementation guidance.** Compare rendered files against the last known-good snapshot before closing a change.

**Verification.** Automated property checks generate varied host states to confirm the control behaves consistently.

**References.** Vendor hardening note VHN-6-4; Vendor hardening note VHN-4-7; Prior assessment finding AF-8

**Revision history.**
- 2022-11: editorial revision to CM-013; clarified scope and wording.
- 2023-07: editorial revision to CM-013; clarified scope and wording.


### CM-014 — Baseline kernel parameter

**Domain:** Configuration Management  **Severity:** Moderate  **Applies to:** gateway and bastion hosts

**Rationale.** Consistent enforcement reduces the mean time to detect anomalous access across the estate.

**Requirement.** Configuration files under management shall include a checksum in the host inventory.

**Implementation guidance.** Compare rendered files against the last known-good snapshot before closing a change.

**Verification.** Automated property checks generate varied host states to confirm the control behaves consistently.

**References.** Prior assessment finding AF-2; Prior assessment finding AF-6; Vendor hardening note VHN-6-5

**Revision history.**
- 2024-04: editorial revision to CM-014; clarified scope and wording.
- 2024-12: editorial revision to CM-014; clarified scope and wording.


### CM-015 — Monitored banner presentation

**Domain:** Configuration Management  **Severity:** Critical  **Applies to:** tier-1 laboratory hosts

**Rationale.** Operational experience shows that small deviations here cascade into larger exposure during incident response.

**Requirement.** Configuration files under management shall include a checksum in the host inventory.

**Implementation guidance.** Store rendered configuration in `/etc` only after the change ticket is approved.

**Verification.** Automated property checks generate varied host states to confirm the control behaves consistently.

**References.** Lab Operations Runbook ROB-1; Prior assessment finding AF-1; Governing Security Policy GSP-2024 §8.5

**Revision history.**
- 2025-11: editorial revision to CM-015; clarified scope and wording.
- 2024-05: editorial revision to CM-015; clarified scope and wording.


### CM-016 — Mandatory module loading

**Domain:** Configuration Management  **Severity:** Critical  **Applies to:** service-account-bearing hosts

**Rationale.** Consistent enforcement reduces the mean time to detect anomalous access across the estate.

**Requirement.** Baseline packages shall be installed only from the approved internal mirror.

**Implementation guidance.** Compare rendered files against the last known-good snapshot before closing a change.

**Verification.** Evidence is the auditor's proposed patch set; a compliant host yields an empty set for this control.

**References.** Baseline Configuration Guide BCG-5.2; Vendor hardening note VHN-6-4; Prior assessment finding AF-6

**Revision history.**
- 2022-07: editorial revision to CM-016; clarified scope and wording.
- 2022-07: editorial revision to CM-016; clarified scope and wording.
- 2025-12: editorial revision to CM-016; clarified scope and wording.
- 2025-08: editorial revision to CM-016; clarified scope and wording.


### CM-017 — Centralized package provenance

**Domain:** Configuration Management  **Severity:** Critical  **Applies to:** gateway and bastion hosts

**Rationale.** Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment.

**Requirement.** Baseline packages shall be installed only from the approved internal mirror.

**Implementation guidance.** Store rendered configuration in `/etc` only after the change ticket is approved.

**Verification.** Assessors may re-run the audit after applying patches to confirm the host has converged.

**References.** Vendor hardening note VHN-2-2; Lab Operations Runbook ROB-2

**Revision history.**
- 2025-03: editorial revision to CM-017; clarified scope and wording.
- 2022-10: editorial revision to CM-017; clarified scope and wording.
- 2023-08: editorial revision to CM-017; clarified scope and wording.
- 2025-10: editorial revision to CM-017; clarified scope and wording.


## 6. System Hardening

The controls in this section apply to gateway and bastion hosts. Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment.


### HD-001 — Baseline module loading

**Domain:** System Hardening  **Severity:** Moderate  **Applies to:** service-account-bearing hosts

**Rationale.** The control exists to keep remediation deterministic so that repeated audits converge on a stable state.

**Requirement.** Unused filesystem mount options that weaken integrity guarantees shall be removed.

**Implementation guidance.** Document Match-block criteria that are intentionally out of scope for the gateway auditor.

**Verification.** Assessors may re-run the audit after applying patches to confirm the host has converged.

**References.** Baseline Configuration Guide BCG-1.5; Baseline Configuration Guide BCG-7.9; Lab Operations Runbook ROB-8; Vendor hardening note VHN-2-2

**Revision history.**
- 2025-04: editorial revision to HD-001; clarified scope and wording.
- 2023-12: editorial revision to HD-001; clarified scope and wording.
- 2022-05: editorial revision to HD-001; clarified scope and wording.
- 2024-03: editorial revision to HD-001; clarified scope and wording.


### HD-002 — Centralized time synchronization

**Domain:** System Hardening  **Severity:** Critical  **Applies to:** service-account-bearing hosts

**Rationale.** Consistent enforcement reduces the mean time to detect anomalous access across the estate.

**Requirement.** Listening services shall be bound to management interfaces unless a waiver is on file.

**Implementation guidance.** Evaluate sshd drop-ins in filename order; do not assume a single monolithic config file.

**Verification.** Assessors may re-run the audit after applying patches to confirm the host has converged.

**References.** Vendor hardening note VHN-5-3; Vendor hardening note VHN-4-4; Lab Operations Runbook ROB-7; Lab Operations Runbook ROB-9

**Revision history.**
- 2024-08: editorial revision to HD-002; clarified scope and wording.
- 2023-08: editorial revision to HD-002; clarified scope and wording.
- 2025-05: editorial revision to HD-002; clarified scope and wording.
- 2023-09: editorial revision to HD-002; clarified scope and wording.


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


### HD-003 — Standard console access

**Domain:** System Hardening  **Severity:** Moderate  **Applies to:** service-account-bearing hosts

**Rationale.** Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment.

**Requirement.** Unused filesystem mount options that weaken integrity guarantees shall be removed.

**Implementation guidance.** Document Match-block criteria that are intentionally out of scope for the gateway auditor.

**Verification.** The verifier records the before and after state for inclusion in the assessment package.

**References.** Prior assessment finding AF-1; Governing Security Policy GSP-2024 §4.4; Governing Security Policy GSP-2024 §3.0; Vendor hardening note VHN-2-0

**Revision history.**
- 2023-11: editorial revision to HD-003; clarified scope and wording.
- 2025-06: editorial revision to HD-003; clarified scope and wording.
- 2023-05: editorial revision to HD-003; clarified scope and wording.


### HD-004 — Centralized package provenance

**Domain:** System Hardening  **Severity:** Low  **Applies to:** shared interactive hosts

**Rationale.** Adversaries routinely probe for misconfigurations of this control when establishing persistence on laboratory infrastructure.

**Requirement.** Unused filesystem mount options that weaken integrity guarantees shall be removed.

**Implementation guidance.** Evaluate sshd drop-ins in filename order; do not assume a single monolithic config file.

**Verification.** Verification is performed by the setup auditor, which compares the host state to the normalized policy expectation.

**References.** Governing Security Policy GSP-2024 §7.2; Prior assessment finding AF-3; Vendor hardening note VHN-7-5; Vendor hardening note VHN-1-1

**Revision history.**
- 2022-08: editorial revision to HD-004; clarified scope and wording.
- 2023-10: editorial revision to HD-004; clarified scope and wording.
- 2022-10: editorial revision to HD-004; clarified scope and wording.
- 2024-02: editorial revision to HD-004; clarified scope and wording.


### HD-SSHD-KBDINT — Effective keyboard-interactive authentication

**Domain:** System Hardening  **Severity:** High  **Applies to:** gateway and bastion hosts

**Rationale.** Keyboard-interactive authentication can silently re-enable password-style prompts even where `PasswordAuthentication` is disabled, so its effective value must be controlled with the same rigor as the other sshd keywords.

**Requirement.** In addition to the keywords in HD-SSHD-DROPIN, the auditor shall evaluate `KbdInteractiveAuthentication`. Its effective value is computed using the **same** drop-in precedence rules as HD-SSHD-DROPIN: fragments concatenated in ascending filename order, everything from the first `Match` line onward ignored, and the first global occurrence of the keyword establishing the effective value (keywords compared case-insensitively). When the effective value is absent, or is any value other than an accepted value, the auditor shall propose `systemd.set_dropin` with unit `sshd`, key `KbdInteractiveAuthentication`, and value `no`. The only accepted value is `no`. *(Appendix G adds a deprecated alias keyword for this control.)*

**Implementation guidance.** Reuse the precedence machinery from HD-SSHD-DROPIN; this keyword is evaluated independently of the others.

**Verification.** A compliant host has an effective `KbdInteractiveAuthentication` of `no` and yields no patch for this keyword.

**References.** Governing Security Policy GSP-2024 §6.3; Vendor hardening note VHN-6-2

**Revision history.**
- 2025-03: initial publication.


### HD-005 — Hardened console access

**Domain:** System Hardening  **Severity:** Low  **Applies to:** all managed hosts

**Rationale.** Adversaries routinely probe for misconfigurations of this control when establishing persistence on laboratory infrastructure.

**Requirement.** Kernel tunables called out in the platform baseline shall match the pinned reference profile.

**Implementation guidance.** Document Match-block criteria that are intentionally out of scope for the gateway auditor.

**Verification.** Verification is performed by the setup auditor, which compares the host state to the normalized policy expectation.

**References.** Governing Security Policy GSP-2024 §1.3; Lab Operations Runbook ROB-1; Governing Security Policy GSP-2024 §1.2; Lab Operations Runbook ROB-5

**Revision history.**
- 2024-06: editorial revision to HD-005; clarified scope and wording.
- 2023-08: editorial revision to HD-005; clarified scope and wording.
- 2024-05: editorial revision to HD-005; clarified scope and wording.
- 2022-04: editorial revision to HD-005; clarified scope and wording.


### HD-006 — Mandatory time synchronization

**Domain:** System Hardening  **Severity:** Critical  **Applies to:** service-account-bearing hosts

**Rationale.** Inconsistent application of this requirement across hosts complicates evidence collection and weakens attestations.

**Requirement.** Kernel tunables called out in the platform baseline shall match the pinned reference profile.

**Implementation guidance.** Document Match-block criteria that are intentionally out of scope for the gateway auditor.

**Verification.** Verification is performed by the setup auditor, which compares the host state to the normalized policy expectation.

**References.** Baseline Configuration Guide BCG-9.9; Baseline Configuration Guide BCG-4.9; Baseline Configuration Guide BCG-2.0

**Revision history.**
- 2024-06: editorial revision to HD-006; clarified scope and wording.
- 2025-08: editorial revision to HD-006; clarified scope and wording.
- 2023-12: editorial revision to HD-006; clarified scope and wording.
- 2025-02: editorial revision to HD-006; clarified scope and wording.


### HD-007 — Approved package provenance

**Domain:** System Hardening  **Severity:** Moderate  **Applies to:** tier-1 laboratory hosts

**Rationale.** Inconsistent application of this requirement across hosts complicates evidence collection and weakens attestations.

**Requirement.** Kernel tunables called out in the platform baseline shall match the pinned reference profile.

**Implementation guidance.** Evaluate sshd drop-ins in filename order; do not assume a single monolithic config file.

**Verification.** Verification is performed by the setup auditor, which compares the host state to the normalized policy expectation.

**References.** Lab Operations Runbook ROB-2; Lab Operations Runbook ROB-3; Lab Operations Runbook ROB-5

**Revision history.**
- 2023-07: editorial revision to HD-007; clarified scope and wording.
- 2025-05: editorial revision to HD-007; clarified scope and wording.
- 2025-02: editorial revision to HD-007; clarified scope and wording.
- 2024-10: editorial revision to HD-007; clarified scope and wording.


### HD-008 — Mandatory umask default

**Domain:** System Hardening  **Severity:** High  **Applies to:** service-account-bearing hosts

**Rationale.** Operational experience shows that small deviations here cascade into larger exposure during incident response.

**Requirement.** Kernel tunables called out in the platform baseline shall match the pinned reference profile.

**Implementation guidance.** Document Match-block criteria that are intentionally out of scope for the gateway auditor.

**Verification.** Evidence is the auditor's proposed patch set; a compliant host yields an empty set for this control.

**References.** Governing Security Policy GSP-2024 §4.7; Prior assessment finding AF-2; Lab Operations Runbook ROB-1; Prior assessment finding AF-4

**Revision history.**
- 2023-08: editorial revision to HD-008; clarified scope and wording.
- 2022-06: editorial revision to HD-008; clarified scope and wording.
- 2025-08: editorial revision to HD-008; clarified scope and wording.


### HD-009 — Baseline credential rotation

**Domain:** System Hardening  **Severity:** Low  **Applies to:** service-account-bearing hosts

**Rationale.** The control exists to keep remediation deterministic so that repeated audits converge on a stable state.

**Requirement.** Unused filesystem mount options that weaken integrity guarantees shall be removed.

**Implementation guidance.** Evaluate sshd drop-ins in filename order; do not assume a single monolithic config file.

**Verification.** Assessors may re-run the audit after applying patches to confirm the host has converged.

**References.** Vendor hardening note VHN-4-3; Governing Security Policy GSP-2024 §6.7

**Revision history.**
- 2025-03: editorial revision to HD-009; clarified scope and wording.
- 2024-06: editorial revision to HD-009; clarified scope and wording.


### HD-010 — Verified console access

**Domain:** System Hardening  **Severity:** Critical  **Applies to:** all managed hosts

**Rationale.** Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment.

**Requirement.** Unused filesystem mount options that weaken integrity guarantees shall be removed.

**Implementation guidance.** Document Match-block criteria that are intentionally out of scope for the gateway auditor.

**Verification.** Assessors may re-run the audit after applying patches to confirm the host has converged.

**References.** Lab Operations Runbook ROB-1; Prior assessment finding AF-5

**Revision history.**
- 2024-10: editorial revision to HD-010; clarified scope and wording.
- 2024-07: editorial revision to HD-010; clarified scope and wording.


### HD-011 — Baseline log forwarding

**Domain:** System Hardening  **Severity:** Moderate  **Applies to:** shared interactive hosts

**Rationale.** The control exists to keep remediation deterministic so that repeated audits converge on a stable state.

**Requirement.** Unused filesystem mount options that weaken integrity guarantees shall be removed.

**Implementation guidance.** Evaluate sshd drop-ins in filename order; do not assume a single monolithic config file.

**Verification.** Assessors may re-run the audit after applying patches to confirm the host has converged.

**References.** Baseline Configuration Guide BCG-8.0; Prior assessment finding AF-1

**Revision history.**
- 2022-03: editorial revision to HD-011; clarified scope and wording.
- 2024-08: editorial revision to HD-011; clarified scope and wording.


### HD-012 — Restricted package provenance

**Domain:** System Hardening  **Severity:** High  **Applies to:** tier-1 laboratory hosts

**Rationale.** Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment.

**Requirement.** Listening services shall be bound to management interfaces unless a waiver is on file.

**Implementation guidance.** Evaluate sshd drop-ins in filename order; do not assume a single monolithic config file.

**Verification.** Evidence is the auditor's proposed patch set; a compliant host yields an empty set for this control.

**References.** Governing Security Policy GSP-2024 §7.2; Lab Operations Runbook ROB-5; Prior assessment finding AF-4; Baseline Configuration Guide BCG-9.9

**Revision history.**
- 2024-03: editorial revision to HD-012; clarified scope and wording.
- 2023-12: editorial revision to HD-012; clarified scope and wording.
- 2023-01: editorial revision to HD-012; clarified scope and wording.


### HD-013 — Restricted package provenance

**Domain:** System Hardening  **Severity:** Low  **Applies to:** all managed hosts

**Rationale.** The control supports reproducible builds of the host baseline and simplifies forensic comparison.

**Requirement.** Kernel tunables called out in the platform baseline shall match the pinned reference profile.

**Implementation guidance.** Evaluate sshd drop-ins in filename order; do not assume a single monolithic config file.

**Verification.** Evidence is the auditor's proposed patch set; a compliant host yields an empty set for this control.

**References.** Governing Security Policy GSP-2024 §1.1; Baseline Configuration Guide BCG-7.5

**Revision history.**
- 2023-08: editorial revision to HD-013; clarified scope and wording.
- 2023-06: editorial revision to HD-013; clarified scope and wording.


### HD-014 — Controlled core dump handling

**Domain:** System Hardening  **Severity:** Critical  **Applies to:** all managed hosts

**Rationale.** This requirement aligns the gateway with the principle of least privilege mandated by the governing security policy.

**Requirement.** Listening services shall be bound to management interfaces unless a waiver is on file.

**Implementation guidance.** Evaluate sshd drop-ins in filename order; do not assume a single monolithic config file.

**Verification.** Evidence is the auditor's proposed patch set; a compliant host yields an empty set for this control.

**References.** Lab Operations Runbook ROB-7; Baseline Configuration Guide BCG-3.5; Lab Operations Runbook ROB-6; Lab Operations Runbook ROB-6

**Revision history.**
- 2024-03: editorial revision to HD-014; clarified scope and wording.
- 2022-01: editorial revision to HD-014; clarified scope and wording.
- 2023-04: editorial revision to HD-014; clarified scope and wording.


### HD-015 — Hardened module loading

**Domain:** System Hardening  **Severity:** Low  **Applies to:** gateway and bastion hosts

**Rationale.** The control exists to keep remediation deterministic so that repeated audits converge on a stable state.

**Requirement.** Unused filesystem mount options that weaken integrity guarantees shall be removed.

**Implementation guidance.** Document Match-block criteria that are intentionally out of scope for the gateway auditor.

**Verification.** The verifier records the before and after state for inclusion in the assessment package.

**References.** Vendor hardening note VHN-7-5; Baseline Configuration Guide BCG-9.8; Lab Operations Runbook ROB-6

**Revision history.**
- 2023-05: editorial revision to HD-015; clarified scope and wording.
- 2024-04: editorial revision to HD-015; clarified scope and wording.
- 2022-11: editorial revision to HD-015; clarified scope and wording.


### HD-016 — Monitored kernel parameter

**Domain:** System Hardening  **Severity:** High  **Applies to:** service-account-bearing hosts

**Rationale.** Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment.

**Requirement.** Listening services shall be bound to management interfaces unless a waiver is on file.

**Implementation guidance.** Document Match-block criteria that are intentionally out of scope for the gateway auditor.

**Verification.** Verification is performed by the setup auditor, which compares the host state to the normalized policy expectation.

**References.** Baseline Configuration Guide BCG-6.6; Lab Operations Runbook ROB-8; Baseline Configuration Guide BCG-9.1; Governing Security Policy GSP-2024 §3.5

**Revision history.**
- 2025-05: editorial revision to HD-016; clarified scope and wording.
- 2024-04: editorial revision to HD-016; clarified scope and wording.
- 2022-03: editorial revision to HD-016; clarified scope and wording.
- 2024-08: editorial revision to HD-016; clarified scope and wording.


### HD-017 — Baseline filesystem mount option

**Domain:** System Hardening  **Severity:** Moderate  **Applies to:** gateway and bastion hosts

**Rationale.** The control exists to keep remediation deterministic so that repeated audits converge on a stable state.

**Requirement.** Listening services shall be bound to management interfaces unless a waiver is on file.

**Implementation guidance.** Document Match-block criteria that are intentionally out of scope for the gateway auditor.

**Verification.** Automated property checks generate varied host states to confirm the control behaves consistently.

**References.** Vendor hardening note VHN-2-5; Lab Operations Runbook ROB-3; Lab Operations Runbook ROB-6; Governing Security Policy GSP-2024 §3.9

**Revision history.**
- 2023-10: editorial revision to HD-017; clarified scope and wording.
- 2022-05: editorial revision to HD-017; clarified scope and wording.
- 2024-02: editorial revision to HD-017; clarified scope and wording.


### HD-018 — Centralized core dump handling

**Domain:** System Hardening  **Severity:** Critical  **Applies to:** all managed hosts

**Rationale.** Inconsistent application of this requirement across hosts complicates evidence collection and weakens attestations.

**Requirement.** Unused filesystem mount options that weaken integrity guarantees shall be removed.

**Implementation guidance.** Document Match-block criteria that are intentionally out of scope for the gateway auditor.

**Verification.** Automated property checks generate varied host states to confirm the control behaves consistently.

**References.** Governing Security Policy GSP-2024 §1.4; Prior assessment finding AF-2

**Revision history.**
- 2025-10: editorial revision to HD-018; clarified scope and wording.
- 2022-02: editorial revision to HD-018; clarified scope and wording.
- 2023-06: editorial revision to HD-018; clarified scope and wording.
- 2022-04: editorial revision to HD-018; clarified scope and wording.


## 7. Logging and Telemetry

The controls in this section apply to tier-1 laboratory hosts. Operational experience shows that small deviations here cascade into larger exposure during incident response.


### LG-001 — Verified package provenance

**Domain:** Logging and Telemetry  **Severity:** High  **Applies to:** all managed hosts

**Rationale.** Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment.

**Requirement.** Log sources shall use a common timestamp format and include the host classification tag.

**Implementation guidance.** Keep local rotation thresholds below the central ingestion limit.

**Verification.** Automated property checks generate varied host states to confirm the control behaves consistently.

**References.** Governing Security Policy GSP-2024 §3.1; Prior assessment finding AF-2

**Revision history.**
- 2024-04: editorial revision to LG-001; clarified scope and wording.
- 2023-08: editorial revision to LG-001; clarified scope and wording.


### LG-002 — Verified credential rotation

**Domain:** Logging and Telemetry  **Severity:** Critical  **Applies to:** service-account-bearing hosts

**Rationale.** Consistent enforcement reduces the mean time to detect anomalous access across the estate.

**Requirement.** Log sources shall use a common timestamp format and include the host classification tag.

**Implementation guidance.** Redact key material from forwarded authentication failure events.

**Verification.** Assessors may re-run the audit after applying patches to confirm the host has converged.

**References.** Lab Operations Runbook ROB-5; Baseline Configuration Guide BCG-3.0; Governing Security Policy GSP-2024 §6.1; Vendor hardening note VHN-5-5

**Revision history.**
- 2023-04: editorial revision to LG-002; clarified scope and wording.
- 2025-01: editorial revision to LG-002; clarified scope and wording.
- 2024-12: editorial revision to LG-002; clarified scope and wording.
- 2024-01: editorial revision to LG-002; clarified scope and wording.


### LG-003 — Baseline session timeout

**Domain:** Logging and Telemetry  **Severity:** Moderate  **Applies to:** shared interactive hosts

**Rationale.** Operational experience shows that small deviations here cascade into larger exposure during incident response.

**Requirement.** Forwarded logs shall include the originating unit name and boot identifier.

**Implementation guidance.** Keep local rotation thresholds below the central ingestion limit.

**Verification.** Assessors may re-run the audit after applying patches to confirm the host has converged.

**References.** Baseline Configuration Guide BCG-9.2; Lab Operations Runbook ROB-2; Prior assessment finding AF-8

**Revision history.**
- 2022-01: editorial revision to LG-003; clarified scope and wording.
- 2025-12: editorial revision to LG-003; clarified scope and wording.
- 2022-08: editorial revision to LG-003; clarified scope and wording.


### LG-004 — Centralized core dump handling

**Domain:** Logging and Telemetry  **Severity:** Moderate  **Applies to:** shared interactive hosts

**Rationale.** This requirement aligns the gateway with the principle of least privilege mandated by the governing security policy.

**Requirement.** Forwarded logs shall include the originating unit name and boot identifier.

**Implementation guidance.** Redact key material from forwarded authentication failure events.

**Verification.** The verifier records the before and after state for inclusion in the assessment package.

**References.** Vendor hardening note VHN-7-9; Lab Operations Runbook ROB-6; Lab Operations Runbook ROB-7; Vendor hardening note VHN-9-2

**Revision history.**
- 2025-08: editorial revision to LG-004; clarified scope and wording.
- 2025-09: editorial revision to LG-004; clarified scope and wording.


### LG-005 — Monitored interface configuration

**Domain:** Logging and Telemetry  **Severity:** High  **Applies to:** gateway and bastion hosts

**Rationale.** The control supports reproducible builds of the host baseline and simplifies forensic comparison.

**Requirement.** Log sources shall use a common timestamp format and include the host classification tag.

**Implementation guidance.** Keep local rotation thresholds below the central ingestion limit.

**Verification.** Verification is performed by the setup auditor, which compares the host state to the normalized policy expectation.

**References.** Baseline Configuration Guide BCG-3.4; Baseline Configuration Guide BCG-5.2

**Revision history.**
- 2024-05: editorial revision to LG-005; clarified scope and wording.
- 2025-08: editorial revision to LG-005; clarified scope and wording.
- 2025-08: editorial revision to LG-005; clarified scope and wording.
- 2022-12: editorial revision to LG-005; clarified scope and wording.


### LG-006 — Baseline credential rotation

**Domain:** Logging and Telemetry  **Severity:** High  **Applies to:** gateway and bastion hosts

**Rationale.** Consistent enforcement reduces the mean time to detect anomalous access across the estate.

**Requirement.** Forwarded logs shall include the originating unit name and boot identifier.

**Implementation guidance.** Redact key material from forwarded authentication failure events.

**Verification.** Verification is performed by the setup auditor, which compares the host state to the normalized policy expectation.

**References.** Lab Operations Runbook ROB-9; Baseline Configuration Guide BCG-1.0

**Revision history.**
- 2025-11: editorial revision to LG-006; clarified scope and wording.
- 2025-01: editorial revision to LG-006; clarified scope and wording.


### LG-007 — Standard umask default

**Domain:** Logging and Telemetry  **Severity:** Moderate  **Applies to:** all managed hosts

**Rationale.** Inconsistent application of this requirement across hosts complicates evidence collection and weakens attestations.

**Requirement.** Forwarded logs shall include the originating unit name and boot identifier.

**Implementation guidance.** Keep local rotation thresholds below the central ingestion limit.

**Verification.** Evidence is the auditor's proposed patch set; a compliant host yields an empty set for this control.

**References.** Baseline Configuration Guide BCG-1.8; Governing Security Policy GSP-2024 §8.2; Governing Security Policy GSP-2024 §5.1

**Revision history.**
- 2025-03: editorial revision to LG-007; clarified scope and wording.
- 2025-07: editorial revision to LG-007; clarified scope and wording.
- 2024-06: editorial revision to LG-007; clarified scope and wording.


### LG-008 — Monitored service enablement

**Domain:** Logging and Telemetry  **Severity:** Critical  **Applies to:** all managed hosts

**Rationale.** Adversaries routinely probe for misconfigurations of this control when establishing persistence on laboratory infrastructure.

**Requirement.** Forwarded logs shall include the originating unit name and boot identifier.

**Implementation guidance.** Keep local rotation thresholds below the central ingestion limit.

**Verification.** Assessors may re-run the audit after applying patches to confirm the host has converged.

**References.** Governing Security Policy GSP-2024 §6.9; Lab Operations Runbook ROB-9; Governing Security Policy GSP-2024 §2.7; Baseline Configuration Guide BCG-5.0

**Revision history.**
- 2022-11: editorial revision to LG-008; clarified scope and wording.
- 2023-07: editorial revision to LG-008; clarified scope and wording.
- 2023-09: editorial revision to LG-008; clarified scope and wording.


### LG-009 — Mandatory session timeout

**Domain:** Logging and Telemetry  **Severity:** Moderate  **Applies to:** gateway and bastion hosts

**Rationale.** Inconsistent application of this requirement across hosts complicates evidence collection and weakens attestations.

**Requirement.** High-volume debug logging shall be disabled on production gateway instances.

**Implementation guidance.** Redact key material from forwarded authentication failure events.

**Verification.** Assessors may re-run the audit after applying patches to confirm the host has converged.

**References.** Vendor hardening note VHN-6-2; Baseline Configuration Guide BCG-3.6

**Revision history.**
- 2023-08: editorial revision to LG-009; clarified scope and wording.
- 2024-11: editorial revision to LG-009; clarified scope and wording.


### LG-010 — Centralized console access

**Domain:** Logging and Telemetry  **Severity:** Moderate  **Applies to:** tier-1 laboratory hosts

**Rationale.** The control supports reproducible builds of the host baseline and simplifies forensic comparison.

**Requirement.** High-volume debug logging shall be disabled on production gateway instances.

**Implementation guidance.** Keep local rotation thresholds below the central ingestion limit.

**Verification.** Assessors may re-run the audit after applying patches to confirm the host has converged.

**References.** Governing Security Policy GSP-2024 §9.1; Vendor hardening note VHN-9-0; Baseline Configuration Guide BCG-3.7; Prior assessment finding AF-3

**Revision history.**
- 2023-06: editorial revision to LG-010; clarified scope and wording.
- 2025-01: editorial revision to LG-010; clarified scope and wording.
- 2022-03: editorial revision to LG-010; clarified scope and wording.
- 2023-02: editorial revision to LG-010; clarified scope and wording.


### LG-011 — Mandatory interface configuration

**Domain:** Logging and Telemetry  **Severity:** Critical  **Applies to:** gateway and bastion hosts

**Rationale.** Consistent enforcement reduces the mean time to detect anomalous access across the estate.

**Requirement.** Log sources shall use a common timestamp format and include the host classification tag.

**Implementation guidance.** Keep local rotation thresholds below the central ingestion limit.

**Verification.** Evidence is the auditor's proposed patch set; a compliant host yields an empty set for this control.

**References.** Baseline Configuration Guide BCG-8.5; Vendor hardening note VHN-6-3; Baseline Configuration Guide BCG-4.9; Vendor hardening note VHN-8-1

**Revision history.**
- 2025-11: editorial revision to LG-011; clarified scope and wording.
- 2024-10: editorial revision to LG-011; clarified scope and wording.


### LG-012 — Restricted kernel parameter

**Domain:** Logging and Telemetry  **Severity:** Critical  **Applies to:** all managed hosts

**Rationale.** This requirement aligns the gateway with the principle of least privilege mandated by the governing security policy.

**Requirement.** High-volume debug logging shall be disabled on production gateway instances.

**Implementation guidance.** Keep local rotation thresholds below the central ingestion limit.

**Verification.** The verifier records the before and after state for inclusion in the assessment package.

**References.** Vendor hardening note VHN-4-9; Baseline Configuration Guide BCG-6.4; Lab Operations Runbook ROB-5

**Revision history.**
- 2025-07: editorial revision to LG-012; clarified scope and wording.
- 2023-08: editorial revision to LG-012; clarified scope and wording.
- 2024-02: editorial revision to LG-012; clarified scope and wording.


### LG-013 — Restricted interface configuration

**Domain:** Logging and Telemetry  **Severity:** High  **Applies to:** service-account-bearing hosts

**Rationale.** Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment.

**Requirement.** High-volume debug logging shall be disabled on production gateway instances.

**Implementation guidance.** Keep local rotation thresholds below the central ingestion limit.

**Verification.** Automated property checks generate varied host states to confirm the control behaves consistently.

**References.** Vendor hardening note VHN-5-8; Vendor hardening note VHN-7-1

**Revision history.**
- 2024-06: editorial revision to LG-013; clarified scope and wording.
- 2022-04: editorial revision to LG-013; clarified scope and wording.
- 2024-07: editorial revision to LG-013; clarified scope and wording.


### LG-014 — Approved session timeout

**Domain:** Logging and Telemetry  **Severity:** Moderate  **Applies to:** gateway and bastion hosts

**Rationale.** Inconsistent application of this requirement across hosts complicates evidence collection and weakens attestations.

**Requirement.** Forwarded logs shall include the originating unit name and boot identifier.

**Implementation guidance.** Redact key material from forwarded authentication failure events.

**Verification.** Automated property checks generate varied host states to confirm the control behaves consistently.

**References.** Vendor hardening note VHN-8-6; Vendor hardening note VHN-2-8; Lab Operations Runbook ROB-1

**Revision history.**
- 2022-07: editorial revision to LG-014; clarified scope and wording.
- 2022-08: editorial revision to LG-014; clarified scope and wording.
- 2023-04: editorial revision to LG-014; clarified scope and wording.


## 8. Maintenance

The controls in this section apply to tier-1 laboratory hosts. This requirement aligns the gateway with the principle of least privilege mandated by the governing security policy.


### MA-001 — Hardened interface configuration

**Domain:** Maintenance  **Severity:** Low  **Applies to:** shared interactive hosts

**Rationale.** Adversaries routinely probe for misconfigurations of this control when establishing persistence on laboratory infrastructure.

**Requirement.** Rollback media for critical packages shall be retained for one full release cycle.

**Implementation guidance.** Capture the patch list emitted before and after maintenance for the change record.

**Verification.** Automated property checks generate varied host states to confirm the control behaves consistently.

**References.** Lab Operations Runbook ROB-6; Vendor hardening note VHN-8-6; Baseline Configuration Guide BCG-6.3

**Revision history.**
- 2023-11: editorial revision to MA-001; clarified scope and wording.
- 2024-02: editorial revision to MA-001; clarified scope and wording.
- 2024-09: editorial revision to MA-001; clarified scope and wording.


### MA-002 — Restricted boot integrity

**Domain:** Maintenance  **Severity:** Critical  **Applies to:** gateway and bastion hosts

**Rationale.** This requirement aligns the gateway with the principle of least privilege mandated by the governing security policy.

**Requirement.** Rollback media for critical packages shall be retained for one full release cycle.

**Implementation guidance.** Capture the patch list emitted before and after maintenance for the change record.

**Verification.** Assessors may re-run the audit after applying patches to confirm the host has converged.

**References.** Vendor hardening note VHN-1-8; Vendor hardening note VHN-5-8; Governing Security Policy GSP-2024 §7.4

**Revision history.**
- 2024-04: editorial revision to MA-002; clarified scope and wording.
- 2022-02: editorial revision to MA-002; clarified scope and wording.
- 2024-08: editorial revision to MA-002; clarified scope and wording.


### MA-003 — Hardened session timeout

**Domain:** Maintenance  **Severity:** High  **Applies to:** all managed hosts

**Rationale.** Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment.

**Requirement.** Rollback media for critical packages shall be retained for one full release cycle.

**Implementation guidance.** Re-run the setup auditor after privilege-affecting package updates.

**Verification.** Assessors may re-run the audit after applying patches to confirm the host has converged.

**References.** Lab Operations Runbook ROB-4; Lab Operations Runbook ROB-8

**Revision history.**
- 2025-10: editorial revision to MA-003; clarified scope and wording.
- 2022-05: editorial revision to MA-003; clarified scope and wording.
- 2024-08: editorial revision to MA-003; clarified scope and wording.
- 2023-02: editorial revision to MA-003; clarified scope and wording.


### MA-004 — Monitored time synchronization

**Domain:** Maintenance  **Severity:** Moderate  **Applies to:** tier-1 laboratory hosts

**Rationale.** Consistent enforcement reduces the mean time to detect anomalous access across the estate.

**Requirement.** Rollback media for critical packages shall be retained for one full release cycle.

**Implementation guidance.** Capture the patch list emitted before and after maintenance for the change record.

**Verification.** Verification is performed by the setup auditor, which compares the host state to the normalized policy expectation.

**References.** Vendor hardening note VHN-6-8; Lab Operations Runbook ROB-1; Prior assessment finding AF-1; Governing Security Policy GSP-2024 §3.3

**Revision history.**
- 2022-06: editorial revision to MA-004; clarified scope and wording.
- 2024-06: editorial revision to MA-004; clarified scope and wording.
- 2023-07: editorial revision to MA-004; clarified scope and wording.
- 2025-07: editorial revision to MA-004; clarified scope and wording.


### MA-005 — Monitored interface configuration

**Domain:** Maintenance  **Severity:** Moderate  **Applies to:** gateway and bastion hosts

**Rationale.** This requirement aligns the gateway with the principle of least privilege mandated by the governing security policy.

**Requirement.** Patch application shall occur only inside the published maintenance window for the site.

**Implementation guidance.** Capture the patch list emitted before and after maintenance for the change record.

**Verification.** Assessors may re-run the audit after applying patches to confirm the host has converged.

**References.** Governing Security Policy GSP-2024 §8.2; Lab Operations Runbook ROB-1

**Revision history.**
- 2024-12: editorial revision to MA-005; clarified scope and wording.
- 2025-11: editorial revision to MA-005; clarified scope and wording.


### MA-006 — Mandatory banner presentation

**Domain:** Maintenance  **Severity:** Low  **Applies to:** all managed hosts

**Rationale.** Operational experience shows that small deviations here cascade into larger exposure during incident response.

**Requirement.** Post-maintenance validation shall include a targeted auditor run against the gateway profile.

**Implementation guidance.** Capture the patch list emitted before and after maintenance for the change record.

**Verification.** Verification is performed by the setup auditor, which compares the host state to the normalized policy expectation.

**References.** Lab Operations Runbook ROB-4; Prior assessment finding AF-6

**Revision history.**
- 2025-04: editorial revision to MA-006; clarified scope and wording.
- 2025-02: editorial revision to MA-006; clarified scope and wording.


### MA-007 — Baseline banner presentation

**Domain:** Maintenance  **Severity:** Moderate  **Applies to:** gateway and bastion hosts

**Rationale.** Operational experience shows that small deviations here cascade into larger exposure during incident response.

**Requirement.** Patch application shall occur only inside the published maintenance window for the site.

**Implementation guidance.** Re-run the setup auditor after privilege-affecting package updates.

**Verification.** The verifier records the before and after state for inclusion in the assessment package.

**References.** Prior assessment finding AF-2; Lab Operations Runbook ROB-2

**Revision history.**
- 2023-04: editorial revision to MA-007; clarified scope and wording.
- 2025-07: editorial revision to MA-007; clarified scope and wording.


### MA-008 — Approved console access

**Domain:** Maintenance  **Severity:** Moderate  **Applies to:** tier-1 laboratory hosts

**Rationale.** Inconsistent application of this requirement across hosts complicates evidence collection and weakens attestations.

**Requirement.** Post-maintenance validation shall include a targeted auditor run against the gateway profile.

**Implementation guidance.** Re-run the setup auditor after privilege-affecting package updates.

**Verification.** Assessors may re-run the audit after applying patches to confirm the host has converged.

**References.** Lab Operations Runbook ROB-2; Prior assessment finding AF-5; Prior assessment finding AF-7

**Revision history.**
- 2025-01: editorial revision to MA-008; clarified scope and wording.
- 2024-06: editorial revision to MA-008; clarified scope and wording.


### MA-009 — Controlled package provenance

**Domain:** Maintenance  **Severity:** Critical  **Applies to:** gateway and bastion hosts

**Rationale.** Consistent enforcement reduces the mean time to detect anomalous access across the estate.

**Requirement.** Rollback media for critical packages shall be retained for one full release cycle.

**Implementation guidance.** Capture the patch list emitted before and after maintenance for the change record.

**Verification.** Assessors may re-run the audit after applying patches to confirm the host has converged.

**References.** Vendor hardening note VHN-9-6; Lab Operations Runbook ROB-2

**Revision history.**
- 2022-09: editorial revision to MA-009; clarified scope and wording.
- 2024-06: editorial revision to MA-009; clarified scope and wording.


### MA-010 — Centralized banner presentation

**Domain:** Maintenance  **Severity:** Low  **Applies to:** all managed hosts

**Rationale.** Consistent enforcement reduces the mean time to detect anomalous access across the estate.

**Requirement.** Rollback media for critical packages shall be retained for one full release cycle.

**Implementation guidance.** Re-run the setup auditor after privilege-affecting package updates.

**Verification.** Verification is performed by the setup auditor, which compares the host state to the normalized policy expectation.

**References.** Governing Security Policy GSP-2024 §4.6; Lab Operations Runbook ROB-8; Vendor hardening note VHN-8-8; Lab Operations Runbook ROB-4

**Revision history.**
- 2023-12: editorial revision to MA-010; clarified scope and wording.
- 2023-07: editorial revision to MA-010; clarified scope and wording.
- 2024-03: editorial revision to MA-010; clarified scope and wording.
- 2024-12: editorial revision to MA-010; clarified scope and wording.


### MA-011 — Baseline module loading

**Domain:** Maintenance  **Severity:** Moderate  **Applies to:** all managed hosts

**Rationale.** Inconsistent application of this requirement across hosts complicates evidence collection and weakens attestations.

**Requirement.** Post-maintenance validation shall include a targeted auditor run against the gateway profile.

**Implementation guidance.** Re-run the setup auditor after privilege-affecting package updates.

**Verification.** Evidence is the auditor's proposed patch set; a compliant host yields an empty set for this control.

**References.** Baseline Configuration Guide BCG-2.0; Prior assessment finding AF-7; Lab Operations Runbook ROB-3

**Revision history.**
- 2025-11: editorial revision to MA-011; clarified scope and wording.
- 2025-07: editorial revision to MA-011; clarified scope and wording.
- 2023-10: editorial revision to MA-011; clarified scope and wording.


### MA-012 — Controlled filesystem mount option

**Domain:** Maintenance  **Severity:** Low  **Applies to:** shared interactive hosts

**Rationale.** Inconsistent application of this requirement across hosts complicates evidence collection and weakens attestations.

**Requirement.** Rollback media for critical packages shall be retained for one full release cycle.

**Implementation guidance.** Re-run the setup auditor after privilege-affecting package updates.

**Verification.** The verifier records the before and after state for inclusion in the assessment package.

**References.** Lab Operations Runbook ROB-3; Governing Security Policy GSP-2024 §7.4

**Revision history.**
- 2025-03: editorial revision to MA-012; clarified scope and wording.
- 2024-10: editorial revision to MA-012; clarified scope and wording.
- 2024-09: editorial revision to MA-012; clarified scope and wording.


### MA-013 — Controlled banner presentation

**Domain:** Maintenance  **Severity:** Critical  **Applies to:** service-account-bearing hosts

**Rationale.** The control exists to keep remediation deterministic so that repeated audits converge on a stable state.

**Requirement.** Rollback media for critical packages shall be retained for one full release cycle.

**Implementation guidance.** Capture the patch list emitted before and after maintenance for the change record.

**Verification.** Evidence is the auditor's proposed patch set; a compliant host yields an empty set for this control.

**References.** Prior assessment finding AF-4; Governing Security Policy GSP-2024 §4.8

**Revision history.**
- 2022-04: editorial revision to MA-013; clarified scope and wording.
- 2023-10: editorial revision to MA-013; clarified scope and wording.
- 2023-08: editorial revision to MA-013; clarified scope and wording.


### MA-014 — Restricted umask default

**Domain:** Maintenance  **Severity:** Moderate  **Applies to:** gateway and bastion hosts

**Rationale.** Operational experience shows that small deviations here cascade into larger exposure during incident response.

**Requirement.** Patch application shall occur only inside the published maintenance window for the site.

**Implementation guidance.** Re-run the setup auditor after privilege-affecting package updates.

**Verification.** Automated property checks generate varied host states to confirm the control behaves consistently.

**References.** Baseline Configuration Guide BCG-5.2; Baseline Configuration Guide BCG-7.4

**Revision history.**
- 2025-04: editorial revision to MA-014; clarified scope and wording.
- 2022-04: editorial revision to MA-014; clarified scope and wording.
- 2024-03: editorial revision to MA-014; clarified scope and wording.
- 2022-02: editorial revision to MA-014; clarified scope and wording.


### MA-015 — Approved filesystem mount option

**Domain:** Maintenance  **Severity:** High  **Applies to:** tier-1 laboratory hosts

**Rationale.** Operational experience shows that small deviations here cascade into larger exposure during incident response.

**Requirement.** Rollback media for critical packages shall be retained for one full release cycle.

**Implementation guidance.** Re-run the setup auditor after privilege-affecting package updates.

**Verification.** Evidence is the auditor's proposed patch set; a compliant host yields an empty set for this control.

**References.** Baseline Configuration Guide BCG-8.7; Prior assessment finding AF-5; Vendor hardening note VHN-1-0; Prior assessment finding AF-4

**Revision history.**
- 2023-03: editorial revision to MA-015; clarified scope and wording.
- 2023-01: editorial revision to MA-015; clarified scope and wording.
- 2022-03: editorial revision to MA-015; clarified scope and wording.


### MA-016 — Centralized time synchronization

**Domain:** Maintenance  **Severity:** Moderate  **Applies to:** gateway and bastion hosts

**Rationale.** Inconsistent application of this requirement across hosts complicates evidence collection and weakens attestations.

**Requirement.** Patch application shall occur only inside the published maintenance window for the site.

**Implementation guidance.** Re-run the setup auditor after privilege-affecting package updates.

**Verification.** Automated property checks generate varied host states to confirm the control behaves consistently.

**References.** Vendor hardening note VHN-5-2; Governing Security Policy GSP-2024 §6.6; Vendor hardening note VHN-8-4; Lab Operations Runbook ROB-9

**Revision history.**
- 2022-12: editorial revision to MA-016; clarified scope and wording.
- 2023-02: editorial revision to MA-016; clarified scope and wording.
- 2023-07: editorial revision to MA-016; clarified scope and wording.


## 9. Network Controls

The controls in this section apply to shared interactive hosts. The control supports reproducible builds of the host baseline and simplifies forensic comparison.


### NW-001 — Centralized boot integrity

**Domain:** Network Controls  **Severity:** Low  **Applies to:** service-account-bearing hosts

**Rationale.** Inconsistent application of this requirement across hosts complicates evidence collection and weakens attestations.

**Requirement.** East-west management traffic shall traverse only approved jump paths.

**Implementation guidance.** Confirm management CIDRs in sudoers Host fields align with the network inventory.

**Verification.** The verifier records the before and after state for inclusion in the assessment package.

**References.** Prior assessment finding AF-6; Vendor hardening note VHN-1-4; Prior assessment finding AF-3; Prior assessment finding AF-4

**Revision history.**
- 2023-08: editorial revision to NW-001; clarified scope and wording.
- 2023-03: editorial revision to NW-001; clarified scope and wording.
- 2025-06: editorial revision to NW-001; clarified scope and wording.


### NW-002 — Verified package provenance

**Domain:** Network Controls  **Severity:** Low  **Applies to:** shared interactive hosts

**Rationale.** The control supports reproducible builds of the host baseline and simplifies forensic comparison.

**Requirement.** Firewall policy changes shall be staged with an explicit rollback rule set.

**Implementation guidance.** Confirm management CIDRs in sudoers Host fields align with the network inventory.

**Verification.** Automated property checks generate varied host states to confirm the control behaves consistently.

**References.** Governing Security Policy GSP-2024 §4.0; Prior assessment finding AF-7

**Revision history.**
- 2022-02: editorial revision to NW-002; clarified scope and wording.
- 2023-08: editorial revision to NW-002; clarified scope and wording.
- 2023-11: editorial revision to NW-002; clarified scope and wording.
- 2023-08: editorial revision to NW-002; clarified scope and wording.


### NW-003 — Monitored core dump handling

**Domain:** Network Controls  **Severity:** Low  **Applies to:** gateway and bastion hosts

**Rationale.** Operational experience shows that small deviations here cascade into larger exposure during incident response.

**Requirement.** NTP sources shall match the site-specific list maintained by platform engineering.

**Implementation guidance.** Stage firewall edits with a timed rollback when altering bastion paths.

**Verification.** Verification is performed by the setup auditor, which compares the host state to the normalized policy expectation.

**References.** Prior assessment finding AF-7; Governing Security Policy GSP-2024 §2.4; Governing Security Policy GSP-2024 §5.5

**Revision history.**
- 2023-05: editorial revision to NW-003; clarified scope and wording.
- 2025-02: editorial revision to NW-003; clarified scope and wording.
- 2022-03: editorial revision to NW-003; clarified scope and wording.


### NW-004 — Verified umask default

**Domain:** Network Controls  **Severity:** Low  **Applies to:** tier-1 laboratory hosts

**Rationale.** This requirement aligns the gateway with the principle of least privilege mandated by the governing security policy.

**Requirement.** Firewall policy changes shall be staged with an explicit rollback rule set.

**Implementation guidance.** Confirm management CIDRs in sudoers Host fields align with the network inventory.

**Verification.** The verifier records the before and after state for inclusion in the assessment package.

**References.** Vendor hardening note VHN-3-9; Vendor hardening note VHN-2-6; Governing Security Policy GSP-2024 §5.2; Vendor hardening note VHN-3-6

**Revision history.**
- 2025-11: editorial revision to NW-004; clarified scope and wording.
- 2022-11: editorial revision to NW-004; clarified scope and wording.
- 2024-12: editorial revision to NW-004; clarified scope and wording.
- 2025-10: editorial revision to NW-004; clarified scope and wording.


### NW-005 — Monitored console access

**Domain:** Network Controls  **Severity:** Moderate  **Applies to:** shared interactive hosts

**Rationale.** Inconsistent application of this requirement across hosts complicates evidence collection and weakens attestations.

**Requirement.** East-west management traffic shall traverse only approved jump paths.

**Implementation guidance.** Stage firewall edits with a timed rollback when altering bastion paths.

**Verification.** Automated property checks generate varied host states to confirm the control behaves consistently.

**References.** Lab Operations Runbook ROB-7; Governing Security Policy GSP-2024 §2.6; Prior assessment finding AF-1; Governing Security Policy GSP-2024 §2.6

**Revision history.**
- 2023-05: editorial revision to NW-005; clarified scope and wording.
- 2023-09: editorial revision to NW-005; clarified scope and wording.
- 2025-05: editorial revision to NW-005; clarified scope and wording.
- 2023-05: editorial revision to NW-005; clarified scope and wording.


### NW-006 — Baseline kernel parameter

**Domain:** Network Controls  **Severity:** Critical  **Applies to:** service-account-bearing hosts

**Rationale.** Inconsistent application of this requirement across hosts complicates evidence collection and weakens attestations.

**Requirement.** East-west management traffic shall traverse only approved jump paths.

**Implementation guidance.** Stage firewall edits with a timed rollback when altering bastion paths.

**Verification.** Evidence is the auditor's proposed patch set; a compliant host yields an empty set for this control.

**References.** Vendor hardening note VHN-1-9; Lab Operations Runbook ROB-4

**Revision history.**
- 2025-01: editorial revision to NW-006; clarified scope and wording.
- 2024-11: editorial revision to NW-006; clarified scope and wording.
- 2025-06: editorial revision to NW-006; clarified scope and wording.


### NW-007 — Baseline console access

**Domain:** Network Controls  **Severity:** Critical  **Applies to:** shared interactive hosts

**Rationale.** This requirement aligns the gateway with the principle of least privilege mandated by the governing security policy.

**Requirement.** NTP sources shall match the site-specific list maintained by platform engineering.

**Implementation guidance.** Stage firewall edits with a timed rollback when altering bastion paths.

**Verification.** Evidence is the auditor's proposed patch set; a compliant host yields an empty set for this control.

**References.** Baseline Configuration Guide BCG-9.3; Baseline Configuration Guide BCG-6.0; Governing Security Policy GSP-2024 §8.8; Baseline Configuration Guide BCG-1.0

**Revision history.**
- 2022-08: editorial revision to NW-007; clarified scope and wording.
- 2023-04: editorial revision to NW-007; clarified scope and wording.


### NW-008 — Baseline boot integrity

**Domain:** Network Controls  **Severity:** Low  **Applies to:** service-account-bearing hosts

**Rationale.** Operational experience shows that small deviations here cascade into larger exposure during incident response.

**Requirement.** NTP sources shall match the site-specific list maintained by platform engineering.

**Implementation guidance.** Stage firewall edits with a timed rollback when altering bastion paths.

**Verification.** Assessors may re-run the audit after applying patches to confirm the host has converged.

**References.** Governing Security Policy GSP-2024 §2.4; Baseline Configuration Guide BCG-6.9; Lab Operations Runbook ROB-4; Lab Operations Runbook ROB-5

**Revision history.**
- 2022-10: editorial revision to NW-008; clarified scope and wording.
- 2023-05: editorial revision to NW-008; clarified scope and wording.


### NW-009 — Controlled filesystem mount option

**Domain:** Network Controls  **Severity:** Critical  **Applies to:** service-account-bearing hosts

**Rationale.** Operational experience shows that small deviations here cascade into larger exposure during incident response.

**Requirement.** East-west management traffic shall traverse only approved jump paths.

**Implementation guidance.** Confirm management CIDRs in sudoers Host fields align with the network inventory.

**Verification.** Assessors may re-run the audit after applying patches to confirm the host has converged.

**References.** Governing Security Policy GSP-2024 §4.5; Governing Security Policy GSP-2024 §8.1

**Revision history.**
- 2022-03: editorial revision to NW-009; clarified scope and wording.
- 2025-12: editorial revision to NW-009; clarified scope and wording.
- 2022-06: editorial revision to NW-009; clarified scope and wording.


### NW-010 — Hardened session timeout

**Domain:** Network Controls  **Severity:** Moderate  **Applies to:** shared interactive hosts

**Rationale.** Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment.

**Requirement.** NTP sources shall match the site-specific list maintained by platform engineering.

**Implementation guidance.** Confirm management CIDRs in sudoers Host fields align with the network inventory.

**Verification.** Automated property checks generate varied host states to confirm the control behaves consistently.

**References.** Baseline Configuration Guide BCG-5.7; Prior assessment finding AF-5; Baseline Configuration Guide BCG-2.5; Lab Operations Runbook ROB-6

**Revision history.**
- 2022-09: editorial revision to NW-010; clarified scope and wording.
- 2022-06: editorial revision to NW-010; clarified scope and wording.


### NW-011 — Baseline credential rotation

**Domain:** Network Controls  **Severity:** Critical  **Applies to:** service-account-bearing hosts

**Rationale.** The control supports reproducible builds of the host baseline and simplifies forensic comparison.

**Requirement.** NTP sources shall match the site-specific list maintained by platform engineering.

**Implementation guidance.** Confirm management CIDRs in sudoers Host fields align with the network inventory.

**Verification.** The verifier records the before and after state for inclusion in the assessment package.

**References.** Vendor hardening note VHN-5-8; Baseline Configuration Guide BCG-5.5; Baseline Configuration Guide BCG-3.2; Prior assessment finding AF-9

**Revision history.**
- 2024-10: editorial revision to NW-011; clarified scope and wording.
- 2023-07: editorial revision to NW-011; clarified scope and wording.
- 2023-10: editorial revision to NW-011; clarified scope and wording.
- 2024-03: editorial revision to NW-011; clarified scope and wording.


### NW-012 — Baseline filesystem mount option

**Domain:** Network Controls  **Severity:** Moderate  **Applies to:** all managed hosts

**Rationale.** Consistent enforcement reduces the mean time to detect anomalous access across the estate.

**Requirement.** NTP sources shall match the site-specific list maintained by platform engineering.

**Implementation guidance.** Confirm management CIDRs in sudoers Host fields align with the network inventory.

**Verification.** Assessors may re-run the audit after applying patches to confirm the host has converged.

**References.** Lab Operations Runbook ROB-2; Prior assessment finding AF-4; Prior assessment finding AF-7; Prior assessment finding AF-2

**Revision history.**
- 2022-11: editorial revision to NW-012; clarified scope and wording.
- 2023-09: editorial revision to NW-012; clarified scope and wording.
- 2022-11: editorial revision to NW-012; clarified scope and wording.
- 2024-09: editorial revision to NW-012; clarified scope and wording.


### NW-013 — Controlled package provenance

**Domain:** Network Controls  **Severity:** Moderate  **Applies to:** all managed hosts

**Rationale.** This requirement aligns the gateway with the principle of least privilege mandated by the governing security policy.

**Requirement.** NTP sources shall match the site-specific list maintained by platform engineering.

**Implementation guidance.** Confirm management CIDRs in sudoers Host fields align with the network inventory.

**Verification.** Automated property checks generate varied host states to confirm the control behaves consistently.

**References.** Prior assessment finding AF-5; Prior assessment finding AF-1

**Revision history.**
- 2022-12: editorial revision to NW-013; clarified scope and wording.
- 2025-11: editorial revision to NW-013; clarified scope and wording.
- 2025-06: editorial revision to NW-013; clarified scope and wording.
- 2022-03: editorial revision to NW-013; clarified scope and wording.


### NW-014 — Restricted core dump handling

**Domain:** Network Controls  **Severity:** Low  **Applies to:** service-account-bearing hosts

**Rationale.** Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment.

**Requirement.** NTP sources shall match the site-specific list maintained by platform engineering.

**Implementation guidance.** Stage firewall edits with a timed rollback when altering bastion paths.

**Verification.** Assessors may re-run the audit after applying patches to confirm the host has converged.

**References.** Lab Operations Runbook ROB-4; Prior assessment finding AF-1

**Revision history.**
- 2023-06: editorial revision to NW-014; clarified scope and wording.
- 2024-12: editorial revision to NW-014; clarified scope and wording.


### NW-015 — Restricted console access

**Domain:** Network Controls  **Severity:** Critical  **Applies to:** all managed hosts

**Rationale.** The control supports reproducible builds of the host baseline and simplifies forensic comparison.

**Requirement.** Firewall policy changes shall be staged with an explicit rollback rule set.

**Implementation guidance.** Confirm management CIDRs in sudoers Host fields align with the network inventory.

**Verification.** The verifier records the before and after state for inclusion in the assessment package.

**References.** Baseline Configuration Guide BCG-2.8; Vendor hardening note VHN-4-8

**Revision history.**
- 2024-01: editorial revision to NW-015; clarified scope and wording.
- 2023-12: editorial revision to NW-015; clarified scope and wording.
- 2022-01: editorial revision to NW-015; clarified scope and wording.


### NW-016 — Standard credential rotation

**Domain:** Network Controls  **Severity:** Moderate  **Applies to:** all managed hosts

**Rationale.** Operational experience shows that small deviations here cascade into larger exposure during incident response.

**Requirement.** Firewall policy changes shall be staged with an explicit rollback rule set.

**Implementation guidance.** Confirm management CIDRs in sudoers Host fields align with the network inventory.

**Verification.** Evidence is the auditor's proposed patch set; a compliant host yields an empty set for this control.

**References.** Governing Security Policy GSP-2024 §4.3; Vendor hardening note VHN-2-5

**Revision history.**
- 2024-07: editorial revision to NW-016; clarified scope and wording.
- 2022-12: editorial revision to NW-016; clarified scope and wording.
- 2022-02: editorial revision to NW-016; clarified scope and wording.


### NW-017 — Verified core dump handling

**Domain:** Network Controls  **Severity:** High  **Applies to:** service-account-bearing hosts

**Rationale.** The control exists to keep remediation deterministic so that repeated audits converge on a stable state.

**Requirement.** Firewall policy changes shall be staged with an explicit rollback rule set.

**Implementation guidance.** Stage firewall edits with a timed rollback when altering bastion paths.

**Verification.** Verification is performed by the setup auditor, which compares the host state to the normalized policy expectation.

**References.** Vendor hardening note VHN-1-5; Vendor hardening note VHN-7-9; Governing Security Policy GSP-2024 §6.9

**Revision history.**
- 2023-12: editorial revision to NW-017; clarified scope and wording.
- 2025-08: editorial revision to NW-017; clarified scope and wording.


## 10. Incident Response

The controls in this section apply to service-account-bearing hosts. Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment.


### IR-001 — Verified session timeout

**Domain:** Incident Response  **Severity:** Critical  **Applies to:** gateway and bastion hosts

**Rationale.** Adversaries routinely probe for misconfigurations of this control when establishing persistence on laboratory infrastructure.

**Requirement.** Compromised credentials shall trigger an immediate access review for affected principals.

**Implementation guidance.** Attach the auditor patch list to the incident ticket as machine-readable evidence.

**Verification.** The verifier records the before and after state for inclusion in the assessment package.

**References.** Vendor hardening note VHN-4-8; Governing Security Policy GSP-2024 §3.5; Prior assessment finding AF-5; Prior assessment finding AF-3

**Revision history.**
- 2024-07: editorial revision to IR-001; clarified scope and wording.
- 2022-03: editorial revision to IR-001; clarified scope and wording.


### IR-002 — Hardened kernel parameter

**Domain:** Incident Response  **Severity:** Low  **Applies to:** gateway and bastion hosts

**Rationale.** Operational experience shows that small deviations here cascade into larger exposure during incident response.

**Requirement.** Compromised credentials shall trigger an immediate access review for affected principals.

**Implementation guidance.** Attach the auditor patch list to the incident ticket as machine-readable evidence.

**Verification.** Automated property checks generate varied host states to confirm the control behaves consistently.

**References.** Prior assessment finding AF-2; Governing Security Policy GSP-2024 §2.5; Governing Security Policy GSP-2024 §4.3

**Revision history.**
- 2024-07: editorial revision to IR-002; clarified scope and wording.
- 2025-11: editorial revision to IR-002; clarified scope and wording.
- 2024-11: editorial revision to IR-002; clarified scope and wording.
- 2025-02: editorial revision to IR-002; clarified scope and wording.


### IR-003 — Baseline service enablement

**Domain:** Incident Response  **Severity:** Moderate  **Applies to:** shared interactive hosts

**Rationale.** Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment.

**Requirement.** Containment playbooks shall reference the gateway auditor patch output as evidence.

**Implementation guidance.** Attach the auditor patch list to the incident ticket as machine-readable evidence.

**Verification.** The verifier records the before and after state for inclusion in the assessment package.

**References.** Governing Security Policy GSP-2024 §5.2; Baseline Configuration Guide BCG-3.9; Vendor hardening note VHN-2-3

**Revision history.**
- 2022-04: editorial revision to IR-003; clarified scope and wording.
- 2022-05: editorial revision to IR-003; clarified scope and wording.
- 2025-01: editorial revision to IR-003; clarified scope and wording.
- 2025-04: editorial revision to IR-003; clarified scope and wording.


### IR-004 — Verified filesystem mount option

**Domain:** Incident Response  **Severity:** High  **Applies to:** service-account-bearing hosts

**Rationale.** This requirement aligns the gateway with the principle of least privilege mandated by the governing security policy.

**Requirement.** Forensic images shall preserve the state of access-control files before remediation.

**Implementation guidance.** Preserve authorized-keys files before revoking credentials during containment.

**Verification.** Assessors may re-run the audit after applying patches to confirm the host has converged.

**References.** Prior assessment finding AF-2; Prior assessment finding AF-4; Vendor hardening note VHN-5-4; Baseline Configuration Guide BCG-3.7

**Revision history.**
- 2022-06: editorial revision to IR-004; clarified scope and wording.
- 2022-12: editorial revision to IR-004; clarified scope and wording.
- 2023-03: editorial revision to IR-004; clarified scope and wording.


### IR-005 — Approved interface configuration

**Domain:** Incident Response  **Severity:** High  **Applies to:** gateway and bastion hosts

**Rationale.** This requirement aligns the gateway with the principle of least privilege mandated by the governing security policy.

**Requirement.** Compromised credentials shall trigger an immediate access review for affected principals.

**Implementation guidance.** Preserve authorized-keys files before revoking credentials during containment.

**Verification.** Automated property checks generate varied host states to confirm the control behaves consistently.

**References.** Baseline Configuration Guide BCG-3.5; Lab Operations Runbook ROB-3

**Revision history.**
- 2023-07: editorial revision to IR-005; clarified scope and wording.
- 2025-04: editorial revision to IR-005; clarified scope and wording.
- 2023-04: editorial revision to IR-005; clarified scope and wording.


### IR-006 — Verified core dump handling

**Domain:** Incident Response  **Severity:** High  **Applies to:** shared interactive hosts

**Rationale.** The control supports reproducible builds of the host baseline and simplifies forensic comparison.

**Requirement.** Compromised credentials shall trigger an immediate access review for affected principals.

**Implementation guidance.** Attach the auditor patch list to the incident ticket as machine-readable evidence.

**Verification.** Verification is performed by the setup auditor, which compares the host state to the normalized policy expectation.

**References.** Baseline Configuration Guide BCG-6.2; Vendor hardening note VHN-3-8; Lab Operations Runbook ROB-4; Prior assessment finding AF-7

**Revision history.**
- 2022-07: editorial revision to IR-006; clarified scope and wording.
- 2023-10: editorial revision to IR-006; clarified scope and wording.


### IR-007 — Verified session timeout

**Domain:** Incident Response  **Severity:** Moderate  **Applies to:** tier-1 laboratory hosts

**Rationale.** Operational experience shows that small deviations here cascade into larger exposure during incident response.

**Requirement.** Forensic images shall preserve the state of access-control files before remediation.

**Implementation guidance.** Preserve authorized-keys files before revoking credentials during containment.

**Verification.** Automated property checks generate varied host states to confirm the control behaves consistently.

**References.** Governing Security Policy GSP-2024 §9.4; Baseline Configuration Guide BCG-5.8

**Revision history.**
- 2023-12: editorial revision to IR-007; clarified scope and wording.
- 2024-06: editorial revision to IR-007; clarified scope and wording.
- 2022-12: editorial revision to IR-007; clarified scope and wording.


### IR-008 — Standard interface configuration

**Domain:** Incident Response  **Severity:** High  **Applies to:** all managed hosts

**Rationale.** This requirement aligns the gateway with the principle of least privilege mandated by the governing security policy.

**Requirement.** Compromised credentials shall trigger an immediate access review for affected principals.

**Implementation guidance.** Preserve authorized-keys files before revoking credentials during containment.

**Verification.** Verification is performed by the setup auditor, which compares the host state to the normalized policy expectation.

**References.** Governing Security Policy GSP-2024 §5.2; Lab Operations Runbook ROB-8; Lab Operations Runbook ROB-1

**Revision history.**
- 2024-05: editorial revision to IR-008; clarified scope and wording.
- 2023-07: editorial revision to IR-008; clarified scope and wording.


### IR-009 — Mandatory session timeout

**Domain:** Incident Response  **Severity:** High  **Applies to:** shared interactive hosts

**Rationale.** Adversaries routinely probe for misconfigurations of this control when establishing persistence on laboratory infrastructure.

**Requirement.** Compromised credentials shall trigger an immediate access review for affected principals.

**Implementation guidance.** Preserve authorized-keys files before revoking credentials during containment.

**Verification.** Verification is performed by the setup auditor, which compares the host state to the normalized policy expectation.

**References.** Lab Operations Runbook ROB-2; Prior assessment finding AF-2

**Revision history.**
- 2022-10: editorial revision to IR-009; clarified scope and wording.
- 2024-12: editorial revision to IR-009; clarified scope and wording.
- 2023-01: editorial revision to IR-009; clarified scope and wording.
- 2024-02: editorial revision to IR-009; clarified scope and wording.


### IR-010 — Approved module loading

**Domain:** Incident Response  **Severity:** Low  **Applies to:** shared interactive hosts

**Rationale.** The control supports reproducible builds of the host baseline and simplifies forensic comparison.

**Requirement.** Forensic images shall preserve the state of access-control files before remediation.

**Implementation guidance.** Attach the auditor patch list to the incident ticket as machine-readable evidence.

**Verification.** Automated property checks generate varied host states to confirm the control behaves consistently.

**References.** Governing Security Policy GSP-2024 §2.7; Baseline Configuration Guide BCG-2.2

**Revision history.**
- 2024-12: editorial revision to IR-010; clarified scope and wording.
- 2025-10: editorial revision to IR-010; clarified scope and wording.
- 2025-10: editorial revision to IR-010; clarified scope and wording.


### IR-011 — Baseline banner presentation

**Domain:** Incident Response  **Severity:** Critical  **Applies to:** all managed hosts

**Rationale.** The control exists to keep remediation deterministic so that repeated audits converge on a stable state.

**Requirement.** Containment playbooks shall reference the gateway auditor patch output as evidence.

**Implementation guidance.** Attach the auditor patch list to the incident ticket as machine-readable evidence.

**Verification.** Verification is performed by the setup auditor, which compares the host state to the normalized policy expectation.

**References.** Lab Operations Runbook ROB-7; Prior assessment finding AF-2

**Revision history.**
- 2022-01: editorial revision to IR-011; clarified scope and wording.
- 2023-04: editorial revision to IR-011; clarified scope and wording.


### IR-012 — Baseline core dump handling

**Domain:** Incident Response  **Severity:** High  **Applies to:** shared interactive hosts

**Rationale.** This requirement aligns the gateway with the principle of least privilege mandated by the governing security policy.

**Requirement.** Forensic images shall preserve the state of access-control files before remediation.

**Implementation guidance.** Preserve authorized-keys files before revoking credentials during containment.

**Verification.** Automated property checks generate varied host states to confirm the control behaves consistently.

**References.** Vendor hardening note VHN-9-1; Governing Security Policy GSP-2024 §7.4; Baseline Configuration Guide BCG-5.4; Prior assessment finding AF-4

**Revision history.**
- 2024-02: editorial revision to IR-012; clarified scope and wording.
- 2025-04: editorial revision to IR-012; clarified scope and wording.


### IR-013 — Restricted package provenance

**Domain:** Incident Response  **Severity:** Critical  **Applies to:** shared interactive hosts

**Rationale.** Inconsistent application of this requirement across hosts complicates evidence collection and weakens attestations.

**Requirement.** Compromised credentials shall trigger an immediate access review for affected principals.

**Implementation guidance.** Attach the auditor patch list to the incident ticket as machine-readable evidence.

**Verification.** Evidence is the auditor's proposed patch set; a compliant host yields an empty set for this control.

**References.** Baseline Configuration Guide BCG-7.8; Prior assessment finding AF-5

**Revision history.**
- 2023-02: editorial revision to IR-013; clarified scope and wording.
- 2022-05: editorial revision to IR-013; clarified scope and wording.


### IR-014 — Verified umask default

**Domain:** Incident Response  **Severity:** Moderate  **Applies to:** shared interactive hosts

**Rationale.** Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment.

**Requirement.** Compromised credentials shall trigger an immediate access review for affected principals.

**Implementation guidance.** Preserve authorized-keys files before revoking credentials during containment.

**Verification.** Automated property checks generate varied host states to confirm the control behaves consistently.

**References.** Baseline Configuration Guide BCG-9.8; Vendor hardening note VHN-1-3

**Revision history.**
- 2023-11: editorial revision to IR-014; clarified scope and wording.
- 2023-02: editorial revision to IR-014; clarified scope and wording.
- 2022-09: editorial revision to IR-014; clarified scope and wording.


### IR-015 — Restricted umask default

**Domain:** Incident Response  **Severity:** High  **Applies to:** all managed hosts

**Rationale.** Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment.

**Requirement.** Forensic images shall preserve the state of access-control files before remediation.

**Implementation guidance.** Attach the auditor patch list to the incident ticket as machine-readable evidence.

**Verification.** Verification is performed by the setup auditor, which compares the host state to the normalized policy expectation.

**References.** Vendor hardening note VHN-4-8; Governing Security Policy GSP-2024 §9.4

**Revision history.**
- 2023-01: editorial revision to IR-015; clarified scope and wording.
- 2022-08: editorial revision to IR-015; clarified scope and wording.
- 2025-11: editorial revision to IR-015; clarified scope and wording.
- 2023-03: editorial revision to IR-015; clarified scope and wording.


### IR-016 — Controlled credential rotation

**Domain:** Incident Response  **Severity:** High  **Applies to:** shared interactive hosts

**Rationale.** Consistent enforcement reduces the mean time to detect anomalous access across the estate.

**Requirement.** Forensic images shall preserve the state of access-control files before remediation.

**Implementation guidance.** Preserve authorized-keys files before revoking credentials during containment.

**Verification.** Assessors may re-run the audit after applying patches to confirm the host has converged.

**References.** Governing Security Policy GSP-2024 §9.8; Baseline Configuration Guide BCG-5.8; Prior assessment finding AF-8

**Revision history.**
- 2023-12: editorial revision to IR-016; clarified scope and wording.
- 2023-01: editorial revision to IR-016; clarified scope and wording.
- 2022-10: editorial revision to IR-016; clarified scope and wording.


## Appendix A. Host classification


- **HC-794**: Service-account-bearing hosts expose automation principals with lowered UID ranges. Prefer explicit values over relying on compiled-in defaults, which may vary between distributions.

- **GW-643**: Bastion hosts forward only management-plane protocols to internal segments. Document any approved deviation in the exceptions register with a scheduled review date.

- **TL-697**: Bastion hosts forward only management-plane protocols to internal segments. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner.

- **TL-623**: Tier-1 hosts host long-lived experiments and inherit the gateway baseline. Document any approved deviation in the exceptions register with a scheduled review date.

- **GW-198**: Tier-1 hosts host long-lived experiments and inherit the gateway baseline. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner.

- **HC-129**: Bastion hosts forward only management-plane protocols to internal segments. Changes should be staged in a non-production environment and validated against the verification procedure below.

- **HC-758**: Gateway hosts terminate interactive laboratory access and run the setup auditor. Document any approved deviation in the exceptions register with a scheduled review date.

- **TL-262**: Shared interactive hosts require quarterly access reviews and named custodians. Coordinate with the accounts team before altering anything that affects service-account behavior.

- **SV-710**: Shared interactive hosts require quarterly access reviews and named custodians. Changes should be staged in a non-production environment and validated against the verification procedure below.


## Appendix C. Banner wording


Authorized pre-authentication banners shall identify the facility, prohibit unauthorized use, and provide a monitored contact address. Wording changes require legal review and do not alter auditor patch behavior.


## Appendix B. Control rationale narratives


### Narrative RB-92

Service-account exemptions are intentionally narrow to keep automation usable. Retain the prior configuration so that a rollback can be performed without rebuilding the host.


### Narrative XB-32

Primary-group membership is easy to miss when only textual group lists are parsed. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner.


### Narrative RB-84

Service-account exemptions are intentionally narrow to keep automation usable. Prefer explicit values over relying on compiled-in defaults, which may vary between distributions.


### Narrative NB-51

Appendix G exists because several 2026 incidents traced to ambiguous body text. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies.


### Narrative NB-91

Ledger durability matters for repeat audits even when the patch set is empty. Operators should prefer configuration that is idempotent so that re-running the auditor produces no further changes.


### Narrative RB-12

Appendix G exists because several 2026 incidents traced to ambiguous body text. Coordinate with the accounts team before altering anything that affects service-account behavior.


### Narrative XB-86

Match-block evaluation must use a fixed audit context or hosts disagree on sshd posture. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner.


### Narrative NB-23

Primary-group membership is easy to miss when only textual group lists are parsed. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner.


### Narrative NB-53

Appendix G exists because several 2026 incidents traced to ambiguous body text. Coordinate with the accounts team before altering anything that affects service-account behavior.


### Narrative RB-57

Match-block evaluation must use a fixed audit context or hosts disagree on sshd posture. Document any approved deviation in the exceptions register with a scheduled review date.


### Narrative NB-52

Gateway auditors reconcile raw configuration because packaged scanners often mis-handle sudoers aliases and sshd drop-in precedence. Prefer explicit values over relying on compiled-in defaults, which may vary between distributions.


### Narrative NB-80

Includedir splicing changes last-match ordering and cannot be treated as comments. Coordinate with the accounts team before altering anything that affects service-account behavior.


### Narrative NB-49

Primary-group membership is easy to miss when only textual group lists are parsed. Prefer explicit values over relying on compiled-in defaults, which may vary between distributions.


### Narrative XB-55

Primary-group membership is easy to miss when only textual group lists are parsed. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies.


### Narrative RB-25

Service-account exemptions are intentionally narrow to keep automation usable. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies.


### Narrative RB-58

Match-block evaluation must use a fixed audit context or hosts disagree on sshd posture. Document any approved deviation in the exceptions register with a scheduled review date.


### Narrative XB-52

Primary-group membership is easy to miss when only textual group lists are parsed. Retain the prior configuration so that a rollback can be performed without rebuilding the host.


### Narrative XB-75

Gateway auditors reconcile raw configuration because packaged scanners often mis-handle sudoers aliases and sshd drop-in precedence. Coordinate with the accounts team before altering anything that affects service-account behavior.


### Narrative RB-37

Appendix G exists because several 2026 incidents traced to ambiguous body text. When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner.


### Narrative NB-85

Ledger durability matters for repeat audits even when the patch set is empty. Where automation is used, ensure the tooling reads the canonical source files rather than cached copies.


### Narrative NB-30

Primary-group membership is easy to miss when only textual group lists are parsed. Coordinate with the accounts team before altering anything that affects service-account behavior.


### Narrative NB-28

Primary-group membership is easy to miss when only textual group lists are parsed. Changes should be staged in a non-production environment and validated against the verification procedure below.



## Appendix D. Assessment procedures


- **Procedure 834.** Collect the auditor patch list before applying remediations. Automated property checks generate varied host states to confirm the control behaves consistently.

- **Procedure 313.** Collect the auditor patch list before applying remediations. Verification is performed by the setup auditor, which compares the host state to the normalized policy expectation.

- **Procedure 604.** Verify ledger schema 2 retention after a non-empty audit. Evidence is the auditor's proposed patch set; a compliant host yields an empty set for this control.

- **Procedure 530.** Compare two consecutive audits of the same snapshot to confirm idempotence. Evidence is the auditor's proposed patch set; a compliant host yields an empty set for this control.

- **Procedure 266.** Archive passwd, shadow, group, sudoers, authorized_keys, and sshd drop-ins with the assessment. The verifier records the before and after state for inclusion in the assessment package.

- **Procedure 467.** Verify ledger schema 2 retention after a non-empty audit. Verification is performed by the setup auditor, which compares the host state to the normalized policy expectation.

- **Procedure 693.** Verify ledger schema 2 retention after a non-empty audit. Verification is performed by the setup auditor, which compares the host state to the normalized policy expectation.

- **Procedure 332.** Collect the auditor patch list before applying remediations. Verification is performed by the setup auditor, which compares the host state to the normalized policy expectation.

- **Procedure 747.** Collect the auditor patch list before applying remediations. The verifier records the before and after state for inclusion in the assessment package.

- **Procedure 772.** Re-run the auditor after remediation and confirm an empty patch set. Automated property checks generate varied host states to confirm the control behaves consistently.

- **Procedure 302.** Collect the auditor patch list before applying remediations. The verifier records the before and after state for inclusion in the assessment package.

- **Procedure 191.** Verify ledger schema 2 retention after a non-empty audit. Assessors may re-run the audit after applying patches to confirm the host has converged.

- **Procedure 295.** Verify ledger schema 2 retention after a non-empty audit. Evidence is the auditor's proposed patch set; a compliant host yields an empty set for this control.

- **Procedure 964.** Compare two consecutive audits of the same snapshot to confirm idempotence. The verifier records the before and after state for inclusion in the assessment package.

- **Procedure 114.** Verify ledger schema 2 retention after a non-empty audit. The verifier records the before and after state for inclusion in the assessment package.

- **Procedure 992.** Re-run the auditor after remediation and confirm an empty patch set. The verifier records the before and after state for inclusion in the assessment package.


## Appendix E. Change log


- 2025-03-13: Added gateway auditor cross-reference in Appendix H.

- 2025-07-03: Added gateway auditor cross-reference in Appendix H.

- 2023-05-25: Documented includedir handling in AC-SUDO-NOPASSWD guidance.

- 2024-07-18: Editorial pass on access-control definitions.

- 2025-12-10: Added gateway auditor cross-reference in Appendix H.

- 2024-01-04: Added gateway auditor cross-reference in Appendix H.

- 2026-05-05: Aligned service-account roster with operations inventory.

- 2023-02-12: Added gateway auditor cross-reference in Appendix H.

- 2023-10-28: Documented includedir handling in AC-SUDO-NOPASSWD guidance.

- 2025-07-12: Documented includedir handling in AC-SUDO-NOPASSWD guidance.

- 2026-06-21: Documented includedir handling in AC-SUDO-NOPASSWD guidance.

- 2024-02-26: Aligned service-account roster with operations inventory.

- 2026-11-18: Editorial pass on access-control definitions.

- 2026-07-07: Aligned service-account roster with operations inventory.

- 2026-10-15: Editorial pass on access-control definitions.

- 2023-02-07: Retired deprecated sshd keyword spelling notes.

- 2024-02-20: Editorial pass on access-control definitions.

- 2026-11-09: Documented includedir handling in AC-SUDO-NOPASSWD guidance.

- 2023-07-04: Added gateway auditor cross-reference in Appendix H.

- 2025-01-04: Added gateway auditor cross-reference in Appendix H.

- 2026-01-14: Documented includedir handling in AC-SUDO-NOPASSWD guidance.

- 2023-10-03: Aligned service-account roster with operations inventory.

- 2026-05-17: Clarified appendix precedence language.

- 2025-07-28: Documented includedir handling in AC-SUDO-NOPASSWD guidance.

- 2024-04-09: Clarified appendix precedence language.

- 2023-04-25: Editorial pass on access-control definitions.

- 2026-01-25: Editorial pass on access-control definitions.

- 2026-08-10: Editorial pass on access-control definitions.

- 2026-01-11: Aligned service-account roster with operations inventory.

- 2026-01-04: Editorial pass on access-control definitions.

- 2023-11-22: Documented includedir handling in AC-SUDO-NOPASSWD guidance.

- 2025-05-25: Retired deprecated sshd keyword spelling notes.

- 2026-02-24: Retired deprecated sshd keyword spelling notes.

- 2026-03-04: Retired deprecated sshd keyword spelling notes.

- 2025-02-28: Added gateway auditor cross-reference in Appendix H.

- 2023-08-09: Added gateway auditor cross-reference in Appendix H.

- 2026-09-16: Editorial pass on access-control definitions.

- 2025-09-26: Editorial pass on access-control definitions.

- 2025-09-13: Aligned service-account roster with operations inventory.

- 2024-03-25: Aligned service-account roster with operations inventory.

- 2023-01-25: Added gateway auditor cross-reference in Appendix H.

- 2026-11-02: Documented includedir handling in AC-SUDO-NOPASSWD guidance.

- 2025-11-08: Editorial pass on access-control definitions.

- 2026-04-06: Documented includedir handling in AC-SUDO-NOPASSWD guidance.

- 2025-10-27: Added gateway auditor cross-reference in Appendix H.

- 2024-09-07: Added gateway auditor cross-reference in Appendix H.

- 2024-11-03: Aligned service-account roster with operations inventory.

- 2024-01-20: Editorial pass on access-control definitions.

- 2026-02-15: Added gateway auditor cross-reference in Appendix H.

- 2026-03-17: Aligned service-account roster with operations inventory.

- 2026-02-01: Added gateway auditor cross-reference in Appendix H.

- 2025-06-26: Documented includedir handling in AC-SUDO-NOPASSWD guidance.

- 2024-02-25: Added gateway auditor cross-reference in Appendix H.

- 2024-10-02: Aligned service-account roster with operations inventory.

- 2025-05-20: Documented includedir handling in AC-SUDO-NOPASSWD guidance.

- 2023-07-25: Clarified appendix precedence language.

- 2025-08-20: Retired deprecated sshd keyword spelling notes.

- 2026-11-06: Editorial pass on access-control definitions.

- 2025-10-24: Editorial pass on access-control definitions.

- 2025-01-04: Retired deprecated sshd keyword spelling notes.

- 2023-05-09: Editorial pass on access-control definitions.

- 2024-02-23: Added gateway auditor cross-reference in Appendix H.

- 2026-09-11: Documented includedir handling in AC-SUDO-NOPASSWD guidance.

- 2024-10-25: Retired deprecated sshd keyword spelling notes.

- 2023-12-02: Aligned service-account roster with operations inventory.

- 2025-07-14: Added gateway auditor cross-reference in Appendix H.

- 2025-09-27: Added gateway auditor cross-reference in Appendix H.

- 2025-06-06: Documented includedir handling in AC-SUDO-NOPASSWD guidance.

- 2025-11-01: Retired deprecated sshd keyword spelling notes.

- 2023-03-17: Added gateway auditor cross-reference in Appendix H.

- 2024-04-22: Added gateway auditor cross-reference in Appendix H.

- 2023-10-20: Retired deprecated sshd keyword spelling notes.

- 2024-07-14: Editorial pass on access-control definitions.

- 2025-07-28: Editorial pass on access-control definitions.

- 2025-04-03: Documented includedir handling in AC-SUDO-NOPASSWD guidance.

- 2025-09-23: Editorial pass on access-control definitions.

- 2026-04-01: Retired deprecated sshd keyword spelling notes.

- 2023-03-06: Editorial pass on access-control definitions.

- 2026-04-16: Documented includedir handling in AC-SUDO-NOPASSWD guidance.

- 2026-07-09: Added gateway auditor cross-reference in Appendix H.

- 2026-07-28: Editorial pass on access-control definitions.

- 2026-03-09: Aligned service-account roster with operations inventory.


## Appendix F. Cross-domain dependencies


### Dependency note 1

AC-SUDO-NOPASSWD resolves `%group` principals through AC-GROUP-EFFECTIVE before applying exemptions. Redact key material from forwarded authentication failure events.


### Dependency note 2

G-2026-09 includedir content participates in G-2026-07 last-match ordering and G-2026-18 host scoping. Treat sudoers alias expansion as recursive and guard against self-referential alias loops.


### Dependency note 3

G-2026-04 broadens PermitRootLogin acceptance without altering the sshd patch shape. Compare rendered files against the last known-good snapshot before closing a change.


### Dependency note 4

A non-applicable Match block must not establish the first effective sshd keyword occurrence. Document Match-block criteria that are intentionally out of scope for the gateway auditor.


### Dependency note 5

G-2026-16 account expiry is evaluated on the shadow field independently of password-token locks. Preserve authorized-keys files before revoking credentials during containment.


### Dependency note 6

AC-KEY-REVOKE depends on the disabled-account determination in AC-ACCT-LOCK and therefore must run after account normalization. Keep local rotation thresholds below the central ingestion limit.


### Dependency note 7

G-2026-04 broadens PermitRootLogin acceptance without altering the sshd patch shape. When migrating ledger formats, never discard historical rows during in-place upgrades.


### Dependency note 8

Host aliases in sudoers recurse like user aliases and may include negated entries. When migrating ledger formats, never discard historical rows during in-place upgrades.


### Dependency note 9

Primary-group membership can cause a `%group` sudo grant to apply even when the member list is empty. Preserve authorized-keys files before revoking credentials during containment.


### Dependency note 10

Primary-group membership can cause a `%group` sudo grant to apply even when the member list is empty. Evaluate sshd drop-ins in filename order; do not assume a single monolithic config file.


### Dependency note 11

G-2026-19 command-tag stickiness applies only after a grant survives G-2026-02, G-2026-15, and G-2026-18 filtering. Confirm management CIDRs in sudoers Host fields align with the network inventory.


### Dependency note 12

G-2026-16 account expiry is evaluated on the shadow field independently of password-token locks. Treat sudoers alias expansion as recursive and guard against self-referential alias loops.


### Dependency note 13

G-2026-16 account expiry is evaluated on the shadow field independently of password-token locks. Validate `/etc/passwd`, `/etc/shadow`, and `/etc/group` together; partial reads miss effective membership.


### Dependency note 14

G-2026-16 account expiry is evaluated on the shadow field independently of password-token locks. Document Match-block criteria that are intentionally out of scope for the gateway auditor.


### Dependency note 15

Primary-group membership can cause a `%group` sudo grant to apply even when the member list is empty. Treat sudoers alias expansion as recursive and guard against self-referential alias loops.


### Dependency note 16

G-2026-20 key detection ignores marker lines so revoked keys do not block compliance. Attach the auditor patch list to the incident ticket as machine-readable evidence.


### Dependency note 17

Host aliases in sudoers recurse like user aliases and may include negated entries. Confirm management CIDRs in sudoers Host fields align with the network inventory.


### Dependency note 18

G-2026-20 key detection ignores marker lines so revoked keys do not block compliance. Document Match-block criteria that are intentionally out of scope for the gateway auditor.


### Dependency note 19

G-2026-04 broadens PermitRootLogin acceptance without altering the sshd patch shape. Compare rendered files against the last known-good snapshot before closing a change.


### Dependency note 20

Host aliases in sudoers recurse like user aliases and may include negated entries. Document Match-block criteria that are intentionally out of scope for the gateway auditor.


### Dependency note 21

G-2026-20 key detection ignores marker lines so revoked keys do not block compliance. Separate durable audit storage from ephemeral container layers on gateway hosts.


### Dependency note 22

HD-SSHD-KBDINT shares drop-in concatenation and Match evaluation with HD-SSHD-DROPIN under G-2026-17. Evaluate sshd drop-ins in filename order; do not assume a single monolithic config file.


### Dependency note 23

G-2026-04 broadens PermitRootLogin acceptance without altering the sshd patch shape. Attach the auditor patch list to the incident ticket as machine-readable evidence.


### Dependency note 24

G-2026-10 deprecated PermitRootLogin spellings do not change PasswordAuthentication acceptance. Treat sudoers alias expansion as recursive and guard against self-referential alias loops.


### Dependency note 25

AC-KEY-REVOKE depends on the disabled-account determination in AC-ACCT-LOCK and therefore must run after account normalization. Capture the patch list emitted before and after maintenance for the change record.


### Dependency note 26

A non-applicable Match block must not establish the first effective sshd keyword occurrence. Document Match-block criteria that are intentionally out of scope for the gateway auditor.


### Dependency note 27

G-2026-10 deprecated PermitRootLogin spellings do not change PasswordAuthentication acceptance. When migrating ledger formats, never discard historical rows during in-place upgrades.


### Dependency note 28

AU-LEDGER records patch objects emitted by access-control and hardening rules without wrapping them in envelopes. Capture the patch list emitted before and after maintenance for the change record.


### Dependency note 29

AC-SUDO-NOPASSWD resolves `%group` principals through AC-GROUP-EFFECTIVE before applying exemptions. Separate durable audit storage from ephemeral container layers on gateway hosts.


### Dependency note 30

A non-applicable Match block must not establish the first effective sshd keyword occurrence. Validate `/etc/passwd`, `/etc/shadow`, and `/etc/group` together; partial reads miss effective membership.


### Dependency note 31

A non-applicable Match block must not establish the first effective sshd keyword occurrence. Keep local rotation thresholds below the central ingestion limit.


### Dependency note 32

G-2026-20 key detection ignores marker lines so revoked keys do not block compliance. Validate `/etc/passwd`, `/etc/shadow`, and `/etc/group` together; partial reads miss effective membership.


### Dependency note 33

A non-applicable Match block must not establish the first effective sshd keyword occurrence. Store rendered configuration in `/etc` only after the change ticket is approved.


### Dependency note 34

G-2026-16 account expiry is evaluated on the shadow field independently of password-token locks. Validate `/etc/passwd`, `/etc/shadow`, and `/etc/group` together; partial reads miss effective membership.


### Dependency note 35

G-2026-04 broadens PermitRootLogin acceptance without altering the sshd patch shape. Keep local rotation thresholds below the central ingestion limit.


### Dependency note 36

AC-KEY-REVOKE depends on the disabled-account determination in AC-ACCT-LOCK and therefore must run after account normalization. Validate `/etc/passwd`, `/etc/shadow`, and `/etc/group` together; partial reads miss effective membership.


### Dependency note 37

AC-SUDO-NOPASSWD resolves `%group` principals through AC-GROUP-EFFECTIVE before applying exemptions. Confirm management CIDRs in sudoers Host fields align with the network inventory.


### Dependency note 38

AC-KEY-REVOKE depends on the disabled-account determination in AC-ACCT-LOCK and therefore must run after account normalization. Store rendered configuration in `/etc` only after the change ticket is approved.


### Dependency note 39

Primary-group membership can cause a `%group` sudo grant to apply even when the member list is empty. Redact key material from forwarded authentication failure events.


### Dependency note 40

Primary-group membership can cause a `%group` sudo grant to apply even when the member list is empty. Confirm management CIDRs in sudoers Host fields align with the network inventory.


### Dependency note 41

HD-SSHD-KBDINT shares drop-in concatenation and Match evaluation with HD-SSHD-DROPIN under G-2026-17. Validate `/etc/passwd`, `/etc/shadow`, and `/etc/group` together; partial reads miss effective membership.


### Dependency note 42

G-2026-20 key detection ignores marker lines so revoked keys do not block compliance. Validate `/etc/passwd`, `/etc/shadow`, and `/etc/group` together; partial reads miss effective membership.


### Dependency note 43

G-2026-16 account expiry is evaluated on the shadow field independently of password-token locks. Preserve authorized-keys files before revoking credentials during containment.


### Dependency note 44

A non-applicable Match block must not establish the first effective sshd keyword occurrence. Keep local rotation thresholds below the central ingestion limit.


### Dependency note 45

G-2026-16 account expiry is evaluated on the shadow field independently of password-token locks. Validate `/etc/passwd`, `/etc/shadow`, and `/etc/group` together; partial reads miss effective membership.


### Dependency note 46

G-2026-05 Defaults overrides are not host-scoped even when ordinary sudoers specs are. Evaluate sshd drop-ins in filename order; do not assume a single monolithic config file.


### Dependency note 47

AC-EXEMPT filters principals after passwordless-sudo detection but before patch emission. Capture the patch list emitted before and after maintenance for the change record.


### Dependency note 48

G-2026-20 key detection ignores marker lines so revoked keys do not block compliance. Validate `/etc/passwd`, `/etc/shadow`, and `/etc/group` together; partial reads miss effective membership.


### Dependency note 49

Primary-group membership can cause a `%group` sudo grant to apply even when the member list is empty. Separate durable audit storage from ephemeral container layers on gateway hosts.


### Dependency note 50

A non-applicable Match block must not establish the first effective sshd keyword occurrence. Compare rendered files against the last known-good snapshot before closing a change.


### Dependency note 51

Primary-group membership can cause a `%group` sudo grant to apply even when the member list is empty. Store rendered configuration in `/etc` only after the change ticket is approved.


### Dependency note 52

A non-applicable Match block must not establish the first effective sshd keyword occurrence. Redact key material from forwarded authentication failure events.


### Dependency note 53

G-2026-09 includedir content participates in G-2026-07 last-match ordering and G-2026-18 host scoping. Document Match-block criteria that are intentionally out of scope for the gateway auditor.


### Dependency note 54

G-2026-19 command-tag stickiness applies only after a grant survives G-2026-02, G-2026-15, and G-2026-18 filtering. Compare rendered files against the last known-good snapshot before closing a change.


### Dependency note 55

G-2026-16 account expiry is evaluated on the shadow field independently of password-token locks. Treat sudoers alias expansion as recursive and guard against self-referential alias loops.


### Dependency note 56

G-2026-09 includedir content participates in G-2026-07 last-match ordering and G-2026-18 host scoping. When migrating ledger formats, never discard historical rows during in-place upgrades.


### Dependency note 57

G-2026-20 key detection ignores marker lines so revoked keys do not block compliance. Validate `/etc/passwd`, `/etc/shadow`, and `/etc/group` together; partial reads miss effective membership.


### Dependency note 58

G-2026-10 deprecated PermitRootLogin spellings do not change PasswordAuthentication acceptance. Store rendered configuration in `/etc` only after the change ticket is approved.


### Dependency note 59

G-2026-04 broadens PermitRootLogin acceptance without altering the sshd patch shape. Evaluate sshd drop-ins in filename order; do not assume a single monolithic config file.


### Dependency note 60

A non-applicable Match block must not establish the first effective sshd keyword occurrence. Store rendered configuration in `/etc` only after the change ticket is approved.


### Dependency note 61

G-2026-10 deprecated PermitRootLogin spellings do not change PasswordAuthentication acceptance. Store rendered configuration in `/etc` only after the change ticket is approved.


### Dependency note 62

AU-LEDGER records patch objects emitted by access-control and hardening rules without wrapping them in envelopes. Re-run the setup auditor after privilege-affecting package updates.


### Dependency note 63

G-2026-04 broadens PermitRootLogin acceptance without altering the sshd patch shape. Re-run the setup auditor after privilege-affecting package updates.


### Dependency note 64

G-2026-16 account expiry is evaluated on the shadow field independently of password-token locks. Validate `/etc/passwd`, `/etc/shadow`, and `/etc/group` together; partial reads miss effective membership.


### Dependency note 65

G-2026-16 account expiry is evaluated on the shadow field independently of password-token locks. Preserve authorized-keys files before revoking credentials during containment.


### Dependency note 66

G-2026-04 broadens PermitRootLogin acceptance without altering the sshd patch shape. Compare rendered files against the last known-good snapshot before closing a change.


### Dependency note 67

G-2026-20 key detection ignores marker lines so revoked keys do not block compliance. Stage firewall edits with a timed rollback when altering bastion paths.


### Dependency note 68

A non-applicable Match block must not establish the first effective sshd keyword occurrence. Validate `/etc/passwd`, `/etc/shadow`, and `/etc/group` together; partial reads miss effective membership.


### Dependency note 69

Primary-group membership can cause a `%group` sudo grant to apply even when the member list is empty. Treat sudoers alias expansion as recursive and guard against self-referential alias loops.


### Dependency note 70

Primary-group membership can cause a `%group` sudo grant to apply even when the member list is empty. Evaluate sshd drop-ins in filename order; do not assume a single monolithic config file.


### Dependency note 71

AC-SUDO-NOPASSWD resolves `%group` principals through AC-GROUP-EFFECTIVE before applying exemptions. Compare rendered files against the last known-good snapshot before closing a change.


### Dependency note 72

G-2026-05 Defaults overrides are not host-scoped even when ordinary sudoers specs are. Re-run the setup auditor after privilege-affecting package updates.


### Dependency note 73

G-2026-05 Defaults overrides are not host-scoped even when ordinary sudoers specs are. Evaluate sshd drop-ins in filename order; do not assume a single monolithic config file.


### Dependency note 74

G-2026-09 includedir content participates in G-2026-07 last-match ordering and G-2026-18 host scoping. Separate durable audit storage from ephemeral container layers on gateway hosts.


### Dependency note 75

G-2026-09 includedir content participates in G-2026-07 last-match ordering and G-2026-18 host scoping. Re-run the setup auditor after privilege-affecting package updates.


### Dependency note 76

G-2026-20 key detection ignores marker lines so revoked keys do not block compliance. Re-run the setup auditor after privilege-affecting package updates.


### Dependency note 77

Primary-group membership can cause a `%group` sudo grant to apply even when the member list is empty. Re-run the setup auditor after privilege-affecting package updates.


### Dependency note 78

G-2026-16 account expiry is evaluated on the shadow field independently of password-token locks. Evaluate sshd drop-ins in filename order; do not assume a single monolithic config file.


### Dependency note 79

G-2026-04 broadens PermitRootLogin acceptance without altering the sshd patch shape. Store rendered configuration in `/etc` only after the change ticket is approved.


### Dependency note 80

AC-SUDO-NOPASSWD resolves `%group` principals through AC-GROUP-EFFECTIVE before applying exemptions. Keep local rotation thresholds below the central ingestion limit.


### Dependency note 81

A non-applicable Match block must not establish the first effective sshd keyword occurrence. Store rendered configuration in `/etc` only after the change ticket is approved.


### Dependency note 82

Host aliases in sudoers recurse like user aliases and may include negated entries. Preserve authorized-keys files before revoking credentials during containment.


### Dependency note 83

G-2026-19 command-tag stickiness applies only after a grant survives G-2026-02, G-2026-15, and G-2026-18 filtering. Store rendered configuration in `/etc` only after the change ticket is approved.


### Dependency note 84

HD-SSHD-KBDINT shares drop-in concatenation and Match evaluation with HD-SSHD-DROPIN under G-2026-17. Store rendered configuration in `/etc` only after the change ticket is approved.


### Dependency note 85

G-2026-20 key detection ignores marker lines so revoked keys do not block compliance. Store rendered configuration in `/etc` only after the change ticket is approved.


### Dependency note 86

AC-SUDO-NOPASSWD resolves `%group` principals through AC-GROUP-EFFECTIVE before applying exemptions. Attach the auditor patch list to the incident ticket as machine-readable evidence.


### Dependency note 87

AC-KEY-REVOKE depends on the disabled-account determination in AC-ACCT-LOCK and therefore must run after account normalization. Separate durable audit storage from ephemeral container layers on gateway hosts.


### Dependency note 88

G-2026-09 includedir content participates in G-2026-07 last-match ordering and G-2026-18 host scoping. When migrating ledger formats, never discard historical rows during in-place upgrades.


### Dependency note 89

G-2026-09 includedir content participates in G-2026-07 last-match ordering and G-2026-18 host scoping. Stage firewall edits with a timed rollback when altering bastion paths.


### Dependency note 90

Primary-group membership can cause a `%group` sudo grant to apply even when the member list is empty. Redact key material from forwarded authentication failure events.


### Dependency note 91

A non-applicable Match block must not establish the first effective sshd keyword occurrence. Attach the auditor patch list to the incident ticket as machine-readable evidence.


### Dependency note 92

Host aliases in sudoers recurse like user aliases and may include negated entries. Confirm management CIDRs in sudoers Host fields align with the network inventory.


### Dependency note 93

AC-EXEMPT filters principals after passwordless-sudo detection but before patch emission. Compare rendered files against the last known-good snapshot before closing a change.


### Dependency note 94

G-2026-09 includedir content participates in G-2026-07 last-match ordering and G-2026-18 host scoping. Compare rendered files against the last known-good snapshot before closing a change.


### Dependency note 95

AC-EXEMPT filters principals after passwordless-sudo detection but before patch emission. Evaluate sshd drop-ins in filename order; do not assume a single monolithic config file.


### Dependency note 96

AC-SUDO-NOPASSWD resolves `%group` principals through AC-GROUP-EFFECTIVE before applying exemptions. Attach the auditor patch list to the incident ticket as machine-readable evidence.


### Dependency note 97

G-2026-20 key detection ignores marker lines so revoked keys do not block compliance. Stage firewall edits with a timed rollback when altering bastion paths.


### Dependency note 98

AU-LEDGER records patch objects emitted by access-control and hardening rules without wrapping them in envelopes. Keep local rotation thresholds below the central ingestion limit.


### Dependency note 99

HD-SSHD-KBDINT shares drop-in concatenation and Match evaluation with HD-SSHD-DROPIN under G-2026-17. Keep local rotation thresholds below the central ingestion limit.


### Dependency note 100

G-2026-20 key detection ignores marker lines so revoked keys do not block compliance. Validate `/etc/passwd`, `/etc/shadow`, and `/etc/group` together; partial reads miss effective membership.


### Dependency note 101

G-2026-20 key detection ignores marker lines so revoked keys do not block compliance. When migrating ledger formats, never discard historical rows during in-place upgrades.



## Appendix I. Assessment evidence examples


### Evidence example 1

An assessor archives the raw `sudoers` text alongside drop-in files when passwordless grants are disputed; the auditor output is compared after includedir splicing is applied. Evidence is the auditor's proposed patch set; a compliant host yields an empty set for this control.


### Evidence example 2

When sshd posture differs between hosts, reviewers first confirm the fixed audit context rather than assuming global keywords were ignored. Evidence is the auditor's proposed patch set; a compliant host yields an empty set for this control.


### Evidence example 3

Key-revocation findings attach the authorized-keys file showing active key types versus `@` marker lines. Evidence is the auditor's proposed patch set; a compliant host yields an empty set for this control.


### Evidence example 4

Statelessness is validated by posting contradictory snapshots for the same username in sequence and confirming the second result stands alone. Automated property checks generate varied host states to confirm the control behaves consistently.


### Evidence example 5

Statelessness is validated by posting contradictory snapshots for the same username in sequence and confirming the second result stands alone. Automated property checks generate varied host states to confirm the control behaves consistently.


### Evidence example 6

Statelessness is validated by posting contradictory snapshots for the same username in sequence and confirming the second result stands alone. The verifier records the before and after state for inclusion in the assessment package.


### Evidence example 7

Ledger migration evidence includes the legacy bootstrap row plus every patch object from a non-compliant fixture run. The verifier records the before and after state for inclusion in the assessment package.


### Evidence example 8

When sshd posture differs between hosts, reviewers first confirm the fixed audit context rather than assuming global keywords were ignored. The verifier records the before and after state for inclusion in the assessment package.


### Evidence example 9

When sshd posture differs between hosts, reviewers first confirm the fixed audit context rather than assuming global keywords were ignored. Evidence is the auditor's proposed patch set; a compliant host yields an empty set for this control.


### Evidence example 10

An assessor archives the raw `sudoers` text alongside drop-in files when passwordless grants are disputed; the auditor output is compared after includedir splicing is applied. Assessors may re-run the audit after applying patches to confirm the host has converged.


### Evidence example 11

When sshd posture differs between hosts, reviewers first confirm the fixed audit context rather than assuming global keywords were ignored. Automated property checks generate varied host states to confirm the control behaves consistently.


### Evidence example 12

Expiry-related disablement is demonstrated with the eighth shadow field and the published reference day rather than password-token locks alone. Automated property checks generate varied host states to confirm the control behaves consistently.


### Evidence example 13

An assessor archives the raw `sudoers` text alongside drop-in files when passwordless grants are disputed; the auditor output is compared after includedir splicing is applied. Verification is performed by the setup auditor, which compares the host state to the normalized policy expectation.


### Evidence example 14

Statelessness is validated by posting contradictory snapshots for the same username in sequence and confirming the second result stands alone. Assessors may re-run the audit after applying patches to confirm the host has converged.


### Evidence example 15

Expiry-related disablement is demonstrated with the eighth shadow field and the published reference day rather than password-token locks alone. Assessors may re-run the audit after applying patches to confirm the host has converged.


### Evidence example 16

Exemption disputes are resolved by checking UID, roster membership, and whether the principal still holds a reportable passwordless grant. Assessors may re-run the audit after applying patches to confirm the host has converged.


### Evidence example 17

Ledger migration evidence includes the legacy bootstrap row plus every patch object from a non-compliant fixture run. Assessors may re-run the audit after applying patches to confirm the host has converged.


### Evidence example 18

When sshd posture differs between hosts, reviewers first confirm the fixed audit context rather than assuming global keywords were ignored. Evidence is the auditor's proposed patch set; a compliant host yields an empty set for this control.


### Evidence example 19

Key-revocation findings attach the authorized-keys file showing active key types versus `@` marker lines. Assessors may re-run the audit after applying patches to confirm the host has converged.


### Evidence example 20

Exemption disputes are resolved by checking UID, roster membership, and whether the principal still holds a reportable passwordless grant. Automated property checks generate varied host states to confirm the control behaves consistently.


### Evidence example 21

Exemption disputes are resolved by checking UID, roster membership, and whether the principal still holds a reportable passwordless grant. Evidence is the auditor's proposed patch set; a compliant host yields an empty set for this control.


### Evidence example 22

Ledger migration evidence includes the legacy bootstrap row plus every patch object from a non-compliant fixture run. Assessors may re-run the audit after applying patches to confirm the host has converged.


### Evidence example 23

Exemption disputes are resolved by checking UID, roster membership, and whether the principal still holds a reportable passwordless grant. Evidence is the auditor's proposed patch set; a compliant host yields an empty set for this control.


### Evidence example 24

An assessor archives the raw `sudoers` text alongside drop-in files when passwordless grants are disputed; the auditor output is compared after includedir splicing is applied. Evidence is the auditor's proposed patch set; a compliant host yields an empty set for this control.


### Evidence example 25

Statelessness is validated by posting contradictory snapshots for the same username in sequence and confirming the second result stands alone. Automated property checks generate varied host states to confirm the control behaves consistently.


### Evidence example 26

Exemption disputes are resolved by checking UID, roster membership, and whether the principal still holds a reportable passwordless grant. The verifier records the before and after state for inclusion in the assessment package.


### Evidence example 27

When sshd posture differs between hosts, reviewers first confirm the fixed audit context rather than assuming global keywords were ignored. Evidence is the auditor's proposed patch set; a compliant host yields an empty set for this control.


### Evidence example 28

Ledger migration evidence includes the legacy bootstrap row plus every patch object from a non-compliant fixture run. Evidence is the auditor's proposed patch set; a compliant host yields an empty set for this control.


### Evidence example 29

Statelessness is validated by posting contradictory snapshots for the same username in sequence and confirming the second result stands alone. The verifier records the before and after state for inclusion in the assessment package.


### Evidence example 30

An assessor archives the raw `sudoers` text alongside drop-in files when passwordless grants are disputed; the auditor output is compared after includedir splicing is applied. Verification is performed by the setup auditor, which compares the host state to the normalized policy expectation.


### Evidence example 31

An assessor archives the raw `sudoers` text alongside drop-in files when passwordless grants are disputed; the auditor output is compared after includedir splicing is applied. Automated property checks generate varied host states to confirm the control behaves consistently.


### Evidence example 32

Ledger migration evidence includes the legacy bootstrap row plus every patch object from a non-compliant fixture run. Verification is performed by the setup auditor, which compares the host state to the normalized policy expectation.


### Evidence example 33

Expiry-related disablement is demonstrated with the eighth shadow field and the published reference day rather than password-token locks alone. Automated property checks generate varied host states to confirm the control behaves consistently.


### Evidence example 34

Ledger migration evidence includes the legacy bootstrap row plus every patch object from a non-compliant fixture run. Assessors may re-run the audit after applying patches to confirm the host has converged.


### Evidence example 35

Statelessness is validated by posting contradictory snapshots for the same username in sequence and confirming the second result stands alone. Evidence is the auditor's proposed patch set; a compliant host yields an empty set for this control.


### Evidence example 36

Expiry-related disablement is demonstrated with the eighth shadow field and the published reference day rather than password-token locks alone. Automated property checks generate varied host states to confirm the control behaves consistently.


### Evidence example 37

When sshd posture differs between hosts, reviewers first confirm the fixed audit context rather than assuming global keywords were ignored. Assessors may re-run the audit after applying patches to confirm the host has converged.


### Evidence example 38

Statelessness is validated by posting contradictory snapshots for the same username in sequence and confirming the second result stands alone. Verification is performed by the setup auditor, which compares the host state to the normalized policy expectation.


### Evidence example 39

An assessor archives the raw `sudoers` text alongside drop-in files when passwordless grants are disputed; the auditor output is compared after includedir splicing is applied. Evidence is the auditor's proposed patch set; a compliant host yields an empty set for this control.


### Evidence example 40

When sshd posture differs between hosts, reviewers first confirm the fixed audit context rather than assuming global keywords were ignored. Assessors may re-run the audit after applying patches to confirm the host has converged.


### Evidence example 41

An assessor archives the raw `sudoers` text alongside drop-in files when passwordless grants are disputed; the auditor output is compared after includedir splicing is applied. Assessors may re-run the audit after applying patches to confirm the host has converged.


### Evidence example 42

An assessor archives the raw `sudoers` text alongside drop-in files when passwordless grants are disputed; the auditor output is compared after includedir splicing is applied. Verification is performed by the setup auditor, which compares the host state to the normalized policy expectation.


### Evidence example 43

Expiry-related disablement is demonstrated with the eighth shadow field and the published reference day rather than password-token locks alone. The verifier records the before and after state for inclusion in the assessment package.


### Evidence example 44

Ledger migration evidence includes the legacy bootstrap row plus every patch object from a non-compliant fixture run. Automated property checks generate varied host states to confirm the control behaves consistently.


### Evidence example 45

Expiry-related disablement is demonstrated with the eighth shadow field and the published reference day rather than password-token locks alone. Verification is performed by the setup auditor, which compares the host state to the normalized policy expectation.


### Evidence example 46

Ledger migration evidence includes the legacy bootstrap row plus every patch object from a non-compliant fixture run. Evidence is the auditor's proposed patch set; a compliant host yields an empty set for this control.


### Evidence example 47

Expiry-related disablement is demonstrated with the eighth shadow field and the published reference day rather than password-token locks alone. Verification is performed by the setup auditor, which compares the host state to the normalized policy expectation.


### Evidence example 48

When sshd posture differs between hosts, reviewers first confirm the fixed audit context rather than assuming global keywords were ignored. The verifier records the before and after state for inclusion in the assessment package.


### Evidence example 49

Ledger migration evidence includes the legacy bootstrap row plus every patch object from a non-compliant fixture run. Verification is performed by the setup auditor, which compares the host state to the normalized policy expectation.


### Evidence example 50

An assessor archives the raw `sudoers` text alongside drop-in files when passwordless grants are disputed; the auditor output is compared after includedir splicing is applied. Evidence is the auditor's proposed patch set; a compliant host yields an empty set for this control.


### Evidence example 51

An assessor archives the raw `sudoers` text alongside drop-in files when passwordless grants are disputed; the auditor output is compared after includedir splicing is applied. Assessors may re-run the audit after applying patches to confirm the host has converged.


### Evidence example 52

Ledger migration evidence includes the legacy bootstrap row plus every patch object from a non-compliant fixture run. Assessors may re-run the audit after applying patches to confirm the host has converged.


### Evidence example 53

Ledger migration evidence includes the legacy bootstrap row plus every patch object from a non-compliant fixture run. The verifier records the before and after state for inclusion in the assessment package.


### Evidence example 54

Ledger migration evidence includes the legacy bootstrap row plus every patch object from a non-compliant fixture run. Assessors may re-run the audit after applying patches to confirm the host has converged.


### Evidence example 55

Statelessness is validated by posting contradictory snapshots for the same username in sequence and confirming the second result stands alone. Verification is performed by the setup auditor, which compares the host state to the normalized policy expectation.


### Evidence example 56

Expiry-related disablement is demonstrated with the eighth shadow field and the published reference day rather than password-token locks alone. Evidence is the auditor's proposed patch set; a compliant host yields an empty set for this control.


### Evidence example 57

Ledger migration evidence includes the legacy bootstrap row plus every patch object from a non-compliant fixture run. Automated property checks generate varied host states to confirm the control behaves consistently.


### Evidence example 58

Key-revocation findings attach the authorized-keys file showing active key types versus `@` marker lines. Verification is performed by the setup auditor, which compares the host state to the normalized policy expectation.


### Evidence example 59

Key-revocation findings attach the authorized-keys file showing active key types versus `@` marker lines. The verifier records the before and after state for inclusion in the assessment package.


### Evidence example 60

Exemption disputes are resolved by checking UID, roster membership, and whether the principal still holds a reportable passwordless grant. Evidence is the auditor's proposed patch set; a compliant host yields an empty set for this control.


### Evidence example 61

Ledger migration evidence includes the legacy bootstrap row plus every patch object from a non-compliant fixture run. Verification is performed by the setup auditor, which compares the host state to the normalized policy expectation.


### Evidence example 62

Statelessness is validated by posting contradictory snapshots for the same username in sequence and confirming the second result stands alone. Automated property checks generate varied host states to confirm the control behaves consistently.


### Evidence example 63

An assessor archives the raw `sudoers` text alongside drop-in files when passwordless grants are disputed; the auditor output is compared after includedir splicing is applied. Evidence is the auditor's proposed patch set; a compliant host yields an empty set for this control.


### Evidence example 64

When sshd posture differs between hosts, reviewers first confirm the fixed audit context rather than assuming global keywords were ignored. The verifier records the before and after state for inclusion in the assessment package.


### Evidence example 65

Key-revocation findings attach the authorized-keys file showing active key types versus `@` marker lines. Automated property checks generate varied host states to confirm the control behaves consistently.


### Evidence example 66

Statelessness is validated by posting contradictory snapshots for the same username in sequence and confirming the second result stands alone. Verification is performed by the setup auditor, which compares the host state to the normalized policy expectation.


### Evidence example 67

Key-revocation findings attach the authorized-keys file showing active key types versus `@` marker lines. Evidence is the auditor's proposed patch set; a compliant host yields an empty set for this control.


### Evidence example 68

When sshd posture differs between hosts, reviewers first confirm the fixed audit context rather than assuming global keywords were ignored. The verifier records the before and after state for inclusion in the assessment package.


### Evidence example 69

Statelessness is validated by posting contradictory snapshots for the same username in sequence and confirming the second result stands alone. Evidence is the auditor's proposed patch set; a compliant host yields an empty set for this control.


### Evidence example 70

An assessor archives the raw `sudoers` text alongside drop-in files when passwordless grants are disputed; the auditor output is compared after includedir splicing is applied. Evidence is the auditor's proposed patch set; a compliant host yields an empty set for this control.


### Evidence example 71

Expiry-related disablement is demonstrated with the eighth shadow field and the published reference day rather than password-token locks alone. Verification is performed by the setup auditor, which compares the host state to the normalized policy expectation.


### Evidence example 72

Ledger migration evidence includes the legacy bootstrap row plus every patch object from a non-compliant fixture run. Verification is performed by the setup auditor, which compares the host state to the normalized policy expectation.


### Evidence example 73

An assessor archives the raw `sudoers` text alongside drop-in files when passwordless grants are disputed; the auditor output is compared after includedir splicing is applied. Assessors may re-run the audit after applying patches to confirm the host has converged.


### Evidence example 74

When sshd posture differs between hosts, reviewers first confirm the fixed audit context rather than assuming global keywords were ignored. Evidence is the auditor's proposed patch set; a compliant host yields an empty set for this control.


### Evidence example 75

Expiry-related disablement is demonstrated with the eighth shadow field and the published reference day rather than password-token locks alone. Assessors may re-run the audit after applying patches to confirm the host has converged.


### Evidence example 76

Ledger migration evidence includes the legacy bootstrap row plus every patch object from a non-compliant fixture run. Verification is performed by the setup auditor, which compares the host state to the normalized policy expectation.


### Evidence example 77

Ledger migration evidence includes the legacy bootstrap row plus every patch object from a non-compliant fixture run. The verifier records the before and after state for inclusion in the assessment package.


### Evidence example 78

When sshd posture differs between hosts, reviewers first confirm the fixed audit context rather than assuming global keywords were ignored. Assessors may re-run the audit after applying patches to confirm the host has converged.


### Evidence example 79

Key-revocation findings attach the authorized-keys file showing active key types versus `@` marker lines. Evidence is the auditor's proposed patch set; a compliant host yields an empty set for this control.


### Evidence example 80

Exemption disputes are resolved by checking UID, roster membership, and whether the principal still holds a reportable passwordless grant. Verification is performed by the setup auditor, which compares the host state to the normalized policy expectation.


### Evidence example 81

When sshd posture differs between hosts, reviewers first confirm the fixed audit context rather than assuming global keywords were ignored. The verifier records the before and after state for inclusion in the assessment package.


### Evidence example 82

Ledger migration evidence includes the legacy bootstrap row plus every patch object from a non-compliant fixture run. Assessors may re-run the audit after applying patches to confirm the host has converged.


### Evidence example 83

Exemption disputes are resolved by checking UID, roster membership, and whether the principal still holds a reportable passwordless grant. The verifier records the before and after state for inclusion in the assessment package.



## Appendix J. Control crosswalk notes


- **Crosswalk 1.** Appendix G amendments may narrow body requirements without introducing new patch types. Privilege-bearing group memberships shall be reconciled against the quarterly access review export.


- **Crosswalk 2.** AU-LEDGER is orthogonal to patch selection and only governs persistence format. Kernel tunables called out in the platform baseline shall match the pinned reference profile.


- **Crosswalk 3.** AC-ACCT-LOCK feeds AC-KEY-REVOKE but does not itself emit patches. Containment playbooks shall reference the gateway auditor patch output as evidence.


- **Crosswalk 4.** AU-LEDGER is orthogonal to patch selection and only governs persistence format. Rollback media for critical packages shall be retained for one full release cycle.


- **Crosswalk 5.** AC-SUDO-NOPASSWD is the only control that emits `sudoers.require_password`. Local retention shall not truncate records needed for the current assessment cycle.


- **Crosswalk 6.** Random assessment hosts exercise combinations of amendments; partial parsers fail intermittently. Interactive accounts shall be limited to approved shells and home-directory mount options.


- **Crosswalk 7.** Appendix G amendments may narrow body requirements without introducing new patch types. East-west management traffic shall traverse only approved jump paths.


- **Crosswalk 8.** Random assessment hosts exercise combinations of amendments; partial parsers fail intermittently. Shared interactive accounts are prohibited except where explicitly registered in Appendix A.


- **Crosswalk 9.** A compliant host satisfies every amended control simultaneously and therefore emits no patches. Kernel tunables called out in the platform baseline shall match the pinned reference profile.


- **Crosswalk 10.** Appendix G amendments may narrow body requirements without introducing new patch types. Patch application shall occur only inside the published maintenance window for the site.


- **Crosswalk 11.** Random assessment hosts exercise combinations of amendments; partial parsers fail intermittently. High-volume debug logging shall be disabled on production gateway instances.


- **Crosswalk 12.** AC-ACCT-LOCK feeds AC-KEY-REVOKE but does not itself emit patches. Forwarded logs shall include the originating unit name and boot identifier.


- **Crosswalk 13.** AC-ACCT-LOCK feeds AC-KEY-REVOKE but does not itself emit patches. Compromised credentials shall trigger an immediate access review for affected principals.


- **Crosswalk 14.** Appendix G amendments may narrow body requirements without introducing new patch types. Firewall policy changes shall be staged with an explicit rollback rule set.


- **Crosswalk 15.** Appendix G amendments may narrow body requirements without introducing new patch types. Patch application shall occur only inside the published maintenance window for the site.


- **Crosswalk 16.** Appendix G amendments may narrow body requirements without introducing new patch types. Security-relevant events shall be forwarded to the central collector with monotonic timestamps.


- **Crosswalk 17.** A compliant host satisfies every amended control simultaneously and therefore emits no patches. Interactive accounts shall be limited to approved shells and home-directory mount options.


- **Crosswalk 18.** Random assessment hosts exercise combinations of amendments; partial parsers fail intermittently. Kernel tunables called out in the platform baseline shall match the pinned reference profile.


- **Crosswalk 19.** AC-ACCT-LOCK feeds AC-KEY-REVOKE but does not itself emit patches. Audit pipelines shall preserve ordering for correlated sign-in and privilege-use events.


- **Crosswalk 20.** AU-LEDGER is orthogonal to patch selection and only governs persistence format. NTP sources shall match the site-specific list maintained by platform engineering.


- **Crosswalk 21.** Random assessment hosts exercise combinations of amendments; partial parsers fail intermittently. NTP sources shall match the site-specific list maintained by platform engineering.


- **Crosswalk 22.** AC-ACCT-LOCK feeds AC-KEY-REVOKE but does not itself emit patches. Post-maintenance validation shall include a targeted auditor run against the gateway profile.


- **Crosswalk 23.** AC-SUDO-NOPASSWD is the only control that emits `sudoers.require_password`. Interactive accounts shall be limited to approved shells and home-directory mount options.


- **Crosswalk 24.** AC-ACCT-LOCK feeds AC-KEY-REVOKE but does not itself emit patches. Local retention shall not truncate records needed for the current assessment cycle.


- **Crosswalk 25.** Appendix G amendments may narrow body requirements without introducing new patch types. Rollback media for critical packages shall be retained for one full release cycle.


- **Crosswalk 26.** Appendix G amendments may narrow body requirements without introducing new patch types. Emergency break-glass accounts shall be disabled automatically when their waiver expires.


- **Crosswalk 27.** AC-SUDO-NOPASSWD is the only control that emits `sudoers.require_password`. NTP sources shall match the site-specific list maintained by platform engineering.


- **Crosswalk 28.** Appendix G amendments may narrow body requirements without introducing new patch types. Compromised credentials shall trigger an immediate access review for affected principals.


- **Crosswalk 29.** AC-ACCT-LOCK feeds AC-KEY-REVOKE but does not itself emit patches. Forensic images shall preserve the state of access-control files before remediation.


- **Crosswalk 30.** Appendix G amendments may narrow body requirements without introducing new patch types. Listening services shall be bound to management interfaces unless a waiver is on file.


- **Crosswalk 31.** HD-SSHD-DROPIN and HD-SSHD-KBDINT are the only controls that emit `systemd.set_dropin` for sshd. Configuration files under management shall include a checksum in the host inventory.


- **Crosswalk 32.** AC-ACCT-LOCK feeds AC-KEY-REVOKE but does not itself emit patches. Audit pipelines shall preserve ordering for correlated sign-in and privilege-use events.


- **Crosswalk 33.** AC-ACCT-LOCK feeds AC-KEY-REVOKE but does not itself emit patches. Rollback media for critical packages shall be retained for one full release cycle.


- **Crosswalk 34.** Appendix G amendments may narrow body requirements without introducing new patch types. Configuration files under management shall include a checksum in the host inventory.


- **Crosswalk 35.** AC-SUDO-NOPASSWD is the only control that emits `sudoers.require_password`. Local retention shall not truncate records needed for the current assessment cycle.


- **Crosswalk 36.** Appendix G amendments may narrow body requirements without introducing new patch types. Listening services shall be bound to management interfaces unless a waiver is on file.


- **Crosswalk 37.** AC-ACCT-LOCK feeds AC-KEY-REVOKE but does not itself emit patches. Privilege-bearing group memberships shall be reconciled against the quarterly access review export.


- **Crosswalk 38.** Random assessment hosts exercise combinations of amendments; partial parsers fail intermittently. East-west management traffic shall traverse only approved jump paths.


- **Crosswalk 39.** A compliant host satisfies every amended control simultaneously and therefore emits no patches. NTP sources shall match the site-specific list maintained by platform engineering.


- **Crosswalk 40.** A compliant host satisfies every amended control simultaneously and therefore emits no patches. Forensic images shall preserve the state of access-control files before remediation.


- **Crosswalk 41.** Random assessment hosts exercise combinations of amendments; partial parsers fail intermittently. Forensic images shall preserve the state of access-control files before remediation.


- **Crosswalk 42.** A compliant host satisfies every amended control simultaneously and therefore emits no patches. Security-relevant events shall be forwarded to the central collector with monotonic timestamps.


- **Crosswalk 43.** AC-SUDO-NOPASSWD is the only control that emits `sudoers.require_password`. Compromised credentials shall trigger an immediate access review for affected principals.


- **Crosswalk 44.** HD-SSHD-DROPIN and HD-SSHD-KBDINT are the only controls that emit `systemd.set_dropin` for sshd. Interactive accounts shall be limited to approved shells and home-directory mount options.


- **Crosswalk 45.** AU-LEDGER is orthogonal to patch selection and only governs persistence format. Unused filesystem mount options that weaken integrity guarantees shall be removed.


- **Crosswalk 46.** A compliant host satisfies every amended control simultaneously and therefore emits no patches. Shared interactive accounts are prohibited except where explicitly registered in Appendix A.


- **Crosswalk 47.** Appendix G amendments may narrow body requirements without introducing new patch types. Forensic images shall preserve the state of access-control files before remediation.


- **Crosswalk 48.** AC-SUDO-NOPASSWD is the only control that emits `sudoers.require_password`. Containment playbooks shall reference the gateway auditor patch output as evidence.


- **Crosswalk 49.** Random assessment hosts exercise combinations of amendments; partial parsers fail intermittently. Firewall policy changes shall be staged with an explicit rollback rule set.


- **Crosswalk 50.** AC-ACCT-LOCK feeds AC-KEY-REVOKE but does not itself emit patches. Forensic images shall preserve the state of access-control files before remediation.


- **Crosswalk 51.** AU-LEDGER is orthogonal to patch selection and only governs persistence format. Containment playbooks shall reference the gateway auditor patch output as evidence.


- **Crosswalk 52.** AC-SUDO-NOPASSWD is the only control that emits `sudoers.require_password`. Post-maintenance validation shall include a targeted auditor run against the gateway profile.


- **Crosswalk 53.** AU-LEDGER is orthogonal to patch selection and only governs persistence format. Kernel tunables called out in the platform baseline shall match the pinned reference profile.


- **Crosswalk 54.** HD-SSHD-DROPIN and HD-SSHD-KBDINT are the only controls that emit `systemd.set_dropin` for sshd. Log sources shall use a common timestamp format and include the host classification tag.


- **Crosswalk 55.** A compliant host satisfies every amended control simultaneously and therefore emits no patches. Baseline packages shall be installed only from the approved internal mirror.


- **Crosswalk 56.** AU-LEDGER is orthogonal to patch selection and only governs persistence format. Privilege-bearing group memberships shall be reconciled against the quarterly access review export.


- **Crosswalk 57.** Appendix G amendments may narrow body requirements without introducing new patch types. Security-relevant events shall be forwarded to the central collector with monotonic timestamps.


- **Crosswalk 58.** AC-SUDO-NOPASSWD is the only control that emits `sudoers.require_password`. Local retention shall not truncate records needed for the current assessment cycle.


- **Crosswalk 59.** AC-ACCT-LOCK feeds AC-KEY-REVOKE but does not itself emit patches. Drift detection jobs shall run before nightly backup windows on gateway hosts.


- **Crosswalk 60.** AC-SUDO-NOPASSWD is the only control that emits `sudoers.require_password`. Audit pipelines shall preserve ordering for correlated sign-in and privilege-use events.


- **Crosswalk 61.** Appendix G amendments may narrow body requirements without introducing new patch types. Configuration files under management shall include a checksum in the host inventory.


- **Crosswalk 62.** AC-SUDO-NOPASSWD is the only control that emits `sudoers.require_password`. Emergency break-glass accounts shall be disabled automatically when their waiver expires.


- **Crosswalk 63.** AC-ACCT-LOCK feeds AC-KEY-REVOKE but does not itself emit patches. Firewall policy changes shall be staged with an explicit rollback rule set.


- **Crosswalk 64.** HD-SSHD-DROPIN and HD-SSHD-KBDINT are the only controls that emit `systemd.set_dropin` for sshd. NTP sources shall match the site-specific list maintained by platform engineering.


- **Crosswalk 65.** AU-LEDGER is orthogonal to patch selection and only governs persistence format. Forensic images shall preserve the state of access-control files before remediation.


- **Crosswalk 66.** AC-ACCT-LOCK feeds AC-KEY-REVOKE but does not itself emit patches. Drift detection jobs shall run before nightly backup windows on gateway hosts.


- **Crosswalk 67.** AC-SUDO-NOPASSWD is the only control that emits `sudoers.require_password`. Kernel tunables called out in the platform baseline shall match the pinned reference profile.


- **Crosswalk 68.** AC-ACCT-LOCK feeds AC-KEY-REVOKE but does not itself emit patches. High-volume debug logging shall be disabled on production gateway instances.


- **Crosswalk 69.** HD-SSHD-DROPIN and HD-SSHD-KBDINT are the only controls that emit `systemd.set_dropin` for sshd. Security-relevant events shall be forwarded to the central collector with monotonic timestamps.


- **Crosswalk 70.** HD-SSHD-DROPIN and HD-SSHD-KBDINT are the only controls that emit `systemd.set_dropin` for sshd. Listening services shall be bound to management interfaces unless a waiver is on file.



## Appendix G. Amendments (authoritative)


The following amendments are in force and **supersede** the body of the referenced controls per section 1.4. They are listed in effective-date order.


### G-2026-06 — amends HD-SSHD-KBDINT

`ChallengeResponseAuthentication` is the deprecated spelling of `KbdInteractiveAuthentication` and denotes the same effective setting. When computing the effective value for HD-SSHD-KBDINT, occurrences of either keyword shall be treated as the same setting, so the first occurrence of either spelling in drop-in order establishes the effective value. The accepted value set is unchanged and remains `no` only.


### G-2026-15 — amends AC-SUDO-NOPASSWD

AC-SUDO-NOPASSWD is further narrowed so that a user specification grants reportable passwordless sudo only when the rule permits execution as the superuser. The optional Runas specification is the parenthesized list immediately following the `=` in the rule (for example `(ALL)`, `(root)`, `(www-data)`, or `(ALL:ALL)`); the runas *user* list is the portion before any `:` inside the parentheses. When no Runas specification is present the rule defaults to running as `root`. A `NOPASSWD: ALL` rule whose runas user list contains `root` or `ALL` qualifies; a `NOPASSWD: ALL` rule whose runas user list names only non-root principals does not qualify. Under the last-match-wins ordering of G-2026-07, such a non-qualifying line still names its principal and therefore sets that principal's effective state to not-passwordless, just as an ordinary non-NOPASSWD grant would.


### G-2026-26 — amends CM-CHECKSUM-POLICY

Configuration checksums must be stored alongside the host inventory export. This amendment does not affect auditor behavior.


### G-2026-21 — amends CM-PACKAGE-MIRROR

The internal package mirror URL rotates quarterly. This amendment does not affect auditor behavior.


### G-2026-16 — amends AC-ACCT-LOCK

AC-ACCT-LOCK is extended with an account-expiration criterion. An account is additionally disabled when the account-expiry field of its `shadow` entry — the eighth colon-separated field — is present, non-empty, and a base-ten integer strictly less than the assessment reference day `20620` (counted in days since 1970-01-01). An empty expiry field, or an integer value greater than or equal to `20620`, does not by itself disable the account. This criterion combines with the password-token and login-shell criteria: an account disabled by any one criterion is disabled.


### G-2026-03 — amends AC-EXEMPT

The service-account user-id ceiling in AC-EXEMPT is lowered from `999` to `499`. The exempt-account roster is extended to add `svc_backup`, so the roster is `svc_monitor` and `svc_backup`.


### G-2026-07 — amends AC-SUDO-NOPASSWD

The accumulation model in the body of AC-SUDO-NOPASSWD is superseded by **last-match-wins** semantics, consistent with how sudo resolves privileges. Process user specifications and `Defaults:<binder> !authenticate` overrides in file order; for each principal, the effective passwordless state is established by the **last** line that names that principal. Consequently a later specification that grants the principal sudo without `NOPASSWD: ALL` revokes a passwordless grant made by an earlier line, and a later `NOPASSWD: ALL` line reinstates it. Group and alias principals are resolved as in the body, and the resulting state is applied to each resolved member.


### G-2026-17 — amends HD-SSHD-DROPIN / HD-SSHD-KBDINT

The instruction in HD-SSHD-DROPIN to ignore conditional blocks is superseded. The auditor evaluates the effective value of each sshd keyword for a fixed **audit connection context**: the connecting user is `root` and the source address is `198.51.100.10`. Drop-in fragments are still concatenated in ascending filename order and scanned top to bottom. Lines in global scope (before any `Match`) always apply. A `Match` line opens a conditional block that applies only when ALL of its criteria match the audit context; the supported criteria are: `User <list>` — a comma-separated list of patterns where `*` matches any user and an exact name matches that user, a pattern may be negated with a leading `!`, and a negated pattern that matches causes the criterion to fail, so the criterion matches when the connecting user `root` matches at least one non-negated pattern and no negated pattern; `Group <list>` — matches when `root` is an effective member (per AC-GROUP-EFFECTIVE) of at least one of the comma-separated groups; and `Address <list>` — a comma-separated list of exact IPv4 addresses or IPv4 CIDR ranges (`a.b.c.d/prefix`), matching when the source address `198.51.100.10` equals a listed address or falls within a listed range. `Match all` always applies. A block whose `Match` line contains any other criterion keyword does not apply. The effective value of a keyword is the FIRST occurrence, in concatenated order, that appears in global scope or within an applicable block; occurrences inside non-applicable blocks are skipped. This context evaluation governs HD-SSHD-KBDINT as well.


### G-2026-04 — amends HD-SSHD-DROPIN

For `PermitRootLogin` only, the value `prohibit-password` (compared case-insensitively) is an accepted effective value in addition to `no`; an effective value of `prohibit-password` shall not produce a patch. The set of accepted values for `PasswordAuthentication` is unchanged and remains `no` only.


### G-2026-02 — amends AC-SUDO-NOPASSWD

A user specification qualifies as granting passwordless sudo only when the `NOPASSWD` tag applies to the entire command set, that is, only when the remainder of the rule contains `NOPASSWD: ALL` (whitespace around the colon is insignificant). Grants that attach `NOPASSWD` to specific commands do not qualify and shall not produce a `sudoers.require_password` patch.


### G-2026-13 — amends NW-NTP-SOURCES

The list of approved time sources is revised. This amendment does not affect auditor behavior.


### G-2026-14 — amends MA-PATCH-WINDOW

The maintenance window is shifted by one hour for the eastern region. This amendment does not affect auditor behavior.


### G-2026-20 — amends AC-KEY-REVOKE

Authorized key files may contain blank lines, comments, marker-style retired entries, and per-key option prefixes. For AC-KEY-REVOKE, an account is considered to possess keys only when at least one line contains an active key record. Blank lines and lines beginning with `#` are ignored. Lines beginning with `@` are marker-style retired entries and do not count as active keys. A line whose first non-option token is a recognized OpenSSH key type (`ssh-*`, `ecdsa-*`, `sk-ssh-*`, `sk-ecdsa-*`, or `rsa-sha2-*`) counts as an active key; option prefixes before that token are permitted. Option-only lines without a following key type do not count.


### G-2026-25 — amends NW-JUMPHOST-LIST

The approved jump-host inventory is republished. This amendment does not affect auditor behavior.


### G-2026-05 — amends AC-SUDO-NOPASSWD

In addition to ordinary user specifications, a per-user or per-group `Defaults` override of the form `Defaults:<binder> !authenticate` grants passwordless sudo over the entire command set to `<binder>`, exactly as if that binder held a `NOPASSWD: ALL` user specification. `<binder>` may be a user, a `%group` reference (resolved through AC-GROUP-EFFECTIVE), or a negated principal. This overrides the body of AC-SUDO-NOPASSWD, which otherwise ignores all `Defaults` lines. The resulting principals are subject to the same disabled-account and AC-EXEMPT filtering as any other grant.


### G-2026-22 — amends IR-CONTACT-ROSTER

The after-hours incident bridge number is updated. This amendment does not affect auditor behavior.


### G-2026-18 — amends AC-SUDO-NOPASSWD

AC-SUDO-NOPASSWD is host-scoped. Each user specification carries a host field — the token(s) between the principal and the first `=` — which is a comma-separated list of `ALL`, hostnames, or `Host_Alias` names, each optionally negated with a leading `!`. The auditor evaluates rules for the audit host whose hostname is `gw-lab-01`. A specification applies to this host only when its host field resolves to include `gw-lab-01`: `ALL` matches, an exact hostname equal to `gw-lab-01` matches, and a `Host_Alias NAME = ...` (whose members may be hostnames, `ALL`, other host aliases, or negated entries) is resolved recursively. A specification that does not apply to the audit host is ignored entirely and therefore does not participate in the last-match-wins ordering of G-2026-07 for its principal. `Defaults:<binder> !authenticate` overrides are not host-scoped and apply on every host.


### G-2026-19 — amends AC-SUDO-NOPASSWD

For command lists, sudo command tags are stateful. A `NOPASSWD:` or `PASSWD:` tag applies to the command entry following the colon and remains in effect for later comma-separated command entries until another password tag appears. Therefore a rule such as `alice ALL=(ALL) NOPASSWD: /usr/bin/id, ALL` grants reportable passwordless sudo because the later `ALL` command inherits `NOPASSWD`. A rule such as `alice ALL=(ALL) NOPASSWD: /usr/bin/id, PASSWD: ALL` does not grant reportable passwordless sudo because the `ALL` command is under `PASSWD`. This amendment narrows how G-2026-02 is evaluated; the runas and host-scoping amendments still apply.


### G-2026-11 — amends LG-BANNER-TEXT

The approved pre-authentication banner wording is updated; see Appendix C. This amendment does not affect auditor behavior.


### G-2026-10 — amends HD-SSHD-DROPIN

For PermitRootLogin, `without-password` is the deprecated spelling of `prohibit-password` and denotes the same effective setting; it is therefore accepted wherever `prohibit-password` is accepted. The accepted value set for the other keywords is unchanged.


### G-2026-01 — amends AC-ACCT-LOCK / AC-ACCT-SHELL

The locked-password value set in AC-ACCT-LOCK is extended to additionally include the literal value `*LK*`. Independently, the recognized non-interactive shell set in AC-ACCT-SHELL is extended to add `/usr/bin/git-shell` and `/bin/sync`. Accounts matching the extended criteria are disabled.


### G-2026-24 — amends MA-REBOOT-NOTICE

Maintenance notifications must be posted 72 hours in advance. This amendment does not affect auditor behavior.


### G-2026-23 — amends LG-FORWARDER-ADDR

The syslog collector address for tier-1 hosts changes. This amendment does not affect auditor behavior.


### G-2026-09 — amends AC-SUDO-NOPASSWD

Sudoers include directives shall be resolved. A line beginning with `@includedir` or `#includedir` (the leading `#` here is a directive, not a comment) names a drop-in directory supplied in the snapshot under the `sudoers.d` map. Its files are spliced into the policy **in ascending filename order at the position of the directive**, and the resulting lines participate in alias resolution and in the last-match-wins ordering of G-2026-07 exactly as if they had appeared inline. A specification that follows the include directive in the main file is therefore later than any rule contributed by the included files.


### G-2026-12 — amends AU-RETENTION

Audit log retention is extended to 400 days for tier-1 hosts. This amendment does not affect auditor behavior.


## Appendix H. Implementation checklist

Implementers should confirm that the auditor, after parsing a host snapshot, produces exactly the patch set implied by the controls above as amended by Appendix G. A host already in compliance must yield an empty patch set.

