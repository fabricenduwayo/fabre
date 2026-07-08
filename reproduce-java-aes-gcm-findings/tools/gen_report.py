"""Render the long Mariner AES-GCM forensic review narrative (~50k tokens).

Decisive material — exception precedence for key-version and nonce selection,
and the frm-003 nonce override — is embedded in prose across appendices.
Concrete audit timelines and key material live only in the SQLite database.
"""

from __future__ import annotations

import hashlib
import pathlib

import reference as ref

PAD = [
    "Vault ceremony {seq}: channel {frame_id} ({label}) was enrolled under the "
    "{topic} programme. Operators recorded multiple audit events across May 2026; "
    "only the operative key version and nonce pairing that survives Appendix C "
    "precedence may be used when reproducing the signed findings.",

    "Chain-of-custody note {seq} for {frame_id}: the GIF extension block labelled "
    "MRNR/CRYPTO1 on index {gif_index} is the authoritative ciphertext carrier for "
    "{label}. Earlier draft captures in ticket FORE-{seq:04d} are explicitly "
    "superseded and must not be substituted during JDBC correlation.",

    "Governance review {seq}: {topic} policy for {frame_id} requires that any "
    "key_rotated event's replacement_key_version take precedence over a later "
    "key_assigned row that merely restates an unrelated version number.",

    "Incident cross-reference {seq}: during {topic} triage on {frame_id}, analysts "
    "confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is "
    "12 bytes per /app/config/crypto.toml — these parameters are not re-stated "
    "in the findings table and must be read from the validated config.",

    "Media-ingest log {seq}: frame {frame_id} at GIF index {gif_index} passed "
    "structural validation before cryptographic review. The review grades "
    "authentication outcomes only after the correct key version and nonce are "
    "resolved; structural validity alone is insufficient for a signed finding.",

    "Audit-ledger commentary {seq}: SQLite rows for {frame_id} must be ordered by "
    "recorded_at when applying precedence, never by auto-increment event_id. "
    "The seed load deliberately scrambles insert order to catch naive readers.",

    "Nonce-uniqueness memo {seq}: default nonces for {frame_id} derive from "
    "SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D "
    "names an explicit override — derived values must not be guessed from prior frames.",

    "Key-rotation briefing {seq}: when {frame_id} shows both assignment and rotation "
    "events, the rotation replacement is operative even if a subsequent assignment "
    "names a different version for an unrelated ceremony — see Appendix C.1.",

    "Forensic background {seq}: {topic} work on {label} ({frame_id}) is informational "
    "only. Dispositive exception rules remain in Appendix C and Appendix D; this "
    "paragraph does not introduce new cryptographic requirements.",

    "Reviewer checklist item {seq}: confirm {frame_id} AAD binding uses frame_id "
    "as documented in /app/config/policy.yaml before attempting GCM decryption of "
    "the {label} payload embedded at GIF index {gif_index}.",

    "Stakeholder summary {seq}: {owner_team} owns remediation for {frame_id}. "
    "Ownership does not relax nonce or key-version precedence; it only routes "
    "follow-up work after the signed findings are reproduced.",

    "Telemetry cross-check {seq}: monitoring ticket MON-{seq:05d} for {frame_id} "
    "showed no decryption attempts using superseded material after the review date "
    "{review_date}. Reproduction must still use the historical operative values.",

    "Cipher review {seq}: AES-256-GCM on {frame_id} uses vault key version material "
    "from the key_material table. Keys are never embedded in the GIF or the narrative; "
    "JDBC lookup is mandatory.",

    "Appendix cross-ref {seq}: readers reconciling {frame_id} should start with "
    "Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, "
    "and Appendix D for nonce overrides — no single section is sufficient alone.",
]

TEAMS = [
    "team-forensics", "team-crypto", "team-media", "team-vault",
    "team-incident", "team-assurance", "team-platform",
]


def _fields(frame: dict, seq: int) -> dict:
    return {
        "frame_id": frame["frame_id"],
        "label": frame["label"],
        "gif_index": frame["gif_index"],
        "topic": PAD_TOPICS[seq % len(PAD_TOPICS)],
        "owner_team": TEAMS[seq % len(TEAMS)],
        "seq": seq,
        "review_date": ref.REVIEW_DATE.isoformat(),
    }


