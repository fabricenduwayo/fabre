"""Behavioral verifier for Maven AWK fixture generation and dependency-tree API."""

import pytest

from helpers import (
    ensure_service,
    fetch_tree,
    load_expected_tree,
    normalize_tree,
    run_maven_tests,
)


@pytest.fixture(scope="module", autouse=True)
def service_ready():
    """Ensure the Spring Boot service is running for API checks."""
    proc = run_maven_tests()
    assert proc.returncode == 0, proc.stderr + proc.stdout
    ensure_service()
    yield


def test_maven_tests_and_package_succeed():
    """mvn test package must pass, including jqwik property tests."""
    proc = run_maven_tests()
    assert proc.returncode == 0, proc.stderr + proc.stdout


def test_dependency_tree_matches_fixture():
    """GET /api/builds/bench-build/dependency-tree must return the nested fixture tree."""
    payload = fetch_tree("bench-build")
    assert normalize_tree(payload) == load_expected_tree()


def test_unknown_build_returns_404():
    """Missing build ids must not return a synthetic tree."""
    import requests

    resp = requests.get("http://127.0.0.1:8080/api/builds/missing-build/dependency-tree", timeout=5)
    assert resp.status_code == 404


def test_generated_seed_sql_exists_in_jar():
    """Package must ship generated seed SQL on the runtime classpath."""
    import zipfile

    with zipfile.ZipFile("/app/dependency-audit/app.jar") as jar:
        names = jar.namelist()
    assert "BOOT-INF/classes/data/seed-dependencies.sql" in names
    with zipfile.ZipFile("/app/dependency-audit/app.jar") as jar:
        sql = jar.read("BOOT-INF/classes/data/seed-dependencies.sql").decode("utf-8")
    assert "INSERT INTO dependency_nodes" in sql
    assert "spring-boot-starter-web" in sql
    assert "bench-build" in sql


def test_health_endpoint():
    """Service health must report ok."""
    import requests

    resp = requests.get("http://127.0.0.1:8080/health", timeout=5)
    assert resp.json() == {"status": "ok"}
