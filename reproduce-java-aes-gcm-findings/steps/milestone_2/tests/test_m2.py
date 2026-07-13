"""Milestone 2 verifier — audit correlation at /app/out/correlation.json."""

import contextlib
import json
import pathlib
import sqlite3
import subprocess

import jsonschema
import pytest

HERE = pathlib.Path(__file__).resolve().parent
OUT = pathlib.Path("/app/out/correlation.json")
SCHEMA = pathlib.Path("/app/schema/correlation.schema.json")
EXPECTED = HERE / "expected_correlation.json"
RULES = pathlib.Path("/app/out/rules.json")
DATABASE = pathlib.Path("/app/data/forensic_audit.db")
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
def _temporary_key_assignments(rows: list[tuple[int, str, str]]):
    """Install verifier-only frm-001 assignments and restore DB/output afterward."""
    original = DATABASE.read_bytes()
    event_ids: list[int] = []
    try:
        with sqlite3.connect(DATABASE) as connection:
            for key_version, recorded_at, effective_at in rows:
                cursor = connection.execute(
                    """
                    INSERT INTO audit_events (
                        frame_id, event_type, key_version, replacement_key_version,
                        nonce_override_hex, supersedes_nonce_hex, recorded_at, effective_at
                    ) VALUES ('frm-001', 'key_assigned', ?, NULL, NULL, NULL, ?, ?)
                    """,
                    (key_version, recorded_at, effective_at),
                )
                event_ids.append(cursor.lastrowid)
        _run_stage("correlate")
        yield event_ids, _load(OUT)
    finally:
        DATABASE.write_bytes(original)
        _run_stage("correlate")


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
        """frm-008 has revoked and superseded DB registrations; latest active wins."""
        got = {r["frame_id"]: r for r in produced}
        assert got["frm-008"]["nonce_source"] == "override"
        assert got["frm-008"]["nonce_hex"] == "C1D2E3F4029384758690A1B2"
        assert got["frm-008"]["nonce_hex"] != "AABBCCDDEEFF001122334455"

    def test_frm008_revoked_registration_not_operative(self, produced) -> None:
        """frm-008 must ignore a later nonce registration voided by revocation."""
        got = {r["frame_id"]: r for r in produced}
        assert got["frm-008"]["nonce_hex"] != "AABBCCDDEEFF001122334455"

    def test_frm009_rotation_not_stale_assign(self, produced) -> None:
        """frm-009 must use rotation replacement v5, not the later stale v3 assign."""
        got = {r["frame_id"]: r for r in produced}
        assert got["frm-009"]["key_version"] == 5
        assert got["frm-009"]["key_source"] == "rotation_replacement"

    def test_frm009_rescinded_rotation_not_operative(self, produced) -> None:
        """frm-009 has a later v2->v4 rotation rescinded; v5 from v2->v5 must win."""
        got = {r["frame_id"]: r for r in produced}
        assert got["frm-009"]["key_version"] == 5
        assert got["frm-009"]["key_version"] != 4

    def test_frm010_report_beats_db_nonce(self, produced) -> None:
        """frm-010 must use the Appendix D override, not the later DB registration."""
        got = {r["frame_id"]: r for r in produced}
        assert got["frm-010"]["nonce_source"] == "override"
        assert got["frm-010"]["nonce_hex"] == "0A1B2C3D4E5F60718293A4B5"
        assert got["frm-010"]["nonce_hex"] != "FEEDFACECAFE000000000001"

    def test_frm011_latest_rotation_not_max_or_stale(self, produced) -> None:
        """frm-011 has three rotations; operative key is v4, not max v6 or stale assign."""
        got = {r["frame_id"]: r for r in produced}
        assert got["frm-011"]["key_version"] == 4
        assert got["frm-011"]["key_source"] == "rotation_replacement"
        assert got["frm-011"]["nonce_source"] == "derived"

    def test_frm011_key_resolution_by_effective_at(self, produced) -> None:
        """frm-011 must pick the rotation with greatest effective_at, not latest recorded_at."""
        got = {r["frame_id"]: r for r in produced}
        assert got["frm-011"]["key_version"] == 4
        assert got["frm-011"]["key_version"] != 6

    def test_frm012_rotation_voids_stale_db_nonce(self, produced) -> None:
        """frm-012 registered a DB nonce for v2 then rotated to v4; derived nonce wins."""
        got = {r["frame_id"]: r for r in produced}
        assert got["frm-012"]["key_version"] == 4
        assert got["frm-012"]["key_source"] == "rotation_replacement"
        assert got["frm-012"]["nonce_source"] == "derived"
        assert got["frm-012"]["nonce_hex"] != "D0E1F2A3B4C5D6E7F8091A2B"

    def test_frm013_revocation_then_rotation(self, produced) -> None:
        """frm-013 revokes a DB override then rotates; derived nonce for v4 wins."""
        got = {r["frame_id"]: r for r in produced}
        assert got["frm-013"]["key_version"] == 4
        assert got["frm-013"]["key_source"] == "rotation_replacement"
        assert got["frm-013"]["nonce_source"] == "derived"
        assert got["frm-013"]["nonce_hex"] != "112233445566778899AABBCC"
        assert got["frm-013"]["nonce_hex"] != "FFEEDDCCBBAA998877665544"

    def test_frm014_post_rotation_db_re_registration(self, produced) -> None:
        """frm-014 must use the v4 DB override, not stale v2 registrations."""
        got = {r["frame_id"]: r for r in produced}
        assert got["frm-014"]["key_version"] == 4
        assert got["frm-014"]["key_source"] == "rotation_replacement"
        assert got["frm-014"]["nonce_source"] == "override"
        assert got["frm-014"]["nonce_hex"] == "ABCDEF0123456789ABCDEF01"
        assert got["frm-014"]["nonce_hex"] != "998877665544332211009988"

    def test_frm015_report_override_survives_rotation(self, produced) -> None:
        """frm-015 must keep the Appendix D override after rotation to v4."""
        got = {r["frame_id"]: r for r in produced}
        assert got["frm-015"]["key_version"] == 4
        assert got["frm-015"]["key_source"] == "rotation_replacement"
        assert got["frm-015"]["nonce_source"] == "override"
        assert got["frm-015"]["nonce_hex"] == "13579BDF2468ACE024681ACE"

    def test_frm016_nonce_amendment_result(self, produced) -> None:
        """frm-016 must use the amendment result, not the pre-amend registration."""
        got = {r["frame_id"]: r for r in produced}
        assert got["frm-016"]["nonce_source"] == "override"
        assert got["frm-016"]["nonce_hex"] == "33445566778899AABBCCDDEE"
        assert got["frm-016"]["nonce_hex"] != "112233445566778899AABBCC"

    def test_frm017_amendment_then_reregistration(self, produced) -> None:
        """frm-017 must honor post-amendment re-registration for the operative key."""
        got = {r["frame_id"]: r for r in produced}
        assert got["frm-017"]["key_version"] == 4
        assert got["frm-017"]["key_source"] == "rotation_replacement"
        assert got["frm-017"]["nonce_source"] == "override"
        assert got["frm-017"]["nonce_hex"] == "66778899AABBCCDDEEFF0011"
        assert got["frm-017"]["nonce_hex"] != "778899AABBCCDDEEFF001122"

    def test_frm017_stale_v2_registration_not_operative(self, produced) -> None:
        """frm-017 must ignore a later v2 DB registration once rotation makes v4 operative."""
        got = {r["frame_id"]: r for r in produced}
        assert got["frm-017"]["nonce_hex"] != "5566778899AABBCCDDEEFF00"

    def test_frm018_rescinded_assignment_not_operative(self, produced) -> None:
        """frm-018 must ignore a later key_assigned row voided by key_assignment_rescinded."""
        got = {r["frame_id"]: r for r in produced}
        assert got["frm-018"]["key_version"] == 2
        assert got["frm-018"]["key_source"] == "latest_assigned"
        assert got["frm-018"]["key_version"] != 6

    def test_frm019_chained_rotation_rescission_fallback(self, produced) -> None:
        """frm-019 must fall back to v3 when the v3->v5 rotation hop is rescinded."""
        got = {r["frame_id"]: r for r in produced}
        assert got["frm-019"]["key_version"] == 3
        assert got["frm-019"]["key_source"] == "rotation_replacement"
        assert got["frm-019"]["key_version"] != 5

    def test_frm020_double_amendment_result(self, produced) -> None:
        """frm-020 must use the final amendment result, not intermediate registrations."""
        got = {r["frame_id"]: r for r in produced}
        assert got["frm-020"]["nonce_source"] == "override"
        assert got["frm-020"]["nonce_hex"] == "D4E5F60718293A4B5C6D7E8F"
        assert got["frm-020"]["nonce_hex"] != "C3D4E5F60718293A4B5C6D7E"
        assert got["frm-020"]["nonce_hex"] != "B2C3D4E5F60718293A4B5C6D"

    def test_frm020_effective_at_not_recorded_at(self, produced) -> None:
        """frm-020 amendment chain must follow effective_at, not ingestion recorded_at."""
        got = {r["frame_id"]: r for r in produced}
        assert got["frm-020"]["nonce_hex"] != "C3D4E5F60718293A4B5C6D7E"

    def test_frm021_all_rotations_rescinded_assignment_fallback(self, produced) -> None:
        """frm-021 must fall back to v2 when every key_rotated row is voided."""
        got = {r["frame_id"]: r for r in produced}
        assert got["frm-021"]["key_version"] == 2
        assert got["frm-021"]["key_source"] == "latest_assigned"
        assert got["frm-021"]["key_version"] != 5
        assert got["frm-021"]["key_version"] != 6

    def test_frm022_report_override_survives_rotation(self, produced) -> None:
        """frm-022 must keep the Appendix D override after rotation, not the DB row."""
        got = {r["frame_id"]: r for r in produced}
        assert got["frm-022"]["key_version"] == 4
        assert got["frm-022"]["key_source"] == "rotation_replacement"
        assert got["frm-022"]["nonce_source"] == "override"
        assert got["frm-022"]["nonce_hex"] == "E1F2A3B4C5D67890ABCDEF01"
        assert got["frm-022"]["nonce_hex"] != "FACEFACEFACEFACEFACEFACE"

    def test_frm023_replacement_rescission_chain(self, produced) -> None:
        """frm-023 must survive replacement, rescission, and a second replacement."""
        got = {r["frame_id"]: r for r in produced}
        assert got["frm-023"]["key_version"] == 2
        assert got["frm-023"]["nonce_source"] == "override"
        assert got["frm-023"]["nonce_hex"] == "3C4D5E6F708192A3B4C5D6E7"
        assert got["frm-023"]["nonce_hex"] != "2B3C4D5E6F708192A3B4C5D6"
        assert got["frm-023"]["nonce_hex"] != "1A2B3C4D5E6F708192A3B4C5"

    def test_frm023_effective_at_not_recorded_at(self, produced) -> None:
        """frm-023 replacement chain must follow effective_at, not scrambled recorded_at."""
        got = {r["frame_id"]: r for r in produced}
        assert got["frm-023"]["nonce_hex"] != "1A2B3C4D5E6F708192A3B4C5"

    def test_frm024_rotation_voids_replacement_scoped_nonce(self, produced) -> None:
        """frm-024 must use the v5 override after rotation, not the v4 replacement."""
        got = {r["frame_id"]: r for r in produced}
        assert got["frm-024"]["key_version"] == 5
        assert got["frm-024"]["key_source"] == "rotation_replacement"
        assert got["frm-024"]["nonce_source"] == "override"
        assert got["frm-024"]["nonce_hex"] == "708192A3B4C5D6E7F8091A2B"
        assert got["frm-024"]["nonce_hex"] != "6F708192A3B4C5D6E7F8091A"

    def test_recorded_at_breaks_effective_at_assignment_tie(self) -> None:
        """Later recorded_at must win an effective_at tie and identify its event."""
        rows = [
            (4, "2026-06-10 12:00:00", "2026-06-10 10:00:00"),
            (3, "2026-06-10 11:00:00", "2026-06-10 10:00:00"),
        ]
        with _temporary_key_assignments(rows) as (event_ids, tied_output):
            frame = {row["frame_id"]: row for row in tied_output}["frm-001"]
            assert frame["key_version"] == 4
            assert frame["key_source"] == "latest_assigned"
            assert frame["key_event_ids"] == [event_ids[0]]

    def test_event_id_breaks_full_timestamp_assignment_tie(self) -> None:
        """Greater event_id must win when effective_at and recorded_at both tie."""
        timestamp = "2026-06-11 10:00:00"
        rows = [(3, timestamp, timestamp), (4, timestamp, timestamp)]
        with _temporary_key_assignments(rows) as (event_ids, tied_output):
            frame = {row["frame_id"]: row for row in tied_output}["frm-001"]
            assert frame["key_version"] == 4
            assert frame["key_source"] == "latest_assigned"
            assert frame["key_event_ids"] == [event_ids[1]]

    def test_operative_event_provenance_chains(self, produced, expected) -> None:
        """Correlation must preserve connected key and nonce lifecycle event IDs."""
        got = {r["frame_id"]: r for r in produced}
        exp = {r["frame_id"]: r for r in expected}
        for frame_id in ("frm-019", "frm-020", "frm-023", "frm-024"):
            assert got[frame_id]["key_event_ids"] == exp[frame_id]["key_event_ids"]
            assert got[frame_id]["nonce_event_ids"] == exp[frame_id]["nonce_event_ids"]
        assert len(got["frm-023"]["nonce_event_ids"]) == 3
        assert len(got["frm-024"]["key_event_ids"]) == 3

    def test_matches_expected_correlation(self, produced, expected) -> None:
        """Full correlation must match ground truth."""
        got = {r["frame_id"]: r for r in produced}
        exp = {r["frame_id"]: r for r in expected}
        mismatches = {fid: (exp[fid], got.get(fid)) for fid in exp if got.get(fid) != exp[fid]}
        assert not mismatches, f"correlation differs: {mismatches}"
