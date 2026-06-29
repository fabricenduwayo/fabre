"""Render every generated artifact for the Mariner TLS waiver task.

Run from the task root:

    python3 tools/gen_dataset.py

Writes (all derived deterministically from tools/reference.py):

  environment/data/seed.sql                 H2 schema + rows (inventory, certs, probes)
  environment/config/policy.yaml            operative policy (YAML)
  environment/config/crypto.toml            key/issuer policy (TOML)
  environment/schema/*.schema.json          JSON schemas for configs + the 3 artifacts
  environment/reports/mariner-tls-waiver-review.md   the long narrative report

  steps/milestone_1/tests/expected_waivers.json
  steps/milestone_2/tests/expected_evidence.json
  steps/milestone_3/tests/expected_findings.json

The expected_*.json files are the hidden ground truth; they live only under
tests/ and are never copied into the image.
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


# ==========================================================================
# 1. H2 seed SQL
# ==========================================================================
def _sql_bool(v: bool) -> str:
    return "TRUE" if v else "FALSE"


def _sql_str(v: str) -> str:
    return "'" + v.replace("'", "''") + "'"


def gen_seed_sql() -> None:
    lines: list[str] = []
    lines.append("-- Mariner service inventory, certificate facts, and captured")
    lines.append("-- curl/httpie probe evidence. Loaded into H2 at image build time.")
    lines.append("")
    lines.append("DROP TABLE IF EXISTS probes;")
    lines.append("DROP TABLE IF EXISTS certificates;")
    lines.append("DROP TABLE IF EXISTS services;")
    lines.append("")
    lines.append("CREATE TABLE services (")
    lines.append("    service_id   VARCHAR(16) PRIMARY KEY,")
    lines.append("    name         VARCHAR(64)  NOT NULL,")
    lines.append("    environment  VARCHAR(16)  NOT NULL,")
    lines.append("    owner        VARCHAR(64)  NOT NULL,")
    lines.append("    endpoint     VARCHAR(160) NOT NULL")
    lines.append(");")
    lines.append("")
    lines.append("CREATE TABLE certificates (")
    lines.append("    service_id   VARCHAR(16) PRIMARY KEY,")
    lines.append("    fingerprint  VARCHAR(128) NOT NULL,")
    lines.append("    not_after    DATE         NOT NULL,")
    lines.append("    key_algo     VARCHAR(8)   NOT NULL,")
    lines.append("    key_bits     INT          NOT NULL,")
    lines.append("    issuer       VARCHAR(64)  NOT NULL,")
    lines.append("    CONSTRAINT fk_cert_service FOREIGN KEY (service_id) REFERENCES services(service_id)")
    lines.append(");")
    lines.append("")
    lines.append("CREATE TABLE probes (")
    lines.append("    probe_id             INT AUTO_INCREMENT PRIMARY KEY,")
    lines.append("    service_id           VARCHAR(16)  NOT NULL,")
    lines.append("    tool                 VARCHAR(16)  NOT NULL,")
    lines.append("    tls_version          VARCHAR(8)   NOT NULL,")
    lines.append("    verify_ok            BOOLEAN      NOT NULL,")
    lines.append("    mtls_required        BOOLEAN      NOT NULL,")
    lines.append("    mtls_presented       BOOLEAN      NOT NULL,")
    lines.append("    chain_valid          BOOLEAN      NOT NULL,")
    lines.append("    http_status          INT          NOT NULL,")
    lines.append("    observed_fingerprint VARCHAR(128) NOT NULL,")
    lines.append("    captured_at          TIMESTAMP    NOT NULL,")
    lines.append("    CONSTRAINT fk_probe_service FOREIGN KEY (service_id) REFERENCES services(service_id)")
    lines.append(");")
    lines.append("")

    services = sorted(ref.SERVICES, key=lambda x: x["sid"])
    for s in services:
        lines.append(
            "INSERT INTO services (service_id, name, environment, owner, endpoint) VALUES ("
            f"{_sql_str(s['sid'])}, {_sql_str(s['name'])}, {_sql_str(s['env'])}, "
            f"{_sql_str(s['owner'])}, {_sql_str(s['endpoint'])});"
        )
    lines.append("")
    for s in services:
        c = s["cert"]
        lines.append(
            "INSERT INTO certificates (service_id, fingerprint, not_after, key_algo, key_bits, issuer) VALUES ("
            f"{_sql_str(s['sid'])}, {_sql_str(ref.cert_fingerprint(s))}, DATE {_sql_str(c['not_after'])}, "
            f"{_sql_str(c['key_algo'])}, {c['key_bits']}, {_sql_str(c['issuer'])});"
        )
    lines.append("")

    # Probe rows: emit in a deterministically scrambled order so that the
    # auto-increment probe_id is NOT correlated with captured_at — the latest
    # probe per service must be chosen by captured_at, never by max(probe_id).
    for s in services:
        idx = int(s["sid"].split("-")[1])
        history = ref.build_probe_history(s)
        ordered = list(reversed(history)) if idx % 2 == 0 else history
        for p in ordered:
            lines.append(
                "INSERT INTO probes (service_id, tool, tls_version, verify_ok, mtls_required, "
                "mtls_presented, chain_valid, http_status, observed_fingerprint, captured_at) VALUES ("
                f"{_sql_str(s['sid'])}, {_sql_str(p['tool'])}, {_sql_str(p['tls_version'])}, "
                f"{_sql_bool(p['verify_ok'])}, {_sql_bool(p['mtls_required'])}, "
                f"{_sql_bool(p['mtls_presented'])}, {_sql_bool(p['chain_valid'])}, "
                f"{p['http_status']}, {_sql_str(p['observed_fingerprint'])}, "
                f"TIMESTAMP {_sql_str(p['captured_at'])});"
            )
    lines.append("")
    _w(ENV / "data" / "seed.sql", "\n".join(lines) + "\n")


# ==========================================================================
# 2. Config files (YAML + TOML)
# ==========================================================================
def gen_configs() -> None:
    yaml = []
    yaml.append("# Mariner transport-security policy — operative parameters for the")
    yaml.append("# 2026 mid-year TLS waiver review. Consumed by the adjudication pipeline.")
    yaml.append(f'review_date: "{ref.REVIEW_DATE.isoformat()}"')
    yaml.append(f"rotation_window_days: {ref.ROTATION_WINDOW_DAYS}")
    yaml.append("allowed_tls_versions:")
    for v in ref.ALLOWED_TLS_VERSIONS:
        yaml.append(f'  - "{v}"')
    yaml.append("mtls_required_environments:")
    for e in ref.MTLS_REQUIRED_ENVS:
        yaml.append(f'  - "{e}"')
    _w(ENV / "config" / "policy.yaml", "\n".join(yaml) + "\n")

    toml = []
    toml.append("# Mariner key-strength and certificate-authority trust policy.")
    toml.append("# The trusted_issuers list is the authoritative trust anchor set.")
    toml.append("trusted_issuers = [")
    for i in ref.TRUSTED_ISSUERS:
        toml.append(f'    "{i}",')
    toml.append("]")
    toml.append("")
    toml.append("[keys]")
    toml.append(f"min_rsa_bits = {ref.MIN_RSA_BITS}")
    toml.append(f"min_ec_bits = {ref.MIN_EC_BITS}")
    _w(ENV / "config" / "crypto.toml", "\n".join(toml) + "\n")


# ==========================================================================
# 3. JSON Schemas
# ==========================================================================
def _dump(obj) -> str:
    return json.dumps(obj, indent=2) + "\n"


def gen_schemas() -> None:
    base = "https://mariner.internal/schema"

    policy_schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": f"{base}/policy.schema.json",
        "title": "Mariner transport-security policy",
        "type": "object",
        "additionalProperties": False,
        "required": [
            "review_date",
            "rotation_window_days",
            "allowed_tls_versions",
            "mtls_required_environments",
        ],
        "properties": {
            "review_date": {"type": "string", "format": "date"},
            "rotation_window_days": {"type": "integer", "minimum": 0},
            "allowed_tls_versions": {
                "type": "array",
                "minItems": 1,
                "items": {"type": "string", "enum": ["TLS1.0", "TLS1.1", "TLS1.2", "TLS1.3"]},
            },
            "mtls_required_environments": {
                "type": "array",
                "items": {"type": "string", "enum": ["prod", "staging", "dev"]},
            },
        },
    }
    _w(ENV / "schema" / "policy.schema.json", _dump(policy_schema))

    crypto_schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": f"{base}/crypto.schema.json",
        "title": "Mariner key-strength and issuer-trust policy",
        "type": "object",
        "additionalProperties": False,
        "required": ["trusted_issuers", "keys"],
        "properties": {
            "trusted_issuers": {
                "type": "array",
                "minItems": 1,
                "items": {"type": "string"},
            },
            "keys": {
                "type": "object",
                "additionalProperties": False,
                "required": ["min_rsa_bits", "min_ec_bits"],
                "properties": {
                    "min_rsa_bits": {"type": "integer", "minimum": 1},
                    "min_ec_bits": {"type": "integer", "minimum": 1},
                },
            },
        },
    }
    _w(ENV / "schema" / "crypto.schema.json", _dump(crypto_schema))

    waivers_schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": f"{base}/waivers.schema.json",
        "title": "Decoded waiver register",
        "type": "array",
        "items": {
            "type": "object",
            "additionalProperties": False,
            "required": [
                "service_id", "service_name", "waiver_id", "waiver_type",
                "status", "scope", "granted_on", "expires_on", "revoked_on",
            ],
            "properties": {
                "service_id": {"type": "string", "pattern": "^svc-[0-9]{3}$"},
                "service_name": {"type": "string"},
                "waiver_id": {"type": ["string", "null"]},
                "waiver_type": {"type": "string", "enum": ["tls", "mtls", "chain", "none"]},
                "status": {"type": "string", "enum": ["granted", "revoked", "none"]},
                "scope": {"type": ["string", "null"], "enum": ["all", "prod", "staging", "dev", None]},
                "granted_on": {"type": ["string", "null"], "format": "date"},
                "expires_on": {"type": ["string", "null"], "format": "date"},
                "revoked_on": {"type": ["string", "null"], "format": "date"},
            },
        },
    }
    _w(ENV / "schema" / "waivers.schema.json", _dump(waivers_schema))

    evidence_schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": f"{base}/evidence.schema.json",
        "title": "Joined probe evidence",
        "type": "array",
        "items": {
            "type": "object",
            "additionalProperties": False,
            "required": [
                "service_id", "service_name", "environment",
                "waiver_type", "waiver_status", "waiver_scope", "waiver_expires_on",
                "cert_fingerprint", "cert_not_after", "cert_key_algo", "cert_key_bits", "cert_issuer",
                "probe_tls_version", "probe_verify_ok", "probe_mtls_required",
                "probe_mtls_presented", "probe_chain_valid", "probe_http_status",
                "probe_observed_fingerprint",
            ],
            "properties": {
                "service_id": {"type": "string", "pattern": "^svc-[0-9]{3}$"},
                "service_name": {"type": "string"},
                "environment": {"type": "string", "enum": ["prod", "staging", "dev"]},
                "waiver_type": {"type": "string", "enum": ["tls", "mtls", "chain", "none"]},
                "waiver_status": {"type": "string", "enum": ["granted", "revoked", "none"]},
                "waiver_scope": {"type": ["string", "null"]},
                "waiver_expires_on": {"type": ["string", "null"], "format": "date"},
                "cert_fingerprint": {"type": "string"},
                "cert_not_after": {"type": "string", "format": "date"},
                "cert_key_algo": {"type": "string", "enum": ["RSA", "EC"]},
                "cert_key_bits": {"type": "integer"},
                "cert_issuer": {"type": "string"},
                "probe_tls_version": {"type": "string"},
                "probe_verify_ok": {"type": "boolean"},
                "probe_mtls_required": {"type": "boolean"},
                "probe_mtls_presented": {"type": "boolean"},
                "probe_chain_valid": {"type": "boolean"},
                "probe_http_status": {"type": "integer"},
                "probe_observed_fingerprint": {"type": "string"},
            },
        },
    }
    _w(ENV / "schema" / "evidence.schema.json", _dump(evidence_schema))

    findings_schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": f"{base}/findings.schema.json",
        "title": "Final TLS waiver findings",
        "type": "array",
        "items": {
            "type": "object",
            "additionalProperties": False,
            "required": [
                "service_id", "service_name", "environment",
                "disposition", "reason_code", "waiver_applied",
            ],
            "properties": {
                "service_id": {"type": "string", "pattern": "^svc-[0-9]{3}$"},
                "service_name": {"type": "string"},
                "environment": {"type": "string", "enum": ["prod", "staging", "dev"]},
                "disposition": {"type": "string", "enum": ["allow", "deny", "rotate"]},
                "reason_code": {
                    "type": "string",
                    "enum": [
                        "compliant", "active_waiver_ok", "cert_near_expiry",
                        "weak_key", "untrusted_issuer", "fingerprint_mismatch",
                        "mtls_missing", "tls_version_blocked", "chain_invalid",
                        "waiver_expired", "waiver_revoked", "waiver_expiring_soon",
                    ],
                },
                "waiver_applied": {"type": "boolean"},
            },
        },
    }
    _w(ENV / "schema" / "findings.schema.json", _dump(findings_schema))


# ==========================================================================
# 4. Expected (hidden) ground-truth artifacts
# ==========================================================================
def gen_expected() -> None:
    _w(STEPS / "milestone_1" / "tests" / "expected_waivers.json",
       json.dumps(ref.waivers_expected(), indent=2) + "\n")
    _w(STEPS / "milestone_2" / "tests" / "expected_evidence.json",
       json.dumps(ref.evidence_expected(), indent=2) + "\n")
    _w(STEPS / "milestone_3" / "tests" / "expected_findings.json",
       json.dumps(ref.findings_expected(), indent=2) + "\n")


def main() -> None:
    print("Generating Mariner TLS waiver dataset...")
    gen_seed_sql()
    gen_configs()
    gen_schemas()
    gen_expected()
    # The narrative report is large; it lives in its own module to keep this
    # file readable.
    import gen_report
    gen_report.gen_report(ENV / "reports" / "mariner-tls-waiver-review.md")
    print("aggregate counts:", ref.aggregate_counts())
    print("done.")


if __name__ == "__main__":
    main()
