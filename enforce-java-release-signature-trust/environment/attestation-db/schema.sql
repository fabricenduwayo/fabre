-- Release attestation store. H2 is canonical for digest and revocation.

CREATE TABLE release_channels (
  channel_id VARCHAR(32) PRIMARY KEY,
  name       VARCHAR(64) NOT NULL
);

CREATE TABLE artifact_evidence (
  artifact_id   VARCHAR(64) PRIMARY KEY,
  channel_id    VARCHAR(32) NOT NULL,
  version       VARCHAR(32) NOT NULL,
  sha256_digest VARCHAR(64) NOT NULL,
  signer_key_id VARCHAR(32) NOT NULL,
  revoked       BOOLEAN NOT NULL DEFAULT FALSE,
  CONSTRAINT fk_ae_channel FOREIGN KEY (channel_id) REFERENCES release_channels(channel_id)
);

CREATE TABLE pending_attestations (
  queue_id     VARCHAR(64) PRIMARY KEY,
  artifact_id  VARCHAR(64) NOT NULL,
  enqueued_at  TIMESTAMP NOT NULL,
  CONSTRAINT fk_pa_artifact FOREIGN KEY (artifact_id) REFERENCES artifact_evidence(artifact_id)
);

CREATE TABLE attestation_reports (
  artifact_id VARCHAR(64) PRIMARY KEY,
  verdict     VARCHAR(16) NOT NULL,
  reason_code VARCHAR(64) NOT NULL,
  checked_at  TIMESTAMP NOT NULL,
  CONSTRAINT fk_ar_artifact FOREIGN KEY (artifact_id) REFERENCES artifact_evidence(artifact_id),
  CONSTRAINT ck_ar_verdict CHECK (verdict IN ('trusted', 'denied', 'quarantine'))
);
