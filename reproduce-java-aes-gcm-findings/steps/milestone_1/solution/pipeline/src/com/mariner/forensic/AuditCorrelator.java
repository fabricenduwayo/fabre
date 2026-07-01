package com.mariner.forensic;

import java.nio.file.Path;
import java.security.MessageDigest;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.ResultSet;
import java.sql.Statement;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

/**
 * Milestone 2 — correlate SQLite audit events with extracted rules.
 */
final class AuditCorrelator {
    private static final Path RULES = Path.of("/app/out/rules.json");
    private static final Path OUT = Path.of("/app/out/correlation.json");
    private static final String JDBC = "jdbc:sqlite:/app/data/forensic_audit.db";

    static void run() throws Exception {
        Map<String, Object> rules = Json.readMap(RULES);
        List<AuditEvent> events = loadEvents();
        List<FrameRow> frames = loadFrames();

        List<Map<String, Object>> out = new ArrayList<>();
        for (FrameRow frame : frames) {
            int keyVersion = resolveKeyVersion(frame.frameId(), events);
            String keySource = hasRotation(frame.frameId(), events)
                    ? "rotation_replacement" : "latest_assigned";
            byte[] nonce = resolveNonce(frame.frameId(), keyVersion, rules, events);
            String nonceSource = nonceSource(frame.frameId(), keyVersion, rules, events);

            Map<String, Object> rec = new LinkedHashMap<>();
            rec.put("frame_id", frame.frameId());
            rec.put("label", frame.label());
            rec.put("gif_index", frame.gifIndex());
            rec.put("key_version", keyVersion);
            rec.put("key_source", keySource);
            rec.put("nonce_hex", toHex(nonce));
            rec.put("nonce_source", nonceSource);
            out.add(rec);
        }

        Json.writeList(OUT, out);
        System.out.println("correlate: wrote " + out.size() + " rows to " + OUT);
    }

    private record FrameRow(String frameId, String label, int gifIndex) {}

    private record AuditEvent(
            String frameId,
            String eventType,
            Integer keyVersion,
            Integer replacementKeyVersion,
            String nonceOverrideHex,
            String supersedesNonceHex,
            String recordedAt) {}

    private record NonceCandidate(String recordedAt, String nonceHex, Integer keyVersion) {}

    private static List<FrameRow> loadFrames() throws Exception {
        List<FrameRow> rows = new ArrayList<>();
        try (Connection conn = DriverManager.getConnection(JDBC);
             Statement st = conn.createStatement();
             ResultSet rs = st.executeQuery(
                     "SELECT frame_id, label, gif_index FROM frames ORDER BY gif_index")) {
            while (rs.next()) {
                rows.add(new FrameRow(
                        rs.getString(1), rs.getString(2), rs.getInt(3)));
            }
        }
        return rows;
    }

    private static List<AuditEvent> loadEvents() throws Exception {
        List<AuditEvent> rows = new ArrayList<>();
        try (Connection conn = DriverManager.getConnection(JDBC);
             Statement st = conn.createStatement();
             ResultSet rs = st.executeQuery(
                     "SELECT frame_id, event_type, key_version, replacement_key_version, "
                     + "nonce_override_hex, supersedes_nonce_hex, recorded_at "
                     + "FROM audit_events")) {
            while (rs.next()) {
                rows.add(new AuditEvent(
                        rs.getString(1),
                        rs.getString(2),
                        (Integer) rs.getObject(3),
                        (Integer) rs.getObject(4),
                        rs.getString(5),
                        rs.getString(6),
                        rs.getString(7)));
            }
        }
        return rows;
    }

    private static java.util.Set<String> revokedNonceHex(
            String frameId, List<AuditEvent> events) {
        java.util.Set<String> revoked = new java.util.HashSet<>();
        for (AuditEvent event : events) {
            if (frameId.equals(event.frameId())
                    && "nonce_override_revoked".equals(event.eventType())
                    && event.nonceOverrideHex() != null) {
                revoked.add(event.nonceOverrideHex());
            }
        }
        return revoked;
    }

    private static List<NonceCandidate> dbOverrideCandidates(
            String frameId, List<AuditEvent> events) {
        java.util.Set<String> revoked = revokedNonceHex(frameId, events);
        List<AuditEvent> frameEvents = events.stream()
                .filter(e -> frameId.equals(e.frameId()))
                .sorted(Comparator.comparing(AuditEvent::recordedAt))
                .toList();
        List<NonceCandidate> candidates = new ArrayList<>();

        for (AuditEvent event : frameEvents) {
            String eventType = event.eventType();
            if ("nonce_override_revoked".equals(eventType)) {
                continue;
            }
            if ("nonce_override_registered".equals(eventType)) {
                String hex = event.nonceOverrideHex();
                if (hex != null && !revoked.contains(hex)) {
                    candidates.add(new NonceCandidate(
                            event.recordedAt(), hex, event.keyVersion()));
                }
            } else if ("nonce_override_amended".equals(eventType)) {
                String supersedes = event.supersedesNonceHex();
                if (supersedes != null) {
                    candidates.removeIf(c -> supersedes.equals(c.nonceHex()));
                }
                String hex = event.nonceOverrideHex();
                if (hex != null && !revoked.contains(hex)) {
                    candidates.add(new NonceCandidate(
                            event.recordedAt(), hex, event.keyVersion()));
                }
            }
        }

        return candidates.stream()
                .filter(c -> !revoked.contains(c.nonceHex()))
                .toList();
    }

