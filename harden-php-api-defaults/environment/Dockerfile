FROM public.ecr.aws/docker/library/python:3.13-slim-bookworm@sha256:01f42367a0a94ad4bc17111776fd66e3500c1d87c15bbd6055b7371d39c124fb
# platform-revision: 2026-07-09-r17

WORKDIR /app

# PHP runs the API (no compilation needed), sqlite3 for the audit ledger,
# plus the agent runtime tools. apt versions float per Terminus apt policy.
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        php-cli \
        php-sqlite3 \
        sqlite3 \
        curl \
        ca-certificates \
        procps \
        tmux \
        asciinema \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir --require-hashes --no-deps -r /tmp/requirements.txt

COPY harbordesk/ /app/harbordesk/
COPY docs/ /app/docs/

# Seed the audit ledger with the legacy schema currently in production (a stale
# "actor" column, no "origin") plus real historical rows, so the audit-logging
# defect is reproducible and a naive rebuild that discards history is caught.
RUN chmod +x /app/harbordesk/start.sh \
    && chmod 600 /app/harbordesk/data/bootstrap_secret \
    && sqlite3 /app/harbordesk/data/audit.db \
        "CREATE TABLE audit_log (id INTEGER PRIMARY KEY AUTOINCREMENT, ts TEXT NOT NULL, event TEXT NOT NULL, route TEXT NOT NULL, actor TEXT NOT NULL, decision TEXT NOT NULL, reason TEXT); INSERT INTO audit_log (ts, event, route, actor, decision, reason) VALUES ('2026-01-02T08:00:00+00:00', 'health', '/health', 'svc-legacy', 'accepted', 'legacy_history'); INSERT INTO audit_log (ts, event, route, actor, decision, reason) VALUES ('2026-01-02T08:05:00+00:00', 'bootstrap', '/admin/bootstrap', 'svc-legacy', 'denied', 'legacy_history');"
