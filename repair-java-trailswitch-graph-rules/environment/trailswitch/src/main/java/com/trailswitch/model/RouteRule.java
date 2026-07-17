package com.trailswitch.model;

public record RouteRule(
        String ruleId,
        String edgeId,
        int rulePriority,
        String lockSw1,
        String lockSw2,
        String ruleAction,
        String matchRelayId,
        String matchRelayState,
        String countRelayId,
        Integer minTransitionCount,
        Integer maxTransitionCount,
        String requiresVisitedStation,
        String requiresCompletedSequence) {}
