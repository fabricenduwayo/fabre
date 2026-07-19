package com.trailswitch.model;

import java.util.Map;

public record SequenceGrant(
        String sequenceId,
        Map<String, Integer> resetEpochsAtGrant,
        Map<String, Integer> transitionCountsAtGrant) {}
