-- Canonical validation evidence for the churn-model registry.
-- Multiple validation_runs per model; amendments define which run is operative.

INSERT INTO models (id, name, version) VALUES ('alpha', 'churn-model-alpha', '1.2.0');
INSERT INTO models (id, name, version) VALUES ('beta',  'churn-model-beta',  '0.9.1');
INSERT INTO models (id, name, version) VALUES ('gamma', 'churn-model-gamma', '2.0.0');
INSERT INTO models (id, name, version) VALUES ('delta', 'churn-model-delta', '1.0.3');
INSERT INTO models (id, name, version) VALUES ('omega', 'churn-model-omega', '1.4.2');
INSERT INTO models (id, name, version) VALUES ('zeta',  'churn-model-zeta',  '0.3.1');

-- alpha: older completed run fails; a later failed run must not override;
-- a superseded row voids the latest completed row so the operative run fails Gate 1
INSERT INTO validation_runs (run_id, model_id, captured_at, status, auc, accuracy, supersedes_run_id)
  VALUES ('alpha-run-1', 'alpha', TIMESTAMP '2026-01-10 08:00:00', 'completed', 0.75, 0.70, NULL);
INSERT INTO validation_runs (run_id, model_id, captured_at, status, auc, accuracy, supersedes_run_id)
  VALUES ('alpha-run-fail', 'alpha', TIMESTAMP '2026-03-01 09:00:00', 'failed', 0.99, 0.99, NULL);
INSERT INTO validation_runs (run_id, model_id, captured_at, status, auc, accuracy, supersedes_run_id)
  VALUES ('alpha-run-2', 'alpha', TIMESTAMP '2026-03-20 10:00:00', 'completed', 0.87, 0.82, 'alpha-run-1');
INSERT INTO validation_runs (run_id, model_id, captured_at, status, auc, accuracy, supersedes_run_id)
  VALUES ('alpha-run-void', 'alpha', TIMESTAMP '2026-03-22 11:00:00', 'superseded', 0.91, 0.88, 'alpha-run-2');
INSERT INTO validation_runs (run_id, model_id, captured_at, status, auc, accuracy, supersedes_run_id)
  VALUES ('alpha-run-3', 'alpha', TIMESTAMP '2026-03-25 10:00:00', 'completed', 0.83, 0.78, NULL);

-- beta: an older passing completed run is stale; latest completed still fails Gate 1
INSERT INTO validation_runs (run_id, model_id, captured_at, status, auc, accuracy, supersedes_run_id)
  VALUES ('beta-run-1', 'beta', TIMESTAMP '2026-01-05 08:00:00', 'completed', 0.88, 0.81, NULL);
INSERT INTO validation_runs (run_id, model_id, captured_at, status, auc, accuracy, supersedes_run_id)
  VALUES ('beta-run-2', 'beta', TIMESTAMP '2026-03-01 10:00:00', 'completed', 0.74, 0.79, NULL);

INSERT INTO validation_runs (run_id, model_id, captured_at, status, auc, accuracy, supersedes_run_id)
  VALUES ('gamma-run-1', 'gamma', TIMESTAMP '2026-02-01 08:00:00', 'completed', 0.88, 0.81, NULL);
INSERT INTO validation_runs (run_id, model_id, captured_at, status, auc, accuracy, supersedes_run_id)
  VALUES ('delta-run-1', 'delta', TIMESTAMP '2026-02-01 08:00:00', 'completed', 0.90, 0.85, NULL);
INSERT INTO validation_runs (run_id, model_id, captured_at, status, auc, accuracy, supersedes_run_id)
  VALUES ('omega-run-1', 'omega', TIMESTAMP '2026-02-01 08:00:00', 'completed', 0.84, 0.80, NULL);
INSERT INTO validation_runs (run_id, model_id, captured_at, status, auc, accuracy, supersedes_run_id)
  VALUES ('zeta-run-1', 'zeta', TIMESTAMP '2026-02-01 08:00:00', 'completed', 0.95, 0.90, NULL);

INSERT INTO feature_hash_lineage (model_id, model_version, feature_hash) VALUES ('alpha', '1.1.0', 'fh_alpha_77d');
INSERT INTO feature_hash_lineage (model_id, model_version, feature_hash) VALUES ('alpha', '1.2.0', 'fh_alpha_9c1');
INSERT INTO feature_hash_lineage (model_id, model_version, feature_hash) VALUES ('beta',  '0.9.0', 'fh_beta_310');
INSERT INTO feature_hash_lineage (model_id, model_version, feature_hash) VALUES ('beta',  '0.9.1', 'fh_beta_44a');
INSERT INTO feature_hash_lineage (model_id, model_version, feature_hash) VALUES ('gamma', '1.9.0', 'fh_gamma_55e');
INSERT INTO feature_hash_lineage (model_id, model_version, feature_hash) VALUES ('gamma', '2.0.0', 'fh_gamma_7d2');
INSERT INTO feature_hash_lineage (model_id, model_version, feature_hash) VALUES ('delta', '1.0.2', 'fh_delta_9f4');
INSERT INTO feature_hash_lineage (model_id, model_version, feature_hash) VALUES ('delta', '1.0.3', 'fh_delta_5e8');
INSERT INTO feature_hash_lineage (model_id, model_version, feature_hash) VALUES ('omega', '1.4.2', 'fh_omega_2b7');
INSERT INTO feature_hash_lineage (model_id, model_version, feature_hash) VALUES ('zeta',  '0.3.1', 'fh_zeta_a19');

