package com.audit.web;

import com.audit.model.DependencyNode;
import com.audit.service.DependencyTreeService;
import java.util.Map;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.server.ResponseStatusException;

@RestController
public class BuildController {
    private final DependencyTreeService treeService;

    public BuildController(DependencyTreeService treeService) {
        this.treeService = treeService;
    }

    @GetMapping("/health")
    public Map<String, String> health() {
        return Map.of("status", "ok");
    }

    @GetMapping("/api/builds/{id}/dependency-tree")
    public DependencyNode dependencyTree(@PathVariable("id") String buildId) {
        return treeService.loadTree(buildId)
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "build not found"));
    }
}
