package com.snorkel.registry;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.SerializationFeature;
import com.fasterxml.jackson.databind.node.ArrayNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.networknt.schema.JsonSchema;
import com.networknt.schema.JsonSchemaFactory;
import com.networknt.schema.SpecVersion;
import com.networknt.schema.ValidationMessage;

import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.nio.file.Files;
import java.nio.file.Path;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.ResultSet;
import java.sql.Statement;
import java.time.Instant;
import java.time.LocalDateTime;
import java.time.ZoneOffset;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.HashMap;
import java.util.HashSet;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.TreeMap;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/** Derive the release-decision manifest from live registry API + H2 evidence. */
public final class Reconciler {
    private static final Path POLICY_PATH = Path.of("/app/policy/promotion-policy.md");
    private static final Path SCHEMA_PATH = Path.of("/app/schemas/release-decision.schema.json");
    private static final String CANDIDATES_URL = "http://localhost:8080/models/candidates";

    private static final String REASON_METRIC = "metric_threshold";
    private static final String REASON_UNCALIBRATED = "uncalibrated";
    private static final String REASON_LINEAGE = "lineage_mismatch";
    private static final String REASON_MISSING = "missing_canonical_evidence";
    private static final String REASON_TIEBREAK = "lost_tiebreak";
    private static final double TOL = 1e-9;

    private static final ObjectMapper JSON =
            new ObjectMapper().enable(SerializationFeature.INDENT_OUTPUT);
    private static final JsonSchemaFactory SCHEMA_FACTORY =
            JsonSchemaFactory.getInstance(SpecVersion.VersionFlag.V202012);
    private static final HttpClient HTTP = HttpClient.newBuilder().build();

    public static void reconcile(String jdbcUrl, String outputPath) throws Exception {
        String policy = Files.readString(POLICY_PATH);
        double aucFloor = policyFloor(policy, "AUC");
        double accuracyFloor = policyFloor(policy, "Accuracy");

        List<JsonNode> candidates = fetchCandidates();
        Evidence evidence = loadEvidence(jdbcUrl);
        ObjectNode manifest = buildManifest(candidates, evidence, aucFloor, accuracyFloor);
        validateManifest(manifest);

        Path out = Path.of(outputPath);
        Files.createDirectories(out.getParent());
        Files.writeString(out, JSON.writeValueAsString(manifest) + System.lineSeparator());
        System.out.printf(
                "release decision written to %s (promoted=%s)%n",
                out,
                manifest.get("promoted"));
    }

    private static double policyFloor(String policy, String metricLabel) {
        Pattern pattern = Pattern.compile(
                "\\|\\s*" + Pattern.quote(metricLabel)
                        + "\\s*\\|\\s*must be greater than or equal to\\s*([0-9.]+)");
        Matcher match = pattern.matcher(policy);
        if (!match.find()) {
            throw new IllegalStateException(
                    "promotion policy does not state the " + metricLabel + " floor");
        }
        return Double.parseDouble(match.group(1));
    }

    private static String readUrl(String dbUrl) {
        return dbUrl.contains("IFEXISTS") ? dbUrl : dbUrl + ";IFEXISTS=TRUE";
    }

    private static List<Map<String, String>> h2Select(String sql, String dbUrl) throws Exception {
        List<Map<String, String>> rows = new ArrayList<>();
        try (Connection conn = DriverManager.getConnection(readUrl(dbUrl), "sa", "");
                Statement stmt = conn.createStatement();
                ResultSet rs = stmt.executeQuery(sql)) {
            int columnCount = rs.getMetaData().getColumnCount();
            while (rs.next()) {
                Map<String, String> row = new LinkedHashMap<>();
                for (int i = 1; i <= columnCount; i++) {
                    String name = rs.getMetaData().getColumnLabel(i).toLowerCase();
                    String value = rs.getString(i);
                    row.put(name, value == null ? "" : value);
                }
                rows.add(row);
            }
        }
        return rows;
    }

    private static List<JsonNode> fetchCandidates() throws Exception {
        Exception lastError = null;
        for (int attempt = 0; attempt < 120; attempt++) {
            try {
                HttpRequest request =
                        HttpRequest.newBuilder(URI.create(CANDIDATES_URL)).GET().timeout(
                                java.time.Duration.ofSeconds(10)).build();
                HttpResponse<String> response =
                        HTTP.send(request, HttpResponse.BodyHandlers.ofString());
                JsonNode body = JSON.readTree(response.body());
                if (body.isArray()) {
                    List<JsonNode> candidates = new ArrayList<>();
                    body.forEach(candidates::add);
                    return candidates;
                }
                lastError = new IllegalStateException(
                        "unexpected candidates payload: " + body.getNodeType());
            } catch (Exception exc) {
                lastError = exc;
            }
            Thread.sleep(1000);
        }
        throw new IllegalStateException(
                "registry API never served /models/candidates", lastError);
    }

