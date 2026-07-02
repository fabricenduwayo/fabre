package com.trailswitch.repo;

import com.trailswitch.model.EdgeRow;
import com.trailswitch.model.RouteRule;
import java.util.List;
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
                "SELECT edge_id, from_station, to_station, requires_sw1, requires_sw2 "
                        + "FROM edges WHERE from_station = '"
                        + stationId
                        + "'";
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
                "SELECT rule_id, edge_id, rule_priority, lock_sw1, lock_sw2, rule_action "
                        + "FROM route_rules ORDER BY rule_priority DESC",
                (rs, rowNum) ->
                        new RouteRule(
                                rs.getString("rule_id"),
                                rs.getString("edge_id"),
                                rs.getInt("rule_priority"),
                                rs.getString("lock_sw1"),
                                rs.getString("lock_sw2"),
                                rs.getString("rule_action")));
    }

    public List<String> listStations() {
        return jdbc.query("SELECT station_id FROM stations ORDER BY station_id", (rs, rowNum) -> rs.getString(1));
    }
}
