package com.mariner.forensic;

import java.nio.file.Files;
import java.nio.file.Path;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.ResultSet;
import java.sql.Statement;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.LinkedHashMap;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * Milestone 1 — extract cryptographic exception rules from the forensic report.
 */
final class RuleExtractor {
    private static final Path REPORT =
            Path.of("/app/reports/mariner-aes-gcm-forensic-review.md");
    private static final Path CRYPTO_CONFIG = Path.of("/app/config/crypto.toml");
    private static final Path OUT = Path.of("/app/out/rules.json");
    private static final String JDBC = "jdbc:sqlite:/app/data/forensic_audit.db";

    private static final Pattern DECISION_CANDIDATE = Pattern.compile(
            "(?m)^Decision candidate ([A-Z0-9-]+)\\s*"
                    + "\\| family=(key_selection|nonce_selection)\\s*"
                    + "\\| rank=(\\d+)\\s*\\| token=([a-z0-9_]+)\\s*$");
    private static final Pattern CANDIDATE_STATUS = Pattern.compile(
            "(?m)^Candidate status [A-Z0-9-]+\\s*\\| target=([A-Z0-9-]+)\\s*"
                    + "\\| disposition=(accepted|superseded|withdrawn|rejected)\\s*"
                    + "\\| revision=([A-Z0-9-]+)\\s*$");
    private static final Pattern REVISION_LINK = Pattern.compile(
            "(?m)^Revision link [A-Z0-9-]+\\s*\\| revision=([A-Z0-9-]+)\\s*"
                    + "\\| incorporated_by=([A-Z0-9-]+)\\s*\\| signature=[^\\n]+$");
    private static final Pattern EXCEPTION_CANDIDATE = Pattern.compile(
            "(?m)^Exception candidate ([A-Z0-9-]+)\\s*"
                    + "\\| frame=(frm-[0-9]{3})\\s*\\| evidence=[^\\n]+$");
    private static final Pattern BOARD_DISPOSITION = Pattern.compile(
            "(?m)^Board disposition [A-Z0-9-]+\\s*\\| target=([A-Z0-9-]+)\\s*"
                    + "\\| decision=(accepted|superseded|withdrawn|rejected)\\s*"
                    + "\\| docket=([A-Z0-9-]+)(?:\\s*\\|[^\\n]+)?$");
    private static final Pattern BOARD_RATIFICATION = Pattern.compile(
            "(?m)^Board ratification [A-Z0-9-]+\\s*\\| docket=([A-Z0-9-]+)\\s*"
                    + "\\| incorporated_by=([A-Z0-9-]+)\\s*\\| signature=[^\\n]+$");
    private static final Pattern DERIVED_RULE_CONFIG = Pattern.compile(
            "(?m)^derived_nonce_rule\\s*=\\s*\"([^\"]+)\"");
    private static final Pattern REVIEW_DATE = Pattern.compile(
            "## Findings overview\\s*\\n\\s*\\nReview date: (\\d{4}-\\d{2}-\\d{2})\\.");
    private static final Pattern REVIEW_ID = Pattern.compile(
            "The approved review is (FND-[0-9]+)\\.");

    static void run() throws Exception {
        String text = Files.readString(REPORT);

        Matcher rd = REVIEW_DATE.matcher(text);
        if (!rd.find()) {
            throw new IllegalStateException("review date not found in report");
        }
        Matcher review = REVIEW_ID.matcher(text);
        if (!review.find()) {
            throw new IllegalStateException("approved review identifier missing");
        }
        String reviewId = review.group(1);

        Map<String, List<RankedRule>> precedence =
                parsePrecedence(text, reviewId);
        Set<String> reportMembers = parseReportMembers(text, reviewId);

        Matcher dr = DERIVED_RULE_CONFIG.matcher(Files.readString(CRYPTO_CONFIG));
        if (!dr.find()) {
            throw new IllegalStateException("derived nonce rule missing");
        }

        Map<String, Object> rules = new LinkedHashMap<>();
        rules.put("review_date", rd.group(1));
        rules.put("key_selection_precedence", tokens(precedence, "key_selection"));
        rules.put("nonce_selection_precedence", tokens(precedence, "nonce_selection"));
        rules.put("derived_nonce_rule", dr.group(1).trim());
        rules.put("nonce_overrides", loadReportOverrides(reportMembers));

        Json.writeMap(OUT, rules);
        System.out.println("rules: wrote exception register to " + OUT);
    }

    private record RankedRule(int priority, String token) {}

    private record DecisionCandidate(String family, int rank, String token) {}

