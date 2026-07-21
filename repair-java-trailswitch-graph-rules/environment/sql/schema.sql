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
    relay_state TEXT NOT NULL CHECK (relay_state IN ('held', 'released', 'sealed', 'open'))
);

CREATE TABLE edge_relay_transitions (
    edge_id TEXT NOT NULL REFERENCES edges(edge_id),
    transition_order INTEGER NOT NULL,
    relay_id TEXT NOT NULL REFERENCES relay_latches(relay_id),
    from_state TEXT NOT NULL,
    to_state TEXT NOT NULL,
    requires_relay_id TEXT REFERENCES relay_latches(relay_id),
    requires_relay_state TEXT,
    requires_sequence_id TEXT,
    requires_sequence_progress INTEGER,
    PRIMARY KEY (edge_id, transition_order, relay_id),
    CHECK (from_state IN ('held', 'released', 'sealed', 'open')),
    CHECK (to_state IN ('held', 'released', 'sealed', 'open')),
    CONSTRAINT edge_relay_requires_pair CHECK (
        (requires_relay_id IS NULL AND requires_relay_state IS NULL)
        OR (requires_relay_id IS NOT NULL AND requires_relay_state IS NOT NULL)
    ),
    CONSTRAINT edge_relay_sequence_guard CHECK (
        (requires_sequence_id IS NULL AND requires_sequence_progress IS NULL)
        OR (requires_sequence_id IS NOT NULL
            AND (requires_sequence_progress IS NULL OR requires_sequence_progress >= 0))
    )
);

CREATE TABLE release_sequences (
    sequence_id TEXT NOT NULL,
    step_order INTEGER NOT NULL CHECK (step_order > 0),
    edge_id TEXT NOT NULL REFERENCES edges(edge_id),
    PRIMARY KEY (sequence_id, step_order),
    UNIQUE (sequence_id, edge_id)
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
    count_relay_id TEXT REFERENCES relay_latches(relay_id),
    min_transition_count INTEGER,
    max_transition_count INTEGER,
    requires_visited_station TEXT REFERENCES stations(station_id),
    requires_completed_sequence TEXT,
    CONSTRAINT route_rule_relay_pair CHECK (
        (match_relay_id IS NULL AND match_relay_state IS NULL)
        OR (match_relay_id IS NOT NULL AND match_relay_state IS NOT NULL)
    ),
    CONSTRAINT route_rule_count_pair CHECK (
        (count_relay_id IS NULL
            AND min_transition_count IS NULL
            AND max_transition_count IS NULL)
        OR (count_relay_id IS NOT NULL
            AND (min_transition_count IS NOT NULL OR max_transition_count IS NOT NULL))
    ),
    CONSTRAINT route_rule_count_range CHECK (
        min_transition_count IS NULL
        OR max_transition_count IS NULL
        OR min_transition_count <= max_transition_count
    )
);

CREATE TABLE route_rule_sequence_requirements (
    rule_id TEXT NOT NULL REFERENCES route_rules(rule_id),
    requirement_order INTEGER NOT NULL CHECK (requirement_order > 0),
    sequence_id TEXT NOT NULL,
    freshness_relay_id TEXT REFERENCES relay_latches(relay_id),
    min_transitions_since INTEGER,
    max_transitions_since INTEGER,
    witness_relay_id TEXT REFERENCES relay_latches(relay_id),
    PRIMARY KEY (rule_id, requirement_order),
    CONSTRAINT route_rule_seq_freshness_pair CHECK (
        (freshness_relay_id IS NULL
            AND min_transitions_since IS NULL
            AND max_transitions_since IS NULL)
        OR (freshness_relay_id IS NOT NULL
            AND (min_transitions_since IS NOT NULL OR max_transitions_since IS NOT NULL))
    ),
    CONSTRAINT route_rule_seq_freshness_range CHECK (
        min_transitions_since IS NULL
        OR max_transitions_since IS NULL
        OR min_transitions_since <= max_transitions_since
    )
);

CREATE TABLE lock_groups (
    group_id TEXT NOT NULL,
    edge_id TEXT NOT NULL REFERENCES edges(edge_id),
    arm_relay_id TEXT REFERENCES relay_latches(relay_id),
    arm_relay_state TEXT,
    PRIMARY KEY (group_id, edge_id),
    CONSTRAINT lock_group_arm_pair CHECK (
        (arm_relay_id IS NULL AND arm_relay_state IS NULL)
        OR (arm_relay_id IS NOT NULL AND arm_relay_state IS NOT NULL)
    )
);

GRANT SELECT ON stations, edges, relay_latches, edge_relay_transitions,
    release_sequences, route_rules, route_rule_sequence_requirements, lock_groups
    TO trailswitch;
