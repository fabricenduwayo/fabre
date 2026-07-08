FROM public.ecr.aws/docker/library/python:3.13-slim-bookworm@sha256:01f42367a0a94ad4bc17111776fd66e3500c1d87c15bbd6055b7371d39c124fb
# platform-revision: 2026-07-08-r19

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        ca-certificates \
        nodejs \
        npm \
        procps \
        tmux \
        asciinema \
    && npm install -g pnpm@9.15.4 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir --require-hashes --no-deps -r /tmp/requirements.txt

COPY referee/package.json referee/pnpm-lock.yaml /app/referee/
WORKDIR /app/referee
RUN pnpm install --frozen-lockfile --prod

COPY referee/src/ /app/referee/src/
COPY referee/start.sh /app/referee/start.sh
COPY worker/ /app/worker/
COPY data/ /app/data/
COPY docs/ /app/docs/

WORKDIR /app

RUN chmod +x /app/referee/start.sh \
    && mkdir -p /app/output
