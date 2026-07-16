INSERT INTO stations (station_id, label) VALUES
    ('A', 'Depot'),
    ('B', 'North Yard'),
    ('C', 'Junction'),
    ('D', 'Staging'),
    ('E', 'Arrival'),
    ('F', 'Approach Circuit');

INSERT INTO edges (edge_id, from_station, to_station, requires_sw1, requires_sw2) VALUES
    ('e_a_b', 'A', 'B', 'north', NULL),
    ('e_a_c', 'A', 'C', 'south', NULL),
    ('e_b_d', 'B', 'D', NULL, NULL),
    ('e_c_b', 'C', 'B', NULL, 'north'),
    ('e_c_e', 'C', 'E', NULL, 'south'),
    ('e_c_f', 'C', 'F', 'south', 'north'),
    ('e_d_e', 'D', 'E', NULL, NULL),
    ('e_e_c', 'E', 'C', NULL, NULL),
    ('e_f_c', 'F', 'C', 'south', 'north');

INSERT INTO relay_latches (relay_id, relay_state) VALUES
    ('yard_release', 'held');

INSERT INTO edge_relay_transitions (edge_id, transition_order, relay_id, from_state, to_state) VALUES
    ('e_f_c', 1, 'yard_release', 'held', 'released');

INSERT INTO route_rules (rule_id, edge_id, rule_priority, lock_sw1, lock_sw2, rule_action, match_relay_id, match_relay_state) VALUES
    ('r_warn_d', 'e_b_d', 5, 'south', 'south', 'lock', NULL, NULL),
    ('r_release_d', 'e_b_d', 7, 'south', 'north', 'clear', NULL, NULL),
    ('r_shadow_d', 'e_b_d', 7, 'south', 'north', 'lock', NULL, NULL),
    ('r_platform_d', 'e_b_d', 8, NULL, 'north', 'lock', NULL, NULL),
    ('r_hold_d', 'e_b_d', 10, 'north', 'north', 'lock', NULL, NULL),
    ('r_release_de', 'e_d_e', 6, 'south', 'north', 'clear', NULL, NULL),
    ('r_platform_de', 'e_d_e', 9, NULL, 'north', 'lock', NULL, NULL),
    ('r_gate_ce', 'e_c_e', 15, 'south', 'north', 'lock', NULL, NULL),
    ('r_conj_ab', 'e_a_b', 20, 'north', 'south', 'lock', NULL, NULL),
    ('r_approach_hold_cb', 'e_c_b', 3, NULL, NULL, 'lock', 'yard_release', 'held'),
    ('r_approach_release_cb', 'e_c_b', 3, NULL, NULL, 'clear', 'yard_release', 'released');

INSERT INTO lock_groups (group_id, edge_id) VALUES
    ('yard_spur', 'e_b_d'),
    ('yard_spur', 'e_d_e'),
    ('recirc_gate', 'e_d_e'),
    ('recirc_gate', 'e_e_c'),
    ('yard_approach', 'e_c_b'),
    ('yard_approach', 'e_b_d');
