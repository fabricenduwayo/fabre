package com.example.registry;

import java.util.List;
import java.util.Map;

/**
 * The full contents of the bundled registry document: the ordered list of
 * candidate models and the deployment alias mapping.
 */
public record RegistryData(
        List<CandidateModel> candidates,
        Map<String, String> aliases) {
}
