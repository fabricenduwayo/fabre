# Mariner AES-GCM forensic media review — mid-year 2026

## Findings overview

Review date: 2026-06-01.

All 22 in-scope GIF frame payloads authenticate under AES-256-GCM when the
exception rules in Appendix C and the nonce overrides in Appendix D are applied.

- authenticated: 22
- auth_failed: 0

GIF fixture: `/app/fixtures/evidence.gif`. Audit DB:
`jdbc:sqlite:/app/data/forensic_audit.db`.

## Extended forensic background

Vault ceremony 0: channel frm-001 (alpha-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-7e501f42.
Review date: 2026-07-15. (Superseded draft circulation — not operative.)

Chain-of-custody note 1 for frm-002: the GIF extension block labelled MRNR/CRYPTO1 on index 1 is the authoritative ciphertext carrier for bravo-channel. Earlier draft captures in ticket FORE-0001 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-bb3e682c.

Governance review 2: GIF steganography review policy for frm-003 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-baa95a03.

Incident cross-reference 3: during AES-GCM authentication tag handling triage on frm-004, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-e462d6ef.

Media-ingest log 4: frame frm-005 at GIF index 5 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-8a1eecc3.

Audit-ledger commentary 5: SQLite rows for frm-006 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-de921fac.

Nonce-uniqueness memo 6: default nonces for frm-007 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-a45ae7ca.

Key-rotation briefing 7: when frm-008 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-59f9c996.

Forensic background 8: incident response playbook work on india-channel (frm-009) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-1a8db3f8.

Reviewer checklist item 9: confirm frm-010 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the juliet-channel payload embedded at GIF index 10. Ref: FORE-49bf5c34.

Stakeholder summary 10: team-vault owns remediation for frm-011. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-d45588e2.

Telemetry cross-check 11: monitoring ticket MON-00011 for frm-012 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-ccbde938.

Cipher review 12: AES-256-GCM on frm-013 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-4a78d777.

Appendix cross-ref 13: readers reconciling frm-014 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-09dc0da0.

Vault ceremony 14: channel frm-015 (oscar-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-2b0826ed.

Chain-of-custody note 15 for frm-016: the GIF extension block labelled MRNR/CRYPTO1 on index 16 is the authoritative ciphertext carrier for papa-channel. Earlier draft captures in ticket FORE-0015 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-64321095.

Governance review 16: GIF steganography review policy for frm-017 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-8b6b8433.

Incident cross-reference 17: during AES-GCM authentication tag handling triage on frm-018, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-7e395856.

Media-ingest log 18: frame frm-019 at GIF index 19 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-2109418e.

Audit-ledger commentary 19: SQLite rows for frm-020 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-13a39e3a.

Nonce-uniqueness memo 20: default nonces for frm-021 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-23a3be67.

Key-rotation briefing 21: when frm-022 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-58806f54.

Forensic background 22: incident response playbook work on alpha-channel (frm-001) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-05407915.

Reviewer checklist item 23: confirm frm-002 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the bravo-channel payload embedded at GIF index 1. Ref: FORE-83a0b0cc.

Stakeholder summary 24: team-vault owns remediation for frm-003. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-d0226189.

Telemetry cross-check 25: monitoring ticket MON-00025 for frm-004 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-8c655f20.

Cipher review 26: AES-256-GCM on frm-005 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-02535b24.

Appendix cross-ref 27: readers reconciling frm-006 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-544d22ce.

Vault ceremony 28: channel frm-007 (golf-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-254f8cc7.

Chain-of-custody note 29 for frm-008: the GIF extension block labelled MRNR/CRYPTO1 on index 8 is the authoritative ciphertext carrier for hotel-channel. Earlier draft captures in ticket FORE-0029 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-a110f40d.

Governance review 30: GIF steganography review policy for frm-009 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-757266ff.

Incident cross-reference 31: during AES-GCM authentication tag handling triage on frm-010, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-4b216d8d.

Media-ingest log 32: frame frm-011 at GIF index 11 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-cd2046b6.

Audit-ledger commentary 33: SQLite rows for frm-012 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-68077bc1.

Nonce-uniqueness memo 34: default nonces for frm-013 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-087397e5.

Key-rotation briefing 35: when frm-014 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-c67c953e.

Forensic background 36: incident response playbook work on oscar-channel (frm-015) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-d4a9687e.

Reviewer checklist item 37: confirm frm-016 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the papa-channel payload embedded at GIF index 16. Ref: FORE-249ec191.
Review date: 2026-07-15. (Superseded draft circulation — not operative.)

Stakeholder summary 38: team-vault owns remediation for frm-017. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-8d210f8d.

Telemetry cross-check 39: monitoring ticket MON-00039 for frm-018 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-998a920a.

Cipher review 40: AES-256-GCM on frm-019 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-db3d1581.

Appendix cross-ref 41: readers reconciling frm-020 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-b728301d.

Vault ceremony 42: channel frm-021 (victor-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-359e28a0.

Chain-of-custody note 43 for frm-022: the GIF extension block labelled MRNR/CRYPTO1 on index 22 is the authoritative ciphertext carrier for whiskey-channel. Earlier draft captures in ticket FORE-0043 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-2a953a68.

Governance review 44: GIF steganography review policy for frm-001 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-9c74644a.

Incident cross-reference 45: during AES-GCM authentication tag handling triage on frm-002, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-552a1eb2.

Media-ingest log 46: frame frm-003 at GIF index 2 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-f0e694b9.

Audit-ledger commentary 47: SQLite rows for frm-004 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-0def2e95.

Nonce-uniqueness memo 48: default nonces for frm-005 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-11aa3dd6.

Key-rotation briefing 49: when frm-006 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-1fe0d266.

Forensic background 50: incident response playbook work on golf-channel (frm-007) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-f2f4bded.

Reviewer checklist item 51: confirm frm-008 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the hotel-channel payload embedded at GIF index 8. Ref: FORE-337a3dd3.

Stakeholder summary 52: team-vault owns remediation for frm-009. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-f572c1c3.

Telemetry cross-check 53: monitoring ticket MON-00053 for frm-010 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-1eefbad2.

Cipher review 54: AES-256-GCM on frm-011 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-b8bae923.

Appendix cross-ref 55: readers reconciling frm-012 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-82210c54.

Vault ceremony 56: channel frm-013 (mike-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-0d3b94e1.

Chain-of-custody note 57 for frm-014: the GIF extension block labelled MRNR/CRYPTO1 on index 14 is the authoritative ciphertext carrier for november-channel. Earlier draft captures in ticket FORE-0057 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-2f01a142.

Governance review 58: GIF steganography review policy for frm-015 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-7d39149e.

Incident cross-reference 59: during AES-GCM authentication tag handling triage on frm-016, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-c13bd9da.

Media-ingest log 60: frame frm-017 at GIF index 17 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-d24a0d9a.

Audit-ledger commentary 61: SQLite rows for frm-018 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-53a8ed37.

Nonce-uniqueness memo 62: default nonces for frm-019 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-85db8645.

Key-rotation briefing 63: when frm-020 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-07863d85.

Forensic background 64: incident response playbook work on victor-channel (frm-021) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-9b0544ae.

Reviewer checklist item 65: confirm frm-022 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the whiskey-channel payload embedded at GIF index 22. Ref: FORE-b9019764.

Stakeholder summary 66: team-vault owns remediation for frm-001. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-6264c8e3.

Telemetry cross-check 67: monitoring ticket MON-00067 for frm-002 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-fc12973a.

Cipher review 68: AES-256-GCM on frm-003 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-cc6a597c.

Appendix cross-ref 69: readers reconciling frm-004 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-b3ce5072.

Vault ceremony 70: channel frm-005 (echo-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-cd7c15c6.

Chain-of-custody note 71 for frm-006: the GIF extension block labelled MRNR/CRYPTO1 on index 6 is the authoritative ciphertext carrier for foxtrot-channel. Earlier draft captures in ticket FORE-0071 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-d85e6e04.

Governance review 72: GIF steganography review policy for frm-007 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-64804ca1.

Incident cross-reference 73: during AES-GCM authentication tag handling triage on frm-008, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-336a707f.

Media-ingest log 74: frame frm-009 at GIF index 9 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-b69fc734.
Review date: 2026-07-15. (Superseded draft circulation — not operative.)

Audit-ledger commentary 75: SQLite rows for frm-010 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-e124566c.

Nonce-uniqueness memo 76: default nonces for frm-011 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-dec15eb8.

Key-rotation briefing 77: when frm-012 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-371dc215.

Forensic background 78: incident response playbook work on mike-channel (frm-013) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-ea03a515.

Reviewer checklist item 79: confirm frm-014 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the november-channel payload embedded at GIF index 14. Ref: FORE-b3268fc3.

Stakeholder summary 80: team-vault owns remediation for frm-015. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-bb230f57.

Telemetry cross-check 81: monitoring ticket MON-00081 for frm-016 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-834eab96.

Cipher review 82: AES-256-GCM on frm-017 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-b6789b64.

Appendix cross-ref 83: readers reconciling frm-018 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-34711571.

Vault ceremony 84: channel frm-019 (tango-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-9b757399.

Chain-of-custody note 85 for frm-020: the GIF extension block labelled MRNR/CRYPTO1 on index 20 is the authoritative ciphertext carrier for uniform-channel. Earlier draft captures in ticket FORE-0085 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-cf23b93b.

Governance review 86: GIF steganography review policy for frm-021 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-0221dcd6.

Incident cross-reference 87: during AES-GCM authentication tag handling triage on frm-022, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-0f45ce48.

Media-ingest log 88: frame frm-001 at GIF index 0 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-94c38590.

Audit-ledger commentary 89: SQLite rows for frm-002 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-d0887721.

Nonce-uniqueness memo 90: default nonces for frm-003 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-4478d9d4.

Key-rotation briefing 91: when frm-004 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-5adf0c56.

Forensic background 92: incident response playbook work on echo-channel (frm-005) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-93d38b06.

Reviewer checklist item 93: confirm frm-006 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the foxtrot-channel payload embedded at GIF index 6. Ref: FORE-cf2d7b56.

Stakeholder summary 94: team-vault owns remediation for frm-007. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-66893743.

Telemetry cross-check 95: monitoring ticket MON-00095 for frm-008 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-557da4e0.

Cipher review 96: AES-256-GCM on frm-009 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-ed55dc86.

Appendix cross-ref 97: readers reconciling frm-010 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-dc23c36f.

Vault ceremony 98: channel frm-011 (kilo-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-bed66fe8.

Chain-of-custody note 99 for frm-012: the GIF extension block labelled MRNR/CRYPTO1 on index 12 is the authoritative ciphertext carrier for lima-channel. Earlier draft captures in ticket FORE-0099 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-997b64ad.

Governance review 100: GIF steganography review policy for frm-013 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-d7449535.

Incident cross-reference 101: during AES-GCM authentication tag handling triage on frm-014, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-300154f6.

Media-ingest log 102: frame frm-015 at GIF index 15 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-1f7c9f76.

Audit-ledger commentary 103: SQLite rows for frm-016 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-fa4ca46f.

Nonce-uniqueness memo 104: default nonces for frm-017 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-8c2f9d11.

Key-rotation briefing 105: when frm-018 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-9ef7cb53.

Forensic background 106: incident response playbook work on tango-channel (frm-019) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-11bd7b14.

Reviewer checklist item 107: confirm frm-020 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the uniform-channel payload embedded at GIF index 20. Ref: FORE-19f32616.

Stakeholder summary 108: team-vault owns remediation for frm-021. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-2d662449.

Telemetry cross-check 109: monitoring ticket MON-00109 for frm-022 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-edbe54ed.

Cipher review 110: AES-256-GCM on frm-001 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-1427cd95.

Appendix cross-ref 111: readers reconciling frm-002 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-0465803d.
Review date: 2026-07-15. (Superseded draft circulation — not operative.)

Vault ceremony 112: channel frm-003 (charlie-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-075cf4f4.

Chain-of-custody note 113 for frm-004: the GIF extension block labelled MRNR/CRYPTO1 on index 4 is the authoritative ciphertext carrier for delta-channel. Earlier draft captures in ticket FORE-0113 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-2e40becd.

Governance review 114: GIF steganography review policy for frm-005 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-0389b64a.

Incident cross-reference 115: during AES-GCM authentication tag handling triage on frm-006, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-8b1f389c.

Media-ingest log 116: frame frm-007 at GIF index 7 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-4c069b16.

Audit-ledger commentary 117: SQLite rows for frm-008 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-3580bd97.

Nonce-uniqueness memo 118: default nonces for frm-009 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-e5629b26.

Key-rotation briefing 119: when frm-010 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-d47a6f7c.

Forensic background 120: incident response playbook work on kilo-channel (frm-011) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-76eedb7c.

Reviewer checklist item 121: confirm frm-012 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the lima-channel payload embedded at GIF index 12. Ref: FORE-12e76ab9.

Stakeholder summary 122: team-vault owns remediation for frm-013. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-abb39b5b.

Telemetry cross-check 123: monitoring ticket MON-00123 for frm-014 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-0ad0b8c2.

Cipher review 124: AES-256-GCM on frm-015 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-2cbfa9e9.

Appendix cross-ref 125: readers reconciling frm-016 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-83d3cd76.

Vault ceremony 126: channel frm-017 (quebec-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-a9b33f90.

Chain-of-custody note 127 for frm-018: the GIF extension block labelled MRNR/CRYPTO1 on index 18 is the authoritative ciphertext carrier for sierra-channel. Earlier draft captures in ticket FORE-0127 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-9e8af13e.

Governance review 128: GIF steganography review policy for frm-019 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-9f72aee6.

Incident cross-reference 129: during AES-GCM authentication tag handling triage on frm-020, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-df510661.

Media-ingest log 130: frame frm-021 at GIF index 21 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-49160f8b.

Audit-ledger commentary 131: SQLite rows for frm-022 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-3b28f9b7.

Nonce-uniqueness memo 132: default nonces for frm-001 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-6adbfdf8.

Key-rotation briefing 133: when frm-002 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-60cebcba.

Forensic background 134: incident response playbook work on charlie-channel (frm-003) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-35417405.

Reviewer checklist item 135: confirm frm-004 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the delta-channel payload embedded at GIF index 4. Ref: FORE-0d8ee2fb.

Stakeholder summary 136: team-vault owns remediation for frm-005. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-f7361f56.

Telemetry cross-check 137: monitoring ticket MON-00137 for frm-006 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-3c7d454d.

Cipher review 138: AES-256-GCM on frm-007 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-9a4514a5.

Appendix cross-ref 139: readers reconciling frm-008 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-584e77b9.

Vault ceremony 140: channel frm-009 (india-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-302e425b.

Chain-of-custody note 141 for frm-010: the GIF extension block labelled MRNR/CRYPTO1 on index 10 is the authoritative ciphertext carrier for juliet-channel. Earlier draft captures in ticket FORE-0141 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-f039553f.

Governance review 142: GIF steganography review policy for frm-011 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-b1bc86d8.

Incident cross-reference 143: during AES-GCM authentication tag handling triage on frm-012, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-2d948191.

Media-ingest log 144: frame frm-013 at GIF index 13 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-e0c4fd92.

Audit-ledger commentary 145: SQLite rows for frm-014 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-acdbf2c3.

Nonce-uniqueness memo 146: default nonces for frm-015 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-8bdc3b55.

Key-rotation briefing 147: when frm-016 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-fd3c8d4e.

Forensic background 148: incident response playbook work on quebec-channel (frm-017) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-ea9c58b5.
Review date: 2026-07-15. (Superseded draft circulation — not operative.)

Reviewer checklist item 149: confirm frm-018 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the sierra-channel payload embedded at GIF index 18. Ref: FORE-10b97ab8.

Stakeholder summary 150: team-vault owns remediation for frm-019. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-c0b4b1ac.

Telemetry cross-check 151: monitoring ticket MON-00151 for frm-020 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-fc965d65.

Cipher review 152: AES-256-GCM on frm-021 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-f96646cf.

Appendix cross-ref 153: readers reconciling frm-022 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-9f7bcb7c.

Vault ceremony 154: channel frm-001 (alpha-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-200bb7de.

Chain-of-custody note 155 for frm-002: the GIF extension block labelled MRNR/CRYPTO1 on index 1 is the authoritative ciphertext carrier for bravo-channel. Earlier draft captures in ticket FORE-0155 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-84766f9a.

Governance review 156: GIF steganography review policy for frm-003 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-837d3563.

Incident cross-reference 157: during AES-GCM authentication tag handling triage on frm-004, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-58fb4bc4.

Media-ingest log 158: frame frm-005 at GIF index 5 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-ec0de97b.

Audit-ledger commentary 159: SQLite rows for frm-006 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-2a9aa316.

Nonce-uniqueness memo 160: default nonces for frm-007 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-b357966c.

Key-rotation briefing 161: when frm-008 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-058e6360.

Forensic background 162: incident response playbook work on india-channel (frm-009) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-674c26fd.

Reviewer checklist item 163: confirm frm-010 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the juliet-channel payload embedded at GIF index 10. Ref: FORE-8084cc34.

Stakeholder summary 164: team-vault owns remediation for frm-011. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-ec014895.

Telemetry cross-check 165: monitoring ticket MON-00165 for frm-012 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-34d652f0.

Cipher review 166: AES-256-GCM on frm-013 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-17c449dc.

Appendix cross-ref 167: readers reconciling frm-014 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-966de700.

Vault ceremony 168: channel frm-015 (oscar-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-537c0a37.

Chain-of-custody note 169 for frm-016: the GIF extension block labelled MRNR/CRYPTO1 on index 16 is the authoritative ciphertext carrier for papa-channel. Earlier draft captures in ticket FORE-0169 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-8a9c29e2.

Governance review 170: GIF steganography review policy for frm-017 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-4776a924.

Incident cross-reference 171: during AES-GCM authentication tag handling triage on frm-018, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-7b834ead.

Media-ingest log 172: frame frm-019 at GIF index 19 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-54174385.

Audit-ledger commentary 173: SQLite rows for frm-020 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-f15d714c.

Nonce-uniqueness memo 174: default nonces for frm-021 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-9122086d.

Key-rotation briefing 175: when frm-022 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-ae425497.

Forensic background 176: incident response playbook work on alpha-channel (frm-001) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-f8ffca1e.

Reviewer checklist item 177: confirm frm-002 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the bravo-channel payload embedded at GIF index 1. Ref: FORE-bfec4834.

Stakeholder summary 178: team-vault owns remediation for frm-003. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-9774d582.

Telemetry cross-check 179: monitoring ticket MON-00179 for frm-004 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-37c85de2.

Cipher review 180: AES-256-GCM on frm-005 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-f644a131.

Appendix cross-ref 181: readers reconciling frm-006 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-a2625c96.

Vault ceremony 182: channel frm-007 (golf-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-21fac9c8.

Chain-of-custody note 183 for frm-008: the GIF extension block labelled MRNR/CRYPTO1 on index 8 is the authoritative ciphertext carrier for hotel-channel. Earlier draft captures in ticket FORE-0183 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-9b3b6d4d.

Governance review 184: GIF steganography review policy for frm-009 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-eb4e380b.

Incident cross-reference 185: during AES-GCM authentication tag handling triage on frm-010, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-8f2e9ba9.
Review date: 2026-07-15. (Superseded draft circulation — not operative.)

Media-ingest log 186: frame frm-011 at GIF index 11 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-45dc78c2.

Audit-ledger commentary 187: SQLite rows for frm-012 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-ec0200bb.

Nonce-uniqueness memo 188: default nonces for frm-013 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-3ae9aa9b.

Key-rotation briefing 189: when frm-014 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-caec9af2.

Forensic background 190: incident response playbook work on oscar-channel (frm-015) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-2d3fc5cc.

Reviewer checklist item 191: confirm frm-016 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the papa-channel payload embedded at GIF index 16. Ref: FORE-4da4b662.

Stakeholder summary 192: team-vault owns remediation for frm-017. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-87495b3b.

Telemetry cross-check 193: monitoring ticket MON-00193 for frm-018 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-111366b9.

Cipher review 194: AES-256-GCM on frm-019 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-dc074c57.

Appendix cross-ref 195: readers reconciling frm-020 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-b4a8ad48.

Vault ceremony 196: channel frm-021 (victor-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-ced982c1.

Chain-of-custody note 197 for frm-022: the GIF extension block labelled MRNR/CRYPTO1 on index 22 is the authoritative ciphertext carrier for whiskey-channel. Earlier draft captures in ticket FORE-0197 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-293b9a92.

Governance review 198: GIF steganography review policy for frm-001 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-5a936412.

Incident cross-reference 199: during AES-GCM authentication tag handling triage on frm-002, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-e687895c.

Media-ingest log 200: frame frm-003 at GIF index 2 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-44450dee.

Audit-ledger commentary 201: SQLite rows for frm-004 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-68ec5282.

Nonce-uniqueness memo 202: default nonces for frm-005 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-3339c0d0.

Key-rotation briefing 203: when frm-006 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-86ac38ac.

Forensic background 204: incident response playbook work on golf-channel (frm-007) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-8a5d0cbc.

Reviewer checklist item 205: confirm frm-008 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the hotel-channel payload embedded at GIF index 8. Ref: FORE-a0bd5113.

Stakeholder summary 206: team-vault owns remediation for frm-009. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-c86b765d.

Telemetry cross-check 207: monitoring ticket MON-00207 for frm-010 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-5f4815b4.

Cipher review 208: AES-256-GCM on frm-011 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-103d718e.

Appendix cross-ref 209: readers reconciling frm-012 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-4be6a77f.

Vault ceremony 210: channel frm-013 (mike-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-c608147b.

Chain-of-custody note 211 for frm-014: the GIF extension block labelled MRNR/CRYPTO1 on index 14 is the authoritative ciphertext carrier for november-channel. Earlier draft captures in ticket FORE-0211 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-9c177718.

Governance review 212: GIF steganography review policy for frm-015 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-121db85e.

Incident cross-reference 213: during AES-GCM authentication tag handling triage on frm-016, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-da394a7e.

Media-ingest log 214: frame frm-017 at GIF index 17 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-dd3a62b0.

Audit-ledger commentary 215: SQLite rows for frm-018 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-902a9003.

Nonce-uniqueness memo 216: default nonces for frm-019 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-4cd5083f.

Key-rotation briefing 217: when frm-020 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-ce78a244.

Forensic background 218: incident response playbook work on victor-channel (frm-021) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-489ac185.

Reviewer checklist item 219: confirm frm-022 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the whiskey-channel payload embedded at GIF index 22. Ref: FORE-d925f6c5.

Stakeholder summary 220: team-vault owns remediation for frm-001. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-2b31afec.

Telemetry cross-check 221: monitoring ticket MON-00221 for frm-002 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-c2e69a98.

Cipher review 222: AES-256-GCM on frm-003 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-6c1eefa4.
Review date: 2026-07-15. (Superseded draft circulation — not operative.)

Appendix cross-ref 223: readers reconciling frm-004 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-49788247.

Vault ceremony 224: channel frm-005 (echo-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-fd6f26d9.

Chain-of-custody note 225 for frm-006: the GIF extension block labelled MRNR/CRYPTO1 on index 6 is the authoritative ciphertext carrier for foxtrot-channel. Earlier draft captures in ticket FORE-0225 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-13fb8038.

Governance review 226: GIF steganography review policy for frm-007 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-9b4d680e.

Incident cross-reference 227: during AES-GCM authentication tag handling triage on frm-008, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-62e5b2e0.

Media-ingest log 228: frame frm-009 at GIF index 9 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-3c6a7324.

Audit-ledger commentary 229: SQLite rows for frm-010 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-9c59ae67.

Nonce-uniqueness memo 230: default nonces for frm-011 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-6034da2c.

Key-rotation briefing 231: when frm-012 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-6c135687.

Forensic background 232: incident response playbook work on mike-channel (frm-013) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-5fe47dad.

Reviewer checklist item 233: confirm frm-014 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the november-channel payload embedded at GIF index 14. Ref: FORE-0be88355.

Stakeholder summary 234: team-vault owns remediation for frm-015. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-cf3e67ef.

Telemetry cross-check 235: monitoring ticket MON-00235 for frm-016 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-eab86cb1.

Cipher review 236: AES-256-GCM on frm-017 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-bbcfbf54.

Appendix cross-ref 237: readers reconciling frm-018 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-e41bd423.

Vault ceremony 238: channel frm-019 (tango-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-cc11964e.

Chain-of-custody note 239 for frm-020: the GIF extension block labelled MRNR/CRYPTO1 on index 20 is the authoritative ciphertext carrier for uniform-channel. Earlier draft captures in ticket FORE-0239 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-93702ce0.

Governance review 240: GIF steganography review policy for frm-021 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-9fbaede5.

Incident cross-reference 241: during AES-GCM authentication tag handling triage on frm-022, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-6be135b3.

Media-ingest log 242: frame frm-001 at GIF index 0 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-6aba3af6.

Audit-ledger commentary 243: SQLite rows for frm-002 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-740a97fe.

Nonce-uniqueness memo 244: default nonces for frm-003 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-15040893.

Key-rotation briefing 245: when frm-004 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-86b38d08.

Forensic background 246: incident response playbook work on echo-channel (frm-005) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-8ca2863b.

Reviewer checklist item 247: confirm frm-006 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the foxtrot-channel payload embedded at GIF index 6. Ref: FORE-76116f44.

Stakeholder summary 248: team-vault owns remediation for frm-007. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-47e817b1.

Telemetry cross-check 249: monitoring ticket MON-00249 for frm-008 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-85e34722.

Cipher review 250: AES-256-GCM on frm-009 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-253ce133.

Appendix cross-ref 251: readers reconciling frm-010 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-3d886a52.

Vault ceremony 252: channel frm-011 (kilo-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-5964add9.

Chain-of-custody note 253 for frm-012: the GIF extension block labelled MRNR/CRYPTO1 on index 12 is the authoritative ciphertext carrier for lima-channel. Earlier draft captures in ticket FORE-0253 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-e36bcb54.

Governance review 254: GIF steganography review policy for frm-013 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-6ed4328d.

Incident cross-reference 255: during AES-GCM authentication tag handling triage on frm-014, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-8d7c9fc5.

Media-ingest log 256: frame frm-015 at GIF index 15 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-e5389ec3.

Audit-ledger commentary 257: SQLite rows for frm-016 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-b5416168.

Nonce-uniqueness memo 258: default nonces for frm-017 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-2409b64e.

Key-rotation briefing 259: when frm-018 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-b1e9fb2c.
Review date: 2026-07-15. (Superseded draft circulation — not operative.)

Forensic background 260: incident response playbook work on tango-channel (frm-019) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-13c71db6.

Reviewer checklist item 261: confirm frm-020 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the uniform-channel payload embedded at GIF index 20. Ref: FORE-8f9e3c81.

Stakeholder summary 262: team-vault owns remediation for frm-021. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-fda0adcc.

Telemetry cross-check 263: monitoring ticket MON-00263 for frm-022 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-6bb08440.

Cipher review 264: AES-256-GCM on frm-001 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-ced28635.

Appendix cross-ref 265: readers reconciling frm-002 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-c6f13d7b.

Vault ceremony 266: channel frm-003 (charlie-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-ea8f27e0.

Chain-of-custody note 267 for frm-004: the GIF extension block labelled MRNR/CRYPTO1 on index 4 is the authoritative ciphertext carrier for delta-channel. Earlier draft captures in ticket FORE-0267 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-31b0d23a.

Governance review 268: GIF steganography review policy for frm-005 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-b6ab10bf.

Incident cross-reference 269: during AES-GCM authentication tag handling triage on frm-006, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-c256b4ca.

Media-ingest log 270: frame frm-007 at GIF index 7 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-f093a99e.

Audit-ledger commentary 271: SQLite rows for frm-008 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-ee6acaf5.

Nonce-uniqueness memo 272: default nonces for frm-009 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-1b77549a.

Key-rotation briefing 273: when frm-010 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-b8d06d61.

Forensic background 274: incident response playbook work on kilo-channel (frm-011) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-38fc4bdd.

Reviewer checklist item 275: confirm frm-012 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the lima-channel payload embedded at GIF index 12. Ref: FORE-e0e7e79f.

Stakeholder summary 276: team-vault owns remediation for frm-013. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-db4d53be.

Telemetry cross-check 277: monitoring ticket MON-00277 for frm-014 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-234cfb32.

Cipher review 278: AES-256-GCM on frm-015 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-364f41b5.

Appendix cross-ref 279: readers reconciling frm-016 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-4b700508.

Vault ceremony 280: channel frm-017 (quebec-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-b3d795a0.

Chain-of-custody note 281 for frm-018: the GIF extension block labelled MRNR/CRYPTO1 on index 18 is the authoritative ciphertext carrier for sierra-channel. Earlier draft captures in ticket FORE-0281 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-890293fa.

Governance review 282: GIF steganography review policy for frm-019 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-57f8a182.

Incident cross-reference 283: during AES-GCM authentication tag handling triage on frm-020, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-23f8f475.

Media-ingest log 284: frame frm-021 at GIF index 21 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-54ddbb12.

Audit-ledger commentary 285: SQLite rows for frm-022 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-605c56cd.

Nonce-uniqueness memo 286: default nonces for frm-001 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-f678319b.

Key-rotation briefing 287: when frm-002 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-d9ab64df.

Forensic background 288: incident response playbook work on charlie-channel (frm-003) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-2a588ad4.

Reviewer checklist item 289: confirm frm-004 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the delta-channel payload embedded at GIF index 4. Ref: FORE-3dbb28b3.

Stakeholder summary 290: team-vault owns remediation for frm-005. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-76477e93.

Telemetry cross-check 291: monitoring ticket MON-00291 for frm-006 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-0f10f549.

Cipher review 292: AES-256-GCM on frm-007 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-cdaba704.

Appendix cross-ref 293: readers reconciling frm-008 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-94e89aa0.

Vault ceremony 294: channel frm-009 (india-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-ddf68c36.

Chain-of-custody note 295 for frm-010: the GIF extension block labelled MRNR/CRYPTO1 on index 10 is the authoritative ciphertext carrier for juliet-channel. Earlier draft captures in ticket FORE-0295 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-16421cc3.

Governance review 296: GIF steganography review policy for frm-011 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-2cfd7821.
Review date: 2026-07-15. (Superseded draft circulation — not operative.)

Incident cross-reference 297: during AES-GCM authentication tag handling triage on frm-012, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-d577c571.

Media-ingest log 298: frame frm-013 at GIF index 13 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-30de0971.

Audit-ledger commentary 299: SQLite rows for frm-014 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-fba903e3.

Nonce-uniqueness memo 300: default nonces for frm-015 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-d3ce1f24.

Key-rotation briefing 301: when frm-016 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-b6ba7f9f.

Forensic background 302: incident response playbook work on quebec-channel (frm-017) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-50109947.

Reviewer checklist item 303: confirm frm-018 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the sierra-channel payload embedded at GIF index 18. Ref: FORE-f9224ca5.

Stakeholder summary 304: team-vault owns remediation for frm-019. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-e0d3f612.

Telemetry cross-check 305: monitoring ticket MON-00305 for frm-020 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-3568cca8.

Cipher review 306: AES-256-GCM on frm-021 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-2cb939aa.

Appendix cross-ref 307: readers reconciling frm-022 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-07e7f541.

Vault ceremony 308: channel frm-001 (alpha-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-4c56ac6e.

Chain-of-custody note 309 for frm-002: the GIF extension block labelled MRNR/CRYPTO1 on index 1 is the authoritative ciphertext carrier for bravo-channel. Earlier draft captures in ticket FORE-0309 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-1e78d0ec.

Governance review 310: GIF steganography review policy for frm-003 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-6fb0fcae.

Incident cross-reference 311: during AES-GCM authentication tag handling triage on frm-004, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-9ecb13b9.

Media-ingest log 312: frame frm-005 at GIF index 5 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-3622b1b2.

Audit-ledger commentary 313: SQLite rows for frm-006 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-e897d33f.

Nonce-uniqueness memo 314: default nonces for frm-007 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-ba50cd60.

Key-rotation briefing 315: when frm-008 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-6ec476e7.

Forensic background 316: incident response playbook work on india-channel (frm-009) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-2b2d291f.

Reviewer checklist item 317: confirm frm-010 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the juliet-channel payload embedded at GIF index 10. Ref: FORE-87ff49a0.

Stakeholder summary 318: team-vault owns remediation for frm-011. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-2ab223cc.

Telemetry cross-check 319: monitoring ticket MON-00319 for frm-012 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-aeaedf5c.

Cipher review 320: AES-256-GCM on frm-013 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-cf24a86e.

Appendix cross-ref 321: readers reconciling frm-014 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-938eb305.

Vault ceremony 322: channel frm-015 (oscar-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-48c629a5.

Chain-of-custody note 323 for frm-016: the GIF extension block labelled MRNR/CRYPTO1 on index 16 is the authoritative ciphertext carrier for papa-channel. Earlier draft captures in ticket FORE-0323 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-9e43c7ad.

Governance review 324: GIF steganography review policy for frm-017 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-8c438e37.

Incident cross-reference 325: during AES-GCM authentication tag handling triage on frm-018, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-724b66a4.

Media-ingest log 326: frame frm-019 at GIF index 19 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-c36a8444.

Audit-ledger commentary 327: SQLite rows for frm-020 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-5d80f5a8.

Nonce-uniqueness memo 328: default nonces for frm-021 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-e492813f.

Key-rotation briefing 329: when frm-022 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-f291c793.

Forensic background 330: incident response playbook work on alpha-channel (frm-001) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-fabef2c2.

Reviewer checklist item 331: confirm frm-002 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the bravo-channel payload embedded at GIF index 1. Ref: FORE-a92b743d.

Stakeholder summary 332: team-vault owns remediation for frm-003. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-64998ad0.

Telemetry cross-check 333: monitoring ticket MON-00333 for frm-004 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-89457321.
Review date: 2026-07-15. (Superseded draft circulation — not operative.)

Cipher review 334: AES-256-GCM on frm-005 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-f38b69bd.

Appendix cross-ref 335: readers reconciling frm-006 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-42236610.

Vault ceremony 336: channel frm-007 (golf-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-3fb30fa4.

Chain-of-custody note 337 for frm-008: the GIF extension block labelled MRNR/CRYPTO1 on index 8 is the authoritative ciphertext carrier for hotel-channel. Earlier draft captures in ticket FORE-0337 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-2c7afb53.

Governance review 338: GIF steganography review policy for frm-009 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-ac20f739.

Incident cross-reference 339: during AES-GCM authentication tag handling triage on frm-010, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-86ae4568.

Media-ingest log 340: frame frm-011 at GIF index 11 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-82ade0bb.

Audit-ledger commentary 341: SQLite rows for frm-012 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-3fb4957a.

Nonce-uniqueness memo 342: default nonces for frm-013 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-643bb56b.

Key-rotation briefing 343: when frm-014 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-1f5f21f7.

Forensic background 344: incident response playbook work on oscar-channel (frm-015) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-003a7e79.

Reviewer checklist item 345: confirm frm-016 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the papa-channel payload embedded at GIF index 16. Ref: FORE-7cefcedb.

Stakeholder summary 346: team-vault owns remediation for frm-017. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-a8b2ff82.

Telemetry cross-check 347: monitoring ticket MON-00347 for frm-018 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-45fac684.

Cipher review 348: AES-256-GCM on frm-019 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-83a6c187.

Appendix cross-ref 349: readers reconciling frm-020 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-03e9f77a.

Vault ceremony 350: channel frm-021 (victor-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-b8d25448.

Chain-of-custody note 351 for frm-022: the GIF extension block labelled MRNR/CRYPTO1 on index 22 is the authoritative ciphertext carrier for whiskey-channel. Earlier draft captures in ticket FORE-0351 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-a78efe9f.

Governance review 352: GIF steganography review policy for frm-001 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-911efc46.

Incident cross-reference 353: during AES-GCM authentication tag handling triage on frm-002, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-e89d24de.

Media-ingest log 354: frame frm-003 at GIF index 2 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-172e54f3.

Audit-ledger commentary 355: SQLite rows for frm-004 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-8284d0e0.

Nonce-uniqueness memo 356: default nonces for frm-005 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-c444267c.

Key-rotation briefing 357: when frm-006 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-0b07fede.

Forensic background 358: incident response playbook work on golf-channel (frm-007) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-b93676b5.

Reviewer checklist item 359: confirm frm-008 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the hotel-channel payload embedded at GIF index 8. Ref: FORE-f8f2233c.

Stakeholder summary 360: team-vault owns remediation for frm-009. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-d339d984.

Telemetry cross-check 361: monitoring ticket MON-00361 for frm-010 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-062f74b4.

Cipher review 362: AES-256-GCM on frm-011 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-b48aea82.

Appendix cross-ref 363: readers reconciling frm-012 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-cbadefad.

Vault ceremony 364: channel frm-013 (mike-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-828b7f77.

Chain-of-custody note 365 for frm-014: the GIF extension block labelled MRNR/CRYPTO1 on index 14 is the authoritative ciphertext carrier for november-channel. Earlier draft captures in ticket FORE-0365 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-28dab034.

Governance review 366: GIF steganography review policy for frm-015 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-202ed88e.

Incident cross-reference 367: during AES-GCM authentication tag handling triage on frm-016, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-ca064bb0.

Media-ingest log 368: frame frm-017 at GIF index 17 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-1a721700.

Audit-ledger commentary 369: SQLite rows for frm-018 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-e07e941c.

Nonce-uniqueness memo 370: default nonces for frm-019 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-0f47ba0c.
Review date: 2026-07-15. (Superseded draft circulation — not operative.)

Key-rotation briefing 371: when frm-020 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-91db0b15.

Forensic background 372: incident response playbook work on victor-channel (frm-021) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-b996cb98.

Reviewer checklist item 373: confirm frm-022 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the whiskey-channel payload embedded at GIF index 22. Ref: FORE-69bc459f.

Stakeholder summary 374: team-vault owns remediation for frm-001. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-6e7e6a15.

Telemetry cross-check 375: monitoring ticket MON-00375 for frm-002 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-fc19829e.

Cipher review 376: AES-256-GCM on frm-003 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-9ce99627.

Appendix cross-ref 377: readers reconciling frm-004 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-0624b78b.

Vault ceremony 378: channel frm-005 (echo-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-b66e7022.

Chain-of-custody note 379 for frm-006: the GIF extension block labelled MRNR/CRYPTO1 on index 6 is the authoritative ciphertext carrier for foxtrot-channel. Earlier draft captures in ticket FORE-0379 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-3ced4d96.

Governance review 380: GIF steganography review policy for frm-007 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-b44214ae.

Incident cross-reference 381: during AES-GCM authentication tag handling triage on frm-008, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-bbb8e548.

Media-ingest log 382: frame frm-009 at GIF index 9 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-0488b110.

Audit-ledger commentary 383: SQLite rows for frm-010 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-bb2186eb.

Nonce-uniqueness memo 384: default nonces for frm-011 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-13903ccb.

Key-rotation briefing 385: when frm-012 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-7b89822d.

Forensic background 386: incident response playbook work on mike-channel (frm-013) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-fe2ef5ab.

Reviewer checklist item 387: confirm frm-014 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the november-channel payload embedded at GIF index 14. Ref: FORE-372465df.

Stakeholder summary 388: team-vault owns remediation for frm-015. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-15d5ff8f.

Telemetry cross-check 389: monitoring ticket MON-00389 for frm-016 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-6d444bac.

Cipher review 390: AES-256-GCM on frm-017 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-a9c04c2c.

Appendix cross-ref 391: readers reconciling frm-018 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-99900e49.

Vault ceremony 392: channel frm-019 (tango-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-46d365fb.

Chain-of-custody note 393 for frm-020: the GIF extension block labelled MRNR/CRYPTO1 on index 20 is the authoritative ciphertext carrier for uniform-channel. Earlier draft captures in ticket FORE-0393 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-10e6736e.

Governance review 394: GIF steganography review policy for frm-021 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-36a7e78f.

Incident cross-reference 395: during AES-GCM authentication tag handling triage on frm-022, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-8470f76c.

Media-ingest log 396: frame frm-001 at GIF index 0 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-e23b3dc3.

Audit-ledger commentary 397: SQLite rows for frm-002 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-31e6f644.

Nonce-uniqueness memo 398: default nonces for frm-003 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-355d4d70.

Key-rotation briefing 399: when frm-004 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-7fa49b42.

Forensic background 400: incident response playbook work on echo-channel (frm-005) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-3bf99fd1.

Reviewer checklist item 401: confirm frm-006 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the foxtrot-channel payload embedded at GIF index 6. Ref: FORE-7bfc6453.

Stakeholder summary 402: team-vault owns remediation for frm-007. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-878d2b90.

Telemetry cross-check 403: monitoring ticket MON-00403 for frm-008 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-c263bd45.

Cipher review 404: AES-256-GCM on frm-009 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-550ba733.

Appendix cross-ref 405: readers reconciling frm-010 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-55fa47d2.

Vault ceremony 406: channel frm-011 (kilo-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-3d50d97e.

Chain-of-custody note 407 for frm-012: the GIF extension block labelled MRNR/CRYPTO1 on index 12 is the authoritative ciphertext carrier for lima-channel. Earlier draft captures in ticket FORE-0407 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-1f7ccaa2.
Review date: 2026-07-15. (Superseded draft circulation — not operative.)

Governance review 408: GIF steganography review policy for frm-013 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-628f77ad.

Incident cross-reference 409: during AES-GCM authentication tag handling triage on frm-014, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-d1b527ad.

Media-ingest log 410: frame frm-015 at GIF index 15 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-4524690f.

Audit-ledger commentary 411: SQLite rows for frm-016 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-b6ec1643.

Nonce-uniqueness memo 412: default nonces for frm-017 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-31ead5c7.

Key-rotation briefing 413: when frm-018 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-0e147a63.

Forensic background 414: incident response playbook work on tango-channel (frm-019) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-45b6053d.

Reviewer checklist item 415: confirm frm-020 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the uniform-channel payload embedded at GIF index 20. Ref: FORE-08ba1f35.

Stakeholder summary 416: team-vault owns remediation for frm-021. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-aa7f46cc.

Telemetry cross-check 417: monitoring ticket MON-00417 for frm-022 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-48b75747.

Cipher review 418: AES-256-GCM on frm-001 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-4e1d9591.

Appendix cross-ref 419: readers reconciling frm-002 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-f51c7db6.

Vault ceremony 420: channel frm-003 (charlie-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-5ee1a420.

Chain-of-custody note 421 for frm-004: the GIF extension block labelled MRNR/CRYPTO1 on index 4 is the authoritative ciphertext carrier for delta-channel. Earlier draft captures in ticket FORE-0421 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-c5d3600e.

Governance review 422: GIF steganography review policy for frm-005 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-cc5fae1b.

Incident cross-reference 423: during AES-GCM authentication tag handling triage on frm-006, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-503d50ea.

Media-ingest log 424: frame frm-007 at GIF index 7 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-ca29d14c.

Audit-ledger commentary 425: SQLite rows for frm-008 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-5cf1a047.

Nonce-uniqueness memo 426: default nonces for frm-009 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-2d303fd7.

Key-rotation briefing 427: when frm-010 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-0187c65e.

Forensic background 428: incident response playbook work on kilo-channel (frm-011) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-92c40d44.

Reviewer checklist item 429: confirm frm-012 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the lima-channel payload embedded at GIF index 12. Ref: FORE-6c330085.

Stakeholder summary 430: team-vault owns remediation for frm-013. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-0dd1cd7f.

Telemetry cross-check 431: monitoring ticket MON-00431 for frm-014 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-30059427.

Cipher review 432: AES-256-GCM on frm-015 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-bfef2082.

Appendix cross-ref 433: readers reconciling frm-016 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-848a07eb.

Vault ceremony 434: channel frm-017 (quebec-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-171cec47.

Chain-of-custody note 435 for frm-018: the GIF extension block labelled MRNR/CRYPTO1 on index 18 is the authoritative ciphertext carrier for sierra-channel. Earlier draft captures in ticket FORE-0435 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-3799113e.

Governance review 436: GIF steganography review policy for frm-019 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-8cca332a.

Incident cross-reference 437: during AES-GCM authentication tag handling triage on frm-020, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-0200423f.

Media-ingest log 438: frame frm-021 at GIF index 21 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-8e05a88a.

Audit-ledger commentary 439: SQLite rows for frm-022 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-93c8fe15.

Nonce-uniqueness memo 440: default nonces for frm-001 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-1fc6edfb.

Key-rotation briefing 441: when frm-002 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-ea1c51c0.

Forensic background 442: incident response playbook work on charlie-channel (frm-003) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-39a51687.

Reviewer checklist item 443: confirm frm-004 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the delta-channel payload embedded at GIF index 4. Ref: FORE-9ac39923.

Stakeholder summary 444: team-vault owns remediation for frm-005. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-02a6a0ef.
Review date: 2026-07-15. (Superseded draft circulation — not operative.)

Telemetry cross-check 445: monitoring ticket MON-00445 for frm-006 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-81ab55d2.

Cipher review 446: AES-256-GCM on frm-007 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-29f707a8.

Appendix cross-ref 447: readers reconciling frm-008 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-9fd5dd59.

Vault ceremony 448: channel frm-009 (india-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-cc85e5ed.

Chain-of-custody note 449 for frm-010: the GIF extension block labelled MRNR/CRYPTO1 on index 10 is the authoritative ciphertext carrier for juliet-channel. Earlier draft captures in ticket FORE-0449 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-47316909.

Governance review 450: GIF steganography review policy for frm-011 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-b0bae382.

Incident cross-reference 451: during AES-GCM authentication tag handling triage on frm-012, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-9bd26467.

Media-ingest log 452: frame frm-013 at GIF index 13 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-78f06a95.

Audit-ledger commentary 453: SQLite rows for frm-014 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-9d1319d5.

Nonce-uniqueness memo 454: default nonces for frm-015 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-6ec3e3a8.

Key-rotation briefing 455: when frm-016 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-accc8acd.

Forensic background 456: incident response playbook work on quebec-channel (frm-017) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-506d261a.

Reviewer checklist item 457: confirm frm-018 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the sierra-channel payload embedded at GIF index 18. Ref: FORE-4b5028c6.

Stakeholder summary 458: team-vault owns remediation for frm-019. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-76079305.

Telemetry cross-check 459: monitoring ticket MON-00459 for frm-020 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-e8c82b84.

Cipher review 460: AES-256-GCM on frm-021 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-d1904595.

Appendix cross-ref 461: readers reconciling frm-022 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-6e5ddd95.

Vault ceremony 462: channel frm-001 (alpha-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-bdd1c96f.

Chain-of-custody note 463 for frm-002: the GIF extension block labelled MRNR/CRYPTO1 on index 1 is the authoritative ciphertext carrier for bravo-channel. Earlier draft captures in ticket FORE-0463 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-6d76ccb8.

Governance review 464: GIF steganography review policy for frm-003 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-b52b8c26.

Incident cross-reference 465: during AES-GCM authentication tag handling triage on frm-004, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-376922ef.

Media-ingest log 466: frame frm-005 at GIF index 5 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-3b8ca1f4.

Audit-ledger commentary 467: SQLite rows for frm-006 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-c79eb279.

Nonce-uniqueness memo 468: default nonces for frm-007 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-a075c8a2.

Key-rotation briefing 469: when frm-008 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-a6d074ef.

Forensic background 470: incident response playbook work on india-channel (frm-009) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-bd39daa0.

Reviewer checklist item 471: confirm frm-010 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the juliet-channel payload embedded at GIF index 10. Ref: FORE-4c6ee728.

Stakeholder summary 472: team-vault owns remediation for frm-011. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-94cb0d64.

Telemetry cross-check 473: monitoring ticket MON-00473 for frm-012 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-3e9d1f07.

Cipher review 474: AES-256-GCM on frm-013 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-eb3269b3.

Appendix cross-ref 475: readers reconciling frm-014 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-0ab239fd.

Vault ceremony 476: channel frm-015 (oscar-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-25923fb0.

Chain-of-custody note 477 for frm-016: the GIF extension block labelled MRNR/CRYPTO1 on index 16 is the authoritative ciphertext carrier for papa-channel. Earlier draft captures in ticket FORE-0477 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-9bbb3262.

Governance review 478: GIF steganography review policy for frm-017 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-bed20dce.

Incident cross-reference 479: during AES-GCM authentication tag handling triage on frm-018, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-7d8b5714.

Media-ingest log 480: frame frm-019 at GIF index 19 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-9ea9eac6.

Audit-ledger commentary 481: SQLite rows for frm-020 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-eacf1bfe.
Review date: 2026-07-15. (Superseded draft circulation — not operative.)

Nonce-uniqueness memo 482: default nonces for frm-021 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-a44562b8.

Key-rotation briefing 483: when frm-022 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-d6903441.

Forensic background 484: incident response playbook work on alpha-channel (frm-001) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-e6e7d7fd.

Reviewer checklist item 485: confirm frm-002 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the bravo-channel payload embedded at GIF index 1. Ref: FORE-84716821.

Stakeholder summary 486: team-vault owns remediation for frm-003. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-1a38229e.

Telemetry cross-check 487: monitoring ticket MON-00487 for frm-004 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-1b4ff065.

Cipher review 488: AES-256-GCM on frm-005 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-d3df2aff.

Appendix cross-ref 489: readers reconciling frm-006 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-ed692296.

Vault ceremony 490: channel frm-007 (golf-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-3a49677e.

Chain-of-custody note 491 for frm-008: the GIF extension block labelled MRNR/CRYPTO1 on index 8 is the authoritative ciphertext carrier for hotel-channel. Earlier draft captures in ticket FORE-0491 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-88cce05f.

Governance review 492: GIF steganography review policy for frm-009 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-831359bd.

Incident cross-reference 493: during AES-GCM authentication tag handling triage on frm-010, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-7a7bf3ae.

Media-ingest log 494: frame frm-011 at GIF index 11 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-cd85a968.

Audit-ledger commentary 495: SQLite rows for frm-012 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-c9a80c09.

Nonce-uniqueness memo 496: default nonces for frm-013 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-4a6aebc6.

Key-rotation briefing 497: when frm-014 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-220462b8.

Forensic background 498: incident response playbook work on oscar-channel (frm-015) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-74d55164.

Reviewer checklist item 499: confirm frm-016 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the papa-channel payload embedded at GIF index 16. Ref: FORE-45eaf6fe.

Stakeholder summary 500: team-vault owns remediation for frm-017. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-f3714bc1.

Telemetry cross-check 501: monitoring ticket MON-00501 for frm-018 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-8369d839.

Cipher review 502: AES-256-GCM on frm-019 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-0e5ebf60.

Appendix cross-ref 503: readers reconciling frm-020 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-c7b17516.

Vault ceremony 504: channel frm-021 (victor-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-87ffa0a8.

Chain-of-custody note 505 for frm-022: the GIF extension block labelled MRNR/CRYPTO1 on index 22 is the authoritative ciphertext carrier for whiskey-channel. Earlier draft captures in ticket FORE-0505 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-8f74856e.

Governance review 506: GIF steganography review policy for frm-001 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-64cfb8e7.

Incident cross-reference 507: during AES-GCM authentication tag handling triage on frm-002, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-1927957a.

Media-ingest log 508: frame frm-003 at GIF index 2 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-9869fc27.

Audit-ledger commentary 509: SQLite rows for frm-004 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-8b0ea964.

Nonce-uniqueness memo 510: default nonces for frm-005 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-8d5ed265.

Key-rotation briefing 511: when frm-006 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-e0918776.

Forensic background 512: incident response playbook work on golf-channel (frm-007) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-b8ff9cf6.

Reviewer checklist item 513: confirm frm-008 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the hotel-channel payload embedded at GIF index 8. Ref: FORE-4bbffa9d.

Stakeholder summary 514: team-vault owns remediation for frm-009. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-3acb1849.

Telemetry cross-check 515: monitoring ticket MON-00515 for frm-010 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-81c9614f.

Cipher review 516: AES-256-GCM on frm-011 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-4df2fbf5.

Appendix cross-ref 517: readers reconciling frm-012 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-41f175a5.

Vault ceremony 518: channel frm-013 (mike-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-3235fc4e.
Review date: 2026-07-15. (Superseded draft circulation — not operative.)

Chain-of-custody note 519 for frm-014: the GIF extension block labelled MRNR/CRYPTO1 on index 14 is the authoritative ciphertext carrier for november-channel. Earlier draft captures in ticket FORE-0519 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-573ff546.

Governance review 520: GIF steganography review policy for frm-015 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-688c15ba.

Incident cross-reference 521: during AES-GCM authentication tag handling triage on frm-016, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-6db9e8f2.

Media-ingest log 522: frame frm-017 at GIF index 17 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-c3e01a7d.

Audit-ledger commentary 523: SQLite rows for frm-018 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-202667a3.

Nonce-uniqueness memo 524: default nonces for frm-019 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-2c2576c5.

Key-rotation briefing 525: when frm-020 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-da3b9753.

Forensic background 526: incident response playbook work on victor-channel (frm-021) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-4a39c5b7.

Reviewer checklist item 527: confirm frm-022 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the whiskey-channel payload embedded at GIF index 22. Ref: FORE-38211d30.

Stakeholder summary 528: team-vault owns remediation for frm-001. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-8873e5b9.

Telemetry cross-check 529: monitoring ticket MON-00529 for frm-002 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-153178e0.

Cipher review 530: AES-256-GCM on frm-003 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-bc24e9ad.

Appendix cross-ref 531: readers reconciling frm-004 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-ad8bdb0a.

Vault ceremony 532: channel frm-005 (echo-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-566b2c6d.

Chain-of-custody note 533 for frm-006: the GIF extension block labelled MRNR/CRYPTO1 on index 6 is the authoritative ciphertext carrier for foxtrot-channel. Earlier draft captures in ticket FORE-0533 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-0df1e6e5.

Governance review 534: GIF steganography review policy for frm-007 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-ef4e7acc.

Incident cross-reference 535: during AES-GCM authentication tag handling triage on frm-008, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-133ba457.

Media-ingest log 536: frame frm-009 at GIF index 9 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-874c5b5a.

Audit-ledger commentary 537: SQLite rows for frm-010 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-a0de06d7.

Nonce-uniqueness memo 538: default nonces for frm-011 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-d3c04f4f.

Key-rotation briefing 539: when frm-012 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-e82849ca.

Forensic background 540: incident response playbook work on mike-channel (frm-013) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-74eba2bc.

Reviewer checklist item 541: confirm frm-014 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the november-channel payload embedded at GIF index 14. Ref: FORE-fdeb8c24.

Stakeholder summary 542: team-vault owns remediation for frm-015. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-14caaba5.

Telemetry cross-check 543: monitoring ticket MON-00543 for frm-016 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-1af1e5e1.

Cipher review 544: AES-256-GCM on frm-017 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-45c8a93b.

Appendix cross-ref 545: readers reconciling frm-018 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-c0226668.

Vault ceremony 546: channel frm-019 (tango-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-d76ee597.

Chain-of-custody note 547 for frm-020: the GIF extension block labelled MRNR/CRYPTO1 on index 20 is the authoritative ciphertext carrier for uniform-channel. Earlier draft captures in ticket FORE-0547 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-4c77c07a.

Governance review 548: GIF steganography review policy for frm-021 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-78b31f36.

Incident cross-reference 549: during AES-GCM authentication tag handling triage on frm-022, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-271d9bec.

Media-ingest log 550: frame frm-001 at GIF index 0 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-60ee6dd3.

Audit-ledger commentary 551: SQLite rows for frm-002 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-7f6e5163.

Nonce-uniqueness memo 552: default nonces for frm-003 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-988f8794.

Key-rotation briefing 553: when frm-004 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-b7c66dc4.

Forensic background 554: incident response playbook work on echo-channel (frm-005) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-f4ffd07c.

Reviewer checklist item 555: confirm frm-006 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the foxtrot-channel payload embedded at GIF index 6. Ref: FORE-ef864de9.
Review date: 2026-07-15. (Superseded draft circulation — not operative.)

Stakeholder summary 556: team-vault owns remediation for frm-007. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-9ed0dcda.

Telemetry cross-check 557: monitoring ticket MON-00557 for frm-008 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-267f00cd.

Cipher review 558: AES-256-GCM on frm-009 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-5347691d.

Appendix cross-ref 559: readers reconciling frm-010 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-ed9f92b8.

Vault ceremony 560: channel frm-011 (kilo-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-9e1d9080.

Chain-of-custody note 561 for frm-012: the GIF extension block labelled MRNR/CRYPTO1 on index 12 is the authoritative ciphertext carrier for lima-channel. Earlier draft captures in ticket FORE-0561 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-95d6f253.

Governance review 562: GIF steganography review policy for frm-013 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-32a94c0e.

Incident cross-reference 563: during AES-GCM authentication tag handling triage on frm-014, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-239416b1.

Media-ingest log 564: frame frm-015 at GIF index 15 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-8ce4bc26.

Audit-ledger commentary 565: SQLite rows for frm-016 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-81a3d93e.

Nonce-uniqueness memo 566: default nonces for frm-017 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-239ba053.

Key-rotation briefing 567: when frm-018 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-e80fe7fc.

Forensic background 568: incident response playbook work on tango-channel (frm-019) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-9031841f.

Reviewer checklist item 569: confirm frm-020 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the uniform-channel payload embedded at GIF index 20. Ref: FORE-8ec840cb.

Stakeholder summary 570: team-vault owns remediation for frm-021. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-e11e02b8.

Telemetry cross-check 571: monitoring ticket MON-00571 for frm-022 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-000314cc.

Cipher review 572: AES-256-GCM on frm-001 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-3e8d7114.

Appendix cross-ref 573: readers reconciling frm-002 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-4d41b02d.

Vault ceremony 574: channel frm-003 (charlie-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-37a0cf9c.

Chain-of-custody note 575 for frm-004: the GIF extension block labelled MRNR/CRYPTO1 on index 4 is the authoritative ciphertext carrier for delta-channel. Earlier draft captures in ticket FORE-0575 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-f8cc3ccc.

Governance review 576: GIF steganography review policy for frm-005 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-a0c450ee.

Incident cross-reference 577: during AES-GCM authentication tag handling triage on frm-006, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-418c049f.

Media-ingest log 578: frame frm-007 at GIF index 7 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-f13113bf.

Audit-ledger commentary 579: SQLite rows for frm-008 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-75dd368d.

Nonce-uniqueness memo 580: default nonces for frm-009 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-f9bfd090.

Key-rotation briefing 581: when frm-010 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-d479e786.

Forensic background 582: incident response playbook work on kilo-channel (frm-011) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-2af93e6e.

Reviewer checklist item 583: confirm frm-012 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the lima-channel payload embedded at GIF index 12. Ref: FORE-1c124cf3.

Stakeholder summary 584: team-vault owns remediation for frm-013. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-aca68843.

Telemetry cross-check 585: monitoring ticket MON-00585 for frm-014 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-2ecf26fb.

Cipher review 586: AES-256-GCM on frm-015 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-ee9394af.

Appendix cross-ref 587: readers reconciling frm-016 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-f5dfd86d.

Vault ceremony 588: channel frm-017 (quebec-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-3f00c62f.

Chain-of-custody note 589 for frm-018: the GIF extension block labelled MRNR/CRYPTO1 on index 18 is the authoritative ciphertext carrier for sierra-channel. Earlier draft captures in ticket FORE-0589 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-044c364d.

Governance review 590: GIF steganography review policy for frm-019 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-2670a005.

Incident cross-reference 591: during AES-GCM authentication tag handling triage on frm-020, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-b1eb929d.

Media-ingest log 592: frame frm-021 at GIF index 21 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-3fa6f31f.
Review date: 2026-07-15. (Superseded draft circulation — not operative.)

Audit-ledger commentary 593: SQLite rows for frm-022 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-ff1c907e.

Nonce-uniqueness memo 594: default nonces for frm-001 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-c1c5a06d.

Key-rotation briefing 595: when frm-002 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-5136e891.

Forensic background 596: incident response playbook work on charlie-channel (frm-003) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-387a6e34.

Reviewer checklist item 597: confirm frm-004 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the delta-channel payload embedded at GIF index 4. Ref: FORE-4823f0f0.

Stakeholder summary 598: team-vault owns remediation for frm-005. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-f8c9f9fd.

Telemetry cross-check 599: monitoring ticket MON-00599 for frm-006 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-d33c0b54.

Cipher review 600: AES-256-GCM on frm-007 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-25aed01d.

Appendix cross-ref 601: readers reconciling frm-008 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-5becb6af.

Vault ceremony 602: channel frm-009 (india-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-7a967d42.

Chain-of-custody note 603 for frm-010: the GIF extension block labelled MRNR/CRYPTO1 on index 10 is the authoritative ciphertext carrier for juliet-channel. Earlier draft captures in ticket FORE-0603 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-8e4c2424.

Governance review 604: GIF steganography review policy for frm-011 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-21251f0c.

Incident cross-reference 605: during AES-GCM authentication tag handling triage on frm-012, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-e0078724.

Media-ingest log 606: frame frm-013 at GIF index 13 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-05c29872.

Audit-ledger commentary 607: SQLite rows for frm-014 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-efc54905.

Nonce-uniqueness memo 608: default nonces for frm-015 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-e32d14f7.

Key-rotation briefing 609: when frm-016 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-4ae5e78c.

Forensic background 610: incident response playbook work on quebec-channel (frm-017) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-901cc623.

Reviewer checklist item 611: confirm frm-018 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the sierra-channel payload embedded at GIF index 18. Ref: FORE-486ecb6e.

Stakeholder summary 612: team-vault owns remediation for frm-019. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-6256faf3.

Telemetry cross-check 613: monitoring ticket MON-00613 for frm-020 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-120e1087.

Cipher review 614: AES-256-GCM on frm-021 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-a7cbee41.

Appendix cross-ref 615: readers reconciling frm-022 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-333afa09.

Vault ceremony 616: channel frm-001 (alpha-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-d5bc7b46.

Chain-of-custody note 617 for frm-002: the GIF extension block labelled MRNR/CRYPTO1 on index 1 is the authoritative ciphertext carrier for bravo-channel. Earlier draft captures in ticket FORE-0617 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-3751783e.

Governance review 618: GIF steganography review policy for frm-003 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-fa83cccd.

Incident cross-reference 619: during AES-GCM authentication tag handling triage on frm-004, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-111b36b3.

Media-ingest log 620: frame frm-005 at GIF index 5 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-969ac943.

Audit-ledger commentary 621: SQLite rows for frm-006 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-3e34519c.

Nonce-uniqueness memo 622: default nonces for frm-007 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-8c13d9b8.

Key-rotation briefing 623: when frm-008 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-2fb063dd.

Forensic background 624: incident response playbook work on india-channel (frm-009) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-e00873f7.

Reviewer checklist item 625: confirm frm-010 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the juliet-channel payload embedded at GIF index 10. Ref: FORE-d631f948.

Stakeholder summary 626: team-vault owns remediation for frm-011. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-8d1d3541.

Telemetry cross-check 627: monitoring ticket MON-00627 for frm-012 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-6e8b740d.

Cipher review 628: AES-256-GCM on frm-013 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-07906654.

Appendix cross-ref 629: readers reconciling frm-014 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-be4a3637.
Review date: 2026-07-15. (Superseded draft circulation — not operative.)

Vault ceremony 630: channel frm-015 (oscar-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-7705395a.

Chain-of-custody note 631 for frm-016: the GIF extension block labelled MRNR/CRYPTO1 on index 16 is the authoritative ciphertext carrier for papa-channel. Earlier draft captures in ticket FORE-0631 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-68a5870b.

Governance review 632: GIF steganography review policy for frm-017 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-55a8d9b2.

Incident cross-reference 633: during AES-GCM authentication tag handling triage on frm-018, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-e8ec3e19.

Media-ingest log 634: frame frm-019 at GIF index 19 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-a51bf17b.

Audit-ledger commentary 635: SQLite rows for frm-020 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-5e4a52e1.

Nonce-uniqueness memo 636: default nonces for frm-021 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-80dc07ae.

Key-rotation briefing 637: when frm-022 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-e5b18d4b.

Forensic background 638: incident response playbook work on alpha-channel (frm-001) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-4a6d043f.

Reviewer checklist item 639: confirm frm-002 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the bravo-channel payload embedded at GIF index 1. Ref: FORE-e274a79d.

Stakeholder summary 640: team-vault owns remediation for frm-003. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-391d08a6.

Telemetry cross-check 641: monitoring ticket MON-00641 for frm-004 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-f2228ee5.

Cipher review 642: AES-256-GCM on frm-005 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-64444dcf.

Appendix cross-ref 643: readers reconciling frm-006 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-61242c06.

Vault ceremony 644: channel frm-007 (golf-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-f74ffe39.

Chain-of-custody note 645 for frm-008: the GIF extension block labelled MRNR/CRYPTO1 on index 8 is the authoritative ciphertext carrier for hotel-channel. Earlier draft captures in ticket FORE-0645 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-831ee342.

Governance review 646: GIF steganography review policy for frm-009 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-ef3fd1d7.

Incident cross-reference 647: during AES-GCM authentication tag handling triage on frm-010, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-dbd2a26f.

Media-ingest log 648: frame frm-011 at GIF index 11 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-35ae2577.

Audit-ledger commentary 649: SQLite rows for frm-012 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-5327cd7f.

Nonce-uniqueness memo 650: default nonces for frm-013 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-8ed67ae2.

Key-rotation briefing 651: when frm-014 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-43438cfd.

Forensic background 652: incident response playbook work on oscar-channel (frm-015) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-e671530d.

Reviewer checklist item 653: confirm frm-016 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the papa-channel payload embedded at GIF index 16. Ref: FORE-e6f2ce19.

Stakeholder summary 654: team-vault owns remediation for frm-017. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-d997cb0c.

Telemetry cross-check 655: monitoring ticket MON-00655 for frm-018 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-124f26bc.

Cipher review 656: AES-256-GCM on frm-019 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-5cadc78d.

Appendix cross-ref 657: readers reconciling frm-020 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-28dfaf22.

Vault ceremony 658: channel frm-021 (victor-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-be7d45fe.

Chain-of-custody note 659 for frm-022: the GIF extension block labelled MRNR/CRYPTO1 on index 22 is the authoritative ciphertext carrier for whiskey-channel. Earlier draft captures in ticket FORE-0659 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-acdae1a9.

Governance review 660: GIF steganography review policy for frm-001 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-f66a528f.

Incident cross-reference 661: during AES-GCM authentication tag handling triage on frm-002, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-6a780afa.

Media-ingest log 662: frame frm-003 at GIF index 2 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-1f4f6992.

Audit-ledger commentary 663: SQLite rows for frm-004 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-4483a1c1.

Nonce-uniqueness memo 664: default nonces for frm-005 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-45772ec0.

Key-rotation briefing 665: when frm-006 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-6b8c0628.

Forensic background 666: incident response playbook work on golf-channel (frm-007) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-c54f1060.
Review date: 2026-07-15. (Superseded draft circulation — not operative.)

Reviewer checklist item 667: confirm frm-008 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the hotel-channel payload embedded at GIF index 8. Ref: FORE-22ae004c.

Stakeholder summary 668: team-vault owns remediation for frm-009. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-3a041f1c.

Telemetry cross-check 669: monitoring ticket MON-00669 for frm-010 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-7da8f21c.

Cipher review 670: AES-256-GCM on frm-011 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-dfe6ba72.

Appendix cross-ref 671: readers reconciling frm-012 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-83234c07.

Vault ceremony 672: channel frm-013 (mike-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-97a50cb5.

Chain-of-custody note 673 for frm-014: the GIF extension block labelled MRNR/CRYPTO1 on index 14 is the authoritative ciphertext carrier for november-channel. Earlier draft captures in ticket FORE-0673 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-8e349f68.

Governance review 674: GIF steganography review policy for frm-015 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-90c23ed2.

Incident cross-reference 675: during AES-GCM authentication tag handling triage on frm-016, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-bc4ab587.

Media-ingest log 676: frame frm-017 at GIF index 17 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-1ada0a41.

Audit-ledger commentary 677: SQLite rows for frm-018 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-97048018.

Nonce-uniqueness memo 678: default nonces for frm-019 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-927a2d39.

Key-rotation briefing 679: when frm-020 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-c764937a.

Forensic background 680: incident response playbook work on victor-channel (frm-021) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-342d2d55.

Reviewer checklist item 681: confirm frm-022 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the whiskey-channel payload embedded at GIF index 22. Ref: FORE-b288e71a.

Stakeholder summary 682: team-vault owns remediation for frm-001. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-5a17395f.

Telemetry cross-check 683: monitoring ticket MON-00683 for frm-002 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-a479226f.

Cipher review 684: AES-256-GCM on frm-003 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-d6cce6f0.

Appendix cross-ref 685: readers reconciling frm-004 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-4dd42020.

Vault ceremony 686: channel frm-005 (echo-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-3f8cdbde.

Chain-of-custody note 687 for frm-006: the GIF extension block labelled MRNR/CRYPTO1 on index 6 is the authoritative ciphertext carrier for foxtrot-channel. Earlier draft captures in ticket FORE-0687 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-ef2c8f4a.

Governance review 688: GIF steganography review policy for frm-007 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-b183c463.

Incident cross-reference 689: during AES-GCM authentication tag handling triage on frm-008, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-9547a3c2.

Media-ingest log 690: frame frm-009 at GIF index 9 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-c7455062.

Audit-ledger commentary 691: SQLite rows for frm-010 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-a949e70e.

Nonce-uniqueness memo 692: default nonces for frm-011 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-9f1323cc.

Key-rotation briefing 693: when frm-012 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-d5f7813c.

Forensic background 694: incident response playbook work on mike-channel (frm-013) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-09fb430b.

Reviewer checklist item 695: confirm frm-014 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the november-channel payload embedded at GIF index 14. Ref: FORE-9666ed4b.

Stakeholder summary 696: team-vault owns remediation for frm-015. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-ad45e94b.

Telemetry cross-check 697: monitoring ticket MON-00697 for frm-016 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-f4458e25.

Cipher review 698: AES-256-GCM on frm-017 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-27356fbd.

Appendix cross-ref 699: readers reconciling frm-018 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-9901bb3d.

Vault ceremony 700: channel frm-019 (tango-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-c94ac05b.

Chain-of-custody note 701 for frm-020: the GIF extension block labelled MRNR/CRYPTO1 on index 20 is the authoritative ciphertext carrier for uniform-channel. Earlier draft captures in ticket FORE-0701 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-67849407.

Governance review 702: GIF steganography review policy for frm-021 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-42b6495d.

Incident cross-reference 703: during AES-GCM authentication tag handling triage on frm-022, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-48512f3b.
Review date: 2026-07-15. (Superseded draft circulation — not operative.)

Media-ingest log 704: frame frm-001 at GIF index 0 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-d6f423a8.

Audit-ledger commentary 705: SQLite rows for frm-002 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-fed0ca79.

Nonce-uniqueness memo 706: default nonces for frm-003 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-26b1d4ef.

Key-rotation briefing 707: when frm-004 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-7aecd16f.

Forensic background 708: incident response playbook work on echo-channel (frm-005) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-d08bc826.

Reviewer checklist item 709: confirm frm-006 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the foxtrot-channel payload embedded at GIF index 6. Ref: FORE-9cf4771c.

Stakeholder summary 710: team-vault owns remediation for frm-007. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-0c0c6fe1.

Telemetry cross-check 711: monitoring ticket MON-00711 for frm-008 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-3f24d393.

Cipher review 712: AES-256-GCM on frm-009 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-5565a56f.

Appendix cross-ref 713: readers reconciling frm-010 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-3ce201f9.

Vault ceremony 714: channel frm-011 (kilo-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-3cc02cce.

Chain-of-custody note 715 for frm-012: the GIF extension block labelled MRNR/CRYPTO1 on index 12 is the authoritative ciphertext carrier for lima-channel. Earlier draft captures in ticket FORE-0715 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-945491a1.

Governance review 716: GIF steganography review policy for frm-013 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-b1e0dd40.

Incident cross-reference 717: during AES-GCM authentication tag handling triage on frm-014, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-3a7075d9.

Media-ingest log 718: frame frm-015 at GIF index 15 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-fe122ce8.

Audit-ledger commentary 719: SQLite rows for frm-016 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-75818edb.

Nonce-uniqueness memo 720: default nonces for frm-017 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-8652819f.

Key-rotation briefing 721: when frm-018 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-104a3515.

Forensic background 722: incident response playbook work on tango-channel (frm-019) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-7d55723a.

Reviewer checklist item 723: confirm frm-020 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the uniform-channel payload embedded at GIF index 20. Ref: FORE-6a1194b6.

Stakeholder summary 724: team-vault owns remediation for frm-021. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-807876e5.

Telemetry cross-check 725: monitoring ticket MON-00725 for frm-022 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-c51fd860.

Cipher review 726: AES-256-GCM on frm-001 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-af64b9dd.

Appendix cross-ref 727: readers reconciling frm-002 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-bc166995.

Vault ceremony 728: channel frm-003 (charlie-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-4ee8916e.

Chain-of-custody note 729 for frm-004: the GIF extension block labelled MRNR/CRYPTO1 on index 4 is the authoritative ciphertext carrier for delta-channel. Earlier draft captures in ticket FORE-0729 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-22da08a8.

Governance review 730: GIF steganography review policy for frm-005 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-8eef33e0.

Incident cross-reference 731: during AES-GCM authentication tag handling triage on frm-006, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-c295ea26.

Media-ingest log 732: frame frm-007 at GIF index 7 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-aa50698e.

Audit-ledger commentary 733: SQLite rows for frm-008 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-9555b377.

Nonce-uniqueness memo 734: default nonces for frm-009 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-2f1c5a16.

Key-rotation briefing 735: when frm-010 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-bfc201f5.

Forensic background 736: incident response playbook work on kilo-channel (frm-011) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-d9681728.

Reviewer checklist item 737: confirm frm-012 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the lima-channel payload embedded at GIF index 12. Ref: FORE-a1ef1f8b.

Stakeholder summary 738: team-vault owns remediation for frm-013. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-56b6781b.

Telemetry cross-check 739: monitoring ticket MON-00739 for frm-014 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-176c9d6f.

Cipher review 740: AES-256-GCM on frm-015 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-e0a8db7c.
Review date: 2026-07-15. (Superseded draft circulation — not operative.)

Appendix cross-ref 741: readers reconciling frm-016 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-a4726698.

Vault ceremony 742: channel frm-017 (quebec-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-7448023f.

Chain-of-custody note 743 for frm-018: the GIF extension block labelled MRNR/CRYPTO1 on index 18 is the authoritative ciphertext carrier for sierra-channel. Earlier draft captures in ticket FORE-0743 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-9fb2d65b.

Governance review 744: GIF steganography review policy for frm-019 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-bae1e58d.

Incident cross-reference 745: during AES-GCM authentication tag handling triage on frm-020, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-9c23dc00.

Media-ingest log 746: frame frm-021 at GIF index 21 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-c9aa47e7.

Audit-ledger commentary 747: SQLite rows for frm-022 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-655a8e7e.

Nonce-uniqueness memo 748: default nonces for frm-001 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-08009024.

Key-rotation briefing 749: when frm-002 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-1a1de9a6.

Forensic background 750: incident response playbook work on charlie-channel (frm-003) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-a6d4254a.

Reviewer checklist item 751: confirm frm-004 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the delta-channel payload embedded at GIF index 4. Ref: FORE-0791b5be.

Stakeholder summary 752: team-vault owns remediation for frm-005. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-1d24c69b.

Telemetry cross-check 753: monitoring ticket MON-00753 for frm-006 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-b52fdb1f.

Cipher review 754: AES-256-GCM on frm-007 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-7cac4bca.

Appendix cross-ref 755: readers reconciling frm-008 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-2e16dc3d.

Vault ceremony 756: channel frm-009 (india-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-8e3546fe.

Chain-of-custody note 757 for frm-010: the GIF extension block labelled MRNR/CRYPTO1 on index 10 is the authoritative ciphertext carrier for juliet-channel. Earlier draft captures in ticket FORE-0757 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-6d7d4868.

Governance review 758: GIF steganography review policy for frm-011 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-e328a8d3.

Incident cross-reference 759: during AES-GCM authentication tag handling triage on frm-012, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-978c3cca.

Media-ingest log 760: frame frm-013 at GIF index 13 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-45a78ed5.

Audit-ledger commentary 761: SQLite rows for frm-014 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-514d4ca3.

Nonce-uniqueness memo 762: default nonces for frm-015 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-2ea5f329.

Key-rotation briefing 763: when frm-016 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-73225913.

Forensic background 764: incident response playbook work on quebec-channel (frm-017) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-ef6a9f9f.

Reviewer checklist item 765: confirm frm-018 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the sierra-channel payload embedded at GIF index 18. Ref: FORE-a979a627.

Stakeholder summary 766: team-vault owns remediation for frm-019. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-c0a21fc0.

Telemetry cross-check 767: monitoring ticket MON-00767 for frm-020 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-063d295f.

Cipher review 768: AES-256-GCM on frm-021 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-9b75e6fc.

Appendix cross-ref 769: readers reconciling frm-022 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-fc93be71.

Vault ceremony 770: channel frm-001 (alpha-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-b099fa86.

Chain-of-custody note 771 for frm-002: the GIF extension block labelled MRNR/CRYPTO1 on index 1 is the authoritative ciphertext carrier for bravo-channel. Earlier draft captures in ticket FORE-0771 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-305ebc7e.

Governance review 772: GIF steganography review policy for frm-003 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-f151dce8.

Incident cross-reference 773: during AES-GCM authentication tag handling triage on frm-004, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-92236397.

Media-ingest log 774: frame frm-005 at GIF index 5 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-b4913a8b.

Audit-ledger commentary 775: SQLite rows for frm-006 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-9641e58f.

Nonce-uniqueness memo 776: default nonces for frm-007 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-9fa11e17.

Key-rotation briefing 777: when frm-008 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-c5e94651.
Review date: 2026-07-15. (Superseded draft circulation — not operative.)

Forensic background 778: incident response playbook work on india-channel (frm-009) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-c1ddfea1.

Reviewer checklist item 779: confirm frm-010 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the juliet-channel payload embedded at GIF index 10. Ref: FORE-5323c6a9.

Stakeholder summary 780: team-vault owns remediation for frm-011. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-fe435a8d.

Telemetry cross-check 781: monitoring ticket MON-00781 for frm-012 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-5a3a0664.

Cipher review 782: AES-256-GCM on frm-013 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-b3173881.

Appendix cross-ref 783: readers reconciling frm-014 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-425c691e.

Vault ceremony 784: channel frm-015 (oscar-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-375f03a1.

Chain-of-custody note 785 for frm-016: the GIF extension block labelled MRNR/CRYPTO1 on index 16 is the authoritative ciphertext carrier for papa-channel. Earlier draft captures in ticket FORE-0785 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-af730753.

Governance review 786: GIF steganography review policy for frm-017 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-6a12e6a1.

Incident cross-reference 787: during AES-GCM authentication tag handling triage on frm-018, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-ed827153.

Media-ingest log 788: frame frm-019 at GIF index 19 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-3f8b5345.

Audit-ledger commentary 789: SQLite rows for frm-020 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-e4df0575.

Nonce-uniqueness memo 790: default nonces for frm-021 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-b417e070.

Key-rotation briefing 791: when frm-022 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-8c0dce4a.

Forensic background 792: incident response playbook work on alpha-channel (frm-001) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-1f28c73e.

Reviewer checklist item 793: confirm frm-002 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the bravo-channel payload embedded at GIF index 1. Ref: FORE-278933c1.

Stakeholder summary 794: team-vault owns remediation for frm-003. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-78f8f75c.

Telemetry cross-check 795: monitoring ticket MON-00795 for frm-004 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-cb7eb18c.

Cipher review 796: AES-256-GCM on frm-005 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-fa7822c0.

Appendix cross-ref 797: readers reconciling frm-006 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-51348c2a.

Vault ceremony 798: channel frm-007 (golf-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-870b6a2f.

Chain-of-custody note 799 for frm-008: the GIF extension block labelled MRNR/CRYPTO1 on index 8 is the authoritative ciphertext carrier for hotel-channel. Earlier draft captures in ticket FORE-0799 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-91c590e8.

Governance review 800: GIF steganography review policy for frm-009 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-e27b471c.

Incident cross-reference 801: during AES-GCM authentication tag handling triage on frm-010, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-52e3ae28.

Media-ingest log 802: frame frm-011 at GIF index 11 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-e0e4b304.

Audit-ledger commentary 803: SQLite rows for frm-012 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-f58c6a38.

Nonce-uniqueness memo 804: default nonces for frm-013 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-28c632e1.

Key-rotation briefing 805: when frm-014 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-887c07f3.

Forensic background 806: incident response playbook work on oscar-channel (frm-015) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-b60aa7c5.

Reviewer checklist item 807: confirm frm-016 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the papa-channel payload embedded at GIF index 16. Ref: FORE-338058d8.

Stakeholder summary 808: team-vault owns remediation for frm-017. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-18666bc0.

Telemetry cross-check 809: monitoring ticket MON-00809 for frm-018 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-3ecd608e.

Cipher review 810: AES-256-GCM on frm-019 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-2c81cbbf.

Appendix cross-ref 811: readers reconciling frm-020 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-72bfaf78.

Vault ceremony 812: channel frm-021 (victor-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-f286aa00.

Chain-of-custody note 813 for frm-022: the GIF extension block labelled MRNR/CRYPTO1 on index 22 is the authoritative ciphertext carrier for whiskey-channel. Earlier draft captures in ticket FORE-0813 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-f72320bc.

Governance review 814: GIF steganography review policy for frm-001 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-1d4197b0.
Review date: 2026-07-15. (Superseded draft circulation — not operative.)

Incident cross-reference 815: during AES-GCM authentication tag handling triage on frm-002, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-c0392310.

Media-ingest log 816: frame frm-003 at GIF index 2 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-cc7650bd.

Audit-ledger commentary 817: SQLite rows for frm-004 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-ad257139.

Nonce-uniqueness memo 818: default nonces for frm-005 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-b9968da9.

Key-rotation briefing 819: when frm-006 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-2cae725c.

Forensic background 820: incident response playbook work on golf-channel (frm-007) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-f2f16ffe.

Reviewer checklist item 821: confirm frm-008 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the hotel-channel payload embedded at GIF index 8. Ref: FORE-c927c2bf.

Stakeholder summary 822: team-vault owns remediation for frm-009. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-bed7eae0.

Telemetry cross-check 823: monitoring ticket MON-00823 for frm-010 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-2b989b33.

Cipher review 824: AES-256-GCM on frm-011 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-0bb35f3e.

Appendix cross-ref 825: readers reconciling frm-012 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-0f5417e9.

Vault ceremony 826: channel frm-013 (mike-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-928776ac.

Chain-of-custody note 827 for frm-014: the GIF extension block labelled MRNR/CRYPTO1 on index 14 is the authoritative ciphertext carrier for november-channel. Earlier draft captures in ticket FORE-0827 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-75cff2a8.

Governance review 828: GIF steganography review policy for frm-015 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-dc60ef88.

Incident cross-reference 829: during AES-GCM authentication tag handling triage on frm-016, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-b9d16859.

Media-ingest log 830: frame frm-017 at GIF index 17 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-5d1ef78b.

Audit-ledger commentary 831: SQLite rows for frm-018 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-d69295e4.

Nonce-uniqueness memo 832: default nonces for frm-019 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-c1ce5294.

Key-rotation briefing 833: when frm-020 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-171ae3e7.

Forensic background 834: incident response playbook work on victor-channel (frm-021) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-57afa8c1.

Reviewer checklist item 835: confirm frm-022 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the whiskey-channel payload embedded at GIF index 22. Ref: FORE-bfb1d280.

Stakeholder summary 836: team-vault owns remediation for frm-001. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-133c086d.

Telemetry cross-check 837: monitoring ticket MON-00837 for frm-002 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-610f482b.

Cipher review 838: AES-256-GCM on frm-003 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-3b86d157.

Appendix cross-ref 839: readers reconciling frm-004 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-0e6b6769.

Vault ceremony 840: channel frm-005 (echo-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-52e8fda2.

Chain-of-custody note 841 for frm-006: the GIF extension block labelled MRNR/CRYPTO1 on index 6 is the authoritative ciphertext carrier for foxtrot-channel. Earlier draft captures in ticket FORE-0841 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-0e4ec2e1.

Governance review 842: GIF steganography review policy for frm-007 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-90c97b68.

Incident cross-reference 843: during AES-GCM authentication tag handling triage on frm-008, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-ea01b654.

Media-ingest log 844: frame frm-009 at GIF index 9 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-c5b28800.

Audit-ledger commentary 845: SQLite rows for frm-010 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-01a57cd4.

Nonce-uniqueness memo 846: default nonces for frm-011 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-35a13508.

Key-rotation briefing 847: when frm-012 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-943cbed0.

Forensic background 848: incident response playbook work on mike-channel (frm-013) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-330c3813.

Reviewer checklist item 849: confirm frm-014 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the november-channel payload embedded at GIF index 14. Ref: FORE-ef6754ad.

Stakeholder summary 850: team-vault owns remediation for frm-015. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-6f640661.

Telemetry cross-check 851: monitoring ticket MON-00851 for frm-016 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-ad68528b.
Review date: 2026-07-15. (Superseded draft circulation — not operative.)

Cipher review 852: AES-256-GCM on frm-017 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-310c23e6.

Appendix cross-ref 853: readers reconciling frm-018 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-89089bde.

Vault ceremony 854: channel frm-019 (tango-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-1ec5fb3e.

Chain-of-custody note 855 for frm-020: the GIF extension block labelled MRNR/CRYPTO1 on index 20 is the authoritative ciphertext carrier for uniform-channel. Earlier draft captures in ticket FORE-0855 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-c911dd13.

Governance review 856: GIF steganography review policy for frm-021 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-d5f31f61.

Incident cross-reference 857: during AES-GCM authentication tag handling triage on frm-022, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-e9820bd1.

Media-ingest log 858: frame frm-001 at GIF index 0 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-11ed2d73.

Audit-ledger commentary 859: SQLite rows for frm-002 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-9200230c.

Nonce-uniqueness memo 860: default nonces for frm-003 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-4c4ab72c.

Key-rotation briefing 861: when frm-004 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-e01dd8ae.

Forensic background 862: incident response playbook work on echo-channel (frm-005) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-4622b7ae.

Reviewer checklist item 863: confirm frm-006 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the foxtrot-channel payload embedded at GIF index 6. Ref: FORE-c214778f.

Stakeholder summary 864: team-vault owns remediation for frm-007. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-daf79181.

Telemetry cross-check 865: monitoring ticket MON-00865 for frm-008 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-08e5f1a3.

Cipher review 866: AES-256-GCM on frm-009 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-a8d5746b.

Appendix cross-ref 867: readers reconciling frm-010 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-8579dc27.

Vault ceremony 868: channel frm-011 (kilo-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-32ae4907.

Chain-of-custody note 869 for frm-012: the GIF extension block labelled MRNR/CRYPTO1 on index 12 is the authoritative ciphertext carrier for lima-channel. Earlier draft captures in ticket FORE-0869 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-5f9272f3.

Governance review 870: GIF steganography review policy for frm-013 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-8978c3a3.

Incident cross-reference 871: during AES-GCM authentication tag handling triage on frm-014, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-df686513.

Media-ingest log 872: frame frm-015 at GIF index 15 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-bec979e7.

Audit-ledger commentary 873: SQLite rows for frm-016 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-7694be24.

Nonce-uniqueness memo 874: default nonces for frm-017 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-db288a23.

Key-rotation briefing 875: when frm-018 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-53d53ba2.

Forensic background 876: incident response playbook work on tango-channel (frm-019) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-ec5fea23.

Reviewer checklist item 877: confirm frm-020 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the uniform-channel payload embedded at GIF index 20. Ref: FORE-67a72516.

Stakeholder summary 878: team-vault owns remediation for frm-021. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-4f069fb3.

Telemetry cross-check 879: monitoring ticket MON-00879 for frm-022 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-6e2b707d.

Cipher review 880: AES-256-GCM on frm-001 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-cebcfce7.

Appendix cross-ref 881: readers reconciling frm-002 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-a63c5955.

Vault ceremony 882: channel frm-003 (charlie-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-e80423f6.

Chain-of-custody note 883 for frm-004: the GIF extension block labelled MRNR/CRYPTO1 on index 4 is the authoritative ciphertext carrier for delta-channel. Earlier draft captures in ticket FORE-0883 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-a6e72dfb.

Governance review 884: GIF steganography review policy for frm-005 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-c0633132.

Incident cross-reference 885: during AES-GCM authentication tag handling triage on frm-006, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-2e439181.

Media-ingest log 886: frame frm-007 at GIF index 7 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-e3ef6fad.

Audit-ledger commentary 887: SQLite rows for frm-008 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-d1efbbf0.

Nonce-uniqueness memo 888: default nonces for frm-009 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-778484bb.
Review date: 2026-07-15. (Superseded draft circulation — not operative.)

Key-rotation briefing 889: when frm-010 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-7e0c9808.

Forensic background 890: incident response playbook work on kilo-channel (frm-011) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-f08e8b99.

Reviewer checklist item 891: confirm frm-012 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the lima-channel payload embedded at GIF index 12. Ref: FORE-a382a5ae.

Stakeholder summary 892: team-vault owns remediation for frm-013. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-ff13bcee.

Telemetry cross-check 893: monitoring ticket MON-00893 for frm-014 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-3c9b178a.

Cipher review 894: AES-256-GCM on frm-015 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-4866ff8c.

Appendix cross-ref 895: readers reconciling frm-016 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-942cbf91.

Vault ceremony 896: channel frm-017 (quebec-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-a872bf21.

Chain-of-custody note 897 for frm-018: the GIF extension block labelled MRNR/CRYPTO1 on index 18 is the authoritative ciphertext carrier for sierra-channel. Earlier draft captures in ticket FORE-0897 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-f1e8de99.

Governance review 898: GIF steganography review policy for frm-019 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-d40e5a40.

Incident cross-reference 899: during AES-GCM authentication tag handling triage on frm-020, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-305ed5ae.

Media-ingest log 900: frame frm-021 at GIF index 21 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-b03d62e0.

Audit-ledger commentary 901: SQLite rows for frm-022 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-4ca7795d.

Nonce-uniqueness memo 902: default nonces for frm-001 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-83a29294.

Key-rotation briefing 903: when frm-002 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-f9cb5af5.

Forensic background 904: incident response playbook work on charlie-channel (frm-003) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-76086b79.

Reviewer checklist item 905: confirm frm-004 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the delta-channel payload embedded at GIF index 4. Ref: FORE-e945a3b1.

Stakeholder summary 906: team-vault owns remediation for frm-005. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-702ecb9d.

Telemetry cross-check 907: monitoring ticket MON-00907 for frm-006 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-a31ddc89.

Cipher review 908: AES-256-GCM on frm-007 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-e05b6ebf.

Appendix cross-ref 909: readers reconciling frm-008 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-dc0a1eb5.

## Appendix C (draft — superseded April 2026 circulation)

An earlier draft of this review circulated the following key-version ordering. It was withdrawn before sign-off and must not be used for reproduction.

```json
["latest_key_assigned", "rotation_replacement"]
```

The same draft omitted `db_override` from nonce precedence and listed only report overrides before derived nonces — that ordering is also withdrawn.

```json
["report_override", "derived_sha256_prefix"]
```

## Appendix A — In-scope frame dossiers

### frm-001 — alpha-channel

GIF index 0. Application extension MRNR/CRYPTO1.

Chain-of-custody note 10 for frm-001: the GIF extension block labelled MRNR/CRYPTO1 on index 0 is the authoritative ciphertext carrier for alpha-channel. Earlier draft captures in ticket FORE-0010 are explicitly superseded and must not be substituted during JDBC correlation.

Governance review 11: HSM provisioning audit policy for frm-001 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number.

Incident cross-reference 12: during cross-region key escrow triage on frm-001, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config.

Media-ingest log 13: frame frm-001 at GIF index 0 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding.

Audit-ledger commentary 14: SQLite rows for frm-001 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers.

Nonce-uniqueness memo 15: default nonces for frm-001 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames.

### frm-002 — bravo-channel

GIF index 1. Application extension MRNR/CRYPTO1.

Governance review 20: forensic media ingestion policy for frm-002 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number.

Incident cross-reference 21: during audit ledger reconciliation triage on frm-002, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config.

Media-ingest log 22: frame frm-002 at GIF index 1 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding.

Audit-ledger commentary 23: SQLite rows for frm-002 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers.

Nonce-uniqueness memo 24: default nonces for frm-002 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames.

Key-rotation briefing 25: when frm-002 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1.

### frm-003 — charlie-channel

GIF index 2. Application extension MRNR/CRYPTO1.

Incident cross-reference 30: during GIF steganography review triage on frm-003, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config.

Media-ingest log 31: frame frm-003 at GIF index 2 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding.

Audit-ledger commentary 32: SQLite rows for frm-003 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers.

Nonce-uniqueness memo 33: default nonces for frm-003 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames.

Key-rotation briefing 34: when frm-003 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1.

Forensic background 35: audit ledger reconciliation work on charlie-channel (frm-003) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements.

### frm-004 — delta-channel

GIF index 4. Application extension MRNR/CRYPTO1.

Media-ingest log 40: frame frm-004 at GIF index 4 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding.

Audit-ledger commentary 41: SQLite rows for frm-004 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers.

Nonce-uniqueness memo 42: default nonces for frm-004 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames.

Key-rotation briefing 43: when frm-004 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1.

Forensic background 44: GIF steganography review work on delta-channel (frm-004) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements.

Reviewer checklist item 45: confirm frm-004 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the delta-channel payload embedded at GIF index 4.

### frm-005 — echo-channel

GIF index 5. Application extension MRNR/CRYPTO1.

Audit-ledger commentary 50: SQLite rows for frm-005 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers.

Nonce-uniqueness memo 51: default nonces for frm-005 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames.

Key-rotation briefing 52: when frm-005 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1.

Forensic background 53: HSM provisioning audit work on echo-channel (frm-005) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements.

Reviewer checklist item 54: confirm frm-005 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the echo-channel payload embedded at GIF index 5.

Stakeholder summary 55: team-platform owns remediation for frm-005. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced.

### frm-006 — foxtrot-channel

GIF index 6. Application extension MRNR/CRYPTO1.

Nonce-uniqueness memo 60: default nonces for frm-006 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames.

Key-rotation briefing 61: when frm-006 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1.

Forensic background 62: forensic media ingestion work on foxtrot-channel (frm-006) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements.

Reviewer checklist item 63: confirm frm-006 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the foxtrot-channel payload embedded at GIF index 6.

Stakeholder summary 64: team-crypto owns remediation for frm-006. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced.

Telemetry cross-check 65: monitoring ticket MON-00065 for frm-006 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values.

### frm-007 — golf-channel

GIF index 7. Application extension MRNR/CRYPTO1.

Key-rotation briefing 70: when frm-007 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1.

Forensic background 71: evidence chain of custody work on golf-channel (frm-007) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements.

Reviewer checklist item 72: confirm frm-007 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the golf-channel payload embedded at GIF index 7.

Stakeholder summary 73: team-vault owns remediation for frm-007. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced.

Telemetry cross-check 74: monitoring ticket MON-00074 for frm-007 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values.

Cipher review 75: AES-256-GCM on frm-007 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory.

### frm-008 — hotel-channel

GIF index 8. Application extension MRNR/CRYPTO1.

Forensic background 80: post-quantum readiness survey work on hotel-channel (frm-008) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements.

Reviewer checklist item 81: confirm frm-008 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the hotel-channel payload embedded at GIF index 8.

Stakeholder summary 82: team-assurance owns remediation for frm-008. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced.

Telemetry cross-check 83: monitoring ticket MON-00083 for frm-008 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values.

Cipher review 84: AES-256-GCM on frm-008 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory.

Appendix cross-ref 85: readers reconciling frm-008 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone.

### frm-009 — india-channel

GIF index 9. Application extension MRNR/CRYPTO1.

Reviewer checklist item 90: confirm frm-009 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the india-channel payload embedded at GIF index 9.

Stakeholder summary 91: team-forensics owns remediation for frm-009. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced.

Telemetry cross-check 92: monitoring ticket MON-00092 for frm-009 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values.

Cipher review 93: AES-256-GCM on frm-009 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory.

Appendix cross-ref 94: readers reconciling frm-009 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone.

Vault ceremony 95: channel frm-009 (india-channel) was enrolled under the HSM provisioning audit programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings.

### frm-010 — juliet-channel

GIF index 10. Application extension MRNR/CRYPTO1.

Stakeholder summary 100: team-media owns remediation for frm-010. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced.

Telemetry cross-check 101: monitoring ticket MON-00101 for frm-010 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values.

Cipher review 102: AES-256-GCM on frm-010 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory.

Appendix cross-ref 103: readers reconciling frm-010 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone.

Vault ceremony 104: channel frm-010 (juliet-channel) was enrolled under the forensic media ingestion programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings.

Chain-of-custody note 105 for frm-010: the GIF extension block labelled MRNR/CRYPTO1 on index 10 is the authoritative ciphertext carrier for juliet-channel. Earlier draft captures in ticket FORE-0105 are explicitly superseded and must not be substituted during JDBC correlation.

### frm-011 — kilo-channel

GIF index 11. Application extension MRNR/CRYPTO1.

Telemetry cross-check 110: monitoring ticket MON-00110 for frm-011 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values.

Cipher review 111: AES-256-GCM on frm-011 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory.

Appendix cross-ref 112: readers reconciling frm-011 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone.

Vault ceremony 113: channel frm-011 (kilo-channel) was enrolled under the evidence chain of custody programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings.

Chain-of-custody note 114 for frm-011: the GIF extension block labelled MRNR/CRYPTO1 on index 11 is the authoritative ciphertext carrier for kilo-channel. Earlier draft captures in ticket FORE-0114 are explicitly superseded and must not be substituted during JDBC correlation.

Governance review 115: AES-GCM authentication tag handling policy for frm-011 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number.

### frm-012 — lima-channel

GIF index 12. Application extension MRNR/CRYPTO1.

Cipher review 120: AES-256-GCM on frm-012 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory.

Appendix cross-ref 121: readers reconciling frm-012 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone.

Vault ceremony 122: channel frm-012 (lima-channel) was enrolled under the post-quantum readiness survey programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings.

Chain-of-custody note 123 for frm-012: the GIF extension block labelled MRNR/CRYPTO1 on index 12 is the authoritative ciphertext carrier for lima-channel. Earlier draft captures in ticket FORE-0123 are explicitly superseded and must not be substituted during JDBC correlation.

Governance review 124: cross-region key escrow policy for frm-012 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number.

Incident cross-reference 125: during media sanitization triage on frm-012, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config.

### frm-013 — mike-channel

GIF index 13. Application extension MRNR/CRYPTO1.

Appendix cross-ref 130: readers reconciling frm-013 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone.

Vault ceremony 131: channel frm-013 (mike-channel) was enrolled under the nonce uniqueness policy programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings.

Chain-of-custody note 132 for frm-013: the GIF extension block labelled MRNR/CRYPTO1 on index 13 is the authoritative ciphertext carrier for mike-channel. Earlier draft captures in ticket FORE-0132 are explicitly superseded and must not be substituted during JDBC correlation.

Governance review 133: audit ledger reconciliation policy for frm-013 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number.

Incident cross-reference 134: during incident response playbook triage on frm-013, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config.

Media-ingest log 135: frame frm-013 at GIF index 13 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding.

### frm-014 — november-channel

GIF index 14. Application extension MRNR/CRYPTO1.

Vault ceremony 140: channel frm-014 (november-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings.

Chain-of-custody note 141 for frm-014: the GIF extension block labelled MRNR/CRYPTO1 on index 14 is the authoritative ciphertext carrier for november-channel. Earlier draft captures in ticket FORE-0141 are explicitly superseded and must not be substituted during JDBC correlation.

Governance review 142: GIF steganography review policy for frm-014 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number.

Incident cross-reference 143: during AES-GCM authentication tag handling triage on frm-014, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config.

Media-ingest log 144: frame frm-014 at GIF index 14 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding.

Audit-ledger commentary 145: SQLite rows for frm-014 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers.

### frm-015 — oscar-channel

GIF index 15. Application extension MRNR/CRYPTO1.

Chain-of-custody note 150 for frm-015: the GIF extension block labelled MRNR/CRYPTO1 on index 15 is the authoritative ciphertext carrier for oscar-channel. Earlier draft captures in ticket FORE-0150 are explicitly superseded and must not be substituted during JDBC correlation.

Governance review 151: HSM provisioning audit policy for frm-015 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number.

Incident cross-reference 152: during cross-region key escrow triage on frm-015, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config.

Media-ingest log 153: frame frm-015 at GIF index 15 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding.

Audit-ledger commentary 154: SQLite rows for frm-015 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers.

Nonce-uniqueness memo 155: default nonces for frm-015 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames.

### frm-016 — papa-channel

GIF index 16. Application extension MRNR/CRYPTO1.

Governance review 160: forensic media ingestion policy for frm-016 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number.

Incident cross-reference 161: during audit ledger reconciliation triage on frm-016, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config.

Media-ingest log 162: frame frm-016 at GIF index 16 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding.

Audit-ledger commentary 163: SQLite rows for frm-016 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers.

Nonce-uniqueness memo 164: default nonces for frm-016 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames.

Key-rotation briefing 165: when frm-016 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1.

### frm-017 — quebec-channel

GIF index 17. Application extension MRNR/CRYPTO1.

Incident cross-reference 170: during GIF steganography review triage on frm-017, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config.

Media-ingest log 171: frame frm-017 at GIF index 17 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding.

Audit-ledger commentary 172: SQLite rows for frm-017 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers.

Nonce-uniqueness memo 173: default nonces for frm-017 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames.

Key-rotation briefing 174: when frm-017 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1.

Forensic background 175: audit ledger reconciliation work on quebec-channel (frm-017) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements.

### frm-018 — sierra-channel

GIF index 18. Application extension MRNR/CRYPTO1.

Media-ingest log 180: frame frm-018 at GIF index 18 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding.

Audit-ledger commentary 181: SQLite rows for frm-018 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers.

Nonce-uniqueness memo 182: default nonces for frm-018 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames.

Key-rotation briefing 183: when frm-018 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1.

Forensic background 184: GIF steganography review work on sierra-channel (frm-018) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements.

Reviewer checklist item 185: confirm frm-018 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the sierra-channel payload embedded at GIF index 18.

### frm-019 — tango-channel

GIF index 19. Application extension MRNR/CRYPTO1.

Audit-ledger commentary 190: SQLite rows for frm-019 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers.

Nonce-uniqueness memo 191: default nonces for frm-019 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames.

Key-rotation briefing 192: when frm-019 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1.

Forensic background 193: HSM provisioning audit work on tango-channel (frm-019) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements.

Reviewer checklist item 194: confirm frm-019 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the tango-channel payload embedded at GIF index 19.

Stakeholder summary 195: team-platform owns remediation for frm-019. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced.

### frm-020 — uniform-channel

GIF index 20. Application extension MRNR/CRYPTO1.

Nonce-uniqueness memo 200: default nonces for frm-020 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames.

Key-rotation briefing 201: when frm-020 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1.

Forensic background 202: forensic media ingestion work on uniform-channel (frm-020) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements.

Reviewer checklist item 203: confirm frm-020 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the uniform-channel payload embedded at GIF index 20.

Stakeholder summary 204: team-crypto owns remediation for frm-020. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced.

Telemetry cross-check 205: monitoring ticket MON-00205 for frm-020 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values.

### frm-021 — victor-channel

GIF index 21. Application extension MRNR/CRYPTO1.

Key-rotation briefing 210: when frm-021 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1.

Forensic background 211: evidence chain of custody work on victor-channel (frm-021) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements.

Reviewer checklist item 212: confirm frm-021 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the victor-channel payload embedded at GIF index 21.

Stakeholder summary 213: team-vault owns remediation for frm-021. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced.

Telemetry cross-check 214: monitoring ticket MON-00214 for frm-021 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values.

Cipher review 215: AES-256-GCM on frm-021 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory.

### frm-022 — whiskey-channel

GIF index 22. Application extension MRNR/CRYPTO1.

Forensic background 220: post-quantum readiness survey work on whiskey-channel (frm-022) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements.

Reviewer checklist item 221: confirm frm-022 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the whiskey-channel payload embedded at GIF index 22.

Stakeholder summary 222: team-assurance owns remediation for frm-022. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced.

Telemetry cross-check 223: monitoring ticket MON-00223 for frm-022 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values.

Cipher review 224: AES-256-GCM on frm-022 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory.

Appendix cross-ref 225: readers reconciling frm-022 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone.

## Appendix B — Audit timeline (narrative index)

Chronological facts and field values are authoritative only in SQLite.
This appendix indexes which event types appear per frame — not operative
key versions, rotation replacements, or nonce override bytes.

- **frm-001**: `key_assigned`
- **frm-002**: `key_assigned`, `key_rotated`, `key_assigned`
- **frm-003**: `key_assigned`, `nonce_override_registered`
- **frm-004**: `key_assigned`, `key_rotated`, `key_rotated`, `key_assigned`
- **frm-005**: `key_assigned`, `key_rotated`
- **frm-006**: `key_assigned`
- **frm-007**: `key_assigned`, `nonce_override_registered`, `nonce_override_registered`
- **frm-008**: `key_assigned`, `nonce_override_registered`, `nonce_override_registered`, `nonce_override_registered`, `nonce_override_revoked`
- **frm-009**: `key_assigned`, `key_rotated`, `key_rotated`, `key_rotation_rescinded`, `key_assigned`
- **frm-010**: `key_assigned`, `nonce_override_registered`
- **frm-011**: `key_assigned`, `key_rotated`, `key_rotated`, `key_rotated`, `key_assigned`
- **frm-012**: `key_assigned`, `nonce_override_registered`, `key_rotated`
- **frm-013**: `key_assigned`, `nonce_override_registered`, `nonce_override_registered`, `nonce_override_revoked`, `key_rotated`
- **frm-014**: `key_assigned`, `nonce_override_registered`, `key_rotated`, `nonce_override_registered`, `nonce_override_registered`
- **frm-015**: `key_assigned`, `key_rotated`
- **frm-016**: `key_assigned`, `nonce_override_registered`, `nonce_override_registered`, `nonce_override_amended`
- **frm-017**: `key_assigned`, `key_rotated`, `nonce_override_registered`, `nonce_override_registered`, `nonce_override_amended`, `nonce_override_registered`, `nonce_override_registered`
- **frm-018**: `key_assigned`, `key_assigned`, `key_assignment_rescinded`
- **frm-019**: `key_assigned`, `key_rotated`, `key_rotated`, `key_rotation_rescinded`
- **frm-020**: `key_assigned`, `nonce_override_registered`, `nonce_override_registered`, `nonce_override_amended`, `nonce_override_amended`
- **frm-021**: `key_assigned`, `key_rotated`, `key_rotation_rescinded`, `key_assigned`, `key_assignment_rescinded`, `key_rotated`, `key_rotation_rescinded`
- **frm-022**: `key_assigned`, `nonce_override_registered`, `key_rotated`

## Appendix C — Normative cryptographic exception precedence

The following precedence is binding when correlating audit events to a
frame's operative decryption material.

### C.1 Key-version selection

1. **rotation_replacement** — when a `key_rotated` audit event exists for the
   frame, the operative key version is the event's `replacement_key_version`,
   not the superseded `key_version` and not any later `key_assigned` row that
   merely restates an unrelated version. When more than one `key_rotated` event
   exists for a frame, the one with the greatest `recorded_at` is operative, and
   its `replacement_key_version` is used as-is even if it is numerically lower
   than a superseded version.
2. **latest_key_assigned** — otherwise, take the `key_assigned` event with the
   greatest `recorded_at` timestamp for the frame.

A `key_rotation_rescinded` event voids every prior `key_rotated` row for the
same frame whose `key_version` and `replacement_key_version` match the
rescission's pair. When choosing the operative rotation, exclude voided rows
first, then take the greatest `recorded_at` among the survivors. When **every**
`key_rotated` row for a frame has been voided, treat the frame as having no
operative rotation and apply **latest_key_assigned** instead.

A `key_assignment_rescinded` event voids every prior `key_assigned` row for
the same frame whose `key_version` equals the rescission's `key_version`.
When falling back to **latest_key_assigned**, exclude voided assignments
before choosing the greatest `recorded_at`.

```json
["rotation_replacement", "latest_key_assigned"]
```

### C.2 Nonce selection

1. **report_override** — when Appendix D names an explicit nonce override,
   that 12-byte value must be used even if key rotation later changes the
   operative key version for the frame.
2. **db_override** — when no Appendix D entry exists for the frame, a
   `nonce_override_registered` audit row is operative only if its `key_version`
   equals the operative key version after key-selection precedence (including
   any non-rescinded `key_rotated` replacement). A registration tied to a
   superseded key version must be ignored once rotation changes the operative
   version — do not reuse the override bytes after rotation. When rotation
   changes the operative key version, a later registration for the new version
   may become operative; a later registration that still names a superseded key
   version must not win over that match even if its `recorded_at` is greater.

   A `nonce_override_revoked` event voids every prior `nonce_override_registered`
   row for the same frame whose `nonce_override_hex` equals the revocation's
   `nonce_override_hex`. After excluding revoked registrations, the latest
   remaining `nonce_override_registered` row by `recorded_at` is eligible —
   but still subject to the operative key-version match above.

   A `nonce_override_amended` event voids every prior registration whose
   `nonce_override_hex` equals the amendment's `supersedes_nonce_hex`, then
   introduces the amendment's own `nonce_override_hex` as a new eligible row
   at that timestamp. A later `nonce_override_registered` row may register
   the same bytes again — re-registration after amendment is operative and
   must not be treated as permanently void.
3. **derived_sha256_prefix** — otherwise derive the nonce as the first 12 bytes
   of SHA-256(frame_id + ':' + key_version).

```json
["report_override", "db_override", "derived_sha256_prefix"]
```

The derived-nonce rule in prose: SHA-256(frame_id + ':' + key_version), first 12 bytes.

## Appendix D (draft — superseded April 2026 circulation)

A withdrawn draft listed nonce overrides that were never operative.
They must not be used for reproduction.

Withdrawn draft value for frm-007: `DEADBEEF0000000000000000`.
Withdrawn draft value for frm-010: `FEEDFACECAFE000000000001`.

## Appendix D — Registered nonce overrides

Five frames carry an explicit nonce override in this appendix. Every override
listed here must be transcribed; a reader that captures only the first few will
derive a wrong nonce for the others and fail authentication. When a frame
section lists more than one operative override line, the last operative
registration in that section wins.

### D.1 frm-003 (charlie-channel)

The operative nonce override for frm-003 is `A7C3E91B4D2F8065E1B9C0A3`.

This override was registered after a vault ceremony mismatch and must be used
instead of the derived nonce when authenticating the charlie-channel GIF frame.

### D.2 frm-006 (foxtrot-channel)

The operative nonce override for frm-006 is `0102030405060708090A0B0C`.

Superseded registration — withdrawn before sign-off.

The operative nonce override for frm-006 is `3F08D5621CA4790BEE17F2D8`.

Like D.1, this 12-byte value supersedes the derived nonce for the foxtrot-channel
frame and must be used verbatim when authenticating its GIF payload.

### D.3 frm-010 (juliet-channel)

The operative nonce override for frm-010 is `0A1B2C3D4E5F60718293A4B5`.

This 12-byte value supersedes the derived nonce for the juliet-channel frame.

### D.4 frm-015 (oscar-channel)

The operative nonce override for frm-015 is `13579BDF2468ACE024681ACE`.

This override remains operative after key rotation for oscar-channel — use the
report value verbatim, not a nonce re-derived for the post-rotation key version.

### D.5 frm-022 (whiskey-channel)

The operative nonce override for frm-022 is `E1F2A3B4C5D67890ABCDEF01`.

This override remains operative after key rotation for whiskey-channel and
must not be replaced by a later SQLite registration with different bytes.

## Appendix D — Post-review errata (withdrawn 2026-06-15)

Circulated errata after sign-off; withdrawn before reproduction use.

The operative nonce override for frm-003 is `DEADBEEFDEADBEEFDEADBEEF`.
The operative nonce override for frm-006 is `CAFEBABECAFEBABECAFEBABE`.
The operative nonce override for frm-010 is `FEEDFACEFEEDFACEFEEDFACE`.
The operative nonce override for frm-015 is `BADC0FFEBADC0FFEBADC0FFE`.
The operative nonce override for frm-022 is `DEADBEEF1234567890ABCDEF`.

