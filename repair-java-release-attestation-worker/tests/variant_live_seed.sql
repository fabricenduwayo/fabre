DELETE FROM attestation_reports;
DELETE FROM pending_attestations;
DELETE FROM artifact_evidence;

INSERT INTO artifact_evidence (artifact_id, channel_id, version, sha256_digest, signer_key_id, revoked) VALUES
  ('art-live', 'stable', '3.0.0', 'dbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb', 'key-b', FALSE);

INSERT INTO pending_attestations (queue_id, artifact_id, enqueued_at) VALUES
  ('q-live', 'art-live', TIMESTAMP '2026-04-01 11:00:00');
