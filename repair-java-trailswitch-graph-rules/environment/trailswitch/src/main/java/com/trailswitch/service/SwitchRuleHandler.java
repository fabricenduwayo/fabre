package com.trailswitch.service;

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

    public Set<String> lockedEdges(Map<String, String> switches) {
        Set<String> locked = new HashSet<>();
        applyLockGroups(locked);
        List<RouteRule> rules = repository.loadRules();
        Map<String, Boolean> edgeDecided = new HashMap<>();
        for (RouteRule rule : rules) {
            if (edgeDecided.containsKey(rule.edgeId())) {
                continue;
            }
            if (ruleMatches(switches, rule)) {
                if ("clear".equalsIgnoreCase(rule.ruleAction())) {
                    locked.add(rule.edgeId());
                    edgeDecided.put(rule.edgeId(), true);
                    continue;
                }
                locked.add(rule.edgeId());
                edgeDecided.put(rule.edgeId(), true);
            } else {
                edgeDecided.put(rule.edgeId(), true);
            }
        }
        return locked;
    }

    private void applyLockGroups(Set<String> locked) {
        Map<String, Set<String>> groups = repository.loadLockGroups();
        for (Set<String> edges : groups.values()) {
            boolean triggered = false;
            for (String edgeId : edges) {
                if (locked.contains(edgeId)) {
                    triggered = true;
                    break;
                }
            }
            if (triggered) {
                locked.addAll(edges);
            }
        }
    }

    private boolean ruleMatches(Map<String, String> switches, RouteRule rule) {
        boolean matched = false;
        if (rule.lockSw1() != null) {
            matched = switches.getOrDefault("sw1", "").equalsIgnoreCase(rule.lockSw1());
        }
        if (rule.lockSw2() != null) {
            matched = matched || switches.getOrDefault("sw2", "").equalsIgnoreCase(rule.lockSw2());
        }
        return matched;
    }
}
