#!/usr/bin/env python3
"""Submit repair-flask-signalbox-configs with ZIP + explanations + rubric."""
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
SUBMISSION_ID = os.environ.get(
    "SUBMISSION_ID", "3a48c644-09b8-4357-9466-403cb2674a1c"
)
INSPIRATION_ID = os.environ.get(
    "INSPIRATION_ID", "4f2e12b2-7089-4863-92ba-1dfce8a5c26e"
)
FOLDER = Path(
    "/Users/fabrice-mac-mini/Documents/snorkel-ai/repair-flask-signalbox-configs"
)
RUBRIC = Path(
    "/Users/fabrice-mac-mini/Documents/snorkel-ai/.review-scratch/signalbox-rubrics.txt"
)
EXPL = FOLDER / ".submission-explanations.txt"


def load_explanations() -> tuple[str, str, str]:
    text = EXPL.read_text().strip().split("\n\n")
    if len(text) < 3:
        raise SystemExit("expected three paragraphs in .submission-explanations.txt")
    return text[0].strip(), text[1].strip(), text[2].strip()


def main() -> None:
    difficulty, solution, verification = load_explanations()
    test_rubrics = RUBRIC.read_text().strip() if RUBRIC.exists() else ""

    assignment_id, _ = get_assignment_id_for_submission(
        SUBMISSION_ID, project_id=PROJECT_ID
    )
    feedback_field_name, feedback_id = get_feedback_button_info(PROJECT_ID)
    task_type_str = get_task_type(PROJECT_ID, TaskCategory.SUBMISSION)
    aht_field = get_task_node_aht_field_id(PROJECT_ID, task_type_str) or "submission_aht"

    zip_path = Path(tempfile.gettempdir()) / "repair-flask-signalbox-configs.zip"
    zip_folder(FOLDER, zip_path)
    print("zipped", f"{zip_path.stat().st_size / 1024:.1f} KB")

    presigned = request_s3_presigned_url(
        PROJECT_ID, assignment_id, "repair-flask-signalbox-configs.zip"
    )
    upload_to_s3(presigned["presigned_url"], zip_path)
    print("uploaded")

    feedback_response = create_feedback(
        task_type_str=task_type_str,
        task_id=SUBMISSION_ID,
        feedback_id=feedback_id,
        feedback_field_name=feedback_field_name,
        s3_key=presigned["s3_key"],
        filename="repair-flask-signalbox-configs.zip",
        uploaded_at=presigned["uploaded_at"],
        s3_uri=presigned["s3_uri"],
    )
    outcome = feedback_response.get("feedback_outcome")
    print("static checks:", outcome)
    if outcome != "PASS":
        import json

        print(json.dumps(feedback_response, indent=2)[:12000])
        raise SystemExit(f"static checks failed: {outcome}")

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
        "filename": "repair-flask-signalbox-configs.zip",
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
    payload["textarea-3dd6b"] = INSPIRATION_ID
    payload[aht_field] = AHT_MINUTES

    result = create_submission(
        {
            "submission_payload": payload,
            "selected_segments": {},
            "submission_id": {"id": SUBMISSION_ID},
            "rebuttal_notes": None,
        }
    )
    print("create_submission:", result)
    print("neg criteria:", test_rubrics.count(", -"))
    zip_path.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
