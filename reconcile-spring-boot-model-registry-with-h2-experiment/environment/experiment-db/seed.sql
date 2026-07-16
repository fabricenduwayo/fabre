-- Canonical validation evidence for the churn-model registry.
-- Multiple validation_runs per model; amendments define which run is operative.

INSERT INTO models (id, name, version) VALUES ('alpha', 'churn-model-alpha', '1.2.0');
INSERT INTO models (id, name, version) VALUES ('beta',  'churn-model-beta',  '0.9.1');
INSERT INTO models (id, name, version) VALUES ('gamma', 'churn-model-gamma', '2.0.0');
INSERT INTO models (id, name, version) VALUES ('delta', 'churn-model-delta', '1.0.3');
INSERT INTO models (id, name, version) VALUES ('omega', 'churn-model-omega', '1.4.2');
INSERT INTO models (id, name, version) VALUES ('zeta',  'churn-model-zeta',  '0.3.1');

-- alpha: older completed run fails; a newer failed run must not override; latest completed passes
INSERT INTO validation_runs (run_id, model_id, captured_at, status, auc, accuracy)
  VALUES ('alpha-run-1', 'alpha', TIMESTAMP '2026-01-10 08:00:00', 'completed', 0.75, 0.70);
INSERT INTO validation_runs (run_id, model_id, captured_at, status, auc, accuracy)
  VALUES ('alpha-run-fail', 'alpha', TIMESTAMP '2026-03-01 09:00:00', 'failed', 0.99, 0.99);
INSERT INTO validation_runs (run_id, model_id, captured_at, status, auc, accuracy)
  VALUES ('alpha-run-2', 'alpha', TIMESTAMP '2026-03-20 10:00:00', 'completed', 0.87, 0.82);

-- beta: an older passing completed run is stale; latest completed still fails Gate 1
INSERT INTO validation_runs (run_id, model_id, captured_at, status, auc, accuracy)
  VALUES ('beta-run-1', 'beta', TIMESTAMP '2026-01-05 08:00:00', 'completed', 0.88, 0.81);
INSERT INTO validation_runs (run_id, model_id, captured_at, status, auc, accuracy)
  VALUES ('beta-run-2', 'beta', TIMESTAMP '2026-03-01 10:00:00', 'completed', 0.74, 0.79);

INSERT INTO validation_runs (run_id, model_id, captured_at, status, auc, accuracy)
  VALUES ('gamma-run-1', 'gamma', TIMESTAMP '2026-02-01 08:00:00', 'completed', 0.88, 0.81);
INSERT INTO validation_runs (run_id, model_id, captured_at, status, auc, accuracy)
  VALUES ('delta-run-1', 'delta', TIMESTAMP '2026-02-01 08:00:00', 'completed', 0.90, 0.85);
INSERT INTO validation_runs (run_id, model_id, captured_at, status, auc, accuracy)
  VALUES ('omega-run-1', 'omega', TIMESTAMP '2026-02-01 08:00:00', 'completed', 0.84, 0.80);
INSERT INTO validation_runs (run_id, model_id, captured_at, status, auc, accuracy)
  VALUES ('zeta-run-1', 'zeta', TIMESTAMP '2026-02-01 08:00:00', 'completed', 0.95, 0.90);

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
