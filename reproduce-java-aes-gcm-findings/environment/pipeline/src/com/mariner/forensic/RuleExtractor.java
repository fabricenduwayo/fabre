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
    private static final String ERRATA_D =
            "## Appendix D — Post-review errata";

    private static final Pattern KEY_PREC_PROSE = Pattern.compile(
            "rotation_replacement is tried first;\\s*latest_key_assigned applies only");
    private static final Pattern NONCE_PREC_PROSE = Pattern.compile(
            "report_override \\(Appendix D bytes verbatim when\\s*"
            + "present for the frame\\), db_override \\(surviving chain under C\\.5 scoped to the\\s*"
            + "operative key version\\), derived_sha256_prefix");
    private static final Pattern REVIEW_DATE = Pattern.compile(
            "Review date: (\\d{4}-\\d{2}-\\d{2})\\.");
    private static final Pattern NONCE_OVERRIDE = Pattern.compile(
            "The operative nonce override for (frm-\\d{3}) is `([0-9A-F]{24})`\\.");

    static void run() throws Exception {
        String text = Files.readString(REPORT);
        String appendixC = slice(text, NORMATIVE_C,
                "## Appendix D (draft", NORMATIVE_D);
        String appendixD = slice(text, NORMATIVE_D, ERRATA_D);

        Matcher rd = REVIEW_DATE.matcher(text);
        if (!rd.find()) {
            throw new IllegalStateException("review date not found in report");
        }

        if (!KEY_PREC_PROSE.matcher(appendixC).find()) {
            throw new IllegalStateException("key precedence prose missing");
        }
        if (!NONCE_PREC_PROSE.matcher(appendixC).find()) {
            throw new IllegalStateException("nonce precedence prose missing");
        }

        Map<String, Object> rules = new LinkedHashMap<>();
        rules.put("review_date", rd.group(1));
        rules.put("key_selection_precedence", List.of(
                "latest_key_assigned", "rotation_replacement"));
        rules.put("nonce_selection_precedence", List.of(
                "report_override", "derived_sha256_prefix"));
        rules.put("derived_nonce_rule",
                "SHA-256(frame_id + ':' + key_version), first 12 bytes");

        Map<String, String> overrides = new LinkedHashMap<>();
        Matcher nov = NONCE_OVERRIDE.matcher(appendixD);
        while (nov.find()) {
            overrides.putIfAbsent(nov.group(1), nov.group(2));
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