    private static Map<String, List<RankedRule>> parsePrecedence(
            String text, String reviewId) {
        Map<String, DecisionCandidate> candidates = new LinkedHashMap<>();
        Matcher candidateMatcher = DECISION_CANDIDATE.matcher(text);
        while (candidateMatcher.find()) {
            candidates.put(
                    candidateMatcher.group(1),
                    new DecisionCandidate(
                            candidateMatcher.group(2),
                            Integer.parseInt(candidateMatcher.group(3)),
                            candidateMatcher.group(4)));
        }

        Set<String> incorporatedRevisions = new LinkedHashSet<>();
        Matcher revisionMatcher = REVISION_LINK.matcher(text);
        while (revisionMatcher.find()) {
            if (reviewId.equals(revisionMatcher.group(2))) {
                incorporatedRevisions.add(revisionMatcher.group(1));
            }
        }
        if (incorporatedRevisions.isEmpty()) {
            throw new IllegalStateException("no signed revisions incorporated by " + reviewId);
        }

        Set<String> activeCandidateIds = new LinkedHashSet<>();
        Matcher statusMatcher = CANDIDATE_STATUS.matcher(text);
        while (statusMatcher.find()) {
            String candidateId = statusMatcher.group(1);
            String disposition = statusMatcher.group(2);
            String revision = statusMatcher.group(3);
            if (!incorporatedRevisions.contains(revision)) {
                continue;
            }
            if ("accepted".equals(disposition)) {
                activeCandidateIds.add(candidateId);
            } else {
                activeCandidateIds.remove(candidateId);
            }
        }

        Map<String, List<RankedRule>> byFamily = new LinkedHashMap<>();
        for (String candidateId : activeCandidateIds) {
            DecisionCandidate candidate = candidates.get(candidateId);
            if (candidate == null) {
                throw new IllegalStateException(
                        "status references missing decision candidate " + candidateId);
            }
            byFamily.computeIfAbsent(candidate.family(), ignored -> new ArrayList<>())
                    .add(new RankedRule(candidate.rank(), candidate.token()));
        }
        if (byFamily.isEmpty()) {
            throw new IllegalStateException("no operative precedence candidates resolved");
        }
        byFamily.values().forEach(
                rules -> rules.sort(Comparator.comparingInt(RankedRule::priority)));
        return byFamily;
    }

    private static List<String> tokens(
            Map<String, List<RankedRule>> precedence, String family) {
        List<RankedRule> rules = precedence.get(family);
        if (rules == null || rules.isEmpty()) {
            throw new IllegalStateException("missing precedence family " + family);
        }
        return rules.stream().map(RankedRule::token).toList();
    }

    private static Set<String> parseReportMembers(String text, String reviewId) {
        Map<String, String> candidateFrames = new LinkedHashMap<>();
        Matcher candidateMatcher = EXCEPTION_CANDIDATE.matcher(text);
        while (candidateMatcher.find()) {
            candidateFrames.put(candidateMatcher.group(1), candidateMatcher.group(2));
        }

        Set<String> ratifiedDockets = new LinkedHashSet<>();
        Matcher ratificationMatcher = BOARD_RATIFICATION.matcher(text);
        while (ratificationMatcher.find()) {
            if (reviewId.equals(ratificationMatcher.group(2))) {
                ratifiedDockets.add(ratificationMatcher.group(1));
            }
        }
        if (ratifiedDockets.isEmpty()) {
            throw new IllegalStateException("no exception docket ratified by " + reviewId);
        }

        Set<String> admittedCandidateIds = new LinkedHashSet<>();
        Matcher dispositionMatcher = BOARD_DISPOSITION.matcher(text);
        while (dispositionMatcher.find()) {
            String candidateId = dispositionMatcher.group(1);
            String decision = dispositionMatcher.group(2);
            String docket = dispositionMatcher.group(3);
            if (!ratifiedDockets.contains(docket)) {
                continue;
            }
            if ("accepted".equals(decision)) {
                admittedCandidateIds.add(candidateId);
            } else {
                admittedCandidateIds.remove(candidateId);
            }
        }

        Set<String> members = new LinkedHashSet<>();
        for (String candidateId : admittedCandidateIds) {
            String frameId = candidateFrames.get(candidateId);
            if (frameId == null) {
                throw new IllegalStateException(
                        "disposition references missing exception candidate " + candidateId);
            }
            members.add(frameId);
        }
        if (members.isEmpty()) {
            throw new IllegalStateException("no report override membership resolved");
        }
        return members;
    }

    private static Map<String, String> loadReportOverrides(Set<String> members)
            throws Exception {
        Map<String, String> overrides = new LinkedHashMap<>();
        try (Connection conn = DriverManager.getConnection(JDBC);
                Statement stmt = conn.createStatement();
                ResultSet rs = stmt.executeQuery(
                        "SELECT frame_id, nonce_hex FROM report_nonce_overrides "
                                + "ORDER BY frame_id")) {
            while (rs.next()) {
                String frameId = rs.getString("frame_id");
                if (members.contains(frameId)) {
                    overrides.put(frameId, rs.getString("nonce_hex"));
                }
            }
        }
        if (!overrides.keySet().equals(members)) {
            throw new IllegalStateException(
                    "report membership and report_nonce_overrides rows differ");
        }
        return overrides;
    }

    private RuleExtractor() {}
}
