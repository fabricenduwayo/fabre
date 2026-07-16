package com.trailswitch.model;

public record RouteRule(
        String ruleId,
        String edgeId,
        int rulePriority,
        String lockSw1,
        String lockSw2,
        String ruleAction,
        String matchRelayId,
        String matchRelayState) {}
