FROM public.ecr.aws/docker/library/python:3.13-slim-bookworm@sha256:01f42367a0a94ad4bc17111776fd66e3500c1d87c15bbd6055b7371d39c124fb
# Canonical Python runtime is required by Harbor's pytest verifier; the same
# container runs the Java 17 service, so the JDK and Maven are installed by apt.
# platform-revision: 2026-07-19-r67

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        openjdk-17-jdk-headless \
        maven \
        postgresql \
        postgresql-client \
        curl \
        procps \
        tmux \
        asciinema \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir --require-hashes --no-deps -r /tmp/requirements.txt

COPY sql/ /app/sql/
COPY docs/ /app/docs/
COPY trailswitch/ /app/trailswitch/

RUN chmod +x /app/sql/init_db.sh /app/trailswitch/build.sh /app/trailswitch/start.sh \
    && pg_ctlcluster 15 main start \
    && runuser -u postgres -- psql -c "CREATE USER trailswitch WITH PASSWORD 'trailswitch';" \
    && runuser -u postgres -- psql -c "CREATE DATABASE trailswitch OWNER trailswitch;" \
    && runuser -u postgres -- psql -d trailswitch -f /app/sql/schema.sql \
    && runuser -u postgres -- psql -d trailswitch -f /app/sql/seed.sql \
    && pg_ctlcluster 15 main stop \
    && bash /app/trailswitch/build.sh

EXPOSE 8080
