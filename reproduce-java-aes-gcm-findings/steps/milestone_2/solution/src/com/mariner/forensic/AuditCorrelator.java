package com.mariner.forensic;

import java.nio.charset.StandardCharsets;
import java.nio.file.Path;
import java.security.MessageDigest;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.ResultSet;
import java.sql.Statement;
import java.util.AbstractMap.SimpleEntry;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.HashMap;
import java.util.HashSet;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;

/** Correlate audit lifecycle events with the milestone 1 rule register. */
final class AuditCorrelator {
    private static final Path RULES = Path.of("/app/out/rules.json");
    private static final Path OUT = Path.of("/app/out/correlation.json");
    private static final String JDBC = "jdbc:sqlite:/app/data/forensic_audit.db";

    private record FrameRow(String frameId, String label, int gifIndex) {}

    private record AuditEvent(
            int eventId,
            String frameId,
            String eventType,
            Integer keyVersion,
            Integer replacementKeyVersion,
            String nonceOverrideHex,
            String supersedesNonceHex,
            String recordedAt,
            String effectiveAt) {}

    private record NonceCandidate(
            AuditEvent lastEvent,
            String nonceHex,
            Integer keyVersion,
            List<Integer> eventIds) {}

    static void run() throws Exception {
        Map<String, Object> rules = Json.readMap(RULES);
        List<AuditEvent> events = loadEvents();
        List<Map<String, Object>> output = new ArrayList<>();

        for (FrameRow frame : loadFrames()) {
            int keyVersion = resolveKeyVersion(frame.frameId(), events);
            boolean rotated = hasRotation(frame.frameId(), events);
            NonceDecision nonce = resolveNonce(frame.frameId(), keyVersion, rules, events);

            Map<String, Object> row = new LinkedHashMap<>();
            row.put("frame_id", frame.frameId());
            row.put("label", frame.label());
            row.put("gif_index", frame.gifIndex());
            row.put("key_version", keyVersion);
            row.put("key_source", rotated ? "rotation_replacement" : "latest_assigned");
            row.put("key_event_ids", keyEventIds(frame.frameId(), keyVersion, events));
            row.put("nonce_hex", nonce.nonceHex());
            row.put("nonce_source", nonce.source());
            row.put("nonce_event_ids", nonce.eventIds());
            output.add(row);
        }

        Json.writeList(OUT, output);
        System.out.println("correlate: wrote " + output.size() + " rows to " + OUT);
    }

    private record NonceDecision(String nonceHex, String source, List<Integer> eventIds) {}

    private static List<FrameRow> loadFrames() throws Exception {
        List<FrameRow> rows = new ArrayList<>();
        try (Connection conn = DriverManager.getConnection(JDBC);
                Statement statement = conn.createStatement();
                ResultSet rs = statement.executeQuery(
                        "SELECT frame_id, label, gif_index FROM frames ORDER BY gif_index")) {
            while (rs.next()) {
                rows.add(new FrameRow(rs.getString(1), rs.getString(2), rs.getInt(3)));
            }
        }
        return rows;
    }

    private static List<AuditEvent> loadEvents() throws Exception {
        List<AuditEvent> rows = new ArrayList<>();
        try (Connection conn = DriverManager.getConnection(JDBC);
                Statement statement = conn.createStatement();
                ResultSet rs = statement.executeQuery(
                        "SELECT event_id, frame_id, event_type, key_version, "
                                + "replacement_key_version, nonce_override_hex, "
                                + "supersedes_nonce_hex, recorded_at, effective_at "
                                + "FROM audit_events")) {
            while (rs.next()) {
                rows.add(new AuditEvent(
                        rs.getInt(1),
                        rs.getString(2),
                        rs.getString(3),
                        (Integer) rs.getObject(4),
                        (Integer) rs.getObject(5),
                        rs.getString(6),
                        rs.getString(7),
                        rs.getString(8),
                        rs.getString(9)));
            }
        }
        return rows;
    }

    private static int compareEvents(AuditEvent left, AuditEvent right) {
        int effective = left.effectiveAt().compareTo(right.effectiveAt());
        if (effective != 0) {
            return effective;
        }
        int recorded = left.recordedAt().compareTo(right.recordedAt());
        if (recorded != 0) {
            return recorded;
        }
        return Integer.compare(left.eventId(), right.eventId());
    }

