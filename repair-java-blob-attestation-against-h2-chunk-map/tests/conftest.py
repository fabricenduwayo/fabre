"""Fixtures for the attestation verifier.

The shipped store lives at /app/store. Each variant is built fresh into a temp
directory from the verifier-owned corpus generator, and the agent's compiled
auditor is rerun against it. Expected reports are recomputed from whichever
store the auditor is pointed at, so nothing here encodes a verdict.
"""

from __future__ import annotations

import shutil
import tempfile
from pathlib import Path

import pytest

from helpers import SAMPLE_DB_URL, build_store

SEEDS = {
    "variant-a": 41010,
    "variant-b": 41020,
    "variant-c": 41030,
    "variant-d": 41040,
    "variant-e": 41050,
    "variant-f": 41060,
}


@pytest.fixture(scope="session")
def sample_db_url() -> str:
    return SAMPLE_DB_URL


@pytest.fixture(scope="session")
def variant_stores() -> dict[str, str]:
    """Build every variant store once and hand back its jdbc url."""
    root = Path(tempfile.mkdtemp(prefix="attest-variants-"))
    urls = {name: build_store(root / name, name, seed) for name, seed in SEEDS.items()}
    yield urls
    shutil.rmtree(root, ignore_errors=True)
