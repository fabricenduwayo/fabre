INSERT INTO release_channels (channel_id, name) VALUES
  ('stable', 'Stable'),
  ('edge',   'Edge');

INSERT INTO signing_keys (key_id, subject, not_before, not_after) VALUES
  ('key-a', 'Release Engineering', TIMESTAMP '2025-01-01 00:00:00', TIMESTAMP '2027-01-01 00:00:00'),
  ('key-b', 'Packaging',           TIMESTAMP '2025-01-01 00:00:00', TIMESTAMP '2026-02-15 00:00:00'),
  ('key-c', 'Build Farm',          TIMESTAMP '2025-01-01 00:00:00', TIMESTAMP '2026-02-01 00:00:00'),
  ('key-d', 'Legacy Mirror',       TIMESTAMP '2025-01-01 00:00:00', TIMESTAMP '2027-01-01 00:00:00'),
  ('key-e', 'Nightly Signer',      TIMESTAMP '2025-01-01 00:00:00', TIMESTAMP '2027-01-01 00:00:00');

INSERT INTO key_lifecycle_events (event_id, key_id, event_type, reason, occurred_at, effective_from) VALUES
  ('kev-001', 'key-a', 'activate', NULL,                     TIMESTAMP '2025-01-01 00:00:00', NULL),
  ('kev-002', 'key-b', 'activate', NULL,                     TIMESTAMP '2025-01-01 00:00:00', NULL),
  ('kev-003', 'key-c', 'activate', NULL,                     TIMESTAMP '2025-01-01 00:00:00', NULL),
  ('kev-004', 'key-d', 'activate', NULL,                     TIMESTAMP '2025-01-01 00:00:00', NULL),
  ('kev-005', 'key-c', 'revoke',   'key_compromise',         TIMESTAMP '2026-03-05 12:00:00', TIMESTAMP '2026-01-15 00:00:00'),
  ('kev-006', 'key-d', 'revoke',   'cessation_of_operation', TIMESTAMP '2026-02-20 09:00:00', TIMESTAMP '2025-06-01 00:00:00'),
  ('kev-007', 'key-e', 'activate', NULL,                     TIMESTAMP '2025-01-01 00:00:00', NULL),
  ('kev-008', 'key-e', 'revoke',   'key_compromise',         TIMESTAMP '2026-03-08 10:00:00', TIMESTAMP '2026-01-10 00:00:00');

INSERT INTO timestamp_authorities (tsa_id, name, valid_from, valid_until) VALUES
  ('tsa-1', 'Corp TSA',   TIMESTAMP '2025-01-01 00:00:00', TIMESTAMP '2027-01-01 00:00:00'),
  ('tsa-2', 'Legacy TSA', TIMESTAMP '2025-01-01 00:00:00', TIMESTAMP '2026-01-01 00:00:00');

INSERT INTO artifacts (artifact_id, channel_id, version) VALUES
  ('art-alpha',   'stable', '2.4.1'),
  ('art-beta',    'stable', '2.4.0'),
  ('art-gamma',   'stable', '2.5.0'),
  ('art-delta',   'stable', '2.3.9'),
  ('art-epsilon', 'edge',   '1.9.0'),
  ('art-zeta',    'edge',   '1.9.1'),
  ('art-omega',   'edge',   '1.9.2'),
  ('art-eta',     'stable', '1.8.2'),
  ('art-theta',   'stable', '2.6.0'),
  ('art-iota',    'stable', '2.6.1'),
  ('art-kappa',   'edge',   '1.9.3'),
  ('art-mu',      'stable', '2.7.0'),
  ('art-lambda',  'stable', '2.7.1'),
  ('art-nu',      'stable', '2.7.2'),
  ('art-omicron', 'stable', '2.6.2'),
  ('art-xi',      'edge',   '1.9.4'),
  ('art-pi',      'stable', '2.8.0'),
  ('art-rho',     'edge',   '0.9.5');

