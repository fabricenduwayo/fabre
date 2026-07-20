"""Verifier tests for rebuild-java-ledger-ingest-parity.

Parity is checked against the legacy jar's own output, computed at verify time on
corpora synthesised for each test. The shipped sample is one of many inputs, not
the target, so an ingester tuned to it does not pass.
"""

from __future__ import annotations

from pathlib import Path

from helpers import (
    SAMPLE_CORPUS,
    compare,
    describe,
    make_corpus,
    run_agent,
    run_oracle,
)

WORK = Path("/tmp/ledger-corpora")


def _assert_parity(name: str, profile: str, seed: int) -> None:
    corpus = make_corpus(WORK / name, profile, seed)
    got, want, got_summary, want_summary = compare(corpus, name)
    assert got == want, (
        f"{name}: {sum(1 for a, b in zip(got, want) if a != b) + abs(len(got) - len(want))} "
        f"rows differ (got {len(got)}, want {len(want)})\n"
        f"  got:\n{describe(got)}\n  want:\n{describe(want)}"
    )
    assert got_summary == want_summary, (
        f"{name}: summary differs\n  got: {got_summary}\n  want: {want_summary}"
    )


def test_sample_corpus_parity() -> None:
    """The ingester reproduces the legacy output on the shipped sample."""
    got, want, got_summary, want_summary = compare(SAMPLE_CORPUS, "sample")
    assert got == want, f"sample rows differ\n  got:\n{describe(got)}\n  want:\n{describe(want)}"
    assert got_summary == want_summary


def test_holdout_corpus_a() -> None:
    """Parity holds on a corpus the ingester was never shown."""
    _assert_parity("holdout-a", "held-out", 4133)


def test_holdout_corpus_b() -> None:
    """Parity holds on a second unseen corpus with a different shape."""
    _assert_parity("holdout-b", "held-out", 9021)


def test_holdout_corpus_c() -> None:
    """Parity holds on a third unseen corpus."""
    _assert_parity("holdout-c", "held-out", 20260720)


def test_duplicate_groups_keep_the_right_row() -> None:
    """Where several rows fold to one key the surviving row is the legacy one, on
    a corpus built so that first-seen and the legacy choice disagree."""
    _assert_parity("dupes", "dupes", 5150)


def test_folded_key_ignores_case_and_spacing() -> None:
    """Rows that differ only by case or internal spacing collapse the way the
    legacy ingester collapses them."""
    _assert_parity("fold", "fold", 6161)


def test_encoding_fallback_is_decided_per_file() -> None:
    """A file carrying one undecodable byte reads back the way the legacy
    ingester reads it, including the lines above that byte."""
    _assert_parity("encoding", "encoding", 7272)


def test_all_axes_together() -> None:
    """Encoding, folding and duplicate survival interact in one corpus."""
    _assert_parity("combined", "combined", 8383)


def test_summary_counts_match_per_file() -> None:
    """The run summary agrees with the legacy summary file by file, not just in
    aggregate."""
    corpus = make_corpus(WORK / "summary", "held-out", 3141)
    _, _, got_summary, want_summary = compare(corpus, "summary")
    assert got_summary.get("per_file") == want_summary.get("per_file")
    assert got_summary.get("canonical_rows") == want_summary.get("canonical_rows")
    assert got_summary.get("total_amount") == want_summary.get("total_amount")


def test_ingester_writes_into_the_store_it_is_given() -> None:
    """Pointed at an empty store the ingester fills it, so the rows come from the
    program rather than from anything left lying around."""
    corpus = make_corpus(WORK / "fresh", "held-out", 2718)
    rows, _ = run_agent(corpus, "fresh-run")
    assert rows, "ingester wrote no rows into a fresh store"
    want, _ = run_oracle(corpus, "fresh-ref")
    assert rows == want


def test_rerunning_is_idempotent() -> None:
    """A second run over the same corpus leaves the same canonical rows."""
    corpus = make_corpus(WORK / "idem", "held-out", 1618)
    first, _ = run_agent(corpus, "idem-1")
    second, _ = run_agent(corpus, "idem-2")
    assert first == second, "a repeated run changed the canonical ledger"
