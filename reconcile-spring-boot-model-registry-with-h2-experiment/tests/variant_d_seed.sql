-- Variant D: operative-run anchoring composes with transitive voiding, quorum,
-- replacement integrity, and stale regrant approvals.

INSERT INTO models (id, name, version) VALUES ('alpha', 'churn-model-alpha', '1.2.0');
INSERT INTO models (id, name, version) VALUES ('beta',  'churn-model-beta',  '0.9.1');
INSERT INTO models (id, name, version) VALUES ('gamma', 'churn-model-gamma', '2.0.0');
INSERT INTO models (id, name, version) VALUES ('delta', 'churn-model-delta', '1.0.3');
INSERT INTO models (id, name, version) VALUES ('omega', 'churn-model-omega', '1.4.2');
INSERT INTO models (id, name, version) VALUES ('zeta',  'churn-model-zeta',  '0.3.1');

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
INSERT INTO validation_runs (run_id, model_id, captured_at, status, auc, accuracy, supersedes_run_id)
  VALUES ('beta-run-1', 'beta', TIMESTAMP '2026-01-05 08:00:00', 'completed', 0.88, 0.81, NULL);
INSERT INTO validation_runs (run_id, model_id, captured_at, status, auc, accuracy, supersedes_run_id)
  VALUES ('beta-run-2', 'beta', TIMESTAMP '2026-03-01 10:00:00', 'completed', 0.74, 0.79, NULL);
INSERT INTO validation_runs (run_id, model_id, captured_at, status, auc, accuracy, supersedes_run_id)
  VALUES ('beta-run-3', 'beta', TIMESTAMP '2026-04-10 10:00:00', 'completed', 0.72, 0.79, 'beta-run-2');
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

INSERT INTO calibration_events (event_id, model_id, event_type, occurred_at)
  VALUES ('delta-cal-1', 'delta', 'calibrate', TIMESTAMP '2026-02-15 08:00:00');
INSERT INTO calibration_events (event_id, model_id, event_type, occurred_at)
  VALUES ('delta-uncal-1', 'delta', 'uncalibrate', TIMESTAMP '2026-04-14 09:00:00');
INSERT INTO calibration_events (event_id, model_id, event_type, occurred_at)
  VALUES ('omega-cal-a', 'omega', 'uncalibrate', TIMESTAMP '2026-04-12 08:00:00');
INSERT INTO calibration_events (event_id, model_id, event_type, occurred_at)
  VALUES ('omega-cal-z', 'omega', 'calibrate', TIMESTAMP '2026-04-12 08:00:00');

INSERT INTO release_context VALUES
  ('current-release', TIMESTAMP '2026-04-15 12:00:00');

INSERT INTO promotion_waivers VALUES
  ('gamma-calibration', 'gamma', '2.0.0', 'uncalibrated',
   TIMESTAMP '2026-01-01 00:00:00', TIMESTAMP '2026-07-01 00:00:00', NULL, NULL);
INSERT INTO promotion_waivers VALUES
  ('beta-metric-quorum', 'beta', '0.9.1', 'metric_threshold',
   TIMESTAMP '2026-01-01 00:00:00', TIMESTAMP '2026-07-01 00:00:00', NULL, NULL);
INSERT INTO promotion_waivers VALUES
  ('beta-metric-anchored-stale', 'beta', '0.9.1', 'metric_threshold',
   TIMESTAMP '2026-01-01 00:00:00', TIMESTAMP '2026-07-01 00:00:00', NULL, 'beta-run-2');
INSERT INTO promotion_waivers VALUES
  ('beta-metric-anchored-live', 'beta', '0.9.1', 'metric_threshold',
   TIMESTAMP '2026-01-01 00:00:00', TIMESTAMP '2026-07-01 00:00:00', NULL, 'beta-run-3');
INSERT INTO promotion_waivers VALUES
  ('beta-metric-anchored-ok', 'beta', '0.9.1', 'metric_threshold',
   TIMESTAMP '2026-01-01 00:00:00', TIMESTAMP '2026-07-01 00:00:00', NULL, 'beta-run-3');
INSERT INTO promotion_waivers VALUES
  ('beta-metric-new-bad', 'beta', '0.9.1', 'metric_threshold',
   TIMESTAMP '2026-04-01 00:00:00', TIMESTAMP '2026-07-01 00:00:00',
   'beta-metric-quorum', 'beta-run-3');

