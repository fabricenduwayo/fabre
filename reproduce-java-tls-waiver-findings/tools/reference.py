"""Canonical model + reference decision logic for the Mariner TLS waiver review.

This module is the single source of truth for the task. It is used only at
authoring time:

  * ``tools/gen_dataset.py`` imports it to render the environment inputs
    (the H2 seed SQL, the YAML/TOML policy, the JSON schemas, and the long
    narrative report) and the hidden per-milestone expected_*.json ground
    truth that ships under each step's tests/ folder.

It is never copied into the task image, so the ground-truth dispositions it
computes stay invisible to the agent. The Java pipeline the agent (and the
oracle) writes must independently reproduce the same three artifacts from the
report, the H2 database, and the config files.

The data is fully deterministic — no randomness, no wall-clock dependence. The
"current" moment is the fixed policy review date.
"""

from __future__ import annotations

import datetime as _dt
import hashlib
from typing import Any

# --------------------------------------------------------------------------
# Policy constants. These are written into the YAML/TOML config (and described,
# in prose, in the narrative report). The decision logic references them; the
# agent must read them out of the validated config, not hard-code them.
# --------------------------------------------------------------------------
REVIEW_DATE = _dt.date(2026, 6, 1)
ROTATION_WINDOW_DAYS = 45
ALLOWED_TLS_VERSIONS = ["TLS1.2", "TLS1.3"]
MTLS_REQUIRED_ENVS = ["prod"]
MIN_RSA_BITS = 2048
MIN_EC_BITS = 256
TRUSTED_ISSUERS = [
    "Mariner Internal CA G2",
    "Mariner Public CA R3",
    "DigiCert Global G3",
]
UNTRUSTED_ISSUER = "Sectigo RSA DV"


def fingerprint(seed: str) -> str:
    """A realistic, deterministic SHA-256 certificate fingerprint string."""
    digest = hashlib.sha256(seed.encode()).hexdigest().upper()
    return ":".join(digest[i : i + 2] for i in range(0, 64, 2))


# --------------------------------------------------------------------------
# The 24-service canonical dataset. Each entry carries everything needed to
# render the DB rows, the narrative waiver register, and to compute the three
# artifacts. ``probe`` is the *latest* (authoritative) captured probe; older
# stale captures are synthesised in build_probe_history() so that any query
# that fails to take the most recent probe per service produces wrong evidence.
#
# By construction each service has at most one protocol-level violation
# (tls / mtls / chain), so the documented decision precedence is unambiguous.
# --------------------------------------------------------------------------
def _svc(
    sid: str,
    name: str,
    env: str,
    owner: str,
    not_after: str,
    key_algo: str,
    key_bits: int,
    issuer: str,
    tls: str,
    verify_ok: bool,
    mtls_presented: bool,
    chain_valid: bool,
    http_status: int,
    waiver: dict[str, Any] | None,
    fp_mismatch: bool = False,
) -> dict[str, Any]:
    return {
        "sid": sid,
        "name": name,
        "env": env,
        "owner": owner,
        "endpoint": f"https://{name.replace('mariner-', '')}.{env}.mariner.internal",
        "cert": {
            "not_after": not_after,
            "key_algo": key_algo,
            "key_bits": key_bits,
            "issuer": issuer,
        },
        "fp_mismatch": fp_mismatch,
        "probe": {
            "tls_version": tls,
            "verify_ok": verify_ok,
            "mtls_presented": mtls_presented,
            "chain_valid": chain_valid,
            "http_status": http_status,
        },
        "waiver": waiver,
    }


def _w(
    wid: str,
    wtype: str,
    status: str,
    scope: str,
    granted_on: str,
    expires_on: str,
    revoked_on: str | None = None,
) -> dict[str, Any]:
    return {
        "id": wid,
        "type": wtype,
        "status": status,
        "scope": scope,
        "granted_on": granted_on,
        "expires_on": expires_on,
        "revoked_on": revoked_on,
    }


_T = True
_F = False

