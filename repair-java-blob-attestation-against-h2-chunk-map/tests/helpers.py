"""Shared helpers for the attestation verifier.

The expected report is recomputed from whichever store the auditor is pointed
at, not from the fixture generator's memory. Each object is attested against its
declared length and digest: among the stored copies (chunk map, blob) that read
back at the declared length, one matching the declared digest makes it intact, a
length match with no digest match is corrupt, and no length match is
unattestable. Only sha256 attests. Nothing here hardcodes a verdict, so the same
machinery grades the shipped store and every verifier-built variant and a
fixture-tuned auditor does not pass.
"""

from __future__ import annotations

import csv
import hashlib
import json
import os
import subprocess
import tempfile
from pathlib import Path

APP = Path(os.environ.get("ATTEST_APP", "/app"))
AGENT_CLASSES = APP / "attest-objects" / "classes"
AGENT_MAIN = "com.snorkel.attest.Main"
LIB = APP / "lib"
TESTS_DIR = Path(__file__).resolve().parent
REPO = TESTS_DIR.parent
SAMPLE_DB_URL = f"jdbc:h2:file:{APP}/store/objects"

ALGOS = {"sha256": hashlib.sha256, "sha1": hashlib.sha1, "md5": hashlib.md5}


def find_h2_jar() -> str:
    for base in (LIB, REPO / "environment" / "lib"):
        hits = sorted(base.glob("h2-*.jar"))
        if hits:
            return str(hits[0])
    raise FileNotFoundError("no h2 jar under /app/lib or environment/lib")


def _classpath(*extra: Path) -> str:
    return ":".join([*(str(p) for p in extra), f"{find_h2_jar()}"])


def run_h2_script(db_url: str, script_path: Path) -> None:
    result = subprocess.run(
        ["java", "-cp", find_h2_jar(), "org.h2.tools.RunScript",
         "-url", db_url, "-user", "sa", "-script", str(script_path)],
        capture_output=True, text=True, timeout=120,
    )
    assert result.returncode == 0, (
        f"RunScript failed for {script_path}:\n{result.stdout}\n{result.stderr}"
    )


def h2_select(sql: str, db_url: str) -> list[dict[str, str]]:
    read_url = db_url if "IFEXISTS" in db_url else f"{db_url};IFEXISTS=TRUE"
    safe_sql = sql.replace("'", "''")
    with tempfile.TemporaryDirectory() as tmp:
        out_csv = Path(tmp) / "out.csv"
        script = Path(tmp) / "q.sql"
        script.write_text(f"CALL CSVWRITE('{out_csv}', '{safe_sql}');\n", encoding="utf-8")
        result = subprocess.run(
            ["java", "-cp", find_h2_jar(), "org.h2.tools.RunScript",
             "-url", read_url, "-user", "sa", "-script", str(script)],
            capture_output=True, text=True, timeout=120,
        )
        assert result.returncode == 0, f"query failed for {sql!r}:\n{result.stderr}"
        with out_csv.open(newline="", encoding="utf-8") as handle:
            return [{k.lower(): v for k, v in row.items()} for row in csv.DictReader(handle)]


def store_root(db_url: str) -> Path:
    path = db_url.split("file:", 1)[1].split(";", 1)[0]
    return Path(path).parent


def schema_path() -> Path:
    for candidate in (Path("/app/store-db/schema.sql"),
                      REPO / "environment" / "store-db" / "schema.sql"):
        if candidate.is_file():
            return candidate
    raise FileNotFoundError("store schema not found under /app or environment")


def build_store(dest: Path, profile: str, seed: int) -> str:
    """Generate a variant store under dest and load it into a fresh H2 database."""
    import corpus

    corpus.build(dest, profile, seed)
    db_url = f"jdbc:h2:file:{dest}/objects"
    run_h2_script(db_url, schema_path())
    run_h2_script(db_url, dest / "seed.sql")
    return db_url