    private static Instant parseTimestamp(String value) {
        String trimmed = value.strip().replace("Z", "+00:00");
        if (trimmed.contains("T")) {
            if (trimmed.contains("+") || trimmed.indexOf('-', 10) >= 0) {
                return java.time.OffsetDateTime.parse(trimmed).toInstant();
            }
            return LocalDateTime.parse(trimmed).toInstant(ZoneOffset.UTC);
        }
        return LocalDateTime.parse(trimmed.replace(' ', 'T')).toInstant(ZoneOffset.UTC);
    }

    private static List<ActiveWaiver> activeWaivers(String dbUrl) throws Exception {
        List<Map<String, String>> contexts =
                h2Select("SELECT context_id, decision_at FROM release_context", dbUrl);
        if (contexts.size() != 1) {
            throw new IllegalStateException("release_context must contain exactly one decision");
        }
        Instant decisionAt = parseTimestamp(contexts.get(0).get("decision_at"));

        Map<String, Map<String, String>> waivers = new HashMap<>();
        for (Map<String, String> row :
                h2Select(
                        """
                        SELECT waiver_id, model_id, model_version, reason_code,
                               valid_from, valid_until, replaces_waiver_id
                        FROM promotion_waivers
                        """,
                        dbUrl)) {
            waivers.put(row.get("waiver_id"), row);
        }

        Map<String, Map<String, String>> events = new HashMap<>();
        for (Map<String, String> row :
                h2Select(
                        """
                        SELECT event_id, waiver_id, event_type, occurred_at, paired_event_id
                        FROM waiver_events
                        """,
                        dbUrl)) {
            if (!parseTimestamp(row.get("occurred_at")).isAfter(decisionAt)) {
                events.put(row.get("event_id"), row);
            }
        }

        List<Map<String, String>> validEvents = new ArrayList<>();
        for (Map<String, String> event : events.values()) {
            Map<String, String> waiver = waivers.get(event.get("waiver_id"));
            String pairedId = event.getOrDefault("paired_event_id", "").strip();
            if (pairedId.isEmpty()) {
                if ("revoke".equals(event.get("event_type"))
                        || waiver.getOrDefault("replaces_waiver_id", "").strip().isEmpty()) {
                    validEvents.add(event);
                }
                continue;
            }
            Map<String, String> mate = events.get(pairedId);
            if (mate == null
                    || !event.get("event_id").equals(mate.getOrDefault("paired_event_id", "").strip())) {
                continue;
            }
            if (!event.get("occurred_at").equals(mate.get("occurred_at"))) {
                continue;
            }
            Map<String, Map<String, String>> pair = new HashMap<>();
            pair.put(event.get("event_type"), event);
            pair.put(mate.get("event_type"), mate);
            if (!Set.of("grant", "revoke").equals(pair.keySet())) {
                continue;
            }
            Map<String, String> successor = waivers.get(pair.get("grant").get("waiver_id"));
            Map<String, String> predecessor = waivers.get(pair.get("revoke").get("waiver_id"));
            if (!predecessor.get("waiver_id").equals(
                    successor.getOrDefault("replaces_waiver_id", "").strip())) {
                continue;
            }
            if (!successor.get("model_id").equals(predecessor.get("model_id"))
                    || !successor.get("model_version").equals(predecessor.get("model_version"))
                    || !successor.get("reason_code").equals(predecessor.get("reason_code"))) {
                continue;
            }
            validEvents.add(event);
        }

        Map<String, Map<String, String>> latest = new HashMap<>();
        for (Map<String, String> event : validEvents) {
            Map<String, String> current = latest.get(event.get("waiver_id"));
            List<Comparable<?>> eventKey =
                    List.of(parseTimestamp(event.get("occurred_at")), event.get("event_id"));
            if (current == null
                    || compareEventKey(eventKey, current) > 0) {
                latest.put(event.get("waiver_id"), event);
            }
        }

        List<ActiveWaiver> active = new ArrayList<>();
        for (Map.Entry<String, Map<String, String>> entry : latest.entrySet()) {
            Map<String, String> waiver = waivers.get(entry.getKey());
            Map<String, String> event = entry.getValue();
            if (!"grant".equals(event.get("event_type"))) {
                continue;
            }
            Instant validFrom = parseTimestamp(waiver.get("valid_from"));
            Instant validUntil = parseTimestamp(waiver.get("valid_until"));
            if (!decisionAt.isBefore(validFrom) && decisionAt.isBefore(validUntil)) {
                active.add(
                        new ActiveWaiver(
                                waiver.get("waiver_id"),
                                waiver.get("model_id"),
                                waiver.get("model_version"),
                                waiver.get("reason_code"),
                                parseTimestamp(event.get("occurred_at"))));
            }
        }
        return active;
    }

