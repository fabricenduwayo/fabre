package com.example.registry;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;

@RestController
public class AliasController {

    private final RegistryStore store;

    public AliasController(RegistryStore store) {
        this.store = store;
    }

    @GetMapping("/aliases")
    public Map<String, String> aliases() {
        return store.aliases();
    }
}
