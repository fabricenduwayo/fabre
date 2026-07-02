# harden-php-api-defaults

HarborDesk Edge PHP REST API that must be reconciled with a long-context
**Hardening Standard** (`/app/docs/standard.md`, body controls plus authoritative
Appendix G). The verifier replays many randomized request lifecycles against one
long-lived PHP process and checks every response and audit row against a hidden
reference implementation.

## Difficulty

`hard`, set from measured accuracy over 5 runs per frontier model: Claude Opus
4.8 passes 0/5 (0%). The earlier edition scored EASY (Opus 80% / GPT-5.5 100%)
because the instructions over-specified the fixes; this edition derives all
behaviour from the long-context Standard, plants long-lived-process state bugs
(sticky CORS, cached bootstrap/token reads) and a silent audit-ledger schema
defect that must be migrated at runtime while preserving history, and replays 45
randomized lifecycles against the hidden reference. The challenge is genuine
engineering, not a long list of edge cases. Oracle passes (1.0) and no-op fails
(0.0); the clean image builds offline.

## Layout

- `environment/harbordesk/` — API source and launcher
- `environment/docs/standard.md` — policy contract
- `tools/gen_standard.py` — regenerates `standard.md`
- `solution/` — oracle PHP files + `solve.sh`
- `tests/` — pytest + hidden reference (`helpers.py`)

## Base image

Canonical Terminal-Bench Python base (`python:3.13-slim-bookworm`) with PHP
via apt.
