"""Milestone 2 verifier — audit correlation at /app/out/correlation.json."""

import json
import pathlib
import subprocess

import jsonschema
import pytest

HERE = pathlib.Path(__file__).resolve().parent
OUT = pathlib.Path("/app/out/correlation.json")
SCHEMA = pathlib.Path("/app/schema/correlation.schema.json")
EXPECTED = HERE / "expected_correlation.json"
RULES = pathlib.Path("/app/out/rules.json")
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
    _run_stage("correlate")
    assert OUT.exists(), f"{OUT} was not produced"
    return _load(OUT)


@pytest.fixture(scope="module")
def expected():
    return _load(EXPECTED)


class TestMilestone2Correlate:
    """Milestone 2: correlate SQLite audit events with extracted rules."""

    def test_java_pipeline_entrypoint_exists(self) -> None:
        """Correlation must remain callable through the Java CLI."""
        assert _class_dir() is not None, "missing compiled com.mariner.forensic.Main class under /app"

    def test_milestone1_artifact_persists(self) -> None:
        """rules.json from milestone 1 must still exist."""
        assert RULES.exists(), "rules.json from milestone 1 is missing"

    def test_output_is_a_list(self, produced) -> None:
        """correlation.json must be a JSON array."""
        assert isinstance(produced, list), "correlation.json must be a JSON array"

    def test_conforms_to_schema(self, produced) -> None:
        """Every row must satisfy the correlation schema."""
        schema = _load(SCHEMA)
        jsonschema.Draft202012Validator(schema).validate(produced)

    def test_covers_every_frame(self, produced, expected) -> None:
        """Exactly one row per in-scope frame."""
        got = [r["frame_id"] for r in produced]
        want = [r["frame_id"] for r in expected]
        assert sorted(got) == sorted(want), "frame set differs"
        assert len(got) == len(set(got)), "duplicate frame rows"

    def test_rotation_replacement_for_frm002(self, produced) -> None:
        """frm-002 must use rotation replacement key version 3, not v1 or v2."""
        got = {r["frame_id"]: r for r in produced}
        assert got["frm-002"]["key_version"] == 3
        assert got["frm-002"]["key_source"] == "rotation_replacement"

    def test_frm003_nonce_override(self, produced) -> None:
        """frm-003 must use the report override nonce, not a derived one."""
        got = {r["frame_id"]: r for r in produced}
        assert got["frm-003"]["nonce_source"] == "override"
        assert got["frm-003"]["nonce_hex"] == "A7C3E91B4D2F8065E1B9C0A3"

    def test_frm007_db_nonce_override(self, produced) -> None:
        """frm-007 nonce override is registered only in SQLite, not Appendix D."""
        got = {r["frame_id"]: r for r in produced}
        assert got["frm-007"]["nonce_source"] == "override"
        assert got["frm-007"]["nonce_hex"] == "B4E19A7305C2D8F61E0A4B9C"

    def test_frm008_latest_db_nonce_override(self, produced) -> None:
        """frm-008 has two DB nonce registrations; the latest recorded_at wins."""
        got = {r["frame_id"]: r for r in produced}
        assert got["frm-008"]["nonce_source"] == "override"
        assert got["frm-008"]["nonce_hex"] == "C1D2E3F4029384758690A1B2"

    def test_matches_expected_correlation(self, produced, expected) -> None:
        """Full correlation must match ground truth."""
        got = {r["frame_id"]: r for r in produced}
        exp = {r["frame_id"]: r for r in expected}
        mismatches = {fid: (exp[fid], got.get(fid)) for fid in exp if got.get(fid) != exp[fid]}
        assert not mismatches, f"correlation differs: {mismatches}"