    private static Set<Integer> rescindedAssignmentVersions(
            String frameId, List<AuditEvent> events) {
        Set<Integer> voided = new HashSet<>();
        for (AuditEvent event : events) {
            if (frameId.equals(event.frameId())
                    && "key_assignment_rescinded".equals(event.eventType())
                    && event.keyVersion() != null) {
                voided.add(event.keyVersion());
            }
        }
        return voided;
    }

    private static Set<SimpleEntry<Integer, Integer>> rescindedRotationPairs(
            String frameId, List<AuditEvent> events) {
        Set<SimpleEntry<Integer, Integer>> voided = new HashSet<>();
        for (AuditEvent event : events) {
            if (frameId.equals(event.frameId())
                    && "key_rotation_rescinded".equals(event.eventType())
                    && event.keyVersion() != null
                    && event.replacementKeyVersion() != null) {
                voided.add(new SimpleEntry<>(
                        event.keyVersion(), event.replacementKeyVersion()));
            }
        }
        return voided;
    }

    private static boolean rotationVoided(
            AuditEvent rotation, Set<SimpleEntry<Integer, Integer>> voided) {
        return voided.contains(new SimpleEntry<>(
                rotation.keyVersion(), rotation.replacementKeyVersion()));
    }

    private static List<AuditEvent> survivingRotations(
            String frameId, List<AuditEvent> events) {
        Set<SimpleEntry<Integer, Integer>> voided = rescindedRotationPairs(frameId, events);
        return events.stream()
                .filter(event -> frameId.equals(event.frameId()))
                .filter(event -> "key_rotated".equals(event.eventType()))
                .filter(event -> !rotationVoided(event, voided))
                .toList();
    }

    private static boolean hasRotation(String frameId, List<AuditEvent> events) {
        return !survivingRotations(frameId, events).isEmpty();
    }

    private static int resolveKeyVersion(String frameId, List<AuditEvent> events) {
        List<AuditEvent> rotations = survivingRotations(frameId, events);
        if (!rotations.isEmpty()) {
            return rotations.stream()
                    .max(AuditCorrelator::compareEvents)
                    .orElseThrow()
                    .replacementKeyVersion();
        }
        Set<Integer> rescinded = rescindedAssignmentVersions(frameId, events);
        return events.stream()
                .filter(event -> frameId.equals(event.frameId()))
                .filter(event -> "key_assigned".equals(event.eventType()))
                .filter(event -> !rescinded.contains(event.keyVersion()))
                .max(AuditCorrelator::compareEvents)
                .orElseThrow()
                .keyVersion();
    }

    private static List<Integer> keyEventIds(
            String frameId, int keyVersion, List<AuditEvent> events) {
        List<AuditEvent> rotations = survivingRotations(frameId, events);
        List<Integer> path = new ArrayList<>();
        int current = keyVersion;
        while (true) {
            int target = current;
            AuditEvent hop = rotations.stream()
                    .filter(event -> event.replacementKeyVersion() != null)
                    .filter(event -> event.replacementKeyVersion() == target)
                    .max(AuditCorrelator::compareEvents)
                    .orElse(null);
            if (hop == null) {
                break;
            }
            path.add(hop.eventId());
            current = hop.keyVersion();
        }
        Collections.reverse(path);

        int rootVersion = current;
        Set<Integer> rescinded = rescindedAssignmentVersions(frameId, events);
        AuditEvent assignment = events.stream()
                .filter(event -> frameId.equals(event.frameId()))
                .filter(event -> "key_assigned".equals(event.eventType()))
                .filter(event -> event.keyVersion() != null)
                .filter(event -> event.keyVersion() == rootVersion)
                .filter(event -> !rescinded.contains(event.keyVersion()))
                .max(AuditCorrelator::compareEvents)
                .orElseThrow();
        path.add(0, assignment.eventId());
        return List.copyOf(path);
    }

