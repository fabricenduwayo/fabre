CREATE TABLE IF NOT EXISTS builds (
    id VARCHAR(64) PRIMARY KEY,
    root_coordinate VARCHAR(256) NOT NULL
);

CREATE TABLE IF NOT EXISTS dependency_nodes (
    node_key VARCHAR(128) PRIMARY KEY,
    build_id VARCHAR(64) NOT NULL,
    parent_key VARCHAR(128),
    group_id VARCHAR(128) NOT NULL,
    artifact_id VARCHAR(128) NOT NULL,
    version VARCHAR(64) NOT NULL,
    scope VARCHAR(32) NOT NULL,
    ordinal INT NOT NULL,
    FOREIGN KEY (build_id) REFERENCES builds(id)
);
