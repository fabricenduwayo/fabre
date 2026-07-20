FROM public.ecr.aws/docker/library/python:3.13-slim-bookworm@sha256:01f42367a0a94ad4bc17111776fd66e3500c1d87c15bbd6055b7371d39c124fb
# platform-revision: 2026-07-20-r1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        openjdk-17-jdk-headless \
        curl \
        procps \
        tmux \
        asciinema \
    && rm -rf /var/lib/apt/lists/*

ENV TZ=UTC
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir --require-hashes --no-deps -r /tmp/requirements.txt \
    && rm -f /tmp/requirements.txt

COPY lib/ /app/lib/
COPY artifact-api/ /app/artifact-api/
COPY attest-worker/ /app/attest-worker/
RUN chmod +x /app/artifact-api/build.sh /app/attest-worker/build.sh \
    && bash /app/artifact-api/build.sh \
    && bash /app/attest-worker/build.sh

COPY policy/signing-trust-policy.md /app/policy/signing-trust-policy.md
COPY policy/signing-trust-amendments.md /app/policy/signing-trust-amendments.md
COPY attestation-db/schema.sql /app/attestation-db/schema.sql
COPY attestation-db/seed.sql /app/attestation-db/seed.sql
RUN mkdir -p /app/attestation-db \
    && java -cp /app/lib/h2-2.2.224.jar org.h2.tools.RunScript \
        -url jdbc:h2:file:/app/attestation-db/attestation -user sa -script /app/attestation-db/schema.sql \
    && java -cp /app/lib/h2-2.2.224.jar org.h2.tools.RunScript \
        -url jdbc:h2:file:/app/attestation-db/attestation -user sa -script /app/attestation-db/seed.sql \
    && chmod 0666 /app/attestation-db/attestation.mv.db

COPY start-api.sh /app/start-api.sh
COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /app/start-api.sh /usr/local/bin/entrypoint.sh

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
CMD ["sleep", "infinity"]
