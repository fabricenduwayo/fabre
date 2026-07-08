The Harbor Terminal Trivia replay worker at `/app/worker/replay.py` is broken: tie-breakers
flip between runs, transient `503`s leave events unapplied, and the stewards' post-match
review is only partly reconciled. Fix it so a run is deterministic and writes the official
standings transcript to `/app/output/scoreboard.txt`. Start the referee with
`/app/referee/start.sh` — the Express API listens on `http://127.0.0.1:3000`. The
authoritative rules are in `/app/docs/scoring_standard.md` (numbered controls, Appendix G,
and Appendix H through H-2026-45). Do not change the Express referee in `/app/referee`.

The ledger at `/app/data/match_night.csv` has columns `seq`, `ts`, `kind`, `question`,
`player`, and `payload`. Ingest rows in ascending `seq` order per TR-ORDER-SEQ, POST each
full row to `/v1/ingest` with idempotency key `match-night-{seq}` per section 3 and retry behavior from section 3, and serialize
each body per TR-INGEST-BODY — default `json.dumps` spacing with spaces after `:` and `,`,
since the referee compares stored body bytes verbatim. Take provisional per-player totals
from `GET /v1/standings` after ingest, reconcile `GET /v1/rulings` per Appendix H through H-2026-45 (rebuild each
incident's effective adjustment before applying credits), then re-rank with
TR-TIEBREAK. Use the live rulings API — do not read `/app/data/rulings.json` directly.

Write the section 4 transcript to `--output`: line 1 `STANDINGS match-night-2026-03-15`,
line 2 `rank player score correct first_buzz_seq`, then one row per player with `-` when
no buzzer win, trailing newline after the last row. The worker must accept `--ledger`,
`--api`, and `--output`.