    private static java.util.Set<Integer> rescindedAssignmentVersions(
            String frameId, List<AuditEvent> events) {
        java.util.Set<Integer> voided = new java.util.HashSet<>();
        for (AuditEvent event : events) {
            if (frameId.equals(event.frameId())
                    && "key_assignment_rescinded".equals(event.eventType())
                    && event.keyVersion() != null) {
                voided.add(event.keyVersion());
            }
        }
        return voided;
    }

    private static java.util.Set<java.util.AbstractMap.SimpleEntry<Integer, Integer>>
            rescindedRotationPairs(String frameId, List<AuditEvent> events) {
        java.util.Set<java.util.AbstractMap.SimpleEntry<Integer, Integer>> voided =
                new java.util.HashSet<>();
        for (AuditEvent event : events) {
            if (frameId.equals(event.frameId())
                    && "key_rotation_rescinded".equals(event.eventType())
                    && event.keyVersion() != null
                    && event.replacementKeyVersion() != null) {
                voided.add(new java.util.AbstractMap.SimpleEntry<>(
                        event.keyVersion(), event.replacementKeyVersion()));
            }
        }
        return voided;
    }

    private static boolean rotationVoided(
            AuditEvent rotation,
            java.util.Set<java.util.AbstractMap.SimpleEntry<Integer, Integer>> voided) {
        for (java.util.AbstractMap.SimpleEntry<Integer, Integer> pair : voided) {
            if (pair.getKey().equals(rotation.keyVersion())
                    && pair.getValue().equals(rotation.replacementKeyVersion())) {
                return true;
            }
        }
        return false;
    }

    private static boolean hasRotation(String frameId, List<AuditEvent> events) {
        java.util.Set<java.util.AbstractMap.SimpleEntry<Integer, Integer>> voided =
                rescindedRotationPairs(frameId, events);
        return events.stream()
                .anyMatch(e -> frameId.equals(e.frameId())
                        && "key_rotated".equals(e.eventType())
                        && !rotationVoided(e, voided));
    }

    private static int resolveKeyVersion(String frameId, List<AuditEvent> events) {
        java.util.Set<java.util.AbstractMap.SimpleEntry<Integer, Integer>> voided =
                rescindedRotationPairs(frameId, events);
        List<AuditEvent> rotations = events.stream()
                .filter(e -> frameId.equals(e.frameId())
                        && "key_rotated".equals(e.eventType())
                        && !rotationVoided(e, voided))
                .toList();
        if (!rotations.isEmpty()) {
            AuditEvent latest = rotations.stream()
                    .max(Comparator.comparing(AuditEvent::recordedAt))
                    .orElseThrow();
            return latest.replacementKeyVersion();
        }
        AuditEvent latestAssigned = events.stream()
                .filter(e -> frameId.equals(e.frameId()) && "key_assigned".equals(e.eventType()))
                .filter(e -> !rescindedAssignmentVersions(frameId, events).contains(e.keyVersion()))
                .max(Comparator.comparing(AuditEvent::recordedAt))
                .orElseThrow();
        return latestAssigned.keyVersion();
    }

    @SuppressWarnings("unchecked")
    private static byte[] resolveNonce(
            String frameId,
            int keyVersion,
            Map<String, Object> rules,
            List<AuditEvent> events) throws Exception {
        Map<String, String> overrides = (Map<String, String>) rules.get("nonce_overrides");
        if (overrides != null && overrides.containsKey(frameId)) {
            return fromHex(overrides.get(frameId));
        }
        List<NonceCandidate> matching = dbOverrideCandidates(frameId, events).stream()
                .filter(c -> c.keyVersion() != null && c.keyVersion() == keyVersion)
                .toList();
        if (!matching.isEmpty()) {
            NonceCandidate latest = matching.stream()
                    .max(Comparator.comparing(NonceCandidate::recordedAt))
                    .orElseThrow();
            return fromHex(latest.nonceHex());
        }
        return derivedNonce(frameId, keyVersion);
    }

    @SuppressWarnings("unchecked")
    private static String nonceSource(
            String frameId,
            int keyVersion,
            Map<String, Object> rules,
            List<AuditEvent> events) {
        Map<String, String> overrides = (Map<String, String>) rules.get("nonce_overrides");
        if (overrides != null && overrides.containsKey(frameId)) {
            return "override";
        }
        boolean db = dbOverrideCandidates(frameId, events).stream()
                .anyMatch(c -> c.keyVersion() != null && c.keyVersion() == keyVersion);
        return db ? "override" : "derived";
    }

    private static byte[] derivedNonce(String frameId, int keyVersion) throws Exception {
        MessageDigest sha = MessageDigest.getInstance("SHA-256");
        byte[] digest = sha.digest((frameId + ":" + keyVersion).getBytes());
        byte[] nonce = new byte[12];
        System.arraycopy(digest, 0, nonce, 0, 12);
        return nonce;
    }

    private static String toHex(byte[] data) {
        StringBuilder sb = new StringBuilder(data.length * 2);
        for (byte b : data) {
            sb.append(String.format("%02X", b));
        }
        return sb.toString();
    }

    private static byte[] fromHex(String hex) {
        byte[] out = new byte[hex.length() / 2];
        for (int i = 0; i < out.length; i++) {
            out[i] = (byte) Integer.parseInt(hex.substring(i * 2, i * 2 + 2), 16);
        }
        return out;
    }

    private AuditCorrelator() {}
}
