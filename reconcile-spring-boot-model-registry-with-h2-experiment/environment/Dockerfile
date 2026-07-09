FROM public.ecr.aws/docker/library/python:3.13-slim-bookworm@sha256:01f42367a0a94ad4bc17111776fd66e3500c1d87c15bbd6055b7371d39c124fb
# platform-revision: 2026-07-09-r11

WORKDIR /app

# JDK 17 + Maven for the agent/oracle offline reconcile build, plus runtime tooling.
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

COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir --require-hashes --no-deps -r /tmp/requirements.txt \
    && rm -f /tmp/requirements.txt

# Pre-warmed offline Maven cache for the reconcile step only (no Spring Boot deps).
COPY maven-repo.tar.gz /tmp/maven-repo.tar.gz
RUN mkdir -p /root/.m2/repository \
    && tar -xzf /tmp/maven-repo.tar.gz -C /root/.m2/repository \
    && find /root/.m2/repository -name '._*' -delete \
    && find /root/.m2/repository -name '.DS_Store' -delete \
    && rm -f /tmp/maven-repo.tar.gz

# Reconcile skeleton ships as source; registry ships as a prebuilt jar only.
COPY reconcile-model-release/ /app/reconcile-model-release/

RUN mkdir -p /app/model-registry/target
COPY model-registry/target/model-registry-0.1.0.jar /app/model-registry/target/model-registry-0.1.0.jar

RUN mkdir -p /app/lib \
    && cp /root/.m2/repository/com/h2database/h2/2.2.224/h2-2.2.224.jar /app/lib/h2-2.2.224.jar

COPY policy/promotion-policy.md /app/policy/promotion-policy.md
COPY schemas/release-decision.schema.json /app/schemas/release-decision.schema.json

COPY experiment-db/experiments.mv.db /app/experiment-db/experiments.mv.db
RUN chmod 0666 /app/experiment-db/experiments.mv.db \
    && mkdir -p /app/build

COPY start-registry.sh /app/start-registry.sh
COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /app/start-registry.sh /usr/local/bin/entrypoint.sh

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
CMD ["sleep", "infinity"]

WORKDIR /app
