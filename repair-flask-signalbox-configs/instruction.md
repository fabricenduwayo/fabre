The Signalbox dispatch cartridge at `/app/cartridge/network.yaml` and
`/app/cartridge/dispatch.toml` is corrupted. Forensic evidence in
`/app/data/evidence.duckdb` is authoritative — do not copy values from the
cartridge files. Repair both cartridge files in place, implement
`/app/tools/play_shift.py` so `python3 /app/tools/play_shift.py` drives the
shift, and write a winning shift transcript to `/app/output/transcript.json`
using the Flask referee already listening on `http://127.0.0.1:5000`. Do not
start another referee process or bind port 5000 yourself. Successful dispatches
are logged by the referee to `/app/data/dispatch.duckdb` in its `dispatch_log`
table.

Query `route_lock_log`, `lock_corrections`, `arrival_candidates`,
`hint_clues`, `shift_meta`, `failed_attempt_notes`, and `route_lock_glossary`.
For each log row apply the `lock_corrections` effective op and effective
detail before folding — corrected detail can override release `hold_id` and
other fields that differ from the raw log (for example a release row whose
logged hold_id does not match the corrected one). Fold surviving rows in seq
order on seal tracks `t_sw1_c`, `t_sw2_d`, `t_sw3_f`, and `t_sw3_g` with
switches `sw1`, `sw2`, and `sw3` at `north` or `south`. Revoke rows void earlier rows:
partial revokes list scoped track ids; stamp revokes (revoke on `_stamp` with
a stamp name in detail) void every earlier row carrying that stamp; rows with
`expires_after` void when the named bulletin is revoked. Later rows from the
same bulletin still apply after a revoke unless voided. hold removes a track
lock until release with matching `hold_id`; nested holds stack per track and
rows targeting a held track skip until the hold clears. unless_present rows
drop while listed tracks are absent and re-apply in seq order once release
restores their conditions. unless_absent drops while listed tracks remain
present. Full revoke on a coupled bulletin voids every earlier row sharing
that coupling id unless `decouple` is set. defer_until rows stay pending until
the named release completes then apply. supersedes voids surviving lower-seq
rows from the named bulletin before the row applies. exclusive_with clears
listed competing tracks after the row lands. precondition skips apply when
required switch positions do not match. replace resets when positions; amend
merges when maps; requires-only amend replaces dependency lists without
changing when maps; amend without a surviving add seeds a new lock; anchored
amends void when their anchor bulletin is partially revoked on that track.
Detail may carry `base_when` plus `inherit_when_from` to compose when maps
from listed source tracks instead of listing every switch inline.

After every surviving row run cascade fixpoints for requires, unless_absent,
unless_present, unless_held, requires_match, unless_matches, witness,
suppresses, binds_requires, unless_requires_changed, requires_when,
unless_requires_when, requires_stable, and inherit_when_from as defined in
`route_lock_glossary`. witness skips unless the named bulletin already
contributed a successfully applied row; suppresses voids lower-seq rows from
listed bulletins before apply; unless_held skips apply while listed tracks are
held and drops surviving locks carrying it while held; binds_requires unions
listed track requires during fixpoints; unless_requires_changed snapshots
dependency tuples at apply time and drops when watched tracks change;
requires_stable snapshots both requires tuples and when maps and drops when
either drifts; requires_when requires each dependency to carry matching when
positions during fixpoints, not mere presence; unless_requires_when drops while
a listed track is locked but its when map misses positions; inherit_when_from
recomputes composed when maps from base_when and source tracks during
fixpoints and drops the lock if a source track disappears. Read
`failed_attempt_notes` for crew mistakes.

`network.yaml` `route_locks` must equal the resolved lock set using the referee
`{track, when}` schema with non-empty when maps. Derive the operative goal
from `arrival_candidates` and `shift_meta.win_rule` as the candidate station
uniquely reachable from the depot under effective locks for some switch
lineup. In `dispatch.toml` set `goal_station` to that operative goal, keep
train and start from `shift_meta`, copy every hint string from `hint_clues`
into `[hints]` keyed by station id, and restore `[validation]` switch positions
for a winning lineup.

`/app/output/transcript.json` must be the `GET /v1/transcript` body of a
completed shift where train `orient-7` runs from `A` to the operative goal
with `won` true, including `train`, `start`, `goal`, `history`, `moves`,
`won`, and `switches`.
