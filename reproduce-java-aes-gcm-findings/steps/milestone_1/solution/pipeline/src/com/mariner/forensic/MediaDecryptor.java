package com.mariner.forensic;

import javax.crypto.Cipher;
import javax.crypto.spec.GCMParameterSpec;
import javax.crypto.spec.SecretKeySpec;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.security.MessageDigest;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.ResultSet;
import java.sql.Statement;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * Milestone 3 — extract GIF payloads and verify AES-GCM authentication.
 */
final class MediaDecryptor {
    private static final Path CORRELATION = Path.of("/app/out/correlation.json");
    private static final Path GIF = Path.of("/app/fixtures/evidence.gif");
    private static final Path OUT = Path.of("/app/out/findings.json");
    private static final String JDBC = "jdbc:sqlite:/app/data/forensic_audit.db";

    static void run() throws Exception {
        List<Map<String, Object>> correlation = loadCorrelation();
        Map<String, byte[]> payloads = extractGifPayloads();

        List<Map<String, Object>> out = new ArrayList<>();
        for (Map<String, Object> row : correlation) {
            String frameId = (String) row.get("frame_id");
            int keyVersion = ((Number) row.get("key_version")).intValue();
            byte[] nonce = fromHex((String) row.get("nonce_hex"));
            byte[] key = loadKey(keyVersion);
            byte[] ciphertext = payloads.get(frameId);

            Map<String, Object> rec = new LinkedHashMap<>(row);
            boolean authOk = false;
            byte[] plaintext = null;
            try {
                plaintext = decrypt(ciphertext, key, nonce, frameId);
                authOk = true;
            } catch (Exception ignored) {
                // auth_failed
            }
            rec.put("auth_ok", authOk);
            rec.put("plaintext_sha256", plaintext == null ? "" : sha256hex(plaintext));
            rec.put("reason_code", authOk ? "authenticated" : "auth_failed");
            out.add(rec);
        }

        Json.writeList(OUT, out);
        System.out.println("decrypt: wrote " + out.size() + " findings to " + OUT);
    }

    @SuppressWarnings("unchecked")
    private static List<Map<String, Object>> loadCorrelation() throws Exception {
        return new com.fasterxml.jackson.databind.ObjectMapper()
                .readValue(CORRELATION.toFile(), List.class);
    }

    private static byte[] loadKey(int version) throws Exception {
        try (Connection conn = DriverManager.getConnection(JDBC);
             Statement st = conn.createStatement();
             ResultSet rs = st.executeQuery(
                     "SELECT key_hex FROM key_material WHERE key_version = " + version)) {
            if (!rs.next()) {
                throw new IllegalStateException("missing key version " + version);
            }
            return fromHex(rs.getString(1));
        }
    }

    private static byte[] decrypt(byte[] ciphertext, byte[] key, byte[] nonce, String aad)
            throws Exception {
        Cipher cipher = Cipher.getInstance("AES/GCM/NoPadding");
        cipher.init(
                Cipher.DECRYPT_MODE,
                new SecretKeySpec(key, "AES"),
                new GCMParameterSpec(128, nonce));
        cipher.updateAAD(aad.getBytes());
        return cipher.doFinal(ciphertext);
    }

    private static final Pattern PAYLOAD =
            Pattern.compile("(frm-\\d{3})\\|([0-9A-F]+)");

    private static Map<String, byte[]> extractGifPayloads() throws Exception {
        String text = new String(Files.readAllBytes(GIF), StandardCharsets.US_ASCII);
        Map<String, byte[]> out = new LinkedHashMap<>();
        Matcher m = PAYLOAD.matcher(text);
        while (m.find()) {
            out.put(m.group(1), fromHex(m.group(2)));
        }
        return out;
    }

    private static String sha256hex(byte[] data) throws Exception {
        MessageDigest sha = MessageDigest.getInstance("SHA-256");
        byte[] digest = sha.digest(data);
        StringBuilder sb = new StringBuilder(digest.length * 2);
        for (byte b : digest) {
            sb.append(String.format("%02x", b));
        }
        return sb.toString();
    }

    private static byte[] fromHex(String hex) {
        byte[] out = new byte[hex.length() / 2];
        for (int i = 0; i < out.length; i++) {
            out[i] = (byte) Integer.parseInt(hex.substring(i * 2, i * 2 + 2), 16);
        }
        return out;
    }

    private MediaDecryptor() {}
}
