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

    private static final String NORMATIVE_C =
            "## Appendix C — Normative cryptographic exception precedence";
    private static final String NORMATIVE_D =
            "## Appendix D — Registered nonce overrides";

    private static final Pattern KEY_PREC = Pattern.compile(
            "```json\\s*\\[\"rotation_replacement\", \"latest_key_assigned\"\\]\\s*```");
    private static final Pattern NONCE_PREC = Pattern.compile(
            "```json\\s*\\[\"report_override\", \"db_override\", \"derived_sha256_prefix\"\\]\\s*```");
    private static final Pattern DERIVED_RULE = Pattern.compile(
            "The derived-nonce rule in prose: ([^.]+)\\.");
    private static final Pattern REVIEW_DATE = Pattern.compile(
            "## Findings overview\\s*\\n\\s*\\nReview date: (\\d{4}-\\d{2}-\\d{2})\\.");
    private static final Pattern NONCE_OVERRIDE = Pattern.compile(
            "The operative nonce override for (frm-\\d{3}) is `([0-9A-F]{24})`\\.");

    static void run() throws Exception {
        String text = Files.readString(REPORT);
        String appendixC = slice(text, NORMATIVE_C,
                "## Appendix D (draft", NORMATIVE_D);
        String appendixD = slice(text, NORMATIVE_D,
                "## Appendix D — Post-review errata");

        Matcher rd = REVIEW_DATE.matcher(text);
        if (!rd.find()) {
            throw new IllegalStateException("review date not found in report");
        }

        if (!KEY_PREC.matcher(appendixC).find()) {
            throw new IllegalStateException("key precedence block missing");
        }
        if (!NONCE_PREC.matcher(appendixC).find()) {
            throw new IllegalStateException("nonce precedence block missing");
        }

        Matcher dr = DERIVED_RULE.matcher(appendixC);
        if (!dr.find()) {
            throw new IllegalStateException("derived nonce rule missing");
        }

        Map<String, Object> rules = new LinkedHashMap<>();
        rules.put("review_date", rd.group(1));
        rules.put("key_selection_precedence", List.of(
                "rotation_replacement", "latest_key_assigned"));
        rules.put("nonce_selection_precedence", List.of(
                "report_override", "db_override", "derived_sha256_prefix"));
        rules.put("derived_nonce_rule", dr.group(1).trim());

        Map<String, String> overrides = new LinkedHashMap<>();
        Matcher nov = NONCE_OVERRIDE.matcher(appendixD);
        while (nov.find()) {
            overrides.put(nov.group(1), nov.group(2));
        }
        rules.put("nonce_overrides", overrides);

        Json.writeMap(OUT, rules);
        System.out.println("rules: wrote exception register to " + OUT);
    }

    private static String slice(String text, String startMarker, String... endMarkers) {
        int start = text.indexOf(startMarker);
        if (start < 0) {
            throw new IllegalStateException(startMarker + " missing");
        }
        int end = text.length();
        for (String marker : endMarkers) {
            int pos = text.indexOf(marker, start + startMarker.length());
            if (pos >= 0 && pos < end) {
                end = pos;
            }
        }
        return text.substring(start, end);
    }

    private RuleExtractor() {}
}
