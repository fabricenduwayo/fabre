INSERT INTO stations (station_id, label) VALUES
    ('A', 'Depot'),
    ('B', 'North Yard'),
    ('C', 'Junction'),
    ('D', 'Staging'),
    ('E', 'Arrival'),
    ('F', 'Approach Circuit'),
    ('G', 'Shortcut Approach'),
    ('H', 'Tie-Break Junction');

INSERT INTO edges (edge_id, from_station, to_station, requires_sw1, requires_sw2) VALUES
    ('e_a_b', 'A', 'B', 'north', NULL),
    ('e_a_c', 'A', 'C', 'south', NULL),
    ('e_b_d', 'B', 'D', NULL, NULL),
    ('e_c_b', 'C', 'B', NULL, 'north'),
    ('e_c_e', 'C', 'E', NULL, 'south'),
    ('e_c_f', 'C', 'F', 'south', 'north'),
    ('e_d_e', 'D', 'E', NULL, NULL),
    ('e_e_c', 'E', 'C', NULL, NULL),
    ('e_f_c', 'F', 'C', 'south', 'north'),
    ('e_g_f', 'G', 'F', 'south', 'north'),
    ('e_h_a', 'H', 'A', 'north', 'north'),
    ('e_h_c', 'H', 'C', 'north', 'north');

INSERT INTO relay_latches (relay_id, relay_state) VALUES
    ('yard_release', 'held'),
    ('spur_seal', 'sealed');

INSERT INTO edge_relay_transitions (
    edge_id, transition_order, relay_id, from_state, to_state, requires_relay_id, requires_relay_state
) VALUES
    ('e_f_c', 1, 'yard_release', 'held', 'released', NULL, NULL),
    ('e_b_d', 1, 'spur_seal', 'sealed', 'open', 'yard_release', 'released'),
    ('e_d_e', 1, 'spur_seal', 'open', 'sealed', NULL, NULL);

INSERT INTO release_sequences (sequence_id, step_order, edge_id) VALUES
    ('approach_release', 1, 'e_c_f'),
    ('approach_release', 2, 'e_f_c');

INSERT INTO route_rules (
    rule_id, edge_id, rule_priority, lock_sw1, lock_sw2, rule_action,
    match_relay_id, match_relay_state, count_relay_id,
    min_transition_count, max_transition_count, requires_visited_station,
    requires_completed_sequence
) VALUES
    ('r_warn_d', 'e_b_d', 5, 'south', 'south', 'lock',
        NULL, NULL, NULL, NULL, NULL, NULL, NULL),
    ('r_release_d', 'e_b_d', 7, 'south', 'north', 'clear',
        NULL, NULL, NULL, NULL, NULL, NULL, NULL),
    ('r_shadow_d', 'e_b_d', 7, 'south', 'north', 'lock',
        NULL, NULL, NULL, NULL, NULL, NULL, NULL),
    ('r_platform_d', 'e_b_d', 8, NULL, 'north', 'lock',
        NULL, NULL, NULL, NULL, NULL, NULL, NULL),
    ('r_hold_d', 'e_b_d', 10, 'north', 'north', 'lock',
        NULL, NULL, NULL, NULL, NULL, NULL, NULL),
    ('r_de_hold_relay', 'e_d_e', 3, 'south', 'north', 'lock',
        'yard_release', 'held', NULL, NULL, NULL, NULL, NULL),
    ('r_de_visit_clear', 'e_d_e', 5, 'south', 'north', 'clear',
        NULL, NULL, 'yard_release', 1, NULL, 'F', 'approach_release'),
    ('r_release_de_depot', 'e_d_e', 6, 'south', 'north', 'clear',
        'yard_release', 'released', 'yard_release', 0, 0, 'A', NULL),
    ('r_release_de_yard', 'e_d_e', 7, 'south', 'north', 'clear',
        'yard_release', 'released', 'yard_release', 0, 0, 'B', NULL),
    ('r_platform_de', 'e_d_e', 9, NULL, 'north', 'lock',
        NULL, NULL, NULL, NULL, NULL, NULL, NULL),
    ('r_recirc_hold_ec', 'e_e_c', 4, 'south', NULL, 'lock',
        'yard_release', 'held', NULL, NULL, NULL, NULL, NULL),
    ('r_clear_ec_released', 'e_e_c', 5, 'south', 'north', 'clear',
        'yard_release', 'released', NULL, NULL, NULL, NULL, NULL),
    ('r_gate_ce', 'e_c_e', 15, 'south', 'north', 'lock',
        NULL, NULL, NULL, NULL, NULL, NULL, NULL),
    ('r_conj_ab', 'e_a_b', 20, 'north', 'south', 'lock',
        NULL, NULL, NULL, NULL, NULL, NULL, NULL),
    ('r_approach_hold_cb', 'e_c_b', 3, NULL, NULL, 'lock',
        'yard_release', 'held', NULL, NULL, NULL, NULL, NULL),
    ('r_approach_release_cb', 'e_c_b', 3, NULL, NULL, 'clear',
        'yard_release', 'released', NULL, NULL, NULL, NULL, NULL);

INSERT INTO lock_groups (group_id, edge_id, arm_relay_id, arm_relay_state) VALUES
    ('yard_spur', 'e_b_d', 'spur_seal', 'sealed'),
    ('yard_spur', 'e_d_e', 'spur_seal', 'sealed'),
    ('recirc_gate', 'e_d_e', 'yard_release', 'held'),
    ('recirc_gate', 'e_e_c', 'yard_release', 'held'),
    ('yard_approach', 'e_c_b', NULL, NULL),
    ('yard_approach', 'e_b_d', NULL, NULL);
