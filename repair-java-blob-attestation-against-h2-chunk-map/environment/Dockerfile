FROM public.ecr.aws/docker/library/python:3.13-slim-bookworm@sha256:01f42367a0a94ad4bc17111776fd66e3500c1d87c15bbd6055b7371d39c124fb
# Canonical Python runtime is required by Harbor's pytest verifier; the same
# image runs the Java 17 auditor, the blob-store service, and H2 tooling, so the
# JDK is installed by apt.
# platform-revision: 2026-07-19-r19

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        openjdk-17-jdk-headless \
        curl \
        procps \
        tmux \
        asciinema \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir --require-hashes --no-deps -r /tmp/requirements.txt \
    && rm -f /tmp/requirements.txt

COPY lib/ /app/lib/

COPY attest-objects/ /app/attest-objects/
RUN chmod +x /app/attest-objects/build.sh \
    && bash /app/attest-objects/build.sh

COPY blob-store/ /app/blob-store/
RUN chmod +x /app/blob-store/build.sh \
    && bash /app/blob-store/build.sh

# Build the shipped store: schema and seed load into an H2 file whose blob and
# chunk files sit alongside it under /app/store.
COPY store-db/ /app/store-db/
COPY store/ /app/store/
RUN java -cp "/app/lib/h2-2.2.224.jar" org.h2.tools.RunScript \
        -url "jdbc:h2:file:/app/store/objects" -user sa -script /app/store-db/schema.sql \
    && java -cp "/app/lib/h2-2.2.224.jar" org.h2.tools.RunScript \
        -url "jdbc:h2:file:/app/store/objects" -user sa -script /app/store-db/seed.sql \
    && chmod 0666 /app/store/objects.mv.db \
    && mkdir -p /app/build

COPY start-blob-store.sh /app/start-blob-store.sh
COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /app/start-blob-store.sh /usr/local/bin/entrypoint.sh

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
CMD ["sleep", "infinity"]
