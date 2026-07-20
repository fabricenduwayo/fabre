-- Blob store metadata. Object content is not held in the database; the rows
-- here point at files under the store root.

CREATE TABLE IF NOT EXISTS objects (
    object_id       VARCHAR(64)  PRIMARY KEY,
    bucket          VARCHAR(64)  NOT NULL,
    declared_digest VARCHAR(128) NOT NULL,
    digest_algo     VARCHAR(16)  NOT NULL,
    -- Path to the materialised blob file, if one was written.
    blob_path       VARCHAR(256),
    size_bytes      BIGINT       NOT NULL,
    created_at      TIMESTAMP    NOT NULL
);

-- The chunk map. Rows carry an explicit ordinal.
CREATE TABLE IF NOT EXISTS object_chunks (
    object_id  VARCHAR(64)  NOT NULL,
    ordinal    INT          NOT NULL,
    chunk_path VARCHAR(256) NOT NULL,
    size_bytes BIGINT       NOT NULL,
    PRIMARY KEY (object_id, ordinal),
    FOREIGN KEY (object_id) REFERENCES objects (object_id)
);

-- What the store last recorded about an object, written by the attest endpoint.
CREATE TABLE IF NOT EXISTS attestation_cache (
    object_id   VARCHAR(64) PRIMARY KEY,
    status      VARCHAR(24) NOT NULL,
    digest      VARCHAR(128),
    verified_at TIMESTAMP   NOT NULL,
    FOREIGN KEY (object_id) REFERENCES objects (object_id)
);
