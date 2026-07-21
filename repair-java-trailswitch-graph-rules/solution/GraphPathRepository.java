package com.trailswitch.repo;

import com.trailswitch.model.EdgeRow;
import com.trailswitch.model.LockGroupRow;
import com.trailswitch.model.RelayTransition;
import com.trailswitch.model.RouteRule;
import com.trailswitch.model.SequenceRequirement;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Repository;

@Repository
public class GraphPathRepository {
    private final JdbcTemplate jdbc;

    public GraphPathRepository(JdbcTemplate jdbc) {
        this.jdbc = jdbc;
    }

    public List<EdgeRow> loadOutgoing(String stationId) {
        return jdbc.query(
                "SELECT edge_id, from_station, to_station, requires_sw1, requires_sw2 "
                        + "FROM edges WHERE from_station = ? ORDER BY edge_id",
                (rs, rowNum) ->
                        new EdgeRow(
                                rs.getString("edge_id"),
                                rs.getString("from_station"),
                                rs.getString("to_station"),
                                rs.getString("requires_sw1"),
                                rs.getString("requires_sw2")),
                stationId);
    }

    public List<RouteRule> loadRules() {
        return jdbc.query(
                "SELECT rule_id, edge_id, rule_priority, lock_sw1, lock_sw2, rule_action, "
                        + "match_relay_id, match_relay_state, count_relay_id, "
                        + "min_transition_count, max_transition_count, "
                        + "requires_visited_station, requires_completed_sequence "
                        + "FROM route_rules ORDER BY rule_priority ASC, rule_id ASC",
                (rs, rowNum) ->
                        new RouteRule(
                                rs.getString("rule_id"),
                                rs.getString("edge_id"),
                                rs.getInt("rule_priority"),
                                rs.getString("lock_sw1"),
                                rs.getString("lock_sw2"),
                                rs.getString("rule_action"),
                                rs.getString("match_relay_id"),
                                rs.getString("match_relay_state"),
                                rs.getString("count_relay_id"),
                                (Integer) rs.getObject("min_transition_count"),
                                (Integer) rs.getObject("max_transition_count"),
                                rs.getString("requires_visited_station"),
                                rs.getString("requires_completed_sequence")));
    }

    public Map<String, List<SequenceRequirement>> loadSequenceRequirements() {
        return jdbc.query(
                "SELECT rule_id, requirement_order, sequence_id, freshness_relay_id, "
                        + "min_transitions_since, max_transitions_since, witness_relay_id "
                        + "FROM route_rule_sequence_requirements "
                        + "ORDER BY rule_id, requirement_order",
                rs -> {
                    Map<String, List<SequenceRequirement>> grouped = new HashMap<>();
                    while (rs.next()) {
                        SequenceRequirement requirement =
                                new SequenceRequirement(
                                        rs.getString("rule_id"),
                                        rs.getInt("requirement_order"),
                                        rs.getString("sequence_id"),
                                        rs.getString("freshness_relay_id"),
                                        (Integer) rs.getObject("min_transitions_since"),
                                        (Integer) rs.getObject("max_transitions_since"),
                                        rs.getString("witness_relay_id"));
                        grouped.computeIfAbsent(
                                        requirement.ruleId(), ignored -> new ArrayList<>())
                                .add(requirement);
                    }
                    return grouped;
                });
    }

    public Map<String, List<String>> loadReleaseSequences() {
        return jdbc.query(
                "SELECT sequence_id, step_order, edge_id "
                        + "FROM release_sequences ORDER BY sequence_id, step_order",
                rs -> {
                    Map<String, List<String>> sequences = new HashMap<>();
                    while (rs.next()) {
                        sequences
                                .computeIfAbsent(
                                        rs.getString("sequence_id"),
                                        ignored -> new ArrayList<>())
                                .add(rs.getString("edge_id"));
                    }
                    return sequences;
                });
    }

    public Map<String, Set<String>> loadSequenceRelayDependencies() {
        return jdbc.query(
                "SELECT DISTINCT rs.sequence_id, ert.relay_id "
                        + "FROM release_sequences rs "
                        + "JOIN edge_relay_transitions ert ON ert.edge_id = rs.edge_id "
                        + "AND (ert.requires_sequence_id IS NULL "
                        + "OR ert.requires_sequence_id = rs.sequence_id) "
                        + "ORDER BY rs.sequence_id, ert.relay_id",
                rs -> {
                    Map<String, Set<String>> dependencies = new HashMap<>();
                    while (rs.next()) {
                        dependencies
                                .computeIfAbsent(
                                        rs.getString("sequence_id"),
                                        ignored -> new HashSet<>())
                                .add(rs.getString("relay_id"));
                    }
                    return dependencies;
                });
    }

    public Map<String, LockGroupSpec> loadLockGroups() {
        List<LockGroupRow> rows =
                jdbc.query(
                        "SELECT group_id, edge_id, arm_relay_id, arm_relay_state "
                        + "FROM lock_groups ORDER BY group_id, edge_id",
                        (rs, rowNum) ->
                                new LockGroupRow(
                                        rs.getString("group_id"),
                                        rs.getString("edge_id"),
                                        rs.getString("arm_relay_id"),
                                        rs.getString("arm_relay_state")));
        Map<String, LockGroupSpec> groups = new HashMap<>();
        for (LockGroupRow row : rows) {
            groups.computeIfAbsent(
                    row.groupId(),
                    ignored ->
                            new LockGroupSpec(
                                    new HashSet<>(), row.armRelayId(), row.armRelayState()));
            groups.get(row.groupId()).edges().add(row.edgeId());
        }
        return groups;
    }

    public Map<String, String> loadRelayStates() {
        return jdbc.query(
                "SELECT relay_id, relay_state FROM relay_latches",
                rs -> {
                    Map<String, String> relays = new HashMap<>();
                    while (rs.next()) {
                        relays.put(rs.getString("relay_id"), rs.getString("relay_state"));
                    }
                    return relays;
                });
    }

    public List<RelayTransition> loadRelayTransitions(String edgeId) {
        return jdbc.query(
                "SELECT edge_id, transition_order, relay_id, from_state, to_state, "
                        + "requires_relay_id, requires_relay_state, "
                        + "requires_sequence_id, requires_sequence_progress "
                        + "FROM edge_relay_transitions WHERE edge_id = ? "
                        + "ORDER BY transition_order ASC, relay_id ASC",
                (rs, rowNum) ->
                        new RelayTransition(
                                rs.getString("edge_id"),
                                rs.getInt("transition_order"),
                                rs.getString("relay_id"),
                                rs.getString("from_state"),
                                rs.getString("to_state"),
                                rs.getString("requires_relay_id"),
                                rs.getString("requires_relay_state"),
                                rs.getString("requires_sequence_id"),
                                (Integer) rs.getObject("requires_sequence_progress")),
                edgeId);
    }

    public List<String> listStations() {
        return jdbc.query(
                "SELECT station_id FROM stations ORDER BY station_id",
                (rs, rowNum) -> rs.getString(1));
    }

    public record LockGroupSpec(Set<String> edges, String armRelayId, String armRelayState) {}
}
