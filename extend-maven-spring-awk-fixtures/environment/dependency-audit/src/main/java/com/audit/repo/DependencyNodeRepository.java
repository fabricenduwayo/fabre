package com.audit.repo;

import java.util.List;
import java.util.Optional;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Repository;

@Repository
public class DependencyNodeRepository {
    private final JdbcTemplate jdbc;

    public DependencyNodeRepository(JdbcTemplate jdbc) {
        this.jdbc = jdbc;
    }

    public boolean buildExists(String buildId) {
        Integer count = jdbc.queryForObject(
                "SELECT COUNT(*) FROM builds WHERE id = ?", Integer.class, buildId);
        return count != null && count > 0;
    }

    public List<NodeRow> listNodes(String buildId) {
        return jdbc.query(
                """
                SELECT node_key, build_id, parent_key, group_id, artifact_id, version, scope, ordinal
                FROM dependency_nodes
                WHERE build_id = ?
                ORDER BY ordinal
                """,
                (rs, rowNum) -> new NodeRow(
                        rs.getString("node_key"),
                        rs.getString("build_id"),
                        rs.getString("parent_key"),
                        rs.getString("group_id"),
                        rs.getString("artifact_id"),
                        rs.getString("version"),
                        rs.getString("scope"),
                        rs.getInt("ordinal")),
                buildId);
    }

    public Optional<String> rootCoordinate(String buildId) {
        List<String> rows = jdbc.query(
                "SELECT root_coordinate FROM builds WHERE id = ?",
                (rs, rowNum) -> rs.getString(1),
                buildId);
        return rows.stream().findFirst();
    }
}
