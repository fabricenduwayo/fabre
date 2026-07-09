#!/usr/bin/env bash
# Start the model-registry Spring Boot API on port 8080 if it is not already
# serving, then wait for /health. Safe to run repeatedly.
set -u

REGISTRY_JAR=/app/model-registry/target/model-registry-0.1.0.jar
REGISTRY_WAIT_SEC="${REGISTRY_WAIT_SEC:-300}"

health_up() {
    curl -sf http://localhost:8080/health >/dev/null 2>&1
}

registry_running() {
    pgrep -f "${REGISTRY_JAR}" >/dev/null 2>&1
}

registry_java_opts=(
    -XX:TieredStopAtLevel=1
    -Xms64m
    -Xmx384m
    -Djava.awt.headless=true
    -Djava.security.egd=file:/dev/./urandom
    -Dspring.main.lazy-initialization=true
    -Dspring.jmx.enabled=false
)

# Fast path: already healthy.
if health_up; then
    exit 0
fi

# The entrypoint or an earlier launcher may already be warming the jar. Wait for
# readiness instead of spawning a duplicate that loses the port bind.
if registry_running; then
    for _ in $(seq 1 "${REGISTRY_WAIT_SEC}"); do
        if health_up; then
            exit 0
        fi
        sleep 1
    done
    echo "model-registry process is running but /health never answered within ${REGISTRY_WAIT_SEC}s; see /var/log/model-registry.log" >&2
    tail -n 40 /var/log/model-registry.log >&2 || true
    exit 1
fi

mkdir -p /var/log
nohup java "${registry_java_opts[@]}" \
    -jar "${REGISTRY_JAR}" \
    --server.port=8080 >>/var/log/model-registry.log 2>&1 &

for _ in $(seq 1 "${REGISTRY_WAIT_SEC}"); do
    if health_up; then
        exit 0
    fi
    sleep 1
done

echo "model-registry API did not become healthy within ${REGISTRY_WAIT_SEC}s; see /var/log/model-registry.log" >&2
tail -n 40 /var/log/model-registry.log >&2 || true
exit 1
