# repair-cpp-setup-auditor

A C++ remediation service (`/v1/setup/audit`) must be brought back into agreement
with the Lab Access Hardening Standard in `/app/docs/standard.md`. The C++ side
predates several amendments to the Standard and also has parsing bugs around
group membership, locked accounts, sudoers negation, and sshd drop-in precedence.
The authoritative resolved policy lives only in the hidden tests; the agent must
derive it from the standard (body controls plus the Appendix G amendments).

## Layout

- `environment/cpp-auditor/` — buggy C++ service (CMake, cpp-httplib, nlohmann/json)
- `environment/docs/standard.md` — long-context policy contract (body + amendments)
- `environment/fixtures/` — raw host config snapshots (passwd/shadow/group/sudoers/keys/sshd)
- `tools/gen_dossier.py` — regenerates `environment/docs/standard.md`

## Base image

Final runtime uses the canonical Terminal-Bench Python base
(`python:3.13-slim-bookworm`) with the C++ toolchain added. `cpp-httplib` has no
canonical apt package on bookworm, so its single header is fetched at build time,
pinned to a release tag and verified by sha256.
