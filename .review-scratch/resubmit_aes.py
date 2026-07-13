import os
import subprocess
import tempfile
import time
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

SUBMISSION_ID = "fbb351b7-0c45-4402-9b19-08d2cd8fddf8"
PROJECT_ID = "bfe79c33-8ab0-4061-9849-08d3207c9927"
FOLDER = Path("/Users/fabrice-mac-mini/Documents/snorkel-ai/reproduce-java-aes-gcm-findings")
AHT_MINUTES = int(os.environ["AHT_MINUTES"])

explanation_blocks = (
    FOLDER / ".submission-explanations.txt"
).read_text().strip().split("\n\n")


def explanation_body(block):
    lines = block.splitlines()
    return "\n".join(lines[1:]).strip()


difficulty = explanation_body(explanation_blocks[0])
solution = explanation_body(explanation_blocks[1])
verification = explanation_body(explanation_blocks[2])

test_rubrics = Path("/Users/fabrice-mac-mini/Documents/snorkel-ai/.review-scratch/aes-rubrics.txt").read_text().strip()

assignment_id, _ = get_assignment_id_for_submission(SUBMISSION_ID)
feedback_field_name, feedback_id = get_feedback_button_info(PROJECT_ID)
task_type_str = get_task_type(PROJECT_ID, TaskCategory.SUBMISSION)
aht_field = get_task_node_aht_field_id(PROJECT_ID, task_type_str) or "submission_aht"

zip_filename = "reproduce-java-aes-gcm-findings.zip"
zip_path = Path(tempfile.gettempdir()) / zip_filename
zip_folder(FOLDER, zip_path)
print("zipped", f"{zip_path.stat().st_size / 1024:.1f} KB")

presigned = request_s3_presigned_url(PROJECT_ID, assignment_id, zip_filename)
for attempt in range(1, 4):
    try:
        size_mb = zip_path.stat().st_size / (1024 * 1024)
        if size_mb > 10:
            result = subprocess.run(
                [
                    "curl",
                    "-fS",
                    "--retry",
                    "3",
                    "--retry-delay",
                    "5",
                    "-X",
                    "PUT",
                    "-H",
                    "Content-Type: application/zip",
                    "--data-binary",
                    f"@{zip_path}",
                    presigned["presigned_url"],
                ],
                capture_output=True,
                text=True,
                timeout=600,
            )
            if result.returncode != 0:
                raise RuntimeError(result.stderr or result.stdout or "curl upload failed")
        else:
            upload_to_s3(presigned["presigned_url"], zip_path)
        break
    except Exception as exc:
        if attempt == 3:
            raise
        print(f"upload attempt {attempt} failed: {exc}; retrying in 10s...")
        time.sleep(10)
print("uploaded")
print("waiting 90s for upload availability")
time.sleep(90)

feedback_response = create_feedback(
    task_type_str=task_type_str,
    task_id=SUBMISSION_ID,
    feedback_id=feedback_id,
    feedback_field_name=feedback_field_name,
    s3_key=presigned["s3_key"],
    filename=zip_filename,
    uploaded_at=presigned["uploaded_at"],
    s3_uri=presigned["s3_uri"],
)
outcome = feedback_response.get("feedback_outcome")
print("static checks:", outcome)
if outcome != "PASS":
    raise SystemExit(f"static checks failed: {outcome}")

payload = get_existing_submission_payload(assignment_id)
payload["upload_a_zip_file"] = {
    "s3Key": presigned["s3_key"],
    "s3Uri": presigned["s3_uri"],
    "filename": zip_filename,
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

result = create_submission({
    "submission_payload": payload,
    "selected_segments": {},
    "submission_id": {"id": SUBMISSION_ID},
    "rebuttal_notes": None,
})
print("create_submission:", result)
print("negative criteria count:", test_rubrics.count(", -"))
zip_path.unlink(missing_ok=True)