INSERT INTO calibration_status (model_id, calibrated, method) VALUES ('alpha', TRUE,  'isotonic');
INSERT INTO calibration_status (model_id, calibrated, method) VALUES ('beta',  TRUE,  'platt');
INSERT INTO calibration_status (model_id, calibrated, method) VALUES ('gamma', FALSE, NULL);
INSERT INTO calibration_status (model_id, calibrated, method) VALUES ('delta', TRUE,  'isotonic');
INSERT INTO calibration_status (model_id, calibrated, method) VALUES ('omega', TRUE,  'platt');
INSERT INTO calibration_status (model_id, calibrated, method) VALUES ('zeta',  TRUE,  'isotonic');

-- delta's dashboard snapshot still says calibrated, but replayed events void it
-- before release_context.decision_at (A-2026-07).
INSERT INTO calibration_events (event_id, model_id, event_type, occurred_at)
  VALUES ('delta-cal-1', 'delta', 'calibrate', TIMESTAMP '2026-02-15 08:00:00');
INSERT INTO calibration_events (event_id, model_id, event_type, occurred_at)
  VALUES ('delta-uncal-1', 'delta', 'uncalibrate', TIMESTAMP '2026-04-14 09:00:00');

-- omega: same-timestamp calibration pair; event_id order decides the survivor
INSERT INTO calibration_events (event_id, model_id, event_type, occurred_at)
  VALUES ('omega-cal-a', 'omega', 'uncalibrate', TIMESTAMP '2026-04-12 08:00:00');
INSERT INTO calibration_events (event_id, model_id, event_type, occurred_at)
  VALUES ('omega-cal-z', 'omega', 'calibrate', TIMESTAMP '2026-04-12 08:00:00');

INSERT INTO release_context (context_id, decision_at)
  VALUES ('current-release', TIMESTAMP '2026-04-15 12:00:00');

-- delta has a valid replacement transaction plus an older overlapping grant.
-- The replacement is the latest applicable lineage waiver at decision time.
INSERT INTO promotion_waivers VALUES
  ('delta-lineage-old', 'delta', '1.0.3', 'lineage_mismatch',
   TIMESTAMP '2026-01-01 00:00:00', TIMESTAMP '2026-07-01 00:00:00', NULL);
INSERT INTO promotion_waivers VALUES
  ('delta-lineage-new', 'delta', '1.0.3', 'lineage_mismatch',
   TIMESTAMP '2026-04-01 00:00:00', TIMESTAMP '2026-07-01 00:00:00',
   'delta-lineage-old');
INSERT INTO promotion_waivers VALUES
  ('delta-lineage-alt', 'delta', '1.0.3', 'lineage_mismatch',
   TIMESTAMP '2026-03-01 00:00:00', TIMESTAMP '2026-07-01 00:00:00', NULL);

-- beta's predecessor is expired and its attempted replacement pair is
-- malformed because the two sides occurred at different times.
INSERT INTO promotion_waivers VALUES
  ('beta-metric-old', 'beta', '0.9.1', 'metric_threshold',
   TIMESTAMP '2026-01-01 00:00:00', TIMESTAMP '2026-03-31 00:00:00', NULL);
INSERT INTO promotion_waivers VALUES
  ('beta-metric-new', 'beta', '0.9.1', 'metric_threshold',
   TIMESTAMP '2026-04-01 00:00:00', TIMESTAMP '2026-07-01 00:00:00',
   'beta-metric-old');
INSERT INTO promotion_waivers VALUES
  ('beta-metric-quorum', 'beta', '0.9.1', 'metric_threshold',
   TIMESTAMP '2026-01-01 00:00:00', TIMESTAMP '2026-07-01 00:00:00', NULL);
INSERT INTO promotion_waivers VALUES
  ('beta-metric-noquorum', 'beta', '0.9.1', 'metric_threshold',
   TIMESTAMP '2026-01-01 00:00:00', TIMESTAMP '2026-07-01 00:00:00', NULL);

-- gamma is revoked; omega's live waiver is irrelevant because its metric gate
-- passes; alpha's grant occurs after the decision time.
INSERT INTO promotion_waivers VALUES
  ('gamma-calibration', 'gamma', '2.0.0', 'uncalibrated',
   TIMESTAMP '2026-01-01 00:00:00', TIMESTAMP '2026-07-01 00:00:00', NULL);
INSERT INTO promotion_waivers VALUES
  ('omega-metric', 'omega', '1.4.2', 'metric_threshold',
   TIMESTAMP '2026-01-01 00:00:00', TIMESTAMP '2026-07-01 00:00:00', NULL);
