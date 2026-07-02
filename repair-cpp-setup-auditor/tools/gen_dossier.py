#!/usr/bin/env python3
"""Generate the Lab Access Hardening Standard dossier.

The dossier is intentionally long. The normative clauses the auditor must
implement are embedded among realistic filler controls, and several of them are
superseded by the authoritative amendments in Appendix G. Where the body and
Appendix G disagree, Appendix G governs (see section 1.4).

Run from the task root:  python3 tools/gen_dossier.py
"""

import os
import random

OUT = os.path.join(os.path.dirname(__file__), "..", "environment", "docs", "standard.md")

rng = random.Random(70414)

DOMAINS = [
    ("AC", "Access Control"),
    ("AU", "Audit and Accountability"),
    ("CM", "Configuration Management"),
    ("HD", "System Hardening"),
    ("LG", "Logging and Telemetry"),
    ("MA", "Maintenance"),
    ("NW", "Network Controls"),
    ("IR", "Incident Response"),
]

SEV = ["Low", "Moderate", "High", "Critical"]
HOSTCLASS = [
    "all managed hosts",
    "gateway and bastion hosts",
    "tier-1 laboratory hosts",
    "shared interactive hosts",
    "service-account-bearing hosts",
]

RATIONALE = [
    "Uncontrolled drift in this area has historically been the root cause of audit findings during the annual assessment.",
    "Adversaries routinely probe for misconfigurations of this control when establishing persistence on laboratory infrastructure.",
    "Consistent enforcement reduces the mean time to detect anomalous access across the estate.",
    "The control exists to keep remediation deterministic so that repeated audits converge on a stable state.",
    "Inconsistent application of this requirement across hosts complicates evidence collection and weakens attestations.",
    "This requirement aligns the gateway with the principle of least privilege mandated by the governing security policy.",
    "Operational experience shows that small deviations here cascade into larger exposure during incident response.",
    "The control supports reproducible builds of the host baseline and simplifies forensic comparison.",
]

GUIDANCE = [
    "Operators should prefer configuration that is idempotent so that re-running the auditor produces no further changes.",
    "Where automation is used, ensure the tooling reads the canonical source files rather than cached copies.",
    "Changes should be staged in a non-production environment and validated against the verification procedure below.",
    "Document any approved deviation in the exceptions register with a scheduled review date.",
    "Prefer explicit values over relying on compiled-in defaults, which may vary between distributions.",
    "When in doubt, treat the stricter interpretation as authoritative pending clarification from the standards owner.",
    "Coordinate with the accounts team before altering anything that affects service-account behavior.",
    "Retain the prior configuration so that a rollback can be performed without rebuilding the host.",
]

GENERIC_REQUIREMENTS = [
    "The host shall record the control owner and last review date in the local compliance register.",
    "Configuration drift from the approved baseline shall be remediated within the published SLA.",
    "Automation that enforces this control shall emit structured evidence suitable for quarterly attestation.",
]

DOMAIN_REQUIREMENTS = {
    "Access Control": [
        "Interactive accounts shall be limited to approved shells and home-directory mount options.",
        "Privilege-bearing group memberships shall be reconciled against the quarterly access review export.",
        "Emergency break-glass accounts shall be disabled automatically when their waiver expires.",
        "Shared interactive accounts are prohibited except where explicitly registered in Appendix A.",
    ],
    "Audit and Accountability": [
        "Security-relevant events shall be forwarded to the central collector with monotonic timestamps.",
        "Local retention shall not truncate records needed for the current assessment cycle.",
        "Audit pipelines shall preserve ordering for correlated sign-in and privilege-use events.",
    ],
    "Configuration Management": [
        "Baseline packages shall be installed only from the approved internal mirror.",
        "Configuration files under management shall include a checksum in the host inventory.",
        "Drift detection jobs shall run before nightly backup windows on gateway hosts.",
    ],
    "System Hardening": [
        "Kernel tunables called out in the platform baseline shall match the pinned reference profile.",
        "Listening services shall be bound to management interfaces unless a waiver is on file.",
        "Unused filesystem mount options that weaken integrity guarantees shall be removed.",
    ],
    "Logging and Telemetry": [
        "Log sources shall use a common timestamp format and include the host classification tag.",
        "High-volume debug logging shall be disabled on production gateway instances.",
        "Forwarded logs shall include the originating unit name and boot identifier.",
    ],
    "Maintenance": [
        "Patch application shall occur only inside the published maintenance window for the site.",
        "Post-maintenance validation shall include a targeted auditor run against the gateway profile.",
        "Rollback media for critical packages shall be retained for one full release cycle.",
    ],
    "Network Controls": [
        "East-west management traffic shall traverse only approved jump paths.",
        "Firewall policy changes shall be staged with an explicit rollback rule set.",
        "NTP sources shall match the site-specific list maintained by platform engineering.",
    ],
    "Incident Response": [
        "Compromised credentials shall trigger an immediate access review for affected principals.",
        "Forensic images shall preserve the state of access-control files before remediation.",
        "Containment playbooks shall reference the gateway auditor patch output as evidence.",
    ],
}

