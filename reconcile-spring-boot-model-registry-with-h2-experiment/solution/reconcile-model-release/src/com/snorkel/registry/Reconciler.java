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
import java.util.Objects;
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
                               valid_from, valid_until, replaces_waiver_id,
                               anchors_run_id
                        FROM promotion_waivers
                        """,
                        dbUrl)) {
            waivers.put(row.get("waiver_id"), row);
        }
        Map<String, String> suppressionGroups = new HashMap<>();
        for (Map<String, String> row :
                h2Select(
                        "SELECT waiver_id, suppression_group FROM waiver_suppression_groups",
                        dbUrl)) {
            suppressionGroups.put(row.get("waiver_id"), row.get("suppression_group"));
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
            if (!successor.getOrDefault("anchors_run_id", "").strip()
                    .equals(predecessor.getOrDefault("anchors_run_id", "").strip())) {
                continue;
            }
            if (!Objects.equals(
                    suppressionGroups.get(successor.get("waiver_id")),
                    suppressionGroups.get(predecessor.get("waiver_id")))) {
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
                                parseTimestamp(event.get("occurred_at")),
                                event.get("event_id"),
                                waiver.getOrDefault("anchors_run_id", "").strip(),
                                suppressionGroups.get(waiver.get("waiver_id"))));
            }
        }
        return active;
    }

    private static Map<RoleKey, Instant> reviewerRoleEpochs(String dbUrl, Instant decisionAt)
            throws Exception {
        Map<RoleKey, Map<String, String>> latest = new HashMap<>();
        for (Map<String, String> event :
                h2Select(
                        """
                        SELECT event_id, reviewer_id, reviewer_role, event_type, occurred_at
                        FROM reviewer_role_events
                        """,
                        dbUrl)) {
            Instant occurredAt = parseTimestamp(event.get("occurred_at"));
            if (occurredAt.isAfter(decisionAt)) {
                continue;
            }
            RoleKey key =
                    new RoleKey(event.get("reviewer_id"), event.get("reviewer_role"));
            Map<String, String> current = latest.get(key);
            if (current == null
                    || compareEventOrder(
                                    occurredAt,
                                    event.get("event_id"),
                                    parseTimestamp(current.get("occurred_at")),
                                    current.get("event_id"))
                            > 0) {
                latest.put(key, event);
            }
        }
        Map<RoleKey, Instant> epochs = new HashMap<>();
        for (Map.Entry<RoleKey, Map<String, String>> entry : latest.entrySet()) {
            String eventType = entry.getValue().get("event_type");
            if ("assign".equals(eventType) || "reassign".equals(eventType)) {
                epochs.put(
                        entry.getKey(),
                        parseTimestamp(entry.getValue().get("occurred_at")));
            }
        }
        return epochs;
    }

    private static Set<String> approvalQuorum(
            String dbUrl, List<ActiveWaiver> activeWaivers) throws Exception {
        List<Map<String, String>> contexts =
                h2Select("SELECT context_id, decision_at FROM release_context", dbUrl);
        if (contexts.size() != 1) {
            throw new IllegalStateException("release_context must contain exactly one decision");
        }
        Instant decisionAt = parseTimestamp(contexts.get(0).get("decision_at"));
        Map<String, ActiveWaiver> activeById = new HashMap<>();
        for (ActiveWaiver waiver : activeWaivers) {
            activeById.put(waiver.waiverId, waiver);
        }
        Map<RoleKey, Instant> roleEpochs = reviewerRoleEpochs(dbUrl, decisionAt);

        Map<ApprovalReviewKey, Map<String, String>> latest = new HashMap<>();
        for (Map<String, String> event :
                h2Select(
                        """
                        SELECT event_id, waiver_id, reviewer_id, reviewer_role,
                               event_type, occurred_at
                        FROM waiver_approval_events
                        """,
                        dbUrl)) {
            ActiveWaiver waiver = activeById.get(event.get("waiver_id"));
            if (waiver == null) {
                continue;
            }
            Instant occurredAt = parseTimestamp(event.get("occurred_at"));
            if (occurredAt.isAfter(decisionAt)
                    || compareEventOrder(
                                    occurredAt,
                                    event.get("event_id"),
                                    waiver.grantAt,
                                    waiver.grantEventId)
                            <= 0) {
                continue;
            }
            ApprovalReviewKey key =
                    new ApprovalReviewKey(
                            event.get("waiver_id"),
                            event.get("reviewer_id"),
                            event.get("reviewer_role"));
            Map<String, String> current = latest.get(key);
            if (current == null
                    || compareEventOrder(
                                    occurredAt,
                                    event.get("event_id"),
                                    parseTimestamp(current.get("occurred_at")),
                                    current.get("event_id"))
                            > 0) {
                latest.put(key, event);
            }
        }

        Map<String, Map<String, Set<String>>> reviewers = new HashMap<>();
        for (Map<String, String> event : latest.values()) {
            if (!"approve".equals(event.get("event_type"))) {
                continue;
            }
            RoleKey roleKey =
                    new RoleKey(event.get("reviewer_id"), event.get("reviewer_role"));
            Instant epochStart = roleEpochs.get(roleKey);
            if (epochStart == null
                    || !parseTimestamp(event.get("occurred_at")).isAfter(epochStart)) {
                continue;
            }
            reviewers
                    .computeIfAbsent(event.get("waiver_id"), ignored -> new HashMap<>())
                    .computeIfAbsent(event.get("reviewer_role"), ignored -> new HashSet<>())
                    .add(event.get("reviewer_id"));
        }

        Set<String> approved = new HashSet<>();
        for (Map.Entry<String, Map<String, Set<String>>> entry : reviewers.entrySet()) {
            Set<String> risk =
                    entry.getValue().getOrDefault("risk", Set.of());
            Set<String> owners =
                    entry.getValue().getOrDefault("model_owner", Set.of());
            boolean distinct = false;
            for (String riskReviewer : risk) {
                for (String ownerReviewer : owners) {
                    if (!riskReviewer.equals(ownerReviewer)) {
                        distinct = true;
                    }
                }
            }
            if (distinct) {
                approved.add(entry.getKey());
            }
        }
        return approved;
    }

    private static int compareEventOrder(
            Instant leftAt, String leftId, Instant rightAt, String rightId) {
        int timeComparison = leftAt.compareTo(rightAt);
        return timeComparison != 0 ? timeComparison : leftId.compareTo(rightId);
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
        Map<String, String> supersedesByRun = new HashMap<>();
        for (Map<String, String> row : runs) {
            String supersedes = row.getOrDefault("supersedes_run_id", "").strip();
            if (!supersedes.isEmpty()) {
                voided.add(supersedes);
                supersedesByRun.put(row.get("run_id"), supersedes);
            }
        }
        boolean changed = true;
        while (changed) {
            changed = false;
            for (Map.Entry<String, String> entry : supersedesByRun.entrySet()) {
                if (voided.contains(entry.getKey())
                        && !entry.getValue().isEmpty()
                        && voided.add(entry.getValue())) {
                    changed = true;
                }
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
        Map<String, String> metricCapturedAt = new HashMap<>();
        Map<String, String> operativeRunIds = new HashMap<>();
        Map<String, String> runModelIds = new HashMap<>();
        Map<String, String> runCapturedAt = new HashMap<>();
        for (Map<String, String> row :
                h2Select(
                        "SELECT run_id, model_id, captured_at FROM validation_runs", dbUrl)) {
            runModelIds.put(row.get("run_id"), row.get("model_id"));
            runCapturedAt.put(row.get("run_id"), row.get("captured_at"));
        }
        for (Map.Entry<String, Map<String, String>> entry : latestByModel.entrySet()) {
            Map<String, String> row = entry.getValue();
            metrics.put(
                    entry.getKey(),
                    new double[] {
                        Double.parseDouble(row.get("auc")),
                        Double.parseDouble(row.get("accuracy"))
                    });
            metricCapturedAt.put(entry.getKey(), row.get("captured_at"));
            operativeRunIds.put(entry.getKey(), row.get("run_id"));
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
        List<Map<String, String>> contexts =
                h2Select("SELECT context_id, decision_at FROM release_context", dbUrl);
        if (contexts.size() != 1) {
            throw new IllegalStateException("release_context must contain exactly one decision");
        }
        Instant decisionAt = parseTimestamp(contexts.get(0).get("decision_at"));
        Map<String, Boolean> snapshot = new HashMap<>();
        for (Map<String, String> row :
                h2Select("SELECT model_id, calibrated FROM calibration_status", dbUrl)) {
            String flag = row.get("calibrated").strip().toUpperCase();
            snapshot.put(
                    row.get("model_id"),
                    flag.equals("TRUE") || flag.equals("1") || flag.equals("T"));
        }
        Map<String, List<Map<String, String>>> eventsByModel = new HashMap<>();
        for (Map<String, String> row :
                h2Select(
                        "SELECT event_id, model_id, event_type, occurred_at FROM calibration_events",
                        dbUrl)) {
            if (parseTimestamp(row.get("occurred_at")).isAfter(decisionAt)) {
                continue;
            }
            eventsByModel.computeIfAbsent(row.get("model_id"), ignored -> new ArrayList<>())
                    .add(row);
        }
        for (Map.Entry<String, Boolean> entry : snapshot.entrySet()) {
            boolean effective = entry.getValue();
            Instant cutoff = decisionAt;
            String operativeCapturedAt = metricCapturedAt.get(entry.getKey());
            if (operativeCapturedAt != null) {
                Instant operativeAt = parseTimestamp(operativeCapturedAt);
                if (operativeAt.isBefore(cutoff)) {
                    cutoff = operativeAt;
                }
            }
            List<Map<String, String>> events =
                    new ArrayList<>(eventsByModel.getOrDefault(entry.getKey(), List.of()));
            events.sort(
                    Comparator.comparing((Map<String, String> row) ->
                                    parseTimestamp(row.get("occurred_at")))
                            .thenComparing(row -> row.get("event_id")));
            for (Map<String, String> event : events) {
                if (parseTimestamp(event.get("occurred_at")).isAfter(cutoff)) {
                    continue;
                }
                effective = "calibrate".equals(event.get("event_type"));
            }
            calibrated.put(entry.getKey(), effective);
        }
        List<ActiveWaiver> waivers = activeWaivers(dbUrl);
        return new Evidence(
                metrics,
                metricCapturedAt,
                operativeRunIds,
                runModelIds,
                runCapturedAt,
                lineage,
                calibrated,
                waivers,
                approvalQuorum(dbUrl, waivers));
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

                String operativeCapturedAt = evidence.metricCapturedAt.get(modelId);
                String operativeRunId = evidence.operativeRunIds.get(modelId);
                Instant operativeAt =
                        operativeCapturedAt == null
                                ? null
                                : parseTimestamp(operativeCapturedAt);
                Map<String, List<ActiveWaiver>> eligibleByReason = new LinkedHashMap<>();
                for (String reason : fails) {
                    List<ActiveWaiver> matching = new ArrayList<>();
                    for (ActiveWaiver waiver : evidence.activeWaivers) {
                        if (!waiver.modelId.equals(modelId)
                                || !waiver.modelVersion.equals(version)
                                || !waiver.reasonCode.equals(reason)
                                || !evidence.approvedWaiverIds.contains(waiver.waiverId)) {
                            continue;
                        }
                        Instant timingAt = operativeAt;
                        if (!waiver.anchorsRunId.isEmpty()) {
                            if (!REASON_METRIC.equals(reason)) {
                                continue;
                            }
                            if (!modelId.equals(evidence.runModelIds.get(waiver.anchorsRunId))) {
                                continue;
                            }
                            if (!waiver.anchorsRunId.equals(operativeRunId)) {
                                continue;
                            }
                            String anchorCaptured =
                                    evidence.runCapturedAt.get(waiver.anchorsRunId);
                            timingAt =
                                    anchorCaptured == null
                                            ? null
                                            : parseTimestamp(anchorCaptured);
                        }
                        if (timingAt != null && !waiver.grantAt.isBefore(timingAt)) {
                            continue;
                        }
                        matching.add(waiver);
                    }
                    eligibleByReason.put(reason, matching);
                }

                Map<String, ActiveWaiver> groupWinners = new HashMap<>();
                for (List<ActiveWaiver> matching : eligibleByReason.values()) {
                    for (ActiveWaiver waiver : matching) {
                        if (waiver.suppressionGroup == null) {
                            continue;
                        }
                        ActiveWaiver current = groupWinners.get(waiver.suppressionGroup);
                        if (current == null
                                || Comparator.comparing((ActiveWaiver w) -> w.grantAt)
                                                .thenComparing(w -> w.waiverId)
                                                .compare(waiver, current)
                                        > 0) {
                            groupWinners.put(waiver.suppressionGroup, waiver);
                        }
                    }
                }

                List<String> remaining = new ArrayList<>();
                for (String reason : fails) {
                    List<ActiveWaiver> matching =
                            eligibleByReason.get(reason).stream()
                                    .filter(
                                            waiver ->
                                                    waiver.suppressionGroup == null
                                                            || groupWinners.get(
                                                                            waiver.suppressionGroup)
                                                                    == waiver)
                                    .toList();
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
            Instant grantAt,
            String grantEventId,
            String anchorsRunId,
            String suppressionGroup) {}

    private record Evidence(
            Map<String, double[]> metrics,
            Map<String, String> metricCapturedAt,
            Map<String, String> operativeRunIds,
            Map<String, String> runModelIds,
            Map<String, String> runCapturedAt,
            Map<LineageKey, String> lineage,
            Map<String, Boolean> calibrated,
            List<ActiveWaiver> activeWaivers,
            Set<String> approvedWaiverIds) {}

    private record RoleKey(String reviewerId, String reviewerRole) {}

    private record ApprovalReviewKey(
            String waiverId, String reviewerId, String reviewerRole) {}

    private Reconciler() {}
}
