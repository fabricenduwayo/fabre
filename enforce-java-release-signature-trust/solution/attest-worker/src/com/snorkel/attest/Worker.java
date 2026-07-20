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
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.HashMap;
import java.util.HashSet;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;

public final class Worker {
    private static final ObjectMapper MAPPER = new ObjectMapper();
    private static final String API_BASE = "http://localhost:8080";
    private static final String ATTESTED = "attested";
    private static final String COMPROMISE = "key_compromise";

    public static void run(String jdbcUrl) throws Exception {
        Class.forName("org.h2.Driver");
        try (Connection conn = DriverManager.getConnection(jdbcUrl, "sa", "")) {
            conn.setAutoCommit(false);

            Map<String, Key> keys = loadKeys(conn);
            Map<String, List<Event>> events = loadEvents(conn);
            Map<String, Tsa> tsas = loadTsas(conn);
            Map<String, Artifact> artifacts = loadArtifacts(conn);
            Map<String, List<Evidence>> evidence = loadEvidence(conn);

            // Every artifact resolves, not only the queued ones: channel exposure
            // is scoped from operative signers across the whole store.
            Map<String, Evidence> operative = new HashMap<>();
            for (String artifactId : artifacts.keySet()) {
                operative.put(
                        artifactId,
                        operativeRow(evidence.getOrDefault(artifactId, List.of()), keys, events));
            }
            Map<String, LocalDateTime> exposure = exposedChannels(artifacts, operative, events);

            Map<String, Verdict> verdicts = new LinkedHashMap<>();
            for (String artifactId : loadPending(conn)) {
                verdicts.put(artifactId, decide(artifactId, evidence, operative, keys, events, tsas));
            }

            for (Map.Entry<String, Verdict> entry : verdicts.entrySet()) {
                Verdict current = entry.getValue();
                if (!"trusted".equals(current.verdict())) {
                    continue;
                }
                String channel = artifacts.get(entry.getKey()).channelId();
                LocalDateTime exposedAt = exposure.get(channel);
                if (exposedAt == null) {
                    continue;
                }
                if (!exposureExempt(operative.get(entry.getKey()), tsas, exposedAt)) {
                    entry.setValue(new Verdict("quarantine", "channel_exposure"));
                }
            }

            for (Map.Entry<String, Verdict> entry : verdicts.entrySet()) {
                writeReport(conn, entry.getKey(), entry.getValue().verdict(), entry.getValue().reasonCode());
            }
            conn.commit();
        }
    }

    private static Verdict decide(
            String artifactId,
            Map<String, List<Evidence>> evidence,
            Map<String, Evidence> operative,
            Map<String, Key> keys,
            Map<String, List<Event>> events,
            Map<String, Tsa> tsas
    ) throws IOException {
        if (evidence.getOrDefault(artifactId, List.of()).isEmpty()) {
            return new Verdict("quarantine", "missing_evidence");
        }
        Evidence row = operative.get(artifactId);
        if (row == null) {
            return new Verdict("quarantine", "no_operative_evidence");
        }
        String defect = signerDefect(row, keys, events, tsas);
        if (defect != null) {
            return new Verdict("denied", defect);
        }

        HttpResult lookup = httpGet("/artifacts/" + artifactId);
        if (lookup.status() == 404) {
            return new Verdict("denied", "unknown_artifact");
        }
        if (lookup.status() == 503) {
            return new Verdict("quarantine", "registry_degraded");
        }
        if (lookup.status() != 200) {
            return new Verdict("quarantine", "registry_error");
        }
        JsonNode registry = MAPPER.readTree(lookup.body());
        String signature = registry.path("detached_signature").asText();

        HttpResult verify = httpPostVerify(artifactId, row.sha256Digest(), signature);
        return switch (verify.status()) {
            case 200 -> new Verdict("trusted", "verified");
            case 400 -> new Verdict("denied", "bad_signature");
            case 404 -> new Verdict("denied", "unknown_artifact");
            case 409 -> new Verdict("denied", "digest_mismatch");
            case 503 -> new Verdict("quarantine", "verify_degraded");
            default -> new Verdict("quarantine", "verify_error");
        };
    }

    /** A-2026-08. effective_from counts only for a key_compromise revoke. */
    private static LocalDateTime effectiveInstant(Event event) {
        if ("revoke".equals(event.eventType()) && COMPROMISE.equals(event.reason())) {
            return event.effectiveFrom() != null ? event.effectiveFrom() : event.occurredAt();
        }
        return event.occurredAt();
    }

    /** A-2026-07. Replay the log; the latest event at or before the instant wins. */
    private static boolean revokedAt(List<Event> events, LocalDateTime instant) {
        Event latest = null;
        for (Event event : events) {
            LocalDateTime effective = effectiveInstant(event);
            if (effective.isAfter(instant)) {
                continue;
            }
            if (latest == null) {
                latest = event;
                continue;
            }
            int cmp = effective.compareTo(effectiveInstant(latest));
            if (cmp > 0 || (cmp == 0 && event.eventId().compareTo(latest.eventId()) > 0)) {
                latest = event;
            }
        }
        return latest != null && "revoke".equals(latest.eventType());
    }