DOMAIN_GUIDANCE = {
    "Access Control": [
        "Validate `/etc/passwd`, `/etc/shadow`, and `/etc/group` together; partial reads miss effective membership.",
        "Treat sudoers alias expansion as recursive and guard against self-referential alias loops.",
    ],
    "Audit and Accountability": [
        "Separate durable audit storage from ephemeral container layers on gateway hosts.",
        "When migrating ledger formats, never discard historical rows during in-place upgrades.",
    ],
    "Configuration Management": [
        "Store rendered configuration in `/etc` only after the change ticket is approved.",
        "Compare rendered files against the last known-good snapshot before closing a change.",
    ],
    "System Hardening": [
        "Evaluate sshd drop-ins in filename order; do not assume a single monolithic config file.",
        "Document Match-block criteria that are intentionally out of scope for the gateway auditor.",
    ],
    "Logging and Telemetry": [
        "Redact key material from forwarded authentication failure events.",
        "Keep local rotation thresholds below the central ingestion limit.",
    ],
    "Maintenance": [
        "Re-run the setup auditor after privilege-affecting package updates.",
        "Capture the patch list emitted before and after maintenance for the change record.",
    ],
    "Network Controls": [
        "Confirm management CIDRs in sudoers Host fields align with the network inventory.",
        "Stage firewall edits with a timed rollback when altering bastion paths.",
    ],
    "Incident Response": [
        "Preserve authorized-keys files before revoking credentials during containment.",
        "Attach the auditor patch list to the incident ticket as machine-readable evidence.",
    ],
}

VERIFY = [
    "Verification is performed by the setup auditor, which compares the host state to the normalized policy expectation.",
    "Evidence is the auditor's proposed patch set; a compliant host yields an empty set for this control.",
    "Assessors may re-run the audit after applying patches to confirm the host has converged.",
    "Automated property checks generate varied host states to confirm the control behaves consistently.",
    "The verifier records the before and after state for inclusion in the assessment package.",
]

