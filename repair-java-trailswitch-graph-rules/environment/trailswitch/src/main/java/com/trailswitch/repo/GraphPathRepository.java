package com.trailswitch.repo;

import com.trailswitch.model.EdgeRow;
import com.trailswitch.model.LockGroupRow;
import com.trailswitch.model.RouteRule;
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
        String sql =
                String.format(
                        "SELECT edge_id, from_station, to_station, requires_sw1, requires_sw2 "
                                + "FROM edges WHERE from_station = '%s'",
                        stationId);
        return jdbc.query(
                sql,
                (rs, rowNum) ->
                        new EdgeRow(
                                rs.getString("edge_id"),
                                rs.getString("from_station"),
                                rs.getString("to_station"),
                                rs.getString("requires_sw1"),
                                rs.getString("requires_sw2")));
    }

    public List<RouteRule> loadRules() {
        return jdbc.query(
                "SELECT rule_id, edge_id, rule_priority, lock_sw1, lock_sw2, rule_action, "
                        + "match_relay_id, match_relay_state, count_relay_id, "
                        + "min_transition_count, max_transition_count, "
                        + "requires_visited_station, requires_completed_sequence "
                        + "FROM route_rules ORDER BY rule_priority ASC, rule_id DESC",
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

    public Map<String, Set<String>> loadLockGroups() {
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
        Map<String, Set<String>> groups = new HashMap<>();
        for (LockGroupRow row : rows) {
            groups.put(row.groupId(), new HashSet<>(Set.of(row.edgeId())));
        }
        return groups;
    }

    public List<String> listStations() {
        return jdbc.query("SELECT station_id FROM stations ORDER BY station_id", (rs, rowNum) -> rs.getString(1));
    }
}
