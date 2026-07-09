"""Pytest fixtures for the release-decision verifier.

These fixtures load the agent-produced manifest, read the canonical evidence
from the live H2 experiment store and registry API, and build the variant H2
databases the agent's jar is rerun against. The pure helpers live in
``helpers.py``.
"""

from __future__ import annotations

import json
import subprocess
import tempfile
from pathlib import Path

import pytest

from helpers import (
    CANDIDATES_URL,
    MAIN_DB_URL,
    MANIFEST_PATH,
    TESTS_DIR,
    expected_decision,
    http_get_json,
    load_evidence,
    run_h2_script,
    wait_for_api,
)


@pytest.fixture(scope="session")
def manifest() -> dict:
    """Parse the agent-produced release-decision manifest."""
    assert MANIFEST_PATH.is_file(), f"expected manifest at {MANIFEST_PATH}"
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


@pytest.fixture(scope="session")
def registry() -> list[dict]:
    """Candidate list reported by the running registry API.

    The API is started by the container entrypoint; if it is not answering yet
    (or was stopped), bring it back with the same launcher script the agent
    uses, then wait for readiness.
    """
    if not wait_for_api(45):
        subprocess.run(
            ["bash", "/app/start-registry.sh"],
            capture_output=True,
            text=True,
            timeout=240,
        )
        assert wait_for_api(120), "registry API never became ready on port 8080"
    candidates = http_get_json(CANDIDATES_URL)
    assert isinstance(candidates, list) and candidates, (
        "registry API returned no candidate models"
    )
    return candidates


@pytest.fixture(scope="session")
def registry_by_id(registry: list[dict]) -> dict[str, dict]:
    """Registry candidates keyed by model id."""
    return {candidate["id"]: candidate for candidate in registry}


@pytest.fixture(scope="session")
def evidence(registry: list[dict]) -> dict:
    """Canonical evidence from the shipped H2 experiment database."""
    return load_evidence(MAIN_DB_URL)


@pytest.fixture(scope="session")
def expected(registry: list[dict], evidence: dict) -> dict:
    """The canonical decision recomputed from live evidence + policy gates."""
    return expected_decision(registry, evidence)


def _build_variant_db(seed_name: str) -> str:
    """Create a variant H2 database from the verifier-owned SQL fixtures."""
    root = Path(tempfile.mkdtemp(prefix=f"verifier-{seed_name.split('.')[0]}-"))
    db_url = f"jdbc:h2:file:{root / 'experiments'}"
    run_h2_script(db_url, TESTS_DIR / "variant_schema.sql")
    run_h2_script(db_url, TESTS_DIR / seed_name)
    return db_url


@pytest.fixture(scope="session")
def variant_a_db_url() -> str:
    """Variant store where the shipped winner lost its calibration."""
    return _build_variant_db("variant_a_seed.sql")


@pytest.fixture(scope="session")
def variant_b_db_url() -> str:
    """Variant store where delta's current-version lineage was corrected."""
    return _build_variant_db("variant_b_seed.sql")
