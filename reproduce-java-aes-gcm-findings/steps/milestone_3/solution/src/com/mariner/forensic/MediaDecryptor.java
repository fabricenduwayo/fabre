package com.mariner.forensic;

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
import javax.crypto.Cipher;
import javax.crypto.spec.GCMParameterSpec;
import javax.crypto.spec.SecretKeySpec;

/** Extract GIF payloads and authenticate them with AES-GCM. */
final class MediaDecryptor {
    private static final Path CORRELATION = Path.of("/app/out/correlation.json");
    private static final Path GIF = Path.of("/app/fixtures/evidence.gif");
    private static final Path OUT = Path.of("/app/out/findings.json");
    private static final String JDBC = "jdbc:sqlite:/app/data/forensic_audit.db";
    private static final Pattern PAYLOAD =
            Pattern.compile("(frm-[0-9]{3})\\|([0-9A-F]+)");

    static void run() throws Exception {
        List<Map<String, Object>> correlation = loadCorrelation();
        Map<String, byte[]> payloads = extractGifPayloads();
        List<Map<String, Object>> output = new ArrayList<>();

        for (Map<String, Object> row : correlation) {
            String frameId = (String) row.get("frame_id");
            int keyVersion = ((Number) row.get("key_version")).intValue();
            byte[] nonce = fromHex((String) row.get("nonce_hex"));
            byte[] key = loadKey(keyVersion);
            byte[] ciphertext = payloads.get(frameId);

            Map<String, Object> finding = new LinkedHashMap<>();
            finding.put("frame_id", frameId);
            finding.put("label", row.get("label"));
            finding.put("gif_index", row.get("gif_index"));
            finding.put("key_version", keyVersion);
            finding.put("key_source", row.get("key_source"));
            finding.put("nonce_hex", row.get("nonce_hex"));
            finding.put("nonce_source", row.get("nonce_source"));

            byte[] plaintext = null;
            try {
                plaintext = decrypt(ciphertext, key, nonce, frameId);
            } catch (Exception ignored) {
                // A failed GCM tag is represented as an unauthenticated finding.
            }
            boolean authOk = plaintext != null;
            finding.put("auth_ok", authOk);
            finding.put("plaintext_sha256", authOk ? sha256hex(plaintext) : null);
            finding.put("reason_code", authOk ? "authenticated" : "auth_failed");
            output.add(finding);
        }

        Json.writeList(OUT, output);
        System.out.println("decrypt: wrote " + output.size() + " findings to " + OUT);
    }

    @SuppressWarnings("unchecked")
    private static List<Map<String, Object>> loadCorrelation() throws Exception {
        return new com.fasterxml.jackson.databind.ObjectMapper()
                .readValue(CORRELATION.toFile(), List.class);
    }

    private static byte[] loadKey(int version) throws Exception {
        try (Connection conn = DriverManager.getConnection(JDBC);
                Statement statement = conn.createStatement();
                ResultSet rs = statement.executeQuery(
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
        cipher.updateAAD(aad.getBytes(StandardCharsets.UTF_8));
        return cipher.doFinal(ciphertext);
    }

    private static Map<String, byte[]> extractGifPayloads() throws Exception {
        byte[] data = Files.readAllBytes(GIF);
        Map<String, byte[]> payloads = new LinkedHashMap<>();
        int offset = 0;
        while (offset < data.length) {
            if (data[offset] == 0x21
                    && offset + 2 < data.length
                    && data[offset + 1] == (byte) 0xFF) {
                int blockSize = data[offset + 2] & 0xFF;
                int headerEnd = offset + 3 + blockSize;
                if (headerEnd > data.length) {
                    break;
                }
                String appId = new String(
                        data,
                        offset + 3,
                        Math.min(11, blockSize),
                        StandardCharsets.US_ASCII);
                if (appId.startsWith("MRNR") && appId.contains("CRYPTO1")) {
                    int position = headerEnd + 1;
                    StringBuilder payload = new StringBuilder();
                    while (position < data.length) {
                        int subLength = data[position] & 0xFF;
                        position++;
                        if (subLength == 0) {
                            break;
                        }
                        if (position + subLength > data.length) {
                            throw new IllegalStateException("truncated GIF application block");
                        }
                        payload.append(new String(
                                data, position, subLength, StandardCharsets.US_ASCII));
                        position += subLength;
                    }
                    Matcher matcher = PAYLOAD.matcher(payload);
                    while (matcher.find()) {
                        payloads.put(matcher.group(1), fromHex(matcher.group(2)));
                    }
                    offset = position;
                    continue;
                }
            }
            offset++;
        }
        return payloads;
    }

    private static String sha256hex(byte[] data) throws Exception {
        byte[] digest = MessageDigest.getInstance("SHA-256").digest(data);
        StringBuilder output = new StringBuilder(digest.length * 2);
        for (byte value : digest) {
            output.append(String.format("%02x", value));
        }
        return output.toString();
    }

    private static byte[] fromHex(String hex) {
        byte[] output = new byte[hex.length() / 2];
        for (int index = 0; index < output.length; index++) {
            output[index] = (byte) Integer.parseInt(
                    hex.substring(index * 2, index * 2 + 2), 16);
        }
        return output;
    }

    private MediaDecryptor() {}
}