    private static int compareEventKey(
            List<Comparable<?>> key, Map<String, String> current) {
        List<Comparable<?>> currentKey =
                List.of(
                        parseTimestamp(current.get("occurred_at")),
                        current.get("event_id"));
        for (int i = 0; i < key.size(); i++) {
            @SuppressWarnings("unchecked")
            int cmp = ((Comparable<Object>) key.get(i)).compareTo(currentKey.get(i));
            if (cmp != 0) {
                return cmp;
            }
        }
        return 0;
    }

    private static Evidence loadEvidence(String dbUrl) throws Exception {
        List<Map<String, String>> runs =
                h2Select(
                        """
                        SELECT run_id, model_id, captured_at, status, auc, accuracy,
                               supersedes_run_id
                        FROM validation_runs
                        """,
                        dbUrl);
        Set<String> voided = new HashSet<>();
        for (Map<String, String> row : runs) {
            String supersedes = row.getOrDefault("supersedes_run_id", "").strip();
            if (!supersedes.isEmpty()) {
                voided.add(supersedes);
            }
        }
        Map<String, Map<String, String>> latestByModel = new HashMap<>();
        for (Map<String, String> row : runs) {
            if (!"completed".equals(row.get("status"))) {
                continue;
            }
            if (voided.contains(row.get("run_id"))) {
                continue;
            }
            String modelId = row.get("model_id");
            Map<String, String> current = latestByModel.get(modelId);
            if (current == null
                    || row.get("captured_at").compareTo(current.get("captured_at")) > 0) {
                latestByModel.put(modelId, row);
            }
        }
        Map<String, double[]> metrics = new HashMap<>();
        for (Map.Entry<String, Map<String, String>> entry : latestByModel.entrySet()) {
            Map<String, String> row = entry.getValue();
            metrics.put(
                    entry.getKey(),
                    new double[] {
                        Double.parseDouble(row.get("auc")),
                        Double.parseDouble(row.get("accuracy"))
                    });
        }
        Map<LineageKey, String> lineage = new HashMap<>();
        for (Map<String, String> row :
                h2Select(
                        "SELECT model_id, model_version, feature_hash FROM feature_hash_lineage",
                        dbUrl)) {
            lineage.put(
                    new LineageKey(row.get("model_id"), row.get("model_version")),
                    row.get("feature_hash"));
        }
        Map<String, Boolean> calibrated = new HashMap<>();
        for (Map<String, String> row :
                h2Select("SELECT model_id, calibrated FROM calibration_status", dbUrl)) {
            String flag = row.get("calibrated").strip().toUpperCase();
            calibrated.put(row.get("model_id"), flag.equals("TRUE") || flag.equals("1") || flag.equals("T"));
        }
        return new Evidence(metrics, lineage, calibrated, activeWaivers(dbUrl));
    }

