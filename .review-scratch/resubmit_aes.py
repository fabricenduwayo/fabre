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

SUBMISSION_ID = "fbb351b7-0c45-4402-9b19-08d2cd8fddf8"
PROJECT_ID = "bfe79c33-8ab0-4061-9849-08d3207c9927"
FOLDER = Path("/Users/fabrice-mac-mini/Documents/snorkel-ai/reproduce-java-aes-gcm-findings")
AHT_MINUTES = int(os.environ["AHT_MINUTES"])

difficulty = (
    "A prior revision restated the whole key/nonce resolution algorithm inside the "
    "milestone instruction, and both Opus and GPT-5.5 then solved every run — the "
    "agent no longer had to read the report. This revision moves that reasoning back "
    "where it belongs: the instruction names the output contract (schema enum tokens "
    "key_source, nonce_source, reason_code), the file paths, and which appendices "
    "govern, but the actual resolution rules live only in the ~230k-char forensic "
    "report. The agent must locate normative Appendix C.1/C.2 and Appendix D and "
    "trust them over a superseded draft Appendix C that sits just before them with a "
    "reversed precedence and a missing db_override tier, plus withdrawn errata that "
    "restate the overrides with wrong hex. Only C.1/C.2 spell out that the operative "
    "rotation is the latest surviving hop (not the highest version), that "
    "key_rotation_rescinded / key_assignment_rescinded void rows with an all-rescinded "
    "assignment fallback, that DB nonce registrations are scoped to the operative key "
    "version so a rotation makes an earlier registration stale, and how revocation, "
    "sequential nonce_override_amended supersession, and post-amendment re-registration "
    "resolve. The agent extends a Java pipeline that walks scrambled SQLite audit "
    "history in recorded_at order, applies all of this across 22 frames, pulls "
    "ciphertext from a GIF, and runs AES-256-GCM with frame_id as AAD. The M2 "
    "verifier requires a byte-exact match on the full correlation, so a single "
    "mis-resolved frame fails the milestone."
)

solution = (
    "I extended the provided three-stage Java CLI under com.mariner.forensic.Main. "
    "The rules stage regex-parses normative Appendix C and D for precedence lists "
    "(including db_override), the verbatim derived-nonce rule, and all five report "
    "overrides (keeping the last operative line per frame when amended). correlate "
    "filters key_rotated rows voided by key_rotation_rescinded, filters "
    "key_assigned rows voided by key_assignment_rescinded, falls back to assignment "
    "when no rotation survives, applies report "
    "overrides before DB registrations that match the operative key_version, "
    "walks nonce_override_amended rows in order to void superseded registrations "
    "while allowing later re-registration of the same bytes, excludes "
    "nonce_override_revoked rows, and derives nonces otherwise. decrypt "
    "extracts ciphertext from the GIF and verifies AES-256-GCM using keys from "
    "the key_material table."
)

verification = (
    "Each milestone runs the compiled Main subcommand for that stage and checks JSON "
    "against the published schema plus hidden expected files under tests/. M1 checks "
    "precedence order including db_override, all five Appendix D overrides from the "
    "normative D section only, amended frm-006 last-line wins, review_date from "
    "Findings overview only, and derived_nonce_rule from Appendix C prose. M2 checks "
    "JDBC correlation including frm-009 rescinded rotation (v5 not v4), frm-014 "
    "post-rotation DB re-registration, frm-015 report override surviving "
    "rotation, frm-016 nonce_override_amended result, frm-017 "
    "post-amendment re-registration for the operative key version, frm-018 "
    "key_assignment_rescinded voiding, frm-019 chained rotation rescission "
    "fallback to v3, frm-020 sequential amendment chain, frm-021 all-rotations-"
    "rescinded assignment fallback to v2, and frm-022 fifth Appendix D override "
    "surviving rotation over a DB registration. M3 checks "
    "schema-valid findings with all required fields and match "
    "to hidden expected_findings.json."
)

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
        upload_to_s3(presigned["presigned_url"], zip_path)
        break
    except Exception as exc:
        if attempt == 3:
            raise
        print(f"upload attempt {attempt} failed: {exc}; retrying")
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
