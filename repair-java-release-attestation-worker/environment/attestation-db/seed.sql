INSERT INTO release_channels (channel_id, name) VALUES
  ('stable', 'Stable'),
  ('beta', 'Beta');

INSERT INTO artifact_evidence (artifact_id, channel_id, version, sha256_digest, signer_key_id, revoked) VALUES
  ('art-alpha',   'stable', '2.4.1', 'd1111111111111111111111111111111111111111111111111111111111111', 'key-a', FALSE),
  ('art-beta',    'stable', '2.4.0', 'd2222222222222222222222222222222222222222222222222222222222222', 'key-b', FALSE),
  ('art-gamma',   'beta',   '1.9.0', 'd3333333333333333333333333333333333333333333333333333333333333', 'key-c', TRUE),
  ('art-delta',   'stable', '2.3.9', 'd4444444444444444444444444444444444444444444444444444444444444', 'key-a', FALSE),
  ('art-epsilon', 'beta',   '1.8.2', 'd5555555555555555555555555555555555555555555555555555555555555', 'key-b', FALSE);

INSERT INTO pending_attestations (queue_id, artifact_id, enqueued_at) VALUES
  ('q-001', 'art-alpha',   TIMESTAMP '2026-03-01 09:00:00'),
  ('q-002', 'art-beta',    TIMESTAMP '2026-03-01 09:05:00'),
  ('q-003', 'art-gamma',   TIMESTAMP '2026-03-01 09:10:00'),
  ('q-004', 'art-delta',   TIMESTAMP '2026-03-01 09:15:00'),
  ('q-005', 'art-epsilon', TIMESTAMP '2026-03-01 09:20:00');
