"""Verifier tests for repair-java-blob-attestation-against-h2-chunk-map.

Every parity check recomputes the correct report from the store the auditor was
pointed at and compares it to what the auditor wrote. The shipped store is one
input, where an object's chunk map and blob agree; the six variant stores are
inputs the auditor was never shown, each pulling the two copies apart so that
attesting the object means judging each copy against what the object declares.
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

from helpers import expected_report, normalise, run_agent


def _report_path(tag: str) -> Path:
    return Path(tempfile.mkdtemp(prefix=f"attest-{tag}-")) / "attestation-report.json"


def _assert_parity(db_url: str, tag: str) -> None:
    got = run_agent(db_url, _report_path(tag))
    want = expected_report(db_url)
    assert normalise(got) == normalise(want), (
        f"{tag}: report disagrees with the store\n"
        f"  got:  {json.dumps(normalise(got))}\n"
        f"  want: {json.dumps(normalise(want))}"
    )


def test_sample_store(sample_db_url: str) -> None:
    """The auditor reproduces the correct report on the shipped store."""
    _assert_parity(sample_db_url, "sample")


def test_variant_a_stale_blob_uses_chunk_map(variant_stores: dict[str, str]) -> None:
    """Where the blob is a stale materialisation and the chunk map still holds
    the declared content, the object is intact, so hashing the blob is wrong."""
    _assert_parity(variant_stores["variant-a"], "variant-a")


def test_variant_b_stale_chunk_map_uses_blob(variant_stores: dict[str, str]) -> None:
    """Where the chunk map is stale and the blob still holds the declared
    content, the object is intact on the blob, so reading the chunk map whenever
    one exists is wrong. The declared length is what tells the copies apart."""
    _assert_parity(variant_stores["variant-b"], "variant-b")


def test_variant_c_unsupported_digest(variant_stores: dict[str, str]) -> None:
    """Content matching a declared sha1 or md5 is unattestable, not intact."""
    _assert_parity(variant_stores["variant-c"], "variant-c")


def test_variant_d_blob_rescues_missing_chunk(variant_stores: dict[str, str]) -> None:
    """A missing chunk file does not condemn an object whose blob still holds the
    declared content; only when no readable copy matches the declared length is
    the object unattestable."""
    _assert_parity(variant_stores["variant-d"], "variant-d")


def test_variant_e_conflicts_from_recompute(variant_stores: dict[str, str]) -> None:
    """Conflicts are the disagreement between the cache and the recomputed
    verdict, in both directions, so they cannot be read back from the cache."""
    _assert_parity(variant_stores["variant-e"], "variant-e")


def test_variant_f_combined(variant_stores: dict[str, str]) -> None:
    """A stale chunk map, a content-bearing blob declared under sha1, a blob
    rescue, and a verified cache row all in one store."""
    _assert_parity(variant_stores["variant-f"], "variant-f")


def test_intact_can_come_from_either_copy(variant_stores: dict[str, str]) -> None:
    """Objects are intact whether the surviving copy is the chunk map (variant a)
    or the blob (variant b), so neither copy is privileged."""
    a = expected_report(variant_stores["variant-a"])
    b = expected_report(variant_stores["variant-b"])
    assert "obj-a001" in a["intact"], "variant a: stale blob should not sink a sound chunk map"
    assert "obj-b001" in b["intact"], "variant b: stale chunk map should not sink a sound blob"
    got_a = normalise(run_agent(variant_stores["variant-a"], _report_path("either-a")))
    got_b = normalise(run_agent(variant_stores["variant-b"], _report_path("either-b")))
    assert got_a == normalise(a)
    assert got_b == normalise(b)


def test_missing_content_never_lands_in_corrupt(variant_stores: dict[str, str]) -> None:
    """No object whose content cannot be read at the declared length is reported
    corrupt; it is unattestable with a missing-content reason."""
    got = run_agent(variant_stores["variant-d"], _report_path("d-buckets"))
    want = expected_report(variant_stores["variant-d"])
    corrupt_ids = {row["object_id"] for row in got.get("corrupt", [])}
    unattestable = {row["object_id"]: row.get("reason") for row in got.get("unattestable", [])}
    missing = [row for row in want["unattestable"] if row["reason"] == "missing_content"]
    assert missing, "variant-d should carry a missing-content object"
    for row in missing:
        assert row["object_id"] not in corrupt_ids, (
            f"{row['object_id']} with missing content was reported corrupt")
        assert unattestable.get(row["object_id"]) == "missing_content"


def test_conflicts_include_cache_verified_but_corrupt(variant_stores: dict[str, str]) -> None:
    """An object the cache calls verified that recomputes to anything but intact
    appears under conflicts."""
    got = normalise(run_agent(variant_stores["variant-e"], _report_path("e-conf")))
    want = normalise(expected_report(variant_stores["variant-e"]))
    assert got["conflicts"] == want["conflicts"]
    assert any(c["cache_status"] == "verified" and c["actual_status"] != "intact"
               for c in want["conflicts"]), "variant-e should carry a verified/corrupt conflict"


def test_points_at_another_store(variant_stores: dict[str, str]) -> None:
    """Pointed at a second store the auditor gives that store's answer, so the
    report comes from the data and not from anything baked in."""
    a = normalise(run_agent(variant_stores["variant-a"], _report_path("cross-a")))
    c = normalise(run_agent(variant_stores["variant-c"], _report_path("cross-c")))
    assert a == normalise(expected_report(variant_stores["variant-a"]))
    assert c == normalise(expected_report(variant_stores["variant-c"]))
    assert a != c, "two different stores produced the same report"


def test_report_is_a_judgment_not_content(variant_stores: dict[str, str]) -> None:
    """The report carries verdicts and object ids, never reconstructed bytes."""
    report_text = _report_path("no-content")
    run_agent(variant_stores["variant-f"], report_text)
    parsed = json.loads(report_text.read_text())
    assert set(parsed) <= {"intact", "corrupt", "unattestable", "conflicts"}
    for row in parsed.get("corrupt", []) + parsed.get("unattestable", []):
        assert set(row) <= {"object_id", "reason"}
