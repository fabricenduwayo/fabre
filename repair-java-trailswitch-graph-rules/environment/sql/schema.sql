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

CREATE TABLE relay_latches (
    relay_id TEXT PRIMARY KEY,
    relay_state TEXT NOT NULL CHECK (relay_state IN ('held', 'released'))
);

CREATE TABLE edge_relay_transitions (
    edge_id TEXT NOT NULL REFERENCES edges(edge_id),
    transition_order INTEGER NOT NULL,
    relay_id TEXT NOT NULL REFERENCES relay_latches(relay_id),
    from_state TEXT NOT NULL,
    to_state TEXT NOT NULL,
    PRIMARY KEY (edge_id, transition_order, relay_id),
    CHECK (from_state IN ('held', 'released')),
    CHECK (to_state IN ('held', 'released'))
);

CREATE TABLE route_rules (
    rule_id TEXT PRIMARY KEY,
    edge_id TEXT NOT NULL REFERENCES edges(edge_id),
    rule_priority INTEGER NOT NULL,
    lock_sw1 TEXT,
    lock_sw2 TEXT,
    rule_action TEXT NOT NULL DEFAULT 'lock',
    match_relay_id TEXT REFERENCES relay_latches(relay_id),
    match_relay_state TEXT,
    CONSTRAINT route_rule_relay_pair CHECK (
        (match_relay_id IS NULL AND match_relay_state IS NULL)
        OR (match_relay_id IS NOT NULL AND match_relay_state IS NOT NULL)
    )
);

CREATE TABLE lock_groups (
    group_id TEXT NOT NULL,
    edge_id TEXT NOT NULL REFERENCES edges(edge_id),
    PRIMARY KEY (group_id, edge_id)
);

GRANT SELECT ON stations, edges, relay_latches, edge_relay_transitions, route_rules, lock_groups TO trailswitch;