INSERT INTO waiver_events VALUES
  ('event-gamma-grant', 'gamma-calibration', 'grant',
   TIMESTAMP '2026-01-05 09:00:00', NULL);
INSERT INTO waiver_events VALUES
  ('event-gamma-revoke', 'gamma-calibration', 'revoke',
   TIMESTAMP '2026-02-05 09:00:00', NULL);
INSERT INTO waiver_events VALUES
  ('event-gamma-regrant', 'gamma-calibration', 'grant',
   TIMESTAMP '2026-03-05 09:00:00', NULL);
INSERT INTO waiver_events VALUES
  ('event-beta-quorum-grant', 'beta-metric-quorum', 'grant',
   TIMESTAMP '2026-01-02 09:00:00', NULL);
INSERT INTO waiver_events VALUES
  ('event-beta-stale-grant', 'beta-metric-anchored-stale', 'grant',
   TIMESTAMP '2026-01-03 09:00:00', NULL);
INSERT INTO waiver_events VALUES
  ('event-beta-live-grant', 'beta-metric-anchored-live', 'grant',
   TIMESTAMP '2026-04-11 09:00:00', NULL);
INSERT INTO waiver_events VALUES
  ('event-beta-ok-grant', 'beta-metric-anchored-ok', 'grant',
   TIMESTAMP '2026-04-09 09:00:00', NULL);
INSERT INTO waiver_events VALUES
  ('event-beta-quorum-revoke', 'beta-metric-quorum', 'revoke',
   TIMESTAMP '2026-04-01 10:00:00', NULL);
INSERT INTO waiver_events VALUES
  ('event-beta-new-bad-grant', 'beta-metric-new-bad', 'grant',
   TIMESTAMP '2026-04-01 10:00:00', NULL);
UPDATE waiver_events SET paired_event_id = 'event-beta-new-bad-grant'
  WHERE event_id = 'event-beta-quorum-revoke';
UPDATE waiver_events SET paired_event_id = 'event-beta-quorum-revoke'
  WHERE event_id = 'event-beta-new-bad-grant';

INSERT INTO waiver_approval_events VALUES
  ('approval-gamma-risk', 'gamma-calibration', 'reviewer-risk-2', 'risk',
   'approve', TIMESTAMP '2026-01-06 09:00:00');
INSERT INTO waiver_approval_events VALUES
  ('approval-gamma-owner', 'gamma-calibration', 'reviewer-owner-2',
   'model_owner', 'approve', TIMESTAMP '2026-01-06 10:00:00');
INSERT INTO waiver_approval_events VALUES
  ('approval-beta-q-risk', 'beta-metric-quorum', 'reviewer-risk-1', 'risk',
   'approve', TIMESTAMP '2026-01-03 09:00:00');
INSERT INTO waiver_approval_events VALUES
  ('approval-beta-q-owner', 'beta-metric-quorum', 'reviewer-owner-1',
   'model_owner', 'approve', TIMESTAMP '2026-01-03 10:00:00');
INSERT INTO waiver_approval_events VALUES
  ('approval-beta-stale-risk', 'beta-metric-anchored-stale', 'reviewer-risk-3', 'risk',
   'approve', TIMESTAMP '2026-01-04 09:00:00');
INSERT INTO waiver_approval_events VALUES
  ('approval-beta-stale-owner', 'beta-metric-anchored-stale', 'reviewer-owner-3',
   'model_owner', 'approve', TIMESTAMP '2026-01-04 10:00:00');
INSERT INTO waiver_approval_events VALUES
  ('approval-beta-live-risk', 'beta-metric-anchored-live', 'reviewer-risk-4', 'risk',
   'approve', TIMESTAMP '2026-04-11 10:00:00');
INSERT INTO waiver_approval_events VALUES
  ('approval-beta-live-owner', 'beta-metric-anchored-live', 'reviewer-owner-4',
   'model_owner', 'approve', TIMESTAMP '2026-04-11 11:00:00');
INSERT INTO waiver_approval_events VALUES
  ('approval-beta-ok-risk', 'beta-metric-anchored-ok', 'reviewer-risk-5', 'risk',
   'approve', TIMESTAMP '2026-04-09 10:00:00');
INSERT INTO waiver_approval_events VALUES
  ('approval-beta-ok-owner', 'beta-metric-anchored-ok', 'reviewer-owner-5',
   'model_owner', 'approve', TIMESTAMP '2026-04-09 11:00:00');
