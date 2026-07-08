package com.example.registry;

import java.util.Map;

/**
 * A candidate model exactly as it appears in the bundled registry metadata.
 * The values carried here are the registry's own view; they are not
 * reconciled against any other source of truth at read time.
 */
public record CandidateModel(
        String id,
        String name,
        String version,
        Map<String, Double> metrics,
        String featureHash) {
}