SERVICES: list[dict[str, Any]] = [
    # --- deny: fingerprint mismatch (non-waivable, highest precedence) -------
    _svc("svc-001", "mariner-edge-gateway", "prod", "team-edge",
         "2026-11-20", "RSA", 2048, "Mariner Internal CA G2",
         "TLS1.3", _F, _T, _T, 200, None, fp_mismatch=_T),
    _svc("svc-002", "mariner-auth-broker", "staging", "team-identity",
         "2027-01-10", "RSA", 2048, "Mariner Internal CA G2",
         "TLS1.2", _F, _F, _T, 200,
         _w("WV-2026-002", "tls", "granted", "all", "2026-02-01", "2026-12-01"),
         fp_mismatch=_T),
    # --- deny: waiver expired ------------------------------------------------
    _svc("svc-003", "mariner-billing-api", "prod", "team-billing",
         "2026-12-05", "RSA", 2048, "Mariner Public CA R3",
         "TLS1.0", _F, _T, _T, 200,
         _w("WV-2026-003", "tls", "granted", "all", "2026-01-15", "2026-05-01")),
    _svc("svc-004", "mariner-fulfillment", "prod", "team-logistics",
         "2026-10-30", "EC", 256, "Mariner Internal CA G2",
         "TLS1.2", _T, _F, _T, 200,
         _w("WV-2026-004", "mtls", "granted", "prod", "2026-01-20", "2026-04-30")),
    # --- deny: waiver revoked ------------------------------------------------
    _svc("svc-005", "mariner-telemetry", "prod", "team-observability",
         "2026-11-01", "RSA", 4096, "DigiCert Global G3",
         "TLS1.2", _F, _T, _F, 200,
         _w("WV-2026-005", "chain", "revoked", "all", "2026-02-10", "2026-09-01",
            revoked_on="2026-04-15")),
    _svc("svc-006", "mariner-config-service", "prod", "team-platform",
         "2026-12-20", "RSA", 2048, "Mariner Internal CA G2",
         "TLS1.0", _F, _T, _T, 200,
         _w("WV-2026-006", "tls", "revoked", "all", "2026-01-05", "2026-08-01",
            revoked_on="2026-03-20")),
    # --- deny: protocol violation, no covering waiver ------------------------
    _svc("svc-007", "mariner-search-index", "prod", "team-search",
         "2027-02-01", "RSA", 2048, "Mariner Public CA R3",
         "TLS1.0", _F, _T, _T, 200, None),
    _svc("svc-008", "mariner-dev-sandbox", "dev", "team-devx",
         "2027-03-01", "RSA", 2048, "Mariner Internal CA G2",
         "TLS1.0", _F, _F, _T, 200, None),
    _svc("svc-009", "mariner-payments-gw", "prod", "team-payments",
         "2026-11-15", "EC", 384, "DigiCert Global G3",
         "TLS1.3", _T, _F, _T, 200, None),
    # --- deny: mtls violation, waiver active but out of scope ----------------
    _svc("svc-010", "mariner-partner-api", "prod", "team-partners",
         "2026-12-10", "RSA", 2048, "Mariner Public CA R3",
         "TLS1.2", _T, _F, _T, 200,
         _w("WV-2026-010", "mtls", "granted", "staging", "2026-02-01", "2026-09-01")),
    _svc("svc-011", "mariner-audit-log", "prod", "team-security",
         "2026-11-25", "RSA", 2048, "Mariner Internal CA G2",
         "TLS1.2", _F, _T, _F, 200, None),
    # --- rotate: certificate near expiry -------------------------------------
    _svc("svc-012", "mariner-notifications", "prod", "team-messaging",
         "2026-06-20", "RSA", 2048, "Mariner Internal CA G2",
         "TLS1.2", _T, _T, _T, 200, None),
    _svc("svc-013", "mariner-staging-portal", "staging", "team-web",
         "2026-07-10", "EC", 256, "Mariner Public CA R3",
         "TLS1.3", _T, _F, _T, 200, None),
    _svc("svc-014", "mariner-reporting", "prod", "team-analytics",
         "2026-06-30", "RSA", 2048, "DigiCert Global G3",
         "TLS1.2", _T, _T, _T, 200, None),
    # --- rotate: weak key ----------------------------------------------------
    _svc("svc-015", "mariner-legacy-soap", "prod", "team-integrations",
         "2026-12-31", "RSA", 1024, "Mariner Internal CA G2",
         "TLS1.2", _T, _T, _T, 200, None),
    _svc("svc-016", "mariner-iot-bridge", "dev", "team-iot",
         "2027-01-15", "RSA", 1024, "Mariner Internal CA G2",
         "TLS1.2", _T, _F, _T, 200, None),
    # --- rotate: untrusted issuer --------------------------------------------
    _svc("svc-017", "mariner-cdn-origin", "prod", "team-edge",
         "2026-11-05", "RSA", 2048, UNTRUSTED_ISSUER,
         "TLS1.3", _T, _T, _T, 200, None),
    _svc("svc-018", "mariner-docs-site", "staging", "team-docs",
         "2026-10-20", "EC", 256, UNTRUSTED_ISSUER,
         "TLS1.3", _T, _F, _T, 200, None),
    # --- rotate: covered violation but waiver lapses within window -----------
    _svc("svc-019", "mariner-grpc-mesh", "prod", "team-platform",
         "2026-12-15", "RSA", 2048, "Mariner Internal CA G2",
         "TLS1.0", _F, _T, _T, 200,
         _w("WV-2026-019", "tls", "granted", "all", "2026-03-01", "2026-07-10")),
    _svc("svc-020", "mariner-webhook-relay", "prod", "team-integrations",
         "2026-11-30", "EC", 256, "Mariner Public CA R3",
         "TLS1.2", _T, _F, _T, 200,
         _w("WV-2026-020", "mtls", "granted", "prod", "2026-03-10", "2026-07-05")),
    # --- allow: covered violation, healthy cert, waiver well in date ---------
    _svc("svc-021", "mariner-ml-gateway", "prod", "team-ml",
         "2027-01-20", "RSA", 2048, "DigiCert Global G3",
         "TLS1.0", _F, _T, _T, 200,
         _w("WV-2026-021", "tls", "granted", "all", "2026-02-15", "2026-12-15")),
    _svc("svc-022", "mariner-vault-proxy", "prod", "team-security",
         "2027-02-28", "EC", 384, "Mariner Internal CA G2",
         "TLS1.3", _T, _F, _T, 200,
         _w("WV-2026-022", "mtls", "granted", "prod", "2026-01-10", "2026-11-01")),
    # --- allow: fully compliant ----------------------------------------------
    _svc("svc-023", "mariner-status-page", "prod", "team-sre",
         "2026-12-01", "RSA", 2048, "Mariner Public CA R3",
         "TLS1.3", _T, _T, _T, 200, None),
    _svc("svc-024", "mariner-feature-flags", "staging", "team-platform",
         "2027-03-15", "EC", 256, "Mariner Internal CA G2",
         "TLS1.2", _T, _F, _T, 200, None),
    # --- rotate: lapsing waiver overrides a concurrent hygiene trigger --------
    # Each of the next three has an in-force protocol waiver that lapses within
    # the rotation window AND an independent hygiene defect. Under the amended
    # precedence the lapsing-waiver pull is decided ahead of hygiene, so the
    # governing reason is waiver_expiring_soon, not the hygiene trigger. A reader
    # who applies the naive top-to-bottom order would report the hygiene reason.
    _svc("svc-025", "mariner-batch-scheduler", "prod", "team-batch",
         "2027-01-10", "RSA", 1024, "Mariner Internal CA G2",
         "TLS1.0", _F, _T, _T, 200,
         _w("WV-2026-025", "tls", "granted", "all", "2026-03-05", "2026-07-12")),
    _svc("svc-026", "mariner-export-gateway", "prod", "team-data",
         "2026-06-25", "EC", 256, "Mariner Internal CA G2",
         "TLS1.2", _T, _F, _T, 200,
         _w("WV-2026-026", "mtls", "granted", "prod", "2026-02-20", "2026-07-08")),
    _svc("svc-027", "mariner-archive-store", "prod", "team-storage",
         "2027-02-01", "RSA", 2048, UNTRUSTED_ISSUER,
         "TLS1.0", _F, _T, _T, 200,
         _w("WV-2026-027", "tls", "granted", "all", "2026-03-15", "2026-07-05")),
    # --- deny: in-force waiver of the WRONG TYPE for the violation -----------
    # tls violation, but the only in-force waiver is a mutual-TLS exception. A
    # reader who treats "any active waiver" as cover wrongly allows it.
    _svc("svc-028", "mariner-quota-service", "prod", "team-platform",
         "2027-03-01", "RSA", 2048, "Mariner Internal CA G2",
         "TLS1.0", _F, _T, _T, 200,
         _w("WV-2026-028", "mtls", "granted", "all", "2026-02-01", "2026-12-01")),
    # --- deny: right type but scope does not reach prod ----------------------
    _svc("svc-029", "mariner-rate-limiter", "prod", "team-edge",
         "2027-01-15", "RSA", 2048, "Mariner Public CA R3",
         "TLS1.0", _F, _T, _T, 200,
         _w("WV-2026-029", "tls", "granted", "staging", "2026-02-01", "2026-12-01")),
    # --- rotate (weak_key): covered violation, waiver NOT lapsing ------------
    # The amended precedence does not fire (waiver comfortably in date), so the
    # hygiene trigger governs the reason while waiver_applied stays true.
    _svc("svc-030", "mariner-session-store", "prod", "team-identity",
         "2027-02-01", "RSA", 1024, "Mariner Internal CA G2",
         "TLS1.0", _F, _T, _T, 200,
         _w("WV-2026-030", "tls", "granted", "all", "2026-01-01", "2026-12-20")),
    # --- allow (compliant): in-force waiver lapses soon but excuses NOTHING --
    # No protocol violation exists, so the lapsing-waiver pull has nothing to
    # act on; the soon-to-lapse waiver is not applied and the service is simply
    # compliant.
    _svc("svc-031", "mariner-pref-service", "prod", "team-platform",
         "2027-03-15", "RSA", 2048, "Mariner Internal CA G2",
         "TLS1.3", _T, _T, _T, 200,
         _w("WV-2026-031", "tls", "granted", "all", "2026-02-01", "2026-06-25")),
    # --- rotate (waiver_expiring_soon): chain violation, lapsing chain waiver -
    _svc("svc-032", "mariner-trace-collector", "prod", "team-observability",
         "2027-01-20", "RSA", 2048, "Mariner Internal CA G2",
         "TLS1.3", _T, _T, _F, 200,
         _w("WV-2026-032", "chain", "granted", "all", "2026-03-01", "2026-07-05")),
    # --- allow (active_waiver_ok): covered tls violation on staging ----------
    _svc("svc-033", "mariner-preview-portal", "staging", "team-web",
         "2027-02-28", "EC", 256, "Mariner Internal CA G2",
         "TLS1.0", _F, _F, _T, 200,
         _w("WV-2026-033", "tls", "granted", "all", "2026-01-15", "2026-12-15")),
]


