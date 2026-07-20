"""Shared helpers for the release attestation verifier."""

from __future__ import annotations

import csv
import glob
import json
import subprocess
import tempfile
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path

APP = Path("/app")
MAIN_DB_URL = "jdbc:h2:file:/app/attestation-db/attestation"
API_BASE = "http://localhost:8080"
HEALTH_URL = f"{API_BASE}/health"
WORKER_CLASSES = APP / "attest-worker" / "classes"
MAIN_CLASS = "com.snorkel.attest.Main"
H2_JAR = APP / "lib" / "h2-2.2.224.jar"
TESTS_DIR = Path(__file__).resolve().parent

VERDICT_TRUSTED = "trusted"
VERDICT_DENIED = "denied"
VERDICT_QUARANTINE = "quarantine"

REASON_VERIFIED = "verified"
REASON_REVOKED = "revoked_signer"
REASON_UNKNOWN = "unknown_artifact"
REASON_BAD_SIG = "bad_signature"
REASON_DIGEST = "digest_mismatch"
REASON_VERIFY_DEGRADED = "verify_degraded"
REASON_REGISTRY_DEGRADED = "registry_degraded"
REASON_REGISTRY_ERROR = "registry_error"
REASON_VERIFY_ERROR = "verify_error"


@dataclass(frozen=True)
class ReportRow:
    artifact_id: str
    verdict: str
    reason_code: str


def find_h2_jar() -> str:
    """Locate the H2 driver jar."""
    if H2_JAR.is_file():
        return str(H2_JAR)
    matches = glob.glob("/root/.m2/repository/com/h2database/h2/*/h2-*.jar")
    jars = [m for m in matches if not m.endswith(("-sources.jar", "-javadoc.jar"))]
    assert jars, "H2 driver jar not found in the image"
    return sorted(jars)[-1]


def worker_classpath() -> str:
    """Classpath for the agent-built attestation worker."""
    assert WORKER_CLASSES.is_dir(), (
        f"attest-worker classes not found at {WORKER_CLASSES} — "
        "build /app/attest-worker with build.sh"
    )
    return f"{WORKER_CLASSES}:/app/lib/*"


def api_healthy(timeout_sec: float = 5.0) -> bool:
    """Return True when the artifact-metadata API answers /health."""
    deadline = time.time() + timeout_sec
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(HEALTH_URL, timeout=2) as resp:
                return resp.status == 200
        except (urllib.error.URLError, TimeoutError):
            time.sleep(0.25)
    return False


def ensure_api_ready() -> None:
    """Start or wait for the artifact-metadata API."""
    subprocess.run(["bash", "/app/start-api.sh"], check=True, timeout=360)
    assert api_healthy(timeout_sec=30), "artifact-metadata API /health is not answering"


