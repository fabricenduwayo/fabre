"""Milestone 1 verifier — extracted rules at /app/out/rules.json."""

import json
import pathlib
import subprocess

import jsonschema
import pytest

HERE = pathlib.Path(__file__).resolve().parent
OUT = pathlib.Path("/app/out/rules.json")
SCHEMA = pathlib.Path("/app/schema/rules.schema.json")
EXPECTED = HERE / "expected_rules.json"
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


def _normalize_rules(rules: dict) -> dict:
    """Treat a trailing period on derived_nonce_rule as optional."""
    out = json.loads(json.dumps(rules))
    prose = out.get("derived_nonce_rule")
    if isinstance(prose, str):
        out["derived_nonce_rule"] = prose.rstrip(".")
    return out


@pytest.fixture(scope="module")
def produced():
    _run_stage("rules")
    assert OUT.exists(), f"{OUT} was not produced"
    return _load(OUT)


@pytest.fixture(scope="module")
def expected():
    return _load(EXPECTED)


class TestMilestone1Rules:
    """Milestone 1: extract cryptographic exception rules from the report."""

    def test_java_pipeline_entrypoint_exists(self) -> None:
        """Rules must be produced by the reusable Java CLI pipeline."""
        assert _class_dir() is not None, "missing compiled com.mariner.forensic.Main class under /app"

    def test_conforms_to_schema(self, produced) -> None:
        """rules.json must satisfy the published rules schema."""
        schema = _load(SCHEMA)
        jsonschema.Draft202012Validator(schema).validate(produced)

    def test_key_precedence_order(self, produced) -> None:
        """Rotation replacement must precede latest key assignment."""
        prec = produced["key_selection_precedence"]
        assert prec.index("rotation_replacement") < prec.index("latest_key_assigned")

    def test_nonce_precedence_order(self, produced) -> None:
        """Report override must precede derived nonce."""
        prec = produced["nonce_selection_precedence"]
        assert prec.index("report_override") < prec.index("derived_sha256_prefix")

    def test_frm003_nonce_override_present(self, produced) -> None:
        """frm-003 requires an explicit nonce override from Appendix D."""
        overrides = produced.get("nonce_overrides", {})
        assert "frm-003" in overrides, "frm-003 nonce override missing"
        assert len(overrides["frm-003"]) == 24

    def test_matches_expected_rules(self, produced, expected) -> None:
        """The full rules register must match ground truth."""
        assert _normalize_rules(produced) == _normalize_rules(expected), (
            f"rules differ: {produced} != {expected}"
        )
