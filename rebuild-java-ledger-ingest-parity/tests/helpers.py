"""Shared helpers for the ledger ingest verifier.

Expected output is produced by running the stashed legacy jar over the same corpus
the agent is given, so nothing here encodes the normalisation rules. Point it at a
corpus it has never seen and it still derives the right answer.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

APP = Path(os.environ.get("LEDGER_APP_ROOT", "/app"))
LIB = APP / "lib"
INGEST_CLASSES = APP / "ingest" / "classes"
SCHEMA = APP / "ledger-db" / "schema.sql"
SAMPLE_CORPUS = APP / "samples" / "corpus-40"

# test.sh moves the legacy jar here before pytest starts, so the agent's program
# cannot shell out to it at run time.
ORACLE_JAR = Path(os.environ.get("LEDGER_ORACLE_JAR", "/tests/ledger-oracle.jar"))

TOOLS = Path(__file__).resolve().parent / "gen_corpus.py"


@dataclass(frozen=True)
class Row:
    seq: int
    account: str
    counterparty: str
    amount: str
    memo: str
    source_file: str
    source_line: int


def h2_jar() -> str:
    matches = sorted(LIB.glob("h2-*.jar"))
    assert matches, f"no H2 jar under {LIB}"
    return str(matches[0])


def classpath(*extra: str) -> str:
    return ":".join([*extra, f"{LIB}/*"])


def run_h2_script(db_url: str, script: Path) -> None:
    result = subprocess.run(
        ["java", "-cp", h2_jar(), "org.h2.tools.RunScript",
         "-url", db_url, "-user", "sa", "-script", str(script)],
        capture_output=True, text=True, timeout=180,
    )
    assert result.returncode == 0, f"RunScript failed:\n{result.stdout}\n{result.stderr}"


def fresh_store(name: str) -> str:
    """A schema-only H2 store. Each caller gets its own, so tests do not collide."""
    target = Path("/tmp") / f"ledger-{name}"
    for stale in Path("/tmp").glob(f"ledger-{name}.*"):
        stale.unlink()
    db_url = f"jdbc:h2:file:{target}"
    run_h2_script(db_url, SCHEMA)
    return db_url


def read_rows(db_url: str) -> list[Row]:
    """RunScript prints columns space separated and the fields contain spaces, so
    concatenate with an explicit delimiter and split on that."""
    query = Path("/tmp/_ledger_query.sql")
    query.write_text(
        "SELECT seq || '~' || account || '~' || counterparty || '~' || amount "
        "|| '~' || memo || '~' || source_file || '~' || source_line "
        "FROM canonical_ledger ORDER BY seq, account;\n"
    )
    result = subprocess.run(
        ["java", "-cp", h2_jar(), "org.h2.tools.RunScript",
         "-url", db_url, "-user", "sa", "-script", str(query), "-showResults"],
        capture_output=True, text=True, timeout=180,
    )
    assert result.returncode == 0, f"query failed:\n{result.stdout}\n{result.stderr}"
    rows = []
    for line in result.stdout.splitlines():
        if not line.startswith("--> "):
            continue
        seq, account, party, amount, memo, src, line_no = line[4:].split("~")
        rows.append(Row(int(seq), account, party, amount, memo, src, int(line_no)))
    return rows


def make_corpus(dest: Path, profile: str, seed: int) -> Path:
    """Synthesise a corpus the agent has never seen."""
    dest.mkdir(parents=True, exist_ok=True)
    result = subprocess.run(
        [sys.executable, str(TOOLS), str(dest), "--profile", profile, "--seed", str(seed)],
        capture_output=True, text=True, timeout=120,
    )
    assert result.returncode == 0, f"corpus generation failed:\n{result.stderr}"
    return dest


def run_oracle(corpus: Path, name: str) -> tuple[list[Row], dict]:
    """Ground truth: the legacy jar's own output for this corpus."""
    assert ORACLE_JAR.is_file(), f"legacy jar not found at {ORACLE_JAR}"
    db_url = fresh_store(f"oracle-{name}")
    summary = Path(f"/tmp/ledger-oracle-{name}.json")
    result = subprocess.run(
        ["java", "-cp", classpath(str(ORACLE_JAR)), "com.snorkel.legacy.Main",
         str(corpus), db_url, str(summary)],
        capture_output=True, text=True, timeout=300,
    )
    assert result.returncode == 0, f"legacy jar failed:\n{result.stdout}\n{result.stderr}"
    return read_rows(db_url), json.loads(summary.read_text())


def run_agent(corpus: Path, name: str) -> tuple[list[Row], dict]:
    """The agent's own program, through the entry point the instruction names."""
    db_url = fresh_store(f"agent-{name}")
    summary = Path(f"/tmp/ledger-agent-{name}.json")
    result = subprocess.run(
        ["bash", str(APP / "ingest" / "run.sh"), str(corpus), db_url, str(summary)],
        capture_output=True, text=True, timeout=300,
    )
    assert result.returncode == 0, (
        f"ingester failed on {corpus.name}:\n{result.stdout}\n{result.stderr}"
    )
    assert summary.is_file(), f"no summary written for {corpus.name}"
    return read_rows(db_url), json.loads(summary.read_text())


def compare(corpus: Path, name: str) -> tuple[list[Row], list[Row], dict, dict]:
    """Run both over the same corpus and hand back all four artefacts."""
    want_rows, want_summary = run_oracle(corpus, name)
    got_rows, got_summary = run_agent(corpus, name)
    return got_rows, want_rows, got_summary, want_summary


def describe(rows: list[Row], limit: int = 6) -> str:
    return "\n".join(
        f"    {r.seq}|{r.account}|{r.counterparty}|{r.amount}|{r.memo}" for r in rows[:limit]
    )
