package com.mariner.audit;

import com.fasterxml.jackson.databind.JsonNode;
import com.networknt.schema.JsonSchema;
import com.networknt.schema.JsonSchemaFactory;
import com.networknt.schema.SpecVersion;
import com.networknt.schema.ValidationMessage;

import java.nio.file.Path;
import java.time.LocalDate;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;

/**
 * Milestone 3 — validate config and emit final findings.
 */
final class FindingsEngine {
    private static final Path POLICY = Path.of("/app/config/policy.yaml");
    private static final Path CRYPTO = Path.of("/app/config/crypto.toml");
    private static final Path EVIDENCE = Path.of("/app/out/evidence.json");
    private static final Path OUT = Path.of("/app/out/findings.json");
    private static final Path SCHEMA_DIR = Path.of("/app/schema");

    private static final JsonSchemaFactory FACTORY =
            JsonSchemaFactory.getInstance(SpecVersion.VersionFlag.V202012);

    private record Finding(String disposition, String reason, boolean waiverApplied) {}

    static void run() throws Exception {
        JsonNode policy = Json.readYaml(POLICY);
        validate("policy.schema.json", policy, "policy.yaml");
        JsonNode crypto = Json.readToml(CRYPTO);
        validate("crypto.schema.json", crypto, "crypto.toml");

        LocalDate review = LocalDate.parse(policy.get("review_date").asText());
        LocalDate windowEnd = review.plusDays(policy.get("rotation_window_days").asInt());
        Set<String> allowedTls = asSet(policy.get("allowed_tls_versions"));
        Set<String> mtlsEnvs = asSet(policy.get("mtls_required_environments"));
        Set<String> trusted = asSet(crypto.get("trusted_issuers"));
        int minRsa = crypto.get("keys").get("min_rsa_bits").asInt();
        int minEc = crypto.get("keys").get("min_ec_bits").asInt();

        List<Map<String, Object>> out = new ArrayList<>();
        for (Map<String, Object> e : Json.readList(EVIDENCE)) {
            Finding f = decide(e, review, windowEnd, allowedTls, mtlsEnvs, trusted, minRsa, minEc);
            Map<String, Object> rec = new LinkedHashMap<>();
            rec.put("service_id", e.get("service_id"));
            rec.put("service_name", e.get("service_name"));
            rec.put("environment", e.get("environment"));
            rec.put("disposition", f.disposition());
            rec.put("reason_code", f.reason());
            rec.put("waiver_applied", f.waiverApplied());
            out.add(rec);
        }

        validate("findings.schema.json", Json.JSON.valueToTree(out), "findings.json");
        Json.writeList(OUT, out);
        System.out.println("validate: wrote " + out.size() + " findings to " + OUT);
    }

    private static Finding decide(
            Map<String, Object> e, LocalDate review, LocalDate windowEnd,
            Set<String> allowedTls, Set<String> mtlsEnvs, Set<String> trusted,
            int minRsa, int minEc) {

        String env = str(e, "environment");
        String waiverType = str(e, "waiver_type");
        String waiverStatus = str(e, "waiver_status");
        String scope = str(e, "waiver_scope");
        String expires = str(e, "waiver_expires_on");

        boolean wActive = "granted".equals(waiverStatus)
                && expires != null && !LocalDate.parse(expires).isBefore(review);
        boolean wExpiringSoon = wActive && !LocalDate.parse(expires).isAfter(windowEnd);

        boolean vFp = !str(e, "probe_observed_fingerprint").equals(str(e, "cert_fingerprint"));

        String violation = null;
        if (!allowedTls.contains(str(e, "probe_tls_version"))) {
            violation = "tls";
        } else if (mtlsEnvs.contains(env) && !bool(e, "probe_mtls_presented")) {
            violation = "mtls";
        } else if (!bool(e, "probe_chain_valid")) {
            violation = "chain";
        }

        if (vFp) {
            return new Finding("deny", "fingerprint_mismatch", false);
        }

        boolean covered = false;
        if (violation != null) {
            covered = wActive && waiverType.equals(violation)
                    && ("all".equals(scope) || env.equals(scope));
            if (!covered) {
                if (waiverType.equals(violation) && "granted".equals(waiverStatus) && !wActive) {
                    return new Finding("deny", "waiver_expired", false);
                }
                if (waiverType.equals(violation) && "revoked".equals(waiverStatus)) {
                    return new Finding("deny", "waiver_revoked", false);
                }
                return new Finding("deny", reasonForViolation(violation), false);
            }
        }

        LocalDate notAfter = LocalDate.parse(str(e, "cert_not_after"));
        boolean nearExpiry = !notAfter.isBefore(review) && !notAfter.isAfter(windowEnd);
        int minBits = "RSA".equals(str(e, "cert_key_algo")) ? minRsa : minEc;
        boolean weakKey = ((Number) e.get("cert_key_bits")).intValue() < minBits;
        boolean untrusted = !trusted.contains(str(e, "cert_issuer"));

        if (nearExpiry) {
            return new Finding("rotate", "cert_near_expiry", covered);
        }
        if (weakKey) {
            return new Finding("rotate", "weak_key", covered);
        }
        if (untrusted) {
            return new Finding("rotate", "untrusted_issuer", covered);
        }
        if (covered && wExpiringSoon) {
            return new Finding("rotate", "waiver_expiring_soon", true);
        }
        if (covered) {
            return new Finding("allow", "active_waiver_ok", true);
        }
        return new Finding("allow", "compliant", false);
    }

    private static String reasonForViolation(String v) {
        return switch (v) {
            case "tls" -> "tls_version_blocked";
            case "mtls" -> "mtls_missing";
            default -> "chain_invalid";
        };
    }

    private static void validate(String schemaName, JsonNode doc, String label) throws Exception {
        JsonSchema schema = FACTORY.getSchema(Json.readJson(SCHEMA_DIR.resolve(schemaName)));
        Set<ValidationMessage> errors = schema.validate(doc);
        if (!errors.isEmpty()) {
            throw new IllegalStateException(label + " failed schema validation: " + errors);
        }
    }

    private static Set<String> asSet(JsonNode arr) {
        Set<String> s = new HashSet<>();
        if (arr != null) {
            arr.forEach(n -> s.add(n.asText()));
        }
        return s;
    }

    private static String str(Map<String, Object> m, String k) {
        Object v = m.get(k);
        return v == null ? null : v.toString();
    }

    private static boolean bool(Map<String, Object> m, String k) {
        return Boolean.TRUE.equals(m.get(k));
    }

    private FindingsEngine() {}
}