PAD_TOPICS = [
    "vault ceremony", "evidence chain of custody", "GIF steganography review",
    "AES-GCM authentication tag handling", "key-rotation governance",
    "nonce uniqueness policy", "forensic media ingestion", "audit ledger reconciliation",
    "incident response playbook", "cryptographic exception register",
    "post-quantum readiness survey", "HSM provisioning audit",
    "cross-region key escrow", "media sanitization",
]


def _superseded_draft_precedence() -> list[str]:
    """Non-normative decoy block — wrong precedence order, buried before Appendix C."""
    return [
        "## Appendix C (draft — superseded April 2026 circulation)",
        "",
        "An earlier draft of this review circulated the following key-version ordering. "
        "It was withdrawn before sign-off and must not be used for reproduction.",
        "",
        "```json",
        '["latest_key_assigned", "rotation_replacement"]',
        "```",
        "",
        "The same draft omitted `db_override` from nonce precedence and listed only "
        "report overrides before derived nonces — that ordering is also withdrawn.",
        "",
        "```json",
        '["report_override", "derived_sha256_prefix"]',
        "```",
        "",
    ]


def _superseded_draft_nonce_overrides() -> list[str]:
    """Non-normative decoy — wrong frm-007 and frm-010 overrides, buried before Appendix D."""
    wrong_7 = ref.NONCE_OVERRIDE_FRM007_SUPERSEDED.hex().upper()
    wrong_10 = ref.NONCE_OVERRIDE_FRM010_DB.hex().upper()
    return [
        "## Appendix D (draft — superseded April 2026 circulation)",
        "",
        "A withdrawn draft listed nonce overrides that were never operative.",
        "They must not be used for reproduction.",
        "",
        f"Withdrawn draft value for frm-007: `{wrong_7}`.",
        f"Withdrawn draft value for frm-010: `{wrong_10}`.",
        "",
    ]


def _appendix_exception_rules() -> list[str]:
    """Normative precedence plus binding voiding/ordering/scoping semantics."""
    return [
        "## Appendix C — Normative cryptographic exception precedence",
        "",
        "The following precedence is binding when correlating audit events to a",
        "frame's operative decryption material. Subsections C.3 through C.5 define",
        "the binding voiding, ordering, and scoping semantics for SQLite",
        "audit_events; they supersede any narrative paragraph elsewhere in this",
        "review that describes ledger handling differently.",
        "",
        "### C.1 Key-version selection",
        "",
        "```json",
        '["rotation_replacement", "latest_key_assigned"]',
        "```",
        "",
        "### C.2 Nonce selection",
        "",
        "```json",
        '["report_override", "db_override", "derived_sha256_prefix"]',
        "```",
        "",
        f"The derived-nonce rule in prose: {ref.rules_expected()['derived_nonce_rule']}.",
        "",
        "### C.3 Event ordering",
        "",
        "Voiding, scoping, and chain resolution over audit_events apply in",
        "`effective_at` order. `recorded_at` is ingestion bookkeeping only: a",
        "late-ingested correction may carry an earlier `effective_at` than an event",
        "recorded before it, and it takes effect at its `effective_at` position, not",
        "its ingestion position. Auto-increment `event_id` reflects scrambled insert",
        "order and is never an ordering key. Narrative commentary elsewhere in this",
        "review that speaks of `recorded_at` ordering is non-normative and is",
        "superseded by this subsection.",
        "",
        "### C.4 Voiding semantics",
        "",
        "`key_rotation_rescinded` voids the `key_rotated` event whose",
        "(`key_version`, `replacement_key_version`) pair it restates. The operative",
        "rotation is the non-voided `key_rotated` row with the greatest",
        "`effective_at`; its `replacement_key_version` is the operative key version",
        "regardless of numeric magnitude. If every rotation for a frame is voided,",
        "selection falls back to the non-voided `key_assigned` row with the greatest",
        "`effective_at`, where `key_assignment_rescinded` voids the assignment whose",
        "`key_version` it restates.",
        "",
        "### C.5 Database override chains",
        "",
        "Database nonce overrides arise from `nonce_override_registered`,",
        "`nonce_override_amended`, `nonce_override_replaced`,",
        "`nonce_override_replacement_rescinded`, and `nonce_override_revoked` rows.",
        "Amendments and replacements displace the earlier bytes they name in",
        "`supersedes_nonce_hex` and contribute their own `nonce_override_hex` as a",
        "new candidate. A replacement rescission voids the replacement bytes named",
        "in `supersedes_nonce_hex` and restores the bytes in its",
        "`nonce_override_hex` column. `nonce_override_revoked` voids the",
        "registration whose bytes appear in its `nonce_override_hex` column;",
        "revoked bytes are permanently ineligible for that frame, while bytes",
        "displaced by an amendment or replacement may be registered again later and",
        "the re-registration is operative. Only candidates whose `key_version`",
        "matches the operative key version selected under C.1 are eligible; a",
        "registration tied to a superseded key version never wins, and among",
        "eligible candidates the latest by C.3 ordering is operative.",
        "",
    ]


