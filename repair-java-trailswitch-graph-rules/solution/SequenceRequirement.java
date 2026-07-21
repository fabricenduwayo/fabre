package com.trailswitch.model;

public record SequenceRequirement(
        String ruleId,
        int requirementOrder,
        String sequenceId,
        String freshnessRelayId,
        Integer minTransitionsSince,
        Integer maxTransitionsSince,
        String witnessRelayId) {}
