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
        List<RouteRule> rules = repository.loadRules();
        Map<String, Boolean> edgeDecided = new java.util.HashMap<>();
        for (RouteRule rule : rules) {
            if (edgeDecided.containsKey(rule.edgeId())) {
                continue;
            }
            if (ruleMatches(switches, rule)) {
                locked.add(rule.edgeId());
            }
            edgeDecided.put(rule.edgeId(), true);
        }
        return locked;
    }

    private boolean ruleMatches(Map<String, String> switches, RouteRule rule) {
        if (rule.lockSw1() != null
                && switches.getOrDefault("sw1", "").equalsIgnoreCase(rule.lockSw1())) {
            return true;
        }
        if (rule.lockSw2() != null
                && switches.getOrDefault("sw2", "").equalsIgnoreCase(rule.lockSw2())) {
            return true;
        }
        return false;
    }
}
