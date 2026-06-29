package com.mariner.audit;

import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.TreeMap;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * Milestone 1 — decode the waiver register from the narrative report.
 *
 * The decisive facts live in two consistent forms: the per-service dossier
 * headers in Appendix A (which enumerate every in-scope service) and the
 * chronological grant / rescission lines in Appendix B (which carry each
 * waiver's type, scope, and dates). A waiver that is granted and later
 * rescinded nets out to a revoked status; a service that never appears in the
 * register has no waiver.
 */
final class WaiverDecoder {
    private static final Path REPORT = Path.of("/app/reports/mariner-tls-waiver-review.md");
    private static final Path OUT = Path.of("/app/out/waivers.json");

    private static final Pattern DOSSIER =
            Pattern.compile("(?m)^###\\s+(svc-\\d{3})\\s+\\u2014\\s+(\\S+)\\s*$");
    private static final Pattern GRANT = Pattern.compile(
            "(?m)^- (\\d{4}-\\d{2}-\\d{2}): (WV-\\S+) granted to .+? \\((svc-\\d{3})\\) "
            + "\\u2014 (transport-protocol|mutual-TLS|certificate-chain) exception, "
            + "scope (all|prod|staging|dev), nominal expiry (\\d{4}-\\d{2}-\\d{2})\\.");
    private static final Pattern RESCIND = Pattern.compile(
            "(?m)^- (\\d{4}-\\d{2}-\\d{2}): (WV-\\S+) for .+? \\((svc-\\d{3})\\) RESCINDED");

    private static final Map<String, String> TYPE = Map.of(
            "transport-protocol", "tls",
            "mutual-TLS", "mtls",
            "certificate-chain", "chain");

    static void run() throws Exception {
        String text = Files.readString(REPORT);

        // Every in-scope service, in inventory order.
        Map<String, String> names = new LinkedHashMap<>();
        Matcher d = DOSSIER.matcher(text);
        while (d.find()) {
            names.putIfAbsent(d.group(1), d.group(2));
        }

        // Grants, then rescissions layered on top. A service can appear more
        // than once if an older waiver was rescinded and a replacement was
        // later granted, so rescissions must match the current waiver ID.
        Map<String, Map<String, Object>> waivers = new TreeMap<>();
        Matcher g = GRANT.matcher(text);
        while (g.find()) {
            Map<String, Object> w = new LinkedHashMap<>();
            w.put("granted_on", g.group(1));
            w.put("waiver_id", g.group(2));
            w.put("waiver_type", TYPE.get(g.group(4)));
            w.put("scope", g.group(5));
            w.put("expires_on", g.group(6));
            w.put("status", "granted");
            w.put("revoked_on", null);
            waivers.put(g.group(3), w);
        }
        Matcher r = RESCIND.matcher(text);
        while (r.find()) {
            Map<String, Object> w = waivers.get(r.group(3));
            if (w != null && r.group(2).equals(w.get("waiver_id"))) {
                w.put("status", "revoked");
                w.put("revoked_on", r.group(1));
            }
        }

        List<Map<String, Object>> out = new ArrayList<>();
        for (String sid : new TreeMap<>(names).keySet()) {
            Map<String, Object> rec = new LinkedHashMap<>();
            rec.put("service_id", sid);
            rec.put("service_name", names.get(sid));
            Map<String, Object> w = waivers.get(sid);
            if (w == null) {
                rec.put("waiver_id", null);
                rec.put("waiver_type", "none");
                rec.put("status", "none");
                rec.put("scope", null);
                rec.put("granted_on", null);
                rec.put("expires_on", null);
                rec.put("revoked_on", null);
            } else {
                rec.put("waiver_id", w.get("waiver_id"));
                rec.put("waiver_type", w.get("waiver_type"));
                rec.put("status", w.get("status"));
                rec.put("scope", w.get("scope"));
                rec.put("granted_on", w.get("granted_on"));
                rec.put("expires_on", w.get("expires_on"));
                rec.put("revoked_on", w.get("revoked_on"));
            }
            out.add(rec);
        }

        Json.writeList(OUT, out);
        System.out.println("decode: wrote " + out.size() + " waiver records to " + OUT);
    }

    private WaiverDecoder() {}
}
