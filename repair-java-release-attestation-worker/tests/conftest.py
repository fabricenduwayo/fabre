"""Pytest fixtures for the attestation verifier."""

from __future__ import annotations

import pytest

from helpers import (
    MAIN_DB_URL,
    ensure_api_ready,
    expected_reports_for_db,
    load_pending_artifact_ids,
    load_reports,
)


@pytest.fixture(scope="session", autouse=True)
def _api_ready() -> None:
    """Ensure the artifact-metadata API is running before tests."""
    ensure_api_ready()


@pytest.fixture(scope="session")
def pending_ids() -> list[str]:
    """Pending artifact ids from the shipped attestation store."""
    return load_pending_artifact_ids(MAIN_DB_URL)


@pytest.fixture(scope="session")
def shipped_reports() -> dict:
    """Reports written by the agent worker on the shipped store."""
    reports = load_reports(MAIN_DB_URL)
    assert reports, "attestation_reports is empty — run the worker first"
    return reports


@pytest.fixture(scope="session")
def expected_shipped() -> dict:
    """Policy-correct reports for the shipped store."""
    return expected_reports_for_db(MAIN_DB_URL)