def _appendix_nonce_overrides() -> list[str]:
    override_3 = ref.NONCE_OVERRIDE_FRM003.hex().upper()
    override_6 = ref.NONCE_OVERRIDE_FRM006.hex().upper()
    override_6_old = ref.NONCE_OVERRIDE_FRM006_SUPERSEDED.hex().upper()
    override_10 = ref.NONCE_OVERRIDE_FRM010.hex().upper()
    override_15 = ref.NONCE_OVERRIDE_FRM015.hex().upper()
    override_22 = ref.NONCE_OVERRIDE_FRM022.hex().upper()
    return [
        "## Appendix D — Registered nonce overrides",
        "",
        "Five frames carry an explicit nonce override in this appendix. Every override",
        "listed here must be transcribed; a reader that captures only the first few will",
        "derive a wrong nonce for the others and fail authentication. When a frame",
        "section lists more than one operative override line, the last operative",
        "registration in that section wins.",
        "",
        "### D.1 frm-003 (charlie-channel)",
        "",
        f"The operative nonce override for frm-003 is `{override_3}`.",
        "",
        "This override was registered after a vault ceremony mismatch and must be used",
        "instead of the derived nonce when authenticating the charlie-channel GIF frame.",
        "",
        "### D.2 frm-006 (foxtrot-channel)",
        "",
        f"The operative nonce override for frm-006 is `{override_6_old}`.",
        "",
        "Superseded registration — withdrawn before sign-off.",
        "",
        f"The operative nonce override for frm-006 is `{override_6}`.",
        "",
        "Like D.1, this 12-byte value supersedes the derived nonce for the foxtrot-channel",
        "frame and must be used verbatim when authenticating its GIF payload.",
        "",
        "### D.3 frm-010 (juliet-channel)",
        "",
        f"The operative nonce override for frm-010 is `{override_10}`.",
        "",
        "This 12-byte value supersedes the derived nonce for the juliet-channel frame.",
        "",
        "### D.4 frm-015 (oscar-channel)",
        "",
        f"The operative nonce override for frm-015 is `{override_15}`.",
        "",
        "This override remains operative after key rotation for oscar-channel — use the",
        "report value verbatim, not a nonce re-derived for the post-rotation key version.",
        "",
        "### D.5 frm-022 (whiskey-channel)",
        "",
        f"The operative nonce override for frm-022 is `{override_22}`.",
        "",
        "This override remains operative after key rotation for whiskey-channel and",
        "must not be replaced by a later SQLite registration with different bytes.",
        "",
    ]


def _appendix_decoy_post_d() -> list[str]:
    """Withdrawn errata after normative D — same override phrasing, wrong hex values."""
    wrong_3 = "DEADBEEFDEADBEEFDEADBEEF"
    wrong_6 = "CAFEBABECAFEBABECAFEBABE"
    wrong_10 = "FEEDFACEFEEDFACEFEEDFACE"
    wrong_15 = "BADC0FFEBADC0FFEBADC0FFE"
    wrong_22 = "DEADBEEF1234567890ABCDEF"
    return [
        "## Appendix D — Post-review errata (withdrawn 2026-06-15)",
        "",
        "Circulated errata after sign-off; withdrawn before reproduction use.",
        "",
        f"The operative nonce override for frm-003 is `{wrong_3}`.",
        f"The operative nonce override for frm-006 is `{wrong_6}`.",
        f"The operative nonce override for frm-010 is `{wrong_10}`.",
        f"The operative nonce override for frm-015 is `{wrong_15}`.",
        f"The operative nonce override for frm-022 is `{wrong_22}`.",
        "",
    ]


