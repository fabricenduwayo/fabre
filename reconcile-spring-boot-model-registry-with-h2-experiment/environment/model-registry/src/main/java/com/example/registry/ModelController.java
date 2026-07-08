package com.example.registry;

import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.server.ResponseStatusException;

import java.util.List;

@RestController
public class ModelController {

    private final RegistryStore store;

    public ModelController(RegistryStore store) {
        this.store = store;
    }

    @GetMapping("/models/candidates")
    public List<CandidateModel> candidates() {
        return store.candidates();
    }

    @GetMapping("/models/{id}")
    public CandidateModel candidate(@PathVariable String id) {
        return store.candidate(id)
                .orElseThrow(() -> new ResponseStatusException(
                        HttpStatus.NOT_FOUND, "Unknown model id: " + id));
    }
}
