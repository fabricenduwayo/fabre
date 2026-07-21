package com.snorkel.attest;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ArrayNode;
import com.fasterxml.jackson.databind.node.ObjectNode;

import java.io.ByteArrayOutputStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.security.MessageDigest;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.Statement;
import java.util.ArrayList;
import java.util.List;

/**
 * Attests each object in a blob store against the declaration it was accepted
 * under.
 *
 * The declared length and digest are the evidence; the chunk map and the
 * materialised blob are copies the store kept, and either can be tampered with or
 * lost. An object is trusted only when a surviving copy still proves out against
 * the declaration, whichever copy that is. Bytes are read to be hashed and then
 * discarded; nothing reconstructed is written out.
 */
public final class Auditor {
    private static final ObjectMapper JSON = new ObjectMapper();

    public static void run(String jdbcUrl, String outputPath) throws Exception {
        Path storeRoot = storeRoot(jdbcUrl);
        List<Verdict> verdicts = new ArrayList<>();

        try (Connection conn = DriverManager.getConnection(readUrl(jdbcUrl), "sa", "")) {
            for (Obj obj : loadObjects(conn)) {
                verdicts.add(attest(conn, storeRoot, obj));
            }
            writeReport(conn, verdicts, outputPath);
        }
    }

    private static Verdict attest(Connection conn, Path root, Obj obj) throws Exception {
        List<byte[]> surviving = new ArrayList<>();
        for (byte[] copy : new byte[][] {chunkCopy(conn, root, obj), blobCopy(root, obj)}) {
            if (copy != null && copy.length == obj.size) {
                surviving.add(copy);
            }
        }
        if (surviving.isEmpty()) {
            return new Verdict(obj.id, "unattestable", "missing_content");
        }
        if (!"sha256".equalsIgnoreCase(obj.algo)) {
            return new Verdict(obj.id, "unattestable", "unsupported_digest");
        }
        for (byte[] copy : surviving) {
            if (sha256Hex(copy).equalsIgnoreCase(obj.declared)) {
                return new Verdict(obj.id, "intact", null);
            }
        }
        return new Verdict(obj.id, "corrupt", "digest_mismatch");
    }

    /** The chunk map concatenated in ordinal order, or null if the object has no
     *  chunk rows or any chunk file is missing. */
    private static byte[] chunkCopy(Connection conn, Path root, Obj obj) throws Exception {
        List<int[]> keys = new ArrayList<>();
        List<String> allPaths = new ArrayList<>();
        int latest = Integer.MIN_VALUE;
        try (PreparedStatement ps = conn.prepareStatement(
                "SELECT generation, ordinal, chunk_path FROM object_chunks WHERE object_id = ?")) {
            ps.setString(1, obj.id);
            try (ResultSet rs = ps.executeQuery()) {
                while (rs.next()) {
                    int gen = rs.getInt(1);
                    keys.add(new int[] {gen, rs.getInt(2)});
                    allPaths.add(rs.getString(3));
                    latest = Math.max(latest, gen);
                }
            }
        }
        if (allPaths.isEmpty()) {
            return null;
        }
        List<int[]> current = new ArrayList<>();
        for (int i = 0; i < keys.size(); i++) {
            if (keys.get(i)[0] == latest) {
                current.add(new int[] {keys.get(i)[1], i});
            }
        }
        current.sort((a, b) -> Integer.compare(a[0], b[0]));
        List<String> paths = new ArrayList<>();
        for (int[] entry : current) {
            paths.add(allPaths.get(entry[1]));
        }
        ByteArrayOutputStream out = new ByteArrayOutputStream();
        for (String rel : paths) {
            Path file = root.resolve(rel);
            if (!Files.isRegularFile(file)) {
                return null;
            }
            out.write(Files.readAllBytes(file));
        }
        return out.toByteArray();
    }

    /** The materialised blob, or null if the object records no blob or its file
     *  is missing. */
    private static byte[] blobCopy(Path root, Obj obj) throws Exception {
        if (obj.blobPath == null) {
            return null;
        }
        Path file = root.resolve(obj.blobPath);
        return Files.isRegularFile(file) ? Files.readAllBytes(file) : null;
    }

