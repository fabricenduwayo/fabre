FROM public.ecr.aws/docker/library/python:3.13-slim-bookworm@sha256:01f42367a0a94ad4bc17111776fd66e3500c1d87c15bbd6055b7371d39c124fb
# platform-revision: 2026-07-16-r2

WORKDIR /app

# JRE for the prebuilt registry jar and H2 tooling; Python drives reconciliation.
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        openjdk-17-jre-headless \
        curl \
        procps \
        tmux \
        asciinema \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir --require-hashes --no-deps -r /tmp/requirements.txt \
    && rm -f /tmp/requirements.txt

COPY reconcile-model-release/reconcile.py /app/reconcile-model-release/reconcile.py
RUN chmod +x /app/reconcile-model-release/reconcile.py

RUN mkdir -p /app/model-registry/target
COPY model-registry/target/model-registry-0.1.0.jar /app/model-registry/target/model-registry-0.1.0.jar

RUN mkdir -p /app/lib
COPY h2-2.2.224.jar /app/lib/h2-2.2.224.jar

COPY policy/promotion-policy.md /app/policy/promotion-policy.md
COPY policy/promotion-policy-amendments.md /app/policy/promotion-policy-amendments.md
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