INSERT INTO artifact_evidence
  (evidence_id, artifact_id, sha256_digest, signer_key_id, signed_at, recorded_at,
   status, supersedes_evidence_id, amendment_key_id, tsa_id) VALUES
  ('ev-a1', 'art-alpha',   RPAD('a1a1a1a1', 64, '0'), 'key-a', TIMESTAMP '2026-02-10 08:00:00', TIMESTAMP '2026-02-10 08:05:00', 'attested',    NULL,    NULL,    NULL),

  ('ev-b1', 'art-beta',    RPAD('b1b1b1b1', 64, '0'), 'key-a', TIMESTAMP '2026-01-15 08:00:00', TIMESTAMP '2026-01-15 08:05:00', 'attested',    NULL,    NULL,    NULL),
  ('ev-b2', 'art-beta',    RPAD('b2b2b2b2', 64, '0'), 'key-a', TIMESTAMP '2026-02-18 08:00:00', TIMESTAMP '2026-02-18 08:05:00', 'attested',    'ev-b1', 'key-a', NULL),

  ('ev-g1', 'art-gamma',   RPAD('c1c1c1c1', 64, '0'), 'key-a', TIMESTAMP '2026-01-05 08:00:00', TIMESTAMP '2026-01-05 08:05:00', 'attested',    NULL,    NULL,    NULL),
  ('ev-g2', 'art-gamma',   RPAD('c2c2c2c2', 64, '0'), 'key-a', TIMESTAMP '2026-01-20 08:00:00', TIMESTAMP '2026-01-20 08:05:00', 'attested',    'ev-g1', 'key-a', NULL),
  ('ev-g3', 'art-gamma',   RPAD('c3c3c3c3', 64, '0'), 'key-a', TIMESTAMP '2026-02-02 08:00:00', TIMESTAMP '2026-02-02 08:05:00', 'withdrawn',   'ev-g2', 'key-a', NULL),

  ('ev-d1', 'art-delta',   RPAD('d1d1d1d1', 64, '0'), 'key-a', TIMESTAMP '2026-02-01 08:00:00', TIMESTAMP '2026-02-01 08:05:00', 'attested',    NULL,    NULL,    NULL),
  ('ev-d2', 'art-delta',   RPAD('d2d2d2d2', 64, '0'), 'key-a', TIMESTAMP '2026-03-10 08:00:00', TIMESTAMP '2026-03-10 08:05:00', 'attested',    'ev-d1', 'key-c', NULL),

  ('ev-e1', 'art-epsilon', RPAD('e1e1e1e1', 64, '0'), 'key-c', TIMESTAMP '2026-01-20 08:00:00', TIMESTAMP '2026-01-20 08:05:00', 'attested',    NULL,    NULL,    NULL),
  ('ev-z1', 'art-zeta',    RPAD('f1f1f1f1', 64, '0'), 'key-c', TIMESTAMP '2026-01-05 08:00:00', TIMESTAMP '2026-01-05 08:05:00', 'attested',    NULL,    NULL,    'tsa-1'),
  ('ev-o1', 'art-omega',   RPAD('0a0a0a0a', 64, '0'), 'key-c', TIMESTAMP '2026-01-06 08:00:00', TIMESTAMP '2026-01-06 08:05:00', 'attested',    NULL,    NULL,    NULL),
  ('ev-k1', 'art-kappa',   RPAD('4e4e4e4e', 64, '0'), 'key-c', TIMESTAMP '2026-02-05 08:00:00', TIMESTAMP '2026-02-05 08:05:00', 'attested',    NULL,    NULL,    'tsa-1'),

  ('ev-h1', 'art-eta',     RPAD('1b1b1b1b', 64, '0'), 'key-d', TIMESTAMP '2026-01-15 08:00:00', TIMESTAMP '2026-01-15 08:05:00', 'attested',    NULL,    NULL,    NULL),

  ('ev-t1', 'art-theta',   RPAD('2c2c2c2c', 64, '0'), 'key-b', TIMESTAMP '2026-03-01 08:00:00', TIMESTAMP '2026-03-01 08:05:00', 'attested',    NULL,    NULL,    NULL),
  ('ev-i1', 'art-iota',    RPAD('3d3d3d3d', 64, '0'), 'key-b', TIMESTAMP '2026-03-02 08:00:00', TIMESTAMP '2026-03-02 08:05:00', 'attested',    NULL,    NULL,    'tsa-1'),

  ('ev-m1', 'art-mu',      RPAD('5f5f5f5f', 64, '0'), 'key-a', TIMESTAMP '2026-02-11 08:00:00', TIMESTAMP '2026-02-11 08:05:00', 'provisional', NULL,    NULL,    NULL),

  ('ev-n1', 'art-nu',      RPAD('6a6a6a6a', 64, '0'), 'key-a', TIMESTAMP '2026-02-12 08:00:00', TIMESTAMP '2026-02-12 08:05:00', 'attested',    NULL,    NULL,    NULL),

  ('ev-x1', 'art-omicron', RPAD('7b7b7b7b', 64, '0'), 'key-b', TIMESTAMP '2026-03-03 08:00:00', TIMESTAMP '2026-03-03 08:05:00', 'attested',    NULL,    NULL,    'tsa-2'),

  ('ev-x2', 'art-xi',      RPAD('8c8c8c8c', 64, '0'), 'key-a', TIMESTAMP '2026-01-10 00:00:00', TIMESTAMP '2026-01-10 08:05:00', 'attested',    NULL,    NULL,    'tsa-1'),

  ('ev-p1', 'art-pi',      RPAD('9d9d9d9d', 64, '0'), 'key-a', TIMESTAMP '2026-02-05 08:00:00', TIMESTAMP '2026-02-05 08:05:00', 'attested',    NULL,    NULL,    NULL),
  ('ev-p2', 'art-pi',      RPAD('aeaeaeae', 64, '0'), 'key-a', TIMESTAMP '2026-03-01 08:00:00', TIMESTAMP '2026-03-01 08:05:00', 'attested',    'ev-p1', 'key-c', NULL),
  ('ev-p3', 'art-pi',      RPAD('bfbfbfbf', 64, '0'), 'key-a', TIMESTAMP '2026-03-15 08:00:00', TIMESTAMP '2026-03-15 08:05:00', 'withdrawn',   'ev-p2', 'key-a', NULL),

  ('ev-r1', 'art-rho',     RPAD('cacacaca', 64, '0'), 'key-e', TIMESTAMP '2026-01-09 08:00:00', TIMESTAMP '2026-01-09 08:05:00', 'attested',    NULL,    NULL,    NULL);

