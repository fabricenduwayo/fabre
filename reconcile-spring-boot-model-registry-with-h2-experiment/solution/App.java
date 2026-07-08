package com.example.reconcile;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
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
import java.time.Duration;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.TreeMap;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * reconcile-model-release: decide which candidate churn model is safe to
 * promote by reconciling the registry API (canonical for the candidate set and
 * identity) against the H2 experiment store (canonical for validation metrics,
 * version-keyed feature-hash lineage, and calibration status), applying the
 * gates documented in /app/policy/promotion-policy.md, and writing the
 * release-decision manifest.
 *
 * <p>Usage: {@code java -jar reconcile-model-release-0.1.0.jar [jdbcUrl] [outputPath]}
 * — both arguments optional, defaulting to the pinned experiment store and
 * /app/build/release-decision.json.
 */
public final class App {

    private static final String DEFAULT_DB_URL = "jdbc:h2:file:/app/experiment-db/experiments";
    private static final String DEFAULT_OUTPUT = "/app/build/release-decision.json";
    private static final String POLICY_PATH = "/app/policy/promotion-policy.md";
    private static final String SCHEMA_PATH = "/app/schemas/release-decision.schema.json";
    private static final String CANDIDATES_URL = "http://localhost:8080/models/candidates";

    private static final String REASON_METRIC = "metric_threshold";
    private static final String REASON_UNCALIBRATED = "uncalibrated";
    private static final String REASON_LINEAGE = "lineage_mismatch";
    private static final String REASON_MISSING = "missing_canonical_evidence";
    private static final String REASON_TIEBREAK = "lost_tiebreak";

    private static final double TOL = 1e-9;

    private record Metrics(double auc, double accuracy) {
    }

    private record Conflict(String model, String field, JsonNode apiValue, JsonNode dbValue) {
    }

    private App() {
    }

