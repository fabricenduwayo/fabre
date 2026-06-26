Our lab access gateway runs a C++ setup auditor in `/app/cpp-auditor`. It takes a
snapshot of a host's configuration files (passwd, shadow, group, sudoers,
authorized_keys, and the sshd drop-ins) and proposes the patches needed to bring
the host into policy. It exposes `POST /v1/setup/audit` with a request body of
the form `{"files": {...}}` and replies with `{"patches": [...]}`, where each
patch is one of `sudoers.require_password` (target), `ssh.revoke_keys` (target),
or `systemd.set_dropin` (unit/key/value).

The authoritative policy is the **Lab Access Hardening Standard** in
`/app/docs/standard.md`. The auditor has fallen behind the Standard: it predates
several changes and also has a few outright parsing defects, so it now disagrees
with policy on many hosts.

The auditor's logic lives mainly in `/app/cpp-auditor/src/parse.cpp` (turns the
raw files into a normalized inventory) and `/app/cpp-auditor/src/audit.cpp`
(turns that inventory into patches). Fix the service so that, for any host
snapshot, `POST /v1/setup/audit` returns exactly the patch set the Standard
implies; a host that is already compliant must produce an empty patch set.
Rebuild with the provided CMake setup (the existing `build/` target) after
editing.

There is also a **behavioral defect that is not in the policy logic**: operators
report that a freshly started auditor returns correct patches, but after it has
audited several different hosts in the same run its recommendations for some
accounts stop matching the host actually being audited. Each call to
`POST /v1/setup/audit` must depend only on the snapshot in that request — the
auditor must not let one host's results influence another's. Track down where the
service carries state between requests and make each audit self-contained;
inspecting the whole service (not only the parsing and policy code) and exercising
it with several different snapshots in a row will help you reproduce and locate
it.

The behaviors the auditor must get right, all governed by the Standard, are:

- **disabled-account detection** — which `shadow` password tokens and which
  non-interactive login shells mark an account disabled;
- **effective group membership** — including members who belong via their
  *primary* group id, not just the textual member list;
- **passwordless-sudo determination** — which `sudoers` rules actually grant it
  (the scope `NOPASSWD` applies to, alias/`%group`/negation resolution, and
  per-user/group `Defaults` overrides);
- **service-account exemptions** — the exempt roster and the user-id ceiling;
- **effective sshd drop-in settings** — the fragment precedence rules and which
  keywords and values are accepted (including the keyboard-interactive keyword
  and its deprecated alias).

Read the Standard carefully. It is maintained as a body of numbered controls
followed by an **authoritative amendments appendix (Appendix G)**; where the body
and an amendment conflict, the amendment governs (see section 1.4), so several
controls do not mean quite what their body text says on its own. The exact token
sets, accepted values, ceilings, and overrides are defined there as amended.

The toolchain (cmake, g++) is already installed and everything runs offline.
