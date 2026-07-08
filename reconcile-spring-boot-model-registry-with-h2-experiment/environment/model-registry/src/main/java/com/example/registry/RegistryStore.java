package com.example.registry;

import com.fasterxml.jackson.databind.ObjectMapper;
import jakarta.annotation.PostConstruct;
import org.springframework.core.io.ClassPathResource;
import org.springframework.stereotype.Component;

import java.io.IOException;
import java.io.InputStream;
import java.util.Collections;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;

/**
 * Loads the bundled registry document once at startup and serves it read-only
 * for the lifetime of the application. There are no runtime writes; the
 * in-memory view is a faithful copy of {@code registry-models.json}.
 */
@Component
public class RegistryStore {

    private static final String RESOURCE_PATH = "registry-models.json";

    private final ObjectMapper objectMapper;

    private List<CandidateModel> candidates = Collections.emptyList();
    private Map<String, CandidateModel> candidatesById = Collections.emptyMap();
    private Map<String, String> aliases = Collections.emptyMap();

    public RegistryStore(ObjectMapper objectMapper) {
        this.objectMapper = objectMapper;
    }

    @PostConstruct
    void load() throws IOException {
        ClassPathResource resource = new ClassPathResource(RESOURCE_PATH);
        try (InputStream in = resource.getInputStream()) {
            RegistryData data = objectMapper.readValue(in, RegistryData.class);

            List<CandidateModel> loaded = List.copyOf(data.candidates());
            Map<String, CandidateModel> byId = new LinkedHashMap<>();
            for (CandidateModel model : loaded) {
                byId.put(model.id(), model);
            }

            this.candidates = loaded;
            this.candidatesById = Collections.unmodifiableMap(byId);
            this.aliases = Collections.unmodifiableMap(new LinkedHashMap<>(data.aliases()));
        }
    }

    public List<CandidateModel> candidates() {
        return candidates;
    }

    public Optional<CandidateModel> candidate(String id) {
        return Optional.ofNullable(candidatesById.get(id));
    }

    public Map<String, String> aliases() {
        return aliases;
    }
}
