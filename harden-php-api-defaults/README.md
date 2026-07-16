# harden-php-api-defaults

HarborDesk Edge PHP REST API that must be reconciled with a long-context
**Hardening Standard** (`/app/docs/standard.md`, body controls plus authoritative
Appendix G). The verifier replays many randomized request lifecycles against one
long-lived PHP process and checks every response and audit row against a hidden
reference implementation.

## Difficulty

The latest measured edition is `trivial`: Claude Opus 4.8 and GPT-5.5 both
passed 5/5. Those agents were given amendment ids, exact outcomes, and the
ledger migration shape in the prompt, so most replaced the four small PHP files
directly. This revision is not yet difficulty-measured and keeps the measured
label until new platform runs exist.

The revised Standard adds a deployment-generation credential cutover with a
shared two-use predecessor overlap. Rotation, concurrent health requests, later
cutovers, live secret/generation reads, and the reseedable audit migration now
interact in one long-lived multi-worker service. The verifier replays 45
randomized lifecycles and a concurrent cutover case against the real API.

## Layout

- `environment/harbordesk/` — API source and launcher
- `environment/docs/standard.md` — policy contract
- `tools/gen_standard.py` — regenerates `standard.md`
- `solution/` — oracle PHP files + `solve.sh`
- `tests/` — pytest + hidden reference (`helpers.py`)

## Base image

Canonical Terminal-Bench Python base (`python:3.13-slim-bookworm`) with PHP
via apt.