INSERT INTO promotion_waivers VALUES
  ('alpha-metric-future', 'alpha', '1.2.0', 'metric_threshold',
   TIMESTAMP '2026-01-01 00:00:00', TIMESTAMP '2026-07-01 00:00:00', NULL);

INSERT INTO waiver_events VALUES
  ('event-delta-old-grant', 'delta-lineage-old', 'grant',
   TIMESTAMP '2026-01-05 09:00:00', NULL);
INSERT INTO waiver_events VALUES
  ('event-delta-alt-grant', 'delta-lineage-alt', 'grant',
   TIMESTAMP '2026-03-25 09:00:00', NULL);
INSERT INTO waiver_events VALUES
  ('event-delta-old-revoke', 'delta-lineage-old', 'revoke',
   TIMESTAMP '2026-04-01 10:00:00', NULL);
INSERT INTO waiver_events VALUES
  ('event-delta-new-grant', 'delta-lineage-new', 'grant',
   TIMESTAMP '2026-04-01 10:00:00', NULL);
UPDATE waiver_events SET paired_event_id = 'event-delta-new-grant'
  WHERE event_id = 'event-delta-old-revoke';
UPDATE waiver_events SET paired_event_id = 'event-delta-old-revoke'
  WHERE event_id = 'event-delta-new-grant';
INSERT INTO waiver_events VALUES
  ('event-delta-new-future-revoke', 'delta-lineage-new', 'revoke',
   TIMESTAMP '2026-05-01 10:00:00', NULL);

INSERT INTO waiver_events VALUES
  ('event-beta-old-grant', 'beta-metric-old', 'grant',
   TIMESTAMP '2026-01-02 09:00:00', NULL);
INSERT INTO waiver_events VALUES
  ('event-beta-old-revoke', 'beta-metric-old', 'revoke',
   TIMESTAMP '2026-04-01 10:00:00', NULL);
INSERT INTO waiver_events VALUES
  ('event-beta-new-grant', 'beta-metric-new', 'grant',
   TIMESTAMP '2026-04-02 10:00:00', NULL);
UPDATE waiver_events SET paired_event_id = 'event-beta-new-grant'
  WHERE event_id = 'event-beta-old-revoke';
UPDATE waiver_events SET paired_event_id = 'event-beta-old-revoke'
  WHERE event_id = 'event-beta-new-grant';
INSERT INTO waiver_events VALUES
  ('event-beta-quorum-grant', 'beta-metric-quorum', 'grant',
   TIMESTAMP '2026-01-02 10:00:00', NULL);
INSERT INTO waiver_events VALUES
  ('event-beta-noquorum-grant', 'beta-metric-noquorum', 'grant',
   TIMESTAMP '2026-01-10 10:00:00', NULL);

INSERT INTO waiver_events VALUES
  ('event-gamma-grant', 'gamma-calibration', 'grant',
   TIMESTAMP '2026-01-02 09:00:00', NULL);
INSERT INTO waiver_events VALUES
  ('event-gamma-revoke', 'gamma-calibration', 'revoke',
   TIMESTAMP '2026-04-10 09:00:00', NULL);
INSERT INTO waiver_events VALUES
  ('event-omega-grant', 'omega-metric', 'grant',
   TIMESTAMP '2026-01-02 09:00:00', NULL);
INSERT INTO waiver_events VALUES
  ('event-alpha-future-grant', 'alpha-metric-future', 'grant',
   TIMESTAMP '2026-04-20 09:00:00', NULL);

-- A-2026-11: the newer beta waiver has both role labels but the same reviewer
-- cannot satisfy both sides of quorum. The older waiver has distinct reviewers;
-- same-timestamp event_id ordering leaves its model-owner approval active.
INSERT INTO waiver_approval_events VALUES
  ('approval-beta-q-risk', 'beta-metric-quorum', 'reviewer-risk-1', 'risk',
   'approve', TIMESTAMP '2026-01-03 09:00:00');
INSERT INTO waiver_approval_events VALUES
  ('approval-beta-q-owner-a-withdraw', 'beta-metric-quorum', 'reviewer-owner-1',
   'model_owner', 'withdraw', TIMESTAMP '2026-01-03 10:00:00');
INSERT INTO waiver_approval_events VALUES
  ('approval-beta-q-owner-z-approve', 'beta-metric-quorum', 'reviewer-owner-1',
   'model_owner', 'approve', TIMESTAMP '2026-01-03 10:00:00');
INSERT INTO waiver_approval_events VALUES
  ('approval-beta-nq-risk', 'beta-metric-noquorum', 'reviewer-dual', 'risk',
   'approve', TIMESTAMP '2026-01-11 09:00:00');
INSERT INTO waiver_approval_events VALUES
  ('approval-beta-nq-owner', 'beta-metric-noquorum', 'reviewer-dual',
   'model_owner', 'approve', TIMESTAMP '2026-01-11 09:05:00');
