#!/usr/bin/env python3
"""Resubmit a Terminus task: ZIP + explanations + rubric in one create_submission call."""
import os
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
AHT_MINUTES = int(os.environ.get("AHT_MINUTES", "240"))

TASKS = {
    "php": {
        "id": "0c176558-e5c1-444a-804b-f4b4cc3cbd29",
        "folder": Path("/Users/fabrice-mac-mini/Documents/snorkel-ai/harden-php-api-defaults"),
        "zip_name": "harden-php-api-defaults.zip",
        "difficulty": (
            "Agents must reconcile a broken PHP API against a long hardening standard "
            "whose body text is superseded by Appendix G amendments. The instruction "
            "names the amended controls but leaves exact header shapes, status codes, "
            "and denial reasons in /app/docs/standard.md. Sticky in-process CORS/"
            "bootstrap/token/secret caches, on-disk digest and secret re-read "
            "requirements, malformed Authorization parsing (G-2026-18), and a silent "
            "audit-schema defect still trip agents across randomized lifecycles."
        ),
        "solution": (
            "Read /app/docs/standard.md including Appendix G, then patch config.php, "
            "http.php, audit.php, index.php, and start.sh. apply_cors() grants only "
            "exact allowlist origins with credentials and Vary: Origin. Bootstrap "
            "returns 409 before secret check on repeat and re-reads the secret file "
            "each attempt. Token is hashed for storage with owner-only file "
            "permissions. Health treats non-Bearer or empty Bearer as "
            "missing_credentials. Audit schema is migrated idempotently on each DB open."
        ),
        "verification": (
            "Pytest drives curl against the live PHP server across deterministic replays "
            "and 75 randomized lifecycles. Checks include per-request CORS grants, "
            "bootstrap ordering and on-disk eligibility after token removal, on-disk "
            "secret rotation without process restart, digest-based token storage with "
            "per-request re-read from disk, authenticated /health with correct denial "
            "reasons including G-2026-18 malformed Authorization handling and G-2026-19 "
            "token-file existence versus digest validity, SQL NULL "
            "origin when no Origin header is present, no debug leak, audit rows with "
            "origin preserved, legacy history retained, and full agreement with a hidden "
            "reference simulator."
        ),
    },
    "aes": {
        "id": "fbb351b7-0c45-4402-9b19-08d2cd8fddf8",
        "folder": Path("/Users/fabrice-mac-mini/Documents/snorkel-ai/reproduce-java-aes-gcm-findings"),
        "zip_name": "reproduce-java-aes-gcm-findings.zip",
        "difficulty": (
            "This task is hard because the rules you need are buried in a long "
            "adversarial forensic report, not in the milestone briefs. The normative "
            "voiding, ordering, and scoping semantics live only in Appendix C "
            "subsections C.3-C.5; narrative padding elsewhere claims recorded_at "
            "ordering while the binding rule is effective_at, and withdrawn errata "
            "after Appendix D repeat override phrasing with wrong hex values. The "
            "M1 rules stage ships nearly complete but with errata-filtering bugs agents "
            "must repair before correlating the adversarial ledger: triple rotations where only the latest-effective replacement counts, "
            "rotation to a lower version, rescission chains, amendment/replacement/"
            "revocation nonce chains paired by supersedes_nonce_hex, key-version "
            "scoping after rotation, and report overrides that beat later SQLite rows."
        ),
        "solution": (
            "Extend the three-stage Java CLI under com.mariner.forensic.Main. Repair the "
            "rules stage to scope parsing to normative Appendix C and D, extract precedence and "
            "five report overrides, anchors review_date on Findings overview. correlate "
            "applies the Appendix C.3-C.5 semantics: effective_at ordering, rescission "
            "voiding, override chain pairing, key-version scoping, report overrides "
            "before DB rows, derived nonces otherwise. decrypt parses GIF MRNR/CRYPTO1 "
            "blocks and verifies AES-256-GCM with frame_id as AAD."
        ),
        "verification": (
            "Each milestone runs the compiled Main subcommand and checks JSON against "
            "schema plus hidden expected files. M1 checks precedence, five Appendix D "
            "overrides without withdrawn errata hex, review_date. M2 checks JDBC "
            "correlation with report-then-DB-then-derived nonce precedence, "
            "triple-rotation frm-011, report-over-DB frm-010, latest DB among "
            "superseded rows. M3 checks every frame authenticates."
        ),
    },
    "tls": {
        "id": "71323da7-976c-405b-9dcd-c24d83fa6102",
        "folder": Path("/Users/fabrice-mac-mini/Documents/snorkel-ai/reproduce-java-tls-waiver-findings"),
        "zip_name": "reproduce-java-tls-waiver-findings.zip",
        "difficulty": (
            "Agents mine waiver lifecycle facts from a long narrative report, join H2 "
            "probe history where only the latest capture matters, then apply an amended "
            "precedence-ordered adjudication ruleset, matching each waiver's type and "
            "scope to the specific violation. Trap cases drive the difficulty: a wrong-type "
            "or out-of-scope in-force waiver is still a denial; the lapsing-waiver rotation "
            "is decided ahead of hygiene triggers but only when the waiver actually excuses "
            "a violation; a covered violation whose waiver is comfortably in date falls "
            "through to the hygiene reason while still counting as applied; and a lapsing "
            "waiver that excuses no violation pulls nothing. A naive Appendix G reading "
            "mislabels several. Each milestone builds on the prior Java pipeline stage; "
            "the starter scaffold is near-complete with subtle defects (wrong probe "
            "selection, scope matching, and precedence ordering) that agents must find "
            "by reading the report and schemas rather than rewriting from scratch."
        ),
        "solution": (
            "Extend the provided Java CLI under com.mariner.audit.Main. decode parses "
            "the report into a schema-valid waivers.json array. join queries H2 for cert "
            "and latest probe rows merged with waivers. validate applies the amended "
            "adjudication precedence and writes findings.json via a no-argument "
            "Main validate subcommand."
        ),
        "verification": (
            "M1 checks waivers.json schema and ground truth with exact flat field "
            "names (revoked_on, svc-NNN ids, waiver_type/status enums) for all "
            "33 inventory services. M2 checks evidence.json uses "
            "latest probe per service. M3 checks findings.json disposition totals and "
            "full reason-code distribution including lapsing-waiver-vs-hygiene overlap."
        ),
    },
}


