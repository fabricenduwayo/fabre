package com.trailswitch.service;

import com.trailswitch.model.RelayTransition;
import com.trailswitch.model.RouteRule;
import com.trailswitch.repo.GraphPathRepository;
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

    public Set<String> lockedEdges(Map<String, String> switches, Map<String, String> relayState) {
        Set<String> locked = new HashSet<>();
        List<RouteRule> rules = repository.loadRules();
        Map<String, Boolean> edgeDecided = new HashMap<>();
        for (RouteRule rule : rules) {
            if (edgeDecided.containsKey(rule.edgeId())) {
                continue;
            }
            if (ruleMatches(switches, relayState, rule)) {
                if ("clear".equalsIgnoreCase(rule.ruleAction())) {
                    edgeDecided.put(rule.edgeId(), true);
                    continue;
                }
                locked.add(rule.edgeId());
                edgeDecided.put(rule.edgeId(), true);
            }
        }
        applyLockGroups(locked);
        return locked;
    }

    public Map<String, String> advanceRelays(String traversedEdge, Map<String, String> relayState) {
        Map<String, String> next = new HashMap<>(relayState);
        for (RelayTransition transition : repository.loadRelayTransitions(traversedEdge)) {
            String current = next.getOrDefault(transition.relayId(), transition.fromState());
            if (current.equalsIgnoreCase(transition.fromState())) {
                next.put(transition.relayId(), transition.toState());
            }
        }
        return Map.copyOf(next);
    }

    private void applyLockGroups(Set<String> locked) {
        Map<String, Set<String>> groups = repository.loadLockGroups();
        boolean changed;
        do {
            changed = false;
            for (Set<String> edges : groups.values()) {
                boolean triggered = false;
                for (String edgeId : edges) {
                    if (locked.contains(edgeId)) {
                        triggered = true;
                        break;
                    }
                }
                if (triggered) {
                    for (String edgeId : edges) {
                        if (locked.add(edgeId)) {
                            changed = true;
                        }
                    }
                }
            }
        } while (changed);
    }

    private boolean ruleMatches(
            Map<String, String> switches, Map<String, String> relayState, RouteRule rule) {
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
        return rule.lockSw1() != null || rule.lockSw2() != null || rule.matchRelayId() != null;
    }
}
