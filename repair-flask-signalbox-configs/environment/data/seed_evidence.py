#!/usr/bin/env python3
"""Seed the Signalbox evidence DuckDB used by the shift forensics task.

route_lock_log is an ordered bulletin log. Revoke rows void only earlier rows
(sharing the revoked bulletin id, or sharing an amend anchor bulletin on that
track) unless detail lists specific track ids for a partial revoke, names a
stamp, or a row carries expires_after tied to the revoked bulletin. Later rows
from the same bulletin id still apply after a revoke. lock_corrections overrides
logged op codes. hold removes a lock until a release row with the matching
hold_id pops that hold; rows targeting a held track are skipped until the hold
clears. unless_absent drops a lock while listed tracks remain present. unless_present drops a
lock while any listed track is absent. precondition gates apply-time skips.
exclusive_with clears competing tracks after a row lands. Requires, unless_absent, and unless_present
cascades run after every surviving row. snapshot rows capture the surviving lock
map under a snapshot_id; rollback rows restore the named capture and clear hold
stacks on snapshotted tracks.
"""

from __future__ import annotations

import json
from pathlib import Path

import duckdb

EVIDENCE = Path("/app/data/evidence.duckdb")

ROUTE_LOCK_LOG = [
    (1, "BUL-A", "add", "t_sw3_g", json.dumps({"sw3": "south"})),
    (2, "BUL-B", "revoke", "BUL-A", ""),
    (3, "BUL-C", "add", "t_sw3_f", json.dumps({"sw3": "north"})),
    (
        4,
        "BUL-C",
        "add",
        "t_sw1_c",
        json.dumps(
            {
                "when": {"sw1": "north"},
                "requires": ["t_sw3_f"],
                "unless_absent": ["t_sw2_d"],
                "expires_after": "BUL-C",
            }
        ),
    ),
    (5, "BUL-D", "withdraw", "t_sw3_f", ""),
    (6, "BUL-E", "release", "t_sw3_f", json.dumps({"hold_id": "BUL-D"})),
    (
        7,
        "BUL-F",
        "add",
        "t_sw2_d",
        json.dumps({"sw2": "north", "coupling": "yard-link"}),
    ),
    (
        8,
        "BUL-G",
        "amend",
        "t_sw3_f",
        json.dumps({"sw1": "south", "anchor": "BUL-C"}),
    ),
    (9, "BUL-H", "revoke", "BUL-C", json.dumps(["t_sw3_f"])),
    (10, "BUL-I", "amend", "t_sw3_f", json.dumps({"sw3": "north"})),
    (
        11,
        "BUL-M",
        "amend",
        "t_sw2_d",
        json.dumps({"requires": ["t_sw1_c"], "coupling": "yard-link"}),
    ),
    (
        12,
        "BUL-J",
        "add",
        "t_sw3_g",
        json.dumps({"sw3": "south", "stamp": "g-seal"}),
    ),
    (13, "BUL-K", "add", "t_phantom", json.dumps({"sw9": "north"})),
    (14, "BUL-L", "withdraw", "t_never_added", ""),
    (15, "BUL-N", "replace", "t_sw1_c", json.dumps({"when": {"sw1": "south"}})),
    (16, "BUL-G", "amend", "t_sw3_f", json.dumps({"sw1": "south"})),
    (
        17,
        "BUL-O",
        "replace",
        "t_sw1_c",
        json.dumps({"when": {"sw1": "north"}, "requires": ["t_sw3_f"]}),
    ),
    (
        18,
        "BUL-P",
        "add",
        "t_sw2_d",
        json.dumps(
            {"sw2": "north", "requires": ["t_sw1_c"], "coupling": "yard-link"}
        ),
    ),
    (19, "BUL-T", "hold", "t_sw1_c", json.dumps({"hold_id": "yard-check"})),
    (20, "BUL-U", "hold", "t_sw1_c", json.dumps({"hold_id": "signal-test"})),
    (21, "BUL-V", "replace", "t_sw1_c", json.dumps({"when": {"sw1": "south"}})),
    (22, "BUL-W", "release", "t_sw1_c", json.dumps({"hold_id": "yard-check"})),
    (23, "BUL-X", "release", "t_sw1_c", json.dumps({"hold_id": "signal-test"})),
    (24, "BUL-Y", "release", "t_sw1_c", json.dumps({"hold_id": "yard-check"})),
    (25, "BUL-S", "revoke", "_stamp", json.dumps({"stamp": "g-seal"})),
    (
        26,
        "BUL-AA",
        "replace",
        "t_sw1_c",
        json.dumps({"unless_present": ["t_sw3_f"], "when": {"sw1": "south"}}),
    ),
    (27, "BUL-AB", "hold", "t_sw1_c", json.dumps({"hold_id": "gate-test"})),
    (28, "BUL-AC", "release", "t_sw1_c", json.dumps({"hold_id": "gate-test"})),
    (
        29,
        "BUL-AD",
        "replace",
        "t_sw1_c",
        json.dumps({"when": {"sw1": "north"}, "requires": ["t_sw3_f"]}),
    ),
    (30, "BUL-AE", "revoke", "BUL-P", ""),
    (
        31,
        "BUL-AF",
        "add",
        "t_sw2_d",
        json.dumps(
            {
                "sw2": "north",
                "requires": ["t_sw1_c"],
                "coupling": "yard-link",
                "decouple": True,
            }
        ),
    ),
    (32, "BUL-AG", "hold", "t_sw1_c", json.dumps({"hold_id": "defer-gate"})),
    (
        33,
        "BUL-AH",
        "amend",
        "t_sw1_c",
        json.dumps({"requires": ["t_sw3_f", "t_sw2_d"], "defer_until": "BUL-AI"}),
    ),
    (34, "BUL-AI", "release", "t_sw1_c", json.dumps({"hold_id": "defer-gate"})),
    (
        35,
        "BUL-AJ",
        "replace",
        "t_sw1_c",
        json.dumps(
            {
                "when": {"sw1": "north"},
                "requires": ["t_sw3_f"],
                "supersedes": "BUL-AD",
                "exclusive_with": ["t_sw2_d"],
            }
        ),
    ),
    (
        36,
        "BUL-AK",
        "amend",
        "t_sw2_d",
        json.dumps(
            {
                "precondition": {"t_sw1_c": {"sw1": "south"}},
                "when": {"sw2": "south"},
            }
        ),
    ),
    (
        37,
        "BUL-AL",
        "add",
        "t_sw2_d",
        json.dumps({"sw2": "north", "requires": ["t_sw1_c"]}),
    ),
    (
        38,
        "BUL-AM",
        "amend",
        "t_sw2_d",
        json.dumps({"when": {"sw2": "south"}, "witness": "BUL-AK"}),
    ),
    (
        39,
        "BUL-AN",
        "amend",
        "t_sw2_d",
        json.dumps(
            {
                "when": {"sw2": "south"},
                "requires_match": {"t_sw1_c": {"sw1": "north"}},
                "unless_matches": {"t_sw3_f": {"sw1": "south"}},
            }
        ),
    ),
    (
        40,
        "BUL-AO",
        "amend",
        "t_sw2_d",
        json.dumps(
            {
                "requires": ["t_sw3_f"],
                "binds_requires": ["t_sw1_c"],
                "unless_requires_changed": ["t_sw1_c"],
                "requires_stable": ["t_sw1_c"],
                "witness": "BUL-AL",
                "suppresses": ["BUL-AK"],
            }
        ),
    ),
    (
        41,
        "BUL-AP",
        "replace",
        "t_sw1_c",
        json.dumps({"when": {"sw1": "south"}, "witness": "BUL-AK"}),
    ),
    (42, "BUL-AQ", "hold", "t_sw1_c", json.dumps({"hold_id": "final-gate"})),
    (
        43,
        "BUL-AR",
        "amend",
        "t_sw2_d",
        json.dumps({"unless_held": ["t_sw1_c"], "when": {"sw2": "south"}}),
    ),
    (44, "BUL-AS", "release", "t_sw1_c", json.dumps({"hold_id": "final-gate"})),
    (
        45,
        "BUL-AU",
        "amend",
        "t_sw2_d",
        json.dumps({"when": {"sw2": "south"}, "witness": "BUL-AK"}),
    ),
    (
        46,
        "BUL-AT",
        "replace",
        "t_sw1_c",
        json.dumps({"when": {"sw1": "north"}, "requires": ["t_sw3_f"]}),
    ),
    (
        47,
        "BUL-AV",
        "add",
        "t_sw2_d",
        json.dumps(
            {
                "base_when": {"sw2": "north"},
                "inherit_when_from": ["t_sw1_c", "t_sw3_f"],
                "requires": ["t_sw3_f"],
                "binds_requires": ["t_sw1_c"],
                "witness": "BUL-AL",
            }
        ),
    ),
    (
        48,
        "BUL-AW",
        "amend",
        "t_sw2_d",
        json.dumps(
            {
                "requires_when": {
                    "t_sw3_f": {"sw1": "south", "sw3": "north"},
                }
            }
        ),
    ),
    (
        49,
        "BUL-AX",
        "amend",
        "t_sw1_c",
        json.dumps(
            {
                "requires_when": {
                    "t_sw3_f": {"sw1": "south"},
                }
            }
        ),
    ),
    (
        50,
        "BUL-AY",
        "amend",
        "t_sw2_d",
        json.dumps(
            {
                "requires_when": {
                    "t_sw3_f": {"sw1": "south", "sw3": "north"},
                    "t_sw1_c": {"sw1": "north"},
                },
                "unless_requires_when": {
                    "t_sw3_f": {"sw1": "south", "sw3": "north"},
                },
                "binds_requires": ["t_sw1_c"],
            }
        ),
    ),
    (
        51,
        "BUL-AZ",
        "amend",
        "t_sw2_d",
        json.dumps(
            {
                "inherit_when_from": ["t_sw1_c", "t_sw3_f"],
                "requires_when": {
                    "t_sw3_f": {"sw1": "south", "sw3": "north"},
                    "t_sw1_c": {"sw1": "north"},
                },
            }
        ),
    ),
    (
        52,
        "BUL-BA",
        "replace",
        "t_sw2_d",
        json.dumps(
            {
                "when": {"sw2": "north"},
                "requires": ["t_sw3_f"],
                "binds_requires": ["t_sw1_c"],
                "requires_when": {
                    "t_sw3_f": {"sw1": "south", "sw3": "north"},
                    "t_sw1_c": {"sw1": "north"},
                },
            }
        ),
    ),
    (
        53,
        "BUL-BB",
        "add",
        "t_sw3_g",
        json.dumps(
            {
                "when": {"sw3": "south"},
                "witness": "BUL-AL",
                "witness_active": True,
            }
        ),
    ),
    (54, "BUL-BC", "snapshot", "_state", json.dumps({"snapshot_id": "pre-maintenance"})),
    (55, "BUL-BD", "amend", "t_sw2_d", json.dumps({"when": {"sw2": "south"}})),
    (56, "BUL-BE", "hold", "t_sw2_d", json.dumps({"hold_id": "maint-window"})),
    (57, "BUL-BF", "replace", "t_sw1_c", json.dumps({"when": {"sw1": "south"}})),
    (58, "BUL-BG", "rollback", "_state", json.dumps({"snapshot_id": "pre-maintenance"})),
    (59, "BUL-BH", "release", "t_sw2_d", json.dumps({"hold_id": "maint-window"})),
    (60, "BUL-BI", "snapshot", "_state", json.dumps({"snapshot_id": "handover"})),
    (61, "BUL-BJ", "replace", "t_sw3_f", json.dumps({"when": {"sw3": "north"}})),
    (62, "BUL-BK", "rollback", "_state", json.dumps({"snapshot_id": "handover"})),
    (
        63,
        "BUL-BL",
        "add",
        "t_sw3_g",
        json.dumps(
            {
                "when": {"sw3": "south"},
                "witness": "BUL-BJ",
            }
        ),
    ),
    (
        64,
        "BUL-BM",
        "replace",
        "t_sw2_d",
        json.dumps(
            {
                "defer_after_rollback": "handover",
                "when": {"sw2": "south"},
                "witness": "BUL-BJ",
            }
        ),
    ),
    (
        65,
        "BUL-BN",
        "amend",
        "t_sw2_d",
        json.dumps({"when": {"sw2": "south"}, "witness": "BUL-BJ"}),
    ),
    (66, "BUL-BO", "hold", "t_sw1_c", json.dumps({"hold_id": "tail-gate"})),
    (
        67,
        "BUL-BP",
        "amend",
        "t_sw2_d",
        json.dumps({"when": {"sw2": "south"}, "unless_hold_on": ["t_sw1_c"]}),
    ),
    (68, "BUL-BQ", "release", "t_sw1_c", json.dumps({"hold_id": "tail-gate"})),
    (
        69,
        "BUL-BR",
        "amend",
        "t_sw2_d",
        json.dumps(
            {
                "when": {"sw2": "south"},
                "unless_replayed": {"handover": ["BUL-BJ"]},
            }
        ),
    ),
    (
        70,
        "BUL-BS",
        "add",
        "t_sw3_g",
        json.dumps(
            {
                "when": {"sw3": "south"},
                "unless_replayed": {"handover": ["BUL-BJ"]},
            }
        ),
    ),
    (
        71,
        "BUL-BT",
        "add",
        "t_sw3_g",
        json.dumps(
            {
                "when": {"sw3": "south"},
                "witness": "BUL-AL",
                "witness_track": "t_sw2_d",
            }
        ),
    ),
    (
        72,
        "BUL-BU",
        "amend",
        "t_sw2_d",
        json.dumps(
            {
                "when": {"sw2": "south"},
                "void_after_rollback": ["handover"],
            }
        ),
    ),
    (
        73,
        "BUL-BV",
        "add",
        "t_sw3_g",
        json.dumps(
            {
                "when": {"sw3": "south"},
                "witness": "BUL-BA",
                "witness_track": "t_sw2_d",
                "witness_snapshot": "handover",
            }
        ),
    ),
    (
        74,
        "BUL-BW",
        "amend",
        "t_sw2_d",
        json.dumps(
            {
                "when": {"sw2": "south"},
                "unless_snapshot_stale": "handover",
            }
        ),
    ),
]

