package com.trailswitch.service;

import com.trailswitch.model.RouteRule;
import com.trailswitch.repo.GraphPathRepository;
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
        for (RouteRule rule : rules) {
            if (!ruleMatches(switches, rule)) {
                continue;
            }
            if ("clear".equalsIgnoreCase(rule.ruleAction())) {
                locked.remove(rule.edgeId());
            } else {
                locked.add(rule.edgeId());
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
        if (rule.lockSw1() != null
                && !switches.getOrDefault("sw1", "").equalsIgnoreCase(rule.lockSw1())) {
            return false;
        }
        if (rule.lockSw2() != null
                && !switches.getOrDefault("sw2", "").equalsIgnoreCase(rule.lockSw2())) {
            return false;
        }
        return rule.lockSw1() != null || rule.lockSw2() != null;
    }
}
