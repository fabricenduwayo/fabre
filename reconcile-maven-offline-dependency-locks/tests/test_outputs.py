"""Behavioral verifier for the offline Maven dependency reconciliation.

Every check drives the real build: pytest runs Maven offline against the local
repository, parses what the build actually resolved, and executes the built CLI
against the bound jars. Nothing asserts on pinned version literals; the policy
constraints (floors, compatibility matrix, single wire version) force the
binding, so a wrong reconciliation fails a named policy test rather than a
string comparison.
"""

import hashlib
import re
import subprocess
from pathlib import Path

PROJECT = Path("/app/project")
MODULES = ["meter-core", "meter-adapter", "meter-cli"]
FLOORS = {"wire-format": (2, 2, 0), "telemetry-client": (1, 3, 0)}
WIRE_COMPAT = {
    ("telemetry-client", (1, 2)): 2,
    ("telemetry-client", (1, 4)): 2,
    ("format-legacy", (0, 9)): 2,
    ("format-legacy", (1, 1)): 3,
}
DEP_LINE = re.compile(r"io\.meterhub:([a-z-]+):jar:([0-9.]+):(?:compile|runtime)")


def mvn(*goals: str, cwd: Path = PROJECT) -> subprocess.CompletedProcess:
    """Run Maven offline in batch mode and capture output."""
    return subprocess.run(
        ["mvn", "-B", "-o", *goals],
        cwd=cwd,
        capture_output=True,
        text=True,
        timeout=300,
    )


def parse_version(text: str) -> tuple[int, ...]:
    """Split a dotted version string into comparable integers."""
    return tuple(int(part) for part in text.split("."))


_RESOLVED: set[tuple[str, str]] = set()


def resolved_dependencies() -> set[tuple[str, str]]:
    """Return the (artifact, version) pairs the build actually resolves.

    Installs first so the reactor's own jars are resolvable offline when the
    cli module's dependencies are listed, and caches the parse because the
    binding cannot change while the verifier runs.
    """
    if _RESOLVED:
        return _RESOLVED
    result = mvn("install", "dependency:list")
    assert result.returncode == 0, (
        f"dependency:list failed offline:\n{result.stdout[-3000:]}"
    )
    _RESOLVED.update(DEP_LINE.findall(result.stdout))
    return _RESOLVED


def module_jars() -> dict[str, bytes]:
    """Map each module jar name to its digest bytes."""
    digests = {}
    for module in MODULES:
        jars = sorted((PROJECT / module / "target").glob("*.jar"))
        assert jars, f"{module} produced no jar"
        digests[module] = hashlib.sha256(jars[0].read_bytes()).digest()
    return digests


def test_offline_build_succeeds():
    """The reconciled build compiles and packages fully offline."""
    result = mvn("clean", "package")
    assert result.returncode == 0, (
        f"offline build failed:\n{result.stdout[-4000:]}"
    )


def test_rebuild_is_byte_identical():
    """Two consecutive clean builds produce byte-identical module jars."""
    assert mvn("clean", "package").returncode == 0
    first = module_jars()
    assert mvn("clean", "package").returncode == 0
    second = module_jars()
    assert first == second, (
        "rebuilding changed jar bytes; the build embeds wall-clock output"
    )


def test_resolved_versions_meet_security_floors():
    """No resolved io.meterhub artifact sits below its policy floor."""
    for artifact, version in resolved_dependencies():
        floor = FLOORS.get(artifact)
        if floor is None:
            continue
        assert parse_version(version) >= floor, (
            f"{artifact}:{version} resolves below the policy floor {floor}"
        )


def test_single_wire_format_version_across_build():
    """Every module binds the same wire-format version."""
    wires = {v for a, v in resolved_dependencies() if a == "wire-format"}
    assert len(wires) == 1, f"modules diverge on wire-format: {sorted(wires)}"


def test_wire_compatibility_matrix_holds():
    """Each bound client library is paired with a compatible wire major."""
    deps = resolved_dependencies()
    wire_major = {parse_version(v)[0] for a, v in deps if a == "wire-format"}
    assert wire_major, "no wire-format resolved at all"
    bound_wire = wire_major.pop()
    for artifact, version in deps:
        key = (artifact, parse_version(version)[:2])
        required = WIRE_COMPAT.get(key)
        if required is None:
            continue
        assert bound_wire == required, (
            f"{artifact}:{version} requires wire-format {required}.x "
            f"but the build binds {bound_wire}.x"
        )


def test_cli_runs_against_the_bound_jars():
    """The built CLI executes cleanly against whatever the build resolved."""
    assert mvn("clean", "install").returncode == 0, "offline install failed"
    cp_file = Path("/tmp/meter-cli-cp.txt")
    result = mvn(
        "dependency:build-classpath",
        f"-Dmdep.outputFile={cp_file}",
        cwd=PROJECT / "meter-cli",
    )
    assert result.returncode == 0, "classpath resolution failed offline"
    classpath = f"{PROJECT}/meter-cli/target/classes:{cp_file.read_text().strip()}"
    run = subprocess.run(
        ["java", "-cp", classpath, "io.meterhub.app.Main"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert run.returncode == 0, (
        f"CLI failed at runtime against the bound jars:\n{run.stderr[-2000:]}"
    )
    wire = {v for a, v in resolved_dependencies() if a == "wire-format"}.pop()
    assert run.stdout.strip() == f"SUMMARY count=3 wire={wire} legacy=3", (
        f"unexpected CLI output: {run.stdout.strip()!r}"
    )


def test_poms_declare_no_remote_repositories():
    """No pom in the project may declare repositories or plugin repositories."""
    for pom in PROJECT.rglob("pom.xml"):
        text = pom.read_text()
        assert "<repositories>" not in text and "<pluginRepositories>" not in text, (
            f"{pom} declares a remote repository, which the policy forbids"
        )