LOCK_CORRECTIONS = [
    (5, "hold", ""),
    (22, "release", json.dumps({"hold_id": "signal-test"})),
]

ARRIVALS = [
    ("D", "staging platform off the sw2 north leg"),
    ("F", "far platform on the sw3 north leg"),
    ("G", "arrival terminal on the sw3 south leg"),
]

HINTS = [
    (10, "B", "north yard spur, sealed while sw1 holds south"),
    (11, "C", "junction on the south approach toward the midline"),
    (12, "D", "staging platform off the sw2 north leg"),
    (13, "F", "far platform on the sw3 north leg, not the arrival"),
    (14, "G", "arrival terminal on the sw3 south leg"),
]

SHIFT_META = [
    ("train", "orient-7"),
    ("start_station", "A"),
    (
        "win_rule",
        "operative arrival is the candidate station uniquely reachable from the "
        "depot under the effective route locks for some switch lineup",
    ),
]

NOTES = [
    (1, "crew kept the BUL-A g-seal after BUL-B; dispatch targeted F"),
    (2, "logged withdraw on t_sw3_f was a hold; BUL-E release needed hold_id BUL-D"),
    (3, "BUL-H partial revoke also expired BUL-C junction seals still on the books"),
    (4, "validation switches aimed at F while locks still blocked G"),
    (5, "unless_absent on t_sw1_c was ignored when t_sw2_d landed; d-seal stuck"),
    (6, "stamp revoke on g-seal was skipped; BUL-J kept G sealed"),
    (7, "BUL-N south replace stuck until BUL-O replace reset the junction north"),
    (8, "nested yard-check/signal-test holds skipped BUL-V replace until both released"),
    (
        9,
        "gate-test hold cleared but unless_present south replace on t_sw1_c was not "
        "re-applied before the final north reset",
    ),
    (
        10,
        "full revoke on BUL-P skipped yard-link coupling and left stale t_sw2_d rows",
    ),
    (
        11,
        "defer_until BUL-AI requires amend fired before release restore and dropped t_sw2_d",
    ),
    (
        12,
        "supersedes on BUL-AD was ignored so BUL-AJ replace stacked on the old junction row",
    ),
    (
        13,
        "BUL-AJ exclusive_with must drop stale t_sw2_d rows when the final junction replace lands",
    ),
    (
        14,
        "BUL-AK south amend was applied even though t_sw1_c precondition was north at seq 36",
    ),
    (
        15,
        "BUL-AL d-seal restore was skipped after exclusive_with cleared t_sw2_d on the final junction replace",
    ),
    (
        16,
        "witness treated log presence as apply; south d-seal amend fired without a prior successful BUL-AK row",
    ),
    (
        17,
        "unless_matches ignored under north f-seal so south d-seal amend stuck on the yard link",
    ),
    (
        18,
        "requires_match only checked at apply time, not during requires/unless cascades",
    ),
    (
        19,
        "suppresses skipped before witness amend; stale BUL-AK row still blocked d-seal dependency refresh",
    ),
    (
        20,
        "witness treated log presence as apply; south junction replace fired without a prior successful BUL-AK row",
    ),
    (
        21,
        "unless_held ignored during final-gate hold; south d-seal amend landed while t_sw1_c was held",
    ),
    (
        22,
        "unless_present south replace re-applied on final-gate release and stuck until BUL-AT north reset",
    ),
    (
        23,
        "binds_requires treated as static requires; t_sw2_d dropped when junction requires changed",
    ),
    (
        24,
        "witness treated log presence as apply; BUL-AU south amend fired without a prior successful BUL-AK row",
    ),
    (
        25,
        "unless_requires_changed ignored after final-gate release; stale t_sw2_d kept when junction requires cleared",
    ),
    (
        26,
        "BUL-AV recovery add skipped after unless_requires_changed drop; yard link missing at shift end",
    ),
    (
        27,
        "requires-only witness amend cleared t_sw2_d when map; empty when treated as unconditional lock",
    ),
    (
        28,
        "requires_when treated presence-only; yard link stayed even though f-seal when was incomplete",
    ),
    (
        29,
        "BUL-W release hold_id was corrected from yard-check to signal-test in lock_corrections",
    ),
    (
        30,
        "requires_stable only watched requires tuple; yard link stuck after junction when flipped south",
    ),
    (
        31,
        "BUL-AV yard-link add kept static sw2 north instead of inheriting merged junction and f-seal when maps",
    ),
    (
        32,
        "inherit_when_from ignored during fixpoints so t_sw2_d when stayed stale after BUL-AY requires_when refresh",
    ),
    (
        33,
        "BUL-BA static replace skipped after inherited when tail; route_locks kept composite switch keys on t_sw2_d",
    ),
    (
        24,
        "witness_active treated prior apply as enough; BUL-BB g-seal landed after BUL-AL retired from state",
    ),
    (
        34,
        "pre-maintenance rollback was skipped; south d-seal amend and south junction replace stuck to shift end",
    ),
    (
        35,
        "rollback restored the lock map but kept the maint-window hold; d-seal stayed off the board",
    ),
    (
        36,
        "BUL-BH release fired against the already-cleared maint-window stack instead of being ignored",
    ),
    (
        37,
        "handover rollback missed; the f-seal north replace wiped the junction and yard link through cascades",
    ),
    (
        38,
        "witness_active treated the rolled-back BUL-BJ replace as still owning a lock; final g-seal add landed",
    ),
    (
        39,
        "defer_after_rollback rows were folded at log tail instead of when handover rollback restored; "
        "BUL-BM south d-seal landed on applied_bulletins alone",
    ),
    (
        40,
        "rollback kept BUL-BJ in witness history after handover restore; BUL-BL g-seal and BUL-BN "
        "south amend fired on log presence alone",
    ),
    (
        41,
        "unless_hold_on ignored during tail-gate hold so BUL-BP south d-seal amend landed early; "
        "unless_replayed ignored after handover rollback so BUL-BR/BUL-BS replayed BUL-BJ-era rows",
    ),
    (
        42,
        "witness_track treated like applied_bulletins membership; BUL-BT g-seal landed even "
        "though BUL-AL no longer owns t_sw2_d",
    ),
    (
        43,
        "void_after_rollback ignored on BUL-BU so south d-seal replay fired after handover rollback",
    ),
    (
        44,
        "witness_snapshot treated like witness_track alone; BUL-BV g-seal landed even though "
        "t_sw2_d when map no longer matched the handover capture",
    ),
    (
        45,
        "unless_snapshot_stale ignored on BUL-BW so south d-seal amend replayed after "
        "handover tracks drifted from the capture",
    ),
]