def run_h2_script(db_url: str, script_path: Path) -> None:
    """Execute a SQL script against an H2 database."""
    result = subprocess.run(
        [
            "java",
            "-cp",
            find_h2_jar(),
            "org.h2.tools.RunScript",
            "-url",
            db_url,
            "-user",
            "sa",
            "-script",
            str(script_path),
        ],
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, (
        f"H2 RunScript failed for {script_path}:\n{result.stdout}\n{result.stderr}"
    )


def h2_select(sql: str, db_url: str = MAIN_DB_URL) -> list[dict[str, str]]:
    """Run a read-only SELECT and return rows as lower-cased dicts."""
    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as tmp:
        csv_path = Path(tmp.name)
    escaped = sql.replace("'", "''")
    write_sql = (
        f"CALL CSVWRITE('{csv_path.as_posix()}', "
        f"'{escaped}', 'charset=UTF-8');"
    )
    result = subprocess.run(
        [
            "java",
            "-cp",
            find_h2_jar(),
            "org.h2.tools.Shell",
            "-url",
            db_url,
            "-user",
            "sa",
            "-sql",
            write_sql,
        ],
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, f"H2 query failed:\n{result.stderr}\n{result.stdout}"
    if not csv_path.is_file() or csv_path.stat().st_size == 0:
        return []
    with csv_path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    csv_path.unlink(missing_ok=True)
    return [{k.lower(): v for k, v in row.items()} for row in rows]


def load_pending_artifact_ids(db_url: str = MAIN_DB_URL) -> list[str]:
    """Return pending artifact ids in enqueue order."""
    rows = h2_select(
        "SELECT artifact_id FROM pending_attestations ORDER BY enqueued_at",
        db_url,
    )
    return [row["artifact_id"] for row in rows]


def load_reports(db_url: str = MAIN_DB_URL) -> dict[str, ReportRow]:
    """Load attestation reports keyed by artifact id."""
    rows = h2_select(
        "SELECT artifact_id, verdict, reason_code FROM attestation_reports ORDER BY artifact_id",
        db_url,
    )
    out: dict[str, ReportRow] = {}
    for row in rows:
        out[row["artifact_id"]] = ReportRow(
            artifact_id=row["artifact_id"],
            verdict=row["verdict"],
            reason_code=row["reason_code"],
        )
    return out


def http_get_json(path: str) -> tuple[int, dict]:
    """GET a JSON API path and return status plus parsed body."""
    req = urllib.request.Request(f"{API_BASE}{path}", method="GET")
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8")
        parsed = json.loads(body) if body else {}
        return exc.code, parsed


def http_post_verify(artifact_id: str, digest: str, signature: str) -> int:
    """POST /verify and return the HTTP status code."""
    payload = json.dumps(
        {
            "artifact_id": artifact_id,
            "digest": digest,
            "detached_signature": signature,
        }
    ).encode("utf-8")
    req = urllib.request.Request(
        f"{API_BASE}/verify",
        data=payload,
        method="POST",
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status
    except urllib.error.HTTPError as exc:
        return exc.code


def load_evidence(db_url: str) -> dict[str, dict[str, str | bool]]:
    """Load artifact_evidence rows keyed by artifact id."""
    rows = h2_select(
        "SELECT artifact_id, sha256_digest, signer_key_id, revoked FROM artifact_evidence",
        db_url,
    )
    out: dict[str, dict[str, str | bool]] = {}
    for row in rows:
        out[row["artifact_id"]] = {
            "sha256_digest": row["sha256_digest"],
            "signer_key_id": row["signer_key_id"],
            "revoked": row["revoked"].lower() == "true",
        }
    return out


def expected_report(artifact_id: str, evidence: dict[str, str | bool]) -> ReportRow:
    """Derive the policy-correct report for one artifact using the live API."""
    if evidence.get("revoked"):
        return ReportRow(artifact_id, VERDICT_DENIED, REASON_REVOKED)

    status, body = http_get_json(f"/artifacts/{artifact_id}")
    if status == 404:
        return ReportRow(artifact_id, VERDICT_DENIED, REASON_UNKNOWN)
    if status == 503:
        return ReportRow(artifact_id, VERDICT_QUARANTINE, REASON_REGISTRY_DEGRADED)
    if status != 200:
        return ReportRow(artifact_id, VERDICT_QUARANTINE, REASON_REGISTRY_ERROR)

    digest = str(evidence["sha256_digest"])
    signature = str(body["detached_signature"])
    verify_status = http_post_verify(artifact_id, digest, signature)
    if verify_status == 200:
        return ReportRow(artifact_id, VERDICT_TRUSTED, REASON_VERIFIED)
    if verify_status == 400:
        return ReportRow(artifact_id, VERDICT_DENIED, REASON_BAD_SIG)
    if verify_status == 409:
        return ReportRow(artifact_id, VERDICT_DENIED, REASON_DIGEST)
    if verify_status == 503:
        return ReportRow(artifact_id, VERDICT_QUARANTINE, REASON_VERIFY_DEGRADED)
    if verify_status == 404:
        return ReportRow(artifact_id, VERDICT_DENIED, REASON_UNKNOWN)
    return ReportRow(artifact_id, VERDICT_QUARANTINE, REASON_VERIFY_ERROR)


def expected_reports_for_db(db_url: str) -> dict[str, ReportRow]:
    """Compute expected reports for every pending artifact in a database."""
    evidence = load_evidence(db_url)
    pending = load_pending_artifact_ids(db_url)
    return {
        artifact_id: expected_report(artifact_id, evidence[artifact_id])
        for artifact_id in pending
    }


def run_attest_worker(db_url: str) -> subprocess.CompletedProcess[str]:
    """Run the agent-built attestation worker against a JDBC URL."""
    ensure_api_ready()
    return subprocess.run(
        [
            "java",
            "-cp",
            worker_classpath(),
            MAIN_CLASS,
            db_url,
        ],
        capture_output=True,
        text=True,
        timeout=300,
    )


def clone_main_database() -> str:
    """Copy the shipped H2 store to a fresh file URL for variant runs."""
    src = APP / "attestation-db" / "attestation.mv.db"
    assert src.is_file(), f"missing shipped database at {src}"
    tmp_dir = Path(tempfile.mkdtemp(prefix="attest-variant-"))
    dest = tmp_dir / "attestation"
    subprocess.run(["cp", str(src), f"{dest}.mv.db"], check=True)
    return f"jdbc:h2:file:{dest}"
