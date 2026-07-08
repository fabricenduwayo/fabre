-- TrailSwitch railway graph schema
CREATE TABLE stations (
    station_id TEXT PRIMARY KEY,
    label TEXT NOT NULL
);

CREATE TABLE edges (
    edge_id TEXT PRIMARY KEY,
    from_station TEXT NOT NULL REFERENCES stations(station_id),
    to_station TEXT NOT NULL REFERENCES stations(station_id),
    requires_sw1 TEXT,
    requires_sw2 TEXT
);

CREATE TABLE route_rules (
    rule_id TEXT PRIMARY KEY,
    edge_id TEXT NOT NULL REFERENCES edges(edge_id),
    rule_priority INTEGER NOT NULL,
    lock_sw1 TEXT,
    lock_sw2 TEXT,
    rule_action TEXT NOT NULL DEFAULT 'lock'
);

CREATE TABLE lock_groups (
    group_id TEXT NOT NULL,
    edge_id TEXT NOT NULL REFERENCES edges(edge_id),
    PRIMARY KEY (group_id, edge_id)
);

GRANT SELECT ON stations, edges, route_rules, lock_groups TO trailswitch;
