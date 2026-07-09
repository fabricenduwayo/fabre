The Harbor Terminal Trivia replay worker at `/app/worker/replay.py` is broken: tie-breakers
flip between runs, transient `503`s leave events unapplied, and the stewards' post-match
review is only partly reconciled. Fix it so a run is deterministic and writes the official
standings transcript to `/app/output/scoreboard.txt`. Start the referee with
`/app/referee/start.sh` — the Express API listens on `http://127.0.0.1:3000`. The
authoritative rules are in `/app/docs/scoring_standard.md` (numbered controls, Appendix G,
and Appendix H through H-2026-51). Do not change the Express referee in `/app/referee`.

The ledger at `/app/data/match_night.csv` has columns `seq`, `ts`, `kind`, `question`,
`player`, and `payload`. Ingest rows in ascending `seq` order per TR-ORDER-SEQ, POST each
full row to `/v1/ingest` with idempotency key `match-night-{seq}` per section 3 and retry behavior from section 3, and serialize
each body per TR-INGEST-BODY — default `json.dumps` spacing with spaces after `:` and `,`,
since the referee compares stored body bytes verbatim. Take provisional per-player totals from `GET /v1/standings` after ingest, then
reconcile `GET /v1/rulings` per all of Appendix H through H-2026-51 — rebuild each
incident's effective adjustment before applying credits. The usual misses are in the
offset/ceiling chain: H-2026-28 voids rulings whose player or offset targets are absent
from provisional standings; H-2026-34/H-2026-40 block deferred correct credit when dual
ceilings zero score credit; H-2026-37/H-2026-48 refund a score offset and skip deferred
correct credit; H-2026-41/H-2026-42 and H-2026-44/H-2026-45 funding-match caps trim
beneficiary credit to what offset solvency collected; and when both `offset_player` and
`offset_correct_player` share a ruling, H-2026-47 caps the primary correct-offset debit
at the score points actually credited to `player` that step after H-2026-27 `max_score_after`
(not the nominal `delta` or `correct_delta`) — even though H-2026-27 applies `correct_delta`
before the score cap — and trim the beneficiary's `correct` when that coupled debit ends
below the applied correct change (H-2026-44); H-2026-46 does the parallel coupling at
deferred `score_applied` after H-2026-42, and either debit is skipped when that capped
score credit is zero. Re-rank with TR-TIEBREAK. Use the
live rulings API — do not read `/app/data/rulings.json` directly.

Write the section 4 transcript to `--output`: line 1 `STANDINGS match-night-2026-03-15`,
line 2 `rank player score correct first_buzz_seq`, then one row per player with `-` when
no buzzer win, trailing newline after the last row. The worker must accept `--ledger`,
`--api`, and `--output`.
