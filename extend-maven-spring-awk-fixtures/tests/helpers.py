"""Verifier helpers for the Maven AWK dependency-audit task."""

from __future__ import annotations

import json
import subprocess
import time
from pathlib import Path

import requests

API = "http://127.0.0.1:8080"
PROJECT = Path("/app/dependency-audit")
EXPECTED = Path("/tests/expected_tree.json")


def run_maven_tests() -> subprocess.CompletedProcess[str]:
    """Run jqwik property tests and the full Maven lifecycle."""
    return subprocess.run(
        ["bash", str(PROJECT / "build.sh")],
        cwd=PROJECT,
        text=True,
        capture_output=True,
    )


def ensure_service() -> None:
    """Build (if needed) and start the Spring Boot dependency-audit service."""
    subprocess.run(["bash", str(PROJECT / "start.sh")], check=True)
    deadline = time.time() + 45.0
    while time.time() < deadline:
        try:
            resp = requests.get(f"{API}/health", timeout=2)
            if resp.json().get("status") == "ok":
                return
        except Exception:
            pass
        time.sleep(0.25)
    raise RuntimeError("dependency-audit service did not become ready")


def fetch_tree(build_id: str) -> dict:
    """GET /api/builds/{id}/dependency-tree."""
    resp = requests.get(f"{API}/api/builds/{build_id}/dependency-tree", timeout=5)
    resp.raise_for_status()
    return resp.json()


def normalize_tree(node: dict) -> dict:
    """Strip empty child lists for stable comparison."""
    children = [normalize_tree(child) for child in node.get("children", [])]
    return {
        "groupId": node["groupId"],
        "artifactId": node["artifactId"],
        "version": node["version"],
        "scope": node["scope"],
        "children": children,
    }


def load_expected_tree() -> dict:
    return normalize_tree(json.loads(EXPECTED.read_text(encoding="utf-8")))