def _date(s: str) -> _dt.date:
    return _dt.date.fromisoformat(s)


def observed_fingerprint(s: dict[str, Any]) -> str:
    """Fingerprint the latest probe captured for the service."""
    base = fingerprint(s["sid"] + "-cert")
    if s["fp_mismatch"]:
        return fingerprint(s["sid"] + "-rogue")
    return base


def cert_fingerprint(s: dict[str, Any]) -> str:
    return fingerprint(s["sid"] + "-cert")


def mtls_required(s: dict[str, Any]) -> bool:
    """Whether the endpoint demanded a client certificate (server-side)."""
    return s["env"] in MTLS_REQUIRED_ENVS


def build_probe_history(s: dict[str, Any]) -> list[dict[str, Any]]:
    """All probe rows for a service, oldest first; the last is authoritative.

    Earlier captures are deliberately stale and differ from the latest in every
    evidence-bearing column, so selecting anything other than the most recent
    capture per service yields incorrect evidence.
    """
    idx = int(s["sid"].split("-")[1])
    latest = s["probe"]
    rows: list[dict[str, Any]] = []

    # One or two stale earlier captures.
    n_stale = 1 + (idx % 2)
    for k in range(n_stale):
        day = 4 + k * 7  # 2026-05-04, 2026-05-11
        rows.append({
            "tool": "httpie" if (idx + k) % 2 else "curl",
            "tls_version": "TLS1.1",
            "verify_ok": False,
            "mtls_required": mtls_required(s),
            "mtls_presented": not latest["mtls_presented"],
            "chain_valid": not latest["chain_valid"],
            "http_status": 526,
            "observed_fingerprint": fingerprint(f"{s['sid']}-stale-{k}"),
            "captured_at": f"2026-05-{day:02d} 08:30:00",
        })

    # The authoritative latest capture, always strictly newest.
    latest_day = 20 + (idx % 9)
    rows.append({
        "tool": "curl" if idx % 2 else "httpie",
        "tls_version": latest["tls_version"],
        "verify_ok": latest["verify_ok"],
        "mtls_required": mtls_required(s),
        "mtls_presented": latest["mtls_presented"],
        "chain_valid": latest["chain_valid"],
        "http_status": latest["http_status"],
        "observed_fingerprint": observed_fingerprint(s),
        "captured_at": f"2026-05-{latest_day:02d} 15:45:00",
    })
    return rows


