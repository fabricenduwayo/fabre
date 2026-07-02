FROM public.ecr.aws/docker/library/python:3.13-slim-bookworm@sha256:01f42367a0a94ad4bc17111776fd66e3500c1d87c15bbd6055b7371d39c124fb
# platform-revision: 2026-07-02-r14

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        openjdk-17-jdk-headless \
        maven \
        gawk \
        curl \
        procps \
        tmux \
        asciinema \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir --require-hashes --no-deps -r /tmp/requirements.txt

COPY docs/ /app/docs/
COPY dependency-audit/ /app/dependency-audit/

RUN chmod +x /app/dependency-audit/build.sh /app/dependency-audit/start.sh \
    && cd /app/dependency-audit \
    && mvn -q org.apache.maven.plugins:maven-dependency-plugin:3.6.1:go-offline \
    && mvn -q -DskipTests package \
    && mvn -q org.apache.maven.plugins:maven-dependency-plugin:3.6.1:get \
        -Dartifact=org.apache.maven.surefire:surefire-junit-platform:3.1.2 \
    && mvn -q org.apache.maven.plugins:maven-dependency-plugin:3.6.1:get \
        -Dartifact=org.codehaus.mojo:exec-maven-plugin:3.1.0:pom \
    && mvn -q org.apache.maven.plugins:maven-dependency-plugin:3.6.1:get \
        -Dartifact=org.codehaus.mojo:exec-maven-plugin:3.1.0:jar \
    && mvn -q org.codehaus.mojo:exec-maven-plugin:3.1.0:help

COPY settings.xml /root/.m2/settings.xml

EXPOSE 8080
