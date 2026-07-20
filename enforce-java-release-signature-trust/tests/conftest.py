"""Pytest fixtures for the attestation verifier."""

from __future__ import annotations

import pytest

from helpers import ensure_api_ready


@pytest.fixture(scope="session", autouse=True)
def _api_ready() -> None:
    """Ensure the artifact-metadata API is running before tests."""
    ensure_api_ready()
