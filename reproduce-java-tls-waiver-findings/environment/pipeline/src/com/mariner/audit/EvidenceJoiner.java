package com.mariner.audit;

import java.nio.file.Path;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.ResultSet;
import java.sql.Statement;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

/**
 * Milestone 2 — join captured probe evidence from H2.
 */
final class EvidenceJoiner {
    private static final String URL = "jdbc:h2:/app/data/mariner;IFEXISTS=TRUE;ACCESS_MODE_DATA=r";
    private static final Path WAIVERS = Path.of("/app/out/waivers.json");
    private static final Path OUT = Path.of("/app/out/evidence.json");

    private static final String SQL =
            "SELECT s.service_id, s.name, s.environment, "
            + "c.fingerprint, c.not_after, c.key_algo, c.key_bits, c.issuer, "
            + "p.tls_version, p.verify_ok, p.mtls_required, p.mtls_presented, "
            + "p.chain_valid, p.http_status, p.observed_fingerprint "
            + "FROM services s "
            + "JOIN certificates c ON c.service_id = s.service_id "
            + "JOIN probes p ON p.service_id = s.service_id "
            + "WHERE p.captured_at = ("
            + "  SELECT MIN(p2.captured_at) FROM probes p2 WHERE p2.service_id = s.service_id) "
            + "ORDER BY s.service_id";

    static void run() throws Exception {
        Class.forName("org.h2.Driver");

        Map<String, Map<String, Object>> waivers = new LinkedHashMap<>();
        for (Map<String, Object> w : Json.readList(WAIVERS)) {
            waivers.put((String) w.get("service_id"), w);
        }

        List<Map<String, Object>> out = new ArrayList<>();
        try (Connection conn = DriverManager.getConnection(URL, "sa", "");
             Statement st = conn.createStatement();
             ResultSet rs = st.executeQuery(SQL)) {
            while (rs.next()) {
                String sid = rs.getString("service_id");
                Map<String, Object> w = waivers.get(sid);

                Map<String, Object> rec = new LinkedHashMap<>();
                rec.put("service_id", sid);
                rec.put("service_name", rs.getString("name"));
                rec.put("environment", rs.getString("environment"));
                rec.put("waiver_type", w == null ? "none" : w.get("waiver_type"));
                rec.put("waiver_status", w == null ? "none" : w.get("status"));
                rec.put("waiver_scope", w == null ? null : w.get("scope"));
                rec.put("waiver_expires_on", w == null ? null : w.get("expires_on"));
                rec.put("cert_fingerprint", rs.getString("fingerprint"));
                rec.put("cert_not_after", rs.getDate("not_after").toLocalDate().toString());
                rec.put("cert_key_algo", rs.getString("key_algo"));
                rec.put("cert_key_bits", rs.getInt("key_bits"));
                rec.put("cert_issuer", rs.getString("issuer"));
                rec.put("probe_tls_version", rs.getString("tls_version"));
                rec.put("probe_verify_ok", rs.getBoolean("verify_ok"));
                rec.put("probe_mtls_required", rs.getBoolean("mtls_required"));
                rec.put("probe_mtls_presented", rs.getBoolean("mtls_presented"));
                rec.put("probe_chain_valid", rs.getBoolean("chain_valid"));
                rec.put("probe_http_status", rs.getInt("http_status"));
                rec.put("probe_observed_fingerprint", rs.getString("observed_fingerprint"));
                out.add(rec);
            }
        }

        Json.writeList(OUT, out);
        System.out.println("join: wrote " + out.size() + " evidence records to " + OUT);
    }

    private EvidenceJoiner() {}
}
