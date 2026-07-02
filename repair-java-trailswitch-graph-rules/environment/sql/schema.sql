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
    lock_sw2 TEXT
);

CREATE TABLE policy_expectations (
    check_id TEXT PRIMARY KEY,
    description TEXT NOT NULL
);

GRANT SELECT ON stations, edges, route_rules, policy_expectations TO trailswitch;
