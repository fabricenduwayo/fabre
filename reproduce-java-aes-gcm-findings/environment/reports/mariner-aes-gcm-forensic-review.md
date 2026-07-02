# Mariner AES-GCM forensic media review — mid-year 2026

## Findings overview

Review date: 2026-06-01.

All 24 in-scope GIF frame payloads authenticate under AES-256-GCM when the
exception rules in Appendix C and the nonce overrides in Appendix D are applied.

- authenticated: 24
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

Forensic background 22: incident response playbook work on xray-channel (frm-023) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-78c04fc8.

Reviewer checklist item 23: confirm frm-024 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the yankee-channel payload embedded at GIF index 24. Ref: FORE-498d018d.

Stakeholder summary 24: team-vault owns remediation for frm-001. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-0c1a4ba3.

Telemetry cross-check 25: monitoring ticket MON-00025 for frm-002 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-fee4e6bb.

Cipher review 26: AES-256-GCM on frm-003 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-09f36d0f.

Appendix cross-ref 27: readers reconciling frm-004 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-9e6e0ebf.

Vault ceremony 28: channel frm-005 (echo-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-823b4ada.

Chain-of-custody note 29 for frm-006: the GIF extension block labelled MRNR/CRYPTO1 on index 6 is the authoritative ciphertext carrier for foxtrot-channel. Earlier draft captures in ticket FORE-0029 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-8e8fc716.

Governance review 30: GIF steganography review policy for frm-007 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-ea272d04.

Incident cross-reference 31: during AES-GCM authentication tag handling triage on frm-008, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-419d19c9.

Media-ingest log 32: frame frm-009 at GIF index 9 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-37301bd3.

Audit-ledger commentary 33: SQLite rows for frm-010 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-d5200c68.

Nonce-uniqueness memo 34: default nonces for frm-011 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-d19c8512.

Key-rotation briefing 35: when frm-012 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-038a7226.

Forensic background 36: incident response playbook work on mike-channel (frm-013) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-cb152f68.

Reviewer checklist item 37: confirm frm-014 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the november-channel payload embedded at GIF index 14. Ref: FORE-56ec6092.
Review date: 2026-07-15. (Superseded draft circulation — not operative.)

Stakeholder summary 38: team-vault owns remediation for frm-015. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-8d41bb07.

Telemetry cross-check 39: monitoring ticket MON-00039 for frm-016 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-f619c1bd.

Cipher review 40: AES-256-GCM on frm-017 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-3ddaf0c5.

Appendix cross-ref 41: readers reconciling frm-018 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-c6994cba.

Vault ceremony 42: channel frm-019 (tango-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-6c14806f.

Chain-of-custody note 43 for frm-020: the GIF extension block labelled MRNR/CRYPTO1 on index 20 is the authoritative ciphertext carrier for uniform-channel. Earlier draft captures in ticket FORE-0043 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-47285306.

Governance review 44: GIF steganography review policy for frm-021 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-ac30db5f.

Incident cross-reference 45: during AES-GCM authentication tag handling triage on frm-022, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-c9693c37.

Media-ingest log 46: frame frm-023 at GIF index 23 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-4cbdc317.

Audit-ledger commentary 47: SQLite rows for frm-024 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-1c067efe.

Nonce-uniqueness memo 48: default nonces for frm-001 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-4b10a4c5.

Key-rotation briefing 49: when frm-002 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-01333f50.

Forensic background 50: incident response playbook work on charlie-channel (frm-003) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-7cc651d0.

Reviewer checklist item 51: confirm frm-004 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the delta-channel payload embedded at GIF index 4. Ref: FORE-e7532c4f.

Stakeholder summary 52: team-vault owns remediation for frm-005. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-ac82c079.

Telemetry cross-check 53: monitoring ticket MON-00053 for frm-006 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-d684770f.

Cipher review 54: AES-256-GCM on frm-007 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-70e9cacb.

Appendix cross-ref 55: readers reconciling frm-008 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-32ce19f3.

Vault ceremony 56: channel frm-009 (india-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-0b4f74a0.

Chain-of-custody note 57 for frm-010: the GIF extension block labelled MRNR/CRYPTO1 on index 10 is the authoritative ciphertext carrier for juliet-channel. Earlier draft captures in ticket FORE-0057 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-c5028dca.

Governance review 58: GIF steganography review policy for frm-011 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-471e1570.

Incident cross-reference 59: during AES-GCM authentication tag handling triage on frm-012, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-0238ff1b.

Media-ingest log 60: frame frm-013 at GIF index 13 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-4d82230b.

Audit-ledger commentary 61: SQLite rows for frm-014 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-35ccaec4.

Nonce-uniqueness memo 62: default nonces for frm-015 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-cc937d03.

Key-rotation briefing 63: when frm-016 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-a319de4e.

Forensic background 64: incident response playbook work on quebec-channel (frm-017) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-f6fa2852.

Reviewer checklist item 65: confirm frm-018 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the sierra-channel payload embedded at GIF index 18. Ref: FORE-4d8c49e4.

Stakeholder summary 66: team-vault owns remediation for frm-019. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-1d0931e0.

Telemetry cross-check 67: monitoring ticket MON-00067 for frm-020 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-31c85b83.

Cipher review 68: AES-256-GCM on frm-021 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-fa3967ec.

Appendix cross-ref 69: readers reconciling frm-022 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-e2d2bca7.

Vault ceremony 70: channel frm-023 (xray-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-3a1b35cb.

Chain-of-custody note 71 for frm-024: the GIF extension block labelled MRNR/CRYPTO1 on index 24 is the authoritative ciphertext carrier for yankee-channel. Earlier draft captures in ticket FORE-0071 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-06b2f3aa.

Governance review 72: GIF steganography review policy for frm-001 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-39c1fd6f.

Incident cross-reference 73: during AES-GCM authentication tag handling triage on frm-002, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-93ec021f.

Media-ingest log 74: frame frm-003 at GIF index 2 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-0b21c5ed.
Review date: 2026-07-15. (Superseded draft circulation — not operative.)

Audit-ledger commentary 75: SQLite rows for frm-004 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-cec65572.

Nonce-uniqueness memo 76: default nonces for frm-005 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-271f4060.

Key-rotation briefing 77: when frm-006 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-4765a325.

Forensic background 78: incident response playbook work on golf-channel (frm-007) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-21358ec3.

Reviewer checklist item 79: confirm frm-008 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the hotel-channel payload embedded at GIF index 8. Ref: FORE-d6a140c7.

Stakeholder summary 80: team-vault owns remediation for frm-009. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-40177cfc.

Telemetry cross-check 81: monitoring ticket MON-00081 for frm-010 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-4849e63a.

Cipher review 82: AES-256-GCM on frm-011 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-1ccee05e.

Appendix cross-ref 83: readers reconciling frm-012 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-1cbd852e.

Vault ceremony 84: channel frm-013 (mike-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-7013614b.

Chain-of-custody note 85 for frm-014: the GIF extension block labelled MRNR/CRYPTO1 on index 14 is the authoritative ciphertext carrier for november-channel. Earlier draft captures in ticket FORE-0085 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-84a1de3b.

Governance review 86: GIF steganography review policy for frm-015 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-fd9981f1.

Incident cross-reference 87: during AES-GCM authentication tag handling triage on frm-016, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-101b16cb.

Media-ingest log 88: frame frm-017 at GIF index 17 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-f06ee187.

Audit-ledger commentary 89: SQLite rows for frm-018 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-7d40d70c.

Nonce-uniqueness memo 90: default nonces for frm-019 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-63014ae5.

Key-rotation briefing 91: when frm-020 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-9f30bbbe.

Forensic background 92: incident response playbook work on victor-channel (frm-021) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-afa7bd93.

Reviewer checklist item 93: confirm frm-022 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the whiskey-channel payload embedded at GIF index 22. Ref: FORE-328fdd7e.

Stakeholder summary 94: team-vault owns remediation for frm-023. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-6e5e5c12.

Telemetry cross-check 95: monitoring ticket MON-00095 for frm-024 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-62832891.

Cipher review 96: AES-256-GCM on frm-001 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-13e7027a.

Appendix cross-ref 97: readers reconciling frm-002 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-4b6867ff.

Vault ceremony 98: channel frm-003 (charlie-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-1b465fc2.

Chain-of-custody note 99 for frm-004: the GIF extension block labelled MRNR/CRYPTO1 on index 4 is the authoritative ciphertext carrier for delta-channel. Earlier draft captures in ticket FORE-0099 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-7ee1868e.

Governance review 100: GIF steganography review policy for frm-005 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-84d8391f.

Incident cross-reference 101: during AES-GCM authentication tag handling triage on frm-006, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-a4fcfc38.

Media-ingest log 102: frame frm-007 at GIF index 7 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-cd2e8239.

Audit-ledger commentary 103: SQLite rows for frm-008 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-568d84b4.

Nonce-uniqueness memo 104: default nonces for frm-009 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-37c7db8f.

Key-rotation briefing 105: when frm-010 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-ff3890f9.

Forensic background 106: incident response playbook work on kilo-channel (frm-011) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-0021dd79.

Reviewer checklist item 107: confirm frm-012 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the lima-channel payload embedded at GIF index 12. Ref: FORE-07e8fd46.

Stakeholder summary 108: team-vault owns remediation for frm-013. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-21578735.

Telemetry cross-check 109: monitoring ticket MON-00109 for frm-014 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-32faf51b.

Cipher review 110: AES-256-GCM on frm-015 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-b7111055.

Appendix cross-ref 111: readers reconciling frm-016 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-9930e62f.
Review date: 2026-07-15. (Superseded draft circulation — not operative.)

Vault ceremony 112: channel frm-017 (quebec-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-1912a90e.

Chain-of-custody note 113 for frm-018: the GIF extension block labelled MRNR/CRYPTO1 on index 18 is the authoritative ciphertext carrier for sierra-channel. Earlier draft captures in ticket FORE-0113 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-08f392b9.

Governance review 114: GIF steganography review policy for frm-019 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-29da3bc1.

Incident cross-reference 115: during AES-GCM authentication tag handling triage on frm-020, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-89a0e88c.

Media-ingest log 116: frame frm-021 at GIF index 21 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-01ed54c8.

Audit-ledger commentary 117: SQLite rows for frm-022 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-53cf3186.

Nonce-uniqueness memo 118: default nonces for frm-023 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-37ba87a8.

Key-rotation briefing 119: when frm-024 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-3a5e8d8e.

Forensic background 120: incident response playbook work on alpha-channel (frm-001) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-74a2fcc5.

Reviewer checklist item 121: confirm frm-002 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the bravo-channel payload embedded at GIF index 1. Ref: FORE-61c2ca8f.

Stakeholder summary 122: team-vault owns remediation for frm-003. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-1f10056c.

Telemetry cross-check 123: monitoring ticket MON-00123 for frm-004 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-05656b5f.

Cipher review 124: AES-256-GCM on frm-005 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-1290bd92.

Appendix cross-ref 125: readers reconciling frm-006 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-581ef755.

Vault ceremony 126: channel frm-007 (golf-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-e412cf1e.

Chain-of-custody note 127 for frm-008: the GIF extension block labelled MRNR/CRYPTO1 on index 8 is the authoritative ciphertext carrier for hotel-channel. Earlier draft captures in ticket FORE-0127 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-1a3fe82b.

Governance review 128: GIF steganography review policy for frm-009 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-35b26e51.

Incident cross-reference 129: during AES-GCM authentication tag handling triage on frm-010, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-eff43a31.

Media-ingest log 130: frame frm-011 at GIF index 11 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-44d47299.

Audit-ledger commentary 131: SQLite rows for frm-012 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-3cc60e7c.

Nonce-uniqueness memo 132: default nonces for frm-013 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-85fda787.

Key-rotation briefing 133: when frm-014 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-c6304f85.

Forensic background 134: incident response playbook work on oscar-channel (frm-015) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-41e6bc09.

Reviewer checklist item 135: confirm frm-016 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the papa-channel payload embedded at GIF index 16. Ref: FORE-01c99a52.

Stakeholder summary 136: team-vault owns remediation for frm-017. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-f49abff6.

Telemetry cross-check 137: monitoring ticket MON-00137 for frm-018 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-25957f10.

Cipher review 138: AES-256-GCM on frm-019 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-7de272ce.

Appendix cross-ref 139: readers reconciling frm-020 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-1a4c8b63.

Vault ceremony 140: channel frm-021 (victor-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-d387f595.

Chain-of-custody note 141 for frm-022: the GIF extension block labelled MRNR/CRYPTO1 on index 22 is the authoritative ciphertext carrier for whiskey-channel. Earlier draft captures in ticket FORE-0141 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-a8507d75.

Governance review 142: GIF steganography review policy for frm-023 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-7733c5b0.

Incident cross-reference 143: during AES-GCM authentication tag handling triage on frm-024, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-8b0e4c9f.

Media-ingest log 144: frame frm-001 at GIF index 0 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-3c7fc927.

Audit-ledger commentary 145: SQLite rows for frm-002 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-51091b18.

Nonce-uniqueness memo 146: default nonces for frm-003 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-9794ea7b.

Key-rotation briefing 147: when frm-004 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-363b3f89.

Forensic background 148: incident response playbook work on echo-channel (frm-005) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-c9b15c56.
Review date: 2026-07-15. (Superseded draft circulation — not operative.)

Reviewer checklist item 149: confirm frm-006 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the foxtrot-channel payload embedded at GIF index 6. Ref: FORE-288ef2ea.

Stakeholder summary 150: team-vault owns remediation for frm-007. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-3baf57ef.

Telemetry cross-check 151: monitoring ticket MON-00151 for frm-008 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-5b93c1a8.

Cipher review 152: AES-256-GCM on frm-009 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-47439692.

Appendix cross-ref 153: readers reconciling frm-010 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-9bd9a4e6.

Vault ceremony 154: channel frm-011 (kilo-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-520f5a22.

Chain-of-custody note 155 for frm-012: the GIF extension block labelled MRNR/CRYPTO1 on index 12 is the authoritative ciphertext carrier for lima-channel. Earlier draft captures in ticket FORE-0155 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-e4e2c8a0.

Governance review 156: GIF steganography review policy for frm-013 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-9283b3b3.

Incident cross-reference 157: during AES-GCM authentication tag handling triage on frm-014, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-4e84c0ec.

Media-ingest log 158: frame frm-015 at GIF index 15 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-f83786d2.

Audit-ledger commentary 159: SQLite rows for frm-016 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-2052f087.

Nonce-uniqueness memo 160: default nonces for frm-017 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-e95bddfe.

Key-rotation briefing 161: when frm-018 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-290a6a3b.

Forensic background 162: incident response playbook work on tango-channel (frm-019) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-520acff6.

Reviewer checklist item 163: confirm frm-020 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the uniform-channel payload embedded at GIF index 20. Ref: FORE-3268a044.

Stakeholder summary 164: team-vault owns remediation for frm-021. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-e8f3033b.

Telemetry cross-check 165: monitoring ticket MON-00165 for frm-022 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-c072c688.

Cipher review 166: AES-256-GCM on frm-023 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-931ca131.

Appendix cross-ref 167: readers reconciling frm-024 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-026e75dc.

Vault ceremony 168: channel frm-001 (alpha-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-3653130a.

Chain-of-custody note 169 for frm-002: the GIF extension block labelled MRNR/CRYPTO1 on index 1 is the authoritative ciphertext carrier for bravo-channel. Earlier draft captures in ticket FORE-0169 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-b91cf8c3.

Governance review 170: GIF steganography review policy for frm-003 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-0bed176b.

Incident cross-reference 171: during AES-GCM authentication tag handling triage on frm-004, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-95de9a46.

Media-ingest log 172: frame frm-005 at GIF index 5 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-15abb7be.

Audit-ledger commentary 173: SQLite rows for frm-006 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-95cc2ac3.

Nonce-uniqueness memo 174: default nonces for frm-007 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-8cf82049.

Key-rotation briefing 175: when frm-008 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-db9aeb3d.

Forensic background 176: incident response playbook work on india-channel (frm-009) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-9ce03e66.

Reviewer checklist item 177: confirm frm-010 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the juliet-channel payload embedded at GIF index 10. Ref: FORE-4d7b7a70.

Stakeholder summary 178: team-vault owns remediation for frm-011. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-0ada7d6b.

Telemetry cross-check 179: monitoring ticket MON-00179 for frm-012 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-921ca038.

Cipher review 180: AES-256-GCM on frm-013 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-2320390c.

Appendix cross-ref 181: readers reconciling frm-014 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-dc68fd49.

Vault ceremony 182: channel frm-015 (oscar-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-caca682e.

Chain-of-custody note 183 for frm-016: the GIF extension block labelled MRNR/CRYPTO1 on index 16 is the authoritative ciphertext carrier for papa-channel. Earlier draft captures in ticket FORE-0183 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-cde00ee3.

Governance review 184: GIF steganography review policy for frm-017 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-eb908fa8.

Incident cross-reference 185: during AES-GCM authentication tag handling triage on frm-018, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-455deea8.
Review date: 2026-07-15. (Superseded draft circulation — not operative.)

Media-ingest log 186: frame frm-019 at GIF index 19 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-7058a8ac.

Audit-ledger commentary 187: SQLite rows for frm-020 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-6c2a79c5.

Nonce-uniqueness memo 188: default nonces for frm-021 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-c76a320c.

Key-rotation briefing 189: when frm-022 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-e5348ad4.

Forensic background 190: incident response playbook work on xray-channel (frm-023) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-91ac1b89.

Reviewer checklist item 191: confirm frm-024 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the yankee-channel payload embedded at GIF index 24. Ref: FORE-c11ad77b.

Stakeholder summary 192: team-vault owns remediation for frm-001. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-5210a60f.

Telemetry cross-check 193: monitoring ticket MON-00193 for frm-002 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-79cdb060.

Cipher review 194: AES-256-GCM on frm-003 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-88ec4a44.

Appendix cross-ref 195: readers reconciling frm-004 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-f3a4cdae.

Vault ceremony 196: channel frm-005 (echo-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-86235bd9.

Chain-of-custody note 197 for frm-006: the GIF extension block labelled MRNR/CRYPTO1 on index 6 is the authoritative ciphertext carrier for foxtrot-channel. Earlier draft captures in ticket FORE-0197 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-36b7d7fa.

Governance review 198: GIF steganography review policy for frm-007 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-c9f95d47.

Incident cross-reference 199: during AES-GCM authentication tag handling triage on frm-008, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-c0b09b92.

Media-ingest log 200: frame frm-009 at GIF index 9 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-4d5c5d40.

Audit-ledger commentary 201: SQLite rows for frm-010 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-77558276.

Nonce-uniqueness memo 202: default nonces for frm-011 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-ac2619a0.

Key-rotation briefing 203: when frm-012 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-c12dc34e.

Forensic background 204: incident response playbook work on mike-channel (frm-013) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-31d11cc4.

Reviewer checklist item 205: confirm frm-014 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the november-channel payload embedded at GIF index 14. Ref: FORE-8c084fd9.

Stakeholder summary 206: team-vault owns remediation for frm-015. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-d796c9b1.

Telemetry cross-check 207: monitoring ticket MON-00207 for frm-016 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-5e30588b.

Cipher review 208: AES-256-GCM on frm-017 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-d34f41e3.

Appendix cross-ref 209: readers reconciling frm-018 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-1831f156.

Vault ceremony 210: channel frm-019 (tango-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-05614a35.

Chain-of-custody note 211 for frm-020: the GIF extension block labelled MRNR/CRYPTO1 on index 20 is the authoritative ciphertext carrier for uniform-channel. Earlier draft captures in ticket FORE-0211 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-c63b6d5c.

Governance review 212: GIF steganography review policy for frm-021 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-af564ad0.

Incident cross-reference 213: during AES-GCM authentication tag handling triage on frm-022, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-169204f9.

Media-ingest log 214: frame frm-023 at GIF index 23 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-920f5e68.

Audit-ledger commentary 215: SQLite rows for frm-024 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-b04b5c5f.

Nonce-uniqueness memo 216: default nonces for frm-001 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-9388847c.

Key-rotation briefing 217: when frm-002 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-4bd31213.

Forensic background 218: incident response playbook work on charlie-channel (frm-003) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-d11f08c7.

Reviewer checklist item 219: confirm frm-004 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the delta-channel payload embedded at GIF index 4. Ref: FORE-f8cdaa21.

Stakeholder summary 220: team-vault owns remediation for frm-005. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-3f7e78b1.

Telemetry cross-check 221: monitoring ticket MON-00221 for frm-006 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-1ba8815f.

Cipher review 222: AES-256-GCM on frm-007 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-e92c63e9.
Review date: 2026-07-15. (Superseded draft circulation — not operative.)

Appendix cross-ref 223: readers reconciling frm-008 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-e79f1f0f.

Vault ceremony 224: channel frm-009 (india-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-2599bf37.

Chain-of-custody note 225 for frm-010: the GIF extension block labelled MRNR/CRYPTO1 on index 10 is the authoritative ciphertext carrier for juliet-channel. Earlier draft captures in ticket FORE-0225 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-38c65fd9.

Governance review 226: GIF steganography review policy for frm-011 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-315dc4cd.

Incident cross-reference 227: during AES-GCM authentication tag handling triage on frm-012, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-def0cc30.

Media-ingest log 228: frame frm-013 at GIF index 13 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-e507f82d.

Audit-ledger commentary 229: SQLite rows for frm-014 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-7e9f4022.

Nonce-uniqueness memo 230: default nonces for frm-015 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-069d95c9.

Key-rotation briefing 231: when frm-016 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-849a913e.

Forensic background 232: incident response playbook work on quebec-channel (frm-017) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-207bc57f.

Reviewer checklist item 233: confirm frm-018 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the sierra-channel payload embedded at GIF index 18. Ref: FORE-53dcbd29.

Stakeholder summary 234: team-vault owns remediation for frm-019. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-9eb53870.

Telemetry cross-check 235: monitoring ticket MON-00235 for frm-020 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-dcdcec63.

Cipher review 236: AES-256-GCM on frm-021 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-3a71162a.

Appendix cross-ref 237: readers reconciling frm-022 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-b2165117.

Vault ceremony 238: channel frm-023 (xray-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-3c62c242.

Chain-of-custody note 239 for frm-024: the GIF extension block labelled MRNR/CRYPTO1 on index 24 is the authoritative ciphertext carrier for yankee-channel. Earlier draft captures in ticket FORE-0239 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-c2057ff4.

Governance review 240: GIF steganography review policy for frm-001 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-7653b19f.

Incident cross-reference 241: during AES-GCM authentication tag handling triage on frm-002, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-a99ce4f1.

Media-ingest log 242: frame frm-003 at GIF index 2 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-3e127cb2.

Audit-ledger commentary 243: SQLite rows for frm-004 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-18709f7a.

Nonce-uniqueness memo 244: default nonces for frm-005 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-6985bbcc.

Key-rotation briefing 245: when frm-006 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-c9233084.

Forensic background 246: incident response playbook work on golf-channel (frm-007) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-5b1a6a14.

Reviewer checklist item 247: confirm frm-008 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the hotel-channel payload embedded at GIF index 8. Ref: FORE-e6571d87.

Stakeholder summary 248: team-vault owns remediation for frm-009. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-ef19a91b.

Telemetry cross-check 249: monitoring ticket MON-00249 for frm-010 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-551d6f11.

Cipher review 250: AES-256-GCM on frm-011 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-a6d992ca.

Appendix cross-ref 251: readers reconciling frm-012 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-9a60d420.

Vault ceremony 252: channel frm-013 (mike-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-73906dcf.

Chain-of-custody note 253 for frm-014: the GIF extension block labelled MRNR/CRYPTO1 on index 14 is the authoritative ciphertext carrier for november-channel. Earlier draft captures in ticket FORE-0253 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-e0aee521.

Governance review 254: GIF steganography review policy for frm-015 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-541d481e.

Incident cross-reference 255: during AES-GCM authentication tag handling triage on frm-016, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-088798a9.

Media-ingest log 256: frame frm-017 at GIF index 17 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-b84c89f0.

Audit-ledger commentary 257: SQLite rows for frm-018 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-f7337b9d.

Nonce-uniqueness memo 258: default nonces for frm-019 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-e1d0cf89.

Key-rotation briefing 259: when frm-020 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-6f916e65.
Review date: 2026-07-15. (Superseded draft circulation — not operative.)

Forensic background 260: incident response playbook work on victor-channel (frm-021) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-290b7dea.

Reviewer checklist item 261: confirm frm-022 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the whiskey-channel payload embedded at GIF index 22. Ref: FORE-23a0004e.

Stakeholder summary 262: team-vault owns remediation for frm-023. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-8d0e0eb9.

Telemetry cross-check 263: monitoring ticket MON-00263 for frm-024 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-82493d6a.

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

Nonce-uniqueness memo 286: default nonces for frm-023 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-5723bc20.

Key-rotation briefing 287: when frm-024 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-72fcbbec.

Forensic background 288: incident response playbook work on alpha-channel (frm-001) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-9ceb973c.

Reviewer checklist item 289: confirm frm-002 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the bravo-channel payload embedded at GIF index 1. Ref: FORE-9f1890f0.

Stakeholder summary 290: team-vault owns remediation for frm-003. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-0c30c9a0.

Telemetry cross-check 291: monitoring ticket MON-00291 for frm-004 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-9f55a001.

Cipher review 292: AES-256-GCM on frm-005 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-eb6f6c06.

Appendix cross-ref 293: readers reconciling frm-006 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-72e039e8.

Vault ceremony 294: channel frm-007 (golf-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-12670c45.

Chain-of-custody note 295 for frm-008: the GIF extension block labelled MRNR/CRYPTO1 on index 8 is the authoritative ciphertext carrier for hotel-channel. Earlier draft captures in ticket FORE-0295 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-ffe3c6c7.

Governance review 296: GIF steganography review policy for frm-009 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-874e59ac.
Review date: 2026-07-15. (Superseded draft circulation — not operative.)

Incident cross-reference 297: during AES-GCM authentication tag handling triage on frm-010, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-22384a58.

Media-ingest log 298: frame frm-011 at GIF index 11 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-b33b511c.

Audit-ledger commentary 299: SQLite rows for frm-012 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-db058f07.

Nonce-uniqueness memo 300: default nonces for frm-013 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-c9153f63.

Key-rotation briefing 301: when frm-014 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-2bb08700.

Forensic background 302: incident response playbook work on oscar-channel (frm-015) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-61d9257e.

Reviewer checklist item 303: confirm frm-016 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the papa-channel payload embedded at GIF index 16. Ref: FORE-70351c75.

Stakeholder summary 304: team-vault owns remediation for frm-017. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-a18eda32.

Telemetry cross-check 305: monitoring ticket MON-00305 for frm-018 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-2bf0c3b5.

Cipher review 306: AES-256-GCM on frm-019 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-45f52b04.

Appendix cross-ref 307: readers reconciling frm-020 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-8f74ecef.

Vault ceremony 308: channel frm-021 (victor-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-d2595724.

Chain-of-custody note 309 for frm-022: the GIF extension block labelled MRNR/CRYPTO1 on index 22 is the authoritative ciphertext carrier for whiskey-channel. Earlier draft captures in ticket FORE-0309 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-d7fff1a3.

Governance review 310: GIF steganography review policy for frm-023 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-fe2f99da.

Incident cross-reference 311: during AES-GCM authentication tag handling triage on frm-024, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-68206cb9.

Media-ingest log 312: frame frm-001 at GIF index 0 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-e8775fac.

Audit-ledger commentary 313: SQLite rows for frm-002 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-a3c971e3.

Nonce-uniqueness memo 314: default nonces for frm-003 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-a09717eb.

Key-rotation briefing 315: when frm-004 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-7681fe1e.

Forensic background 316: incident response playbook work on echo-channel (frm-005) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-91017f5f.

Reviewer checklist item 317: confirm frm-006 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the foxtrot-channel payload embedded at GIF index 6. Ref: FORE-a25470a9.

Stakeholder summary 318: team-vault owns remediation for frm-007. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-974f93fd.

Telemetry cross-check 319: monitoring ticket MON-00319 for frm-008 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-40a16256.

Cipher review 320: AES-256-GCM on frm-009 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-0128c5bb.

Appendix cross-ref 321: readers reconciling frm-010 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-82ebab08.

Vault ceremony 322: channel frm-011 (kilo-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-f4db5b17.

Chain-of-custody note 323 for frm-012: the GIF extension block labelled MRNR/CRYPTO1 on index 12 is the authoritative ciphertext carrier for lima-channel. Earlier draft captures in ticket FORE-0323 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-b7914d8f.

Governance review 324: GIF steganography review policy for frm-013 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-60a1b57b.

Incident cross-reference 325: during AES-GCM authentication tag handling triage on frm-014, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-758d8e80.

Media-ingest log 326: frame frm-015 at GIF index 15 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-f8f0612a.

Audit-ledger commentary 327: SQLite rows for frm-016 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-6d2bb147.

Nonce-uniqueness memo 328: default nonces for frm-017 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-2ff3c275.

Key-rotation briefing 329: when frm-018 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-2343be9e.

Forensic background 330: incident response playbook work on tango-channel (frm-019) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-07b4d99b.

Reviewer checklist item 331: confirm frm-020 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the uniform-channel payload embedded at GIF index 20. Ref: FORE-f427b8ac.

Stakeholder summary 332: team-vault owns remediation for frm-021. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-a3a77d71.

Telemetry cross-check 333: monitoring ticket MON-00333 for frm-022 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-4d3d456c.
Review date: 2026-07-15. (Superseded draft circulation — not operative.)

Cipher review 334: AES-256-GCM on frm-023 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-60597dff.

Appendix cross-ref 335: readers reconciling frm-024 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-eff0e559.

Vault ceremony 336: channel frm-001 (alpha-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-063b8de7.

Chain-of-custody note 337 for frm-002: the GIF extension block labelled MRNR/CRYPTO1 on index 1 is the authoritative ciphertext carrier for bravo-channel. Earlier draft captures in ticket FORE-0337 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-a471f398.

Governance review 338: GIF steganography review policy for frm-003 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-5652c8f3.

Incident cross-reference 339: during AES-GCM authentication tag handling triage on frm-004, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-df332402.

Media-ingest log 340: frame frm-005 at GIF index 5 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-fc27725e.

Audit-ledger commentary 341: SQLite rows for frm-006 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-48a88936.

Nonce-uniqueness memo 342: default nonces for frm-007 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-206363ab.

Key-rotation briefing 343: when frm-008 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-370bffb4.

Forensic background 344: incident response playbook work on india-channel (frm-009) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-6d1f14c9.

Reviewer checklist item 345: confirm frm-010 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the juliet-channel payload embedded at GIF index 10. Ref: FORE-7e40c443.

Stakeholder summary 346: team-vault owns remediation for frm-011. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-2addba36.

Telemetry cross-check 347: monitoring ticket MON-00347 for frm-012 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-11278c57.

Cipher review 348: AES-256-GCM on frm-013 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-7c4118da.

Appendix cross-ref 349: readers reconciling frm-014 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-ba2f7d9b.

Vault ceremony 350: channel frm-015 (oscar-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-b86cc960.

Chain-of-custody note 351 for frm-016: the GIF extension block labelled MRNR/CRYPTO1 on index 16 is the authoritative ciphertext carrier for papa-channel. Earlier draft captures in ticket FORE-0351 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-2b44a149.

Governance review 352: GIF steganography review policy for frm-017 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-cbb82f07.

Incident cross-reference 353: during AES-GCM authentication tag handling triage on frm-018, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-5d7b838b.

Media-ingest log 354: frame frm-019 at GIF index 19 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-47ef0df7.

Audit-ledger commentary 355: SQLite rows for frm-020 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-fe63aa38.

Nonce-uniqueness memo 356: default nonces for frm-021 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-50c3234f.

Key-rotation briefing 357: when frm-022 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-86f03669.

Forensic background 358: incident response playbook work on xray-channel (frm-023) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-23722fbc.

Reviewer checklist item 359: confirm frm-024 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the yankee-channel payload embedded at GIF index 24. Ref: FORE-a3188130.

Stakeholder summary 360: team-vault owns remediation for frm-001. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-f75bdaaa.

Telemetry cross-check 361: monitoring ticket MON-00361 for frm-002 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-fc4b04c7.

Cipher review 362: AES-256-GCM on frm-003 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-ee632db9.

Appendix cross-ref 363: readers reconciling frm-004 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-84f04fae.

Vault ceremony 364: channel frm-005 (echo-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-eda64e8c.

Chain-of-custody note 365 for frm-006: the GIF extension block labelled MRNR/CRYPTO1 on index 6 is the authoritative ciphertext carrier for foxtrot-channel. Earlier draft captures in ticket FORE-0365 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-720b37b5.

Governance review 366: GIF steganography review policy for frm-007 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-c864ee5d.

Incident cross-reference 367: during AES-GCM authentication tag handling triage on frm-008, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-b333d870.

Media-ingest log 368: frame frm-009 at GIF index 9 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-cf64bed6.

Audit-ledger commentary 369: SQLite rows for frm-010 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-a9ba288b.

Nonce-uniqueness memo 370: default nonces for frm-011 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-161fa18f.
Review date: 2026-07-15. (Superseded draft circulation — not operative.)

Key-rotation briefing 371: when frm-012 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-a3981c27.

Forensic background 372: incident response playbook work on mike-channel (frm-013) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-d1730e58.

Reviewer checklist item 373: confirm frm-014 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the november-channel payload embedded at GIF index 14. Ref: FORE-593ec4f6.

Stakeholder summary 374: team-vault owns remediation for frm-015. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-637bd9fa.

Telemetry cross-check 375: monitoring ticket MON-00375 for frm-016 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-991290a0.

Cipher review 376: AES-256-GCM on frm-017 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-ba93b2c6.

Appendix cross-ref 377: readers reconciling frm-018 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-2f0babf6.

Vault ceremony 378: channel frm-019 (tango-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-da2e4ec9.

Chain-of-custody note 379 for frm-020: the GIF extension block labelled MRNR/CRYPTO1 on index 20 is the authoritative ciphertext carrier for uniform-channel. Earlier draft captures in ticket FORE-0379 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-608c449e.

Governance review 380: GIF steganography review policy for frm-021 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-e3e1e25e.

Incident cross-reference 381: during AES-GCM authentication tag handling triage on frm-022, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-8f88d3cb.

Media-ingest log 382: frame frm-023 at GIF index 23 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-1219404e.

Audit-ledger commentary 383: SQLite rows for frm-024 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-c7bcefcc.

Nonce-uniqueness memo 384: default nonces for frm-001 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-c35a2a3b.

Key-rotation briefing 385: when frm-002 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-a71a0ad0.

Forensic background 386: incident response playbook work on charlie-channel (frm-003) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-362dac7a.

Reviewer checklist item 387: confirm frm-004 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the delta-channel payload embedded at GIF index 4. Ref: FORE-50c2e734.

Stakeholder summary 388: team-vault owns remediation for frm-005. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-7f97c7e8.

Telemetry cross-check 389: monitoring ticket MON-00389 for frm-006 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-56342309.

Cipher review 390: AES-256-GCM on frm-007 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-68c29de2.

Appendix cross-ref 391: readers reconciling frm-008 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-ee48322e.

Vault ceremony 392: channel frm-009 (india-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-1a5aeaaa.

Chain-of-custody note 393 for frm-010: the GIF extension block labelled MRNR/CRYPTO1 on index 10 is the authoritative ciphertext carrier for juliet-channel. Earlier draft captures in ticket FORE-0393 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-dbbd50ce.

Governance review 394: GIF steganography review policy for frm-011 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-5ec27526.

Incident cross-reference 395: during AES-GCM authentication tag handling triage on frm-012, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-131dc358.

Media-ingest log 396: frame frm-013 at GIF index 13 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-ea9fec9f.

Audit-ledger commentary 397: SQLite rows for frm-014 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-fd95dd41.

Nonce-uniqueness memo 398: default nonces for frm-015 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-3ed69f0a.

Key-rotation briefing 399: when frm-016 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-c306937f.

Forensic background 400: incident response playbook work on quebec-channel (frm-017) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-26d18232.

Reviewer checklist item 401: confirm frm-018 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the sierra-channel payload embedded at GIF index 18. Ref: FORE-8f459faa.

Stakeholder summary 402: team-vault owns remediation for frm-019. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-faea02b8.

Telemetry cross-check 403: monitoring ticket MON-00403 for frm-020 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-8e2772e9.

Cipher review 404: AES-256-GCM on frm-021 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-d53f1916.

Appendix cross-ref 405: readers reconciling frm-022 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-f83a47d8.

Vault ceremony 406: channel frm-023 (xray-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-de406725.

Chain-of-custody note 407 for frm-024: the GIF extension block labelled MRNR/CRYPTO1 on index 24 is the authoritative ciphertext carrier for yankee-channel. Earlier draft captures in ticket FORE-0407 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-ff1f21c1.
Review date: 2026-07-15. (Superseded draft circulation — not operative.)

Governance review 408: GIF steganography review policy for frm-001 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-1bf3e2f8.

Incident cross-reference 409: during AES-GCM authentication tag handling triage on frm-002, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-99052217.

Media-ingest log 410: frame frm-003 at GIF index 2 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-853056b9.

Audit-ledger commentary 411: SQLite rows for frm-004 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-a39c30e5.

Nonce-uniqueness memo 412: default nonces for frm-005 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-b4c3e841.

Key-rotation briefing 413: when frm-006 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-42eb8864.

Forensic background 414: incident response playbook work on golf-channel (frm-007) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-2486475d.

Reviewer checklist item 415: confirm frm-008 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the hotel-channel payload embedded at GIF index 8. Ref: FORE-2c6c5a68.

Stakeholder summary 416: team-vault owns remediation for frm-009. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-523567ed.

Telemetry cross-check 417: monitoring ticket MON-00417 for frm-010 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-b99dc1b8.

Cipher review 418: AES-256-GCM on frm-011 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-556a2f94.

Appendix cross-ref 419: readers reconciling frm-012 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-a0c2a667.

Vault ceremony 420: channel frm-013 (mike-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-ea9386bd.

Chain-of-custody note 421 for frm-014: the GIF extension block labelled MRNR/CRYPTO1 on index 14 is the authoritative ciphertext carrier for november-channel. Earlier draft captures in ticket FORE-0421 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-35afe96c.

Governance review 422: GIF steganography review policy for frm-015 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-2e2f9335.

Incident cross-reference 423: during AES-GCM authentication tag handling triage on frm-016, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-cb52463b.

Media-ingest log 424: frame frm-017 at GIF index 17 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-b5bc383a.

Audit-ledger commentary 425: SQLite rows for frm-018 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-be0ca3a4.

Nonce-uniqueness memo 426: default nonces for frm-019 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-407e4f20.

Key-rotation briefing 427: when frm-020 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-5f7dafdf.

Forensic background 428: incident response playbook work on victor-channel (frm-021) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-1246b17b.

Reviewer checklist item 429: confirm frm-022 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the whiskey-channel payload embedded at GIF index 22. Ref: FORE-c731d994.

Stakeholder summary 430: team-vault owns remediation for frm-023. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-4a5b318f.

Telemetry cross-check 431: monitoring ticket MON-00431 for frm-024 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-0d9b0a4b.

Cipher review 432: AES-256-GCM on frm-001 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-0ffade54.

Appendix cross-ref 433: readers reconciling frm-002 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-5934ec6c.

Vault ceremony 434: channel frm-003 (charlie-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-e7764362.

Chain-of-custody note 435 for frm-004: the GIF extension block labelled MRNR/CRYPTO1 on index 4 is the authoritative ciphertext carrier for delta-channel. Earlier draft captures in ticket FORE-0435 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-3485bd22.

Governance review 436: GIF steganography review policy for frm-005 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-7b86e76e.

Incident cross-reference 437: during AES-GCM authentication tag handling triage on frm-006, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-7818b6de.

Media-ingest log 438: frame frm-007 at GIF index 7 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-3b51e9f3.

Audit-ledger commentary 439: SQLite rows for frm-008 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-28e56bd3.

Nonce-uniqueness memo 440: default nonces for frm-009 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-3fdf2264.

Key-rotation briefing 441: when frm-010 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-67a05f53.

Forensic background 442: incident response playbook work on kilo-channel (frm-011) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-c55bd3d8.

Reviewer checklist item 443: confirm frm-012 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the lima-channel payload embedded at GIF index 12. Ref: FORE-f3e05855.

Stakeholder summary 444: team-vault owns remediation for frm-013. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-ad3e9b2f.
Review date: 2026-07-15. (Superseded draft circulation — not operative.)

Telemetry cross-check 445: monitoring ticket MON-00445 for frm-014 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-92dbda30.

Cipher review 446: AES-256-GCM on frm-015 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-a7662861.

Appendix cross-ref 447: readers reconciling frm-016 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-80cdcfea.

Vault ceremony 448: channel frm-017 (quebec-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-307d057a.

Chain-of-custody note 449 for frm-018: the GIF extension block labelled MRNR/CRYPTO1 on index 18 is the authoritative ciphertext carrier for sierra-channel. Earlier draft captures in ticket FORE-0449 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-4c839fba.

Governance review 450: GIF steganography review policy for frm-019 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-3b1dd9db.

Incident cross-reference 451: during AES-GCM authentication tag handling triage on frm-020, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-0b3ec09d.

Media-ingest log 452: frame frm-021 at GIF index 21 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-f49470b7.

Audit-ledger commentary 453: SQLite rows for frm-022 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-74f3ba0d.

Nonce-uniqueness memo 454: default nonces for frm-023 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-4e020be0.

Key-rotation briefing 455: when frm-024 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-d5133fcb.

Forensic background 456: incident response playbook work on alpha-channel (frm-001) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-3058e278.

Reviewer checklist item 457: confirm frm-002 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the bravo-channel payload embedded at GIF index 1. Ref: FORE-1ed026dd.

Stakeholder summary 458: team-vault owns remediation for frm-003. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-2c0cf94f.

Telemetry cross-check 459: monitoring ticket MON-00459 for frm-004 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-fcb85688.

Cipher review 460: AES-256-GCM on frm-005 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-93087610.

Appendix cross-ref 461: readers reconciling frm-006 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-6d6226c2.

Vault ceremony 462: channel frm-007 (golf-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-3f09dc69.

Chain-of-custody note 463 for frm-008: the GIF extension block labelled MRNR/CRYPTO1 on index 8 is the authoritative ciphertext carrier for hotel-channel. Earlier draft captures in ticket FORE-0463 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-9f76eb9c.

Governance review 464: GIF steganography review policy for frm-009 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-dec9258e.

Incident cross-reference 465: during AES-GCM authentication tag handling triage on frm-010, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-f8e63fb7.

Media-ingest log 466: frame frm-011 at GIF index 11 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-c666ae06.

Audit-ledger commentary 467: SQLite rows for frm-012 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-d0d370c8.

Nonce-uniqueness memo 468: default nonces for frm-013 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-86dd7a1c.

Key-rotation briefing 469: when frm-014 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-c3ecdfaa.

Forensic background 470: incident response playbook work on oscar-channel (frm-015) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-dd2f1bb1.

Reviewer checklist item 471: confirm frm-016 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the papa-channel payload embedded at GIF index 16. Ref: FORE-87d31ddb.

Stakeholder summary 472: team-vault owns remediation for frm-017. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-395c1f85.

Telemetry cross-check 473: monitoring ticket MON-00473 for frm-018 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-637f3f8b.

Cipher review 474: AES-256-GCM on frm-019 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-b8e5faf0.

Appendix cross-ref 475: readers reconciling frm-020 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-5eaf6cc7.

Vault ceremony 476: channel frm-021 (victor-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-6bb28050.

Chain-of-custody note 477 for frm-022: the GIF extension block labelled MRNR/CRYPTO1 on index 22 is the authoritative ciphertext carrier for whiskey-channel. Earlier draft captures in ticket FORE-0477 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-96ad6a9b.

Governance review 478: GIF steganography review policy for frm-023 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-e53bdcdd.

Incident cross-reference 479: during AES-GCM authentication tag handling triage on frm-024, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-7a8a6ae0.

Media-ingest log 480: frame frm-001 at GIF index 0 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-9647e556.

Audit-ledger commentary 481: SQLite rows for frm-002 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-43be9e14.
Review date: 2026-07-15. (Superseded draft circulation — not operative.)

Nonce-uniqueness memo 482: default nonces for frm-003 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-d7d4f4ec.

Key-rotation briefing 483: when frm-004 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-8f29139a.

Forensic background 484: incident response playbook work on echo-channel (frm-005) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-82a3b857.

Reviewer checklist item 485: confirm frm-006 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the foxtrot-channel payload embedded at GIF index 6. Ref: FORE-edcbf815.

Stakeholder summary 486: team-vault owns remediation for frm-007. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-76eeefc4.

Telemetry cross-check 487: monitoring ticket MON-00487 for frm-008 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-88ee15c1.

Cipher review 488: AES-256-GCM on frm-009 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-ae91c44c.

Appendix cross-ref 489: readers reconciling frm-010 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-950d69af.

Vault ceremony 490: channel frm-011 (kilo-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-7ddaaf15.

Chain-of-custody note 491 for frm-012: the GIF extension block labelled MRNR/CRYPTO1 on index 12 is the authoritative ciphertext carrier for lima-channel. Earlier draft captures in ticket FORE-0491 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-db93f16d.

Governance review 492: GIF steganography review policy for frm-013 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-cf83c5c6.

Incident cross-reference 493: during AES-GCM authentication tag handling triage on frm-014, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-67910de0.

Media-ingest log 494: frame frm-015 at GIF index 15 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-208a4015.

Audit-ledger commentary 495: SQLite rows for frm-016 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-661b8f6b.

Nonce-uniqueness memo 496: default nonces for frm-017 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-352277e1.

Key-rotation briefing 497: when frm-018 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-9ddf1a05.

Forensic background 498: incident response playbook work on tango-channel (frm-019) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-4fc44911.

Reviewer checklist item 499: confirm frm-020 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the uniform-channel payload embedded at GIF index 20. Ref: FORE-22e6ad1a.

Stakeholder summary 500: team-vault owns remediation for frm-021. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-daa1736a.

Telemetry cross-check 501: monitoring ticket MON-00501 for frm-022 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-caa25a99.

Cipher review 502: AES-256-GCM on frm-023 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-c9d1867f.

Appendix cross-ref 503: readers reconciling frm-024 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-8ecd8618.

Vault ceremony 504: channel frm-001 (alpha-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-f9f73d20.

Chain-of-custody note 505 for frm-002: the GIF extension block labelled MRNR/CRYPTO1 on index 1 is the authoritative ciphertext carrier for bravo-channel. Earlier draft captures in ticket FORE-0505 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-4b3584cb.

Governance review 506: GIF steganography review policy for frm-003 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-16f4961f.

Incident cross-reference 507: during AES-GCM authentication tag handling triage on frm-004, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-d7c73ce1.

Media-ingest log 508: frame frm-005 at GIF index 5 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-07c5f8e2.

Audit-ledger commentary 509: SQLite rows for frm-006 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-cbd2a807.

Nonce-uniqueness memo 510: default nonces for frm-007 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-32d94d22.

Key-rotation briefing 511: when frm-008 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-fd602a87.

Forensic background 512: incident response playbook work on india-channel (frm-009) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-831610ec.

Reviewer checklist item 513: confirm frm-010 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the juliet-channel payload embedded at GIF index 10. Ref: FORE-0bc0864e.

Stakeholder summary 514: team-vault owns remediation for frm-011. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-d81d0b67.

Telemetry cross-check 515: monitoring ticket MON-00515 for frm-012 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-a614d143.

Cipher review 516: AES-256-GCM on frm-013 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-d3765886.

Appendix cross-ref 517: readers reconciling frm-014 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-80a896b8.

Vault ceremony 518: channel frm-015 (oscar-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-5e69f618.
Review date: 2026-07-15. (Superseded draft circulation — not operative.)

Chain-of-custody note 519 for frm-016: the GIF extension block labelled MRNR/CRYPTO1 on index 16 is the authoritative ciphertext carrier for papa-channel. Earlier draft captures in ticket FORE-0519 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-91bfba3a.

Governance review 520: GIF steganography review policy for frm-017 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-98fba140.

Incident cross-reference 521: during AES-GCM authentication tag handling triage on frm-018, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-97fd80a8.

Media-ingest log 522: frame frm-019 at GIF index 19 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-a1acd9e4.

Audit-ledger commentary 523: SQLite rows for frm-020 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-678cb606.

Nonce-uniqueness memo 524: default nonces for frm-021 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-3c5221ce.

Key-rotation briefing 525: when frm-022 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-24f8adc2.

Forensic background 526: incident response playbook work on xray-channel (frm-023) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-3bbe4f45.

Reviewer checklist item 527: confirm frm-024 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the yankee-channel payload embedded at GIF index 24. Ref: FORE-509fa81e.

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

Media-ingest log 550: frame frm-023 at GIF index 23 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-2a2f328d.

Audit-ledger commentary 551: SQLite rows for frm-024 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-63ee2192.

Nonce-uniqueness memo 552: default nonces for frm-001 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-4283baa0.

Key-rotation briefing 553: when frm-002 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-101fb2fb.

Forensic background 554: incident response playbook work on charlie-channel (frm-003) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-867b9f98.

Reviewer checklist item 555: confirm frm-004 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the delta-channel payload embedded at GIF index 4. Ref: FORE-ba4e301b.
Review date: 2026-07-15. (Superseded draft circulation — not operative.)

Stakeholder summary 556: team-vault owns remediation for frm-005. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-15455569.

Telemetry cross-check 557: monitoring ticket MON-00557 for frm-006 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-876fd018.

Cipher review 558: AES-256-GCM on frm-007 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-8ecb94ea.

Appendix cross-ref 559: readers reconciling frm-008 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-04dfa2e2.

Vault ceremony 560: channel frm-009 (india-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-0f43b1cf.

Chain-of-custody note 561 for frm-010: the GIF extension block labelled MRNR/CRYPTO1 on index 10 is the authoritative ciphertext carrier for juliet-channel. Earlier draft captures in ticket FORE-0561 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-d6f6feb4.

Governance review 562: GIF steganography review policy for frm-011 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-c68cfc34.

Incident cross-reference 563: during AES-GCM authentication tag handling triage on frm-012, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-6949ab7a.

Media-ingest log 564: frame frm-013 at GIF index 13 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-26a4c278.

Audit-ledger commentary 565: SQLite rows for frm-014 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-5b0730ce.

Nonce-uniqueness memo 566: default nonces for frm-015 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-aad8dc54.

Key-rotation briefing 567: when frm-016 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-75ebb982.

Forensic background 568: incident response playbook work on quebec-channel (frm-017) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-0ac99c68.

Reviewer checklist item 569: confirm frm-018 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the sierra-channel payload embedded at GIF index 18. Ref: FORE-4f01f142.

Stakeholder summary 570: team-vault owns remediation for frm-019. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-f6ce31f5.

Telemetry cross-check 571: monitoring ticket MON-00571 for frm-020 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-23d6c6d7.

Cipher review 572: AES-256-GCM on frm-021 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-34fa6620.

Appendix cross-ref 573: readers reconciling frm-022 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-fefb69af.

Vault ceremony 574: channel frm-023 (xray-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-2e2c9570.

Chain-of-custody note 575 for frm-024: the GIF extension block labelled MRNR/CRYPTO1 on index 24 is the authoritative ciphertext carrier for yankee-channel. Earlier draft captures in ticket FORE-0575 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-f7ed9e3a.

Governance review 576: GIF steganography review policy for frm-001 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-bce95518.

Incident cross-reference 577: during AES-GCM authentication tag handling triage on frm-002, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-4fada6a0.

Media-ingest log 578: frame frm-003 at GIF index 2 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-dcd7178c.

Audit-ledger commentary 579: SQLite rows for frm-004 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-9384aab2.

Nonce-uniqueness memo 580: default nonces for frm-005 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-37305101.

Key-rotation briefing 581: when frm-006 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-c72a82bb.

Forensic background 582: incident response playbook work on golf-channel (frm-007) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-d599129f.

Reviewer checklist item 583: confirm frm-008 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the hotel-channel payload embedded at GIF index 8. Ref: FORE-f0d297bb.

Stakeholder summary 584: team-vault owns remediation for frm-009. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-3a409547.

Telemetry cross-check 585: monitoring ticket MON-00585 for frm-010 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-e1d7eec9.

Cipher review 586: AES-256-GCM on frm-011 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-3492c634.

Appendix cross-ref 587: readers reconciling frm-012 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-25d8b436.

Vault ceremony 588: channel frm-013 (mike-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-cadd397e.

Chain-of-custody note 589 for frm-014: the GIF extension block labelled MRNR/CRYPTO1 on index 14 is the authoritative ciphertext carrier for november-channel. Earlier draft captures in ticket FORE-0589 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-031e6ba1.

Governance review 590: GIF steganography review policy for frm-015 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-a8da1bba.

Incident cross-reference 591: during AES-GCM authentication tag handling triage on frm-016, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-c152ce9b.

Media-ingest log 592: frame frm-017 at GIF index 17 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-479b7b54.
Review date: 2026-07-15. (Superseded draft circulation — not operative.)

Audit-ledger commentary 593: SQLite rows for frm-018 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-4d009109.

Nonce-uniqueness memo 594: default nonces for frm-019 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-94a96e86.

Key-rotation briefing 595: when frm-020 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-97dfea7d.

Forensic background 596: incident response playbook work on victor-channel (frm-021) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-d3e65cab.

Reviewer checklist item 597: confirm frm-022 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the whiskey-channel payload embedded at GIF index 22. Ref: FORE-c7889842.

Stakeholder summary 598: team-vault owns remediation for frm-023. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-c89668ab.

Telemetry cross-check 599: monitoring ticket MON-00599 for frm-024 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-b728af5f.

Cipher review 600: AES-256-GCM on frm-001 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-1ddc8ac6.

Appendix cross-ref 601: readers reconciling frm-002 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-a917c404.

Vault ceremony 602: channel frm-003 (charlie-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-606850e4.

Chain-of-custody note 603 for frm-004: the GIF extension block labelled MRNR/CRYPTO1 on index 4 is the authoritative ciphertext carrier for delta-channel. Earlier draft captures in ticket FORE-0603 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-f65cd11e.

Governance review 604: GIF steganography review policy for frm-005 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-7954f4ce.

Incident cross-reference 605: during AES-GCM authentication tag handling triage on frm-006, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-57dd4bc1.

Media-ingest log 606: frame frm-007 at GIF index 7 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-75a49922.

Audit-ledger commentary 607: SQLite rows for frm-008 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-4ab60536.

Nonce-uniqueness memo 608: default nonces for frm-009 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-f4391d52.

Key-rotation briefing 609: when frm-010 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-0e1664f3.

Forensic background 610: incident response playbook work on kilo-channel (frm-011) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-b40391a1.

Reviewer checklist item 611: confirm frm-012 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the lima-channel payload embedded at GIF index 12. Ref: FORE-85ff53eb.

Stakeholder summary 612: team-vault owns remediation for frm-013. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-a0011239.

Telemetry cross-check 613: monitoring ticket MON-00613 for frm-014 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-3038a92e.

Cipher review 614: AES-256-GCM on frm-015 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-4b0b8ad9.

Appendix cross-ref 615: readers reconciling frm-016 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-93b8c1f7.

Vault ceremony 616: channel frm-017 (quebec-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-fffa6153.

Chain-of-custody note 617 for frm-018: the GIF extension block labelled MRNR/CRYPTO1 on index 18 is the authoritative ciphertext carrier for sierra-channel. Earlier draft captures in ticket FORE-0617 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-92f4ffa2.

Governance review 618: GIF steganography review policy for frm-019 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-2a6b9463.

Incident cross-reference 619: during AES-GCM authentication tag handling triage on frm-020, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-e9f7198a.

Media-ingest log 620: frame frm-021 at GIF index 21 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-e43842e3.

Audit-ledger commentary 621: SQLite rows for frm-022 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-55faa006.

Nonce-uniqueness memo 622: default nonces for frm-023 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-4e7e34cc.

Key-rotation briefing 623: when frm-024 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-a1b32ddc.

Forensic background 624: incident response playbook work on alpha-channel (frm-001) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-4b72c257.

Reviewer checklist item 625: confirm frm-002 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the bravo-channel payload embedded at GIF index 1. Ref: FORE-fbb3e791.

Stakeholder summary 626: team-vault owns remediation for frm-003. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-d6c7b8a9.

Telemetry cross-check 627: monitoring ticket MON-00627 for frm-004 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-1afb9657.

Cipher review 628: AES-256-GCM on frm-005 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-33e99299.

Appendix cross-ref 629: readers reconciling frm-006 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-11b46498.
Review date: 2026-07-15. (Superseded draft circulation — not operative.)

Vault ceremony 630: channel frm-007 (golf-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-f3e2d67b.

Chain-of-custody note 631 for frm-008: the GIF extension block labelled MRNR/CRYPTO1 on index 8 is the authoritative ciphertext carrier for hotel-channel. Earlier draft captures in ticket FORE-0631 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-43dd7d63.

Governance review 632: GIF steganography review policy for frm-009 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-9ad0bd19.

Incident cross-reference 633: during AES-GCM authentication tag handling triage on frm-010, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-f02c1e33.

Media-ingest log 634: frame frm-011 at GIF index 11 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-32ac8300.

Audit-ledger commentary 635: SQLite rows for frm-012 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-6afd37a7.

Nonce-uniqueness memo 636: default nonces for frm-013 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-b645c3d7.

Key-rotation briefing 637: when frm-014 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-dca18576.

Forensic background 638: incident response playbook work on oscar-channel (frm-015) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-68ac767f.

Reviewer checklist item 639: confirm frm-016 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the papa-channel payload embedded at GIF index 16. Ref: FORE-381986c7.

Stakeholder summary 640: team-vault owns remediation for frm-017. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-9595a4ba.

Telemetry cross-check 641: monitoring ticket MON-00641 for frm-018 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-159e137b.

Cipher review 642: AES-256-GCM on frm-019 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-e7556ae9.

Appendix cross-ref 643: readers reconciling frm-020 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-6818ee41.

Vault ceremony 644: channel frm-021 (victor-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-cc28fd1e.

Chain-of-custody note 645 for frm-022: the GIF extension block labelled MRNR/CRYPTO1 on index 22 is the authoritative ciphertext carrier for whiskey-channel. Earlier draft captures in ticket FORE-0645 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-1a2a9ed0.

Governance review 646: GIF steganography review policy for frm-023 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-58d29aa9.

Incident cross-reference 647: during AES-GCM authentication tag handling triage on frm-024, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-11265e69.

Media-ingest log 648: frame frm-001 at GIF index 0 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-414d54c0.

Audit-ledger commentary 649: SQLite rows for frm-002 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-b97e0273.

Nonce-uniqueness memo 650: default nonces for frm-003 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-1d3bc1da.

Key-rotation briefing 651: when frm-004 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-d2657146.

Forensic background 652: incident response playbook work on echo-channel (frm-005) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-4c913a41.

Reviewer checklist item 653: confirm frm-006 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the foxtrot-channel payload embedded at GIF index 6. Ref: FORE-e8f439ad.

Stakeholder summary 654: team-vault owns remediation for frm-007. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-a5c8cc30.

Telemetry cross-check 655: monitoring ticket MON-00655 for frm-008 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-f3338338.

Cipher review 656: AES-256-GCM on frm-009 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-897a6c77.

Appendix cross-ref 657: readers reconciling frm-010 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-934c52ee.

Vault ceremony 658: channel frm-011 (kilo-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-555ce7f8.

Chain-of-custody note 659 for frm-012: the GIF extension block labelled MRNR/CRYPTO1 on index 12 is the authoritative ciphertext carrier for lima-channel. Earlier draft captures in ticket FORE-0659 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-c224584d.

Governance review 660: GIF steganography review policy for frm-013 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-a07e5fdf.

Incident cross-reference 661: during AES-GCM authentication tag handling triage on frm-014, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-415ba0b4.

Media-ingest log 662: frame frm-015 at GIF index 15 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-07804b43.

Audit-ledger commentary 663: SQLite rows for frm-016 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-60bf3621.

Nonce-uniqueness memo 664: default nonces for frm-017 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-fb0f0b1c.

Key-rotation briefing 665: when frm-018 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-191ffb57.

Forensic background 666: incident response playbook work on tango-channel (frm-019) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-9d705ff8.
Review date: 2026-07-15. (Superseded draft circulation — not operative.)

Reviewer checklist item 667: confirm frm-020 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the uniform-channel payload embedded at GIF index 20. Ref: FORE-57d384ce.

Stakeholder summary 668: team-vault owns remediation for frm-021. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-a28a2346.

Telemetry cross-check 669: monitoring ticket MON-00669 for frm-022 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-80b7125e.

Cipher review 670: AES-256-GCM on frm-023 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-4c1bab8a.

Appendix cross-ref 671: readers reconciling frm-024 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-66b47730.

Vault ceremony 672: channel frm-001 (alpha-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-d73a6555.

Chain-of-custody note 673 for frm-002: the GIF extension block labelled MRNR/CRYPTO1 on index 1 is the authoritative ciphertext carrier for bravo-channel. Earlier draft captures in ticket FORE-0673 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-0ca22a68.

Governance review 674: GIF steganography review policy for frm-003 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-cfc25618.

Incident cross-reference 675: during AES-GCM authentication tag handling triage on frm-004, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-6690adf8.

Media-ingest log 676: frame frm-005 at GIF index 5 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-84e400c5.

Audit-ledger commentary 677: SQLite rows for frm-006 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-7bd580ca.

Nonce-uniqueness memo 678: default nonces for frm-007 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-6a73a395.

Key-rotation briefing 679: when frm-008 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-829fec2d.

Forensic background 680: incident response playbook work on india-channel (frm-009) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-40a44f40.

Reviewer checklist item 681: confirm frm-010 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the juliet-channel payload embedded at GIF index 10. Ref: FORE-dec35ba8.

Stakeholder summary 682: team-vault owns remediation for frm-011. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-2ed66465.

Telemetry cross-check 683: monitoring ticket MON-00683 for frm-012 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-e90f8761.

Cipher review 684: AES-256-GCM on frm-013 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-aed2092d.

Appendix cross-ref 685: readers reconciling frm-014 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-99805f9f.

Vault ceremony 686: channel frm-015 (oscar-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-6fb5c8ca.

Chain-of-custody note 687 for frm-016: the GIF extension block labelled MRNR/CRYPTO1 on index 16 is the authoritative ciphertext carrier for papa-channel. Earlier draft captures in ticket FORE-0687 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-a34f892e.

Governance review 688: GIF steganography review policy for frm-017 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-34375c30.

Incident cross-reference 689: during AES-GCM authentication tag handling triage on frm-018, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-3240a3d5.

Media-ingest log 690: frame frm-019 at GIF index 19 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-a3fc3744.

Audit-ledger commentary 691: SQLite rows for frm-020 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-02806c9c.

Nonce-uniqueness memo 692: default nonces for frm-021 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-f84ee9ec.

Key-rotation briefing 693: when frm-022 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-aa07410e.

Forensic background 694: incident response playbook work on xray-channel (frm-023) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-1925fc2c.

Reviewer checklist item 695: confirm frm-024 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the yankee-channel payload embedded at GIF index 24. Ref: FORE-48ea4c7b.

Stakeholder summary 696: team-vault owns remediation for frm-001. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-66efadb7.

Telemetry cross-check 697: monitoring ticket MON-00697 for frm-002 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-e3ca73d1.

Cipher review 698: AES-256-GCM on frm-003 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-778e6953.

Appendix cross-ref 699: readers reconciling frm-004 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-0ee2db74.

Vault ceremony 700: channel frm-005 (echo-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-969362a2.

Chain-of-custody note 701 for frm-006: the GIF extension block labelled MRNR/CRYPTO1 on index 6 is the authoritative ciphertext carrier for foxtrot-channel. Earlier draft captures in ticket FORE-0701 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-3208b16e.

Governance review 702: GIF steganography review policy for frm-007 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-b3b07f20.

Incident cross-reference 703: during AES-GCM authentication tag handling triage on frm-008, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-76ddadde.
Review date: 2026-07-15. (Superseded draft circulation — not operative.)

Media-ingest log 704: frame frm-009 at GIF index 9 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-72559ce7.

Audit-ledger commentary 705: SQLite rows for frm-010 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-59246014.

Nonce-uniqueness memo 706: default nonces for frm-011 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-0074aa1e.

Key-rotation briefing 707: when frm-012 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-6203eee8.

Forensic background 708: incident response playbook work on mike-channel (frm-013) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-21238f61.

Reviewer checklist item 709: confirm frm-014 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the november-channel payload embedded at GIF index 14. Ref: FORE-aca4a940.

Stakeholder summary 710: team-vault owns remediation for frm-015. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-1c222723.

Telemetry cross-check 711: monitoring ticket MON-00711 for frm-016 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-8c4a8dbd.

Cipher review 712: AES-256-GCM on frm-017 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-bd851a6e.

Appendix cross-ref 713: readers reconciling frm-018 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-56c1a47d.

Vault ceremony 714: channel frm-019 (tango-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-5d803bc1.

Chain-of-custody note 715 for frm-020: the GIF extension block labelled MRNR/CRYPTO1 on index 20 is the authoritative ciphertext carrier for uniform-channel. Earlier draft captures in ticket FORE-0715 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-6efdaf45.

Governance review 716: GIF steganography review policy for frm-021 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-6276463a.

Incident cross-reference 717: during AES-GCM authentication tag handling triage on frm-022, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-9f450da5.

Media-ingest log 718: frame frm-023 at GIF index 23 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-fda38c2e.

Audit-ledger commentary 719: SQLite rows for frm-024 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-7092a9b1.

Nonce-uniqueness memo 720: default nonces for frm-001 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-524c0591.

Key-rotation briefing 721: when frm-002 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-cff742e1.

Forensic background 722: incident response playbook work on charlie-channel (frm-003) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-999360bb.

Reviewer checklist item 723: confirm frm-004 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the delta-channel payload embedded at GIF index 4. Ref: FORE-55ddf263.

Stakeholder summary 724: team-vault owns remediation for frm-005. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-e0cbadb6.

Telemetry cross-check 725: monitoring ticket MON-00725 for frm-006 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-cb2b40f5.

Cipher review 726: AES-256-GCM on frm-007 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-aaa93e2c.

Appendix cross-ref 727: readers reconciling frm-008 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-6f388ba6.

Vault ceremony 728: channel frm-009 (india-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-fece7205.

Chain-of-custody note 729 for frm-010: the GIF extension block labelled MRNR/CRYPTO1 on index 10 is the authoritative ciphertext carrier for juliet-channel. Earlier draft captures in ticket FORE-0729 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-98cb29cd.

Governance review 730: GIF steganography review policy for frm-011 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-0868443a.

Incident cross-reference 731: during AES-GCM authentication tag handling triage on frm-012, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-1bee997a.

Media-ingest log 732: frame frm-013 at GIF index 13 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-897bb42f.

Audit-ledger commentary 733: SQLite rows for frm-014 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-820e48d3.

Nonce-uniqueness memo 734: default nonces for frm-015 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-411d121f.

Key-rotation briefing 735: when frm-016 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-d4fad750.

Forensic background 736: incident response playbook work on quebec-channel (frm-017) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-fe76f4c9.

Reviewer checklist item 737: confirm frm-018 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the sierra-channel payload embedded at GIF index 18. Ref: FORE-080d3531.

Stakeholder summary 738: team-vault owns remediation for frm-019. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-b033ef94.

Telemetry cross-check 739: monitoring ticket MON-00739 for frm-020 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-687ebd44.

Cipher review 740: AES-256-GCM on frm-021 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-e3d3b84a.
Review date: 2026-07-15. (Superseded draft circulation — not operative.)

Appendix cross-ref 741: readers reconciling frm-022 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-f39683ff.

Vault ceremony 742: channel frm-023 (xray-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-db600820.

Chain-of-custody note 743 for frm-024: the GIF extension block labelled MRNR/CRYPTO1 on index 24 is the authoritative ciphertext carrier for yankee-channel. Earlier draft captures in ticket FORE-0743 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-e1a767da.

Governance review 744: GIF steganography review policy for frm-001 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-11bc4c39.

Incident cross-reference 745: during AES-GCM authentication tag handling triage on frm-002, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-b40869b4.

Media-ingest log 746: frame frm-003 at GIF index 2 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-3c20188b.

Audit-ledger commentary 747: SQLite rows for frm-004 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-74b93d0e.

Nonce-uniqueness memo 748: default nonces for frm-005 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-c4caa742.

Key-rotation briefing 749: when frm-006 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-eca0ccdf.

Forensic background 750: incident response playbook work on golf-channel (frm-007) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-7fc0f767.

Reviewer checklist item 751: confirm frm-008 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the hotel-channel payload embedded at GIF index 8. Ref: FORE-43ba2804.

Stakeholder summary 752: team-vault owns remediation for frm-009. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-c112d9ab.

Telemetry cross-check 753: monitoring ticket MON-00753 for frm-010 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-e7c4e55c.

Cipher review 754: AES-256-GCM on frm-011 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-92f380ca.

Appendix cross-ref 755: readers reconciling frm-012 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-fb6b780f.

Vault ceremony 756: channel frm-013 (mike-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-3c73cf41.

Chain-of-custody note 757 for frm-014: the GIF extension block labelled MRNR/CRYPTO1 on index 14 is the authoritative ciphertext carrier for november-channel. Earlier draft captures in ticket FORE-0757 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-baf05e3f.

Governance review 758: GIF steganography review policy for frm-015 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-6d87f0f5.

Incident cross-reference 759: during AES-GCM authentication tag handling triage on frm-016, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-49bf4709.

Media-ingest log 760: frame frm-017 at GIF index 17 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-540cd9ef.

Audit-ledger commentary 761: SQLite rows for frm-018 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-660897bf.

Nonce-uniqueness memo 762: default nonces for frm-019 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-1db0341b.

Key-rotation briefing 763: when frm-020 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-0caacb1a.

Forensic background 764: incident response playbook work on victor-channel (frm-021) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-edaf2bf4.

Reviewer checklist item 765: confirm frm-022 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the whiskey-channel payload embedded at GIF index 22. Ref: FORE-2eb32877.

Stakeholder summary 766: team-vault owns remediation for frm-023. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-3a0894f8.

Telemetry cross-check 767: monitoring ticket MON-00767 for frm-024 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-e1ea6907.

Cipher review 768: AES-256-GCM on frm-001 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-eeee008d.

Appendix cross-ref 769: readers reconciling frm-002 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-ee49a098.

Vault ceremony 770: channel frm-003 (charlie-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-952db0b9.

Chain-of-custody note 771 for frm-004: the GIF extension block labelled MRNR/CRYPTO1 on index 4 is the authoritative ciphertext carrier for delta-channel. Earlier draft captures in ticket FORE-0771 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-7de157a6.

Governance review 772: GIF steganography review policy for frm-005 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-c249a299.

Incident cross-reference 773: during AES-GCM authentication tag handling triage on frm-006, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-140cc064.

Media-ingest log 774: frame frm-007 at GIF index 7 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-755fac67.

Audit-ledger commentary 775: SQLite rows for frm-008 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-9dbc18de.

Nonce-uniqueness memo 776: default nonces for frm-009 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-24ad9130.

Key-rotation briefing 777: when frm-010 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-3f2dd8ba.
Review date: 2026-07-15. (Superseded draft circulation — not operative.)

Forensic background 778: incident response playbook work on kilo-channel (frm-011) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-5e5c9159.

Reviewer checklist item 779: confirm frm-012 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the lima-channel payload embedded at GIF index 12. Ref: FORE-e3c4115e.

Stakeholder summary 780: team-vault owns remediation for frm-013. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-69b0cf01.

Telemetry cross-check 781: monitoring ticket MON-00781 for frm-014 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-960696f9.

Cipher review 782: AES-256-GCM on frm-015 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-228d3635.

Appendix cross-ref 783: readers reconciling frm-016 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-8332d8a0.

Vault ceremony 784: channel frm-017 (quebec-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-313e7760.

Chain-of-custody note 785 for frm-018: the GIF extension block labelled MRNR/CRYPTO1 on index 18 is the authoritative ciphertext carrier for sierra-channel. Earlier draft captures in ticket FORE-0785 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-e43f4d54.

Governance review 786: GIF steganography review policy for frm-019 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-74d8e84c.

Incident cross-reference 787: during AES-GCM authentication tag handling triage on frm-020, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-203faf2f.

Media-ingest log 788: frame frm-021 at GIF index 21 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-1889699b.

Audit-ledger commentary 789: SQLite rows for frm-022 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-05d9f746.

Nonce-uniqueness memo 790: default nonces for frm-023 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-0acdc39e.

Key-rotation briefing 791: when frm-024 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-74d96bc2.

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

Governance review 814: GIF steganography review policy for frm-023 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-5d967bf9.
Review date: 2026-07-15. (Superseded draft circulation — not operative.)

Incident cross-reference 815: during AES-GCM authentication tag handling triage on frm-024, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-49787bb9.

Media-ingest log 816: frame frm-001 at GIF index 0 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-75d660c1.

Audit-ledger commentary 817: SQLite rows for frm-002 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-7d61fca2.

Nonce-uniqueness memo 818: default nonces for frm-003 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-96ab7804.

Key-rotation briefing 819: when frm-004 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-0b2c870f.

Forensic background 820: incident response playbook work on echo-channel (frm-005) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-ece70c65.

Reviewer checklist item 821: confirm frm-006 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the foxtrot-channel payload embedded at GIF index 6. Ref: FORE-c375a335.

Stakeholder summary 822: team-vault owns remediation for frm-007. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-050dd39a.

Telemetry cross-check 823: monitoring ticket MON-00823 for frm-008 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-af894d31.

Cipher review 824: AES-256-GCM on frm-009 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-b9f03bf0.

Appendix cross-ref 825: readers reconciling frm-010 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-aaabffb1.

Vault ceremony 826: channel frm-011 (kilo-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-e973781f.

Chain-of-custody note 827 for frm-012: the GIF extension block labelled MRNR/CRYPTO1 on index 12 is the authoritative ciphertext carrier for lima-channel. Earlier draft captures in ticket FORE-0827 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-65bbdd48.

Governance review 828: GIF steganography review policy for frm-013 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-9c5922a7.

Incident cross-reference 829: during AES-GCM authentication tag handling triage on frm-014, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-c5d7d401.

Media-ingest log 830: frame frm-015 at GIF index 15 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-e72702a1.

Audit-ledger commentary 831: SQLite rows for frm-016 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-7ffe16ba.

Nonce-uniqueness memo 832: default nonces for frm-017 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-0c3b83e4.

Key-rotation briefing 833: when frm-018 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-9f6bf508.

Forensic background 834: incident response playbook work on tango-channel (frm-019) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-73cb3dd7.

Reviewer checklist item 835: confirm frm-020 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the uniform-channel payload embedded at GIF index 20. Ref: FORE-5c40a4ac.

Stakeholder summary 836: team-vault owns remediation for frm-021. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-b47e614c.

Telemetry cross-check 837: monitoring ticket MON-00837 for frm-022 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-75511851.

Cipher review 838: AES-256-GCM on frm-023 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-8075281e.

Appendix cross-ref 839: readers reconciling frm-024 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-68b61c81.

Vault ceremony 840: channel frm-001 (alpha-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-3b584c41.

Chain-of-custody note 841 for frm-002: the GIF extension block labelled MRNR/CRYPTO1 on index 1 is the authoritative ciphertext carrier for bravo-channel. Earlier draft captures in ticket FORE-0841 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-cc7dc766.

Governance review 842: GIF steganography review policy for frm-003 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-03caee96.

Incident cross-reference 843: during AES-GCM authentication tag handling triage on frm-004, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-64af0978.

Media-ingest log 844: frame frm-005 at GIF index 5 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-372338ae.

Audit-ledger commentary 845: SQLite rows for frm-006 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-ca03f142.

Nonce-uniqueness memo 846: default nonces for frm-007 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-2f879c86.

Key-rotation briefing 847: when frm-008 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-4b591bc3.

Forensic background 848: incident response playbook work on india-channel (frm-009) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-73828940.

Reviewer checklist item 849: confirm frm-010 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the juliet-channel payload embedded at GIF index 10. Ref: FORE-517bc372.

Stakeholder summary 850: team-vault owns remediation for frm-011. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-2447a968.

Telemetry cross-check 851: monitoring ticket MON-00851 for frm-012 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-a1ec1011.
Review date: 2026-07-15. (Superseded draft circulation — not operative.)

Cipher review 852: AES-256-GCM on frm-013 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-ba1a25be.

Appendix cross-ref 853: readers reconciling frm-014 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-28371a10.

Vault ceremony 854: channel frm-015 (oscar-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-72b2ec5b.

Chain-of-custody note 855 for frm-016: the GIF extension block labelled MRNR/CRYPTO1 on index 16 is the authoritative ciphertext carrier for papa-channel. Earlier draft captures in ticket FORE-0855 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-83ff512c.

Governance review 856: GIF steganography review policy for frm-017 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-361a7b10.

Incident cross-reference 857: during AES-GCM authentication tag handling triage on frm-018, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-4448b76d.

Media-ingest log 858: frame frm-019 at GIF index 19 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-7395b665.

Audit-ledger commentary 859: SQLite rows for frm-020 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-bf790242.

Nonce-uniqueness memo 860: default nonces for frm-021 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-4a582e59.

Key-rotation briefing 861: when frm-022 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-98ed70ce.

Forensic background 862: incident response playbook work on xray-channel (frm-023) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-18a3e06a.

Reviewer checklist item 863: confirm frm-024 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the yankee-channel payload embedded at GIF index 24. Ref: FORE-9ac4a4e6.

Stakeholder summary 864: team-vault owns remediation for frm-001. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-2fcd2467.

Telemetry cross-check 865: monitoring ticket MON-00865 for frm-002 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-e37ed1bc.

Cipher review 866: AES-256-GCM on frm-003 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-d183bccc.

Appendix cross-ref 867: readers reconciling frm-004 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-937908c3.

Vault ceremony 868: channel frm-005 (echo-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-aef71728.

Chain-of-custody note 869 for frm-006: the GIF extension block labelled MRNR/CRYPTO1 on index 6 is the authoritative ciphertext carrier for foxtrot-channel. Earlier draft captures in ticket FORE-0869 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-207335fd.

Governance review 870: GIF steganography review policy for frm-007 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-d111f7df.

Incident cross-reference 871: during AES-GCM authentication tag handling triage on frm-008, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-2dd0a233.

Media-ingest log 872: frame frm-009 at GIF index 9 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-b0e584c9.

Audit-ledger commentary 873: SQLite rows for frm-010 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-98123a41.

Nonce-uniqueness memo 874: default nonces for frm-011 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-e17d89e1.

Key-rotation briefing 875: when frm-012 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-caa5098c.

Forensic background 876: incident response playbook work on mike-channel (frm-013) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-26cd5ed0.

Reviewer checklist item 877: confirm frm-014 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the november-channel payload embedded at GIF index 14. Ref: FORE-57a8dffe.

Stakeholder summary 878: team-vault owns remediation for frm-015. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-968e099d.

Telemetry cross-check 879: monitoring ticket MON-00879 for frm-016 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-3e79c325.

Cipher review 880: AES-256-GCM on frm-017 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-889d126f.

Appendix cross-ref 881: readers reconciling frm-018 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-d2e91360.

Vault ceremony 882: channel frm-019 (tango-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-a79a9ad5.

Chain-of-custody note 883 for frm-020: the GIF extension block labelled MRNR/CRYPTO1 on index 20 is the authoritative ciphertext carrier for uniform-channel. Earlier draft captures in ticket FORE-0883 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-24821416.

Governance review 884: GIF steganography review policy for frm-021 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-f4ce3a32.

Incident cross-reference 885: during AES-GCM authentication tag handling triage on frm-022, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-5ffb7d65.

Media-ingest log 886: frame frm-023 at GIF index 23 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-c6372dae.

Audit-ledger commentary 887: SQLite rows for frm-024 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-ed12c19a.

Nonce-uniqueness memo 888: default nonces for frm-001 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-0156de95.
Review date: 2026-07-15. (Superseded draft circulation — not operative.)

Key-rotation briefing 889: when frm-002 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-8ea4bb5d.

Forensic background 890: incident response playbook work on charlie-channel (frm-003) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-92313a96.

Reviewer checklist item 891: confirm frm-004 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the delta-channel payload embedded at GIF index 4. Ref: FORE-ac56d874.

Stakeholder summary 892: team-vault owns remediation for frm-005. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-ed7fec18.

Telemetry cross-check 893: monitoring ticket MON-00893 for frm-006 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-38ba699d.

Cipher review 894: AES-256-GCM on frm-007 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-b2334ca8.

Appendix cross-ref 895: readers reconciling frm-008 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-604dff09.

Vault ceremony 896: channel frm-009 (india-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-011cd7d7.

Chain-of-custody note 897 for frm-010: the GIF extension block labelled MRNR/CRYPTO1 on index 10 is the authoritative ciphertext carrier for juliet-channel. Earlier draft captures in ticket FORE-0897 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-52ab234c.

Governance review 898: GIF steganography review policy for frm-011 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-3d255a23.

Incident cross-reference 899: during AES-GCM authentication tag handling triage on frm-012, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-2b70e51d.

Media-ingest log 900: frame frm-013 at GIF index 13 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-7dacf807.

Audit-ledger commentary 901: SQLite rows for frm-014 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-968559fb.

Nonce-uniqueness memo 902: default nonces for frm-015 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-32740305.

Key-rotation briefing 903: when frm-016 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-c2c9774b.

Forensic background 904: incident response playbook work on quebec-channel (frm-017) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-28460745.

Reviewer checklist item 905: confirm frm-018 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the sierra-channel payload embedded at GIF index 18. Ref: FORE-06349b5c.

Stakeholder summary 906: team-vault owns remediation for frm-019. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-5be3f20b.

Telemetry cross-check 907: monitoring ticket MON-00907 for frm-020 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-09411577.

Cipher review 908: AES-256-GCM on frm-021 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-5f97eff4.

Appendix cross-ref 909: readers reconciling frm-022 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-9e833a55.

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

### frm-023 — xray-channel

GIF index 23. Application extension MRNR/CRYPTO1.

Reviewer checklist item 230: confirm frm-023 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the xray-channel payload embedded at GIF index 23.

Stakeholder summary 231: team-forensics owns remediation for frm-023. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced.

Telemetry cross-check 232: monitoring ticket MON-00232 for frm-023 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values.

Cipher review 233: AES-256-GCM on frm-023 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory.

Appendix cross-ref 234: readers reconciling frm-023 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone.

Vault ceremony 235: channel frm-023 (xray-channel) was enrolled under the HSM provisioning audit programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings.

### frm-024 — yankee-channel

GIF index 24. Application extension MRNR/CRYPTO1.

Stakeholder summary 240: team-media owns remediation for frm-024. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced.

Telemetry cross-check 241: monitoring ticket MON-00241 for frm-024 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values.

Cipher review 242: AES-256-GCM on frm-024 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory.

Appendix cross-ref 243: readers reconciling frm-024 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone.

Vault ceremony 244: channel frm-024 (yankee-channel) was enrolled under the forensic media ingestion programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings.

Chain-of-custody note 245 for frm-024: the GIF extension block labelled MRNR/CRYPTO1 on index 24 is the authoritative ciphertext carrier for yankee-channel. Earlier draft captures in ticket FORE-0245 are explicitly superseded and must not be substituted during JDBC correlation.

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
- **frm-023**: `key_assigned`, `nonce_override_registered`, `nonce_override_replaced`, `nonce_override_replacement_rescinded`, `nonce_override_replaced`
- **frm-024**: `key_assigned`, `nonce_override_registered`, `key_rotated`, `nonce_override_registered`, `nonce_override_replaced`, `key_rotated`, `nonce_override_registered`

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

   A `nonce_override_replaced` event voids every prior registration whose
   `nonce_override_hex` equals the replacement's `supersedes_nonce_hex`, then
   introduces the replacement's own `nonce_override_hex` as a new eligible row
   at that timestamp.

   A `nonce_override_replacement_rescinded` event voids the replacement row
   whose `nonce_override_hex` equals the rescission's `supersedes_nonce_hex`,
   then re-introduces the rescission's `nonce_override_hex` as an eligible row
   — restoring the pre-replacement bytes without treating them as revoked.
   A later `nonce_override_replaced` event may supersede the restored bytes
   again; only the final surviving replacement chain determines the operative
   DB override.
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