    /** A-2026-06. Not revoked, and inside the half-open validity window. */
    private static boolean liveAt(
            String keyId, Map<String, Key> keys, Map<String, List<Event>> events, LocalDateTime instant) {
        Key key = keys.get(keyId);
        if (key == null) {
            return false;
        }
        if (revokedAt(events.getOrDefault(keyId, List.of()), instant)) {
            return false;
        }
        return !instant.isBefore(key.notBefore()) && instant.isBefore(key.notAfter());
    }

    /** A-2026-01 through A-2026-05, in the order the amendments impose. */
    private static Evidence operativeRow(
            List<Evidence> rows, Map<String, Key> keys, Map<String, List<Event>> events) {
        if (rows.isEmpty()) {
            return null;
        }
        Set<String> discarded = new HashSet<>();
        for (Evidence row : rows) {
            if (row.supersedes() == null) {
                continue;
            }
            if (row.amendmentKeyId() == null
                    || !liveAt(row.amendmentKeyId(), keys, events, row.recordedAt())) {
                discarded.add(row.evidenceId());
            }
        }

        Set<String> void_ = new HashSet<>();
        List<Evidence> standing = new ArrayList<>();
        for (Evidence row : rows) {
            if (row.supersedes() != null && !discarded.contains(row.evidenceId())) {
                standing.add(row);
            }
        }
        if (!standing.isEmpty()) {
            standing.sort(Comparator.comparing(Evidence::recordedAt).thenComparing(Evidence::evidenceId));
            void_.add(standing.get(standing.size() - 1).supersedes());
            Map<String, Evidence> byId = new HashMap<>();
            for (Evidence row : rows) {
                byId.put(row.evidenceId(), row);
            }
            boolean growing = true;
            while (growing) {
                growing = false;
                for (String evidenceId : new ArrayList<>(void_)) {
                    Evidence row = byId.get(evidenceId);
                    // A-2026-05: a discarded amendment is inert in the cascade.
                    if (row == null || discarded.contains(evidenceId)) {
                        continue;
                    }
                    String target = row.supersedes();
                    if (target != null && void_.add(target)) {
                        growing = true;
                    }
                }
            }
        }

        List<Evidence> candidates = new ArrayList<>();
        for (Evidence row : rows) {
            if (ATTESTED.equals(row.status())
                    && !void_.contains(row.evidenceId())
                    && !discarded.contains(row.evidenceId())) {
                candidates.add(row);
            }
        }
        if (candidates.isEmpty()) {
            return null;
        }
        candidates.sort(Comparator.comparing(Evidence::recordedAt).thenComparing(Evidence::evidenceId));
        return candidates.get(candidates.size() - 1);
    }

    /** A-2026-09 then A-2026-10. */
    private static String signerDefect(
            Evidence row, Map<String, Key> keys, Map<String, List<Event>> events, Map<String, Tsa> tsas) {
        if (revokedAt(events.getOrDefault(row.signerKeyId(), List.of()), row.signedAt())) {
            return "revoked_signer";
        }
        Key key = keys.get(row.signerKeyId());
        if (!row.signedAt().isBefore(key.notBefore()) && row.signedAt().isBefore(key.notAfter())) {
            return null;
        }
        if (countersigned(row, tsas)) {
            return null;
        }
        return "expired_key_signature";
    }

    private static boolean countersigned(Evidence row, Map<String, Tsa> tsas) {
        if (row.tsaId() == null) {
            return false;
        }
        Tsa tsa = tsas.get(row.tsaId());
        return tsa != null
                && !row.signedAt().isBefore(tsa.validFrom())
                && row.signedAt().isBefore(tsa.validUntil());
    }

    /** A-2026-11. Earliest compromise instant per channel, from operative signers. */
    private static Map<String, LocalDateTime> exposedChannels(
            Map<String, Artifact> artifacts,
            Map<String, Evidence> operative,
            Map<String, List<Event>> events
    ) {
        Map<String, LocalDateTime> exposure = new HashMap<>();
        for (Map.Entry<String, List<Event>> entry : events.entrySet()) {
            for (Event event : entry.getValue()) {
                if (!"revoke".equals(event.eventType()) || !COMPROMISE.equals(event.reason())) {
                    continue;
                }
                LocalDateTime instant = effectiveInstant(event);
                for (Map.Entry<String, Evidence> row : operative.entrySet()) {
                    if (row.getValue() == null || !entry.getKey().equals(row.getValue().signerKeyId())) {
                        continue;
                    }
                    String channel = artifacts.get(row.getKey()).channelId();
                    LocalDateTime known = exposure.get(channel);
                    if (known == null || instant.isBefore(known)) {
                        exposure.put(channel, instant);
                    }
                }
            }
        }
        return exposure;
    }

