"""Render environment artifacts and hidden expected JSON from tools/reference.py.

Run from the task root:

    python3 tools/gen_dataset.py
"""

from __future__ import annotations

import json
import pathlib

import reference as ref

ROOT = pathlib.Path(__file__).resolve().parent.parent
ENV = ROOT / "environment"
STEPS = ROOT / "steps"


def _w(path: pathlib.Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    print(f"  wrote {path.relative_to(ROOT)}  ({len(text):,} bytes)")


def _dump(obj) -> str:
    return json.dumps(obj, indent=2) + "\n"


def gen_seed_sql() -> None:
    lines: list[str] = []
    lines.append("-- Mariner forensic audit store. Loaded into SQLite at image build.")
    lines.append("")
    lines.append("PRAGMA foreign_keys = ON;")
    lines.append("")
    lines.append("DROP TABLE IF EXISTS audit_events;")
    lines.append("DROP TABLE IF EXISTS key_material;")
    lines.append("DROP TABLE IF EXISTS frames;")
    lines.append("")
    lines.append("CREATE TABLE frames (")
    lines.append("    frame_id   TEXT PRIMARY KEY,")
    lines.append("    label      TEXT NOT NULL,")
    lines.append("    gif_index  INTEGER NOT NULL")
    lines.append(");")
    lines.append("")
    lines.append("CREATE TABLE key_material (")
    lines.append("    key_version INTEGER PRIMARY KEY,")
    lines.append("    key_hex     TEXT NOT NULL")
    lines.append(");")
    lines.append("")
    lines.append("CREATE TABLE audit_events (")
    lines.append("    event_id                INTEGER PRIMARY KEY AUTOINCREMENT,")
    lines.append("    frame_id                TEXT NOT NULL,")
    lines.append("    event_type              TEXT NOT NULL,")
    lines.append("    key_version             INTEGER,")
    lines.append("    replacement_key_version INTEGER,")
    lines.append("    nonce_override_hex      TEXT,")
    lines.append("    recorded_at             TEXT NOT NULL,")
    lines.append("    FOREIGN KEY (frame_id) REFERENCES frames(frame_id)")
    lines.append(");")
    lines.append("")

    for frame in ref.FRAMES:
        lines.append(
            "INSERT INTO frames (frame_id, label, gif_index) VALUES ("
            f"'{frame['frame_id']}', '{frame['label']}', {frame['gif_index']});"
        )
    lines.append("")

    versions: set[int] = set()
    for e in ref.build_audit_events():
        if e["key_version"] is not None:
            versions.add(e["key_version"])
        if e["replacement_key_version"] is not None:
            versions.add(e["replacement_key_version"])
    for frame in ref.FRAMES:
        versions.add(frame["key_version"])
    for version in sorted(versions):
        key_hex = ref.key_material(version).hex().upper()
        lines.append(
            f"INSERT INTO key_material (key_version, key_hex) VALUES ({version}, '{key_hex}');"
        )
    lines.append("")

    # Scramble insert order so event_id is not correlated with recorded_at.
    events = ref.build_audit_events()
    ordered = list(reversed(events))
    for e in ordered:
        repl = "NULL" if e["replacement_key_version"] is None else str(e["replacement_key_version"])
        nov = "NULL" if e["nonce_override_hex"] is None else f"'{e['nonce_override_hex']}'"
        kv = "NULL" if e["key_version"] is None else str(e["key_version"])
        lines.append(
            "INSERT INTO audit_events "
            "(frame_id, event_type, key_version, replacement_key_version, "
            "nonce_override_hex, recorded_at) VALUES ("
            f"'{e['frame_id']}', '{e['event_type']}', {kv}, {repl}, {nov}, "
            f"'{e['recorded_at']}');"
        )
    lines.append("")
    _w(ENV / "data" / "seed.sql", "\n".join(lines) + "\n")


def gen_configs() -> None:
    yaml = [
        "# Mariner AES-GCM forensic policy — operative parameters for the",
        "# 2026 mid-year media-evidence review.",
        f'review_date: "{ref.REVIEW_DATE.isoformat()}"',
        f'gif_fixture: "{ref.GIF_PATH}"',
        f'jdbc_url: "{ref.JDBC_URL}"',
        "aad_binding: frame_id",
        "algorithm: AES-256-GCM",
    ]
    _w(ENV / "config" / "policy.yaml", "\n".join(yaml) + "\n")

    versions: set[int] = set()
    for e in ref.build_audit_events():
        if e["key_version"] is not None:
            versions.add(e["key_version"])
        if e["replacement_key_version"] is not None:
            versions.add(e["replacement_key_version"])
    for frame in ref.FRAMES:
        versions.add(frame["key_version"])
    toml = [
        "# Vault key-version catalogue cross-reference.",
        f"active_versions = [{', '.join(str(v) for v in sorted(versions))}]",
        "",
        "[gcm]",
        "nonce_length_bytes = 12",
        "tag_length_bytes = 16",
    ]
    _w(ENV / "config" / "crypto.toml", "\n".join(toml) + "\n")


def gen_schemas() -> None:
    base = "https://mariner.internal/schema"

    policy_schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": f"{base}/policy.schema.json",
        "title": "Mariner AES-GCM forensic policy",
        "type": "object",
        "additionalProperties": False,
        "required": [
            "review_date", "gif_fixture", "jdbc_url", "aad_binding", "algorithm",
        ],
        "properties": {
            "review_date": {"type": "string", "format": "date"},
            "gif_fixture": {"type": "string"},
            "jdbc_url": {"type": "string"},
            "aad_binding": {"type": "string", "enum": ["frame_id"]},
            "algorithm": {"type": "string", "enum": ["AES-256-GCM"]},
        },
    }
    _w(ENV / "schema" / "policy.schema.json", _dump(policy_schema))

    crypto_schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": f"{base}/crypto.schema.json",
        "title": "Mariner GCM parameters",
        "type": "object",
        "additionalProperties": False,
        "required": ["active_versions", "gcm"],
        "properties": {
            "active_versions": {
                "type": "array",
                "items": {"type": "integer", "minimum": 1},
            },
            "gcm": {
                "type": "object",
                "additionalProperties": False,
                "required": ["nonce_length_bytes", "tag_length_bytes"],
                "properties": {
                    "nonce_length_bytes": {"type": "integer", "enum": [12]},
                    "tag_length_bytes": {"type": "integer", "enum": [16]},
                },
            },
        },
    }
    _w(ENV / "schema" / "crypto.schema.json", _dump(crypto_schema))

    rules_schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": f"{base}/rules.schema.json",
        "title": "Extracted cryptographic exception rules",
        "type": "object",
        "additionalProperties": False,
        "required": [
            "review_date",
            "key_selection_precedence",
            "nonce_selection_precedence",
            "derived_nonce_rule",
            "nonce_overrides",
        ],
        "properties": {
            "review_date": {"type": "string", "format": "date"},
            "key_selection_precedence": {
                "type": "array",
                "minItems": 2,
                "items": {
                    "type": "string",
                    "enum": ["rotation_replacement", "latest_key_assigned"],
                },
            },
            "nonce_selection_precedence": {
                "type": "array",
                "minItems": 2,
                "items": {
                    "type": "string",
                    "enum": ["report_override", "derived_sha256_prefix"],
                },
            },
            "derived_nonce_rule": {"type": "string"},
            "nonce_overrides": {
                "type": "object",
                "additionalProperties": {"type": "string", "pattern": "^[0-9A-F]{24}$"},
            },
        },
    }
    _w(ENV / "schema" / "rules.schema.json", _dump(rules_schema))

    correlation_schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": f"{base}/correlation.schema.json",
        "title": "Audit-database correlation",
        "type": "array",
        "items": {
            "type": "object",
            "additionalProperties": False,
            "required": [
                "frame_id", "label", "gif_index",
                "key_version", "key_source", "nonce_hex", "nonce_source",
            ],
            "properties": {
                "frame_id": {"type": "string", "pattern": "^frm-[0-9]{3}$"},
                "label": {"type": "string"},
                "gif_index": {"type": "integer", "minimum": 0},
                "key_version": {"type": "integer", "minimum": 1},
                "key_source": {
                    "type": "string",
                    "enum": ["rotation_replacement", "latest_assigned"],
                },
                "nonce_hex": {"type": "string", "pattern": "^[0-9A-F]{24}$"},
                "nonce_source": {"type": "string", "enum": ["derived", "override"]},
            },
        },
    }
    _w(ENV / "schema" / "correlation.schema.json", _dump(correlation_schema))

    findings_schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": f"{base}/findings.schema.json",
        "title": "AES-GCM media decryption findings",
        "type": "array",
        "items": {
            "type": "object",
            "additionalProperties": False,
            "required": [
                "frame_id", "label", "gif_index",
                "key_version", "key_source", "nonce_hex", "nonce_source",
                "auth_ok", "plaintext_sha256", "reason_code",
            ],
            "properties": {
                "frame_id": {"type": "string", "pattern": "^frm-[0-9]{3}$"},
                "label": {"type": "string"},
                "gif_index": {"type": "integer", "minimum": 0},
                "key_version": {"type": "integer", "minimum": 1},
                "key_source": {
                    "type": "string",
                    "enum": ["rotation_replacement", "latest_assigned"],
                },
                "nonce_hex": {"type": "string", "pattern": "^[0-9A-F]{24}$"},
                "nonce_source": {"type": "string", "enum": ["derived", "override"]},
                "auth_ok": {"type": "boolean"},
                "plaintext_sha256": {"type": "string", "pattern": "^[0-9a-f]{64}$"},
                "reason_code": {
                    "type": "string",
                    "enum": ["authenticated", "auth_failed"],
                },
            },
        },
    }
    _w(ENV / "schema" / "findings.schema.json", _dump(findings_schema))


def gen_expected() -> None:
    _w(STEPS / "milestone_1" / "tests" / "expected_rules.json",
       _dump(ref.rules_expected()))
    _w(STEPS / "milestone_2" / "tests" / "expected_correlation.json",
       _dump(ref.correlation_expected()))
    _w(STEPS / "milestone_3" / "tests" / "expected_findings.json",
       _dump(ref.findings_expected()))


def main() -> None:
    print("Generating Mariner AES-GCM forensic dataset...")
    gen_seed_sql()
    gen_configs()
    gen_schemas()
    gen_expected()
    import gen_gif
    gen_gif.main()
    import gen_report
    gen_report.gen_report(ENV / "reports" / "mariner-aes-gcm-forensic-review.md")
    print("aggregate counts:", ref.aggregate_counts())
    print("done.")


if __name__ == "__main__":
    main()
