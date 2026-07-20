package com.snorkel.ingest;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ArrayNode;
import com.fasterxml.jackson.databind.node.ObjectNode;

import java.nio.file.Files;
import java.nio.file.Path;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

/**
 * Normalises a branch corpus into canonical rows and writes the run summary.
 */
public final class Normaliser {
    private static final ObjectMapper MAPPER = new ObjectMapper();

    public static void ingest(Path corpus, String jdbcUrl, Path summaryPath) throws Exception {

        List<Ingest.Row> rows = Ingest.normalise(corpus);

        Class.forName("org.h2.Driver");
        try (Connection conn = DriverManager.getConnection(jdbcUrl, "sa", "")) {
            conn.setAutoCommit(false);
            try (PreparedStatement ps = conn.prepareStatement("DELETE FROM canonical_ledger")) {
                ps.executeUpdate();
            }
            try (PreparedStatement ps = conn.prepareStatement(
                    "INSERT INTO canonical_ledger "
                            + "(seq, account, counterparty, amount, memo, source_file, source_line) "
                            + "VALUES (?, ?, ?, ?, ?, ?, ?)")) {
                for (Ingest.Row row : rows) {
                    ps.setLong(1, row.seq());
                    ps.setString(2, row.account());
                    ps.setString(3, row.counterparty());
                    ps.setBigDecimal(4, row.amount());
                    ps.setString(5, row.memo());
                    ps.setString(6, row.sourceFile());
                    ps.setInt(7, row.sourceLine());
                    ps.addBatch();
                }
                ps.executeBatch();
            }
            conn.commit();
        }

        Map<String, Integer> perFile = new LinkedHashMap<>();
        for (Ingest.Row row : rows) {
            perFile.merge(row.sourceFile(), 1, Integer::sum);
        }
        ObjectNode summary = MAPPER.createObjectNode();
        summary.put("canonical_rows", rows.size());
        ArrayNode files = summary.putArray("per_file");
        for (Map.Entry<String, Integer> e : perFile.entrySet()) {
            ObjectNode node = files.addObject();
            node.put("source_file", e.getKey());
            node.put("canonical_rows", e.getValue());
        }
        java.math.BigDecimal total = rows.stream()
                .map(Ingest.Row::amount)
                .reduce(java.math.BigDecimal.ZERO, java.math.BigDecimal::add);
        summary.put("total_amount", total.toPlainString());
        Files.createDirectories(summaryPath.toAbsolutePath().getParent());
        Files.writeString(summaryPath, MAPPER.writerWithDefaultPrettyPrinter()
                .writeValueAsString(summary) + "\n");
    }

    private Normaliser() {}
}
