#!/usr/bin/env python3
"""First-time submission of reconcile-spring-boot-model-registry-with-h2-experiment.

Mirrors `stb submissions create` (fresh assignment, checkbox_send_to_reviewer=None)
but carries the ZIP, the three explanation fields, and the flat rubric in ONE
create_submission payload, per .cursor/rules/terminus-submission-hardening.mdc.
"""
import os
import re
import tempfile
import time
import zipfile
from pathlib import Path

from snorkelai_stb.config import FolderConfig
from snorkelai_stb.submission_utils import (
    create_feedback,
    create_submission,
    get_assignment_task_id,
    get_feedback_button_info,
    get_task_node_aht_field_id,
)
from snorkelai_stb.utils import (
    TaskCategory,
    get_task_type,
    request_s3_presigned_url,
    upload_to_s3,
)

PROJECT_ID = "bfe79c33-8ab0-4061-9849-08d3207c9927"
AHT_MINUTES = 240
FOLDER = Path(
    "/Users/fabrice-mac-mini/Documents/snorkel-ai/"
    "reconcile-spring-boot-model-registry-with-h2-experiment"
)
ZIP_NAME = f"{FOLDER.name}.zip"
# Only the task deliverables ship; local planning files (completion_plan.*,
# scaffold_plan.yaml) and .snorkel_config stay out of the ZIP.
SHIP = ("instruction.md", "task.toml", "environment", "solution", "tests")
SCRATCH = Path("/Users/fabrice-mac-mini/Documents/snorkel-ai/.review-scratch")


def parse_explanations() -> dict[str, str]:
    text = (SCRATCH / "registry-explanations.txt").read_text()
    out: dict[str, str] = {}
    for key, header in (
        ("difficulty_explanation", "Difficulty"),
        ("solution_explanation", "Solution"),
        ("verification_explanation", "Verification"),
    ):
        m = re.search(rf"=== {header} ===\n(.*?)(?:\n=== |\Z)", text, re.S)
        if not m or not m.group(1).strip():
            raise SystemExit(f"missing {header} section in registry-explanations.txt")
        out[key] = m.group(1).strip()
    return out


def build_zip(dest: Path) -> list[str]:
    with zipfile.ZipFile(dest, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for item in SHIP:
            src = FOLDER / item
            if src.is_file():
                zf.write(src, item)
                continue
            for path in sorted(src.rglob("*")):
                if path.is_dir() or path.is_symlink():
                    continue
                if path.name in {".DS_Store", ".snorkel_config"}:
                    continue
                if "__pycache__" in path.parts or ".pytest_cache" in path.parts:
                    continue
                zf.write(path, path.relative_to(FOLDER).as_posix())
    names = zipfile.ZipFile(dest).namelist()
    bad = [
        n
        for n in names
        if any(
            x in n.lower()
            for x in (
                "completion_plan",
                "scaffold_plan",
                "rubric",
                "review-scratch",
                "snorkel_config",
                ".ds_store",
            )
        )
    ]
    if bad:
        raise SystemExit(f"refusing to upload ZIP with local-only files: {bad}")
    required = {
        "instruction.md",
        "task.toml",
        "environment/Dockerfile",
        "solution/solve.sh",
        "solution/App.java",
        "tests/test.sh",
        "tests/test_outputs.py",
    }
    missing = required - set(names)
    if missing:
        raise SystemExit(f"ZIP missing required files: {missing}")
    return names


def main() -> None:
    explanations = parse_explanations()
    rubric_path = SCRATCH / "registry-rubrics.txt"
    rubric_lines = [
        ln.strip()
        for ln in rubric_path.read_text().splitlines()
        if ln.strip() and not ln.startswith(("reconcile-", "("))
    ]
    test_rubrics = "\n".join(rubric_lines)
    neg = sum(1 for ln in rubric_lines if re.search(r", -\d+$", ln))
    if neg < 3:
        raise SystemExit(f"rubric has only {neg} negative criteria (need >= 3)")

    zip_path = Path(tempfile.gettempdir()) / ZIP_NAME
    names = build_zip(zip_path)
    print(f"zipped {len(names)} files ({zip_path.stat().st_size / 1024:.1f} KB)")

    task_type_str = get_task_type(PROJECT_ID, TaskCategory.SUBMISSION)
    aht_field = get_task_node_aht_field_id(PROJECT_ID, task_type_str) or "submission_aht"
    feedback_field_name, feedback_id = get_feedback_button_info(PROJECT_ID)

    # Reuse the assignment from a previous aborted attempt when provided, so we
    # don't leave orphan OFFERED slots on the platform.
    task_id = os.environ.get("REUSE_TASK_ID")
    assignment_id = os.environ.get("REUSE_ASSIGNMENT_ID")
    if not (task_id and assignment_id):
        task_id, assignment_id = get_assignment_task_id(PROJECT_ID, task_type_str)
    print(f"assignment {assignment_id} / submission task {task_id}")

    presigned = request_s3_presigned_url(PROJECT_ID, assignment_id, ZIP_NAME)
    upload_to_s3(presigned["presigned_url"], zip_path)
    print("uploaded")

    feedback_response = None
    for attempt in range(1, 4):
        try:
            feedback_response = create_feedback(
                task_type_str=task_type_str,
                task_id=task_id,
                feedback_id=feedback_id,
                feedback_field_name=feedback_field_name,
                s3_key=presigned["s3_key"],
                filename=ZIP_NAME,
                uploaded_at=presigned["uploaded_at"],
                s3_uri=presigned["s3_uri"],
            )
            break
        except Exception as exc:
            if attempt == 3 or "504" not in str(exc):
                raise
            print(f"static checks attempt {attempt} timed out (504); retrying in 30s...")
            time.sleep(30)
    assert feedback_response is not None
    outcome = feedback_response.get("feedback_outcome")
    print("static checks:", outcome)
    if outcome != "PASS":
        print(feedback_response)
        raise SystemExit(f"static checks failed: {outcome}")

    payload = {
        "upload_a_zip_file": {
            "s3Key": presigned["s3_key"],
            "s3Uri": presigned["s3_uri"],
            "filename": ZIP_NAME,
            "uploadedAt": presigned["uploaded_at"],
        },
        feedback_field_name: feedback_response,
        "code_difficulty_check_results": "",
        "code_quality_check_results": "",
        "checkbox_send_to_reviewer": None,  # --no-send-to-reviewer
        "task_type_discriminator": task_type_str,
        aht_field: AHT_MINUTES,
        "test_rubrics": test_rubrics,
        "checkbox_evaluate_rubrics": True,
        **explanations,
    }

    result = create_submission(
        {
            "submission_payload": payload,
            "selected_segments": {},
            "submission_id": {"id": task_id},
            "rebuttal_notes": None,
        }
    )
    print("create_submission:", result)
    FolderConfig.write(FOLDER, task_id)
    print(f"submission id: {task_id}  (rubric neg criteria: {neg})")
    zip_path.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
