package com.audit.model;

import java.util.ArrayList;
import java.util.List;

public class DependencyNode {
    private String groupId;
    private String artifactId;
    private String version;
    private String scope;
    private List<DependencyNode> children = new ArrayList<>();

    public String getGroupId() {
        return groupId;
    }

    public void setGroupId(String groupId) {
        this.groupId = groupId;
    }

    public String getArtifactId() {
        return artifactId;
    }

    public void setArtifactId(String artifactId) {
        this.artifactId = artifactId;
    }

    public String getVersion() {
        return version;
    }

    public void setVersion(String version) {
        this.version = version;
    }

    public String getScope() {
        return scope;
    }

    public void setScope(String scope) {
        this.scope = scope;
    }

    public List<DependencyNode> getChildren() {
        return children;
    }

    public void setChildren(List<DependencyNode> children) {
        this.children = children;
    }
}
