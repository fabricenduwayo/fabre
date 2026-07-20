DELETE FROM attestation_reports;
DELETE FROM pending_attestations;
DELETE FROM artifact_evidence;

INSERT INTO artifact_evidence (artifact_id, channel_id, version, sha256_digest, signer_key_id, revoked) VALUES
  ('art-probe', 'stable', '9.9.9', 'daaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa', 'key-a', FALSE);

INSERT INTO pending_attestations (queue_id, artifact_id, enqueued_at) VALUES
  ('q-probe', 'art-probe', TIMESTAMP '2026-04-01 10:00:00');