def main() -> None:
    if len(sys.argv) != 2 or sys.argv[1] not in TASKS:
        print(f"usage: resubmit_one.py [{'|'.join(TASKS)}]")
        sys.exit(1)

    task = TASKS[sys.argv[1]]
    rubric_path = Path(f"/Users/fabrice-mac-mini/Documents/snorkel-ai/.review-scratch/{sys.argv[1]}-rubrics.txt")
    test_rubrics = rubric_path.read_text().strip() if rubric_path.exists() else ""

    assignment_id, _ = get_assignment_id_for_submission(task["id"])
    feedback_field_name, feedback_id = get_feedback_button_info(PROJECT_ID)
    task_type_str = get_task_type(PROJECT_ID, TaskCategory.SUBMISSION)
    aht_field = get_task_node_aht_field_id(PROJECT_ID, task_type_str) or "submission_aht"

    zip_path = Path(tempfile.gettempdir()) / task["zip_name"]
    zip_task_folder(task["folder"], zip_path)
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

    presigned = request_s3_presigned_url(PROJECT_ID, assignment_id, task["zip_name"])
    upload_to_s3(presigned["presigned_url"], zip_path)
    print("uploaded")

    feedback_response = None
    for attempt in range(1, 4):
        try:
            feedback_response = create_feedback(
                task_type_str=task_type_str,
                task_id=task["id"],
                feedback_id=feedback_id,
                feedback_field_name=feedback_field_name,
                s3_key=presigned["s3_key"],
                filename=task["zip_name"],
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
        raise SystemExit(f"static checks failed: {outcome}")

    payload = get_existing_submission_payload(assignment_id)
    payload["upload_a_zip_file"] = {
        "s3Key": presigned["s3_key"],
        "s3Uri": presigned["s3_uri"],
        "filename": task["zip_name"],
        "uploadedAt": presigned["uploaded_at"],
    }
    payload[feedback_field_name] = feedback_response
    payload["difficulty_explanation"] = task["difficulty"]
    payload["solution_explanation"] = task["solution"]
    payload["verification_explanation"] = task["verification"]
    payload["test_rubrics"] = test_rubrics
    payload["checkbox_evaluate_rubrics"] = True
    payload["checkbox_send_to_reviewer"] = None
    payload["task_type_discriminator"] = task_type_str
    payload[aht_field] = AHT_MINUTES

    result = create_submission({
        "submission_payload": payload,
        "selected_segments": {},
        "submission_id": {"id": task["id"]},
        "rebuttal_notes": None,
    })
    print("create_submission:", result)
    print("neg criteria:", test_rubrics.count(", -"))
    zip_path.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
