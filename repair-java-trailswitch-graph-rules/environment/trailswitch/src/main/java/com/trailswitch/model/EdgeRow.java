package com.trailswitch.model;

public record EdgeRow(
        String edgeId,
        String fromStation,
        String toStation,
        String requiresSw1,
        String requiresSw2) {}