def latest_probe(s: dict[str, Any]) -> dict[str, Any]:
    return build_probe_history(s)[-1]


# --------------------------------------------------------------------------
# Artifact 1 (milestone 1): the decoded waiver register, purely from narrative.
# status is the narrative disposition (granted / revoked / none); whether a
# granted waiver is still in force is a config-derived question deferred to
# milestone 3.
# --------------------------------------------------------------------------
def waiver_record(s: dict[str, Any]) -> dict[str, Any]:
    w = s["waiver"]
    if w is None:
        return {
            "service_id": s["sid"],
            "service_name": s["name"],
            "waiver_id": None,
            "waiver_type": "none",
            "status": "none",
            "scope": None,
            "granted_on": None,
            "expires_on": None,
            "revoked_on": None,
        }
    return {
        "service_id": s["sid"],
        "service_name": s["name"],
        "waiver_id": w["id"],
        "waiver_type": w["type"],
        "status": w["status"],
        "scope": w["scope"],
        "granted_on": w["granted_on"],
        "expires_on": w["expires_on"],
        "revoked_on": w["revoked_on"],
    }


def waivers_expected() -> list[dict[str, Any]]:
    return [waiver_record(s) for s in sorted(SERVICES, key=lambda x: x["sid"])]


# --------------------------------------------------------------------------
# Artifact 2 (milestone 2): joined evidence — DB inventory + certificate +
# latest probe, merged with the decoded waiver. The cert/probe columns exist
# only in the H2 database, so this artifact cannot be produced without querying
# it (and taking the latest probe per service).
# --------------------------------------------------------------------------
def evidence_record(s: dict[str, Any]) -> dict[str, Any]:
    w = s["waiver"]
    p = latest_probe(s)
    c = s["cert"]
    return {
        "service_id": s["sid"],
        "service_name": s["name"],
        "environment": s["env"],
        "waiver_type": "none" if w is None else w["type"],
        "waiver_status": "none" if w is None else w["status"],
        "waiver_scope": None if w is None else w["scope"],
        "waiver_expires_on": None if w is None else w["expires_on"],
        "cert_fingerprint": cert_fingerprint(s),
        "cert_not_after": c["not_after"],
        "cert_key_algo": c["key_algo"],
        "cert_key_bits": c["key_bits"],
        "cert_issuer": c["issuer"],
        "probe_tls_version": p["tls_version"],
        "probe_verify_ok": p["verify_ok"],
        "probe_mtls_required": p["mtls_required"],
        "probe_mtls_presented": p["mtls_presented"],
        "probe_chain_valid": p["chain_valid"],
        "probe_http_status": p["http_status"],
        "probe_observed_fingerprint": p["observed_fingerprint"],
    }