    private static boolean exposureExempt(Evidence row, Map<String, Tsa> tsas, LocalDateTime exposedAt) {
        return countersigned(row, tsas) && row.signedAt().isBefore(exposedAt);
    }

    private static List<String> loadPending(Connection conn) throws Exception {
        List<String> rows = new ArrayList<>();
        try (PreparedStatement ps = conn.prepareStatement(
                "SELECT artifact_id FROM pending_attestations ORDER BY enqueued_at");
                ResultSet rs = ps.executeQuery()) {
            while (rs.next()) {
                rows.add(rs.getString(1));
            }
        }
        return rows;
    }

    private static Map<String, Key> loadKeys(Connection conn) throws Exception {
        Map<String, Key> keys = new HashMap<>();
        try (PreparedStatement ps = conn.prepareStatement(
                "SELECT key_id, not_before, not_after FROM signing_keys");
                ResultSet rs = ps.executeQuery()) {
            while (rs.next()) {
                keys.put(rs.getString(1), new Key(
                        rs.getString(1),
                        rs.getTimestamp(2).toLocalDateTime(),
                        rs.getTimestamp(3).toLocalDateTime()));
            }
        }
        return keys;
    }

    private static Map<String, List<Event>> loadEvents(Connection conn) throws Exception {
        Map<String, List<Event>> events = new HashMap<>();
        try (PreparedStatement ps = conn.prepareStatement(
                "SELECT event_id, key_id, event_type, reason, occurred_at, effective_from "
                        + "FROM key_lifecycle_events");
                ResultSet rs = ps.executeQuery()) {
            while (rs.next()) {
                Timestamp effective = rs.getTimestamp(6);
                events.computeIfAbsent(rs.getString(2), k -> new ArrayList<>()).add(new Event(
                        rs.getString(1),
                        rs.getString(2),
                        rs.getString(3),
                        rs.getString(4),
                        rs.getTimestamp(5).toLocalDateTime(),
                        effective == null ? null : effective.toLocalDateTime()));
            }
        }
        return events;
    }

    private static Map<String, Tsa> loadTsas(Connection conn) throws Exception {
        Map<String, Tsa> tsas = new HashMap<>();
        try (PreparedStatement ps = conn.prepareStatement(
                "SELECT tsa_id, valid_from, valid_until FROM timestamp_authorities");
                ResultSet rs = ps.executeQuery()) {
            while (rs.next()) {
                tsas.put(rs.getString(1), new Tsa(
                        rs.getTimestamp(2).toLocalDateTime(),
                        rs.getTimestamp(3).toLocalDateTime()));
            }
        }
        return tsas;
    }

    private static Map<String, Artifact> loadArtifacts(Connection conn) throws Exception {
        Map<String, Artifact> artifacts = new HashMap<>();
        try (PreparedStatement ps = conn.prepareStatement(
                "SELECT artifact_id, channel_id FROM artifacts");
                ResultSet rs = ps.executeQuery()) {
            while (rs.next()) {
                artifacts.put(rs.getString(1), new Artifact(rs.getString(1), rs.getString(2)));
            }
        }
        return artifacts;
    }

    private static Map<String, List<Evidence>> loadEvidence(Connection conn) throws Exception {
        Map<String, List<Evidence>> evidence = new HashMap<>();
        try (PreparedStatement ps = conn.prepareStatement(
                "SELECT evidence_id, artifact_id, sha256_digest, signer_key_id, signed_at, "
                        + "recorded_at, status, supersedes_evidence_id, amendment_key_id, tsa_id "
                        + "FROM artifact_evidence");
                ResultSet rs = ps.executeQuery()) {
            while (rs.next()) {
                evidence.computeIfAbsent(rs.getString(2), k -> new ArrayList<>()).add(new Evidence(
                        rs.getString(1),
                        rs.getString(2),
                        rs.getString(3),
                        rs.getString(4),
                        rs.getTimestamp(5).toLocalDateTime(),
                        rs.getTimestamp(6).toLocalDateTime(),
                        rs.getString(7),
                        rs.getString(8),
                        rs.getString(9),
                        rs.getString(10)));
            }
        }
        return evidence;
    }

    private static void writeReport(
            Connection conn, String artifactId, String verdict, String reasonCode) throws Exception {
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

    private record Key(String keyId, LocalDateTime notBefore, LocalDateTime notAfter) {}

    private record Event(
            String eventId,
            String keyId,
            String eventType,
            String reason,
            LocalDateTime occurredAt,
            LocalDateTime effectiveFrom) {}

    private record Tsa(LocalDateTime validFrom, LocalDateTime validUntil) {}

    private record Artifact(String artifactId, String channelId) {}

    private record Evidence(
            String evidenceId,
            String artifactId,
            String sha256Digest,
            String signerKeyId,
            LocalDateTime signedAt,
            LocalDateTime recordedAt,
            String status,
            String supersedes,
            String amendmentKeyId,
            String tsaId) {}

    private record Verdict(String verdict, String reasonCode) {}

    private record HttpResult(int status, String body) {}
}
