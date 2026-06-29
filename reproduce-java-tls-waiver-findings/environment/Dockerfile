FROM public.ecr.aws/docker/library/python:3.13-slim-bookworm@sha256:01f42367a0a94ad4bc17111776fd66e3500c1d87c15bbd6055b7371d39c124fb
# platform-revision: 2026-06-29-r2

WORKDIR /app

# JDK 17 plus the agent runtime tooling. Common Debian packages are left
# unpinned: bookworm serves a single version of each, and the digest-pinned base
# image fixes the snapshot, so this stays reproducible while avoiding build
# breaks when a point release supersedes a pinned security version in the mirror.
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        openjdk-17-jdk-headless \
        procps \
        tmux \
        asciinema \
    && rm -rf /var/lib/apt/lists/*

# Fully pinned, hash-locked verifier dependencies (pytest, pytest-json-ctrf,
# jsonschema, and their transitive deps).
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir --require-hashes --no-deps -r /tmp/requirements.txt

# Vendored offline jars (H2, Jackson core/databind/yaml/toml, networknt schema
# validator), the long narrative report, the YAML/TOML config set, and the JSON
# schemas. Nothing is fetched from the network at build or run time.
COPY lib/ /app/lib/
COPY reports/ /app/reports/
COPY config/ /app/config/
COPY schema/ /app/schema/

# Starter pipeline scaffold (Main dispatcher + stubbed decode/join/validate
# stages + build.sh). The agent extends these stubs; it carries no solution logic.
COPY pipeline/ /app/pipeline/

# Seed the H2 inventory database from SQL at build time, then delete the SQL so
# the service inventory, certificate facts, and probe evidence are reachable only
# through JDBC against the binary H2 store — not by reading a text dump.
COPY data/seed.sql /tmp/seed.sql
RUN mkdir -p /app/data \
    && java -cp "/app/lib/h2-2.2.224.jar" org.h2.tools.RunScript \
        -url "jdbc:h2:/app/data/mariner" -user sa -script /tmp/seed.sql \
    && rm -f /tmp/seed.sql
