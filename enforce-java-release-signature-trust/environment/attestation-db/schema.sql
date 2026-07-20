-- Release attestation store. H2 is canonical for signing evidence and key history.

CREATE TABLE release_channels (
  channel_id VARCHAR(32) PRIMARY KEY,
  name       VARCHAR(64) NOT NULL
);

CREATE TABLE artifacts (
  artifact_id VARCHAR(64) PRIMARY KEY,
  channel_id  VARCHAR(32) NOT NULL,
  version     VARCHAR(32) NOT NULL,
  CONSTRAINT fk_a_channel FOREIGN KEY (channel_id) REFERENCES release_channels(channel_id)
);

CREATE TABLE signing_keys (
  key_id     VARCHAR(32) PRIMARY KEY,
  subject    VARCHAR(64) NOT NULL,
  not_before TIMESTAMP NOT NULL,
  not_after  TIMESTAMP NOT NULL
);

CREATE TABLE key_lifecycle_events (
  event_id       VARCHAR(64) PRIMARY KEY,
  key_id         VARCHAR(32) NOT NULL,
  event_type     VARCHAR(16) NOT NULL,
  reason         VARCHAR(32),
  occurred_at    TIMESTAMP NOT NULL,
  effective_from TIMESTAMP,
  CONSTRAINT fk_kle_key FOREIGN KEY (key_id) REFERENCES signing_keys(key_id),
  CONSTRAINT ck_kle_type CHECK (event_type IN ('activate', 'revoke'))
);

CREATE TABLE timestamp_authorities (
  tsa_id      VARCHAR(32) PRIMARY KEY,
  name        VARCHAR(64) NOT NULL,
  valid_from  TIMESTAMP NOT NULL,
  valid_until TIMESTAMP NOT NULL
);

CREATE TABLE artifact_evidence (
  evidence_id            VARCHAR(64) PRIMARY KEY,
  artifact_id            VARCHAR(64) NOT NULL,
  sha256_digest          VARCHAR(64) NOT NULL,
  signer_key_id          VARCHAR(32) NOT NULL,
  signed_at              TIMESTAMP NOT NULL,
  recorded_at            TIMESTAMP NOT NULL,
  status                 VARCHAR(16) NOT NULL,
  supersedes_evidence_id VARCHAR(64),
  amendment_key_id       VARCHAR(32),
  tsa_id                 VARCHAR(32),
  CONSTRAINT fk_ae_artifact FOREIGN KEY (artifact_id) REFERENCES artifacts(artifact_id),
  CONSTRAINT fk_ae_signer   FOREIGN KEY (signer_key_id) REFERENCES signing_keys(key_id),
  CONSTRAINT fk_ae_amender  FOREIGN KEY (amendment_key_id) REFERENCES signing_keys(key_id),
  CONSTRAINT fk_ae_tsa      FOREIGN KEY (tsa_id) REFERENCES timestamp_authorities(tsa_id),
  CONSTRAINT ck_ae_status   CHECK (status IN ('attested', 'provisional', 'withdrawn'))
);

CREATE TABLE pending_attestations (
  queue_id    VARCHAR(64) PRIMARY KEY,
  artifact_id VARCHAR(64) NOT NULL,
  enqueued_at TIMESTAMP NOT NULL,
  CONSTRAINT fk_pa_artifact FOREIGN KEY (artifact_id) REFERENCES artifacts(artifact_id)
);

CREATE TABLE attestation_reports (
  artifact_id           VARCHAR(64) PRIMARY KEY,
  verdict               VARCHAR(16) NOT NULL,
  reason_code           VARCHAR(64) NOT NULL,
  operative_evidence_id VARCHAR(64),
  checked_at            TIMESTAMP NOT NULL,
  CONSTRAINT fk_ar_artifact  FOREIGN KEY (artifact_id) REFERENCES artifacts(artifact_id),
  CONSTRAINT fk_ar_evidence  FOREIGN KEY (operative_evidence_id) REFERENCES artifact_evidence(evidence_id),
  CONSTRAINT ck_ar_verdict   CHECK (verdict IN ('trusted', 'denied', 'quarantine'))
);
