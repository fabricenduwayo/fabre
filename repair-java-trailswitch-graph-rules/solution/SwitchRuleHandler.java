package com.trailswitch.service;

import com.trailswitch.model.RelayTransition;
import com.trailswitch.model.RouteRule;
import com.trailswitch.model.SequenceGrant;
import com.trailswitch.model.SequenceRequirement;
import com.trailswitch.repo.GraphPathRepository;
import com.trailswitch.repo.GraphPathRepository.LockGroupSpec;
import java.util.ArrayList;
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
            Set<String> visitedStations,
            Map<String, SequenceGrant> sequenceGrants,
            Map<String, Integer> relayResetEpochs) {
        Set<String> locked = new HashSet<>();
        List<RouteRule> rules = repository.loadRules();
        Map<String, Boolean> edgeDecided = new HashMap<>();
        for (RouteRule rule : rules) {
            if (edgeDecided.containsKey(rule.edgeId())) {
                continue;
            }
            if (ruleMatches(
                    switches,
                    relayState,
                    transitionCounts,
                    visitedStations,
                    sequenceGrants,
                    relayResetEpochs,
                    rule)) {
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

    public SearchAdvanceResult advanceState(
            String traversedEdge,
            Map<String, String> relayState,
            Map<String, Integer> transitionCounts,
            Map<String, Integer> sequenceProgress,
            Map<String, SequenceGrant> sequenceGrants,
            Map<String, Integer> relayResetEpochs,
            Map<String, String> initialRelays) {
        Map<String, String> nextRelays = new HashMap<>(relayState);
        Map<String, Integer> nextCounts = new HashMap<>(transitionCounts);
        Map<String, Integer> nextResetEpochs = new HashMap<>(relayResetEpochs);
        for (RelayTransition transition : repository.loadRelayTransitions(traversedEdge)) {
            if (transition.requiresSequenceId() != null) {
                if (transition.requiresSequenceProgress() == null) {
                    if (!sequenceGrants.containsKey(transition.requiresSequenceId())) {
                        continue;
                    }
                } else if (sequenceProgress.getOrDefault(
                                transition.requiresSequenceId(), 0)
                        != transition.requiresSequenceProgress()) {
                    continue;
                }
            }
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
                String initial = initialRelays.getOrDefault(transition.relayId(), "");
                if (transition.toState().equalsIgnoreCase(initial)
                        && nextCounts.getOrDefault(transition.relayId(), 0) > 0) {
                    nextResetEpochs.merge(transition.relayId(), 1, Integer::sum);
                }
            }
        }

        Map<String, Integer> nextProgress = new HashMap<>(sequenceProgress);
        Map<String, SequenceGrant> nextGrants = new HashMap<>(sequenceGrants);
        for (Map.Entry<String, List<String>> entry :
                repository.loadReleaseSequences().entrySet()) {
            List<String> steps = entry.getValue();
            if (steps.isEmpty()) {
                continue;
            }
            int progress = nextProgress.getOrDefault(entry.getKey(), 0);
            if (progress >= steps.size()) {
                progress = 0;
            }
            if (traversedEdge.equals(steps.get(progress))) {
                progress++;
            } else if (traversedEdge.equals(steps.get(0))) {
                progress = 1;
            } else {
                progress = 0;
            }
            if (progress == steps.size()) {
                nextGrants.put(
                        entry.getKey(),
                        issueGrant(entry.getKey(), nextResetEpochs, nextCounts));
                progress = 0;
            }
            nextProgress.put(entry.getKey(), progress);
        }

        voidStaleGrants(nextResetEpochs, nextGrants);
        return new SearchAdvanceResult(
                Map.copyOf(nextRelays),
                Map.copyOf(nextCounts),
                Map.copyOf(nextProgress),
                Map.copyOf(nextGrants),
                Map.copyOf(nextResetEpochs));
    }

    private SequenceGrant issueGrant(
            String sequenceId,
            Map<String, Integer> resetEpochs,
            Map<String, Integer> transitionCounts) {
        Map<String, Integer> epochsAtGrant = new HashMap<>();
        Map<String, Integer> countsAtGrant = new HashMap<>();
        for (String relayId :
                    repository.loadSequenceRelayDependencies()
                            .getOrDefault(sequenceId, Set.of())) {
            epochsAtGrant.put(relayId, resetEpochs.getOrDefault(relayId, 0));
            countsAtGrant.put(relayId, transitionCounts.getOrDefault(relayId, 0));
        }
        return new SequenceGrant(
                sequenceId,
                Map.copyOf(epochsAtGrant),
                Map.copyOf(countsAtGrant),
                Map.copyOf(resetEpochs));
    }

    private void voidStaleGrants(
            Map<String, Integer> resetEpochs, Map<String, SequenceGrant> sequenceGrants) {
        List<String> stale = new ArrayList<>();
        Map<String, Set<String>> dependencies = repository.loadSequenceRelayDependencies();
        for (Map.Entry<String, SequenceGrant> entry : sequenceGrants.entrySet()) {
            SequenceGrant grant = entry.getValue();
            for (String relayId : dependencies.getOrDefault(grant.sequenceId(), Set.of())) {
                int grantEpoch = grant.resetEpochsAtGrant().getOrDefault(relayId, 0);
                int currentEpoch = resetEpochs.getOrDefault(relayId, 0);
                if (grantEpoch < currentEpoch) {
                    stale.add(entry.getKey());
                    break;
                }
            }
        }
        stale.forEach(sequenceGrants::remove);
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
            Map<String, SequenceGrant> sequenceGrants,
            Map<String, Integer> relayResetEpochs,
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
        if (rule.countRelayId() != null && rule.maxTransitionCount() != null) {
            int count = transitionCounts.getOrDefault(rule.countRelayId(), 0);
            if (count > rule.maxTransitionCount()) {
                return false;
            }
        }
        for (SequenceRequirement requirement : requirementsForRule(rule)) {
            if (!sequenceRequirementSatisfied(
                    requirement, sequenceGrants, transitionCounts, relayResetEpochs)) {
                return false;
            }
        }
        return rule.lockSw1() != null
                || rule.lockSw2() != null
                || rule.matchRelayId() != null
                || rule.requiresVisitedStation() != null
                || rule.countRelayId() != null
                || rule.requiresCompletedSequence() != null
                || repository.loadSequenceRequirements().containsKey(rule.ruleId());
    }

    private List<SequenceRequirement> requirementsForRule(RouteRule rule) {
        List<SequenceRequirement> requirements =
                new ArrayList<>(
                        repository.loadSequenceRequirements().getOrDefault(rule.ruleId(), List.of()));
        if (rule.requiresCompletedSequence() != null) {
            requirements.add(
                    new SequenceRequirement(
                            rule.ruleId(),
                            0,
                            rule.requiresCompletedSequence(),
                            null,
                            null,
                            null,
                            null));
        }
        return requirements;
    }

    private boolean sequenceRequirementSatisfied(
            SequenceRequirement requirement,
            Map<String, SequenceGrant> sequenceGrants,
            Map<String, Integer> transitionCounts,
            Map<String, Integer> relayResetEpochs) {
        SequenceGrant grant = sequenceGrants.get(requirement.sequenceId());
        if (grant == null) {
            return false;
        }
        if (requirement.witnessRelayId() != null) {
            int currentEpoch = relayResetEpochs.getOrDefault(requirement.witnessRelayId(), 0);
            int atGrant = grant.witnessEpochsAtGrant().getOrDefault(requirement.witnessRelayId(), 0);
            if (currentEpoch > atGrant) {
                return false;
            }
        }
        if (requirement.freshnessRelayId() == null) {
            return true;
        }
        int current = transitionCounts.getOrDefault(requirement.freshnessRelayId(), 0);
        int atGrant =
                grant.transitionCountsAtGrant().getOrDefault(requirement.freshnessRelayId(), 0);
        int since = current - atGrant;
        if (requirement.minTransitionsSince() != null && since < requirement.minTransitionsSince()) {
            return false;
        }
        if (requirement.maxTransitionsSince() != null && since > requirement.maxTransitionsSince()) {
            return false;
        }
        return true;
    }

    public record SearchAdvanceResult(
            Map<String, String> relays,
            Map<String, Integer> transitionCounts,
            Map<String, Integer> sequenceProgress,
            Map<String, SequenceGrant> sequenceGrants,
            Map<String, Integer> relayResetEpochs) {}
}
