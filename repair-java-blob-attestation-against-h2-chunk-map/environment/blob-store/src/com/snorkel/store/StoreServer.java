package com.snorkel.store;

import com.sun.net.httpserver.HttpExchange;
import com.sun.net.httpserver.HttpServer;

import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.net.InetSocketAddress;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.Statement;
import java.util.ArrayList;
import java.util.List;

/**
 * The blob store API, backed by an in-memory playground that behaves like the
 * real store. It is here so the object contract can be checked by experiment
 * rather than assumed from the schema: ingest an object, replace its content,
 * and read it back the two ways the store exposes.
 *
 * An object is kept as an ordered chunk map and as a materialised blob copy.
 * The two are written together at ingest, but a later replace only rewrites the
 * chunk map, so the copy can fall behind. GET /objects/{id} answers with the
 * object as the store holds it; /objects/{id}/blob answers from the copy; and
 * the attestation endpoint answers from a cache it never rechecks, which is why
 * it keeps calling stale objects verified.
 */
public final class StoreServer {
    private final Connection db;

    private StoreServer(Connection db) {
        this.db = db;
    }

    public static void main(String[] args) throws Exception {
        int port = args.length > 0 ? Integer.parseInt(args[0]) : 8080;
        Connection db = DriverManager.getConnection(
                "jdbc:h2:mem:playground;DB_CLOSE_DELAY=-1", "sa", "");
        StoreServer store = new StoreServer(db);
        store.initSchema();
        store.seed();

        HttpServer server = HttpServer.create(new InetSocketAddress(port), 0);
        server.createContext("/health", ex -> store.text(ex, 200, "ok\n"));
        server.createContext("/objects", store::handleObjects);
        server.setExecutor(null);
        server.start();
        System.out.println("blob-store listening on " + port);
    }

    private void handleObjects(HttpExchange ex) throws IOException {
        String path = ex.getRequestURI().getPath();
        String method = ex.getRequestMethod();
        String rest = path.substring("/objects".length());
        try {
            if (rest.isEmpty() || rest.equals("/")) {
                if (method.equals("GET")) {
                    text(ex, 200, String.join("\n", listIds()) + "\n");
                } else {
                    text(ex, 405, "method not allowed\n");
                }
                return;
            }
            String[] parts = rest.substring(1).split("/", 2);
            String id = parts[0];
            String tail = parts.length > 1 ? parts[1] : "";

            synchronized (this) {
                if (method.equals("PUT") && tail.isEmpty()) {
                    ingest(id, readBody(ex));
                    text(ex, 200, "ingested " + id + "\n");
                } else if (method.equals("POST") && tail.isEmpty()) {
                    replace(id, readBody(ex));
                    text(ex, 200, "replaced " + id + "\n");
                } else if (method.equals("GET") && tail.isEmpty()) {
                    bytes(ex, durableBytes(id));
                } else if (method.equals("GET") && tail.equals("blob")) {
                    bytes(ex, blobBytes(id));
                } else if (method.equals("GET") && tail.equals("attestation")) {
                    text(ex, 200, attestation(id) + "\n");
                } else {
                    text(ex, 404, "no such route\n");
                }
            }
        } catch (NotFound nf) {
            text(ex, 404, nf.getMessage() + "\n");
        } catch (Exception e) {
            text(ex, 500, e.getClass().getSimpleName() + ": " + e.getMessage() + "\n");
        }
    }

    private void ingest(String id, byte[] content) throws Exception {
        deleteChunks(id);
        try (PreparedStatement ps = db.prepareStatement(
                "MERGE INTO objects (object_id, declared_digest, digest_algo, blob, verified) "
                        + "KEY (object_id) VALUES (?,?,?,?,?)")) {
            ps.setString(1, id);
            ps.setString(2, sha256(content));
            ps.setString(3, "sha256");
            ps.setBytes(4, content);
            ps.setBoolean(5, true);
            ps.executeUpdate();
        }
        insertChunk(id, 0, content);
    }

    private void replace(String id, byte[] content) throws Exception {
        // A replace rewrites the chunk map and refreshes the declared digest to
        // the new content. It does not touch the blob copy, so that copy now
        // lags, and it does not reset the verified flag, so attestation stays
        // stale until something rechecks it.
        requireExists(id);
        deleteChunks(id);
        int ordinal = 0;
        for (byte[] chunk : split(content)) {
            insertChunk(id, ordinal++, chunk);
        }
        try (PreparedStatement ps = db.prepareStatement(
                "UPDATE objects SET declared_digest = ? WHERE object_id = ?")) {
            ps.setString(1, sha256(content));
            ps.setString(2, id);
            ps.executeUpdate();
        }
    }

    private byte[] durableBytes(String id) throws Exception {
        requireExists(id);
        List<byte[]> parts = new ArrayList<>();
        try (PreparedStatement ps = db.prepareStatement(
                "SELECT bytes FROM chunks WHERE object_id = ? ORDER BY ordinal")) {
            ps.setString(1, id);
            try (ResultSet rs = ps.executeQuery()) {
                while (rs.next()) {
                    parts.add(rs.getBytes(1));
                }
            }
        }
        return concat(parts);
    }