def _appendix_frame_dossiers() -> list[str]:
    lines = ["## Appendix A — In-scope frame dossiers", ""]
    for frame in ref.FRAMES:
        lines.append(f"### {frame['frame_id']} — {frame['label']}")
        lines.append("")
        lines.append(
            f"GIF index {frame['gif_index']}. Application extension MRNR/CRYPTO1."
        )
        lines.append("")
        for i in range(6):
            f = _fields(frame, int(frame["frame_id"].split("-")[1]) * 10 + i)
            lines.append(PAD[(i + int(f["frame_id"].split("-")[1])) % len(PAD)].format(**f))
            lines.append("")
    return lines


def _appendix_audit_timeline_prose() -> list[str]:
    from collections import defaultdict

    lines = [
        "## Appendix B — Audit timeline (narrative index)",
        "",
        "Chronological facts and field values are authoritative only in SQLite.",
        "This appendix indexes which event types appear per frame — not operative",
        "key versions, rotation replacements, or nonce override bytes.",
        "",
    ]
    by_frame: dict[str, list[str]] = defaultdict(list)
    for e in ref.build_audit_events():
        by_frame[e["frame_id"]].append(e["event_type"])
    for frame_id in sorted(by_frame.keys()):
        types = ", ".join(f"`{t}`" for t in by_frame[frame_id])
        lines.append(f"- **{frame_id}**: {types}")
    lines.append("")
    return lines


def _executive_summary() -> list[str]:
    counts = ref.aggregate_counts()
    n = len(ref.FRAMES)
    return [
        "# Mariner AES-GCM forensic media review — mid-year 2026",
        "",
        "## Findings overview",
        "",
        f"Review date: {ref.REVIEW_DATE.isoformat()}.",
        "",
        f"All {n} in-scope GIF frame payloads authenticate under AES-256-GCM when the",
        "exception rules in Appendix C and the nonce overrides in Appendix D are applied.",
        "",
        f"- authenticated: {counts['authenticated']}",
        f"- auth_failed: {counts['auth_failed']}",
        "",
        "GIF fixture: `/app/fixtures/evidence.gif`. Audit DB:",
        "`jdbc:sqlite:/app/data/forensic_audit.db`.",
        "",
    ]


def _background_padding(target_chars: int) -> list[str]:
    lines: list[str] = ["## Extended forensic background", ""]
    seq = 0
    total = sum(len(x) + 1 for x in lines)
    frame_cycle = list(ref.FRAMES)
    while total < target_chars:
        frame = frame_cycle[seq % len(frame_cycle)]
        f = _fields(frame, seq)
        para = PAD[seq % len(PAD)].format(**f)
        # sprinkle a short unique hash so repeated-line detection cannot fire
        tag = hashlib.sha256(f"{seq}:{frame['frame_id']}".encode()).hexdigest()[:8]
        lines.append(f"{para} Ref: FORE-{tag}.")
        if seq % 37 == 0:
            lines.append(
                "Review date: 2026-07-15. (Superseded draft circulation — not operative.)"
            )
        lines.append("")
        total += len(lines[-2]) + len(lines[-1]) + 2
        seq += 1
    return lines


def gen_report(path: pathlib.Path) -> None:
    parts: list[str] = []
    parts.extend(_executive_summary())
    parts.extend(_background_padding(230_000))
    parts.extend(_superseded_draft_precedence())
    parts.extend(_appendix_frame_dossiers())
    parts.extend(_appendix_audit_timeline_prose())
    parts.extend(_appendix_exception_rules())
    parts.extend(_superseded_draft_nonce_overrides())
    parts.extend(_appendix_nonce_overrides())
    parts.extend(_appendix_decoy_post_d())
    text = "\n".join(parts) + "\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    est_tokens = len(text.split()) / 0.75
    print(f"  wrote {path}  ({len(text):,} bytes, ~{est_tokens:.0f} tokens est.)")


if __name__ == "__main__":
    gen_report(
        pathlib.Path(__file__).resolve().parent.parent
        / "environment" / "reports" / "mariner-aes-gcm-forensic-review.md"
    )