def _chunk_copy(root: Path, db_url: str, object_id: str) -> bytes | None:
    """The current chunk map, the latest generation's rows in ordinal order, or
    None when the object has no chunk rows or any of those files is missing."""
    rows = h2_select(
        "SELECT chunk_path FROM object_chunks "
        f"WHERE object_id = '{object_id}' AND generation = "
        f"(SELECT MAX(generation) FROM object_chunks WHERE object_id = '{object_id}') "
        "ORDER BY ordinal",
        db_url,
    )
    if not rows:
        return None
    parts = []
    for row in rows:
        path = root / row["chunk_path"]
        if not path.is_file():
            return None
        parts.append(path.read_bytes())
    return b"".join(parts)


def _blob_copy(root: Path, blob_path: str | None) -> bytes | None:
    if not blob_path:
        return None
    path = root / blob_path
    return path.read_bytes() if path.is_file() else None


def expected_report(db_url: str) -> dict:
    """Recompute the correct report by reading the store the CLI is pointed at.

    An object is attested against its declaration: among the copies that still
    read back at the declared length, one that matches the declared digest makes
    it intact; if a copy matches the length but none matches the digest it is
    corrupt; if no copy matches the length it is unattestable.
    """
    root = store_root(db_url)
    objects = h2_select(
        "SELECT object_id, declared_digest, digest_algo, blob_path, size_bytes FROM objects",
        db_url)
    cache = {
        row["object_id"]: row["status"]
        for row in h2_select("SELECT object_id, status FROM attestation_cache", db_url)
    }

    intact, corrupt, unattestable, conflicts = [], [], [], []
    for obj in sorted(objects, key=lambda o: o["object_id"]):
        oid = obj["object_id"]
        size = int(obj["size_bytes"])
        copies = [_chunk_copy(root, db_url, oid), _blob_copy(root, obj["blob_path"] or None)]
        declared_length = [c for c in copies if c is not None and len(c) == size]
        declared = obj["declared_digest"].lower()

        if not declared_length:
            status, reason = "unattestable", "missing_content"
        elif obj["digest_algo"].lower() != "sha256":
            status, reason = "unattestable", "unsupported_digest"
        elif any(hashlib.sha256(c).hexdigest() == declared for c in declared_length):
            status, reason = "intact", None
        else:
            status, reason = "corrupt", "digest_mismatch"

        if status == "intact":
            intact.append(oid)
        elif status == "corrupt":
            corrupt.append({"object_id": oid, "reason": reason})
        else:
            unattestable.append({"object_id": oid, "reason": reason})

        asserted = cache.get(oid)
        if asserted == "verified" and status != "intact":
            conflicts.append({"object_id": oid, "cache_status": asserted,
                              "actual_status": status})
        elif asserted == "failed" and status != "corrupt":
            conflicts.append({"object_id": oid, "cache_status": asserted,
                              "actual_status": status})
    return {"intact": intact, "corrupt": corrupt,
            "unattestable": unattestable, "conflicts": conflicts}


def run_agent(db_url: str, out_path: Path) -> dict:
    """Run the agent's compiled auditor and return the report it wrote."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    if out_path.exists():
        out_path.unlink()
    result = subprocess.run(
        ["java", "-cp", _classpath(AGENT_CLASSES, LIB / "*"), AGENT_MAIN,
         db_url, str(out_path)],
        capture_output=True, text=True, timeout=180,
    )
    assert result.returncode == 0, (
        f"auditor exited {result.returncode}:\n{result.stdout}\n{result.stderr}")
    assert out_path.is_file(), f"auditor wrote no report at {out_path}"
    return json.loads(out_path.read_text())


def normalise(report: dict) -> dict:
    """Order-independent comparison form."""
    def key(item):
        return item if isinstance(item, str) else json.dumps(item, sort_keys=True)
    return {
        "intact": sorted(report.get("intact", [])),
        "corrupt": sorted(report.get("corrupt", []), key=key),
        "unattestable": sorted(report.get("unattestable", []), key=key),
        "conflicts": sorted(report.get("conflicts", []), key=key),
    }
