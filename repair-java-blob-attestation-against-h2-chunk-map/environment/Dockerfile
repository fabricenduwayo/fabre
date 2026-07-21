FROM public.ecr.aws/docker/library/python:3.13-slim-bookworm@sha256:01f42367a0a94ad4bc17111776fd66e3500c1d87c15bbd6055b7371d39c124fb
# Canonical Python runtime is required by Harbor's pytest verifier; the same
# image runs the Java 17 auditor, the reference attestor, and H2 tooling, so the
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
    && apt-get clean
# The apt package index is kept on purpose. The agent harness runs
# "apt-get update && apt-get install -y curl procps" at setup; if that runs with
# a degraded network it needs the cached index to see curl and procps are already
# present, otherwise the install aborts and the agent never starts.

COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir --require-hashes --no-deps -r /tmp/requirements.txt \
    && rm -f /tmp/requirements.txt

COPY lib/ /app/lib/

COPY attest-objects/ /app/attest-objects/
RUN chmod +x /app/attest-objects/build.sh \
    && bash /app/attest-objects/build.sh

COPY policy/ /app/policy/

# The reference attestor. It produces the correct report for any store; the agent
# works out how it decides and reimplements it, and the verifier moves it out of
# the way before grading so parity comes from the agent's own control.
COPY ref/ /app/ref/
RUN chmod +x /app/ref/attest-ref /app/ref/attest-ref-*

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

COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
CMD ["sleep", "infinity"]
