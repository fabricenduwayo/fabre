FROM public.ecr.aws/docker/library/python:3.13-slim-bookworm@sha256:01f42367a0a94ad4bc17111776fd66e3500c1d87c15bbd6055b7371d39c124fb
# The verifier runs on Python (pytest); the build under test is Java 17 with
# Maven, both installed from the base image's apt repository.

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        openjdk-17-jdk-headless \
        maven \
        procps \
        tmux \
        asciinema \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir --require-hashes --no-deps -r /tmp/requirements.txt \
    && rm -f /tmp/requirements.txt

# Populate the local Maven repository. The vendor script installs every
# candidate version of the io.meterhub artifacts; the prime build caches the
# lifecycle plugins pinned by the project so everything resolves offline.
COPY vendor/ /opt/vendor/
RUN bash /opt/vendor/install.sh && rm -rf /opt/vendor

COPY prime/ /opt/prime/
RUN mvn -B -q -f /opt/prime/pom.xml clean install dependency:list dependency:build-classpath \
        -Dmdep.outputFile=/tmp/prime-cp.txt \
    && rm -rf /opt/prime /tmp/prime-cp.txt

COPY project/ /app/project/
COPY docs/dependency-policy.md /app/docs/dependency-policy.md
