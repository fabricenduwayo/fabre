package com.snorkel.attestapi;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.sun.net.httpserver.Headers;
import com.sun.net.httpserver.HttpExchange;
import com.sun.net.httpserver.HttpHandler;
import com.sun.net.httpserver.HttpServer;

import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.net.InetSocketAddress;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.HashMap;
import java.util.Map;

public final class ApiServer {
    private static final ObjectMapper MAPPER = new ObjectMapper();
    private final Map<String, ArtifactRecord> artifacts = new HashMap<>();

    public static void main(String[] args) throws Exception {
        Path dataPath = Path.of(args.length > 0 ? args[0] : "/app/artifact-api/data/registry.json");
        int port = args.length > 1 ? Integer.parseInt(args[1]) : 8080;
        ApiServer server = new ApiServer();
        server.load(dataPath);
        server.start(port);
        Thread.currentThread().join();
    }

    void load(Path dataPath) throws IOException {
        JsonNode root = MAPPER.readTree(Files.readString(dataPath));
        for (JsonNode node : root.get("artifacts")) {
            ArtifactRecord record = ArtifactRecord.from(node);
            artifacts.put(record.artifactId, record);
        }
    }

    void start(int port) throws IOException {
        HttpServer http = HttpServer.create(new InetSocketAddress(port), 0);
        http.createContext("/health", new HealthHandler());
        http.createContext("/artifacts/", new ArtifactGetHandler());
        http.createContext("/verify", new VerifyHandler());
        http.setExecutor(null);
        http.start();
    }

    private static void sendJson(HttpExchange exchange, int status, String body) throws IOException {
        byte[] bytes = body.getBytes(StandardCharsets.UTF_8);
        Headers headers = exchange.getResponseHeaders();
        headers.set("Content-Type", "application/json");
        exchange.sendResponseHeaders(status, bytes.length);
        try (OutputStream out = exchange.getResponseBody()) {
            out.write(bytes);
        }
    }

    private static String readBody(HttpExchange exchange) throws IOException {
        try (InputStream in = exchange.getRequestBody()) {
            return new String(in.readAllBytes(), StandardCharsets.UTF_8);
        }
    }

    private static String expectedSignature(String digest, String signerKeyId) {
        return "sig-" + digest.substring(0, 8) + "-" + signerKeyId;
    }

    private final class HealthHandler implements HttpHandler {
        @Override
        public void handle(HttpExchange exchange) throws IOException {
            if (!"GET".equalsIgnoreCase(exchange.getRequestMethod())) {
                exchange.sendResponseHeaders(405, -1);
                return;
            }
            sendJson(exchange, 200, "{\"status\":\"ok\"}");
        }
    }

    private final class ArtifactGetHandler implements HttpHandler {
        @Override
        public void handle(HttpExchange exchange) throws IOException {
            if (!"GET".equalsIgnoreCase(exchange.getRequestMethod())) {
                exchange.sendResponseHeaders(405, -1);
                return;
            }
            String path = exchange.getRequestURI().getPath();
            String artifactId = path.substring("/artifacts/".length());
            ArtifactRecord record = artifacts.get(artifactId);
            if (record == null) {
                sendJson(exchange, 404, "{\"error\":\"unknown_artifact\"}");
                return;
            }
            if (record.registryDegraded) {
                sendJson(exchange, 503, "{\"error\":\"registry_degraded\"}");
                return;
            }
            ObjectNode body = MAPPER.createObjectNode();
            body.put("artifact_id", record.artifactId);
            body.put("version", record.version);
            body.put("registry_digest", record.registryDigest);
            body.put("detached_signature", record.detachedSignature);
            body.put("signer_key_id", record.signerKeyId);
            sendJson(exchange, 200, MAPPER.writeValueAsString(body));
        }
    }

    private final class VerifyHandler implements HttpHandler {
        @Override
        public void handle(HttpExchange exchange) throws IOException {
            if (!"POST".equalsIgnoreCase(exchange.getRequestMethod())) {
                exchange.sendResponseHeaders(405, -1);
                return;
            }
            JsonNode body = MAPPER.readTree(readBody(exchange));
            String artifactId = body.path("artifact_id").asText("");
            String digest = body.path("digest").asText("");
            String signature = body.path("detached_signature").asText("");
            ArtifactRecord record = artifacts.get(artifactId);
            if (record == null) {
                sendJson(exchange, 404, "{\"error\":\"unknown_artifact\"}");
                return;
            }
            if (record.verifyDegraded) {
                sendJson(exchange, 503, "{\"error\":\"verify_degraded\"}");
                return;
            }
            if (!record.canonicalDigest.equals(digest)) {
                sendJson(exchange, 409, "{\"error\":\"digest_mismatch\"}");
                return;
            }
            String expected = expectedSignature(digest, record.signerKeyId);
            if (!expected.equals(signature)) {
                sendJson(exchange, 400, "{\"error\":\"bad_signature\"}");
                return;
            }
            ObjectNode ok = MAPPER.createObjectNode();
            ok.put("status", "verified");
            ok.put("signer_key_id", record.signerKeyId);
            sendJson(exchange, 200, MAPPER.writeValueAsString(ok));
        }
    }

    static final class ArtifactRecord {
        final String artifactId;
        final String version;
        final String registryDigest;
        final String canonicalDigest;
        final String detachedSignature;
        final String signerKeyId;
        final boolean verifyDegraded;
        final boolean registryDegraded;

        private ArtifactRecord(
                String artifactId,
                String version,
                String registryDigest,
                String canonicalDigest,
                String detachedSignature,
                String signerKeyId,
                boolean verifyDegraded,
                boolean registryDegraded
        ) {
            this.artifactId = artifactId;
            this.version = version;
            this.registryDigest = registryDigest;
            this.canonicalDigest = canonicalDigest;
            this.detachedSignature = detachedSignature;
            this.signerKeyId = signerKeyId;
            this.verifyDegraded = verifyDegraded;
            this.registryDegraded = registryDegraded;
        }

        static ArtifactRecord from(JsonNode node) {
            String artifactId = node.get("artifact_id").asText();
            String registryDigest = node.get("registry_digest").asText();
            String detachedSignature = node.get("detached_signature").asText();
            String signerKeyId = node.get("signer_key_id").asText();
            boolean verifyDegraded = node.path("verify_degraded").asBoolean(false);
            boolean registryDegraded = node.path("registry_degraded").asBoolean(false);
            String canonicalDigest = node.path("canonical_digest").asText(registryDigest);
            return new ArtifactRecord(
                    artifactId,
                    node.get("version").asText(),
                    registryDigest,
                    canonicalDigest,
                    detachedSignature,
                    signerKeyId,
                    verifyDegraded,
                    registryDegraded
            );
        }
    }
}
