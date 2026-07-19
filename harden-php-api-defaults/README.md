# harden-php-api-defaults

HarborDesk Edge PHP REST API that must be reconciled with a long-context
**Hardening Standard** (`/app/docs/standard.md`, body controls plus authoritative
Appendix G). The verifier replays many randomized request lifecycles against one
long-lived PHP process and checks every response and audit row against a hidden
reference implementation.

## Difficulty

The latest measured edition is `hard`: Claude Opus 4.8 and GPT-5.5 both passed
0/5. The evaluation also found one specification gap: every near-complete run
used a reasonable but different key for the pending secret fingerprint. This
revision names that envelope field and keeps the difficulty in interacting state
rather than an undocumented string literal.

The current revision trims the agent prompt back to control names and the
normative Standard. It adds phase-fresh origin sponsorship, live secret
fingerprint invalidation of partial cutovers, and audit-gated credential
publication. It also denial-fences each origin's sponsorship independently.
The verifier replays 45 randomized lifecycles and injects SQLite
append failures during sponsorship, confirmation, activation, and predecessor
consumption against the real multi-worker API.

## Layout

- `environment/harbordesk/` — API source and launcher
- `environment/docs/standard.md` — policy contract
- `tools/gen_standard.py` — regenerates `standard.md`
- `solution/` — oracle PHP files + `solve.sh`
- `tests/` — pytest + hidden reference (`helpers.py`)

## Base image

Canonical Terminal-Bench Python base (`python:3.13-slim-bookworm`) with PHP
via apt.
