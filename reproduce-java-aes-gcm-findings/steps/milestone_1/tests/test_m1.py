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


def _normalize_rules(rules: dict) -> dict:
    """Normalize derived_nonce_rule punctuation and optional report preamble."""
    out = json.loads(json.dumps(rules))
    prose = out.get("derived_nonce_rule")
    if isinstance(prose, str):
        prefix = "The derived-nonce rule in prose: "
        if prose.startswith(prefix):
            prose = prose[len(prefix) :]
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
        """Report override, db override, then derived nonce."""
        prec = produced["nonce_selection_precedence"]
        assert prec.index("report_override") < prec.index("db_override")
        assert prec.index("db_override") < prec.index("derived_sha256_prefix")

    def test_nonce_precedence_includes_db_override(self, produced) -> None:
        """Nonce precedence must include the db_override tier from Appendix C."""
        assert "db_override" in produced["nonce_selection_precedence"]

    def test_frm003_nonce_override_present(self, produced) -> None:
        """frm-003 requires an explicit nonce override from Appendix D."""
        overrides = produced.get("nonce_overrides", {})
        assert "frm-003" in overrides, "frm-003 nonce override missing"
        assert len(overrides["frm-003"]) == 24

    def test_frm006_nonce_override_present(self, produced) -> None:
        """frm-006 requires the second Appendix D nonce override."""
        overrides = produced.get("nonce_overrides", {})
        assert "frm-006" in overrides, "frm-006 nonce override missing"
        assert len(overrides["frm-006"]) == 24

    def test_frm010_nonce_override_present(self, produced) -> None:
        """frm-010 requires the third Appendix D nonce override."""
        overrides = produced.get("nonce_overrides", {})
        assert "frm-010" in overrides, "frm-010 nonce override missing"
        assert len(overrides["frm-010"]) == 24

    def test_frm015_nonce_override_present(self, produced) -> None:
        """frm-015 requires an Appendix D nonce override."""
        overrides = produced.get("nonce_overrides", {})
        assert "frm-015" in overrides, "frm-015 nonce override missing"
        assert len(overrides["frm-015"]) == 24

    def test_frm022_nonce_override_present(self, produced) -> None:
        """Every operative Appendix D override must be transcribed, including frm-022."""
        overrides = produced.get("nonce_overrides", {})
        assert "frm-022" in overrides, "frm-022 nonce override missing"
        assert len(overrides["frm-022"]) == 24

    def test_all_report_overrides_transcribed(self, produced, expected) -> None:
        """nonce_overrides must include every frame named in normative Appendix D."""
        assert produced.get("nonce_overrides") == expected.get("nonce_overrides")

    def test_frm006_amended_override_not_superseded(self, produced) -> None:
        """frm-006 must use the amended Appendix D override, not the superseded line."""
        overrides = produced.get("nonce_overrides", {})
        assert overrides.get("frm-006") != "0102030405060708090A0B0C"

    def test_review_date_from_findings_overview(self, produced) -> None:
        """Review date must come from Findings overview, not superseded drafts."""
        assert produced["review_date"] == "2026-06-01"
        assert produced["review_date"] != "2026-07-15"

    def test_nonce_overrides_exclude_withdrawn_errata(self, produced) -> None:
        """Normative Appendix D overrides must not include withdrawn post-review errata."""
        overrides = produced.get("nonce_overrides", {})
        assert overrides.get("frm-003") != "DEADBEEFDEADBEEFDEADBEEF"
        assert overrides.get("frm-006") != "CAFEBABECAFEBABECAFEBABE"
        assert overrides.get("frm-010") != "FEEDFACEFEEDFACEFEEDFACE"
        assert overrides.get("frm-015") != "BADC0FFEBADC0FFEBADC0FFE"
        assert overrides.get("frm-022") != "DEADBEEF1234567890ABCDEF"

    def test_matches_expected_rules(self, produced, expected) -> None:
        """The full rules register must match ground truth."""
        assert _normalize_rules(produced) == _normalize_rules(expected), (
            f"rules differ: {produced} != {expected}"
        )
