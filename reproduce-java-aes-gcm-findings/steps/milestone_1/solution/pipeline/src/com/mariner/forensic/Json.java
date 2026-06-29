package com.mariner.forensic;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.SerializationFeature;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;
import java.util.Map;

final class Json {
    private static final ObjectMapper MAPPER = new ObjectMapper()
            .enable(SerializationFeature.INDENT_OUTPUT);

    static void writeMap(Path path, Map<String, Object> data) throws IOException {
        Files.createDirectories(path.getParent());
        MAPPER.writeValue(path.toFile(), data);
    }

    static void writeList(Path path, List<Map<String, Object>> data) throws IOException {
        Files.createDirectories(path.getParent());
        MAPPER.writeValue(path.toFile(), data);
    }

    @SuppressWarnings("unchecked")
    static Map<String, Object> readMap(Path path) throws IOException {
        return MAPPER.readValue(path.toFile(), Map.class);
    }

    private Json() {}
}
