package com.snorkel.attest;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ArrayNode;
import com.fasterxml.jackson.databind.node.ObjectNode;

import java.io.InputStream;
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
 * Audits a blob store against what its objects actually hash to.
 *
 * The durable bytes of an object are its chunk map concatenated in ordinal
 * order. blob_path is a materialised copy the store keeps for the legacy read
 * path; a replace rewrites the chunk map and leaves that copy alone, so it is
 * not authoritative and is only read when an object has no chunk map. Bytes are
 * streamed into the digest and discarded, never written anywhere.
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
        List<Path> parts = durableParts(conn, root, obj);
        MessageDigest sha256 = MessageDigest.getInstance("SHA-256");
        for (Path part : parts) {
            if (!Files.isRegularFile(part)) {
                return new Verdict(obj.id, "unattestable", "missing_content");
            }
            try (InputStream in = Files.newInputStream(part)) {
                byte[] buf = new byte[8192];
                int read;
                while ((read = in.read(buf)) != -1) {
                    sha256.update(buf, 0, read);
                }
            }
        }
        if (!"sha256".equalsIgnoreCase(obj.algo)) {
            return new Verdict(obj.id, "unattestable", "unsupported_digest");
        }
        String actual = hex(sha256.digest());
        if (actual.equalsIgnoreCase(obj.declared)) {
            return new Verdict(obj.id, "intact", null);
        }
        return new Verdict(obj.id, "corrupt", "digest_mismatch");
    }

    private static List<Path> durableParts(Connection conn, Path root, Obj obj) throws Exception {
        List<Path> parts = new ArrayList<>();
        try (PreparedStatement ps = conn.prepareStatement(
                "SELECT chunk_path FROM object_chunks WHERE object_id = ? ORDER BY ordinal")) {
            ps.setString(1, obj.id);
            try (ResultSet rs = ps.executeQuery()) {
                while (rs.next()) {
                    parts.add(root.resolve(rs.getString(1)));
                }
            }
        }
        if (parts.isEmpty() && obj.blobPath != null) {
            parts.add(root.resolve(obj.blobPath));
        }
        return parts;
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
                        "SELECT object_id, declared_digest, digest_algo, blob_path FROM objects")) {
            while (rs.next()) {
                objects.add(new Obj(
                        rs.getString("object_id"),
                        rs.getString("declared_digest"),
                        rs.getString("digest_algo"),
                        rs.getString("blob_path")));
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

    private static String hex(byte[] bytes) {
        StringBuilder sb = new StringBuilder(bytes.length * 2);
        for (byte b : bytes) {
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

        Obj(String id, String declared, String algo, String blobPath) {
            this.id = id;
            this.declared = declared;
            this.algo = algo;
            this.blobPath = blobPath;
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