INSERT INTO pending_attestations (queue_id, artifact_id, enqueued_at) VALUES
  ('q-001', 'art-alpha',   TIMESTAMP '2026-03-20 09:00:00'),
  ('q-002', 'art-beta',    TIMESTAMP '2026-03-20 09:01:00'),
  ('q-003', 'art-gamma',   TIMESTAMP '2026-03-20 09:02:00'),
  ('q-004', 'art-delta',   TIMESTAMP '2026-03-20 09:03:00'),
  ('q-005', 'art-epsilon', TIMESTAMP '2026-03-20 09:04:00'),
  ('q-006', 'art-zeta',    TIMESTAMP '2026-03-20 09:05:00'),
  ('q-007', 'art-omega',   TIMESTAMP '2026-03-20 09:06:00'),
  ('q-008', 'art-eta',     TIMESTAMP '2026-03-20 09:07:00'),
  ('q-009', 'art-theta',   TIMESTAMP '2026-03-20 09:08:00'),
  ('q-010', 'art-iota',    TIMESTAMP '2026-03-20 09:09:00'),
  ('q-011', 'art-kappa',   TIMESTAMP '2026-03-20 09:10:00'),
  ('q-012', 'art-mu',      TIMESTAMP '2026-03-20 09:11:00'),
  ('q-013', 'art-lambda',  TIMESTAMP '2026-03-20 09:12:00'),
  ('q-014', 'art-nu',      TIMESTAMP '2026-03-20 09:13:00'),
  ('q-015', 'art-omicron', TIMESTAMP '2026-03-20 09:14:00'),
  ('q-016', 'art-xi',      TIMESTAMP '2026-03-20 09:15:00'),
  ('q-017', 'art-pi',      TIMESTAMP '2026-03-20 09:16:00');
