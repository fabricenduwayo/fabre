#!/usr/bin/env bash
set -u

API_CLASSPATH="/app/artifact-api/classes:/app/lib/*"
API_WAIT_SEC="${API_WAIT_SEC:-300}"

health_up() {
    curl -sf http://localhost:8080/health >/dev/null 2>&1
}

api_running() {
    pgrep -f "com.snorkel.attestapi.ApiServer" >/dev/null 2>&1
}

if health_up; then
    exit 0
fi

if api_running; then
    for _ in $(seq 1 "${API_WAIT_SEC}"); do
        if health_up; then
            exit 0
        fi
        sleep 1
    done
    echo "artifact-metadata API process is running but /health never answered within ${API_WAIT_SEC}s" >&2
    tail -n 40 /var/log/artifact-api.log >&2 || true
    exit 1
fi

mkdir -p /var/log
nohup java -XX:TieredStopAtLevel=1 -Xms64m -Xmx256m \
    -cp "${API_CLASSPATH}" com.snorkel.attestapi.ApiServer \
    >>/var/log/artifact-api.log 2>&1 &

for _ in $(seq 1 "${API_WAIT_SEC}"); do
    if health_up; then
        exit 0
    fi
    sleep 1
done

echo "artifact-metadata API did not become healthy within ${API_WAIT_SEC}s" >&2
tail -n 40 /var/log/artifact-api.log >&2 || true
exit 1
