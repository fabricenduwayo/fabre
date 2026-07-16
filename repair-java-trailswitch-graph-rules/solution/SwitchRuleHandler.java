package com.trailswitch.service;

import com.trailswitch.model.RelayTransition;
import com.trailswitch.model.RouteRule;
import com.trailswitch.repo.GraphPathRepository;
import com.trailswitch.repo.GraphPathRepository.LockGroupSpec;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import org.springframework.stereotype.Service;

@Service
public class SwitchRuleHandler {
    private final GraphPathRepository repository;

    public SwitchRuleHandler(GraphPathRepository repository) {
        this.repository = repository;
    }

    public Set<String> lockedEdges(
            Map<String, String> switches,
            Map<String, String> relayState,
            Map<String, Integer> transitionCounts,
            Set<String> visitedStations) {
        Set<String> locked = new HashSet<>();
        List<RouteRule> rules = repository.loadRules();
        Map<String, Boolean> edgeDecided = new HashMap<>();
        for (RouteRule rule : rules) {
            if (edgeDecided.containsKey(rule.edgeId())) {
                continue;
            }
            if (ruleMatches(switches, relayState, transitionCounts, visitedStations, rule)) {
                if ("clear".equalsIgnoreCase(rule.ruleAction())) {
                    edgeDecided.put(rule.edgeId(), true);
                    continue;
                }
                locked.add(rule.edgeId());
                edgeDecided.put(rule.edgeId(), true);
            }
        }
        applyLockGroups(locked, relayState);
        return locked;
    }

    public RelayAdvanceResult advanceRelays(
            String traversedEdge, Map<String, String> relayState, Map<String, Integer> transitionCounts) {
        Map<String, String> nextRelays = new HashMap<>(relayState);
        Map<String, Integer> nextCounts = new HashMap<>(transitionCounts);
        for (RelayTransition transition : repository.loadRelayTransitions(traversedEdge)) {
            if (transition.requiresRelayId() != null) {
                String required =
                        nextRelays.getOrDefault(transition.requiresRelayId(), "");
                if (!required.equalsIgnoreCase(transition.requiresRelayState())) {
                    continue;
                }
            }
            String current = nextRelays.getOrDefault(transition.relayId(), transition.fromState());
            if (current.equalsIgnoreCase(transition.fromState())) {
                nextRelays.put(transition.relayId(), transition.toState());
                nextCounts.merge(transition.relayId(), 1, Integer::sum);
            }
        }
        return new RelayAdvanceResult(Map.copyOf(nextRelays), Map.copyOf(nextCounts));
    }

    private void applyLockGroups(Set<String> locked, Map<String, String> relayState) {
        Map<String, LockGroupSpec> groups = repository.loadLockGroups();
        boolean changed;
        do {
            changed = false;
            for (LockGroupSpec group : groups.values()) {
                if (!groupArmed(group, relayState)) {
                    continue;
                }
                boolean triggered = false;
                for (String edgeId : group.edges()) {
                    if (locked.contains(edgeId)) {
                        triggered = true;
                        break;
                    }
                }
                if (triggered) {
                    for (String edgeId : group.edges()) {
                        if (locked.add(edgeId)) {
                            changed = true;
                        }
                    }
                }
            }
        } while (changed);
    }

    private boolean groupArmed(LockGroupSpec group, Map<String, String> relayState) {
        if (group.armRelayId() == null) {
            return true;
        }
        String current = relayState.getOrDefault(group.armRelayId(), "");
        return current.equalsIgnoreCase(group.armRelayState());
    }

    private boolean ruleMatches(
            Map<String, String> switches,
            Map<String, String> relayState,
            Map<String, Integer> transitionCounts,
            Set<String> visitedStations,
            RouteRule rule) {
        if (rule.lockSw1() != null
                && !switches.getOrDefault("sw1", "").equalsIgnoreCase(rule.lockSw1())) {
            return false;
        }
        if (rule.lockSw2() != null
                && !switches.getOrDefault("sw2", "").equalsIgnoreCase(rule.lockSw2())) {
            return false;
        }
        if (rule.matchRelayId() != null) {
            String current = relayState.getOrDefault(rule.matchRelayId(), "");
            if (!current.equalsIgnoreCase(rule.matchRelayState())) {
                return false;
            }
        }
        if (rule.requiresVisitedStation() != null
                && !visitedStations.contains(rule.requiresVisitedStation())) {
            return false;
        }
        if (rule.countRelayId() != null && rule.minTransitionCount() != null) {
            int count = transitionCounts.getOrDefault(rule.countRelayId(), 0);
            if (count < rule.minTransitionCount()) {
                return false;
            }
        }
        return rule.lockSw1() != null
                || rule.lockSw2() != null
                || rule.matchRelayId() != null
                || rule.requiresVisitedStation() != null
                || rule.countRelayId() != null;
    }

    public record RelayAdvanceResult(Map<String, String> relays, Map<String, Integer> transitionCounts) {}
}