def evidence_expected() -> list[dict[str, Any]]:
    return [evidence_record(s) for s in sorted(SERVICES, key=lambda x: x["sid"])]


# --------------------------------------------------------------------------
# Artifact 3 (milestone 3): the final disposition per service, applying the
# documented precedence to the joined evidence and the validated policy.
# Returns (disposition, reason_code, waiver_applied).
# --------------------------------------------------------------------------
def decision(s: dict[str, Any]) -> tuple[str, str, bool]:
    c = s["cert"]
    p = latest_probe(s)
    env = s["env"]
    w = s["waiver"]

    w_active = (
        w is not None
        and w["status"] == "granted"
        and _date(w["expires_on"]) >= REVIEW_DATE
    )
    w_expiring_soon = (
        w_active
        and (_date(w["expires_on"]) - REVIEW_DATE).days <= ROTATION_WINDOW_DAYS
    )

    # The single protocol violation (if any), in fixed priority order.
    v_fp = p["observed_fingerprint"] != cert_fingerprint(s)
    violation = None
    if p["tls_version"] not in ALLOWED_TLS_VERSIONS:
        violation = "tls"
    elif env in MTLS_REQUIRED_ENVS and not p["mtls_presented"]:
        violation = "mtls"
    elif not p["chain_valid"]:
        violation = "chain"

    # A. deny checks ------------------------------------------------------
    if v_fp:
        return ("deny", "fingerprint_mismatch", False)

    covered = False
    if violation is not None:
        covered = (
            w_active
            and w["type"] == violation
            and (w["scope"] == "all" or w["scope"] == env)
        )
        if not covered:
            if w is not None and w["type"] == violation and w["status"] == "granted" and not w_active:
                return ("deny", "waiver_expired", False)
            if w is not None and w["type"] == violation and w["status"] == "revoked":
                return ("deny", "waiver_revoked", False)
            reason = {
                "tls": "tls_version_blocked",
                "mtls": "mtls_missing",
                "chain": "chain_invalid",
            }[violation]
            return ("deny", reason, False)

    # B. rotate checks ----------------------------------------------------
    # Amended precedence (this cycle): where a protocol violation is excused by
    # an in-force waiver that itself lapses within the rotation window, that
    # lapsing-waiver pull is determined AHEAD of the hygiene triggers, so it
    # governs the reason even when the certificate is also near expiry,
    # under-strength, or anchored to an untrusted issuer.
    if covered and w_expiring_soon:
        return ("rotate", "waiver_expiring_soon", True)

    waiver_applied = covered
    not_after = _date(c["not_after"])
    window_end = REVIEW_DATE + _dt.timedelta(days=ROTATION_WINDOW_DAYS)
    near_expiry = REVIEW_DATE <= not_after <= window_end
    min_bits = MIN_RSA_BITS if c["key_algo"] == "RSA" else MIN_EC_BITS
    weak_key = c["key_bits"] < min_bits
    untrusted = c["issuer"] not in TRUSTED_ISSUERS

    if near_expiry:
        return ("rotate", "cert_near_expiry", waiver_applied)
    if weak_key:
        return ("rotate", "weak_key", waiver_applied)
    if untrusted:
        return ("rotate", "untrusted_issuer", waiver_applied)

    # C. allow ------------------------------------------------------------
    if covered:
        return ("allow", "active_waiver_ok", True)
    return ("allow", "compliant", False)


def finding_record(s: dict[str, Any]) -> dict[str, Any]:
    disposition, reason_code, waiver_applied = decision(s)
    return {
        "service_id": s["sid"],
        "service_name": s["name"],
        "environment": s["env"],
        "disposition": disposition,
        "reason_code": reason_code,
        "waiver_applied": waiver_applied,
    }


def findings_expected() -> list[dict[str, Any]]:
    return [finding_record(s) for s in sorted(SERVICES, key=lambda x: x["sid"])]


def aggregate_counts() -> dict[str, int]:
    counts = {"allow": 0, "deny": 0, "rotate": 0}
    for f in findings_expected():
        counts[f["disposition"]] += 1
    return counts


if __name__ == "__main__":
    import json

    assert len({s["sid"] for s in SERVICES}) == len(SERVICES), "duplicate sids"
    print("services:", len(SERVICES))
    print("aggregate:", aggregate_counts())
    reasons: dict[str, int] = {}
    for f in findings_expected():
        reasons[f["reason_code"]] = reasons.get(f["reason_code"], 0) + 1
    print("reasons:", json.dumps(reasons, indent=2, sort_keys=True))
