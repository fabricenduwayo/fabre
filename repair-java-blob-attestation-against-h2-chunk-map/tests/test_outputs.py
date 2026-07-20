"""Verifier tests for repair-java-blob-attestation-against-h2-chunk-map.

Every parity check recomputes the correct report from the store the auditor was
pointed at and compares it to what the auditor wrote. The shipped store is one
input; the six variant stores are inputs the auditor was never shown, each
isolating one way the attestation cache or the blob copy disagrees with what the
durable chunk map actually hashes to.
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


def test_variant_a_chunk_authority(variant_stores: dict[str, str]) -> None:
    """Objects whose blob copy is a stale materialisation are judged on their
    chunk map, not on the blob."""
    _assert_parity(variant_stores["variant-a"], "variant-a")


def test_variant_b_partial_materialisation(variant_stores: dict[str, str]) -> None:
    """A blob copy holding only the first chunk of a multi-chunk object does not
    stand in for the object."""
    _assert_parity(variant_stores["variant-b"], "variant-b")


def test_variant_c_unsupported_digest(variant_stores: dict[str, str]) -> None:
    """Content matching a declared sha1 or md5 is unattestable, not intact."""
    _assert_parity(variant_stores["variant-c"], "variant-c")


def test_variant_d_missing_chunk_is_unattestable(variant_stores: dict[str, str]) -> None:
    """A chunk row pointing at a missing file makes the object unattestable, not
    corrupt, even when a stale blob copy is present."""
    _assert_parity(variant_stores["variant-d"], "variant-d")


def test_variant_e_conflicts_follow_the_chunk_map(variant_stores: dict[str, str]) -> None:
    """The conflict set is the disagreement between the cache and what the chunk
    map hashes to, so it cannot be produced from the blob copy."""
    _assert_parity(variant_stores["variant-e"], "variant-e")


def test_variant_f_combined(variant_stores: dict[str, str]) -> None:
    """Stale blob, declared sha1, verified cache and a blob whose sha1 matches
    the declared digest all at once."""
    _assert_parity(variant_stores["variant-f"], "variant-f")


def test_missing_content_never_lands_in_corrupt(variant_stores: dict[str, str]) -> None:
    """No object whose content cannot be read is reported corrupt; it is
    unattestable with a missing-content reason."""
    got = run_agent(variant_stores["variant-d"], _report_path("d-buckets"))
    want = expected_report(variant_stores["variant-d"])
    corrupt_ids = {row["object_id"] for row in got.get("corrupt", [])}
    unattestable = {row["object_id"]: row.get("reason") for row in got.get("unattestable", [])}
    for row in want["unattestable"]:
        if row["reason"] == "missing_content":
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
    raw = report_text.read_text()
    parsed = json.loads(raw)
    assert set(parsed) <= {"intact", "corrupt", "unattestable", "conflicts"}
    for row in parsed.get("corrupt", []) + parsed.get("unattestable", []):
        assert set(row) <= {"object_id", "reason"}
