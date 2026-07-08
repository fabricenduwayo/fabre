FROM public.ecr.aws/docker/library/python:3.13-slim-bookworm@sha256:01f42367a0a94ad4bc17111776fd66e3500c1d87c15bbd6055b7371d39c124fb
# platform-revision: 2026-07-07-r1

WORKDIR /app

# JDK 17 + Maven for the two Java projects, plus the agent runtime tooling.
# Common Debian packages are left unpinned: bookworm serves a single version of
# each and the digest-pinned base fixes the snapshot, so this stays reproducible.
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        openjdk-17-jdk-headless \
        maven \
        curl \
        procps \
        tmux \
        asciinema \
    && rm -rf /var/lib/apt/lists/*

# Fully pinned, hash-locked verifier dependencies (pytest, pytest-json-ctrf,
# jsonschema, and their transitive deps).
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir --require-hashes --no-deps -r /tmp/requirements.txt \
    && rm -f /tmp/requirements.txt

# Both Maven projects. A full `mvn package` per project at build time warms
# /root/.m2 with every dependency and plugin artifact (so `mvn -o` works at
# runtime with allow_internet=false), runs the registry JUnit suite, and
# produces both jars. dependency:go-offline hardens offline resolution.
COPY model-registry/ /app/model-registry/
COPY reconcile-model-release/ /app/reconcile-model-release/
RUN mvn -B -q -f /app/model-registry/pom.xml package \
    && mvn -B -q -f /app/reconcile-model-release/pom.xml package \
    && mvn -B -q -f /app/model-registry/pom.xml dependency:go-offline \
    && mvn -B -q -f /app/reconcile-model-release/pom.xml dependency:go-offline

# Keep a fixed-path copy of the H2 driver jar for command-line JDBC access.
RUN mkdir -p /app/lib \
    && cp /root/.m2/repository/com/h2database/h2/2.2.224/h2-2.2.224.jar /app/lib/h2-2.2.224.jar

# Policy bundle and the decision-manifest JSON Schema.
COPY policy/promotion-policy.md /app/policy/promotion-policy.md
COPY schemas/release-decision.schema.json /app/schemas/release-decision.schema.json

# Seed the embedded H2 experiment database at build time, then delete the SQL
# so the canonical metrics, lineage history, and calibration evidence are
# reachable only through JDBC against the binary store — not by reading a dump.
COPY experiment-db/schema.sql /tmp/schema.sql
COPY experiment-db/seed.sql /tmp/seed.sql
RUN mkdir -p /app/experiment-db \
    && java -cp /app/lib/h2-2.2.224.jar org.h2.tools.RunScript \
        -url "jdbc:h2:file:/app/experiment-db/experiments" -user sa -script /tmp/schema.sql \
    && java -cp /app/lib/h2-2.2.224.jar org.h2.tools.RunScript \
        -url "jdbc:h2:file:/app/experiment-db/experiments" -user sa -script /tmp/seed.sql \
    && chmod 0666 /app/experiment-db/experiments.mv.db \
    && rm -f /tmp/schema.sql /tmp/seed.sql

# Registry service launcher (also usable by the agent to restart the API) and
# the container entrypoint that boots it before handing over to the command.
COPY start-registry.sh /app/start-registry.sh
COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /app/start-registry.sh /usr/local/bin/entrypoint.sh

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
CMD ["sleep", "infinity"]

WORKDIR /app
