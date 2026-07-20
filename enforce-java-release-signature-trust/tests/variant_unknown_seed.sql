-- art-lambda carries no registry entry, so a worker that gets past the evidence
-- stage has to handle a lookup the registry cannot answer.
INSERT INTO release_channels (channel_id, name) VALUES
  ('stable', 'Stable');

INSERT INTO signing_keys (key_id, subject, not_before, not_after) VALUES
  ('key-a', 'Release Engineering', TIMESTAMP '2025-01-01 00:00:00', TIMESTAMP '2027-01-01 00:00:00');

INSERT INTO key_lifecycle_events (event_id, key_id, event_type, reason, occurred_at, effective_from) VALUES
  ('kev-001', 'key-a', 'activate', NULL, TIMESTAMP '2025-01-01 00:00:00', NULL);

INSERT INTO artifacts (artifact_id, channel_id, version) VALUES
  ('art-lambda', 'stable', '2.7.1');

INSERT INTO artifact_evidence
  (evidence_id, artifact_id, sha256_digest, signer_key_id, signed_at, recorded_at,
   status, supersedes_evidence_id, amendment_key_id, tsa_id) VALUES
  ('ev-u1', 'art-lambda', RPAD('cccccccc', 64, '0'), 'key-a', TIMESTAMP '2026-02-01 08:00:00', TIMESTAMP '2026-02-01 08:05:00', 'attested', NULL, NULL, NULL);

INSERT INTO pending_attestations (queue_id, artifact_id, enqueued_at) VALUES
  ('q-u1', 'art-lambda', TIMESTAMP '2026-04-01 11:00:00');
