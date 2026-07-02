package com.audit;

import static org.junit.jupiter.api.Assertions.assertTrue;

import java.nio.file.Files;
import java.nio.file.Path;
import net.jqwik.api.ForAll;
import net.jqwik.api.Property;
import net.jqwik.api.Provide;
import net.jqwik.api.Arbitraries;
import net.jqwik.api.Arbitrary;

class MavenArtifactProperties {
    @Provide
    Arbitrary<String> centralCoordinates() {
        return Arbitraries.of(
                "org.springframework.boot:spring-boot-starter-web:3.2.5",
                "com.h2database:h2:2.2.224",
                "net.jqwik:jqwik:1.8.2");
    }

    @Property
    void coordinateHasThreeGavSegments(@ForAll("centralCoordinates") String coordinate) {
        String[] parts = coordinate.split(":");
        assertTrue(parts.length == 3);
        assertTrue(parts[0].contains("."));
        assertTrue(!parts[1].isBlank());
        assertTrue(parts[2].matches("\\d+\\.\\d+\\.\\d+"));
    }

    @Property
    void localRepositoryContainsResolvedArtifact(@ForAll("centralCoordinates") String coordinate)
            throws Exception {
        String[] parts = coordinate.split(":");
        String groupPath = parts[0].replace('.', '/');
        Path base = Path.of(System.getProperty("user.home"), ".m2", "repository", groupPath, parts[1], parts[2]);
        Path pom = base.resolve(parts[1] + "-" + parts[2] + ".pom");
        Path jar = base.resolve(parts[1] + "-" + parts[2] + ".jar");
        assertTrue(Files.exists(pom), "missing pom for " + coordinate + " at " + pom);
        assertTrue(Files.exists(jar), "missing jar for " + coordinate + " under " + base);
    }
}
