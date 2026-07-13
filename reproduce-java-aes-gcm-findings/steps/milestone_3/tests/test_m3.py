"""Milestone 3 verifier — decryption findings at /app/out/findings.json."""

import collections
import contextlib
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
    """Pick the newest compiled Main.class when multiple output trees exist."""
    found: list[tuple[float, pathlib.Path]] = []
    candidates = [pathlib.Path("/app/classes"), pathlib.Path("/app/pipeline/classes")]
    candidates.extend(sorted(pathlib.Path("/app").glob("*/classes")))
    for candidate in candidates:
        main_class = candidate / MAIN_CLASS_REL
        if main_class.exists():
            found.append((main_class.stat().st_mtime, candidate))
    if not found:
        return None
    found.sort(key=lambda item: item[0], reverse=True)
    return found[0][1]


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


@contextlib.contextmanager
def _temporary_wrong_nonce(frame_id: str):
    """Change one correlated nonce and restore correlation/findings afterward."""
    original = CORRELATION.read_text()
    try:
        correlation = json.loads(original)
        target = next(row for row in correlation if row["frame_id"] == frame_id)
        first = target["nonce_hex"][0]
        target["nonce_hex"] = ("0" if first != "0" else "1") + target["nonce_hex"][1:]
        CORRELATION.write_text(json.dumps(correlation, indent=2) + "\n")
        _run_stage("decrypt")
        yield _load(OUT)
    finally:
        CORRELATION.write_text(original)
        _run_stage("decrypt")


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

    def test_superseded_crypto_block_not_used(self, produced, expected) -> None:
        """Operative MRNR/CRYPTO1 block must win over an earlier stale block for the frame."""
        got = {r["frame_id"]: r for r in produced}
        exp = {r["frame_id"]: r for r in expected}
        assert got["frm-001"]["plaintext_sha256"] == exp["frm-001"]["plaintext_sha256"]
        assert got["frm-011"]["plaintext_sha256"] == exp["frm-011"]["plaintext_sha256"]

    def test_auth_totals_match(self, produced, expected) -> None:
        """Authenticated vs failed totals must match the signed report."""
        got = collections.Counter(r["reason_code"] for r in produced)
        want = collections.Counter(r["reason_code"] for r in expected)
        assert got == want, f"reason totals {dict(got)} != {dict(want)}"

    def test_tag_failure_has_null_hash_and_failure_reason(self) -> None:
        """A verifier-induced wrong nonce must produce the defined tag-failure record."""
        with _temporary_wrong_nonce("frm-001") as failed_output:
            finding = {row["frame_id"]: row for row in failed_output}["frm-001"]
            assert finding["auth_ok"] is False
            assert finding["reason_code"] == "auth_failed"
            assert finding["plaintext_sha256"] is None
            schema = _load(SCHEMA)
            jsonschema.Draft202012Validator(schema).validate(failed_output)

    def test_matches_expected_findings(self, produced, expected) -> None:
        """Every frame's authentication result must match ground truth."""
        got = {r["frame_id"]: r for r in produced}
        exp = {r["frame_id"]: r for r in expected}
        mismatches = {fid: (exp[fid], got.get(fid)) for fid in exp if got.get(fid) != exp[fid]}
        assert not mismatches, f"findings differ: {mismatches}"
