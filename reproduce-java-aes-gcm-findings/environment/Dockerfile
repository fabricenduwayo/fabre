FROM public.ecr.aws/docker/library/python:3.13-slim-bookworm@sha256:01f42367a0a94ad4bc17111776fd66e3500c1d87c15bbd6055b7371d39c124fb
# platform-revision: 2026-07-01-r26

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        openjdk-17-jdk-headless \
        sqlite3 \
        procps \
        tmux \
        asciinema \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir --require-hashes --no-deps -r /tmp/requirements.txt

COPY lib/ /app/lib/
COPY reports/ /app/reports/
COPY config/ /app/config/
COPY schema/ /app/schema/
COPY fixtures/ /app/fixtures/

# Starter pipeline scaffold (Main dispatcher + broken rules/correlate + decrypt
# stub + build.sh). The agent repairs rules/correlate; it carries no solution logic.
COPY pipeline/ /app/pipeline/

COPY data/seed.sql /tmp/seed.sql
RUN mkdir -p /app/data \
    && sqlite3 /app/data/forensic_audit.db < /tmp/seed.sql \
    && rm -f /tmp/seed.sql