    private static Set<String> revokedNonceHex(String frameId, List<AuditEvent> events) {
        Set<String> revoked = new HashSet<>();
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
        Set<String> revoked = revokedNonceHex(frameId, events);
        List<AuditEvent> frameEvents = events.stream()
                .filter(event -> frameId.equals(event.frameId()))
                .sorted(AuditCorrelator::compareEvents)
                .toList();
        List<NonceCandidate> candidates = new ArrayList<>();
        Map<String, List<Integer>> history = new HashMap<>();

        for (AuditEvent event : frameEvents) {
            String type = event.eventType();
            if ("nonce_override_registered".equals(type)) {
                registerCandidate(candidates, history, revoked, event, List.of());
            } else if ("nonce_override_amended".equals(type)
                    || "nonce_override_replaced".equals(type)) {
                String superseded = event.supersedesNonceHex();
                List<Integer> path = pathFor(superseded, candidates, history);
                if (superseded != null) {
                    candidates.removeIf(candidate -> superseded.equals(candidate.nonceHex()));
                }
                registerCandidate(candidates, history, revoked, event, path);
            } else if ("nonce_override_replacement_rescinded".equals(type)) {
                String voided = event.supersedesNonceHex();
                if (voided != null) {
                    candidates.removeIf(candidate -> voided.equals(candidate.nonceHex()));
                }
                String restored = event.nonceOverrideHex();
                if (restored != null && !revoked.contains(restored)) {
                    List<Integer> path = append(
                            history.getOrDefault(restored, List.of()), event.eventId());
                    candidates.add(new NonceCandidate(
                            event, restored, event.keyVersion(), path));
                    history.put(restored, path);
                }
            }
        }
        return candidates.stream()
                .filter(candidate -> !revoked.contains(candidate.nonceHex()))
                .toList();
    }

    private static void registerCandidate(
            List<NonceCandidate> candidates,
            Map<String, List<Integer>> history,
            Set<String> revoked,
            AuditEvent event,
            List<Integer> priorPath) {
        String nonceHex = event.nonceOverrideHex();
        if (nonceHex == null || revoked.contains(nonceHex)) {
            return;
        }
        List<Integer> path = append(priorPath, event.eventId());
        NonceCandidate candidate = new NonceCandidate(
                event, nonceHex, event.keyVersion(), path);
        candidates.add(candidate);
        history.put(nonceHex, path);
    }

    private static List<Integer> pathFor(
            String nonceHex,
            List<NonceCandidate> candidates,
            Map<String, List<Integer>> history) {
        if (nonceHex == null) {
            return List.of();
        }
        return candidates.stream()
                .filter(candidate -> nonceHex.equals(candidate.nonceHex()))
                .max((left, right) -> compareEvents(left.lastEvent(), right.lastEvent()))
                .map(NonceCandidate::eventIds)
                .orElseGet(() -> history.getOrDefault(nonceHex, List.of()));
    }

    private static List<Integer> append(List<Integer> path, int eventId) {
        List<Integer> output = new ArrayList<>(path);
        output.add(eventId);
        return List.copyOf(output);
    }

    @SuppressWarnings("unchecked")
    private static NonceDecision resolveNonce(
            String frameId,
            int keyVersion,
            Map<String, Object> rules,
            List<AuditEvent> events) throws Exception {
        Map<String, String> reportOverrides =
                (Map<String, String>) rules.get("nonce_overrides");
        if (reportOverrides != null && reportOverrides.containsKey(frameId)) {
            return new NonceDecision(reportOverrides.get(frameId), "override", List.of());
        }

        NonceCandidate database = dbOverrideCandidates(frameId, events).stream()
                .filter(candidate -> candidate.keyVersion() != null)
                .filter(candidate -> candidate.keyVersion() == keyVersion)
                .max((left, right) -> compareEvents(left.lastEvent(), right.lastEvent()))
                .orElse(null);
        if (database != null) {
            return new NonceDecision(
                    database.nonceHex(), "override", database.eventIds());
        }
        return new NonceDecision(derivedNonce(frameId, keyVersion), "derived", List.of());
    }

    private static String derivedNonce(String frameId, int keyVersion) throws Exception {
        MessageDigest sha = MessageDigest.getInstance("SHA-256");
        byte[] digest = sha.digest(
                (frameId + ":" + keyVersion).getBytes(StandardCharsets.UTF_8));
        byte[] nonce = new byte[12];
        System.arraycopy(digest, 0, nonce, 0, nonce.length);
        return toHex(nonce);
    }

    private static String toHex(byte[] data) {
        StringBuilder output = new StringBuilder(data.length * 2);
        for (byte value : data) {
            output.append(String.format("%02X", value));
        }
        return output.toString();
    }

    private AuditCorrelator() {}
}
