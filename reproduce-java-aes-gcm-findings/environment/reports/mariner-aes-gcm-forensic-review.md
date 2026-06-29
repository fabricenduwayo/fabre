# Mariner AES-GCM forensic media review — mid-year 2026

## Findings overview

Review date: 2026-06-01.

All 8 in-scope GIF frame payloads authenticate under AES-256-GCM when the
exception rules in Appendix C and the nonce overrides in Appendix D are applied.

- authenticated: 8
- auth_failed: 0

GIF fixture: `/app/fixtures/evidence.gif`. Audit DB:
`jdbc:sqlite:/app/data/forensic_audit.db`.

## Extended forensic background

Vault ceremony 0: channel frm-001 (alpha-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-7e501f42.

Chain-of-custody note 1 for frm-002: the GIF extension block labelled MRNR/CRYPTO1 on index 1 is the authoritative ciphertext carrier for bravo-channel. Earlier draft captures in ticket FORE-0001 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-bb3e682c.

Governance review 2: GIF steganography review policy for frm-003 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-baa95a03.

Incident cross-reference 3: during AES-GCM authentication tag handling triage on frm-004, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-e462d6ef.

Media-ingest log 4: frame frm-005 at GIF index 5 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-8a1eecc3.

Audit-ledger commentary 5: SQLite rows for frm-006 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-de921fac.

Nonce-uniqueness memo 6: default nonces for frm-007 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-a45ae7ca.

Key-rotation briefing 7: when frm-008 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-59f9c996.

Forensic background 8: incident response playbook work on alpha-channel (frm-001) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-5ec99e49.

Reviewer checklist item 9: confirm frm-002 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the bravo-channel payload embedded at GIF index 1. Ref: FORE-e2fed34c.

Stakeholder summary 10: team-vault owns remediation for frm-003. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-b0a76ae6.

Telemetry cross-check 11: monitoring ticket MON-00011 for frm-004 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-71b9902e.

Cipher review 12: AES-256-GCM on frm-005 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-a7843c5e.

Appendix cross-ref 13: readers reconciling frm-006 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-e957d9d3.

Vault ceremony 14: channel frm-007 (golf-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-c5974ffd.

Chain-of-custody note 15 for frm-008: the GIF extension block labelled MRNR/CRYPTO1 on index 8 is the authoritative ciphertext carrier for hotel-channel. Earlier draft captures in ticket FORE-0015 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-53506f60.

Governance review 16: GIF steganography review policy for frm-001 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-57958587.

Incident cross-reference 17: during AES-GCM authentication tag handling triage on frm-002, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-ad0f7dc2.

Media-ingest log 18: frame frm-003 at GIF index 2 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-0165accd.

Audit-ledger commentary 19: SQLite rows for frm-004 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-bdd6872d.

Nonce-uniqueness memo 20: default nonces for frm-005 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-57845c4e.

Key-rotation briefing 21: when frm-006 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-a4758233.

Forensic background 22: incident response playbook work on golf-channel (frm-007) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-2ea9a6db.

Reviewer checklist item 23: confirm frm-008 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the hotel-channel payload embedded at GIF index 8. Ref: FORE-97cf479f.

Stakeholder summary 24: team-vault owns remediation for frm-001. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-0c1a4ba3.

Telemetry cross-check 25: monitoring ticket MON-00025 for frm-002 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-fee4e6bb.

Cipher review 26: AES-256-GCM on frm-003 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-09f36d0f.

Appendix cross-ref 27: readers reconciling frm-004 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-9e6e0ebf.

Vault ceremony 28: channel frm-005 (echo-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-823b4ada.

Chain-of-custody note 29 for frm-006: the GIF extension block labelled MRNR/CRYPTO1 on index 6 is the authoritative ciphertext carrier for foxtrot-channel. Earlier draft captures in ticket FORE-0029 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-8e8fc716.

Governance review 30: GIF steganography review policy for frm-007 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-ea272d04.

Incident cross-reference 31: during AES-GCM authentication tag handling triage on frm-008, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-419d19c9.

Media-ingest log 32: frame frm-001 at GIF index 0 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-18295a7d.

Audit-ledger commentary 33: SQLite rows for frm-002 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-0ec990f2.

Nonce-uniqueness memo 34: default nonces for frm-003 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-92b5a417.

Key-rotation briefing 35: when frm-004 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-27c1c835.

Forensic background 36: incident response playbook work on echo-channel (frm-005) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-8bf934e1.

Reviewer checklist item 37: confirm frm-006 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the foxtrot-channel payload embedded at GIF index 6. Ref: FORE-5d06b907.

Stakeholder summary 38: team-vault owns remediation for frm-007. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-e387a7bb.

Telemetry cross-check 39: monitoring ticket MON-00039 for frm-008 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-ebbd74bb.

Cipher review 40: AES-256-GCM on frm-001 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-1d2bd2a3.

Appendix cross-ref 41: readers reconciling frm-002 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-dcf93590.

Vault ceremony 42: channel frm-003 (charlie-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-b19b26a7.

Chain-of-custody note 43 for frm-004: the GIF extension block labelled MRNR/CRYPTO1 on index 4 is the authoritative ciphertext carrier for delta-channel. Earlier draft captures in ticket FORE-0043 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-1739e5a2.

Governance review 44: GIF steganography review policy for frm-005 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-d8d6007a.

Incident cross-reference 45: during AES-GCM authentication tag handling triage on frm-006, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-a22639b1.

Media-ingest log 46: frame frm-007 at GIF index 7 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-20bcaef6.

Audit-ledger commentary 47: SQLite rows for frm-008 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-7e85daf8.

Nonce-uniqueness memo 48: default nonces for frm-001 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-4b10a4c5.

Key-rotation briefing 49: when frm-002 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-01333f50.

Forensic background 50: incident response playbook work on charlie-channel (frm-003) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-7cc651d0.

Reviewer checklist item 51: confirm frm-004 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the delta-channel payload embedded at GIF index 4. Ref: FORE-e7532c4f.

Stakeholder summary 52: team-vault owns remediation for frm-005. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-ac82c079.

Telemetry cross-check 53: monitoring ticket MON-00053 for frm-006 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-d684770f.

Cipher review 54: AES-256-GCM on frm-007 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-70e9cacb.

Appendix cross-ref 55: readers reconciling frm-008 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-32ce19f3.

Vault ceremony 56: channel frm-001 (alpha-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-8848c3aa.

Chain-of-custody note 57 for frm-002: the GIF extension block labelled MRNR/CRYPTO1 on index 1 is the authoritative ciphertext carrier for bravo-channel. Earlier draft captures in ticket FORE-0057 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-c576b9ce.

Governance review 58: GIF steganography review policy for frm-003 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-f06db964.

Incident cross-reference 59: during AES-GCM authentication tag handling triage on frm-004, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-c0f507e3.

Media-ingest log 60: frame frm-005 at GIF index 5 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-792b1399.

Audit-ledger commentary 61: SQLite rows for frm-006 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-2951a081.

Nonce-uniqueness memo 62: default nonces for frm-007 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-871c8796.

Key-rotation briefing 63: when frm-008 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-15cf6ab3.

Forensic background 64: incident response playbook work on alpha-channel (frm-001) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-b01af42d.

Reviewer checklist item 65: confirm frm-002 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the bravo-channel payload embedded at GIF index 1. Ref: FORE-d9454093.

Stakeholder summary 66: team-vault owns remediation for frm-003. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-dfdc864f.

Telemetry cross-check 67: monitoring ticket MON-00067 for frm-004 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-564f967e.

Cipher review 68: AES-256-GCM on frm-005 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-adb16e66.

Appendix cross-ref 69: readers reconciling frm-006 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-bb6c42a6.

Vault ceremony 70: channel frm-007 (golf-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-6734c4e0.

Chain-of-custody note 71 for frm-008: the GIF extension block labelled MRNR/CRYPTO1 on index 8 is the authoritative ciphertext carrier for hotel-channel. Earlier draft captures in ticket FORE-0071 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-e1cffe51.

Governance review 72: GIF steganography review policy for frm-001 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-39c1fd6f.

Incident cross-reference 73: during AES-GCM authentication tag handling triage on frm-002, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-93ec021f.

Media-ingest log 74: frame frm-003 at GIF index 2 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-0b21c5ed.

Audit-ledger commentary 75: SQLite rows for frm-004 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-cec65572.

Nonce-uniqueness memo 76: default nonces for frm-005 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-271f4060.

Key-rotation briefing 77: when frm-006 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-4765a325.

Forensic background 78: incident response playbook work on golf-channel (frm-007) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-21358ec3.

Reviewer checklist item 79: confirm frm-008 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the hotel-channel payload embedded at GIF index 8. Ref: FORE-d6a140c7.

Stakeholder summary 80: team-vault owns remediation for frm-001. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-a0bed83b.

Telemetry cross-check 81: monitoring ticket MON-00081 for frm-002 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-d008686e.

Cipher review 82: AES-256-GCM on frm-003 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-4a71a08c.

Appendix cross-ref 83: readers reconciling frm-004 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-de02d331.

Vault ceremony 84: channel frm-005 (echo-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-36dad900.

Chain-of-custody note 85 for frm-006: the GIF extension block labelled MRNR/CRYPTO1 on index 6 is the authoritative ciphertext carrier for foxtrot-channel. Earlier draft captures in ticket FORE-0085 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-b65da259.

Governance review 86: GIF steganography review policy for frm-007 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-5c742c44.

Incident cross-reference 87: during AES-GCM authentication tag handling triage on frm-008, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-a8ba7dd7.

Media-ingest log 88: frame frm-001 at GIF index 0 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-94c38590.

Audit-ledger commentary 89: SQLite rows for frm-002 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-d0887721.

Nonce-uniqueness memo 90: default nonces for frm-003 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-4478d9d4.

Key-rotation briefing 91: when frm-004 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-5adf0c56.

Forensic background 92: incident response playbook work on echo-channel (frm-005) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-93d38b06.

Reviewer checklist item 93: confirm frm-006 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the foxtrot-channel payload embedded at GIF index 6. Ref: FORE-cf2d7b56.

Stakeholder summary 94: team-vault owns remediation for frm-007. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-66893743.

Telemetry cross-check 95: monitoring ticket MON-00095 for frm-008 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-557da4e0.

Cipher review 96: AES-256-GCM on frm-001 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-13e7027a.

Appendix cross-ref 97: readers reconciling frm-002 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-4b6867ff.

Vault ceremony 98: channel frm-003 (charlie-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-1b465fc2.

Chain-of-custody note 99 for frm-004: the GIF extension block labelled MRNR/CRYPTO1 on index 4 is the authoritative ciphertext carrier for delta-channel. Earlier draft captures in ticket FORE-0099 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-7ee1868e.

Governance review 100: GIF steganography review policy for frm-005 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-84d8391f.

Incident cross-reference 101: during AES-GCM authentication tag handling triage on frm-006, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-a4fcfc38.

Media-ingest log 102: frame frm-007 at GIF index 7 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-cd2e8239.

Audit-ledger commentary 103: SQLite rows for frm-008 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-568d84b4.

Nonce-uniqueness memo 104: default nonces for frm-001 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-978cb8b4.

Key-rotation briefing 105: when frm-002 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-c341d7f0.

Forensic background 106: incident response playbook work on charlie-channel (frm-003) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-8ef64318.

Reviewer checklist item 107: confirm frm-004 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the delta-channel payload embedded at GIF index 4. Ref: FORE-c92e5ef5.

Stakeholder summary 108: team-vault owns remediation for frm-005. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-b5a749b6.

Telemetry cross-check 109: monitoring ticket MON-00109 for frm-006 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-d0a9c5b6.

Cipher review 110: AES-256-GCM on frm-007 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-0430f58e.

Appendix cross-ref 111: readers reconciling frm-008 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-241b2907.

Vault ceremony 112: channel frm-001 (alpha-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-b2ddd6df.

Chain-of-custody note 113 for frm-002: the GIF extension block labelled MRNR/CRYPTO1 on index 1 is the authoritative ciphertext carrier for bravo-channel. Earlier draft captures in ticket FORE-0113 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-7b74b315.

Governance review 114: GIF steganography review policy for frm-003 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-e9cdebd3.

Incident cross-reference 115: during AES-GCM authentication tag handling triage on frm-004, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-0257e927.

Media-ingest log 116: frame frm-005 at GIF index 5 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-66519e59.

Audit-ledger commentary 117: SQLite rows for frm-006 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-a64aa0c7.

Nonce-uniqueness memo 118: default nonces for frm-007 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-770c2afc.

Key-rotation briefing 119: when frm-008 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-a22cea15.

Forensic background 120: incident response playbook work on alpha-channel (frm-001) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-74a2fcc5.

Reviewer checklist item 121: confirm frm-002 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the bravo-channel payload embedded at GIF index 1. Ref: FORE-61c2ca8f.

Stakeholder summary 122: team-vault owns remediation for frm-003. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-1f10056c.

Telemetry cross-check 123: monitoring ticket MON-00123 for frm-004 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-05656b5f.

Cipher review 124: AES-256-GCM on frm-005 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-1290bd92.

Appendix cross-ref 125: readers reconciling frm-006 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-581ef755.

Vault ceremony 126: channel frm-007 (golf-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-e412cf1e.

Chain-of-custody note 127 for frm-008: the GIF extension block labelled MRNR/CRYPTO1 on index 8 is the authoritative ciphertext carrier for hotel-channel. Earlier draft captures in ticket FORE-0127 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-1a3fe82b.

Governance review 128: GIF steganography review policy for frm-001 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-24862abb.

Incident cross-reference 129: during AES-GCM authentication tag handling triage on frm-002, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-6dd155b5.

Media-ingest log 130: frame frm-003 at GIF index 2 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-7188bedc.

Audit-ledger commentary 131: SQLite rows for frm-004 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-d2f15478.

Nonce-uniqueness memo 132: default nonces for frm-005 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-13fdd2a6.

Key-rotation briefing 133: when frm-006 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-c6ad5fb4.

Forensic background 134: incident response playbook work on golf-channel (frm-007) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-98b10a76.

Reviewer checklist item 135: confirm frm-008 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the hotel-channel payload embedded at GIF index 8. Ref: FORE-fd3618fa.

Stakeholder summary 136: team-vault owns remediation for frm-001. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-f58a832b.

Telemetry cross-check 137: monitoring ticket MON-00137 for frm-002 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-f4afdd82.

Cipher review 138: AES-256-GCM on frm-003 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-50f1792d.

Appendix cross-ref 139: readers reconciling frm-004 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-75980a87.

Vault ceremony 140: channel frm-005 (echo-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-c8b144a0.

Chain-of-custody note 141 for frm-006: the GIF extension block labelled MRNR/CRYPTO1 on index 6 is the authoritative ciphertext carrier for foxtrot-channel. Earlier draft captures in ticket FORE-0141 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-7b8ff55f.

Governance review 142: GIF steganography review policy for frm-007 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-4a4d2fe0.

Incident cross-reference 143: during AES-GCM authentication tag handling triage on frm-008, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-53e2722b.

Media-ingest log 144: frame frm-001 at GIF index 0 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-3c7fc927.

Audit-ledger commentary 145: SQLite rows for frm-002 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-51091b18.

Nonce-uniqueness memo 146: default nonces for frm-003 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-9794ea7b.

Key-rotation briefing 147: when frm-004 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-363b3f89.

Forensic background 148: incident response playbook work on echo-channel (frm-005) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-c9b15c56.

Reviewer checklist item 149: confirm frm-006 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the foxtrot-channel payload embedded at GIF index 6. Ref: FORE-288ef2ea.

Stakeholder summary 150: team-vault owns remediation for frm-007. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-3baf57ef.

Telemetry cross-check 151: monitoring ticket MON-00151 for frm-008 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-5b93c1a8.

Cipher review 152: AES-256-GCM on frm-001 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-2c4cb8ba.

Appendix cross-ref 153: readers reconciling frm-002 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-85f2ee0f.

Vault ceremony 154: channel frm-003 (charlie-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-7328049d.

Chain-of-custody note 155 for frm-004: the GIF extension block labelled MRNR/CRYPTO1 on index 4 is the authoritative ciphertext carrier for delta-channel. Earlier draft captures in ticket FORE-0155 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-4178af8f.

Governance review 156: GIF steganography review policy for frm-005 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-a9a9f028.

Incident cross-reference 157: during AES-GCM authentication tag handling triage on frm-006, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-0746404a.

Media-ingest log 158: frame frm-007 at GIF index 7 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-d061bb4b.

Audit-ledger commentary 159: SQLite rows for frm-008 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-d402235c.

Nonce-uniqueness memo 160: default nonces for frm-001 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-997aed9a.

Key-rotation briefing 161: when frm-002 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-6e859ff1.

Forensic background 162: incident response playbook work on charlie-channel (frm-003) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-94d569f5.

Reviewer checklist item 163: confirm frm-004 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the delta-channel payload embedded at GIF index 4. Ref: FORE-e9419eff.

Stakeholder summary 164: team-vault owns remediation for frm-005. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-25f0045e.

Telemetry cross-check 165: monitoring ticket MON-00165 for frm-006 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-fa91461b.

Cipher review 166: AES-256-GCM on frm-007 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-3f13a2b2.

Appendix cross-ref 167: readers reconciling frm-008 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-86e8a5be.

Vault ceremony 168: channel frm-001 (alpha-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-3653130a.

Chain-of-custody note 169 for frm-002: the GIF extension block labelled MRNR/CRYPTO1 on index 1 is the authoritative ciphertext carrier for bravo-channel. Earlier draft captures in ticket FORE-0169 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-b91cf8c3.

Governance review 170: GIF steganography review policy for frm-003 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-0bed176b.

Incident cross-reference 171: during AES-GCM authentication tag handling triage on frm-004, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-95de9a46.

Media-ingest log 172: frame frm-005 at GIF index 5 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-15abb7be.

Audit-ledger commentary 173: SQLite rows for frm-006 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-95cc2ac3.

Nonce-uniqueness memo 174: default nonces for frm-007 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-8cf82049.

Key-rotation briefing 175: when frm-008 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-db9aeb3d.

Forensic background 176: incident response playbook work on alpha-channel (frm-001) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-f8ffca1e.

Reviewer checklist item 177: confirm frm-002 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the bravo-channel payload embedded at GIF index 1. Ref: FORE-bfec4834.

Stakeholder summary 178: team-vault owns remediation for frm-003. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-9774d582.

Telemetry cross-check 179: monitoring ticket MON-00179 for frm-004 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-37c85de2.

Cipher review 180: AES-256-GCM on frm-005 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-f644a131.

Appendix cross-ref 181: readers reconciling frm-006 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-a2625c96.

Vault ceremony 182: channel frm-007 (golf-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-21fac9c8.

Chain-of-custody note 183 for frm-008: the GIF extension block labelled MRNR/CRYPTO1 on index 8 is the authoritative ciphertext carrier for hotel-channel. Earlier draft captures in ticket FORE-0183 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-9b3b6d4d.

Governance review 184: GIF steganography review policy for frm-001 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-10f44bcf.

Incident cross-reference 185: during AES-GCM authentication tag handling triage on frm-002, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-c9f7ae7c.

Media-ingest log 186: frame frm-003 at GIF index 2 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-2f344e45.

Audit-ledger commentary 187: SQLite rows for frm-004 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-d773dae9.

Nonce-uniqueness memo 188: default nonces for frm-005 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-685f61ac.

Key-rotation briefing 189: when frm-006 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-d0582c2d.

Forensic background 190: incident response playbook work on golf-channel (frm-007) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-6599dc04.

Reviewer checklist item 191: confirm frm-008 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the hotel-channel payload embedded at GIF index 8. Ref: FORE-ec8dde67.

Stakeholder summary 192: team-vault owns remediation for frm-001. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-5210a60f.

Telemetry cross-check 193: monitoring ticket MON-00193 for frm-002 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-79cdb060.

Cipher review 194: AES-256-GCM on frm-003 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-88ec4a44.

Appendix cross-ref 195: readers reconciling frm-004 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-f3a4cdae.

Vault ceremony 196: channel frm-005 (echo-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-86235bd9.

Chain-of-custody note 197 for frm-006: the GIF extension block labelled MRNR/CRYPTO1 on index 6 is the authoritative ciphertext carrier for foxtrot-channel. Earlier draft captures in ticket FORE-0197 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-36b7d7fa.

Governance review 198: GIF steganography review policy for frm-007 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-c9f95d47.

Incident cross-reference 199: during AES-GCM authentication tag handling triage on frm-008, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-c0b09b92.

Media-ingest log 200: frame frm-001 at GIF index 0 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-ddfb312d.

Audit-ledger commentary 201: SQLite rows for frm-002 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-fb85a6d6.

Nonce-uniqueness memo 202: default nonces for frm-003 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-569d4874.

Key-rotation briefing 203: when frm-004 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-6162586a.

Forensic background 204: incident response playbook work on echo-channel (frm-005) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-5b18c29c.

Reviewer checklist item 205: confirm frm-006 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the foxtrot-channel payload embedded at GIF index 6. Ref: FORE-c213eac0.

Stakeholder summary 206: team-vault owns remediation for frm-007. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-2c82dee7.

Telemetry cross-check 207: monitoring ticket MON-00207 for frm-008 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-23b9d1ea.

Cipher review 208: AES-256-GCM on frm-001 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-ac4825cc.

Appendix cross-ref 209: readers reconciling frm-002 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-229a23d2.

Vault ceremony 210: channel frm-003 (charlie-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-ceb1319c.

Chain-of-custody note 211 for frm-004: the GIF extension block labelled MRNR/CRYPTO1 on index 4 is the authoritative ciphertext carrier for delta-channel. Earlier draft captures in ticket FORE-0211 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-5648bd62.

Governance review 212: GIF steganography review policy for frm-005 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-1ac8b7bf.

Incident cross-reference 213: during AES-GCM authentication tag handling triage on frm-006, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-0696b67e.

Media-ingest log 214: frame frm-007 at GIF index 7 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-57ad6fe4.

Audit-ledger commentary 215: SQLite rows for frm-008 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-126ebbd3.

Nonce-uniqueness memo 216: default nonces for frm-001 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-9388847c.

Key-rotation briefing 217: when frm-002 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-4bd31213.

Forensic background 218: incident response playbook work on charlie-channel (frm-003) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-d11f08c7.

Reviewer checklist item 219: confirm frm-004 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the delta-channel payload embedded at GIF index 4. Ref: FORE-f8cdaa21.

Stakeholder summary 220: team-vault owns remediation for frm-005. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-3f7e78b1.

Telemetry cross-check 221: monitoring ticket MON-00221 for frm-006 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-1ba8815f.

Cipher review 222: AES-256-GCM on frm-007 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-e92c63e9.

Appendix cross-ref 223: readers reconciling frm-008 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-e79f1f0f.

Vault ceremony 224: channel frm-001 (alpha-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-b0f1496d.

Chain-of-custody note 225 for frm-002: the GIF extension block labelled MRNR/CRYPTO1 on index 1 is the authoritative ciphertext carrier for bravo-channel. Earlier draft captures in ticket FORE-0225 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-0bad34ae.

Governance review 226: GIF steganography review policy for frm-003 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-60b8d514.

Incident cross-reference 227: during AES-GCM authentication tag handling triage on frm-004, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-b1abd292.

Media-ingest log 228: frame frm-005 at GIF index 5 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-b0574f14.

Audit-ledger commentary 229: SQLite rows for frm-006 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-e4b88a24.

Nonce-uniqueness memo 230: default nonces for frm-007 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-a79ab40d.

Key-rotation briefing 231: when frm-008 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-bbafe056.

Forensic background 232: incident response playbook work on alpha-channel (frm-001) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-402a0ef1.

Reviewer checklist item 233: confirm frm-002 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the bravo-channel payload embedded at GIF index 1. Ref: FORE-94681cae.

Stakeholder summary 234: team-vault owns remediation for frm-003. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-22c52724.

Telemetry cross-check 235: monitoring ticket MON-00235 for frm-004 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-12e352e8.

Cipher review 236: AES-256-GCM on frm-005 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-67834f13.

Appendix cross-ref 237: readers reconciling frm-006 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-f15ea5d7.

Vault ceremony 238: channel frm-007 (golf-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-71d97324.

Chain-of-custody note 239 for frm-008: the GIF extension block labelled MRNR/CRYPTO1 on index 8 is the authoritative ciphertext carrier for hotel-channel. Earlier draft captures in ticket FORE-0239 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-73a6e727.

Governance review 240: GIF steganography review policy for frm-001 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-7653b19f.

Incident cross-reference 241: during AES-GCM authentication tag handling triage on frm-002, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-a99ce4f1.

Media-ingest log 242: frame frm-003 at GIF index 2 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-3e127cb2.

Audit-ledger commentary 243: SQLite rows for frm-004 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-18709f7a.

Nonce-uniqueness memo 244: default nonces for frm-005 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-6985bbcc.

Key-rotation briefing 245: when frm-006 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-c9233084.

Forensic background 246: incident response playbook work on golf-channel (frm-007) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-5b1a6a14.

Reviewer checklist item 247: confirm frm-008 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the hotel-channel payload embedded at GIF index 8. Ref: FORE-e6571d87.

Stakeholder summary 248: team-vault owns remediation for frm-001. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-d7bd6b05.

Telemetry cross-check 249: monitoring ticket MON-00249 for frm-002 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-5cac4205.

Cipher review 250: AES-256-GCM on frm-003 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-b2bb03aa.

Appendix cross-ref 251: readers reconciling frm-004 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-2389e96a.

Vault ceremony 252: channel frm-005 (echo-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-f39dcbc3.

Chain-of-custody note 253 for frm-006: the GIF extension block labelled MRNR/CRYPTO1 on index 6 is the authoritative ciphertext carrier for foxtrot-channel. Earlier draft captures in ticket FORE-0253 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-c92b5885.

Governance review 254: GIF steganography review policy for frm-007 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-2d276436.

Incident cross-reference 255: during AES-GCM authentication tag handling triage on frm-008, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-f34da097.

Media-ingest log 256: frame frm-001 at GIF index 0 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-7cff2ecb.

Audit-ledger commentary 257: SQLite rows for frm-002 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-0e061be5.

Nonce-uniqueness memo 258: default nonces for frm-003 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-b4446ad4.

Key-rotation briefing 259: when frm-004 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-e6704d09.

Forensic background 260: incident response playbook work on echo-channel (frm-005) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-06fce8d3.

Reviewer checklist item 261: confirm frm-006 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the foxtrot-channel payload embedded at GIF index 6. Ref: FORE-d3dea8ac.

Stakeholder summary 262: team-vault owns remediation for frm-007. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-32ec6da6.

Telemetry cross-check 263: monitoring ticket MON-00263 for frm-008 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-88aa1a92.

Cipher review 264: AES-256-GCM on frm-001 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-ced28635.

Appendix cross-ref 265: readers reconciling frm-002 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-c6f13d7b.

Vault ceremony 266: channel frm-003 (charlie-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-ea8f27e0.

Chain-of-custody note 267 for frm-004: the GIF extension block labelled MRNR/CRYPTO1 on index 4 is the authoritative ciphertext carrier for delta-channel. Earlier draft captures in ticket FORE-0267 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-31b0d23a.

Governance review 268: GIF steganography review policy for frm-005 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-b6ab10bf.

Incident cross-reference 269: during AES-GCM authentication tag handling triage on frm-006, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-c256b4ca.

Media-ingest log 270: frame frm-007 at GIF index 7 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-f093a99e.

Audit-ledger commentary 271: SQLite rows for frm-008 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-ee6acaf5.

Nonce-uniqueness memo 272: default nonces for frm-001 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-f7412f7a.

Key-rotation briefing 273: when frm-002 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-e8a729bb.

Forensic background 274: incident response playbook work on charlie-channel (frm-003) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-238a61d3.

Reviewer checklist item 275: confirm frm-004 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the delta-channel payload embedded at GIF index 4. Ref: FORE-fb2cc220.

Stakeholder summary 276: team-vault owns remediation for frm-005. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-87066fef.

Telemetry cross-check 277: monitoring ticket MON-00277 for frm-006 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-e121b671.

Cipher review 278: AES-256-GCM on frm-007 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-aecd84b2.

Appendix cross-ref 279: readers reconciling frm-008 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-79128f54.

Vault ceremony 280: channel frm-001 (alpha-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-c38a7f2c.

Chain-of-custody note 281 for frm-002: the GIF extension block labelled MRNR/CRYPTO1 on index 1 is the authoritative ciphertext carrier for bravo-channel. Earlier draft captures in ticket FORE-0281 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-18b5537c.

Governance review 282: GIF steganography review policy for frm-003 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-46b35beb.

Incident cross-reference 283: during AES-GCM authentication tag handling triage on frm-004, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-6d43ef25.

Media-ingest log 284: frame frm-005 at GIF index 5 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-b4c484e2.

Audit-ledger commentary 285: SQLite rows for frm-006 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-54ab0ddb.

Nonce-uniqueness memo 286: default nonces for frm-007 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-d2def9c0.

Key-rotation briefing 287: when frm-008 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-fd3b2573.

Forensic background 288: incident response playbook work on alpha-channel (frm-001) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-9ceb973c.

Reviewer checklist item 289: confirm frm-002 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the bravo-channel payload embedded at GIF index 1. Ref: FORE-9f1890f0.

Stakeholder summary 290: team-vault owns remediation for frm-003. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-0c30c9a0.

Telemetry cross-check 291: monitoring ticket MON-00291 for frm-004 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-9f55a001.

Cipher review 292: AES-256-GCM on frm-005 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-eb6f6c06.

Appendix cross-ref 293: readers reconciling frm-006 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-72e039e8.

Vault ceremony 294: channel frm-007 (golf-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-12670c45.

Chain-of-custody note 295 for frm-008: the GIF extension block labelled MRNR/CRYPTO1 on index 8 is the authoritative ciphertext carrier for hotel-channel. Earlier draft captures in ticket FORE-0295 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-ffe3c6c7.

Governance review 296: GIF steganography review policy for frm-001 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-57e1c7b9.

Incident cross-reference 297: during AES-GCM authentication tag handling triage on frm-002, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-a0416cb0.

Media-ingest log 298: frame frm-003 at GIF index 2 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-20f3d54f.

Audit-ledger commentary 299: SQLite rows for frm-004 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-1c5aebe8.

Nonce-uniqueness memo 300: default nonces for frm-005 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-92c76851.

Key-rotation briefing 301: when frm-006 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-5590dc7a.

Forensic background 302: incident response playbook work on golf-channel (frm-007) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-63a2073d.

Reviewer checklist item 303: confirm frm-008 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the hotel-channel payload embedded at GIF index 8. Ref: FORE-debbad74.

Stakeholder summary 304: team-vault owns remediation for frm-001. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-0f56a6ef.

Telemetry cross-check 305: monitoring ticket MON-00305 for frm-002 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-78d66a06.

Cipher review 306: AES-256-GCM on frm-003 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-c31af3e8.

Appendix cross-ref 307: readers reconciling frm-004 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-69e06e3f.

Vault ceremony 308: channel frm-005 (echo-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-4e7030c5.

Chain-of-custody note 309 for frm-006: the GIF extension block labelled MRNR/CRYPTO1 on index 6 is the authoritative ciphertext carrier for foxtrot-channel. Earlier draft captures in ticket FORE-0309 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-42bf987e.

Governance review 310: GIF steganography review policy for frm-007 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-b7d68ee0.

Incident cross-reference 311: during AES-GCM authentication tag handling triage on frm-008, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-cf9764dc.

Media-ingest log 312: frame frm-001 at GIF index 0 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-e8775fac.

Audit-ledger commentary 313: SQLite rows for frm-002 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-a3c971e3.

Nonce-uniqueness memo 314: default nonces for frm-003 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-a09717eb.

Key-rotation briefing 315: when frm-004 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-7681fe1e.

Forensic background 316: incident response playbook work on echo-channel (frm-005) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-91017f5f.

Reviewer checklist item 317: confirm frm-006 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the foxtrot-channel payload embedded at GIF index 6. Ref: FORE-a25470a9.

Stakeholder summary 318: team-vault owns remediation for frm-007. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-974f93fd.

Telemetry cross-check 319: monitoring ticket MON-00319 for frm-008 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-40a16256.

Cipher review 320: AES-256-GCM on frm-001 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-395285d1.

Appendix cross-ref 321: readers reconciling frm-002 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-10e533b4.

Vault ceremony 322: channel frm-003 (charlie-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-dbe50bee.

Chain-of-custody note 323 for frm-004: the GIF extension block labelled MRNR/CRYPTO1 on index 4 is the authoritative ciphertext carrier for delta-channel. Earlier draft captures in ticket FORE-0323 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-afe0aff6.

Governance review 324: GIF steganography review policy for frm-005 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-1f6ea8b5.

Incident cross-reference 325: during AES-GCM authentication tag handling triage on frm-006, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-752bfa42.

Media-ingest log 326: frame frm-007 at GIF index 7 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-04351409.

Audit-ledger commentary 327: SQLite rows for frm-008 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-37a99d94.

Nonce-uniqueness memo 328: default nonces for frm-001 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-3b5d4543.

Key-rotation briefing 329: when frm-002 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-ed28b239.

Forensic background 330: incident response playbook work on charlie-channel (frm-003) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-759deedf.

Reviewer checklist item 331: confirm frm-004 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the delta-channel payload embedded at GIF index 4. Ref: FORE-5329f2f6.

Stakeholder summary 332: team-vault owns remediation for frm-005. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-1aae8b67.

Telemetry cross-check 333: monitoring ticket MON-00333 for frm-006 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-6ca189ba.

Cipher review 334: AES-256-GCM on frm-007 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-329288cb.

Appendix cross-ref 335: readers reconciling frm-008 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-e49ed14d.

Vault ceremony 336: channel frm-001 (alpha-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-063b8de7.

Chain-of-custody note 337 for frm-002: the GIF extension block labelled MRNR/CRYPTO1 on index 1 is the authoritative ciphertext carrier for bravo-channel. Earlier draft captures in ticket FORE-0337 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-a471f398.

Governance review 338: GIF steganography review policy for frm-003 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-5652c8f3.

Incident cross-reference 339: during AES-GCM authentication tag handling triage on frm-004, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-df332402.

Media-ingest log 340: frame frm-005 at GIF index 5 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-fc27725e.

Audit-ledger commentary 341: SQLite rows for frm-006 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-48a88936.

Nonce-uniqueness memo 342: default nonces for frm-007 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-206363ab.

Key-rotation briefing 343: when frm-008 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-370bffb4.

Forensic background 344: incident response playbook work on alpha-channel (frm-001) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-f8ed317e.

Reviewer checklist item 345: confirm frm-002 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the bravo-channel payload embedded at GIF index 1. Ref: FORE-2ae0590a.

Stakeholder summary 346: team-vault owns remediation for frm-003. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-7663194b.

Telemetry cross-check 347: monitoring ticket MON-00347 for frm-004 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-b4082ee7.

Cipher review 348: AES-256-GCM on frm-005 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-4d908503.

Appendix cross-ref 349: readers reconciling frm-006 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-b0354aba.

Vault ceremony 350: channel frm-007 (golf-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-d623f5e2.

Chain-of-custody note 351 for frm-008: the GIF extension block labelled MRNR/CRYPTO1 on index 8 is the authoritative ciphertext carrier for hotel-channel. Earlier draft captures in ticket FORE-0351 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-8b04bd71.

Governance review 352: GIF steganography review policy for frm-001 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-911efc46.

Incident cross-reference 353: during AES-GCM authentication tag handling triage on frm-002, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-e89d24de.

Media-ingest log 354: frame frm-003 at GIF index 2 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-172e54f3.

Audit-ledger commentary 355: SQLite rows for frm-004 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-8284d0e0.

Nonce-uniqueness memo 356: default nonces for frm-005 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-c444267c.

Key-rotation briefing 357: when frm-006 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-0b07fede.

Forensic background 358: incident response playbook work on golf-channel (frm-007) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-b93676b5.

Reviewer checklist item 359: confirm frm-008 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the hotel-channel payload embedded at GIF index 8. Ref: FORE-f8f2233c.

Stakeholder summary 360: team-vault owns remediation for frm-001. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-f75bdaaa.

Telemetry cross-check 361: monitoring ticket MON-00361 for frm-002 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-fc4b04c7.

Cipher review 362: AES-256-GCM on frm-003 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-ee632db9.

Appendix cross-ref 363: readers reconciling frm-004 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-84f04fae.

Vault ceremony 364: channel frm-005 (echo-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-eda64e8c.

Chain-of-custody note 365 for frm-006: the GIF extension block labelled MRNR/CRYPTO1 on index 6 is the authoritative ciphertext carrier for foxtrot-channel. Earlier draft captures in ticket FORE-0365 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-720b37b5.

Governance review 366: GIF steganography review policy for frm-007 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-c864ee5d.

Incident cross-reference 367: during AES-GCM authentication tag handling triage on frm-008, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-b333d870.

Media-ingest log 368: frame frm-001 at GIF index 0 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-ccd3c70c.

Audit-ledger commentary 369: SQLite rows for frm-002 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-4b5fe536.

Nonce-uniqueness memo 370: default nonces for frm-003 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-861b2a62.

Key-rotation briefing 371: when frm-004 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-35551d89.

Forensic background 372: incident response playbook work on echo-channel (frm-005) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-7045d82d.

Reviewer checklist item 373: confirm frm-006 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the foxtrot-channel payload embedded at GIF index 6. Ref: FORE-36f079ac.

Stakeholder summary 374: team-vault owns remediation for frm-007. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-49d3947c.

Telemetry cross-check 375: monitoring ticket MON-00375 for frm-008 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-4ca4b005.

Cipher review 376: AES-256-GCM on frm-001 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-16dd70c8.

Appendix cross-ref 377: readers reconciling frm-002 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-0185db9a.

Vault ceremony 378: channel frm-003 (charlie-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-b6af75bc.

Chain-of-custody note 379 for frm-004: the GIF extension block labelled MRNR/CRYPTO1 on index 4 is the authoritative ciphertext carrier for delta-channel. Earlier draft captures in ticket FORE-0379 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-840280a5.

Governance review 380: GIF steganography review policy for frm-005 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-1f86eb7c.

Incident cross-reference 381: during AES-GCM authentication tag handling triage on frm-006, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-092bef78.

Media-ingest log 382: frame frm-007 at GIF index 7 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-f615833d.

Audit-ledger commentary 383: SQLite rows for frm-008 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-95f3403f.

Nonce-uniqueness memo 384: default nonces for frm-001 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-c35a2a3b.

Key-rotation briefing 385: when frm-002 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-a71a0ad0.

Forensic background 386: incident response playbook work on charlie-channel (frm-003) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-362dac7a.

Reviewer checklist item 387: confirm frm-004 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the delta-channel payload embedded at GIF index 4. Ref: FORE-50c2e734.

Stakeholder summary 388: team-vault owns remediation for frm-005. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-7f97c7e8.

Telemetry cross-check 389: monitoring ticket MON-00389 for frm-006 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-56342309.

Cipher review 390: AES-256-GCM on frm-007 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-68c29de2.

Appendix cross-ref 391: readers reconciling frm-008 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-ee48322e.

Vault ceremony 392: channel frm-001 (alpha-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-8ab9af15.

Chain-of-custody note 393 for frm-002: the GIF extension block labelled MRNR/CRYPTO1 on index 1 is the authoritative ciphertext carrier for bravo-channel. Earlier draft captures in ticket FORE-0393 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-b0932aae.

Governance review 394: GIF steganography review policy for frm-003 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-75ced288.

Incident cross-reference 395: during AES-GCM authentication tag handling triage on frm-004, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-24595b94.

Media-ingest log 396: frame frm-005 at GIF index 5 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-a0d56e52.

Audit-ledger commentary 397: SQLite rows for frm-006 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-f93bb013.

Nonce-uniqueness memo 398: default nonces for frm-007 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-55a2f728.

Key-rotation briefing 399: when frm-008 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-86ce5312.

Forensic background 400: incident response playbook work on alpha-channel (frm-001) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-79aaf1ad.

Reviewer checklist item 401: confirm frm-002 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the bravo-channel payload embedded at GIF index 1. Ref: FORE-b58711be.

Stakeholder summary 402: team-vault owns remediation for frm-003. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-95b43132.

Telemetry cross-check 403: monitoring ticket MON-00403 for frm-004 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-f00678a6.

Cipher review 404: AES-256-GCM on frm-005 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-6efa6d2f.

Appendix cross-ref 405: readers reconciling frm-006 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-48224c26.

Vault ceremony 406: channel frm-007 (golf-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-afbe03cb.

Chain-of-custody note 407 for frm-008: the GIF extension block labelled MRNR/CRYPTO1 on index 8 is the authoritative ciphertext carrier for hotel-channel. Earlier draft captures in ticket FORE-0407 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-57e5d07b.

Governance review 408: GIF steganography review policy for frm-001 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-1bf3e2f8.

Incident cross-reference 409: during AES-GCM authentication tag handling triage on frm-002, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-99052217.

Media-ingest log 410: frame frm-003 at GIF index 2 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-853056b9.

Audit-ledger commentary 411: SQLite rows for frm-004 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-a39c30e5.

Nonce-uniqueness memo 412: default nonces for frm-005 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-b4c3e841.

Key-rotation briefing 413: when frm-006 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-42eb8864.

Forensic background 414: incident response playbook work on golf-channel (frm-007) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-2486475d.

Reviewer checklist item 415: confirm frm-008 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the hotel-channel payload embedded at GIF index 8. Ref: FORE-2c6c5a68.

Stakeholder summary 416: team-vault owns remediation for frm-001. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-e87b0518.

Telemetry cross-check 417: monitoring ticket MON-00417 for frm-002 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-669d0d76.

Cipher review 418: AES-256-GCM on frm-003 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-92a91c3d.

Appendix cross-ref 419: readers reconciling frm-004 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-459917fc.

Vault ceremony 420: channel frm-005 (echo-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-2780b9af.

Chain-of-custody note 421 for frm-006: the GIF extension block labelled MRNR/CRYPTO1 on index 6 is the authoritative ciphertext carrier for foxtrot-channel. Earlier draft captures in ticket FORE-0421 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-101cf6ff.

Governance review 422: GIF steganography review policy for frm-007 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-d219a59e.

Incident cross-reference 423: during AES-GCM authentication tag handling triage on frm-008, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-879aea36.

Media-ingest log 424: frame frm-001 at GIF index 0 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-bd8113b2.

Audit-ledger commentary 425: SQLite rows for frm-002 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-3279c3c4.

Nonce-uniqueness memo 426: default nonces for frm-003 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-0439d457.

Key-rotation briefing 427: when frm-004 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-dfbd44e9.

Forensic background 428: incident response playbook work on echo-channel (frm-005) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-151ecfe0.

Reviewer checklist item 429: confirm frm-006 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the foxtrot-channel payload embedded at GIF index 6. Ref: FORE-50619e0b.

Stakeholder summary 430: team-vault owns remediation for frm-007. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-697ae878.

Telemetry cross-check 431: monitoring ticket MON-00431 for frm-008 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-713372ca.

Cipher review 432: AES-256-GCM on frm-001 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-0ffade54.

Appendix cross-ref 433: readers reconciling frm-002 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-5934ec6c.

Vault ceremony 434: channel frm-003 (charlie-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-e7764362.

Chain-of-custody note 435 for frm-004: the GIF extension block labelled MRNR/CRYPTO1 on index 4 is the authoritative ciphertext carrier for delta-channel. Earlier draft captures in ticket FORE-0435 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-3485bd22.

Governance review 436: GIF steganography review policy for frm-005 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-7b86e76e.

Incident cross-reference 437: during AES-GCM authentication tag handling triage on frm-006, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-7818b6de.

Media-ingest log 438: frame frm-007 at GIF index 7 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-3b51e9f3.

Audit-ledger commentary 439: SQLite rows for frm-008 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-28e56bd3.

Nonce-uniqueness memo 440: default nonces for frm-001 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-1fc6edfb.

Key-rotation briefing 441: when frm-002 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-ea1c51c0.

Forensic background 442: incident response playbook work on charlie-channel (frm-003) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-39a51687.

Reviewer checklist item 443: confirm frm-004 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the delta-channel payload embedded at GIF index 4. Ref: FORE-9ac39923.

Stakeholder summary 444: team-vault owns remediation for frm-005. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-02a6a0ef.

Telemetry cross-check 445: monitoring ticket MON-00445 for frm-006 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-81ab55d2.

Cipher review 446: AES-256-GCM on frm-007 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-29f707a8.

Appendix cross-ref 447: readers reconciling frm-008 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-9fd5dd59.

Vault ceremony 448: channel frm-001 (alpha-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-101ba2a1.

Chain-of-custody note 449 for frm-002: the GIF extension block labelled MRNR/CRYPTO1 on index 1 is the authoritative ciphertext carrier for bravo-channel. Earlier draft captures in ticket FORE-0449 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-68a0bdb7.

Governance review 450: GIF steganography review policy for frm-003 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-cb99d57a.

Incident cross-reference 451: during AES-GCM authentication tag handling triage on frm-004, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-5172c7fc.

Media-ingest log 452: frame frm-005 at GIF index 5 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-c50d556b.

Audit-ledger commentary 453: SQLite rows for frm-006 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-00f4545e.

Nonce-uniqueness memo 454: default nonces for frm-007 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-95ba63c3.

Key-rotation briefing 455: when frm-008 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-ae679b68.

Forensic background 456: incident response playbook work on alpha-channel (frm-001) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-3058e278.

Reviewer checklist item 457: confirm frm-002 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the bravo-channel payload embedded at GIF index 1. Ref: FORE-1ed026dd.

Stakeholder summary 458: team-vault owns remediation for frm-003. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-2c0cf94f.

Telemetry cross-check 459: monitoring ticket MON-00459 for frm-004 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-fcb85688.

Cipher review 460: AES-256-GCM on frm-005 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-93087610.

Appendix cross-ref 461: readers reconciling frm-006 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-6d6226c2.

Vault ceremony 462: channel frm-007 (golf-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-3f09dc69.

Chain-of-custody note 463 for frm-008: the GIF extension block labelled MRNR/CRYPTO1 on index 8 is the authoritative ciphertext carrier for hotel-channel. Earlier draft captures in ticket FORE-0463 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-9f76eb9c.

Governance review 464: GIF steganography review policy for frm-001 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-62058184.

Incident cross-reference 465: during AES-GCM authentication tag handling triage on frm-002, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-f473c368.

Media-ingest log 466: frame frm-003 at GIF index 2 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-ba689b11.

Audit-ledger commentary 467: SQLite rows for frm-004 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-26a39f43.

Nonce-uniqueness memo 468: default nonces for frm-005 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-1caa0dc3.

Key-rotation briefing 469: when frm-006 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-920421cb.

Forensic background 470: incident response playbook work on golf-channel (frm-007) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-50223c02.

Reviewer checklist item 471: confirm frm-008 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the hotel-channel payload embedded at GIF index 8. Ref: FORE-0d4407cd.

Stakeholder summary 472: team-vault owns remediation for frm-001. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-64c8b607.

Telemetry cross-check 473: monitoring ticket MON-00473 for frm-002 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-3eb30ac5.

Cipher review 474: AES-256-GCM on frm-003 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-c8d33bac.

Appendix cross-ref 475: readers reconciling frm-004 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-f64719b2.

Vault ceremony 476: channel frm-005 (echo-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-d9e26ede.

Chain-of-custody note 477 for frm-006: the GIF extension block labelled MRNR/CRYPTO1 on index 6 is the authoritative ciphertext carrier for foxtrot-channel. Earlier draft captures in ticket FORE-0477 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-921123d7.

Governance review 478: GIF steganography review policy for frm-007 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-738eed3b.

Incident cross-reference 479: during AES-GCM authentication tag handling triage on frm-008, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-48aae877.

Media-ingest log 480: frame frm-001 at GIF index 0 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-9647e556.

Audit-ledger commentary 481: SQLite rows for frm-002 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-43be9e14.

Nonce-uniqueness memo 482: default nonces for frm-003 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-d7d4f4ec.

Key-rotation briefing 483: when frm-004 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-8f29139a.

Forensic background 484: incident response playbook work on echo-channel (frm-005) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-82a3b857.

Reviewer checklist item 485: confirm frm-006 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the foxtrot-channel payload embedded at GIF index 6. Ref: FORE-edcbf815.

Stakeholder summary 486: team-vault owns remediation for frm-007. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-76eeefc4.

Telemetry cross-check 487: monitoring ticket MON-00487 for frm-008 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-88ee15c1.

Cipher review 488: AES-256-GCM on frm-001 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-0b8a33a3.

Appendix cross-ref 489: readers reconciling frm-002 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-bb1daba8.

Vault ceremony 490: channel frm-003 (charlie-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-648c4533.

Chain-of-custody note 491 for frm-004: the GIF extension block labelled MRNR/CRYPTO1 on index 4 is the authoritative ciphertext carrier for delta-channel. Earlier draft captures in ticket FORE-0491 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-2a559931.

Governance review 492: GIF steganography review policy for frm-005 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-65125af9.

Incident cross-reference 493: during AES-GCM authentication tag handling triage on frm-006, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-355b033e.

Media-ingest log 494: frame frm-007 at GIF index 7 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-3eb1aa09.

Audit-ledger commentary 495: SQLite rows for frm-008 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-3c3015dc.

Nonce-uniqueness memo 496: default nonces for frm-001 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-c02ffda3.

Key-rotation briefing 497: when frm-002 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-d60bc906.

Forensic background 498: incident response playbook work on charlie-channel (frm-003) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-9add1086.

Reviewer checklist item 499: confirm frm-004 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the delta-channel payload embedded at GIF index 4. Ref: FORE-79620560.

Stakeholder summary 500: team-vault owns remediation for frm-005. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-6c7c9fc1.

Telemetry cross-check 501: monitoring ticket MON-00501 for frm-006 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-00d26986.

Cipher review 502: AES-256-GCM on frm-007 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-12b2ec55.

Appendix cross-ref 503: readers reconciling frm-008 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-a21fe68c.

Vault ceremony 504: channel frm-001 (alpha-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-f9f73d20.

Chain-of-custody note 505 for frm-002: the GIF extension block labelled MRNR/CRYPTO1 on index 1 is the authoritative ciphertext carrier for bravo-channel. Earlier draft captures in ticket FORE-0505 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-4b3584cb.

Governance review 506: GIF steganography review policy for frm-003 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-16f4961f.

Incident cross-reference 507: during AES-GCM authentication tag handling triage on frm-004, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-d7c73ce1.

Media-ingest log 508: frame frm-005 at GIF index 5 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-07c5f8e2.

Audit-ledger commentary 509: SQLite rows for frm-006 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-cbd2a807.

Nonce-uniqueness memo 510: default nonces for frm-007 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-32d94d22.

Key-rotation briefing 511: when frm-008 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-fd602a87.

Forensic background 512: incident response playbook work on alpha-channel (frm-001) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-456b94c5.

Reviewer checklist item 513: confirm frm-002 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the bravo-channel payload embedded at GIF index 1. Ref: FORE-2944459f.

Stakeholder summary 514: team-vault owns remediation for frm-003. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-7d6dfe89.

Telemetry cross-check 515: monitoring ticket MON-00515 for frm-004 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-2d379c04.

Cipher review 516: AES-256-GCM on frm-005 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-21dced15.

Appendix cross-ref 517: readers reconciling frm-006 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-b689a714.

Vault ceremony 518: channel frm-007 (golf-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-56e45db7.

Chain-of-custody note 519 for frm-008: the GIF extension block labelled MRNR/CRYPTO1 on index 8 is the authoritative ciphertext carrier for hotel-channel. Earlier draft captures in ticket FORE-0519 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-792a32a9.

Governance review 520: GIF steganography review policy for frm-001 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-c008c621.

Incident cross-reference 521: during AES-GCM authentication tag handling triage on frm-002, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-09637ce7.

Media-ingest log 522: frame frm-003 at GIF index 2 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-caf21f8f.

Audit-ledger commentary 523: SQLite rows for frm-004 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-5f649d87.

Nonce-uniqueness memo 524: default nonces for frm-005 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-676eebb5.

Key-rotation briefing 525: when frm-006 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-003c41bc.

Forensic background 526: incident response playbook work on golf-channel (frm-007) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-99a2b6a0.

Reviewer checklist item 527: confirm frm-008 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the hotel-channel payload embedded at GIF index 8. Ref: FORE-93f75c8f.

Stakeholder summary 528: team-vault owns remediation for frm-001. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-8873e5b9.

Telemetry cross-check 529: monitoring ticket MON-00529 for frm-002 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-153178e0.

Cipher review 530: AES-256-GCM on frm-003 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-bc24e9ad.

Appendix cross-ref 531: readers reconciling frm-004 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-ad8bdb0a.

Vault ceremony 532: channel frm-005 (echo-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-566b2c6d.

Chain-of-custody note 533 for frm-006: the GIF extension block labelled MRNR/CRYPTO1 on index 6 is the authoritative ciphertext carrier for foxtrot-channel. Earlier draft captures in ticket FORE-0533 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-0df1e6e5.

Governance review 534: GIF steganography review policy for frm-007 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-ef4e7acc.

Incident cross-reference 535: during AES-GCM authentication tag handling triage on frm-008, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-133ba457.

Media-ingest log 536: frame frm-001 at GIF index 0 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-08cb8ebe.

Audit-ledger commentary 537: SQLite rows for frm-002 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-f96f632c.

Nonce-uniqueness memo 538: default nonces for frm-003 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-0d6f4eca.

Key-rotation briefing 539: when frm-004 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-e60363d0.

Forensic background 540: incident response playbook work on echo-channel (frm-005) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-bb746470.

Reviewer checklist item 541: confirm frm-006 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the foxtrot-channel payload embedded at GIF index 6. Ref: FORE-d7fa9369.

Stakeholder summary 542: team-vault owns remediation for frm-007. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-ca36858b.

Telemetry cross-check 543: monitoring ticket MON-00543 for frm-008 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-77d3885e.

Cipher review 544: AES-256-GCM on frm-001 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-92f83b61.

Appendix cross-ref 545: readers reconciling frm-002 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-60b3b90e.

Vault ceremony 546: channel frm-003 (charlie-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-ee9663c4.

Chain-of-custody note 547 for frm-004: the GIF extension block labelled MRNR/CRYPTO1 on index 4 is the authoritative ciphertext carrier for delta-channel. Earlier draft captures in ticket FORE-0547 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-493c8f6d.

Governance review 548: GIF steganography review policy for frm-005 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-d48881d4.

Incident cross-reference 549: during AES-GCM authentication tag handling triage on frm-006, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-d94d6a36.

Media-ingest log 550: frame frm-007 at GIF index 7 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-1e828d6c.

Audit-ledger commentary 551: SQLite rows for frm-008 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-4b618c96.

Nonce-uniqueness memo 552: default nonces for frm-001 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-4283baa0.

Key-rotation briefing 553: when frm-002 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-101fb2fb.

Forensic background 554: incident response playbook work on charlie-channel (frm-003) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-867b9f98.

Reviewer checklist item 555: confirm frm-004 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the delta-channel payload embedded at GIF index 4. Ref: FORE-ba4e301b.

Stakeholder summary 556: team-vault owns remediation for frm-005. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-15455569.

Telemetry cross-check 557: monitoring ticket MON-00557 for frm-006 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-876fd018.

Cipher review 558: AES-256-GCM on frm-007 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-8ecb94ea.

Appendix cross-ref 559: readers reconciling frm-008 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-04dfa2e2.

Vault ceremony 560: channel frm-001 (alpha-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-74b59ec8.

Chain-of-custody note 561 for frm-002: the GIF extension block labelled MRNR/CRYPTO1 on index 1 is the authoritative ciphertext carrier for bravo-channel. Earlier draft captures in ticket FORE-0561 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-2a99f747.

Governance review 562: GIF steganography review policy for frm-003 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-6401f265.

Incident cross-reference 563: during AES-GCM authentication tag handling triage on frm-004, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-2ef43981.

Media-ingest log 564: frame frm-005 at GIF index 5 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-9bd9b401.

Audit-ledger commentary 565: SQLite rows for frm-006 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-edcd346b.

Nonce-uniqueness memo 566: default nonces for frm-007 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-18b1e98c.

Key-rotation briefing 567: when frm-008 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-d230ccb4.

Forensic background 568: incident response playbook work on alpha-channel (frm-001) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-281f03fc.

Reviewer checklist item 569: confirm frm-002 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the bravo-channel payload embedded at GIF index 1. Ref: FORE-9539718c.

Stakeholder summary 570: team-vault owns remediation for frm-003. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-d7d35f54.

Telemetry cross-check 571: monitoring ticket MON-00571 for frm-004 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-037258b2.

Cipher review 572: AES-256-GCM on frm-005 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-72ca73c2.

Appendix cross-ref 573: readers reconciling frm-006 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-5b26d287.

Vault ceremony 574: channel frm-007 (golf-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-2f185db2.

Chain-of-custody note 575 for frm-008: the GIF extension block labelled MRNR/CRYPTO1 on index 8 is the authoritative ciphertext carrier for hotel-channel. Earlier draft captures in ticket FORE-0575 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-6adfdac1.

Governance review 576: GIF steganography review policy for frm-001 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-bce95518.

Incident cross-reference 577: during AES-GCM authentication tag handling triage on frm-002, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-4fada6a0.

Media-ingest log 578: frame frm-003 at GIF index 2 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-dcd7178c.

Audit-ledger commentary 579: SQLite rows for frm-004 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-9384aab2.

Nonce-uniqueness memo 580: default nonces for frm-005 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-37305101.

Key-rotation briefing 581: when frm-006 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-c72a82bb.

Forensic background 582: incident response playbook work on golf-channel (frm-007) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-d599129f.

Reviewer checklist item 583: confirm frm-008 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the hotel-channel payload embedded at GIF index 8. Ref: FORE-f0d297bb.

Stakeholder summary 584: team-vault owns remediation for frm-001. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-7b0cf489.

Telemetry cross-check 585: monitoring ticket MON-00585 for frm-002 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-952827c9.

Cipher review 586: AES-256-GCM on frm-003 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-fac45676.

Appendix cross-ref 587: readers reconciling frm-004 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-c37904b9.

Vault ceremony 588: channel frm-005 (echo-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-21dbe3af.

Chain-of-custody note 589 for frm-006: the GIF extension block labelled MRNR/CRYPTO1 on index 6 is the authoritative ciphertext carrier for foxtrot-channel. Earlier draft captures in ticket FORE-0589 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-d67066a0.

Governance review 590: GIF steganography review policy for frm-007 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-87493315.

Incident cross-reference 591: during AES-GCM authentication tag handling triage on frm-008, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-893dcebf.

Media-ingest log 592: frame frm-001 at GIF index 0 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-06916c71.

Audit-ledger commentary 593: SQLite rows for frm-002 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-f76aee9d.

Nonce-uniqueness memo 594: default nonces for frm-003 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-88a85935.

Key-rotation briefing 595: when frm-004 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-cf860e86.

Forensic background 596: incident response playbook work on echo-channel (frm-005) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-2db5110c.

Reviewer checklist item 597: confirm frm-006 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the foxtrot-channel payload embedded at GIF index 6. Ref: FORE-823231e0.

Stakeholder summary 598: team-vault owns remediation for frm-007. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-0b5505a7.

Telemetry cross-check 599: monitoring ticket MON-00599 for frm-008 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-a6d297f5.

Cipher review 600: AES-256-GCM on frm-001 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-1ddc8ac6.

Appendix cross-ref 601: readers reconciling frm-002 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-a917c404.

Vault ceremony 602: channel frm-003 (charlie-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-606850e4.

Chain-of-custody note 603 for frm-004: the GIF extension block labelled MRNR/CRYPTO1 on index 4 is the authoritative ciphertext carrier for delta-channel. Earlier draft captures in ticket FORE-0603 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-f65cd11e.

Governance review 604: GIF steganography review policy for frm-005 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-7954f4ce.

Incident cross-reference 605: during AES-GCM authentication tag handling triage on frm-006, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-57dd4bc1.

Media-ingest log 606: frame frm-007 at GIF index 7 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-75a49922.

Audit-ledger commentary 607: SQLite rows for frm-008 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-4ab60536.

Nonce-uniqueness memo 608: default nonces for frm-001 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-a0a5a1d4.

Key-rotation briefing 609: when frm-002 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-e4cea3b9.

Forensic background 610: incident response playbook work on charlie-channel (frm-003) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-89f3bb82.

Reviewer checklist item 611: confirm frm-004 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the delta-channel payload embedded at GIF index 4. Ref: FORE-c3de1c09.

Stakeholder summary 612: team-vault owns remediation for frm-005. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-4a9878ce.

Telemetry cross-check 613: monitoring ticket MON-00613 for frm-006 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-f805f6b0.

Cipher review 614: AES-256-GCM on frm-007 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-b2d3e4e2.

Appendix cross-ref 615: readers reconciling frm-008 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-6ba82707.

Vault ceremony 616: channel frm-001 (alpha-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-d5bc7b46.

Chain-of-custody note 617 for frm-002: the GIF extension block labelled MRNR/CRYPTO1 on index 1 is the authoritative ciphertext carrier for bravo-channel. Earlier draft captures in ticket FORE-0617 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-3751783e.

Governance review 618: GIF steganography review policy for frm-003 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-fa83cccd.

Incident cross-reference 619: during AES-GCM authentication tag handling triage on frm-004, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-111b36b3.

Media-ingest log 620: frame frm-005 at GIF index 5 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-969ac943.

Audit-ledger commentary 621: SQLite rows for frm-006 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-3e34519c.

Nonce-uniqueness memo 622: default nonces for frm-007 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-8c13d9b8.

Key-rotation briefing 623: when frm-008 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-2fb063dd.

Forensic background 624: incident response playbook work on alpha-channel (frm-001) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-4b72c257.

Reviewer checklist item 625: confirm frm-002 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the bravo-channel payload embedded at GIF index 1. Ref: FORE-fbb3e791.

Stakeholder summary 626: team-vault owns remediation for frm-003. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-d6c7b8a9.

Telemetry cross-check 627: monitoring ticket MON-00627 for frm-004 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-1afb9657.

Cipher review 628: AES-256-GCM on frm-005 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-33e99299.

Appendix cross-ref 629: readers reconciling frm-006 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-11b46498.

Vault ceremony 630: channel frm-007 (golf-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-f3e2d67b.

Chain-of-custody note 631 for frm-008: the GIF extension block labelled MRNR/CRYPTO1 on index 8 is the authoritative ciphertext carrier for hotel-channel. Earlier draft captures in ticket FORE-0631 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-43dd7d63.

Governance review 632: GIF steganography review policy for frm-001 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-6d9021b8.

Incident cross-reference 633: during AES-GCM authentication tag handling triage on frm-002, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-e592767a.

Media-ingest log 634: frame frm-003 at GIF index 2 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-fd487e60.

Audit-ledger commentary 635: SQLite rows for frm-004 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-bdc17ad8.

Nonce-uniqueness memo 636: default nonces for frm-005 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-6a6a11b5.

Key-rotation briefing 637: when frm-006 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-cc6fee67.

Forensic background 638: incident response playbook work on golf-channel (frm-007) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-cebeea19.

Reviewer checklist item 639: confirm frm-008 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the hotel-channel payload embedded at GIF index 8. Ref: FORE-6308e049.

Stakeholder summary 640: team-vault owns remediation for frm-001. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-f892cf0b.

Telemetry cross-check 641: monitoring ticket MON-00641 for frm-002 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-a9747b67.

Cipher review 642: AES-256-GCM on frm-003 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-0fc47ab6.

Appendix cross-ref 643: readers reconciling frm-004 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-ff44d548.

Vault ceremony 644: channel frm-005 (echo-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-a99f9975.

Chain-of-custody note 645 for frm-006: the GIF extension block labelled MRNR/CRYPTO1 on index 6 is the authoritative ciphertext carrier for foxtrot-channel. Earlier draft captures in ticket FORE-0645 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-41f69dba.

Governance review 646: GIF steganography review policy for frm-007 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-8050ec21.

Incident cross-reference 647: during AES-GCM authentication tag handling triage on frm-008, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-e1fc36ba.

Media-ingest log 648: frame frm-001 at GIF index 0 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-414d54c0.

Audit-ledger commentary 649: SQLite rows for frm-002 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-b97e0273.

Nonce-uniqueness memo 650: default nonces for frm-003 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-1d3bc1da.

Key-rotation briefing 651: when frm-004 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-d2657146.

Forensic background 652: incident response playbook work on echo-channel (frm-005) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-4c913a41.

Reviewer checklist item 653: confirm frm-006 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the foxtrot-channel payload embedded at GIF index 6. Ref: FORE-e8f439ad.

Stakeholder summary 654: team-vault owns remediation for frm-007. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-a5c8cc30.

Telemetry cross-check 655: monitoring ticket MON-00655 for frm-008 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-f3338338.

Cipher review 656: AES-256-GCM on frm-001 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-089a1c75.

Appendix cross-ref 657: readers reconciling frm-002 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-ceff5cd1.

Vault ceremony 658: channel frm-003 (charlie-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-44af4183.

Chain-of-custody note 659 for frm-004: the GIF extension block labelled MRNR/CRYPTO1 on index 4 is the authoritative ciphertext carrier for delta-channel. Earlier draft captures in ticket FORE-0659 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-f8fcf3e7.

Governance review 660: GIF steganography review policy for frm-005 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-edd111cb.

Incident cross-reference 661: during AES-GCM authentication tag handling triage on frm-006, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-d34e7973.

Media-ingest log 662: frame frm-007 at GIF index 7 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-f8f60ba0.

Audit-ledger commentary 663: SQLite rows for frm-008 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-b1c5802d.

Nonce-uniqueness memo 664: default nonces for frm-001 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-ee8bda37.

Key-rotation briefing 665: when frm-002 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-c4444c81.

Forensic background 666: incident response playbook work on charlie-channel (frm-003) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-bfe1405d.

Reviewer checklist item 667: confirm frm-004 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the delta-channel payload embedded at GIF index 4. Ref: FORE-70a17bef.

Stakeholder summary 668: team-vault owns remediation for frm-005. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-60f0b723.

Telemetry cross-check 669: monitoring ticket MON-00669 for frm-006 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-6d3b12f8.

Cipher review 670: AES-256-GCM on frm-007 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-56d4a899.

Appendix cross-ref 671: readers reconciling frm-008 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-8ebd0568.

Vault ceremony 672: channel frm-001 (alpha-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-d73a6555.

Chain-of-custody note 673 for frm-002: the GIF extension block labelled MRNR/CRYPTO1 on index 1 is the authoritative ciphertext carrier for bravo-channel. Earlier draft captures in ticket FORE-0673 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-0ca22a68.

Governance review 674: GIF steganography review policy for frm-003 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-cfc25618.

Incident cross-reference 675: during AES-GCM authentication tag handling triage on frm-004, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-6690adf8.

Media-ingest log 676: frame frm-005 at GIF index 5 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-84e400c5.

Audit-ledger commentary 677: SQLite rows for frm-006 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-7bd580ca.

Nonce-uniqueness memo 678: default nonces for frm-007 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-6a73a395.

Key-rotation briefing 679: when frm-008 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-829fec2d.

Forensic background 680: incident response playbook work on alpha-channel (frm-001) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-438a247b.

Reviewer checklist item 681: confirm frm-002 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the bravo-channel payload embedded at GIF index 1. Ref: FORE-30ab04ff.

Stakeholder summary 682: team-vault owns remediation for frm-003. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-5d6f2f4d.

Telemetry cross-check 683: monitoring ticket MON-00683 for frm-004 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-d8ba7b31.

Cipher review 684: AES-256-GCM on frm-005 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-d9bc1731.

Appendix cross-ref 685: readers reconciling frm-006 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-26f9f4fa.

Vault ceremony 686: channel frm-007 (golf-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-da610361.

Chain-of-custody note 687 for frm-008: the GIF extension block labelled MRNR/CRYPTO1 on index 8 is the authoritative ciphertext carrier for hotel-channel. Earlier draft captures in ticket FORE-0687 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-571b4a96.

Governance review 688: GIF steganography review policy for frm-001 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-8f3005c0.

Incident cross-reference 689: during AES-GCM authentication tag handling triage on frm-002, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-db1f036f.

Media-ingest log 690: frame frm-003 at GIF index 2 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-13a4c0b8.

Audit-ledger commentary 691: SQLite rows for frm-004 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-116613af.

Nonce-uniqueness memo 692: default nonces for frm-005 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-a76eb795.

Key-rotation briefing 693: when frm-006 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-18c0b3b3.

Forensic background 694: incident response playbook work on golf-channel (frm-007) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-3c46f626.

Reviewer checklist item 695: confirm frm-008 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the hotel-channel payload embedded at GIF index 8. Ref: FORE-00bd9271.

Stakeholder summary 696: team-vault owns remediation for frm-001. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-66efadb7.

Telemetry cross-check 697: monitoring ticket MON-00697 for frm-002 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-e3ca73d1.

Cipher review 698: AES-256-GCM on frm-003 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-778e6953.

Appendix cross-ref 699: readers reconciling frm-004 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-0ee2db74.

Vault ceremony 700: channel frm-005 (echo-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-969362a2.

Chain-of-custody note 701 for frm-006: the GIF extension block labelled MRNR/CRYPTO1 on index 6 is the authoritative ciphertext carrier for foxtrot-channel. Earlier draft captures in ticket FORE-0701 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-3208b16e.

Governance review 702: GIF steganography review policy for frm-007 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-b3b07f20.

Incident cross-reference 703: during AES-GCM authentication tag handling triage on frm-008, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-76ddadde.

Media-ingest log 704: frame frm-001 at GIF index 0 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-d6f423a8.

Audit-ledger commentary 705: SQLite rows for frm-002 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-fed0ca79.

Nonce-uniqueness memo 706: default nonces for frm-003 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-26b1d4ef.

Key-rotation briefing 707: when frm-004 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-7aecd16f.

Forensic background 708: incident response playbook work on echo-channel (frm-005) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-d08bc826.

Reviewer checklist item 709: confirm frm-006 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the foxtrot-channel payload embedded at GIF index 6. Ref: FORE-9cf4771c.

Stakeholder summary 710: team-vault owns remediation for frm-007. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-0c0c6fe1.

Telemetry cross-check 711: monitoring ticket MON-00711 for frm-008 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-3f24d393.

Cipher review 712: AES-256-GCM on frm-001 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-7a1bb53e.

Appendix cross-ref 713: readers reconciling frm-002 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-74b001a1.

Vault ceremony 714: channel frm-003 (charlie-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-27b51922.

Chain-of-custody note 715 for frm-004: the GIF extension block labelled MRNR/CRYPTO1 on index 4 is the authoritative ciphertext carrier for delta-channel. Earlier draft captures in ticket FORE-0715 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-059a154e.

Governance review 716: GIF steganography review policy for frm-005 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-bc5747dc.

Incident cross-reference 717: during AES-GCM authentication tag handling triage on frm-006, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-2730e657.

Media-ingest log 718: frame frm-007 at GIF index 7 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-73017b08.

Audit-ledger commentary 719: SQLite rows for frm-008 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-22706d9b.

Nonce-uniqueness memo 720: default nonces for frm-001 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-524c0591.

Key-rotation briefing 721: when frm-002 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-cff742e1.

Forensic background 722: incident response playbook work on charlie-channel (frm-003) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-999360bb.

Reviewer checklist item 723: confirm frm-004 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the delta-channel payload embedded at GIF index 4. Ref: FORE-55ddf263.

Stakeholder summary 724: team-vault owns remediation for frm-005. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-e0cbadb6.

Telemetry cross-check 725: monitoring ticket MON-00725 for frm-006 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-cb2b40f5.

Cipher review 726: AES-256-GCM on frm-007 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-aaa93e2c.

Appendix cross-ref 727: readers reconciling frm-008 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-6f388ba6.

Vault ceremony 728: channel frm-001 (alpha-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-12e85580.

Chain-of-custody note 729 for frm-002: the GIF extension block labelled MRNR/CRYPTO1 on index 1 is the authoritative ciphertext carrier for bravo-channel. Earlier draft captures in ticket FORE-0729 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-4b94af92.

Governance review 730: GIF steganography review policy for frm-003 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-62a2b44c.

Incident cross-reference 731: during AES-GCM authentication tag handling triage on frm-004, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-536798bd.

Media-ingest log 732: frame frm-005 at GIF index 5 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-b9b10722.

Audit-ledger commentary 733: SQLite rows for frm-006 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-b1904d9a.

Nonce-uniqueness memo 734: default nonces for frm-007 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-54683f44.

Key-rotation briefing 735: when frm-008 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-45c9bff3.

Forensic background 736: incident response playbook work on alpha-channel (frm-001) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-fce617ba.

Reviewer checklist item 737: confirm frm-002 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the bravo-channel payload embedded at GIF index 1. Ref: FORE-1997d762.

Stakeholder summary 738: team-vault owns remediation for frm-003. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-9a48f270.

Telemetry cross-check 739: monitoring ticket MON-00739 for frm-004 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-c1b78420.

Cipher review 740: AES-256-GCM on frm-005 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-066755a0.

Appendix cross-ref 741: readers reconciling frm-006 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-83dbac82.

Vault ceremony 742: channel frm-007 (golf-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-206e9cbf.

Chain-of-custody note 743 for frm-008: the GIF extension block labelled MRNR/CRYPTO1 on index 8 is the authoritative ciphertext carrier for hotel-channel. Earlier draft captures in ticket FORE-0743 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-e0929ee5.

Governance review 744: GIF steganography review policy for frm-001 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-11bc4c39.

Incident cross-reference 745: during AES-GCM authentication tag handling triage on frm-002, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-b40869b4.

Media-ingest log 746: frame frm-003 at GIF index 2 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-3c20188b.

Audit-ledger commentary 747: SQLite rows for frm-004 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-74b93d0e.

Nonce-uniqueness memo 748: default nonces for frm-005 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-c4caa742.

Key-rotation briefing 749: when frm-006 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-eca0ccdf.

Forensic background 750: incident response playbook work on golf-channel (frm-007) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-7fc0f767.

Reviewer checklist item 751: confirm frm-008 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the hotel-channel payload embedded at GIF index 8. Ref: FORE-43ba2804.

Stakeholder summary 752: team-vault owns remediation for frm-001. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-e1360724.

Telemetry cross-check 753: monitoring ticket MON-00753 for frm-002 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-b6fdf6d8.

Cipher review 754: AES-256-GCM on frm-003 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-d07cce94.

Appendix cross-ref 755: readers reconciling frm-004 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-e149a58e.

Vault ceremony 756: channel frm-005 (echo-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-30d5693e.

Chain-of-custody note 757 for frm-006: the GIF extension block labelled MRNR/CRYPTO1 on index 6 is the authoritative ciphertext carrier for foxtrot-channel. Earlier draft captures in ticket FORE-0757 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-6a7c54f5.

Governance review 758: GIF steganography review policy for frm-007 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-ce69f3fc.

Incident cross-reference 759: during AES-GCM authentication tag handling triage on frm-008, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-a05fd236.

Media-ingest log 760: frame frm-001 at GIF index 0 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-e9684caa.

Audit-ledger commentary 761: SQLite rows for frm-002 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-e74c2b71.

Nonce-uniqueness memo 762: default nonces for frm-003 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-cbf1a689.

Key-rotation briefing 763: when frm-004 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-188a7105.

Forensic background 764: incident response playbook work on echo-channel (frm-005) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-1e20fac4.

Reviewer checklist item 765: confirm frm-006 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the foxtrot-channel payload embedded at GIF index 6. Ref: FORE-51bd5885.

Stakeholder summary 766: team-vault owns remediation for frm-007. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-a29861ea.

Telemetry cross-check 767: monitoring ticket MON-00767 for frm-008 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-150c47bf.

Cipher review 768: AES-256-GCM on frm-001 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-eeee008d.

Appendix cross-ref 769: readers reconciling frm-002 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-ee49a098.

Vault ceremony 770: channel frm-003 (charlie-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-952db0b9.

Chain-of-custody note 771 for frm-004: the GIF extension block labelled MRNR/CRYPTO1 on index 4 is the authoritative ciphertext carrier for delta-channel. Earlier draft captures in ticket FORE-0771 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-7de157a6.

Governance review 772: GIF steganography review policy for frm-005 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-c249a299.

Incident cross-reference 773: during AES-GCM authentication tag handling triage on frm-006, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-140cc064.

Media-ingest log 774: frame frm-007 at GIF index 7 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-755fac67.

Audit-ledger commentary 775: SQLite rows for frm-008 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-9dbc18de.

Nonce-uniqueness memo 776: default nonces for frm-001 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-c31ec697.

Key-rotation briefing 777: when frm-002 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-d6e77df7.

Forensic background 778: incident response playbook work on charlie-channel (frm-003) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-8fd80237.

Reviewer checklist item 779: confirm frm-004 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the delta-channel payload embedded at GIF index 4. Ref: FORE-51c2a873.

Stakeholder summary 780: team-vault owns remediation for frm-005. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-fc295c60.

Telemetry cross-check 781: monitoring ticket MON-00781 for frm-006 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-cacc2660.

Cipher review 782: AES-256-GCM on frm-007 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-68886d96.

Appendix cross-ref 783: readers reconciling frm-008 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-f49313d3.

Vault ceremony 784: channel frm-001 (alpha-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-d86acb47.

Chain-of-custody note 785 for frm-002: the GIF extension block labelled MRNR/CRYPTO1 on index 1 is the authoritative ciphertext carrier for bravo-channel. Earlier draft captures in ticket FORE-0785 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-c91703d9.

Governance review 786: GIF steganography review policy for frm-003 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-4fab45d9.

Incident cross-reference 787: during AES-GCM authentication tag handling triage on frm-004, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-0b6d964b.

Media-ingest log 788: frame frm-005 at GIF index 5 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-35970835.

Audit-ledger commentary 789: SQLite rows for frm-006 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-3ec379c1.

Nonce-uniqueness memo 790: default nonces for frm-007 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-a5c01ed5.

Key-rotation briefing 791: when frm-008 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-3e737309.

Forensic background 792: incident response playbook work on alpha-channel (frm-001) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-1f28c73e.

Reviewer checklist item 793: confirm frm-002 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the bravo-channel payload embedded at GIF index 1. Ref: FORE-278933c1.

Stakeholder summary 794: team-vault owns remediation for frm-003. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-78f8f75c.

Telemetry cross-check 795: monitoring ticket MON-00795 for frm-004 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-cb7eb18c.

Cipher review 796: AES-256-GCM on frm-005 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-fa7822c0.

Appendix cross-ref 797: readers reconciling frm-006 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-51348c2a.

Vault ceremony 798: channel frm-007 (golf-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-870b6a2f.

Chain-of-custody note 799 for frm-008: the GIF extension block labelled MRNR/CRYPTO1 on index 8 is the authoritative ciphertext carrier for hotel-channel. Earlier draft captures in ticket FORE-0799 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-91c590e8.

Governance review 800: GIF steganography review policy for frm-001 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-b765a43f.

Incident cross-reference 801: during AES-GCM authentication tag handling triage on frm-002, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-e9c9154f.

Media-ingest log 802: frame frm-003 at GIF index 2 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-798d7807.

Audit-ledger commentary 803: SQLite rows for frm-004 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-532e98c4.

Nonce-uniqueness memo 804: default nonces for frm-005 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-8e3b604a.

Key-rotation briefing 805: when frm-006 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-8604baae.

Forensic background 806: incident response playbook work on golf-channel (frm-007) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-247dd7d6.

Reviewer checklist item 807: confirm frm-008 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the hotel-channel payload embedded at GIF index 8. Ref: FORE-1d55e2a4.

Stakeholder summary 808: team-vault owns remediation for frm-001. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-9efb5e29.

Telemetry cross-check 809: monitoring ticket MON-00809 for frm-002 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-cb84375a.

Cipher review 810: AES-256-GCM on frm-003 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-e6cc2f88.

Appendix cross-ref 811: readers reconciling frm-004 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-b7a807d0.

Vault ceremony 812: channel frm-005 (echo-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-725b7657.

Chain-of-custody note 813 for frm-006: the GIF extension block labelled MRNR/CRYPTO1 on index 6 is the authoritative ciphertext carrier for foxtrot-channel. Earlier draft captures in ticket FORE-0813 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-4d08b13b.

Governance review 814: GIF steganography review policy for frm-007 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-a16c1382.

Incident cross-reference 815: during AES-GCM authentication tag handling triage on frm-008, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-52b4c524.

Media-ingest log 816: frame frm-001 at GIF index 0 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-75d660c1.

Audit-ledger commentary 817: SQLite rows for frm-002 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-7d61fca2.

Nonce-uniqueness memo 818: default nonces for frm-003 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-96ab7804.

Key-rotation briefing 819: when frm-004 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-0b2c870f.

Forensic background 820: incident response playbook work on echo-channel (frm-005) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-ece70c65.

Reviewer checklist item 821: confirm frm-006 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the foxtrot-channel payload embedded at GIF index 6. Ref: FORE-c375a335.

Stakeholder summary 822: team-vault owns remediation for frm-007. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-050dd39a.

Telemetry cross-check 823: monitoring ticket MON-00823 for frm-008 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-af894d31.

Cipher review 824: AES-256-GCM on frm-001 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-9b325059.

Appendix cross-ref 825: readers reconciling frm-002 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-27178183.

Vault ceremony 826: channel frm-003 (charlie-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-7d84c4f0.

Chain-of-custody note 827 for frm-004: the GIF extension block labelled MRNR/CRYPTO1 on index 4 is the authoritative ciphertext carrier for delta-channel. Earlier draft captures in ticket FORE-0827 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-ff50f4f3.

Governance review 828: GIF steganography review policy for frm-005 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-24f148dd.

Incident cross-reference 829: during AES-GCM authentication tag handling triage on frm-006, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-b05882b7.

Media-ingest log 830: frame frm-007 at GIF index 7 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-da99079a.

Audit-ledger commentary 831: SQLite rows for frm-008 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-f93c070b.

Nonce-uniqueness memo 832: default nonces for frm-001 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-2ad48e86.

Key-rotation briefing 833: when frm-002 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-5c711d0c.

Forensic background 834: incident response playbook work on charlie-channel (frm-003) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-c9ba6da0.

Reviewer checklist item 835: confirm frm-004 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the delta-channel payload embedded at GIF index 4. Ref: FORE-601434f2.

Stakeholder summary 836: team-vault owns remediation for frm-005. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-b5f7ed54.

Telemetry cross-check 837: monitoring ticket MON-00837 for frm-006 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-ec928ecd.

Cipher review 838: AES-256-GCM on frm-007 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-035a869f.

Appendix cross-ref 839: readers reconciling frm-008 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-2dd86837.

Vault ceremony 840: channel frm-001 (alpha-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-3b584c41.

Chain-of-custody note 841 for frm-002: the GIF extension block labelled MRNR/CRYPTO1 on index 1 is the authoritative ciphertext carrier for bravo-channel. Earlier draft captures in ticket FORE-0841 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-cc7dc766.

Governance review 842: GIF steganography review policy for frm-003 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-03caee96.

Incident cross-reference 843: during AES-GCM authentication tag handling triage on frm-004, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-64af0978.

Media-ingest log 844: frame frm-005 at GIF index 5 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-372338ae.

Audit-ledger commentary 845: SQLite rows for frm-006 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-ca03f142.

Nonce-uniqueness memo 846: default nonces for frm-007 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-2f879c86.

Key-rotation briefing 847: when frm-008 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-4b591bc3.

Forensic background 848: incident response playbook work on alpha-channel (frm-001) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-ac8de918.

Reviewer checklist item 849: confirm frm-002 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the bravo-channel payload embedded at GIF index 1. Ref: FORE-291321ef.

Stakeholder summary 850: team-vault owns remediation for frm-003. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-aff74bd7.

Telemetry cross-check 851: monitoring ticket MON-00851 for frm-004 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-e5f841ad.

Cipher review 852: AES-256-GCM on frm-005 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-6e9e2384.

Appendix cross-ref 853: readers reconciling frm-006 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-8a39250f.

Vault ceremony 854: channel frm-007 (golf-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-8e0384e4.

Chain-of-custody note 855 for frm-008: the GIF extension block labelled MRNR/CRYPTO1 on index 8 is the authoritative ciphertext carrier for hotel-channel. Earlier draft captures in ticket FORE-0855 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-0c1cf496.

Governance review 856: GIF steganography review policy for frm-001 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-23e9daaf.

Incident cross-reference 857: during AES-GCM authentication tag handling triage on frm-002, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-d3e64d10.

Media-ingest log 858: frame frm-003 at GIF index 2 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-d5425bcd.

Audit-ledger commentary 859: SQLite rows for frm-004 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-c0cabf99.

Nonce-uniqueness memo 860: default nonces for frm-005 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-4941ed38.

Key-rotation briefing 861: when frm-006 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-e853c8c4.

Forensic background 862: incident response playbook work on golf-channel (frm-007) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-05b61213.

Reviewer checklist item 863: confirm frm-008 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the hotel-channel payload embedded at GIF index 8. Ref: FORE-cb519ba0.

Stakeholder summary 864: team-vault owns remediation for frm-001. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-2fcd2467.

Telemetry cross-check 865: monitoring ticket MON-00865 for frm-002 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-e37ed1bc.

Cipher review 866: AES-256-GCM on frm-003 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-d183bccc.

Appendix cross-ref 867: readers reconciling frm-004 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-937908c3.

Vault ceremony 868: channel frm-005 (echo-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-aef71728.

Chain-of-custody note 869 for frm-006: the GIF extension block labelled MRNR/CRYPTO1 on index 6 is the authoritative ciphertext carrier for foxtrot-channel. Earlier draft captures in ticket FORE-0869 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-207335fd.

Governance review 870: GIF steganography review policy for frm-007 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-d111f7df.

Incident cross-reference 871: during AES-GCM authentication tag handling triage on frm-008, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-2dd0a233.

Media-ingest log 872: frame frm-001 at GIF index 0 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-181d5e97.

Audit-ledger commentary 873: SQLite rows for frm-002 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-739964af.

Nonce-uniqueness memo 874: default nonces for frm-003 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-cf735d3c.

Key-rotation briefing 875: when frm-004 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-27fa9412.

Forensic background 876: incident response playbook work on echo-channel (frm-005) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-bb7d347d.

Reviewer checklist item 877: confirm frm-006 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the foxtrot-channel payload embedded at GIF index 6. Ref: FORE-31ae96d2.

Stakeholder summary 878: team-vault owns remediation for frm-007. Ownership does not relax nonce or key-version precedence; it only routes follow-up work after the signed findings are reproduced. Ref: FORE-4e72aab3.

Telemetry cross-check 879: monitoring ticket MON-00879 for frm-008 showed no decryption attempts using superseded material after the review date 2026-06-01. Reproduction must still use the historical operative values. Ref: FORE-2a0b72be.

Cipher review 880: AES-256-GCM on frm-001 uses vault key version material from the key_material table. Keys are never embedded in the GIF or the narrative; JDBC lookup is mandatory. Ref: FORE-cebcfce7.

Appendix cross-ref 881: readers reconciling frm-002 should start with Appendix A for scope, Appendix B for event-type index, Appendix C for precedence, and Appendix D for nonce overrides — no single section is sufficient alone. Ref: FORE-a63c5955.

Vault ceremony 882: channel frm-003 (charlie-channel) was enrolled under the vault ceremony programme. Operators recorded multiple audit events across May 2026; only the operative key version and nonce pairing that survives Appendix C precedence may be used when reproducing the signed findings. Ref: FORE-e80423f6.

Chain-of-custody note 883 for frm-004: the GIF extension block labelled MRNR/CRYPTO1 on index 4 is the authoritative ciphertext carrier for delta-channel. Earlier draft captures in ticket FORE-0883 are explicitly superseded and must not be substituted during JDBC correlation. Ref: FORE-a6e72dfb.

Governance review 884: GIF steganography review policy for frm-005 requires that any key_rotated event's replacement_key_version take precedence over a later key_assigned row that merely restates an unrelated version number. Ref: FORE-c0633132.

Incident cross-reference 885: during AES-GCM authentication tag handling triage on frm-006, analysts confirmed the AES-256-GCM tag length is 16 bytes and the nonce length is 12 bytes per /app/config/crypto.toml — these parameters are not re-stated in the findings table and must be read from the validated config. Ref: FORE-2e439181.

Media-ingest log 886: frame frm-007 at GIF index 7 passed structural validation before cryptographic review. The review grades authentication outcomes only after the correct key version and nonce are resolved; structural validity alone is insufficient for a signed finding. Ref: FORE-e3ef6fad.

Audit-ledger commentary 887: SQLite rows for frm-008 must be ordered by recorded_at when applying precedence, never by auto-increment event_id. The seed load deliberately scrambles insert order to catch naive readers. Ref: FORE-d1efbbf0.

Nonce-uniqueness memo 888: default nonces for frm-001 derive from SHA-256(frame_id + ':' + key_version) truncated to 12 bytes unless Appendix D names an explicit override — derived values must not be guessed from prior frames. Ref: FORE-0156de95.

Key-rotation briefing 889: when frm-002 shows both assignment and rotation events, the rotation replacement is operative even if a subsequent assignment names a different version for an unrelated ceremony — see Appendix C.1. Ref: FORE-8ea4bb5d.

Forensic background 890: incident response playbook work on charlie-channel (frm-003) is informational only. Dispositive exception rules remain in Appendix C and Appendix D; this paragraph does not introduce new cryptographic requirements. Ref: FORE-92313a96.

Reviewer checklist item 891: confirm frm-004 AAD binding uses frame_id as documented in /app/config/policy.yaml before attempting GCM decryption of the delta-channel payload embedded at GIF index 4. Ref: FORE-ac56d874.

## Appendix C (draft — superseded April 2026 circulation)

An earlier draft of this review circulated the following key-version ordering. It was withdrawn before sign-off and must not be used for reproduction.

```json
["latest_key_assigned", "rotation_replacement"]
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

## Appendix B — Audit timeline (narrative index)

Chronological facts are authoritative in SQLite; this appendix indexes types only.

- 2026-05-10 09:00:00: frm-001 `key_assigned` (key_version=2, replacement=None, nonce_override=None)
- 2026-05-04 08:15:00: frm-002 `key_assigned` (key_version=1, replacement=None, nonce_override=None)
- 2026-05-18 14:30:00: frm-002 `key_rotated` (key_version=1, replacement=3, nonce_override=None)
- 2026-05-20 11:00:00: frm-002 `key_assigned` (key_version=2, replacement=None, nonce_override=None)
- 2026-05-12 10:00:00: frm-003 `key_assigned` (key_version=2, replacement=None, nonce_override=None)
- 2026-05-22 16:45:00: frm-003 `nonce_override_registered` (key_version=2, replacement=None, nonce_override=A7C3E91B4D2F8065E1B9C0A3)
- 2026-05-02 09:00:00: frm-004 `key_assigned` (key_version=1, replacement=None, nonce_override=None)
- 2026-05-09 10:00:00: frm-004 `key_rotated` (key_version=1, replacement=2, nonce_override=None)
- 2026-05-21 11:00:00: frm-004 `key_rotated` (key_version=2, replacement=4, nonce_override=None)
- 2026-05-25 12:00:00: frm-004 `key_assigned` (key_version=2, replacement=None, nonce_override=None)
- 2026-05-06 09:00:00: frm-005 `key_assigned` (key_version=3, replacement=None, nonce_override=None)
- 2026-05-19 14:00:00: frm-005 `key_rotated` (key_version=3, replacement=2, nonce_override=None)
- 2026-05-08 09:00:00: frm-006 `key_assigned` (key_version=2, replacement=None, nonce_override=None)
- 2026-05-11 10:00:00: frm-007 `key_assigned` (key_version=2, replacement=None, nonce_override=None)
- 2026-05-20 14:00:00: frm-007 `nonce_override_registered` (key_version=2, replacement=None, nonce_override=DEADBEEF0000000000000000)
- 2026-05-23 15:30:00: frm-007 `nonce_override_registered` (key_version=2, replacement=None, nonce_override=B4E19A7305C2D8F61E0A4B9C)
- 2026-05-13 09:00:00: frm-008 `key_assigned` (key_version=2, replacement=None, nonce_override=None)
- 2026-05-21 10:00:00: frm-008 `nonce_override_registered` (key_version=2, replacement=None, nonce_override=FFFFFFFFFFFFFFFFFFFFFFFF)
- 2026-05-24 16:00:00: frm-008 `nonce_override_registered` (key_version=2, replacement=None, nonce_override=C1D2E3F4029384758690A1B2)

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

```json
["rotation_replacement", "latest_key_assigned"]
```

### C.2 Nonce selection

1. **report_override** — when Appendix D names an explicit nonce override,
   that 12-byte value must be used.
2. **derived_sha256_prefix** — otherwise derive the nonce as the first 12 bytes
   of SHA-256(frame_id + ':' + key_version), unless one or more
   `nonce_override_registered` audit events exist for the frame; then the
   event with the greatest `recorded_at` is operative.

```json
["report_override", "derived_sha256_prefix"]
```

The derived-nonce rule in prose: SHA-256(frame_id + ':' + key_version), first 12 bytes.

## Appendix D (draft — superseded April 2026 circulation)

A withdrawn draft listed a nonce override for frm-007 that was never
registered in the audit ledger. It must not be used for reproduction.

Withdrawn draft value for frm-007: `DEADBEEF0000000000000000`.

## Appendix D — Registered nonce overrides

Two frames carry an explicit nonce override. Every override listed here must be
transcribed; a reader that captures only the first will derive a wrong nonce for
the second and fail authentication.

### D.1 frm-003 (charlie-channel)

The operative nonce override for frm-003 is `A7C3E91B4D2F8065E1B9C0A3`.

This override was registered after a vault ceremony mismatch and must be used
instead of the derived nonce when authenticating the charlie-channel GIF frame.

### D.2 frm-006 (foxtrot-channel)

The operative nonce override for frm-006 is `3F08D5621CA4790BEE17F2D8`.

Like D.1, this 12-byte value supersedes the derived nonce for the foxtrot-channel
frame and must be used verbatim when authenticating its GIF payload.

