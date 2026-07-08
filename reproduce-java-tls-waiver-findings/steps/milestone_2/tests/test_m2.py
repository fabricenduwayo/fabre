"""Milestone 2 verifier — the joined probe evidence at /app/out/evidence.json.

Run alone with: pytest tests/test_m2.py
"""

import json
import pathlib
import subprocess

import jsonschema
import pytest

HERE = pathlib.Path(__file__).resolve().parent
OUT = pathlib.Path("/app/out/evidence.json")
SCHEMA = pathlib.Path("/app/schema/evidence.schema.json")
EXPECTED = HERE / "expected_evidence.json"
WAIVERS = pathlib.Path("/app/out/waivers.json")
MAIN_CLASS_REL = pathlib.Path("com/mariner/audit/Main.class")


def _class_dir() -> pathlib.Path | None:
    candidates = [pathlib.Path("/app/classes"), pathlib.Path("/app/pipeline/classes")]
    candidates.extend(sorted(pathlib.Path("/app").glob("*/classes")))
    existing = [candidate for candidate in candidates if (candidate / MAIN_CLASS_REL).exists()]
    if not existing:
        return None
    return max(existing, key=lambda path: (path / MAIN_CLASS_REL).stat().st_mtime)


def _run_stage(stage: str) -> None:
    class_dir = _class_dir()
    assert class_dir is not None, "missing compiled com.mariner.audit.Main class under /app"
    subprocess.run(
        ["java", "-cp", f"{class_dir}:/app/lib/*", "com.mariner.audit.Main", stage],
        cwd="/app",
        check=True,
        timeout=45,
    )


def _load(path: pathlib.Path):
    return json.loads(pathlib.Path(path).read_text())


@pytest.fixture(scope="module")
def produced():
    _run_stage("join")
    assert OUT.exists(), f"{OUT} was not produced"
    return _load(OUT)


@pytest.fixture(scope="module")
def expected():
    return _load(EXPECTED)


class TestMilestone2Join:
    """Milestone 2: join the H2 probe evidence with the decoded register."""

    def test_java_pipeline_entrypoint_exists(self) -> None:
        """The H2 evidence join must remain callable through the Java CLI."""
        assert _class_dir() is not None, "missing compiled com.mariner.audit.Main class under /app"

    def test_milestone1_artifact_persists(self) -> None:
        """The milestone 1 register must still exist (state persists)."""
        assert WAIVERS.exists(), "waivers.json from milestone 1 is missing"

    def test_output_is_a_list(self, produced) -> None:
        """evidence.json must be a JSON array of per-service evidence records."""
        assert isinstance(produced, list), "evidence.json must be a JSON array"

    def test_conforms_to_schema(self, produced) -> None:
        """Every record must satisfy the published evidence schema."""
        schema = _load(SCHEMA)
        jsonschema.Draft202012Validator(schema).validate(produced)

    def test_covers_every_service(self, produced, expected) -> None:
        """Exactly one joined record per in-scope service."""
        got = [r["service_id"] for r in produced]
        want = [r["service_id"] for r in expected]
        assert sorted(got) == sorted(want), "service set differs from inventory"
        assert len(got) == len(set(got)), "duplicate service rows present"

    def test_uses_latest_probe_only(self, produced) -> None:
        """Evidence must come from the most recent probe, never a stale one.

        Stale captures are the only rows carrying TLS1.1 or HTTP 526; their
        presence means an earlier probe was selected instead of the latest.
        """
        for r in produced:
            assert r["probe_tls_version"] != "TLS1.1", (
                f"{r['service_id']} used a stale probe (TLS1.1)"
            )
            assert r["probe_http_status"] != 526, (
                f"{r['service_id']} used a stale probe (HTTP 526)"
            )

    def test_matches_expected_evidence(self, produced, expected) -> None:
        """The full joined evidence must match the ground truth."""
        got = {r["service_id"]: r for r in produced}
        exp = {r["service_id"]: r for r in expected}
        mismatches = {sid: (exp[sid], got.get(sid)) for sid in exp if got.get(sid) != exp[sid]}
        assert not mismatches, f"evidence records differ from expected: {mismatches}"
