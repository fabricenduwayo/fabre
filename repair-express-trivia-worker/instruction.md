The Harbor Terminal Trivia replay worker at `/app/worker/replay.py` is broken: tie-breakers
flip between runs, transient `503`s leave events unapplied, and the stewards' post-match
review is only partly reconciled. Fix it so a run is deterministic and writes the official
standings transcript to `/app/output/scoreboard.txt`. Start the referee with
`/app/referee/start.sh` — the Express API listens on `http://127.0.0.1:3000`. The
authoritative rules are in `/app/docs/scoring_standard.md` (numbered controls, Appendix G,
and Appendix H through H-2026-22). Do not change the Express referee in `/app/referee`.

The ledger at `/app/data/match_night.csv` has columns `seq`, `ts`, `kind`, `question`,
`player`, and `payload`. Ingest rows in ascending `seq` order (ignore `ts` for ordering),
POST each full row to `/v1/ingest` with `X-Idempotency-Key` `match-night-{seq}`, retry
transient `503`s with backoff, and serialize each body per TR-INGEST-BODY (all six ledger
fields, JSON `null` for empty `question`/`player`, `{}` for empty `payload`, default
`json.dumps` spacing). Take provisional per-player totals from `GET /v1/standings`, reconcile
`GET /v1/rulings` per Appendix H: replay incidents in ascending `ruling_seq`, apply the
sequential primary floor checkpoints, then the deferred post-floor pass, and honor the
dependency and paired-incident rules through H-2026-22. A ruling whose `player` never
appears in the provisional standings is void (H-2026-03) — skip it and do not add that
player to the transcript. A `paired_incident` ruling is void unless its named parent is
active in the incident map when the ruling is recorded, and rescinding an incident also
clears every incident still paired to it, cascading transitively and dropping those
incidents from the deferred pass (H-2026-12, H-2026-15). A surviving primary ruling whose
`requires_incident` chain or `paired_incident` names an incident that was ever rescinded is
void even if that incident is later re-issued (H-2026-16, H-2026-17), while
`supersedes_incident` removes the named incident without that rescind taint (H-2026-21).
For H-2026-19, store a frozen deferred snapshot only when the deferred ruling carries
`paired_incident` and that parent is active at record time; a later rescind of the paired
parent must not drop that snapshotted post-floor adjustment. When a later `amend` supersedes
a snapshotted incident, copy the amended `player`, `delta`, and `correct_delta` into the
frozen snapshot so the deferred adjustment lands on the amended player even after the parent
is rescinded (H-2026-20); demoting a snapshotted incident to primary instead drops paired
frozen snapshots (H-2026-22). Then re-rank with TR-TIEBREAK. Write the section 4 transcript to
`--output`: line 1 `STANDINGS match-night-2026-03-15`, line 2
`rank player score correct first_buzz_seq`, then one row per player with `-` when no buzzer
win, trailing newline after the last row. The worker must accept `--ledger`, `--api`, and
`--output`.
