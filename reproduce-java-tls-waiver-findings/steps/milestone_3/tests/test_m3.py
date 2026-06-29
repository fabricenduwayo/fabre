"""Milestone 3 verifier — the final findings at /app/out/findings.json.

Run alone with: pytest tests/test_m3.py
"""

import collections
import json
import pathlib
import subprocess

import jsonschema
import pytest

HERE = pathlib.Path(__file__).resolve().parent
OUT = pathlib.Path("/app/out/findings.json")
SCHEMA = pathlib.Path("/app/schema/findings.schema.json")
EXPECTED = HERE / "expected_findings.json"
EVIDENCE = pathlib.Path("/app/out/evidence.json")
MAIN_CLASS_REL = pathlib.Path("com/mariner/audit/Main.class")


def _class_dir() -> pathlib.Path | None:
    candidates = [pathlib.Path("/app/classes"), pathlib.Path("/app/pipeline/classes")]
    candidates.extend(sorted(pathlib.Path("/app").glob("*/classes")))
    for candidate in candidates:
        if (candidate / MAIN_CLASS_REL).exists():
            return candidate
    return None


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
    _run_stage("validate")
    assert OUT.exists(), f"{OUT} was not produced"
    return _load(OUT)


@pytest.fixture(scope="module")
def expected():
    return _load(EXPECTED)


class TestMilestone3Findings:
    """Milestone 3: reconcile config + evidence into schema-valid findings."""

    def test_java_pipeline_entrypoint_exists(self) -> None:
        """The final findings stage must remain callable through the Java CLI."""
        assert _class_dir() is not None, "missing compiled com.mariner.audit.Main class under /app"

    def test_milestone2_artifact_persists(self) -> None:
        """The milestone 2 evidence must still exist (state persists)."""
        assert EVIDENCE.exists(), "evidence.json from milestone 2 is missing"

    def test_output_is_a_list(self, produced) -> None:
        """findings.json must be a JSON array of per-service findings."""
        assert isinstance(produced, list), "findings.json must be a JSON array"

    def test_is_schema_valid(self, produced) -> None:
        """Findings must validate against the published findings schema."""
        schema = _load(SCHEMA)
        jsonschema.Draft202012Validator(schema).validate(produced)

    def test_covers_every_service(self, produced, expected) -> None:
        """Exactly one finding per in-scope service."""
        got = [r["service_id"] for r in produced]
        want = [r["service_id"] for r in expected]
        assert sorted(got) == sorted(want), "service set differs from inventory"
        assert len(got) == len(set(got)), "duplicate findings present"

    def test_disposition_totals_match(self, produced, expected) -> None:
        """The allow/deny/rotate totals must match the review's totals."""
        got = collections.Counter(r["disposition"] for r in produced)
        want = collections.Counter(r["disposition"] for r in expected)
        assert got == want, f"disposition totals {dict(got)} != {dict(want)}"

    def test_reason_code_distribution_matches(self, produced, expected) -> None:
        """The reason-code distribution must match the ground truth."""
        got = collections.Counter(r["reason_code"] for r in produced)
        want = collections.Counter(r["reason_code"] for r in expected)
        assert got == want, f"reason-code distribution {dict(got)} != {dict(want)}"

    def test_matches_expected_findings(self, produced, expected) -> None:
        """Every service's disposition, reason, and waiver flag must match."""
        got = {r["service_id"]: r for r in produced}
        exp = {r["service_id"]: r for r in expected}
        mismatches = {sid: (exp[sid], got.get(sid)) for sid in exp if got.get(sid) != exp[sid]}
        assert not mismatches, f"findings differ from expected: {mismatches}"
