import os
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

SUBMISSION_ID = "71323da7-976c-405b-9dcd-c24d83fa6102"
PROJECT_ID = "bfe79c33-8ab0-4061-9849-08d3207c9927"
FOLDER = Path("/Users/fabrice-mac-mini/Documents/snorkel-ai/reproduce-java-tls-waiver-findings")
AHT_MINUTES = int(os.environ["AHT_MINUTES"])

difficulty = (
    "Agents have to mine waiver lifecycle facts from a long (~100k token) narrative "
    "report (grants, rescissions, and replacement waivers tied by waiver ID), join that "
    "with H2 probe history where only the latest capture matters, then apply a "
    "precedence-ordered adjudication ruleset from the report appendices - including "
    "comparing waiver expiry dates to the policy review date, not a literal expired "
    "status. The precedence was amended this cycle so the lapsing-waiver rotation is "
    "decided ahead of the certificate-hygiene triggers; several services trip both a "
    "lapsing waiver and a hygiene defect, and a naive top-to-bottom reading of the "
    "appendix reports the wrong reason code for them. Each milestone builds on the prior "
    "Java pipeline stage, so mistakes in decode or join propagate."
)

solution = (
    "A small Java CLI under /app with com.mariner.audit.Main dispatching decode, join, "
    "and validate, each a no-argument subcommand that writes its own output file. "
    "Milestone 1 parses the report into schema-valid waivers.json reflecting final waiver "
    "state per service. Milestone 2 queries H2 for cert and latest probe rows and merges "
    "waivers into evidence.json. Milestone 3 validates policy/crypto config against "
    "schemas, applies the report's adjudication precedence including this cycle's amended "
    "ordering (lapsing-waiver rotation ahead of the hygiene triggers), and writes "
    "findings.json with disposition totals matching the review overview."
)

verification = (
    "Milestone 1 checks waivers.json against the published schema and ground truth - "
    "every in-scope service present with the correct final waiver state. The pipeline "
    "must compile Main under /app/classes or /app/pipeline/classes, and Main validate "
    "must run as a no-argument stage that produces findings.json on its own. Milestone 2 "
    "checks evidence.json rows include the latest probe fields and merged waiver data. "
    "Milestone 3 checks findings.json against the schema, confirms allow/deny/rotate "
    "counts match the report overview, and checks the full per-service reason-code "
    "distribution - so the lapsing-waiver-vs-hygiene overlap cases must report "
    "waiver_expiring_soon, not the hygiene trigger."
)

test_rubrics = Path("/Users/fabrice-mac-mini/Documents/snorkel-ai/.review-scratch/tls-rubrics.txt").read_text().strip()

assignment_id, _ = get_assignment_id_for_submission(SUBMISSION_ID)
feedback_field_name, feedback_id = get_feedback_button_info(PROJECT_ID)
task_type_str = get_task_type(PROJECT_ID, TaskCategory.SUBMISSION)
aht_field = get_task_node_aht_field_id(PROJECT_ID, task_type_str) or "submission_aht"

zip_filename = "reproduce-java-tls-waiver-findings.zip"
zip_path = Path(tempfile.gettempdir()) / zip_filename
zip_folder(FOLDER, zip_path)
print("zipped", f"{zip_path.stat().st_size / 1024:.1f} KB")

presigned = request_s3_presigned_url(PROJECT_ID, assignment_id, zip_filename)
upload_to_s3(presigned["presigned_url"], zip_path)
print("uploaded")

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
