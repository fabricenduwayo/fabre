-- Variant A: identical to the shipped evidence except alpha lost its
-- calibration. With alpha uncalibrated, the only remaining qualifier under the
-- policy is omega, so a generic implementation must flip its promotion.

INSERT INTO models (id, name, version) VALUES ('alpha', 'churn-model-alpha', '1.2.0');
INSERT INTO models (id, name, version) VALUES ('beta',  'churn-model-beta',  '0.9.1');
INSERT INTO models (id, name, version) VALUES ('gamma', 'churn-model-gamma', '2.0.0');
INSERT INTO models (id, name, version) VALUES ('delta', 'churn-model-delta', '1.0.3');
INSERT INTO models (id, name, version) VALUES ('omega', 'churn-model-omega', '1.4.2');
INSERT INTO models (id, name, version) VALUES ('zeta',  'churn-model-zeta',  '0.3.1');

INSERT INTO validation_metrics (model_id, auc, accuracy) VALUES ('alpha', 0.87, 0.82);
INSERT INTO validation_metrics (model_id, auc, accuracy) VALUES ('beta',  0.74, 0.79);
INSERT INTO validation_metrics (model_id, auc, accuracy) VALUES ('gamma', 0.88, 0.81);
INSERT INTO validation_metrics (model_id, auc, accuracy) VALUES ('delta', 0.90, 0.85);
INSERT INTO validation_metrics (model_id, auc, accuracy) VALUES ('omega', 0.84, 0.80);
INSERT INTO validation_metrics (model_id, auc, accuracy) VALUES ('zeta',  0.95, 0.90);

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

INSERT INTO calibration_status (model_id, calibrated, method) VALUES ('alpha', FALSE, NULL);
INSERT INTO calibration_status (model_id, calibrated, method) VALUES ('beta',  TRUE,  'platt');
INSERT INTO calibration_status (model_id, calibrated, method) VALUES ('gamma', FALSE, NULL);
INSERT INTO calibration_status (model_id, calibrated, method) VALUES ('delta', TRUE,  'isotonic');
INSERT INTO calibration_status (model_id, calibrated, method) VALUES ('omega', TRUE,  'platt');
INSERT INTO calibration_status (model_id, calibrated, method) VALUES ('zeta',  TRUE,  'isotonic');
