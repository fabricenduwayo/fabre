package com.audit.service;

import com.audit.model.DependencyNode;
import com.audit.repo.DependencyNodeRepository;
import com.audit.repo.NodeRow;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import org.springframework.stereotype.Service;

@Service
public class DependencyTreeService {
    private final DependencyNodeRepository repository;

    public DependencyTreeService(DependencyNodeRepository repository) {
        this.repository = repository;
    }

    public Optional<DependencyNode> loadTree(String buildId) {
        if (!repository.buildExists(buildId)) {
            return Optional.empty();
        }
        List<NodeRow> rows = repository.listNodes(buildId);
        if (rows.isEmpty()) {
            return Optional.empty();
        }
        Map<String, DependencyNode> built = new HashMap<>();
        for (NodeRow row : rows) {
            DependencyNode node = new DependencyNode();
            node.setGroupId(row.groupId());
            node.setArtifactId(row.artifactId());
            node.setVersion(row.version());
            node.setScope(row.scope());
            built.put(row.nodeKey(), node);
        }
        Map<String, List<NodeRow>> byParent = new HashMap<>();
        for (NodeRow row : rows) {
            if (row.parentKey() == null) {
                continue;
            }
            byParent.computeIfAbsent(row.parentKey(), ignored -> new ArrayList<>()).add(row);
        }
        for (List<NodeRow> siblings : byParent.values()) {
            siblings.sort(Comparator.comparingInt(NodeRow::ordinal));
        }
        for (NodeRow row : rows) {
            if (row.parentKey() == null) {
                continue;
            }
            DependencyNode parent = built.get(row.parentKey());
            DependencyNode child = built.get(row.nodeKey());
            if (parent != null && child != null) {
                parent.getChildren().add(child);
            }
        }
        return Optional.ofNullable(built.get("root"));
    }
}