    private static ObjectNode buildManifest(
            List<JsonNode> candidates,
            Evidence evidence,
            double aucFloor,
            double accuracyFloor) {
        Map<String, List<String>> reasons = new LinkedHashMap<>();
        List<ObjectNode> conflicts = new ArrayList<>();
        List<ObjectNode> appliedWaivers = new ArrayList<>();

        for (JsonNode candidate : candidates) {
            String modelId = candidate.get("id").asText();
            String version = candidate.get("version").asText();
            String registryHash = candidate.get("featureHash").asText();
            double apiAuc = candidate.get("metrics").get("auc").asDouble();
            double apiAccuracy = candidate.get("metrics").get("accuracy").asDouble();

            double[] metrics = evidence.metrics.get(modelId);
            Boolean calibratedFlag = evidence.calibrated.get(modelId);
            String canonicalHash = evidence.lineage.get(new LineageKey(modelId, version));

            if (metrics != null) {
                double dbAuc = metrics[0];
                double dbAccuracy = metrics[1];
                if (Math.abs(apiAuc - dbAuc) > TOL) {
                    conflicts.add(conflict(modelId, "auc", apiAuc, dbAuc));
                }
                if (Math.abs(apiAccuracy - dbAccuracy) > TOL) {
                    conflicts.add(conflict(modelId, "accuracy", apiAccuracy, dbAccuracy));
                }
            }
            if (canonicalHash != null && !canonicalHash.equals(registryHash)) {
                conflicts.add(conflict(modelId, "feature_hash", registryHash, canonicalHash));
            }

            List<String> fails = new ArrayList<>();
            if (metrics == null || calibratedFlag == null || canonicalHash == null) {
                fails.add(REASON_MISSING);
            } else {
                double dbAuc = metrics[0];
                double dbAccuracy = metrics[1];
                if (dbAuc < aucFloor || dbAccuracy < accuracyFloor) {
                    fails.add(REASON_METRIC);
                }
                if (!calibratedFlag) {
                    fails.add(REASON_UNCALIBRATED);
                }
                if (!canonicalHash.equals(registryHash)) {
                    fails.add(REASON_LINEAGE);
                }

                List<String> remaining = new ArrayList<>();
                for (String reason : fails) {
                    List<ActiveWaiver> matching = new ArrayList<>();
                    for (ActiveWaiver waiver : evidence.activeWaivers) {
                        if (waiver.modelId.equals(modelId)
                                && waiver.modelVersion.equals(version)
                                && waiver.reasonCode.equals(reason)) {
                            matching.add(waiver);
                        }
                    }
                    if (matching.isEmpty()) {
                        remaining.add(reason);
                        continue;
                    }
                    ActiveWaiver selected =
                            matching.stream()
                                    .max(
                                            Comparator.comparing((ActiveWaiver w) -> w.grantAt)
                                                    .thenComparing(w -> w.waiverId))
                                    .orElseThrow();
                    ObjectNode applied = JSON.createObjectNode();
                    applied.put("waiver_id", selected.waiverId);
                    applied.put("model", modelId);
                    applied.put("model_version", version);
                    applied.put("reason", reason);
                    appliedWaivers.add(applied);
                }
                fails = remaining;
            }
            reasons.put(modelId, fails);
        }

        List<String> qualifiers = new ArrayList<>();
        for (Map.Entry<String, List<String>> entry : reasons.entrySet()) {
            if (entry.getValue().isEmpty()) {
                qualifiers.add(entry.getKey());
            }
        }
        qualifiers.sort(
                Comparator.<String>comparingDouble(mid -> evidence.metrics.get(mid)[0])
                        .reversed()
                        .thenComparing(mid -> mid));
        String promoted = qualifiers.isEmpty() ? null : qualifiers.get(0);
        for (String modelId : qualifiers) {
            if (!modelId.equals(promoted)) {
                reasons.get(modelId).add(REASON_TIEBREAK);
            }
        }

        ArrayNode rejected = JSON.createArrayNode();
        for (String modelId : new TreeMap<>(reasons).keySet()) {
            if (modelId.equals(promoted)) {
                continue;
            }
            ObjectNode entry = JSON.createObjectNode();
            entry.put("model", modelId);
            ArrayNode reasonCodes = entry.putArray("reasons");
            reasons.get(modelId).forEach(reasonCodes::add);
            rejected.add(entry);
        }

        conflicts.sort(
                Comparator.comparing((ObjectNode row) -> row.get("model").asText())
                        .thenComparing(row -> row.get("field").asText()));
        appliedWaivers.sort(
                Comparator.comparing((ObjectNode row) -> row.get("model").asText())
                        .thenComparing(row -> row.get("reason").asText())
                        .thenComparing(row -> row.get("waiver_id").asText()));

        ObjectNode manifest = JSON.createObjectNode();
        if (promoted == null) {
            manifest.putNull("promoted");
        } else {
            manifest.put("promoted", promoted);
        }
        manifest.set("rejected", rejected);
        manifest.set("applied_waivers", JSON.valueToTree(appliedWaivers));
        manifest.set("conflicts", JSON.valueToTree(conflicts));
        return manifest;
    }

    private static ObjectNode conflict(
            String model, String field, Object apiValue, Object dbValue) {
        ObjectNode row = JSON.createObjectNode();
        row.put("model", model);
        row.put("field", field);
        row.set("api_value", JSON.valueToTree(apiValue));
        row.set("db_value", JSON.valueToTree(dbValue));
        row.put("canonical_source", "h2");
        return row;
    }

    private static void validateManifest(ObjectNode manifest) throws Exception {
        JsonNode schemaNode = JSON.readTree(Files.readString(SCHEMA_PATH));
        JsonSchema schema = SCHEMA_FACTORY.getSchema(schemaNode);
        Set<ValidationMessage> errors = schema.validate(manifest);
        if (!errors.isEmpty()) {
            throw new IllegalStateException("manifest failed schema validation: " + errors);
        }
    }

    private record LineageKey(String modelId, String modelVersion) {}

    private record ActiveWaiver(
            String waiverId,
            String modelId,
            String modelVersion,
            String reasonCode,
            Instant grantAt) {}

    private record Evidence(
            Map<String, double[]> metrics,
            Map<LineageKey, String> lineage,
            Map<String, Boolean> calibrated,
            List<ActiveWaiver> activeWaivers) {}

    private Reconciler() {}
}