ROUTE_LOCK_GLOSSARY = [
    (
        "revoke",
        "Void every earlier row sharing the revoked bulletin id on the same track. "
        "Partial revokes list scoped track ids in detail JSON. Stamp revokes use "
        "track_id _stamp with a stamp name in detail and void every earlier row "
        "carrying that stamp. Rows with expires_after void when the named bulletin "
        "is revoked. Later rows from the same bulletin still apply after a revoke "
        "unless voided.",
    ),
    (
        "hold",
        "Remove a track lock until release with matching hold_id. Nested holds "
        "stack per track. Rows targeting a held track skip until the hold clears.",
    ),
    (
        "release",
        "Pop the top nested hold on the track. required hold_id must match the "
        "top hold or the release is ignored.",
    ),
    (
        "unless_absent",
        "Drop the lock while any listed track is absent from state; re-apply in "
        "seq order once conditions restore.",
    ),
    (
        "unless_present",
        "Drop the lock while any listed prerequisite track is absent; re-apply in "
        "seq order after a matching release restores conditions.",
    ),
    (
        "coupling",
        "Full revoke on a coupled bulletin voids every earlier row sharing that "
        "coupling id unless decouple is set on a later add.",
    ),
    (
        "defer_until",
        "Row stays pending until the named release completes, then applies in seq "
        "order.",
    ),
    (
        "supersedes",
        "Void surviving lower-seq rows from the named bulletin before the row "
        "applies.",
    ),
    (
        "exclusive_with",
        "Clear listed competing tracks from state after the row lands.",
    ),
    (
        "precondition",
        "Skip apply when required switch positions in detail do not match the "
        "effective lock state at apply time.",
    ),
    (
        "amend",
        "Merge when maps and dependency lists into an existing lock. requires-only "
        "amend replaces dependency lists without changing when maps. amend without "
        "a surviving add seeds a new lock. anchored amends void when their anchor "
        "bulletin is partially revoked on that track.",
    ),
    (
        "replace",
        "Reset the track lock from detail when maps; do not merge like amend.",
    ),
    (
        "requires_cascade",
        "After every surviving row, drop locks whose explicit requires list "
        "references a track that left the effective set.",
    ),
    (
        "cascade_fixpoint",
        "After every surviving row rerun requires, unless_absent, unless_present, "
        "unless_held, requires_match, unless_matches, witness, witness_active, suppresses, "
        "binds_requires, unless_requires_changed, requires_when, "
        "unless_requires_when, requires_stable, and inherit_when_from until stable.",
    ),
    (
        "requires_match",
        "Drop during every cascade while any listed track is absent or its when-map "
        "misses a listed switch position.",
    ),
    (
        "unless_matches",
        "Drop while any listed track is locked and its when-map contains every "
        "listed switch position.",
    ),
    (
        "witness",
        "Skip the row unless the named bulletin already contributed a successfully "
        "applied row earlier in seq order.",
    ),
    (
        "witness_active",
        "When true alongside witness, skip unless the named bulletin still owns a "
        "surviving track lock in state at apply time — prior apply alone is not enough.",
    ),
    (
        "witness_track",
        "When set alongside witness, skip unless the named bulletin owns the surviving "
        "lock on that exact track_id in state at apply time — membership in "
        "applied_bulletins alone is not enough.",
    ),
    (
        "suppresses",
        "Void every surviving lower-seq row from the listed bulletin ids before "
        "the row applies.",
    ),
    (
        "unless_held",
        "Skip the row at apply time while any listed track is held. Surviving locks "
        "carrying unless_held drop while a listed track is held.",
    ),
    (
        "binds_requires",
        "Union the listed track ids and their current requires lists into this lock "
        "during every requires cascade fixpoint, in addition to explicit requires.",
    ),
    (
        "unless_requires_changed",
        "Snapshot each listed track's effective requires at apply time and drop this "
        "lock during cascade fixpoints if any watched effective requires tuple changes.",
    ),
    (
        "requires_when",
        "During every cascade fixpoint, each effective requires entry must appear in "
        "state with a when-map containing every listed switch position.",
    ),
    (
        "unless_requires_when",
        "Drop during cascade fixpoints while any listed track is locked but its "
        "when-map misses a listed switch position.",
    ),
    (
        "requires_stable",
        "Snapshot each listed track's effective requires tuple and when-map at apply "
        "time and drop this lock during cascade fixpoints if either tuple changes.",
    ),
    (
        "inherit_when_from",
        "Merge base_when with the current when maps of listed source tracks in order "
        "(later sources override switch keys). Recompute during every cascade fixpoint; "
        "drop the lock if any source track is absent.",
    ),
    (
        "base_when",
        "Static switch positions merged before inherit_when_from sources during when "
        "composition.",
    ),
    (
        "snapshot",
        "Capture the surviving lock map under snapshot_id after cascade fixpoints "
        "settle, including when maps, dependency metadata, and bulletin ownership. "
        "A later snapshot with the same id overwrites the capture.",
    ),
    (
        "rollback",
        "Replace the surviving lock map with the named snapshot capture and clear "
        "hold stacks on snapshotted tracks. Tracks absent from the snapshot drop "
        "from state; holds on tracks absent from the snapshot stay in place. "
        "Rollback with an unknown snapshot_id is ignored. Retire witness history "
        "next: drop every bulletin from applied_bulletins that does not own a lock "
        "in the restored snapshot capture. Only after retire runs, flush any "
        "defer_after_rollback queue for the same snapshot_id. Cascade fixpoints "
        "rerun after the restore. witness_active still requires the witness bulletin "
        "to own a surviving track lock at apply time.",
    ),
    (
        "defer_after_rollback",
        "Row stays pending until a rollback restores the named snapshot_id, then "
        "applies in seq order before the log continues. Like defer_until, the row "
        "does not run at its seq position.",
    ),
    (
        "unless_hold_on",
        "Skip apply while any listed track has an active hold stack, even when the "
        "row targets a different track.",
    ),
    (
        "unless_replayed",
        "Skip apply when any listed bulletin under the named snapshot_id was last "
        "successfully applied before that snapshot's most recent rollback generation. "
        "Track rollback generation on each rollback and bulletin apply generation on "
        "each successful row.",
    ),
    (
        "void_after_rollback",
        "Skip apply once any listed snapshot_id has been restored by a rollback row. "
        "Unlike unless_replayed this gates on snapshot rollback events, not bulletin "
        "apply generation.",
    ),
    (
        "witness_snapshot",
        "When set alongside witness and witness_track, skip unless the witness bulletin "
        "owns witness_track in state and its when-map equals the named snapshot capture "
        "for that track — current ownership alone is not enough.",
    ),
    (
        "unless_snapshot_stale",
        "Skip apply while any track present in both state and the named snapshot capture "
        "has a different when-map or bulletin owner than the capture.",
    ),
]


