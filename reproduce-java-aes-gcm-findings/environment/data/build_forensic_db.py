#!/usr/bin/env python3
"""Build the vendored forensic_audit.db from seed.sql at image build time."""
from __future__ import annotations

import sqlite3
from pathlib import Path

DB_PATH = Path("/app/data/forensic_audit.db")
SEED_SQL = Path("/app/data/seed.sql")


def main() -> None:
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.executescript(SEED_SQL.read_text())
        conn.commit()
    finally:
        conn.close()


if __name__ == "__main__":
    main()
