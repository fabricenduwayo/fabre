-- Variant F: operative-run calibration cutoff, suppression-group arbitration,
-- and replacement group integrity must compose before waiver selection.

INSERT INTO models (id, name, version)
  VALUES ('omega', 'churn-model-omega', '1.4.2');
INSERT INTO models (id, name, version)
  VALUES ('beta', 'churn-model-beta', '0.9.1');

INSERT INTO validation_runs
  (run_id, model_id, captured_at, status, auc, accuracy, supersedes_run_id)
  VALUES
  ('omega-run-f', 'omega', TIMESTAMP '2026-03-01 10:00:00',
   'completed', 0.70, 0.70, NULL);
INSERT INTO validation_runs
  (run_id, model_id, captured_at, status, auc, accuracy, supersedes_run_id)
  VALUES
  ('beta-run-f', 'beta', TIMESTAMP '2026-03-01 10:00:00',
   'completed', 0.70, 0.80, NULL);

INSERT INTO feature_hash_lineage (model_id, model_version, feature_hash)
  VALUES ('omega', '1.4.2', 'fh_omega_2b7');
INSERT INTO feature_hash_lineage (model_id, model_version, feature_hash)
  VALUES ('beta', '0.9.1', 'fh_beta_44a');

INSERT INTO calibration_status (model_id, calibrated, method)
  VALUES ('omega', FALSE, NULL);
INSERT INTO calibration_status (model_id, calibrated, method)
  VALUES ('beta', TRUE, 'platt');

-- This event is visible at decision time but too late for omega's operative run.
INSERT INTO calibration_events (event_id, model_id, event_type, occurred_at)
  VALUES
  ('omega-cal-after-run', 'omega', 'calibrate',
   TIMESTAMP '2026-03-02 10:00:00');

INSERT INTO release_context (context_id, decision_at)
  VALUES ('current-release', TIMESTAMP '2026-04-01 12:00:00');

INSERT INTO promotion_waivers VALUES
  ('omega-metric-grouped', 'omega', '1.4.2', 'metric_threshold',
   TIMESTAMP '2026-01-01 00:00:00', TIMESTAMP '2026-06-01 00:00:00',
   NULL, NULL);
INSERT INTO promotion_waivers VALUES
  ('omega-calibration-grouped', 'omega', '1.4.2', 'uncalibrated',
   TIMESTAMP '2026-01-01 00:00:00', TIMESTAMP '2026-06-01 00:00:00',
   NULL, NULL);
INSERT INTO promotion_waivers VALUES
  ('beta-metric-old-group', 'beta', '0.9.1', 'metric_threshold',
   TIMESTAMP '2026-01-01 00:00:00', TIMESTAMP '2026-06-01 00:00:00',
   NULL, NULL);
INSERT INTO promotion_waivers VALUES
  ('beta-metric-new-group', 'beta', '0.9.1', 'metric_threshold',
   TIMESTAMP '2026-01-01 00:00:00', TIMESTAMP '2026-06-01 00:00:00',
   'beta-metric-old-group', NULL);

INSERT INTO waiver_suppression_groups VALUES
  ('omega-metric-grouped', 'omega-release');
INSERT INTO waiver_suppression_groups VALUES
  ('omega-calibration-grouped', 'omega-release');
INSERT INTO waiver_suppression_groups VALUES
  ('beta-metric-old-group', 'beta-old-release');
INSERT INTO waiver_suppression_groups VALUES
  ('beta-metric-new-group', 'beta-new-release');

INSERT INTO waiver_events VALUES
  ('event-omega-metric-grant', 'omega-metric-grouped', 'grant',
   TIMESTAMP '2026-01-10 09:00:00', NULL);
INSERT INTO waiver_events VALUES
  ('event-omega-cal-grant', 'omega-calibration-grouped', 'grant',
   TIMESTAMP '2026-02-10 09:00:00', NULL);
INSERT INTO waiver_events VALUES
  ('event-beta-old-grant', 'beta-metric-old-group', 'grant',
   TIMESTAMP '2026-01-05 09:00:00', NULL);
INSERT INTO waiver_events VALUES
  ('event-beta-old-revoke', 'beta-metric-old-group', 'revoke',
   TIMESTAMP '2026-02-01 09:00:00', NULL);
INSERT INTO waiver_events VALUES
  ('event-beta-new-grant', 'beta-metric-new-group', 'grant',
   TIMESTAMP '2026-02-01 09:00:00', NULL);
UPDATE waiver_events SET paired_event_id = 'event-beta-new-grant'
  WHERE event_id = 'event-beta-old-revoke';
UPDATE waiver_events SET paired_event_id = 'event-beta-old-revoke'
  WHERE event_id = 'event-beta-new-grant';

INSERT INTO reviewer_role_events VALUES
  ('role-risk-omega-metric', 'risk-omega-metric', 'risk', 'assign',
   TIMESTAMP '2026-01-01 08:00:00');
INSERT INTO reviewer_role_events VALUES
  ('role-owner-omega-metric', 'owner-omega-metric', 'model_owner', 'assign',
   TIMESTAMP '2026-01-01 08:00:00');
INSERT INTO reviewer_role_events VALUES
  ('role-risk-omega-cal', 'risk-omega-cal', 'risk', 'assign',
   TIMESTAMP '2026-01-01 08:00:00');
INSERT INTO reviewer_role_events VALUES
  ('role-owner-omega-cal', 'owner-omega-cal', 'model_owner', 'assign',
   TIMESTAMP '2026-01-01 08:00:00');
INSERT INTO reviewer_role_events VALUES
  ('role-risk-beta-new', 'risk-beta-new', 'risk', 'assign',
   TIMESTAMP '2026-01-01 08:00:00');
INSERT INTO reviewer_role_events VALUES
  ('role-owner-beta-new', 'owner-beta-new', 'model_owner', 'assign',
   TIMESTAMP '2026-01-01 08:00:00');

INSERT INTO waiver_approval_events VALUES
  ('approval-omega-metric-risk', 'omega-metric-grouped',
   'risk-omega-metric', 'risk', 'approve',
   TIMESTAMP '2026-01-11 09:00:00');
INSERT INTO waiver_approval_events VALUES
  ('approval-omega-metric-owner', 'omega-metric-grouped',
   'owner-omega-metric', 'model_owner', 'approve',
   TIMESTAMP '2026-01-11 10:00:00');
INSERT INTO waiver_approval_events VALUES
  ('approval-omega-cal-risk', 'omega-calibration-grouped',
   'risk-omega-cal', 'risk', 'approve',
   TIMESTAMP '2026-02-11 09:00:00');
INSERT INTO waiver_approval_events VALUES
  ('approval-omega-cal-owner', 'omega-calibration-grouped',
   'owner-omega-cal', 'model_owner', 'approve',
   TIMESTAMP '2026-02-11 10:00:00');
INSERT INTO waiver_approval_events VALUES
  ('approval-beta-new-risk', 'beta-metric-new-group',
   'risk-beta-new', 'risk', 'approve',
   TIMESTAMP '2026-02-02 09:00:00');
INSERT INTO waiver_approval_events VALUES
  ('approval-beta-new-owner', 'beta-metric-new-group',
   'owner-beta-new', 'model_owner', 'approve',
   TIMESTAMP '2026-02-02 10:00:00');
