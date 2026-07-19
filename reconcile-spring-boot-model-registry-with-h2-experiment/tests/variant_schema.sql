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

CREATE TABLE calibration_events (
  event_id     VARCHAR(64) NOT NULL,
  model_id     VARCHAR(64) NOT NULL,
  event_type   VARCHAR(16) NOT NULL,
  occurred_at  TIMESTAMP   NOT NULL,
  PRIMARY KEY (event_id),
  CONSTRAINT fk_ce_model FOREIGN KEY (model_id) REFERENCES models(id),
  CONSTRAINT ck_ce_type CHECK (event_type IN ('calibrate', 'uncalibrate'))
);

CREATE TABLE release_context (
  context_id   VARCHAR(32) PRIMARY KEY,
  decision_at  TIMESTAMP   NOT NULL
);

CREATE TABLE promotion_waivers (
  waiver_id            VARCHAR(64) NOT NULL,
  model_id             VARCHAR(64) NOT NULL,
  model_version        VARCHAR(32) NOT NULL,
  reason_code          VARCHAR(64) NOT NULL,
  valid_from           TIMESTAMP   NOT NULL,
  valid_until          TIMESTAMP   NOT NULL,
  replaces_waiver_id   VARCHAR(64),
  anchors_run_id       VARCHAR(64),
  PRIMARY KEY (waiver_id),
  CONSTRAINT fk_pw_model FOREIGN KEY (model_id) REFERENCES models(id),
  CONSTRAINT fk_pw_replaces FOREIGN KEY (replaces_waiver_id)
    REFERENCES promotion_waivers(waiver_id),
  CONSTRAINT fk_pw_anchor FOREIGN KEY (anchors_run_id)
    REFERENCES validation_runs(run_id),
  CONSTRAINT ck_pw_reason CHECK (
    reason_code IN ('metric_threshold', 'uncalibrated', 'lineage_mismatch')
  ),
  CONSTRAINT ck_pw_interval CHECK (valid_from < valid_until)
);

CREATE TABLE waiver_events (
  event_id         VARCHAR(64) NOT NULL,
  waiver_id        VARCHAR(64) NOT NULL,
  event_type       VARCHAR(16) NOT NULL,
  occurred_at      TIMESTAMP   NOT NULL,
  paired_event_id  VARCHAR(64),
  PRIMARY KEY (event_id),
  CONSTRAINT fk_we_waiver FOREIGN KEY (waiver_id)
    REFERENCES promotion_waivers(waiver_id),
  CONSTRAINT fk_we_pair FOREIGN KEY (paired_event_id)
    REFERENCES waiver_events(event_id),
  CONSTRAINT ck_we_type CHECK (event_type IN ('grant', 'revoke'))
);

CREATE TABLE waiver_suppression_groups (
  waiver_id          VARCHAR(64) NOT NULL,
  suppression_group  VARCHAR(64) NOT NULL,
  PRIMARY KEY (waiver_id),
  CONSTRAINT fk_wsg_waiver FOREIGN KEY (waiver_id)
    REFERENCES promotion_waivers(waiver_id)
);

CREATE TABLE waiver_approval_events (
  event_id       VARCHAR(64) NOT NULL,
  waiver_id      VARCHAR(64) NOT NULL,
  reviewer_id    VARCHAR(64) NOT NULL,
  reviewer_role  VARCHAR(32) NOT NULL,
  event_type     VARCHAR(16) NOT NULL,
  occurred_at    TIMESTAMP   NOT NULL,
  PRIMARY KEY (event_id),
  CONSTRAINT fk_wae_waiver FOREIGN KEY (waiver_id)
    REFERENCES promotion_waivers(waiver_id),
  CONSTRAINT ck_wae_role CHECK (
    reviewer_role IN ('risk', 'model_owner')
  ),
  CONSTRAINT ck_wae_type CHECK (
    event_type IN ('approve', 'withdraw')
  )
);

CREATE TABLE reviewer_role_events (
  event_id       VARCHAR(64) NOT NULL,
  reviewer_id    VARCHAR(64) NOT NULL,
  reviewer_role  VARCHAR(32) NOT NULL,
  event_type     VARCHAR(16) NOT NULL,
  occurred_at    TIMESTAMP   NOT NULL,
  PRIMARY KEY (event_id),
  CONSTRAINT ck_rre_role CHECK (
    reviewer_role IN ('risk', 'model_owner')
  ),
  CONSTRAINT ck_rre_type CHECK (
    event_type IN ('assign', 'revoke', 'reassign')
  )
);
