package com.trailswitch.model;

public record RelayTransition(
        String edgeId,
        int transitionOrder,
        String relayId,
        String fromState,
        String toState) {}
