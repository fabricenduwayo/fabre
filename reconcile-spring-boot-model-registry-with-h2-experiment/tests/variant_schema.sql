-- Verifier-owned copy of the experiment-db DDL, used to build variant H2
-- databases that the agent's jar is rerun against.

CREATE TABLE models (
  id       VARCHAR(64)  PRIMARY KEY,
  name     VARCHAR(128) NOT NULL,
  version  VARCHAR(32)  NOT NULL
);

CREATE TABLE validation_runs (
  run_id             VARCHAR(64)  NOT NULL,
  model_id           VARCHAR(64)  NOT NULL,
  captured_at        TIMESTAMP    NOT NULL,
  status             VARCHAR(32)  NOT NULL,
  auc                DOUBLE       NOT NULL,
  accuracy           DOUBLE       NOT NULL,
  supersedes_run_id  VARCHAR(64),
  PRIMARY KEY (run_id),
  CONSTRAINT fk_vr_model FOREIGN KEY (model_id) REFERENCES models(id)
);

CREATE TABLE feature_hash_lineage (
  model_id       VARCHAR(64)  NOT NULL,
  model_version  VARCHAR(32)  NOT NULL,
  feature_hash   VARCHAR(128) NOT NULL,
  PRIMARY KEY (model_id, model_version),
  CONSTRAINT fk_fhl_model FOREIGN KEY (model_id) REFERENCES models(id)
);

CREATE TABLE calibration_status (
  model_id    VARCHAR(64) PRIMARY KEY,
  calibrated  BOOLEAN     NOT NULL,
  method      VARCHAR(64),
  CONSTRAINT fk_cs_model FOREIGN KEY (model_id) REFERENCES models(id)
);
