package com.trailswitch.service;

import com.trailswitch.model.EdgeRow;
import com.trailswitch.model.SequenceGrant;
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
    private static final int MAX_DEPTH = 24;

    private final GraphPathRepository repository;
    private final SwitchRuleHandler ruleHandler;

    public PathPlanner(GraphPathRepository repository, SwitchRuleHandler ruleHandler) {
        this.repository = repository;
        this.ruleHandler = ruleHandler;
    }

    public PlanResult plan(String from, String to, Map<String, String> switches) {
        Map<String, String> initialRelays = repository.loadRelayStates();
        SearchState start =
                new SearchState(
                        from,
                        initialRelays,
                        Map.of(),
                        Map.of(),
                        Map.of(),
                        Map.of(),
                        Set.of(from),
                        initialRelays);
        Queue<SearchState> queue = new ArrayDeque<>();
        Map<SearchState, SearchState> parent = new HashMap<>();
        Set<SearchState> discovered = new HashSet<>();
        queue.add(start);
        discovered.add(start);
        parent.put(start, null);

        while (!queue.isEmpty()) {
            SearchState current = queue.poll();
            if (current.station().equals(to)) {
                return new PlanResult(true, rebuild(parent, current), true);
            }
            if (depthOf(parent, current) >= MAX_DEPTH) {
                continue;
            }
            Set<String> locked =
                    ruleHandler.lockedEdges(
                            switches,
                            current.relays(),
                            current.transitionCounts(),
                            current.visited(),
                            current.sequenceGrants());
            for (EdgeRow edge : repository.loadOutgoing(current.station())) {
                if (locked.contains(edge.edgeId())) {
                    continue;
                }
                if (!edgeActive(edge, switches)) {
                    continue;
                }
                SwitchRuleHandler.SearchAdvanceResult advanced =
                        ruleHandler.advanceState(
                                edge.edgeId(),
                                current.relays(),
                                current.transitionCounts(),
                                current.sequenceProgress(),
                                current.sequenceGrants(),
                                current.relayResetEpochs(),
                                current.initialRelays());
                Set<String> nextVisited = new HashSet<>(current.visited());
                nextVisited.add(edge.toStation());
                SearchState next =
                        new SearchState(
                                edge.toStation(),
                                advanced.relays(),
                                advanced.transitionCounts(),
                                advanced.sequenceProgress(),
                                advanced.sequenceGrants(),
                                advanced.relayResetEpochs(),
                                nextVisited,
                                current.initialRelays());
                if (discovered.add(next)) {
                    parent.put(next, current);
                    queue.add(next);
                }
            }
        }
        return new PlanResult(false, List.of(), true);
    }

    private int depthOf(Map<SearchState, SearchState> parent, SearchState node) {
        int depth = 0;
        SearchState walk = node;
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

    private List<String> rebuild(Map<SearchState, SearchState> parent, SearchState goal) {
        List<String> path = new ArrayList<>();
        SearchState walk = goal;
        while (walk != null) {
            path.add(0, walk.station());
            walk = parent.get(walk);
        }
        return path;
    }

    public record PlanResult(boolean reachable, List<String> path, boolean cycleGuard) {}

    private record SearchState(
            String station,
            Map<String, String> relays,
            Map<String, Integer> transitionCounts,
            Map<String, Integer> sequenceProgress,
            Map<String, SequenceGrant> sequenceGrants,
            Map<String, Integer> relayResetEpochs,
            Set<String> visited,
            Map<String, String> initialRelays) {
        private SearchState {
            relays = Map.copyOf(relays);
            transitionCounts = Map.copyOf(transitionCounts);
            sequenceProgress = Map.copyOf(sequenceProgress);
            sequenceGrants = Map.copyOf(sequenceGrants);
            relayResetEpochs = Map.copyOf(relayResetEpochs);
            visited = Set.copyOf(visited);
            initialRelays = Map.copyOf(initialRelays);
        }
    }
}
