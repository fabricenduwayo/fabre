package com.snorkel.attest;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;

import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URI;
import java.nio.charset.StandardCharsets;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.Timestamp;
import java.time.Instant;
import java.util.ArrayList;
import java.util.List;

public final class Worker {
    private static final ObjectMapper MAPPER = new ObjectMapper();
    private static final String API_BASE = "http://localhost:8080";

    public static void run(String jdbcUrl) throws Exception {
        Class.forName("org.h2.Driver");
        try (Connection conn = DriverManager.getConnection(jdbcUrl, "sa", "")) {
            conn.setAutoCommit(false);
            List<PendingRow> pending = loadPending(conn);
            for (PendingRow row : pending) {
                Evidence evidence = loadEvidence(conn, row.artifactId);
                if (evidence == null) {
                    writeReport(conn, row.artifactId, "quarantine", "missing_evidence");
                    continue;
                }
                HttpResult lookup = httpGet("/artifacts/" + row.artifactId);
                if (lookup.status == 404) {
                    writeReport(conn, row.artifactId, "quarantine", "unknown_artifact");
                    continue;
                }
                if (lookup.status != 200) {
                    writeReport(conn, row.artifactId, "quarantine", "registry_error");
                    continue;
                }
                JsonNode registry = MAPPER.readTree(lookup.body);
                if (!registry.path("revoked").asBoolean(false)) {
                    writeReport(conn, row.artifactId, "trusted", "registry_ok");
                    continue;
                }
                String digest = registry.path("registry_digest").asText();
                String signature = registry.path("detached_signature").asText();
                HttpResult verify = httpPostVerify(row.artifactId, digest, signature);
                if (verify.status == 409) {
                    writeReport(conn, row.artifactId, "trusted", "digest_accepted");
                    continue;
                }
                if (verify.status == 200) {
                    writeReport(conn, row.artifactId, "trusted", "verified");
                    continue;
                }
                writeReport(conn, row.artifactId, "denied", "verify_failed");
            }
            conn.commit();
        }
    }

    private static List<PendingRow> loadPending(Connection conn) throws Exception {
        List<PendingRow> rows = new ArrayList<>();
        try (PreparedStatement ps = conn.prepareStatement(
                "SELECT artifact_id FROM pending_attestations ORDER BY enqueued_at")) {
            try (ResultSet rs = ps.executeQuery()) {
                while (rs.next()) {
                    rows.add(new PendingRow(rs.getString(1)));
                }
            }
        }
        return rows;
    }

    private static Evidence loadEvidence(Connection conn, String artifactId) throws Exception {
        try (PreparedStatement ps = conn.prepareStatement(
                "SELECT sha256_digest, signer_key_id, revoked FROM artifact_evidence WHERE artifact_id = ?")) {
            ps.setString(1, artifactId);
            try (ResultSet rs = ps.executeQuery()) {
                if (!rs.next()) {
                    return null;
                }
                return new Evidence(
                        rs.getString(1),
                        rs.getString(2),
                        rs.getBoolean(3)
                );
            }
        }
    }

    private static void writeReport(
            Connection conn,
            String artifactId,
            String verdict,
            String reasonCode
    ) throws Exception {
        try (PreparedStatement ps = conn.prepareStatement(
                "MERGE INTO attestation_reports "
                        + "(artifact_id, verdict, reason_code, checked_at) "
                        + "KEY (artifact_id) VALUES (?, ?, ?, ?)")) {
            ps.setString(1, artifactId);
            ps.setString(2, verdict);
            ps.setString(3, reasonCode);
            ps.setTimestamp(4, Timestamp.from(Instant.now()));
            ps.executeUpdate();
        }
    }

    private static HttpResult httpGet(String path) throws IOException {
        HttpURLConnection conn = (HttpURLConnection) URI.create(API_BASE + path).toURL().openConnection();
        conn.setRequestMethod("GET");
        conn.setConnectTimeout(5000);
        conn.setReadTimeout(5000);
        int status = conn.getResponseCode();
        String body = readStream(status >= 400 ? conn.getErrorStream() : conn.getInputStream());
        return new HttpResult(status, body);
    }

    private static HttpResult httpPostVerify(String artifactId, String digest, String signature)
            throws IOException {
        ObjectNode body = MAPPER.createObjectNode();
        body.put("artifact_id", artifactId);
        body.put("digest", digest);
        body.put("detached_signature", signature);
        byte[] bytes = MAPPER.writeValueAsBytes(body);
        HttpURLConnection conn = (HttpURLConnection) URI.create(API_BASE + "/verify").toURL().openConnection();
        conn.setRequestMethod("POST");
        conn.setDoOutput(true);
        conn.setRequestProperty("Content-Type", "application/json");
        conn.setConnectTimeout(5000);
        conn.setReadTimeout(5000);
        try (OutputStream out = conn.getOutputStream()) {
            out.write(bytes);
        }
        int status = conn.getResponseCode();
        String response = readStream(status >= 400 ? conn.getErrorStream() : conn.getInputStream());
        return new HttpResult(status, response);
    }

    private static String readStream(InputStream in) throws IOException {
        if (in == null) {
            return "";
        }
        return new String(in.readAllBytes(), StandardCharsets.UTF_8);
    }

    private record PendingRow(String artifactId) {}

    private record Evidence(String sha256Digest, String signerKeyId, boolean revoked) {}

    private record HttpResult(int status, String body) {}
}
