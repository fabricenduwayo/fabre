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
 * real store. Ingest an object, replace its content, and read it back through
 * the routes below to see how a declaration and its stored copies drift apart.
 *
 * An object declares a length and a digest. Its bytes are kept as an ordered
 * chunk map and as a materialised blob, and either copy can fall behind. The
 * store serves the copy that still reads back at the declared length.
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
                    bytes(ex, servedContent(id));
                } else if (method.equals("GET") && tail.equals("blob")) {
                    bytes(ex, blobBytes(id));
                } else if (method.equals("GET") && tail.equals("declared")) {
                    text(ex, 200, declared(id) + "\n");
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
        writeDeclaration(id, content);
        setBlob(id, content);
        insertChunk(id, 0, content);
    }

    private void replace(String id, byte[] content) throws Exception {
        // A replace re-declares the object to the new content and rewrites the
        // chunk map to it. The blob copy is left as it was, so it falls behind.
        requireExists(id);
        deleteChunks(id);
        writeDeclaration(id, content);
        int ordinal = 0;
        for (byte[] chunk : split(content)) {
            insertChunk(id, ordinal++, chunk);
        }
    }

    /** Serve the copy that reads back at the declared length. */
    private byte[] servedContent(String id) throws Exception {
        long size = declaredSize(id);
        byte[] chunks = chunkBytes(id);
        if (chunks != null && chunks.length == size) {
            return chunks;
        }
        byte[] blob = blobBytesOrNull(id);
        if (blob != null && blob.length == size) {
            return blob;
        }
        throw new NotFound("no copy of " + id + " matches its declared length");
    }

    private byte[] chunkBytes(String id) throws Exception {
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
        return parts.isEmpty() ? null : concat(parts);
    }

    private byte[] blobBytesOrNull(String id) throws Exception {
        try (PreparedStatement ps = db.prepareStatement(
                "SELECT blob FROM objects WHERE object_id = ?")) {
            ps.setString(1, id);
            try (ResultSet rs = ps.executeQuery()) {
                return rs.next() ? rs.getBytes(1) : null;
            }
        }
    }

    private byte[] blobBytes(String id) throws Exception {
        byte[] blob = blobBytesOrNull(id);
        if (blob == null) {
            throw new NotFound("no object " + id);
        }
        return blob;
    }

    private String declared(String id) throws Exception {
        try (PreparedStatement ps = db.prepareStatement(
                "SELECT declared_digest, declared_size FROM objects WHERE object_id = ?")) {
            ps.setString(1, id);
            try (ResultSet rs = ps.executeQuery()) {
                if (!rs.next()) {
                    throw new NotFound("no object " + id);
                }
                return "size=" + rs.getLong(2) + " sha256=" + rs.getString(1);
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
        // A sound object.
        ingest("demo-fresh", "the quick brown fox".getBytes(StandardCharsets.UTF_8));

        // Replaced object: the chunk map holds the new content, the blob is the
        // earlier materialisation, so the chunk map is the copy at the declared
        // length and the blob is behind.
        ingest("demo-stale-blob", "first materialisation".getBytes(StandardCharsets.UTF_8));
        replace("demo-stale-blob",
                "first materialisation and everything appended after it"
                        .getBytes(StandardCharsets.UTF_8));

        // The other way round: the blob holds the declared content and the chunk
        // map is a stale fragment, so here the blob is the copy served.
        byte[] content = "declared content served from the blob".getBytes(StandardCharsets.UTF_8);
        writeDeclaration("demo-stale-chunks", content);
        setBlob("demo-stale-chunks", content);
        insertChunk("demo-stale-chunks", 0, "stale fragment".getBytes(StandardCharsets.UTF_8));
    }

    private void initSchema() throws Exception {
        try (Statement st = db.createStatement()) {
            st.execute("CREATE TABLE objects (object_id VARCHAR(64) PRIMARY KEY, "
                    + "declared_digest VARCHAR(128), declared_size BIGINT, "
                    + "blob VARBINARY, verified BOOLEAN)");
            st.execute("CREATE TABLE chunks (object_id VARCHAR(64), ordinal INT, "
                    + "bytes VARBINARY, PRIMARY KEY (object_id, ordinal))");
        }
    }

    private void writeDeclaration(String id, byte[] content) throws Exception {
        try (PreparedStatement ps = db.prepareStatement(
                "MERGE INTO objects (object_id, declared_digest, declared_size, verified) "
                        + "KEY (object_id) VALUES (?,?,?,?)")) {
            ps.setString(1, id);
            ps.setString(2, sha256(content));
            ps.setLong(3, content.length);
            ps.setBoolean(4, true);
            ps.executeUpdate();
        }
    }

    private void setBlob(String id, byte[] content) throws Exception {
        try (PreparedStatement ps = db.prepareStatement(
                "UPDATE objects SET blob = ? WHERE object_id = ?")) {
            ps.setBytes(1, content);
            ps.setString(2, id);
            ps.executeUpdate();
        }
    }

    private long declaredSize(String id) throws Exception {
        try (PreparedStatement ps = db.prepareStatement(
                "SELECT declared_size FROM objects WHERE object_id = ?")) {
            ps.setString(1, id);
            try (ResultSet rs = ps.executeQuery()) {
                if (!rs.next()) {
                    throw new NotFound("no object " + id);
                }
                return rs.getLong(1);
            }
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
