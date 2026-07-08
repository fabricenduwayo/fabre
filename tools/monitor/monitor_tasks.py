"""Auto-discover task folders and map submissions."""

from __future__ import annotations

import json
from pathlib import Path


def discover_task_folders(repo_root: Path) -> list[str]:
    folders: list[str] = []
    for path in repo_root.iterdir():
        if not path.is_dir():
            continue
        if path.name.startswith("."):
            continue
        if (path / "task.toml").is_file():
            folders.append(path.name)
    return sorted(folders)


def sync_tasks_json(repo_root: Path, tasks_file: Path) -> dict:
    """Merge discovered folders into tasks.json without removing manual entries."""
    existing: dict = {}
    if tasks_file.is_file():
        existing = json.loads(tasks_file.read_text(encoding="utf-8"))
    discovered = discover_task_folders(repo_root)
    changed = False
    for folder in discovered:
        if folder not in existing:
            existing[folder] = {}
            changed = True
    if changed:
        tasks_file.write_text(json.dumps(existing, indent=2) + "\n", encoding="utf-8")
    return existing


def find_submission_for_folder(subs: list[dict], folder: str) -> dict | None:
    folder_l = folder.lower()
    for sub in subs:
        name = (sub.get("folder_name") or "").strip()
        if name.lower() == folder_l:
            return sub
    for sub in subs:
        name = (sub.get("folder_name") or "").strip()
        if folder_l in name.lower():
            return sub
    return None


def resolve_folder_name(text: str, subs: list[dict], repo_root: Path) -> str | None:
    """Match partial folder name against queue, submissions, or disk."""
    needle = text.strip().lower()
    if not needle:
        return None
    for sub in subs:
        name = (sub.get("folder_name") or "").strip()
        if name.lower() == needle or needle in name.lower():
            return name
    for folder in discover_task_folders(repo_root):
        if folder.lower() == needle or needle in folder.lower():
            return folder
    return None
