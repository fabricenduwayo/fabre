#!/usr/bin/env python3
"""First-time submit for extend-maven-spring-awk-fixtures and repair-java-trailswitch-graph-rules."""
import os
import sys
import tempfile
from pathlib import Path

from snorkelai_stb.submission_utils import (
    create_feedback,
    create_submission,
    get_assignment_id_for_submission,
    get_existing_submission_payload,
    get_feedback_button_info,
    get_task_node_aht_field_id,
)
from snorkelai_stb.utils import (
    TaskCategory,
    get_task_type,
    request_s3_presigned_url,
    upload_to_s3,
    zip_folder,
)

PROJECT_ID = "bfe79c33-8ab0-4061-9849-08d3207c9927"
AHT_MINUTES = int(os.environ.get("AHT_MINUTES", "240"))
ROOT = Path("/Users/fabrice-mac-mini/Documents/snorkel-ai")

TASKS = {
    "awk": {
        "submission_id": "6b30193a-b8fc-4a73-86c1-0b5c3182d99c",
        "folder": ROOT / "extend-maven-spring-awk-fixtures",
        "zip_name": "extend-maven-spring-awk-fixtures.zip",
        "rubric": ROOT / ".review-scratch/awk-rubrics.txt",
    },
    "trailswitch": {
        "submission_id": "f0e91036-8b36-4f80-9e35-52e7ce33dd3e",
        "folder": ROOT / "repair-java-trailswitch-graph-rules",
        "zip_name": "repair-java-trailswitch-graph-rules.zip",
        "rubric": ROOT / ".review-scratch/trailswitch-rubrics.txt",
    },
}


def load_explanations(folder: Path) -> tuple[str, str, str]:
    text = (folder / ".submission-explanations.txt").read_text().strip().split("\n\n")
    if len(text) < 3:
        raise SystemExit(f"expected three paragraphs in {folder}/.submission-explanations.txt")
    return text[0].strip(), text[1].strip(), text[2].strip()


def submit_one(task_key: str) -> None:
    task = TASKS[task_key]
    difficulty, solution, verification = load_explanations(task["folder"])
    test_rubrics = task["rubric"].read_text().strip()

    submission_id = task["submission_id"]
    assignment_id, _ = get_assignment_id_for_submission(
        submission_id, project_id=PROJECT_ID
    )
    feedback_field_name, feedback_id = get_feedback_button_info(PROJECT_ID)
    task_type_str = get_task_type(PROJECT_ID, TaskCategory.SUBMISSION)
    aht_field = get_task_node_aht_field_id(PROJECT_ID, task_type_str) or "submission_aht"

    zip_path = Path(tempfile.gettempdir()) / task["zip_name"]
    zip_folder(task["folder"], zip_path)
    print(f"[{task_key}] zipped {zip_path.stat().st_size / 1024:.1f} KB")

    presigned = request_s3_presigned_url(PROJECT_ID, assignment_id, task["zip_name"])
    upload_to_s3(presigned["presigned_url"], zip_path)
    print(f"[{task_key}] uploaded")

    feedback_response = create_feedback(
        task_type_str=task_type_str,
        task_id=submission_id,
        feedback_id=feedback_id,
        feedback_field_name=feedback_field_name,
        s3_key=presigned["s3_key"],
        filename=task["zip_name"],
        uploaded_at=presigned["uploaded_at"],
        s3_uri=presigned["s3_uri"],
    )
    outcome = feedback_response.get("feedback_outcome")
    print(f"[{task_key}] static checks: {outcome}")
    if outcome != "PASS":
        import json

        print(json.dumps(feedback_response, indent=2)[:12000])
        raise SystemExit(f"[{task_key}] static checks failed: {outcome}")

    try:
        payload = get_existing_submission_payload(assignment_id)
    except ValueError:
        payload = {
            "code_difficulty_check_results": "",
            "code_quality_check_results": "",
        }

    payload["upload_a_zip_file"] = {
        "s3Key": presigned["s3_key"],
        "s3Uri": presigned["s3_uri"],
        "filename": task["zip_name"],
        "uploadedAt": presigned["uploaded_at"],
    }
    payload[feedback_field_name] = feedback_response
    payload["difficulty_explanation"] = difficulty
    payload["solution_explanation"] = solution
    payload["verification_explanation"] = verification
    payload["test_rubrics"] = test_rubrics
    payload["checkbox_evaluate_rubrics"] = True
    payload["checkbox_send_to_reviewer"] = None
    payload["task_type_discriminator"] = task_type_str
    payload[aht_field] = AHT_MINUTES

    result = create_submission(
        {
            "submission_payload": payload,
            "selected_segments": {},
            "submission_id": {"id": submission_id},
            "rebuttal_notes": None,
        }
    )
    print(f"[{task_key}] create_submission: {result}")
    print(f"[{task_key}] neg criteria: {test_rubrics.count(', -')}")

    snorkel_config = task["folder"] / ".snorkel_config"
    snorkel_config.write_text(f"submission_id: {submission_id}\n")
    print(f"[{task_key}] wrote {snorkel_config}")
    zip_path.unlink(missing_ok=True)


def main() -> None:
    if len(sys.argv) != 2 or sys.argv[1] not in TASKS and sys.argv[1] != "all":
        print(f"usage: submit_new_tasks.py [{'|'.join(TASKS)}|all]")
        sys.exit(1)

    keys = list(TASKS) if sys.argv[1] == "all" else [sys.argv[1]]
    for key in keys:
        submit_one(key)


if __name__ == "__main__":
    main()
