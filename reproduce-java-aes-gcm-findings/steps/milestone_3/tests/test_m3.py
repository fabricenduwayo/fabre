"""Milestone 3 verifier — decryption findings at /app/out/findings.json."""

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
CORRELATION = pathlib.Path("/app/out/correlation.json")
MAIN_CLASS_REL = pathlib.Path("com/mariner/forensic/Main.class")


def _class_dir() -> pathlib.Path | None:
    candidates = [pathlib.Path("/app/classes"), pathlib.Path("/app/pipeline/classes")]
    candidates.extend(sorted(pathlib.Path("/app").glob("*/classes")))
    for candidate in candidates:
        if (candidate / MAIN_CLASS_REL).exists():
            return candidate
    return None


def _run_stage(stage: str) -> None:
    class_dir = _class_dir()
    assert class_dir is not None, "missing compiled com.mariner.forensic.Main class under /app"
    subprocess.run(
        ["java", "-cp", f"{class_dir}:/app/lib/*", "com.mariner.forensic.Main", stage],
        cwd="/app",
        check=True,
        timeout=45,
    )


def _load(path: pathlib.Path):
    return json.loads(path.read_text())


@pytest.fixture(scope="module")
def produced():
    _run_stage("decrypt")
    assert OUT.exists(), f"{OUT} was not produced"
    return _load(OUT)


@pytest.fixture(scope="module")
def expected():
    return _load(EXPECTED)


class TestMilestone3Decrypt:
    """Milestone 3: verify AES-GCM authentication of GIF frame payloads."""

    def test_java_pipeline_entrypoint_exists(self) -> None:
        """Decryption must remain callable through the Java CLI."""
        assert _class_dir() is not None, "missing compiled com.mariner.forensic.Main class under /app"

    def test_milestone2_artifact_persists(self) -> None:
        """correlation.json from milestone 2 must still exist."""
        assert CORRELATION.exists(), "correlation.json from milestone 2 is missing"

    def test_output_is_a_list(self, produced) -> None:
        """findings.json must be a JSON array."""
        assert isinstance(produced, list), "findings.json must be a JSON array"

    def test_conforms_to_schema(self, produced) -> None:
        """Findings must validate against the published schema."""
        schema = _load(SCHEMA)
        jsonschema.Draft202012Validator(schema).validate(produced)

    def test_covers_every_frame(self, produced, expected) -> None:
        """Exactly one finding per in-scope frame."""
        got = [r["frame_id"] for r in produced]
        want = [r["frame_id"] for r in expected]
        assert sorted(got) == sorted(want), "frame set differs"
        assert len(got) == len(set(got)), "duplicate findings"

    def test_all_payloads_authenticate(self, produced) -> None:
        """Every in-scope GIF payload must pass GCM authentication."""
        for r in produced:
            assert r["auth_ok"] is True, f"{r['frame_id']} failed authentication"
            assert r["reason_code"] == "authenticated"

    def test_auth_totals_match(self, produced, expected) -> None:
        """Authenticated vs failed totals must match the signed report."""
        got = collections.Counter(r["reason_code"] for r in produced)
        want = collections.Counter(r["reason_code"] for r in expected)
        assert got == want, f"reason totals {dict(got)} != {dict(want)}"

    def test_matches_expected_findings(self, produced, expected) -> None:
        """Every frame's authentication result must match ground truth."""
        got = {r["frame_id"]: r for r in produced}
        exp = {r["frame_id"]: r for r in expected}
        mismatches = {fid: (exp[fid], got.get(fid)) for fid in exp if got.get(fid) != exp[fid]}
        assert not mismatches, f"findings differ: {mismatches}"
