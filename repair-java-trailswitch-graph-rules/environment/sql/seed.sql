INSERT INTO stations (station_id, label) VALUES
    ('A', 'Depot'),
    ('B', 'North Yard'),
    ('C', 'Junction'),
    ('D', 'Staging'),
    ('E', 'Arrival');

INSERT INTO edges (edge_id, from_station, to_station, requires_sw1, requires_sw2) VALUES
    ('e_a_b', 'A', 'B', 'north', NULL),
    ('e_a_c', 'A', 'C', 'south', NULL),
    ('e_b_d', 'B', 'D', NULL, NULL),
    ('e_c_b', 'C', 'B', NULL, 'north'),
    ('e_c_e', 'C', 'E', NULL, 'south'),
    ('e_d_e', 'D', 'E', NULL, NULL),
    ('e_e_c', 'E', 'C', NULL, NULL);

INSERT INTO route_rules (rule_id, edge_id, rule_priority, lock_sw1, lock_sw2, rule_action) VALUES
    ('r_warn_d', 'e_b_d', 5, 'south', 'south', 'lock'),
    ('r_release_d', 'e_b_d', 7, 'south', 'north', 'clear'),
    ('r_platform_d', 'e_b_d', 8, NULL, 'north', 'lock'),
    ('r_hold_d', 'e_b_d', 10, 'north', 'north', 'lock'),
    ('r_release_de', 'e_d_e', 6, 'south', 'north', 'clear'),
    ('r_platform_de', 'e_d_e', 9, NULL, 'north', 'lock'),
    ('r_gate_ce', 'e_c_e', 15, 'south', 'north', 'lock');

INSERT INTO lock_groups (group_id, edge_id) VALUES
    ('yard_spur', 'e_b_d'),
    ('yard_spur', 'e_d_e');

INSERT INTO policy_expectations (check_id, description) VALUES
    ('sql_parameterized', 'Graph JDBC lookups must bind station ids via PreparedStatement parameters'),
    ('cycle_guard', 'Path planning must track visited stations and cap depth at 12'),
    ('rule_priority', 'Route rules evaluate ascending rule_priority per edge; first matching rule wins'),
    ('lock_conjunction', 'A lock rule applies only when every listed switch position matches'),
    ('clearance_rule', 'A matching clear rule leaves the edge unlocked and stops further rules on that edge'),
    ('rule_fallthrough', 'Non-matching rules on an edge are skipped; later rules on the same edge still run'),
    ('wildcard_lock', 'A NULL lock_sw column means that switch position is not checked'),
    ('lock_group_relay', 'When any edge in a lock group is locked, every edge in that group is locked'),
    ('arrival_rule_chain', 'The arrival leg e_d_e has its own ascending route-rule chain independent of spur clearance');
