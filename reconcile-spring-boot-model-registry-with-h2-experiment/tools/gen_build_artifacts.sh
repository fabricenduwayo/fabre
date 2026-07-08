#!/usr/bin/env bash
# One-shot helper: build the registry jar and warm a minimal Maven cache for the
# reconcile step only. Outputs land under environment/ for COPY-only Docker builds.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV="${ROOT}/environment"
ARTIFACT_CONTAINER="registry-artifacts-$$"

cleanup() {
  docker rm -f "${ARTIFACT_CONTAINER}" >/dev/null 2>&1 || true
}
trap cleanup EXIT

docker run -d --name "${ARTIFACT_CONTAINER}" \
  public.ecr.aws/docker/library/python:3.13-slim-bookworm@sha256:01f42367a0a94ad4bc17111776fd66e3500c1d87c15bbd6055b7371d39c124fb \
  sleep infinity

docker exec "${ARTIFACT_CONTAINER}" bash -lc '
  set -euo pipefail
  apt-get update
  apt-get install -y --no-install-recommends openjdk-17-jdk-headless maven
  rm -rf /var/lib/apt/lists/*
  mkdir -p /work
'

docker cp "${ENV}/model-registry" "${ARTIFACT_CONTAINER}:/work/model-registry"
docker cp "${ENV}/reconcile-model-release" "${ARTIFACT_CONTAINER}:/work/reconcile-model-release"

docker exec "${ARTIFACT_CONTAINER}" bash -lc '
  set -euo pipefail
  cd /work
  mvn -B -q -f model-registry/pom.xml package -DskipTests
  rm -rf /root/.m2/repository
  # Warm only the reconcile step cache — Spring Boot deps are not needed offline.
  mvn -B -q -f reconcile-model-release/pom.xml dependency:go-offline
  mvn -B -q -f reconcile-model-release/pom.xml package
  mvn -B -q -f reconcile-model-release/pom.xml -o package
'

rm -rf "${ENV}/model-registry/target" "${ENV}/maven-repo"
mkdir -p "${ENV}/model-registry/target" "${ENV}/maven-repo"

docker cp "${ARTIFACT_CONTAINER}:/work/model-registry/target/model-registry-0.1.0.jar" \
  "${ENV}/model-registry/target/model-registry-0.1.0.jar"
docker cp "${ARTIFACT_CONTAINER}:/root/.m2/repository/." "${ENV}/maven-repo/"

tar -czf "${ENV}/maven-repo.tar.gz" -C "${ENV}/maven-repo" .
rm -rf "${ENV}/maven-repo"

du -sh "${ENV}/model-registry/target/model-registry-0.1.0.jar" "${ENV}/maven-repo.tar.gz"
du -sh "${ENV}"
