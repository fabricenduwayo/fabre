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
    return f"""### {cid} — {title}

**Domain:** {domain}  **Severity:** {rng.choice(SEV)}  **Applies to:** {rng.choice(HOSTCLASS)}

**Rationale.** {para(RATIONALE, rng.randint(3, 5))}

**Requirement.** {para(GUIDANCE, 1)} The host shall maintain the configuration described in this control at all times, and the setup auditor shall treat any deviation as reportable. {para(RATIONALE, 1)}

**Implementation guidance.** {para(GUIDANCE, rng.randint(5, 8))}

**Verification.** {para(VERIFY, rng.randint(3, 5))}

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
        + para(RATIONALE, 4)
        + "\n\n### 1.4 Precedence of amendments\n\n"
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
        parts.append(f"\n**{t}.** {d} {para(RATIONALE, rng.randint(1,2))}\n")

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
        parts.append(para(RATIONALE, rng.randint(4, 6)) + "\n\n")
        parts.append(para(GUIDANCE, rng.randint(4, 6)) + "\n")
        # filler controls for this domain
        n_filler = rng.randint(11, 15)
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
    for _ in range(rng.randint(8, 12)):
        parts.append(
            f"\n- **{rng.choice(['HC', 'GW', 'TL', 'SV'])}-{rng.randint(100,999)}**: "
            + para(GUIDANCE, rng.randint(2, 3))
        )
    parts.append("\n\n## Appendix C. Banner wording\n\n" + para(GUIDANCE, 6) + "\n")
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
