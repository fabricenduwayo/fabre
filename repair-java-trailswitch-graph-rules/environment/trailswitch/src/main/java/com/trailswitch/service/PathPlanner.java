package com.trailswitch.service;

import com.trailswitch.model.EdgeRow;
import com.trailswitch.repo.GraphPathRepository;
import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Queue;
import java.util.Set;
import org.springframework.stereotype.Service;

@Service
public class PathPlanner {
    private static final int MAX_DEPTH = 12;

    private final GraphPathRepository repository;
    private final SwitchRuleHandler ruleHandler;

    public PathPlanner(GraphPathRepository repository, SwitchRuleHandler ruleHandler) {
        this.repository = repository;
        this.ruleHandler = ruleHandler;
    }

    public PlanResult plan(String from, String to, Map<String, String> switches) {
        Set<String> locked = ruleHandler.lockedEdges(switches);
        Queue<String> queue = new ArrayDeque<>();
        Map<String, String> parent = new HashMap<>();
        Set<String> visited = new HashSet<>();
        queue.add(from);
        parent.put(from, null);

        while (!queue.isEmpty()) {
            String current = queue.poll();
            if (!visited.add(current)) {
                continue;
            }
            if (current.equals(to)) {
                return new PlanResult(true, rebuild(parent, to), true);
            }
            int depth = depthOf(parent, current);
            if (depth >= MAX_DEPTH) {
                continue;
            }
            for (EdgeRow edge : repository.loadOutgoing(current)) {
                if (locked.contains(edge.edgeId())) {
                    continue;
                }
                if (!edgeActive(edge, switches)) {
                    continue;
                }
                String next = edge.toStation();
                parent.put(next, current);
                queue.add(next);
            }
        }
        return new PlanResult(false, List.of(), true);
    }

    private int depthOf(Map<String, String> parent, String node) {
        int depth = 0;
        String walk = node;
        while (parent.get(walk) != null) {
            depth++;
            walk = parent.get(walk);
        }
        return depth;
    }

    private boolean edgeActive(EdgeRow edge, Map<String, String> switches) {
        if (edge.requiresSw1() != null
                && !edge.requiresSw1().equalsIgnoreCase(switches.getOrDefault("sw1", ""))) {
            return false;
        }
        if (edge.requiresSw2() != null
                && !edge.requiresSw2().equalsIgnoreCase(switches.getOrDefault("sw2", ""))) {
            return false;
        }
        return true;
    }

    private List<String> rebuild(Map<String, String> parent, String to) {
        List<String> path = new ArrayList<>();
        String walk = to;
        while (walk != null) {
            path.add(0, walk);
            walk = parent.get(walk);
        }
        return path;
    }

    public record PlanResult(boolean reachable, List<String> path, boolean cycleGuard) {}
}