    private static void writeReport(Connection conn, List<Verdict> verdicts, String outputPath)
            throws Exception {
        verdicts.sort((a, b) -> a.id.compareTo(b.id));

        ObjectNode report = JSON.createObjectNode();
        ArrayNode intact = report.putArray("intact");
        ArrayNode corrupt = report.putArray("corrupt");
        ArrayNode unattestable = report.putArray("unattestable");
        ArrayNode conflicts = report.putArray("conflicts");

        for (Verdict v : verdicts) {
            if ("intact".equals(v.status)) {
                intact.add(v.id);
            } else if ("corrupt".equals(v.status)) {
                corrupt.add(reasoned(v));
            } else {
                unattestable.add(reasoned(v));
            }
            String asserted = cacheStatus(conn, v.id);
            if (asserted != null && conflicts(asserted, v.status)) {
                ObjectNode row = JSON.createObjectNode();
                row.put("object_id", v.id);
                row.put("cache_status", asserted);
                row.put("actual_status", v.status);
                conflicts.add(row);
            }
        }

        Path out = Paths.get(outputPath);
        if (out.getParent() != null) {
            Files.createDirectories(out.getParent());
        }
        JSON.writerWithDefaultPrettyPrinter().writeValue(out.toFile(), report);
    }

    private static ObjectNode reasoned(Verdict v) {
        ObjectNode node = JSON.createObjectNode();
        node.put("object_id", v.id);
        node.put("reason", v.reason);
        return node;
    }

    /** A cache row conflicts when its claim does not match the recomputed status. */
    private static boolean conflicts(String cacheStatus, String actual) {
        if ("verified".equals(cacheStatus)) {
            return !"intact".equals(actual);
        }
        if ("failed".equals(cacheStatus)) {
            return !"corrupt".equals(actual);
        }
        return false;
    }

    private static String cacheStatus(Connection conn, String objectId) throws Exception {
        try (PreparedStatement ps = conn.prepareStatement(
                "SELECT status FROM attestation_cache WHERE object_id = ?")) {
            ps.setString(1, objectId);
            try (ResultSet rs = ps.executeQuery()) {
                return rs.next() ? rs.getString(1) : null;
            }
        }
    }

    private static List<Obj> loadObjects(Connection conn) throws Exception {
        List<Obj> objects = new ArrayList<>();
        try (Statement st = conn.createStatement();
                ResultSet rs = st.executeQuery(
                        "SELECT object_id, declared_digest, digest_algo, blob_path, size_bytes "
                                + "FROM objects")) {
            while (rs.next()) {
                objects.add(new Obj(
                        rs.getString("object_id"),
                        rs.getString("declared_digest"),
                        rs.getString("digest_algo"),
                        rs.getString("blob_path"),
                        rs.getLong("size_bytes")));
            }
        }
        return objects;
    }

    private static Path storeRoot(String jdbcUrl) {
        int marker = jdbcUrl.indexOf("file:");
        if (marker < 0) {
            throw new IllegalArgumentException("expected a file-backed H2 url: " + jdbcUrl);
        }
        String path = jdbcUrl.substring(marker + "file:".length());
        int semi = path.indexOf(';');
        if (semi >= 0) {
            path = path.substring(0, semi);
        }
        Path parent = Paths.get(path).getParent();
        return parent != null ? parent : Paths.get(".");
    }

    private static String readUrl(String dbUrl) {
        return dbUrl.contains("IFEXISTS") ? dbUrl : dbUrl + ";IFEXISTS=TRUE";
    }

    private static String sha256Hex(byte[] bytes) throws Exception {
        byte[] digest = MessageDigest.getInstance("SHA-256").digest(bytes);
        StringBuilder sb = new StringBuilder(digest.length * 2);
        for (byte b : digest) {
            sb.append(Character.forDigit((b >> 4) & 0xF, 16));
            sb.append(Character.forDigit(b & 0xF, 16));
        }
        return sb.toString();
    }

    private Auditor() {}

    private static final class Obj {
        final String id;
        final String declared;
        final String algo;
        final String blobPath;
        final long size;

        Obj(String id, String declared, String algo, String blobPath, long size) {
            this.id = id;
            this.declared = declared;
            this.algo = algo;
            this.blobPath = blobPath;
            this.size = size;
        }
    }

    private static final class Verdict {
        final String id;
        final String status;
        final String reason;

        Verdict(String id, String status, String reason) {
            this.id = id;
            this.status = status;
            this.reason = reason;
        }
    }
}
