#!/usr/bin/env python3
"""Resubmit reconcile-spring-boot-model-registry-with-h2-experiment."""
import os
import re
import subprocess
import sys
import tempfile
import time
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

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
SUBMISSION_ID = "66067373-eca1-43cf-8a0d-2911c7b737fb"
FOLDER = Path(
    "/Users/fabrice-mac-mini/Documents/snorkel-ai/"
    "reconcile-spring-boot-model-registry-with-h2-experiment"
)
SCRATCH = Path("/Users/fabrice-mac-mini/Documents/snorkel-ai/.review-scratch")
AHT_MINUTES = int(os.environ.get("AHT_MINUTES", "240"))


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
    ship = ("instruction.md", "task.toml", "environment", "solution", "tests")
    with zipfile.ZipFile(dest, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for item in ship:
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
    return zipfile.ZipFile(dest).namelist()


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

    assignment_id, _ = get_assignment_id_for_submission(SUBMISSION_ID, project_id=PROJECT_ID)
    feedback_field_name, feedback_id = get_feedback_button_info(PROJECT_ID)
    task_type_str = get_task_type(PROJECT_ID, TaskCategory.SUBMISSION)
    aht_field = get_task_node_aht_field_id(PROJECT_ID, task_type_str) or "submission_aht"

    zip_path = Path(tempfile.gettempdir()) / f"{FOLDER.name}.zip"
    names = build_zip(zip_path)
    leaked = [
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
    if leaked:
        raise SystemExit(f"refusing to upload ZIP with local-only files: {leaked}")
    required = {
        "instruction.md",
        "task.toml",
        "environment/Dockerfile",
        "environment/experiment-db/experiments.mv.db",
        "environment/model-registry/target/model-registry-0.1.0.jar",
        "solution/solve.sh",
        "solution/App.java",
        "tests/test.sh",
        "tests/test_outputs.py",
    }
    missing = required - set(names)
    if missing:
        raise SystemExit(f"ZIP missing required files: {missing}")
    print(f"zipped {len(names)} files ({zip_path.stat().st_size / 1024:.1f} KB)")

    presigned = request_s3_presigned_url(PROJECT_ID, assignment_id, zip_path.name)
    for attempt in range(1, 4):
        try:
            size_mb = zip_path.stat().st_size / (1024 * 1024)
            if size_mb > 20:
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
    print("waiting 90s for S3 availability scan...")
    time.sleep(90)

    feedback_response = None
    for attempt in range(1, 4):
        try:
            feedback_response = create_feedback(
                task_type_str=task_type_str,
                task_id=SUBMISSION_ID,
                feedback_id=feedback_id,
                feedback_field_name=feedback_field_name,
                s3_key=presigned["s3_key"],
                filename=zip_path.name,
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

    payload = get_existing_submission_payload(assignment_id)
    payload["upload_a_zip_file"] = {
        "s3Key": presigned["s3_key"],
        "s3Uri": presigned["s3_uri"],
        "filename": zip_path.name,
        "uploadedAt": presigned["uploaded_at"],
    }
    payload[feedback_field_name] = feedback_response
    payload["checkbox_send_to_reviewer"] = None
    payload["task_type_discriminator"] = task_type_str
    payload[aht_field] = AHT_MINUTES
    payload["test_rubrics"] = test_rubrics
    payload["checkbox_evaluate_rubrics"] = True
    payload.update(explanations)

    result = create_submission(
        {
            "submission_payload": payload,
            "selected_segments": {},
            "submission_id": {"id": SUBMISSION_ID},
            "rebuttal_notes": None,
        }
    )
    print("create_submission:", result)
    print(f"neg criteria: {neg}")
    zip_path.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
