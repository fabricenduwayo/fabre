FROM public.ecr.aws/docker/library/python:3.13-slim-bookworm@sha256:01f42367a0a94ad4bc17111776fd66e3500c1d87c15bbd6055b7371d39c124fb
# platform-revision: 2026-07-01-r2

WORKDIR /app

# Common Debian build/runtime packages are left unpinned: bookworm serves a
# single version of each, and the digest-pinned base image fixes the snapshot,
# so this stays reproducible while avoiding build breaks when point releases
# supersede a pinned security version (e.g. ca-certificates) in the mirror.
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        g++ \
        cmake \
        make \
        nlohmann-json3-dev \
        ca-certificates \
        procps \
        tmux \
        asciinema \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir --require-hashes --no-deps -r /tmp/requirements.txt

COPY cpp-auditor/ /app/cpp-auditor/
COPY fixtures/ /app/fixtures/
COPY docs/ /app/docs/

# Persistent audit ledger, left over from an older release in the legacy
# schema-1 layout (records under "audits"). The service is expected to keep
# appending audits here.
RUN mkdir -p /app/cpp-auditor/state \
    && printf '%s' '{"schema": 1, "audits": [{"action": "audit.bootstrap", "target": "legacy-seed"}]}' \
        > /app/cpp-auditor/state/ledger.json

# Header-only HTTP server (cpp-httplib v0.15.3), vendored under
# cpp-auditor/include/ so the build has no external network dependency. The
# header is copied in with the rest of cpp-auditor/ above.
RUN cmake -S /app/cpp-auditor -B /app/cpp-auditor/build \
    && cmake --build /app/cpp-auditor/build -j 2
