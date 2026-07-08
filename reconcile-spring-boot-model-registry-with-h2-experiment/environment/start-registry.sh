#!/usr/bin/env bash
# Start the model-registry Spring Boot API on port 8080 if it is not already
# serving, then wait for /health. Safe to run repeatedly.
set -u

if curl -sf http://localhost:8080/health >/dev/null 2>&1; then
    exit 0
fi

nohup java -jar /app/model-registry/target/model-registry-0.1.0.jar \
    --server.port=8080 >>/var/log/model-registry.log 2>&1 &

for _ in $(seq 1 60); do
    if curl -sf http://localhost:8080/health >/dev/null 2>&1; then
        exit 0
    fi
    sleep 1
done

echo "model-registry API did not become healthy within 60s; see /var/log/model-registry.log" >&2
exit 1