    public static void main(String[] args) throws Exception {
        String dbUrl = args.length > 0 ? args[0] : DEFAULT_DB_URL;
        Path outputPath = Path.of(args.length > 1 ? args[1] : DEFAULT_OUTPUT);

        ObjectMapper mapper = new ObjectMapper();

        // Gate 1 thresholds come from the policy document, not from constants.
        String policy = Files.readString(Path.of(POLICY_PATH));
        double aucFloor = policyFloor(policy, "AUC");
        double accuracyFloor = policyFloor(policy, "Accuracy");

        JsonNode candidates = fetchCandidates(mapper);

        Map<String, Metrics> metrics = new HashMap<>();
        Map<String, String> lineage = new HashMap<>();
        Map<String, Boolean> calibrated = new HashMap<>();
        try (Connection connection = DriverManager.getConnection(dbUrl, "sa", "")) {
            try (Statement statement = connection.createStatement();
                 ResultSet rows = statement.executeQuery(
                         "SELECT model_id, auc, accuracy FROM validation_metrics")) {
                while (rows.next()) {
                    metrics.put(rows.getString(1), new Metrics(rows.getDouble(2), rows.getDouble(3)));
                }
            }
            try (Statement statement = connection.createStatement();
                 ResultSet rows = statement.executeQuery(
                         "SELECT model_id, model_version, feature_hash FROM feature_hash_lineage")) {
                while (rows.next()) {
                    lineage.put(rows.getString(1) + "\u0000" + rows.getString(2), rows.getString(3));
                }
            }
            try (Statement statement = connection.createStatement();
                 ResultSet rows = statement.executeQuery(
                         "SELECT model_id, calibrated FROM calibration_status")) {
                while (rows.next()) {
                    calibrated.put(rows.getString(1), rows.getBoolean(2));
                }
            }
        }

        Map<String, List<String>> reasons = new LinkedHashMap<>();
        List<Conflict> conflicts = new ArrayList<>();
        for (JsonNode candidate : candidates) {
            String id = candidate.get("id").asText();
            String version = candidate.get("version").asText();
            String registryHash = candidate.get("featureHash").asText();
            double apiAuc = candidate.get("metrics").get("auc").asDouble();
            double apiAccuracy = candidate.get("metrics").get("accuracy").asDouble();

            Metrics canonical = metrics.get(id);
            Boolean calibratedFlag = calibrated.get(id);
            String canonicalHash = lineage.get(id + "\u0000" + version);

            // Conflicts are recorded per comparable field, H2 canonical.
            if (canonical != null) {
                if (Math.abs(apiAuc - canonical.auc()) > TOL) {
                    conflicts.add(new Conflict(id, "auc",
                            candidate.get("metrics").get("auc"), mapper.getNodeFactory().numberNode(canonical.auc())));
                }
                if (Math.abs(apiAccuracy - canonical.accuracy()) > TOL) {
                    conflicts.add(new Conflict(id, "accuracy",
                            candidate.get("metrics").get("accuracy"), mapper.getNodeFactory().numberNode(canonical.accuracy())));
                }
            }
            if (canonicalHash != null && !canonicalHash.equals(registryHash)) {
                conflicts.add(new Conflict(id, "feature_hash",
                        mapper.getNodeFactory().textNode(registryHash), mapper.getNodeFactory().textNode(canonicalHash)));
            }

            // Evidence completeness gates everything else (fail closed).
            List<String> fails = new ArrayList<>();
            if (canonical == null || calibratedFlag == null || canonicalHash == null) {
                fails.add(REASON_MISSING);
            } else {
                if (canonical.auc() < aucFloor || canonical.accuracy() < accuracyFloor) {
                    fails.add(REASON_METRIC);
                }
                if (!calibratedFlag) {
                    fails.add(REASON_UNCALIBRATED);
                }
                if (!canonicalHash.equals(registryHash)) {
                    fails.add(REASON_LINEAGE);
                }
            }
            reasons.put(id, fails);
        }

        // Tie-break: highest canonical AUC, then lexicographically smallest id.
        List<String> qualifiers = reasons.entrySet().stream()
                .filter(entry -> entry.getValue().isEmpty())
                .map(Map.Entry::getKey)
                .sorted(Comparator.comparingDouble((String id) -> -metrics.get(id).auc())
                        .thenComparing(Comparator.naturalOrder()))
                .toList();
        String promoted = qualifiers.isEmpty() ? null : qualifiers.get(0);
        for (String id : qualifiers) {
            if (!id.equals(promoted)) {
                reasons.get(id).add(REASON_TIEBREAK);
            }
        }

        ObjectNode manifest = mapper.createObjectNode();
        if (promoted == null) {
            manifest.putNull("promoted");
        } else {
            manifest.put("promoted", promoted);
        }
        ArrayNode rejected = manifest.putArray("rejected");
        new TreeMap<>(reasons).forEach((id, fails) -> {
            if (id.equals(promoted)) {
                return;
            }
            ObjectNode entry = rejected.addObject();
            entry.put("model", id);
            ArrayNode reasonsNode = entry.putArray("reasons");
            fails.forEach(reasonsNode::add);
        });
        ArrayNode conflictsNode = manifest.putArray("conflicts");
        conflicts.stream()
                .sorted(Comparator.comparing(Conflict::model).thenComparing(Conflict::field))
                .forEach(conflict -> {
                    ObjectNode entry = conflictsNode.addObject();
                    entry.put("model", conflict.model());
                    entry.put("field", conflict.field());
                    entry.set("api_value", conflict.apiValue());
                    entry.set("db_value", conflict.dbValue());
                    entry.put("canonical_source", "h2");
                });

        // The manifest must conform to the published schema before it ships.
        JsonSchema schema = JsonSchemaFactory.getInstance(SpecVersion.VersionFlag.V202012)
                .getSchema(mapper.readTree(Files.readString(Path.of(SCHEMA_PATH))));
        Set<ValidationMessage> violations = schema.validate(manifest);
        if (!violations.isEmpty()) {
            System.err.println("release-decision manifest failed schema validation: " + violations);
            System.exit(1);
        }

        if (outputPath.getParent() != null) {
            Files.createDirectories(outputPath.getParent());
        }
        Files.writeString(outputPath, mapper.writerWithDefaultPrettyPrinter()
                .writeValueAsString(manifest) + System.lineSeparator());
        System.out.println("release decision written to " + outputPath
                + " (promoted=" + (promoted == null ? "null" : promoted) + ")");
    }

    private static double policyFloor(String policy, String metricLabel) {
        Pattern pattern = Pattern.compile(
                "\\|\\s*" + metricLabel + "\\s*\\|\\s*must be greater than or equal to\\s*([0-9.]+)");
        Matcher matcher = pattern.matcher(policy);
        if (!matcher.find()) {
            throw new IllegalStateException(
                    "promotion policy does not state the " + metricLabel + " floor");
        }
        return Double.parseDouble(matcher.group(1));
    }

    private static JsonNode fetchCandidates(ObjectMapper mapper) throws Exception {
        HttpClient client = HttpClient.newBuilder()
                .connectTimeout(Duration.ofSeconds(5))
                .build();
        HttpRequest request = HttpRequest.newBuilder(URI.create(CANDIDATES_URL))
                .timeout(Duration.ofSeconds(10))
                .GET()
                .build();
        Exception last = null;
        for (int attempt = 0; attempt < 30; attempt++) {
            try {
                HttpResponse<String> response = client.send(request, HttpResponse.BodyHandlers.ofString());
                if (response.statusCode() == 200) {
                    JsonNode body = mapper.readTree(response.body());
                    if (body.isArray()) {
                        return body;
                    }
                }
                last = new IllegalStateException("unexpected candidates response: " + response.statusCode());
            } catch (Exception e) {
                last = e;
            }
            Thread.sleep(2000);
        }
        throw new IllegalStateException("registry API never served /models/candidates", last);
    }
}
