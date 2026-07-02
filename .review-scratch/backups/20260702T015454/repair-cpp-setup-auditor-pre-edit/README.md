# repair-cpp-setup-auditor

A C++ remediation service (`/v1/setup/audit`) must be brought back into agreement
with the Lab Access Hardening Standard in `/app/docs/standard.md` and have two
runtime defects fixed. The C++ side predates several amendments to the Standard
and has parsing bugs around group membership, locked accounts, sudoers
resolution, and sshd drop-in precedence. On top of the policy work, the service
has two behavioral defects the agent must diagnose:

- it carries per-account state across requests (a process-wide registry), so
  audits drift once several hosts have been processed in the same run;
- its persistent audit ledger silently stopped being written because the on-disk
  file is still in the legacy schema, so the agent must reconcile/migrate it.

The authoritative resolved policy lives only in the hidden tests; the agent must
derive it from the standard (body controls plus the Appendix G amendments) and
make each audit a pure, well-logged function of its request.

## Layout

- `environment/cpp-auditor/` — buggy C++ service (CMake, cpp-httplib, nlohmann/json)
- `environment/docs/standard.md` — long-context policy contract (body + amendments)
- `environment/fixtures/` — raw host config snapshots (passwd/shadow/group/sudoers/keys/sshd)
- `tools/gen_dossier.py` — regenerates `environment/docs/standard.md`

## Difficulty

Difficulty is `hard`: the platform AutoEval measured the two frontier models at
GPT-5.5 80% and Opus 4.8 20% (worst-performing model 1/5). The challenge is
genuine engineering — long-context policy reconciliation across
passwd/shadow/group/sudoers/sshd, plus a stateless-service fix and an audit
ledger schema migration — not a large number of edge cases. The exact I/O
contract (request `files` shape, patch `action` objects, audit context, and the
`schema 2` / `entries` ledger layout) is stated in `instruction.md`; the policy
itself must be derived from the Standard.

## Base image

Final runtime uses the canonical Terminal-Bench Python base
(`python:3.13-slim-bookworm`) with the C++ toolchain added. `cpp-httplib` has no
canonical apt package on bookworm, so its single header (v0.15.3) is vendored
under `cpp-auditor/include/` and copied in at build time — no network fetch — so
the build is hermetic and reproducible offline.
