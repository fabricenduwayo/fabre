FROM public.ecr.aws/docker/library/python:3.13-slim-bookworm@sha256:01f42367a0a94ad4bc17111776fd66e3500c1d87c15bbd6055b7371d39c124fb
# platform-revision: 2026-07-02-r45

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        curl \
        ca-certificates \
        procps \
        tmux \
        asciinema \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir --require-hashes --no-deps -r /tmp/requirements.txt

COPY referee/ /app/referee/
COPY cartridge/ /app/cartridge/
COPY tools/ /app/tools/
COPY data/seed_evidence.py /tmp/seed_evidence.py

RUN python3 /tmp/seed_evidence.py \
    && rm -f /tmp/seed_evidence.py \
    && chmod +x /app/referee/start.sh \
    && mkdir -p /app/output
