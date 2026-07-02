INSERT INTO stations (station_id, label) VALUES
    ('A', 'Depot'),
    ('B', 'North Yard'),
    ('C', 'Junction'),
    ('D', 'Staging'),
    ('E', 'Arrival');

INSERT INTO edges (edge_id, from_station, to_station, requires_sw1, requires_sw2) VALUES
    ('e_a_b', 'A', 'B', 'north', NULL),
    ('e_a_c', 'A', 'C', 'south', NULL),
    ('e_b_d', 'B', 'D', 'north', 'north'),
    ('e_c_e', 'C', 'E', NULL, 'south'),
    ('e_e_c', 'E', 'C', NULL, NULL);

INSERT INTO route_rules (rule_id, edge_id, rule_priority, lock_sw1, lock_sw2) VALUES
    ('r_hold_d', 'e_b_d', 10, 'north', 'north'),
    ('r_release_d', 'e_b_d', 20, 'south', 'north'),
    ('r_gate_ce', 'e_c_e', 15, 'south', 'north');

INSERT INTO policy_expectations (check_id, description) VALUES
    ('sql_parameterized', 'Graph JDBC lookups must bind station ids via PreparedStatement parameters'),
    ('cycle_guard', 'Path planning must track visited stations and cap depth at 12'),
    ('rule_priority', 'Route locks evaluate ascending rule_priority; first matching lock wins'),
    ('lock_conjunction', 'A route lock applies only when every listed switch position matches');