    private byte[] blobBytes(String id) throws Exception {
        try (PreparedStatement ps = db.prepareStatement(
                "SELECT blob FROM objects WHERE object_id = ?")) {
            ps.setString(1, id);
            try (ResultSet rs = ps.executeQuery()) {
                if (!rs.next()) {
                    throw new NotFound("no object " + id);
                }
                return rs.getBytes(1);
            }
        }
    }

    private String attestation(String id) throws Exception {
        try (PreparedStatement ps = db.prepareStatement(
                "SELECT verified FROM objects WHERE object_id = ?")) {
            ps.setString(1, id);
            try (ResultSet rs = ps.executeQuery()) {
                if (!rs.next()) {
                    throw new NotFound("no object " + id);
                }
                return rs.getBoolean(1) ? "verified" : "failed";
            }
        }
    }

    private void seed() throws Exception {
        // One object whose blob copy is already behind its chunk map, so the
        // divergence is visible on the first read without ingesting anything.
        ingest("demo-fresh", "the quick brown fox".getBytes(StandardCharsets.UTF_8));
        ingest("demo-stale", "first materialisation".getBytes(StandardCharsets.UTF_8));
        replace("demo-stale",
                "first materialisation and everything appended after it"
                        .getBytes(StandardCharsets.UTF_8));
    }

    private void initSchema() throws Exception {
        try (Statement st = db.createStatement()) {
            st.execute("CREATE TABLE objects (object_id VARCHAR(64) PRIMARY KEY, "
                    + "declared_digest VARCHAR(128), digest_algo VARCHAR(16), "
                    + "blob VARBINARY, verified BOOLEAN)");
            st.execute("CREATE TABLE chunks (object_id VARCHAR(64), ordinal INT, "
                    + "bytes VARBINARY, PRIMARY KEY (object_id, ordinal))");
        }
    }

    private List<String> listIds() throws Exception {
        List<String> ids = new ArrayList<>();
        try (Statement st = db.createStatement();
                ResultSet rs = st.executeQuery("SELECT object_id FROM objects ORDER BY object_id")) {
            while (rs.next()) {
                ids.add(rs.getString(1));
            }
        }
        return ids;
    }

    private void insertChunk(String id, int ordinal, byte[] bytes) throws Exception {
        try (PreparedStatement ps = db.prepareStatement(
                "INSERT INTO chunks (object_id, ordinal, bytes) VALUES (?,?,?)")) {
            ps.setString(1, id);
            ps.setInt(2, ordinal);
            ps.setBytes(3, bytes);
            ps.executeUpdate();
        }
    }

    private void deleteChunks(String id) throws Exception {
        try (PreparedStatement ps = db.prepareStatement(
                "DELETE FROM chunks WHERE object_id = ?")) {
            ps.setString(1, id);
            ps.executeUpdate();
        }
    }

    private void requireExists(String id) throws Exception {
        try (PreparedStatement ps = db.prepareStatement(
                "SELECT 1 FROM objects WHERE object_id = ?")) {
            ps.setString(1, id);
            try (ResultSet rs = ps.executeQuery()) {
                if (!rs.next()) {
                    throw new NotFound("no object " + id);
                }
            }
        }
    }

    private static List<byte[]> split(byte[] content) {
        // Chunk on roughly even thirds so a replaced object really is multi-part.
        List<byte[]> parts = new ArrayList<>();
        if (content.length == 0) {
            parts.add(content);
            return parts;
        }
        int size = Math.max(1, content.length / 3);
        for (int start = 0; start < content.length; start += size) {
            int end = Math.min(content.length, start + size);
            byte[] part = new byte[end - start];
            System.arraycopy(content, start, part, 0, end - start);
            parts.add(part);
        }
        return parts;
    }

    private static byte[] concat(List<byte[]> parts) {
        int total = parts.stream().mapToInt(p -> p.length).sum();
        byte[] out = new byte[total];
        int at = 0;
        for (byte[] part : parts) {
            System.arraycopy(part, 0, out, at, part.length);
            at += part.length;
        }
        return out;
    }

    private static byte[] readBody(HttpExchange ex) throws IOException {
        try (InputStream in = ex.getRequestBody()) {
            return in.readAllBytes();
        }
    }

    private static String sha256(byte[] content) throws Exception {
        MessageDigest md = MessageDigest.getInstance("SHA-256");
        byte[] digest = md.digest(content);
        StringBuilder sb = new StringBuilder(digest.length * 2);
        for (byte b : digest) {
            sb.append(Character.forDigit((b >> 4) & 0xF, 16));
            sb.append(Character.forDigit(b & 0xF, 16));
        }
        return sb.toString();
    }

    private void text(HttpExchange ex, int code, String body) throws IOException {
        bytes(ex, code, body.getBytes(StandardCharsets.UTF_8));
    }

    private void bytes(HttpExchange ex, byte[] body) throws IOException {
        bytes(ex, 200, body);
    }

    private void bytes(HttpExchange ex, int code, byte[] body) throws IOException {
        ex.sendResponseHeaders(code, body.length);
        try (OutputStream out = ex.getResponseBody()) {
            out.write(body);
        }
    }

    private static final class NotFound extends RuntimeException {
        NotFound(String message) {
            super(message);
        }
    }
}