def main() -> None:
    EVIDENCE.parent.mkdir(parents=True, exist_ok=True)
    if EVIDENCE.exists():
        EVIDENCE.unlink()
    conn = duckdb.connect(str(EVIDENCE))
    conn.execute(
        "CREATE TABLE route_lock_log "
        "(seq INTEGER, bulletin TEXT, op TEXT, track_id TEXT, detail TEXT)"
    )
    conn.executemany(
        "INSERT INTO route_lock_log VALUES (?, ?, ?, ?, ?)", ROUTE_LOCK_LOG
    )
    conn.execute(
        "CREATE TABLE lock_corrections "
        "(seq INTEGER PRIMARY KEY, effective_op TEXT, effective_detail TEXT)"
    )
    conn.executemany(
        "INSERT INTO lock_corrections VALUES (?, ?, ?)", LOCK_CORRECTIONS
    )
    conn.execute(
        "CREATE TABLE arrival_candidates (station_id TEXT PRIMARY KEY, note TEXT)"
    )
    conn.executemany("INSERT INTO arrival_candidates VALUES (?, ?)", ARRIVALS)
    conn.execute(
        "CREATE TABLE hint_clues (seq INTEGER, station_id TEXT, hint TEXT)"
    )
    conn.executemany("INSERT INTO hint_clues VALUES (?, ?, ?)", HINTS)
    conn.execute("CREATE TABLE shift_meta (key TEXT PRIMARY KEY, value TEXT)")
    conn.executemany("INSERT INTO shift_meta VALUES (?, ?)", SHIFT_META)
    conn.execute(
        "CREATE TABLE failed_attempt_notes (attempt_id INTEGER, note TEXT)"
    )
    conn.executemany("INSERT INTO failed_attempt_notes VALUES (?, ?)", NOTES)
    conn.execute(
        "CREATE TABLE route_lock_glossary (key TEXT PRIMARY KEY, definition TEXT)"
    )
    conn.executemany(
        "INSERT INTO route_lock_glossary VALUES (?, ?)", ROUTE_LOCK_GLOSSARY
    )
    conn.close()


if __name__ == "__main__":
    main()
