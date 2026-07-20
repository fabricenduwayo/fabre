-- A different store with the same artifact ids, so the registry fixture still
-- resolves but the derivation lands somewhere else than the shipped answer.
INSERT INTO release_channels (channel_id, name) VALUES
  ('stable', 'Stable'),
  ('edge',   'Edge');

INSERT INTO signing_keys (key_id, subject, not_before, not_after) VALUES
  ('key-a', 'Release Engineering', TIMESTAMP '2025-01-01 00:00:00', TIMESTAMP '2027-01-01 00:00:00'),
  ('key-c', 'Build Farm',          TIMESTAMP '2025-01-01 00:00:00', TIMESTAMP '2026-02-01 00:00:00');

INSERT INTO key_lifecycle_events (event_id, key_id, event_type, reason, occurred_at, effective_from) VALUES
  ('kev-001', 'key-a', 'activate', NULL,             TIMESTAMP '2025-01-01 00:00:00', NULL),
  ('kev-002', 'key-c', 'activate', NULL,             TIMESTAMP '2025-01-01 00:00:00', NULL),
  ('kev-003', 'key-c', 'revoke',   'key_compromise', TIMESTAMP '2026-03-05 12:00:00', TIMESTAMP '2026-01-10 00:00:00');

INSERT INTO artifacts (artifact_id, channel_id, version) VALUES
  ('art-beta',  'stable', '2.4.0'),
  ('art-delta', 'stable', '2.3.9');

INSERT INTO artifact_evidence
  (evidence_id, artifact_id, sha256_digest, signer_key_id, signed_at, recorded_at,
   status, supersedes_evidence_id, amendment_key_id, tsa_id) VALUES
  ('ev-v1', 'art-beta',  RPAD('b2b2b2b2', 64, '0'), 'key-a', TIMESTAMP '2026-02-18 08:00:00', TIMESTAMP '2026-02-18 08:05:00', 'attested', NULL, NULL, NULL),
  ('ev-v2', 'art-delta', RPAD('d1d1d1d1', 64, '0'), 'key-c', TIMESTAMP '2026-01-20 08:00:00', TIMESTAMP '2026-01-20 08:05:00', 'attested', NULL, NULL, NULL);

INSERT INTO pending_attestations (queue_id, artifact_id, enqueued_at) VALUES
  ('q-v1', 'art-beta',  TIMESTAMP '2026-04-01 11:00:00'),
  ('q-v2', 'art-delta', TIMESTAMP '2026-04-01 11:01:00');