REFS = [
    "Governing Security Policy GSP-2024 §{a}.{b}",
    "Lab Operations Runbook ROB-{a}",
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
    req = rng.choice(DOMAIN_REQUIREMENTS.get(domain, GENERIC_REQUIREMENTS))
    impl = rng.choice(DOMAIN_GUIDANCE.get(domain, GUIDANCE))
    verify = rng.choice(VERIFY)
    return f"""### {cid} — {title}

**Domain:** {domain}  **Severity:** {rng.choice(SEV)}  **Applies to:** {rng.choice(HOSTCLASS)}

**Rationale.** {rng.choice(RATIONALE)}

**Requirement.** {req}

**Implementation guidance.** {impl}

**Verification.** {verify}

**References.** {refs()}

**Revision history.**
{revhist(cid)}
"""


# ---------------------------------------------------------------------------
# Normative controls (the auditor must implement these). Body states the BASE
# values; Appendix G amends several of them.
# ---------------------------------------------------------------------------
NORMATIVE = {}

NORMATIVE["AC-ACCT-LOCK"] = """### AC-ACCT-LOCK — Disabled account determination

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
"""

NORMATIVE["AC-ACCT-SHELL"] = """### AC-ACCT-SHELL — Non-interactive login shells

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
"""

NORMATIVE["AC-GROUP-EFFECTIVE"] = """### AC-GROUP-EFFECTIVE — Effective group membership

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
"""

NORMATIVE["AC-SUDO-NOPASSWD"] = """### AC-SUDO-NOPASSWD — Passwordless sudo determination

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
"""

NORMATIVE["AC-KEY-REVOKE"] = """### AC-KEY-REVOKE — Revocation of keys for disabled accounts

**Domain:** Access Control  **Severity:** High  **Applies to:** all managed hosts

**Rationale.** A disabled account that retains authorized keys remains a usable entry point and must be remediated.

**Requirement.** An account is deemed to **possess keys** when its `authorized_keys` content contains at least one line that is neither blank nor a comment (a line whose first non-whitespace character is `#`). For every account that possesses keys and is disabled per AC-ACCT-LOCK, the auditor shall propose `ssh.revoke_keys` for that account.

**Implementation guidance.** Whitespace-only lines and comment lines do not constitute possession of keys.

**Verification.** A compliant host has no disabled account that possesses keys.

**References.** Baseline Configuration Guide BCG-4.1

**Revision history.**
- 2023-04: initial publication.
"""

NORMATIVE["AC-EXEMPT"] = """### AC-EXEMPT — Service-account exemptions

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
"""

NORMATIVE["HD-SSHD-DROPIN"] = """### HD-SSHD-DROPIN — Effective sshd drop-in settings

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
"""

NORMATIVE["HD-SSHD-KBDINT"] = """### HD-SSHD-KBDINT — Effective keyboard-interactive authentication

**Domain:** System Hardening  **Severity:** High  **Applies to:** gateway and bastion hosts

**Rationale.** Keyboard-interactive authentication can silently re-enable password-style prompts even where `PasswordAuthentication` is disabled, so its effective value must be controlled with the same rigor as the other sshd keywords.

**Requirement.** In addition to the keywords in HD-SSHD-DROPIN, the auditor shall evaluate `KbdInteractiveAuthentication`. Its effective value is computed using the **same** drop-in precedence rules as HD-SSHD-DROPIN: fragments concatenated in ascending filename order, everything from the first `Match` line onward ignored, and the first global occurrence of the keyword establishing the effective value (keywords compared case-insensitively). When the effective value is absent, or is any value other than an accepted value, the auditor shall propose `systemd.set_dropin` with unit `sshd`, key `KbdInteractiveAuthentication`, and value `no`. The only accepted value is `no`. *(Appendix G adds a deprecated alias keyword for this control.)*

**Implementation guidance.** Reuse the precedence machinery from HD-SSHD-DROPIN; this keyword is evaluated independently of the others.

**Verification.** A compliant host has an effective `KbdInteractiveAuthentication` of `no` and yields no patch for this keyword.

**References.** Governing Security Policy GSP-2024 §6.3; Vendor hardening note VHN-6-2

**Revision history.**
- 2025-03: initial publication.
"""

NORMATIVE["AU-LEDGER"] = """### AU-LEDGER — Audit ledger schema and durability

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
"""

# ---------------------------------------------------------------------------
# Appendix G amendments (authoritative). Real overrides + filler.
# ---------------------------------------------------------------------------
AMENDMENTS_REAL = [
    ("G-2026-01", "AC-ACCT-LOCK / AC-ACCT-SHELL",
     "The locked-password value set in AC-ACCT-LOCK is extended to additionally "
     "include the literal value `*LK*`. Independently, the recognized "
     "non-interactive shell set in AC-ACCT-SHELL is extended to add "
     "`/usr/bin/git-shell` and `/bin/sync`. Accounts matching the extended "
     "criteria are disabled."),
    ("G-2026-02", "AC-SUDO-NOPASSWD",
     "A user specification qualifies as granting passwordless sudo only when the "
     "`NOPASSWD` tag applies to the entire command set, that is, only when the "
     "remainder of the rule contains `NOPASSWD: ALL` (whitespace around the colon "
     "is insignificant). Grants that attach `NOPASSWD` to specific commands do "
     "not qualify and shall not produce a `sudoers.require_password` patch."),
    ("G-2026-03", "AC-EXEMPT",
     "The service-account user-id ceiling in AC-EXEMPT is lowered from `999` to "
     "`499`. The exempt-account roster is extended to add `svc_backup`, so the "
     "roster is `svc_monitor` and `svc_backup`."),
    ("G-2026-04", "HD-SSHD-DROPIN",
     "For `PermitRootLogin` only, the value `prohibit-password` (compared "
     "case-insensitively) is an accepted effective value in addition to `no`; an "
     "effective value of `prohibit-password` shall not produce a patch. The set of "
     "accepted values for `PasswordAuthentication` is unchanged and remains `no` "
     "only."),
    ("G-2026-05", "AC-SUDO-NOPASSWD",
     "In addition to ordinary user specifications, a per-user or per-group "
     "`Defaults` override of the form `Defaults:<binder> !authenticate` grants "
     "passwordless sudo over the entire command set to `<binder>`, exactly as if "
     "that binder held a `NOPASSWD: ALL` user specification. `<binder>` may be a "
     "user, a `%group` reference (resolved through AC-GROUP-EFFECTIVE), or a "
     "negated principal. This overrides the body of AC-SUDO-NOPASSWD, which "
     "otherwise ignores all `Defaults` lines. The resulting principals are subject "
     "to the same disabled-account and AC-EXEMPT filtering as any other grant."),
    ("G-2026-06", "HD-SSHD-KBDINT",
     "`ChallengeResponseAuthentication` is the deprecated spelling of "
     "`KbdInteractiveAuthentication` and denotes the same effective setting. When "
     "computing the effective value for HD-SSHD-KBDINT, occurrences of either "
     "keyword shall be treated as the same setting, so the first occurrence of "
     "either spelling in drop-in order establishes the effective value. The "
     "accepted value set is unchanged and remains `no` only."),
    ("G-2026-07", "AC-SUDO-NOPASSWD",
     "The accumulation model in the body of AC-SUDO-NOPASSWD is superseded by "
     "**last-match-wins** semantics, consistent with how sudo resolves "
     "privileges. Process user specifications and `Defaults:<binder> "
     "!authenticate` overrides in file order; for each principal, the effective "
     "passwordless state is established by the **last** line that names that "
     "principal. Consequently a later specification that grants the principal "
     "sudo without `NOPASSWD: ALL` revokes a passwordless grant made by an "
     "earlier line, and a later `NOPASSWD: ALL` line reinstates it. Group and "
     "alias principals are resolved as in the body, and the resulting state is "
     "applied to each resolved member."),
    ("G-2026-17", "HD-SSHD-DROPIN / HD-SSHD-KBDINT",
     "The instruction in HD-SSHD-DROPIN to ignore conditional blocks is "
     "superseded. The auditor evaluates the effective value of each sshd keyword "
     "for a fixed **audit connection context**: the connecting user is `root` and "
     "the source address is `198.51.100.10`. Drop-in fragments are still "
     "concatenated in ascending filename order and scanned top to bottom. Lines "
     "in global scope (before any `Match`) always apply. A `Match` line opens a "
     "conditional block that applies only when ALL of its criteria match the "
     "audit context; the supported criteria are: `User <list>` — a "
     "comma-separated list of patterns where `*` matches any user and an exact "
     "name matches that user, a pattern may be negated with a leading `!`, and a "
     "negated pattern that matches causes the criterion to fail, so the criterion "
     "matches when the connecting user `root` matches at least one non-negated "
     "pattern and no negated pattern; `Group <list>` — matches when `root` is an "
     "effective member (per AC-GROUP-EFFECTIVE) of at least one of the "
     "comma-separated groups; and `Address <list>` — a comma-separated list of "
     "exact IPv4 addresses or IPv4 CIDR ranges (`a.b.c.d/prefix`), matching when "
     "the source address `198.51.100.10` equals a listed address or falls within "
     "a listed range. `Match all` always applies. A block whose `Match` line "
     "contains any other criterion keyword does not apply. The effective value of "
     "a keyword is the FIRST occurrence, in concatenated order, that appears in "
     "global scope or within an applicable block; occurrences inside "
     "non-applicable blocks are skipped. This context evaluation governs "
     "HD-SSHD-KBDINT as well."),
    ("G-2026-09", "AC-SUDO-NOPASSWD",
     "Sudoers include directives shall be resolved. A line beginning with "
     "`@includedir` or `#includedir` (the leading `#` here is a directive, not a "
     "comment) names a drop-in directory supplied in the snapshot under the "
     "`sudoers.d` map. Its files are spliced into the policy **in ascending "
     "filename order at the position of the directive**, and the resulting lines "
     "participate in alias resolution and in the last-match-wins ordering of "
     "G-2026-07 exactly as if they had appeared inline. A specification that "
     "follows the include directive in the main file is therefore later than any "
     "rule contributed by the included files."),
    ("G-2026-10", "HD-SSHD-DROPIN",
     "For PermitRootLogin, `without-password` is the deprecated spelling of "
     "`prohibit-password` and denotes the same effective setting; it is "
     "therefore accepted wherever `prohibit-password` is accepted. The accepted "
     "value set for the other keywords is unchanged."),
    ("G-2026-15", "AC-SUDO-NOPASSWD",
     "AC-SUDO-NOPASSWD is further narrowed so that a user specification grants "
     "reportable passwordless sudo only when the rule permits execution as the "
     "superuser. The optional Runas specification is the parenthesized list "
     "immediately following the `=` in the rule (for example `(ALL)`, `(root)`, "
     "`(www-data)`, or `(ALL:ALL)`); the runas *user* list is the portion before "
     "any `:` inside the parentheses. When no Runas specification is present the "
     "rule defaults to running as `root`. A `NOPASSWD: ALL` rule whose runas user "
     "list contains `root` or `ALL` qualifies; a `NOPASSWD: ALL` rule whose runas "
     "user list names only non-root principals does not qualify. Under the "
     "last-match-wins ordering of G-2026-07, such a non-qualifying line still "
     "names its principal and therefore sets that principal's effective state to "
     "not-passwordless, just as an ordinary non-NOPASSWD grant would."),
    ("G-2026-18", "AC-SUDO-NOPASSWD",
     "AC-SUDO-NOPASSWD is host-scoped. Each user specification carries a host "
     "field — the token(s) between the principal and the first `=` — which is a "
     "comma-separated list of `ALL`, hostnames, or `Host_Alias` names, each "
     "optionally negated with a leading `!`. The auditor evaluates rules for the "
     "audit host whose hostname is `gw-lab-01`. A specification applies to this "
     "host only when its host field resolves to include `gw-lab-01`: `ALL` "
     "matches, an exact hostname equal to `gw-lab-01` matches, and a `Host_Alias "
     "NAME = ...` (whose members may be hostnames, `ALL`, other host aliases, or "
     "negated entries) is resolved recursively. A specification that does not "
     "apply to the audit host is ignored entirely and therefore does not "
     "participate in the last-match-wins ordering of G-2026-07 for its principal. "
     "`Defaults:<binder> !authenticate` overrides are not host-scoped and apply on "
     "every host."),
    ("G-2026-16", "AC-ACCT-LOCK",
     "AC-ACCT-LOCK is extended with an account-expiration criterion. An account "
     "is additionally disabled when the account-expiry field of its `shadow` "
     "entry — the eighth colon-separated field — is present, non-empty, and a "
     "base-ten integer strictly less than the assessment reference day `20620` "
     "(counted in days since 1970-01-01). An empty expiry field, or an integer "
     "value greater than or equal to `20620`, does not by itself disable the "
     "account. This criterion combines with the password-token and login-shell "
     "criteria: an account disabled by any one criterion is disabled."),
    ("G-2026-19", "AC-SUDO-NOPASSWD",
     "For command lists, sudo command tags are stateful. A `NOPASSWD:` or "
     "`PASSWD:` tag applies to the command entry following the colon and "
     "remains in effect for later comma-separated command entries until another "
     "password tag appears. Therefore a rule such as "
     "`alice ALL=(ALL) NOPASSWD: /usr/bin/id, ALL` grants reportable "
     "passwordless sudo because the later `ALL` command inherits `NOPASSWD`. A "
     "rule such as `alice ALL=(ALL) NOPASSWD: /usr/bin/id, PASSWD: ALL` does "
     "not grant reportable passwordless sudo because the `ALL` command is under "
     "`PASSWD`. This amendment narrows how G-2026-02 is evaluated; the runas "
     "and host-scoping amendments still apply."),
    ("G-2026-20", "AC-KEY-REVOKE",
     "Authorized key files may contain blank lines, comments, marker-style "
     "retired entries, and per-key option prefixes. For AC-KEY-REVOKE, an "
     "account is considered to possess keys only when at least one line contains "
     "an active key record. Blank lines and lines beginning with `#` are "
     "ignored. Lines beginning with `@` are marker-style retired entries and do "
     "not count as active keys. A line whose first non-option token is a "
     "recognized OpenSSH key type (`ssh-*`, `ecdsa-*`, `sk-ssh-*`, "
     "`sk-ecdsa-*`, or `rsa-sha2-*`) counts as an active key; option prefixes "
     "before that token are permitted. Option-only lines without a following "
     "key type do not count."),
]

AMENDMENTS_FILLER = [
    ("G-2026-11", "LG-BANNER-TEXT",
     "The approved pre-authentication banner wording is updated; see Appendix C. "
     "This amendment does not affect auditor behavior."),
    ("G-2026-12", "AU-RETENTION",
     "Audit log retention is extended to 400 days for tier-1 hosts. This "
     "amendment does not affect auditor behavior."),
    ("G-2026-13", "NW-NTP-SOURCES",
     "The list of approved time sources is revised. This amendment does not "
     "affect auditor behavior."),
    ("G-2026-14", "MA-PATCH-WINDOW",
     "The maintenance window is shifted by one hour for the eastern region. This "
     "amendment does not affect auditor behavior."),
    ("G-2026-21", "CM-PACKAGE-MIRROR",
     "The internal package mirror URL rotates quarterly. This amendment does not "
     "affect auditor behavior."),
    ("G-2026-22", "IR-CONTACT-ROSTER",
     "The after-hours incident bridge number is updated. This amendment does not "
     "affect auditor behavior."),
    ("G-2026-23", "LG-FORWARDER-ADDR",
     "The syslog collector address for tier-1 hosts changes. This amendment does "
     "not affect auditor behavior."),
    ("G-2026-24", "MA-REBOOT-NOTICE",
     "Maintenance notifications must be posted 72 hours in advance. This amendment "
     "does not affect auditor behavior."),
    ("G-2026-25", "NW-JUMPHOST-LIST",
     "The approved jump-host inventory is republished. This amendment does not "
     "affect auditor behavior."),
    ("G-2026-26", "CM-CHECKSUM-POLICY",
     "Configuration checksums must be stored alongside the host inventory export. "
     "This amendment does not affect auditor behavior."),
]


def build():
    rng.seed(70414)
    parts = []
    parts.append("# Lab Access Hardening Standard (LAHS)\n")
    parts.append(
        "| Field | Value |\n|---|---|\n| Document | LAHS |\n| Status | In force |\n"
        "| Edition | 2026.1 |\n| Owner | Laboratory Security Engineering |\n"
        "| Classification | Internal |\n"
    )
    parts.append(
        "\n## 1. Purpose and scope\n\n"
        "This Standard defines the configuration baseline that the lab access "
        "gateway's setup auditor enforces. It is the single source of truth for "
        "how a host inventory is parsed, normalized, and evaluated into a set of "
        "remediation patches. The auditor must agree with this Standard for every "
        "host it evaluates.\n\n"
        "Most numbered controls in the body describe enterprise baselines that "
        "surround gateway access. Only the controls called out in Appendix H and "
        "their Appendix G amendments are implemented by the setup auditor.\n\n"
        "### 1.4 Precedence of amendments\n\n"
        "This Standard is maintained as a body of numbered controls followed by "
        "an authoritative list of amendments in **Appendix G**. Where the body of "
        "a control and an amendment in Appendix G disagree, **the amendment in "
        "Appendix G governs**. Implementers must therefore read both the relevant "
        "control and any amendment that references it before encoding behavior. "
        "Amendments that state they do not affect auditor behavior may be noted "
        "and disregarded for implementation.\n"
    )

    parts.append("\n## 2. Definitions\n")
    terms = [
        ("Account", "An entry in the host `passwd` data with a name, user id, primary group id, and login shell."),
        ("Disabled account", "An account meeting the criteria of control AC-ACCT-LOCK as amended."),
        ("Effective group members", "The membership computed under control AC-GROUP-EFFECTIVE."),
        ("Passwordless sudo", "Sudo authority obtained without a password challenge, as determined under AC-SUDO-NOPASSWD as amended."),
        ("Exempt account", "An account excused from passwordless-sudo remediation under AC-EXEMPT as amended."),
        ("Effective sshd value", "The value computed under HD-SSHD-DROPIN as amended."),
        ("Patch", "A single remediation action proposed by the auditor."),
        ("Normalized inventory", "The intermediate representation produced after parsing, on which the policy rules operate."),
    ]
    for t, d in terms:
        parts.append(f"\n**{t}.** {d}\n")

    # Control domains. Interleave normative controls into the relevant domains.
    normative_by_domain = {
        "Access Control": [
            "AC-ACCT-LOCK", "AC-ACCT-SHELL", "AC-GROUP-EFFECTIVE",
            "AC-SUDO-NOPASSWD", "AC-KEY-REVOKE", "AC-EXEMPT",
        ],
        "Audit and Accountability": ["AU-LEDGER"],
        "System Hardening": ["HD-SSHD-DROPIN", "HD-SSHD-KBDINT"],
    }

    section = 3
    for code, dname in DOMAINS:
        parts.append(f"\n## {section}. {dname}\n")
        parts.append(
            f"The controls in this section apply to {rng.choice(HOSTCLASS)}. "
            f"{rng.choice(RATIONALE)}\n"
        )
        n_filler = rng.randint(14, 18)
        idx = 1
        # emit some filler, then normative (if any), then more filler
        for _ in range(n_filler):
            cid = f"{code}-{idx:03d}"
            title = filler_title(rng)
            parts.append("\n" + filler_control(cid, title, dname))
            idx += 1
            if dname in normative_by_domain and normative_by_domain[dname] and rng.random() < 0.4:
                nid = normative_by_domain[dname].pop(0)
                parts.append("\n" + NORMATIVE[nid])
        # flush remaining normative for this domain
        for nid in normative_by_domain.get(dname, []):
            parts.append("\n" + NORMATIVE[nid])
        normative_by_domain[dname] = []
        section += 1

    # Appendices
    parts.append("\n## Appendix A. Host classification\n")
    host_notes = [
        "Gateway hosts terminate interactive laboratory access and run the setup auditor.",
        "Tier-1 hosts host long-lived experiments and inherit the gateway baseline.",
        "Service-account-bearing hosts expose automation principals with lowered UID ranges.",
        "Shared interactive hosts require quarterly access reviews and named custodians.",
        "Bastion hosts forward only management-plane protocols to internal segments.",
    ]
    for _ in range(rng.randint(8, 12)):
        parts.append(
            f"\n- **{rng.choice(['HC', 'GW', 'TL', 'SV'])}-{rng.randint(100,999)}**: "
            + rng.choice(host_notes)
            + " "
            + rng.choice(GUIDANCE)
        )
    parts.append("\n\n## Appendix C. Banner wording\n\n")
    parts.append(
        "Authorized pre-authentication banners shall identify the facility, prohibit "
        "unauthorized use, and provide a monitored contact address. Wording changes "
        "require legal review and do not alter auditor patch behavior.\n"
    )
    parts.append("\n## Appendix B. Control rationale narratives\n")
    narratives = [
        "Gateway auditors reconcile raw configuration because packaged scanners often "
        "mis-handle sudoers aliases and sshd drop-in precedence.",
        "Primary-group membership is easy to miss when only textual group lists are parsed.",
        "Appendix G exists because several 2026 incidents traced to ambiguous body text.",
        "Ledger durability matters for repeat audits even when the patch set is empty.",
        "Service-account exemptions are intentionally narrow to keep automation usable.",
        "Match-block evaluation must use a fixed audit context or hosts disagree on sshd posture.",
        "Includedir splicing changes last-match ordering and cannot be treated as comments.",
    ]
    for i in range(rng.randint(18, 24)):
        parts.append(
            f"\n### Narrative {rng.choice(['NB','RB','XB'])}-{rng.randint(10,99)}\n\n"
            + rng.choice(narratives)
            + " "
            + rng.choice(GUIDANCE)
            + "\n"
        )
    parts.append("\n\n## Appendix D. Assessment procedures\n")
    procedures = [
        "Collect the auditor patch list before applying remediations.",
        "Re-run the auditor after remediation and confirm an empty patch set.",
        "Archive passwd, shadow, group, sudoers, authorized_keys, and sshd drop-ins with the assessment.",
        "Compare two consecutive audits of the same snapshot to confirm idempotence.",
        "Verify ledger schema 2 retention after a non-empty audit.",
    ]
    for _ in range(rng.randint(12, 16)):
        parts.append(
            f"\n- **Procedure {rng.randint(100,999)}.** "
            + rng.choice(procedures)
            + " "
            + rng.choice(VERIFY)
        )
    parts.append("\n\n## Appendix E. Change log\n")
    changelog = [
        "Clarified appendix precedence language.",
        "Added gateway auditor cross-reference in Appendix H.",
        "Retired deprecated sshd keyword spelling notes.",
        "Aligned service-account roster with operations inventory.",
        "Editorial pass on access-control definitions.",
        "Documented includedir handling in AC-SUDO-NOPASSWD guidance.",
    ]
    for _ in range(rng.randint(70, 85)):
        y = rng.choice([2023, 2024, 2025, 2026])
        parts.append(
            f"\n- {y}-{rng.randint(1,12):02d}-{rng.randint(1,28):02d}: "
            + rng.choice(changelog)
        )

    parts.append("\n\n## Appendix F. Cross-domain dependencies\n")
    cross_refs = [
        "AC-KEY-REVOKE depends on the disabled-account determination in AC-ACCT-LOCK and therefore must run after account normalization.",
        "AC-SUDO-NOPASSWD resolves `%group` principals through AC-GROUP-EFFECTIVE before applying exemptions.",
        "HD-SSHD-KBDINT shares drop-in concatenation and Match evaluation with HD-SSHD-DROPIN under G-2026-17.",
        "AU-LEDGER records patch objects emitted by access-control and hardening rules without wrapping them in envelopes.",
        "AC-EXEMPT filters principals after passwordless-sudo detection but before patch emission.",
        "G-2026-09 includedir content participates in G-2026-07 last-match ordering and G-2026-18 host scoping.",
        "G-2026-19 command-tag stickiness applies only after a grant survives G-2026-02, G-2026-15, and G-2026-18 filtering.",
        "G-2026-16 account expiry is evaluated on the shadow field independently of password-token locks.",
        "G-2026-05 Defaults overrides are not host-scoped even when ordinary sudoers specs are.",
        "G-2026-20 key detection ignores marker lines so revoked keys do not block compliance.",
        "G-2026-10 deprecated PermitRootLogin spellings do not change PasswordAuthentication acceptance.",
        "G-2026-04 broadens PermitRootLogin acceptance without altering the sshd patch shape.",
        "Primary-group membership can cause a `%group` sudo grant to apply even when the member list is empty.",
        "Host aliases in sudoers recurse like user aliases and may include negated entries.",
        "A non-applicable Match block must not establish the first effective sshd keyword occurrence.",
    ]
    for i in range(rng.randint(90, 110)):
        parts.append(
            f"\n### Dependency note {i + 1}\n\n"
            + rng.choice(cross_refs)
            + " "
            + rng.choice(DOMAIN_GUIDANCE.get(rng.choice([d[1] for d in DOMAINS]), GUIDANCE))
            + "\n"
        )

    parts.append("\n\n## Appendix I. Assessment evidence examples\n")
    evidence_examples = [
        "An assessor archives the raw `sudoers` text alongside drop-in files when "
        "passwordless grants are disputed; the auditor output is compared after "
        "includedir splicing is applied.",
        "When sshd posture differs between hosts, reviewers first confirm the fixed "
        "audit context rather than assuming global keywords were ignored.",
        "Ledger migration evidence includes the legacy bootstrap row plus every "
        "patch object from a non-compliant fixture run.",
        "Exemption disputes are resolved by checking UID, roster membership, and "
        "whether the principal still holds a reportable passwordless grant.",
        "Key-revocation findings attach the authorized-keys file showing active "
        "key types versus `@` marker lines.",
        "Expiry-related disablement is demonstrated with the eighth shadow field "
        "and the published reference day rather than password-token locks alone.",
        "Statelessness is validated by posting contradictory snapshots for the "
        "same username in sequence and confirming the second result stands alone.",
    ]
    for i in range(rng.randint(80, 95)):
        parts.append(
            f"\n### Evidence example {i + 1}\n\n"
            + rng.choice(evidence_examples)
            + " "
            + rng.choice(VERIFY)
            + "\n"
        )

    parts.append("\n\n## Appendix J. Control crosswalk notes\n")
    crosswalk = [
        "AC-ACCT-LOCK feeds AC-KEY-REVOKE but does not itself emit patches.",
        "AC-SUDO-NOPASSWD is the only control that emits `sudoers.require_password`.",
        "HD-SSHD-DROPIN and HD-SSHD-KBDINT are the only controls that emit `systemd.set_dropin` for sshd.",
        "AU-LEDGER is orthogonal to patch selection and only governs persistence format.",
        "Appendix G amendments may narrow body requirements without introducing new patch types.",
        "A compliant host satisfies every amended control simultaneously and therefore emits no patches.",
        "Random assessment hosts exercise combinations of amendments; partial parsers fail intermittently.",
    ]
    for i in range(rng.randint(70, 85)):
        parts.append(
            f"\n- **Crosswalk {i + 1}.** "
            + rng.choice(crosswalk)
            + " "
            + rng.choice(DOMAIN_REQUIREMENTS.get(rng.choice([d[1] for d in DOMAINS]), GENERIC_REQUIREMENTS))
            + "\n"
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

    parts.append(
        "\n## Appendix H. Implementation checklist\n\n"
        "Implementers should confirm that the auditor, after parsing a host "
        "snapshot, produces exactly the patch set implied by the controls above "
        "as amended by Appendix G. A host already in compliance must yield an "
        "empty patch set.\n"
    )

    text = "\n".join(parts) + "\n"
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as fh:
        fh.write(text)
    words = len(text.split())
    print(f"wrote {OUT}: {len(text)} chars, ~{words} words, ~{int(words*1.33)} tokens")


TITLE_A = ["Mandatory", "Approved", "Restricted", "Centralized", "Hardened",
           "Verified", "Controlled", "Standard", "Baseline", "Monitored"]
TITLE_B = ["banner presentation", "time synchronization", "session timeout",
           "log forwarding", "kernel parameter", "package provenance",
           "filesystem mount option", "service enablement", "credential rotation",
           "interface configuration", "umask default", "core dump handling",
           "module loading", "boot integrity", "console access"]


def filler_title(rng):
    return f"{rng.choice(TITLE_A)} {rng.choice(TITLE_B)}"


if __name__ == "__main__":
    build()
