#!/usr/bin/env python3
"""Local sanity harness for the signalbox snapshot/rollback hardening.

Feeds the seed rows straight into the oracle's pure fold functions and asserts
every new prefix expectation plus the untouched full-log expectations.
"""

from __future__ import annotations

import sys
from pathlib import Path

import yaml

TASK = Path("/Users/fabrice-mac-mini/Documents/snorkel-ai/repair-flask-signalbox-configs")
sys.path.insert(0, str(TASK / "solution"))
sys.path.insert(0, str(TASK / "environment" / "data"))

import repair_cartridge as rc  # noqa: E402
import seed_evidence as seed  # noqa: E402

network = yaml.safe_load((TASK / "environment" / "cartridge" / "network.yaml").read_text())
rows = sorted(seed.ROUTE_LOCK_LOG, key=lambda r: r[0])
corrections = {int(s): (op, det) for s, op, det in seed.LOCK_CORRECTIONS}


def locks_upto(seq: int) -> dict[str, dict]:
    prefix = [row for row in rows if row[0] <= seq]
    return rc.lock_map(rc.effective_locks(network, prefix, corrections))


# --- new snapshot/rollback expectations ---
l55 = locks_upto(55)
assert l55.get("t_sw2_d") == {"sw2": "south"}, l55

l57 = locks_upto(57)
assert "t_sw2_d" not in l57, l57
assert l57.get("t_sw1_c") == {"sw1": "south"}, l57

l58 = locks_upto(58)
assert l58.get("t_sw2_d") == {"sw2": "north"}, l58
assert l58.get("t_sw1_c") == {"sw1": "north"}, l58
assert l58.get("t_sw3_f") == {"sw3": "north", "sw1": "south"}, l58

l59 = locks_upto(59)
assert l59 == l58, (l59, l58)

l61 = locks_upto(61)
assert l61 == {"t_sw3_f": {"sw3": "north"}}, l61

l62 = locks_upto(62)
assert l62.get("t_sw3_f") == {"sw3": "north", "sw1": "south"}, l62
assert l62.get("t_sw1_c") == {"sw1": "north"}, l62
assert l62.get("t_sw2_d") == {"sw2": "north"}, l62

l63 = locks_upto(63)
assert "t_sw3_g" not in l63, l63

# --- untouched full-log expectations ---
full_locks = rc.effective_locks(network, rows, corrections)
full = rc.lock_map(full_locks)
assert full == {
    "t_sw3_f": {"sw3": "north", "sw1": "south"},
    "t_sw1_c": {"sw1": "north"},
    "t_sw2_d": {"sw2": "north"},
}, full

candidates = [station for station, _note in seed.ARRIVALS]
goal, switches = rc.operative_plan(network, full, candidates)
assert goal == "G", (goal, switches)

# determinism over every prefix
for end in range(1, len(rows) + 1):
    a = locks_upto(rows[end - 1][0])
    b = locks_upto(rows[end - 1][0])
    assert a == b, end

print("all rollback hardening checks pass; goal =", goal, "switches =", switches)
