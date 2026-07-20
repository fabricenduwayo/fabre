"""Generate the artifact-metadata fixture from the H2 store.

Hand-writing this file is how the fixture drifts out of sync with the seed, which
shows up as a baffling wall of 404s rather than an authoring error. Everything here
is derived: the canonical digest is the operative row's digest, and the detached
signature is what ApiServer will accept for that digest and signer.

  python3 tools/gen_registry.py jdbc:h2:file:/path/to/attestation
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from trace_seed import load_store  # noqa: E402

TASK = Path(__file__).resolve().parent.parent
OUT = TASK / "environment" / "artifact-api" / "data" / "registry.json"

# Artifacts with no operative row still get an entry, keyed on the row a shortcut
# would pick, so that skipping a mechanic yields a loud wrong verdict instead of a
# coincidentally-correct 404.
SHORTCUT_ROW = {
    "art-gamma": "ev-g1",   # what a solver who skips the A-2026-03 cascade selects
    "art-mu": "ev-m1",      # what a solver who ignores `status` selects
}

# Fixture-level outcomes. These are properties of the API, not of the database.
BAD_SIGNATURE = {"art-alpha"}
VERIFY_DEGRADED = {"art-nu", "art-epsilon"}


def main(db_url: str) -> int:
    store = load_store(db_url)
    entries = []

    for artifact_id in sorted(store["artifacts"]):
        rows = store["rows"][artifact_id]
        if not rows:
            continue  # art-lambda: nothing to describe
        row = store["operative"].get(artifact_id)
        if row is None:
            pick = SHORTCUT_ROW.get(artifact_id)
            row = next((r for r in rows if r["evidence_id"] == pick), None)
            if row is None:
                continue
        digest = row["sha256_digest"]
        signer = row["signer_key_id"]
        signature = f"sig-{digest[:8]}-{signer}"
        if artifact_id in BAD_SIGNATURE:
            signature = "sig-bad00000-" + signer
        entries.append(
            {
                "artifact_id": artifact_id,
                "version": store["artifacts"][artifact_id]["version"],
                # Deliberately never equal to the canonical digest: an agent that
                # sends this to /verify gets a 409 instead of a pass.
                "registry_digest": "dd" + digest[2:],
                "canonical_digest": digest,
                "detached_signature": signature,
                "signer_key_id": signer,
                "verify_degraded": artifact_id in VERIFY_DEGRADED,
                "registry_degraded": False,
            }
        )

    OUT.write_text(json.dumps({"artifacts": entries}, indent=2) + "\n")
    print(f"wrote {len(entries)} entries to {OUT.relative_to(TASK)}")
    for e in entries:
        flag = ""
        if e["verify_degraded"]:
            flag = "  [verify_degraded]"
        elif e["detached_signature"].startswith("sig-bad"):
            flag = "  [bad_signature]"
        print(f"  {e['artifact_id']:13s} canonical={e['canonical_digest'][:8]} {e['signer_key_id']}{flag}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1] if len(sys.argv) > 1 else "jdbc:h2:file:/tmp/attestation"))
