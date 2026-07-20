#!/usr/bin/env python3
"""Submit enforce-java-release-signature-trust with ZIP + explanations + rubric."""
import os
import re
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from zip_task import zip_task_folder

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
)

PROJECT_ID = "bfe79c33-8ab0-4061-9849-08d3207c9927"
AHT_MINUTES = int(os.environ.get("AHT_MINUTES", "180"))
SUBMISSION_ID = os.environ.get("SUBMISSION_ID", "")
INSPIRATION_ID = os.environ.get("INSPIRATION_ID", "")
FOLDER = Path(
    "/Users/fabrice-mac-mini/Documents/snorkel-ai/enforce-java-release-signature-trust"
)
RUBRIC = Path(
    "/Users/fabrice-mac-mini/Documents/snorkel-ai/.review-scratch/attestation-rubrics.txt"
)
EXPL = Path(
    "/Users/fabrice-mac-mini/Documents/snorkel-ai/.review-scratch/attestation-explanations.txt"
)


def load_explanations() -> tuple[str, str, str]:
    text = EXPL.read_text().strip().split("\n\n")
    if len(text) < 3:
        raise SystemExit("expected three paragraphs in attestation-explanations.txt")
    return text[0].strip(), text[1].strip(), text[2].strip()


def validate_rubric(test_rubrics: str) -> None:
    rubric_lines = [
        ln.strip()
        for ln in test_rubrics.splitlines()
        if ln.strip() and not ln.startswith(("repair-", "("))
    ]
    invalid = [
        ln
        for ln in rubric_lines
        if not re.fullmatch(r"Agent .+, [+-](?:1|2|3|5)", ln)
    ]
    if invalid:
        raise SystemExit(f"invalid rubric wording or score: {invalid}")
    neg = sum(1 for ln in rubric_lines if re.search(r", -\d+$", ln))
    if neg < 3:
        raise SystemExit(f"rubric has only {neg} negative criteria (need >= 3)")
    pos = sum(int(re.search(r", \+(\d+)$", ln).group(1)) for ln in rubric_lines if ", +" in ln)
    if pos < 10 or pos > 40:
        raise SystemExit(f"positive rubric total {pos} outside 10-40")


def main() -> None:
    if not SUBMISSION_ID:
        raise SystemExit("set SUBMISSION_ID (and INSPIRATION_ID) before running")
    difficulty, solution, verification = load_explanations()
    test_rubrics = RUBRIC.read_text().strip()
    validate_rubric(test_rubrics)

    assignment_id, _ = get_assignment_id_for_submission(SUBMISSION_ID, project_id=PROJECT_ID)
    feedback_field_name, feedback_id = get_feedback_button_info(PROJECT_ID)
    task_type_str = get_task_type(PROJECT_ID, TaskCategory.SUBMISSION)
    aht_field = get_task_node_aht_field_id(PROJECT_ID, task_type_str) or "submission_aht"

    zip_path = Path(tempfile.gettempdir()) / f"{FOLDER.name}.zip"
    zip_task_folder(FOLDER, zip_path)
    import zipfile

    names = zipfile.ZipFile(zip_path).namelist()
    leaked = [
        n
        for n in names
        if any(
            x in n.lower()
            for x in (
                "rubric",
                "review-scratch",
                "submission-explanations",
                "tools/",
                "readme.md",
            )
        )
    ]
    if leaked:
        raise SystemExit(f"refusing to upload ZIP with non-task files: {leaked}")
    print("zipped", len(names), "files", f"({zip_path.stat().st_size / 1024:.1f} KB)")

    presigned = request_s3_presigned_url(
        PROJECT_ID, assignment_id, f"{FOLDER.name}.zip"
    )
    upload_to_s3(presigned["presigned_url"], zip_path)
    print("uploaded")

    feedback_response = None
    for attempt in range(1, 4):
        try:
            feedback_response = create_feedback(
                task_type_str=task_type_str,
                task_id=SUBMISSION_ID,
                feedback_id=feedback_id,
                feedback_field_name=feedback_field_name,
                s3_key=presigned["s3_key"],
                filename=f"{FOLDER.name}.zip",
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
        "filename": f"{FOLDER.name}.zip",
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
    if INSPIRATION_ID:
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
    zip_path.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
