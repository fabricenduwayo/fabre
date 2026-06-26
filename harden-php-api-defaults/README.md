# harden-php-api-defaults

A small HarborDesk PHP REST API ships with insecure staging defaults and a broken
launcher. The agent must harden it so it runs under `php -S` with locked-down
behavior, then the verifier replays a sequence of requests and checks the SQLite
audit ledger.

## What's wrong in the shipped state

- `start.sh` runs `php -S` with no router, so `/health` and `/admin/bootstrap`
  never reach the front controller (everything 404s).
- `config.php` has `debug = true`, wildcard CORS, and `allow_plaintext_bootstrap`.
- `lib/http.php` reflects the configured CORS origin to every caller and pairs a
  wildcard origin with `Allow-Credentials: true` (a combination browsers reject).
- `index.php` lets bootstrap run with no secret, allows re-bootstrapping, stores
  the admin token verbatim, and writes it world-readable (`0644`).
- The on-disk audit ledger has a **legacy schema** (a stale `actor NOT NULL`
  column, no `origin`). `audit_log()` swallows the resulting insert error, so the
  API looks healthy while every audit write silently fails. This is the main
  debugging challenge: the PHP reads as correct, so the agent must reproduce it
  (responses OK but ledger empty), enable debug / inspect the DB to find the
  schema mismatch, and reconcile it in code.

## Secure target (what the oracle does)

- Fix `start.sh` to serve through `index.php`.
- `config.php`: `debug = false`, `allow_plaintext_bootstrap = false`.
- `lib/http.php`: emit CORS only for the allowlisted internal origin, echoing the
  exact origin with `Allow-Credentials: true` and `Vary: Origin` (never `*`).
- `index.php`: bootstrap requires the secret and refuses once an admin token
  exists; the token is stored as a sha256 digest (raw token returned once) and
  the file is written `0600`; `/health` validates the presented bearer token
  against that digest.
- `lib/audit.php`: reconcile the legacy ledger schema (rebuild the table) so
  audit writes succeed.

## Layout

- `environment/harbordesk/` — the API (front controller, config, lib, launcher,
  `data/bootstrap_secret`); `admin_token` and `audit.db` are created at runtime
- `solution/` — corrected files + `solve.sh`
- `tests/` — `test.sh` starts the API via `start.sh`, then pytest replays
  requests and runs SQL assertions on the audit ledger

## Base image

Uses the canonical Terminal-Bench Python base (`python:3.13-slim-bookworm`) with
PHP added via apt. PHP is interpreted, so no build toolchain ends up in the
image and a single stage is appropriate.
