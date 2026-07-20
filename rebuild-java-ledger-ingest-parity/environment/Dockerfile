FROM public.ecr.aws/docker/library/python:3.13-slim-bookworm@sha256:01f42367a0a94ad4bc17111776fd66e3500c1d87c15bbd6055b7371d39c124fb AS legacy-build
# platform-revision: 2026-07-20-r1
RUN apt-get update \
    && apt-get install -y --no-install-recommends openjdk-17-jdk-headless=17.0.15+6-1~deb12u1 \
    && rm -rf /var/lib/apt/lists/*
COPY lib/ /build/lib/
COPY legacy-src/ /build/src/
RUN mkdir -p /build/classes \
    && find /build/src -name '*.java' > /build/sources.txt \
    && javac --release 17 -encoding UTF-8 -g:none -cp "/build/lib/*" -d /build/classes @/build/sources.txt \
    && printf 'Main-Class: com.snorkel.legacy.Main\n' > /build/manifest.txt \
    && jar --create --file /build/ledger-oracle.jar --manifest /build/manifest.txt -C /build/classes .

FROM public.ecr.aws/docker/library/python:3.13-slim-bookworm@sha256:01f42367a0a94ad4bc17111776fd66e3500c1d87c15bbd6055b7371d39c124fb
ENV TZ=UTC
ENV LANG=C.UTF-8
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        openjdk-17-jdk-headless=17.0.15+6-1~deb12u1 \
        tmux=3.3a-1 \
        asciinema=2.2.0-1 \
        procps=2:4.0.2-3 \
        curl=7.88.1-10+deb12u12 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir --require-hashes --no-deps -r /tmp/requirements.txt \
    && rm /tmp/requirements.txt

COPY lib/ /app/lib/
COPY ingest/ /app/ingest/
COPY ledger-db/schema.sql /app/ledger-db/schema.sql
COPY samples/ /app/samples/

# Only the built artefact crosses over; the legacy sources stay in the discarded stage.
COPY --from=legacy-build /build/ledger-oracle.jar /opt/legacy/ledger-oracle.jar

RUN chmod +x /app/ingest/build.sh /app/ingest/run.sh \
    && java -cp "/app/lib/h2-2.2.224.jar" org.h2.tools.RunScript \
        -url jdbc:h2:file:/app/ledger-db/ledger -user sa -script /app/ledger-db/schema.sql \
    && chmod 0666 /app/ledger-db/ledger.mv.db

WORKDIR /app
