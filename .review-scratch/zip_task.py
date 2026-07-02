"""Zip a Terminus task folder, omitting local-only files that must not ship."""
from __future__ import annotations

import zipfile
from pathlib import Path

SKIP_FILE_NAMES = {
    ".submission-explanations.txt",
    ".rubric-for-ui.txt",
    ".snorkel_config",
    "README.md",
}
SKIP_DIR_NAMES = {
    "jobs",
    "tools",
    ".git",
    ".ruff_cache",
    ".dev",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
}


def zip_task_folder(folder: Path, dest: Path) -> None:
    """Write a submission ZIP for ``folder`` to ``dest``."""
    folder = folder.resolve()
    with zipfile.ZipFile(dest, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(folder.rglob("*")):
            if path.is_dir():
                continue
            rel = path.relative_to(folder)
            if any(part in SKIP_DIR_NAMES for part in rel.parts):
                continue
            if path.name in SKIP_FILE_NAMES:
                continue
            zf.write(path, rel.as_posix())
