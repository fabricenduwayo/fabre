package com.mariner.audit;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.SerializationFeature;
import com.fasterxml.jackson.dataformat.toml.TomlMapper;
import com.fasterxml.jackson.dataformat.yaml.YAMLMapper;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;
import java.util.Map;

/** Small wrappers around Jackson for the formats this pipeline touches. */
final class Json {
    static final ObjectMapper JSON =
            new ObjectMapper().enable(SerializationFeature.INDENT_OUTPUT);
    static final YAMLMapper YAML = new YAMLMapper();
    static final TomlMapper TOML = new TomlMapper();

    private Json() {}

    static void writeList(Path path, List<?> value) throws IOException {
        Files.createDirectories(path.getParent());
        JSON.writeValue(path.toFile(), value);
    }

    @SuppressWarnings("unchecked")
    static List<Map<String, Object>> readList(Path path) throws IOException {
        return JSON.readValue(path.toFile(), List.class);
    }

    static JsonNode readYaml(Path path) throws IOException {
        return YAML.readTree(path.toFile());
    }

    static JsonNode readToml(Path path) throws IOException {
        return TOML.readTree(path.toFile());
    }

    static JsonNode readJson(Path path) throws IOException {
        return JSON.readTree(path.toFile());
    }
}
