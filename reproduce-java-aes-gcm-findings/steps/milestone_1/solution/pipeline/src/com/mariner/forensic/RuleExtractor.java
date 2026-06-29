package com.mariner.forensic;

import java.nio.file.Files;
import java.nio.file.Path;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * Milestone 1 — extract cryptographic exception rules from the forensic report.
 */
final class RuleExtractor {
    private static final Path REPORT =
            Path.of("/app/reports/mariner-aes-gcm-forensic-review.md");
    private static final Path OUT = Path.of("/app/out/rules.json");

    private static final Pattern KEY_PREC = Pattern.compile(
            "```json\\s*\\[\"rotation_replacement\", \"latest_key_assigned\"\\]\\s*```");
    private static final Pattern NONCE_PREC = Pattern.compile(
            "```json\\s*\\[\"report_override\", \"derived_sha256_prefix\"\\]\\s*```");
    private static final Pattern DERIVED_RULE = Pattern.compile(
            "The derived-nonce rule in prose: ([^.]+)\\.");
    private static final Pattern REVIEW_DATE = Pattern.compile(
            "Review date: (\\d{4}-\\d{2}-\\d{2})\\.");
    private static final Pattern NONCE_OVERRIDE = Pattern.compile(
            "The operative nonce override for (frm-\\d{3}) is `([0-9A-F]{24})`\\.");

    static void run() throws Exception {
        String text = Files.readString(REPORT);

        Matcher rd = REVIEW_DATE.matcher(text);
        if (!rd.find()) {
            throw new IllegalStateException("review date not found in report");
        }

        if (!KEY_PREC.matcher(text).find()) {
            throw new IllegalStateException("key precedence block missing");
        }
        if (!NONCE_PREC.matcher(text).find()) {
            throw new IllegalStateException("nonce precedence block missing");
        }

        Matcher dr = DERIVED_RULE.matcher(text);
        if (!dr.find()) {
            throw new IllegalStateException("derived nonce rule missing");
        }

        Map<String, Object> rules = new LinkedHashMap<>();
        rules.put("review_date", rd.group(1));
        rules.put("key_selection_precedence", List.of(
                "rotation_replacement", "latest_key_assigned"));
        rules.put("nonce_selection_precedence", List.of(
                "report_override", "derived_sha256_prefix"));
        rules.put("derived_nonce_rule", dr.group(1).trim());

        Map<String, String> overrides = new LinkedHashMap<>();
        Matcher nov = NONCE_OVERRIDE.matcher(text);
        while (nov.find()) {
            overrides.put(nov.group(1), nov.group(2));
        }
        rules.put("nonce_overrides", overrides);

        Json.writeMap(OUT, rules);
        System.out.println("rules: wrote exception register to " + OUT);
    }

    private RuleExtractor() {}
}
