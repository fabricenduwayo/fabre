package com.audit.repo;

public record NodeRow(
        String nodeKey,
        String buildId,
        String parentKey,
        String groupId,
        String artifactId,
        String version,
        String scope,
        int ordinal) {}
