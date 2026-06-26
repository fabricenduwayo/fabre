FROM public.ecr.aws/docker/library/python:3.13-slim-bookworm@sha256:01f42367a0a94ad4bc17111776fd66e3500c1d87c15bbd6055b7371d39c124fb

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        g++=4:12.2.0-3 \
        cmake=3.25.1-1 \
        make=4.3-4.1 \
        nlohmann-json3-dev=3.11.2-2 \
        curl=7.88.1-10+deb12u14 \
        ca-certificates=20230311+deb12u1 \
        procps=2:4.0.2-3 \
        tmux=3.3a-3 \
        asciinema=2.2.0-1 \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir \
        pytest==8.2.2 \
        pytest-json-ctrf==0.3.5

COPY cpp-auditor/ /app/cpp-auditor/
COPY fixtures/ /app/fixtures/
COPY docs/ /app/docs/

# Header-only HTTP server, pinned and checksum-verified (no canonical apt package
# exists in bookworm). Downloaded at build time only; the task runs offline.
RUN mkdir -p /app/cpp-auditor/include \
    && curl -fsSL -o /app/cpp-auditor/include/httplib.h \
        https://raw.githubusercontent.com/yhirose/cpp-httplib/v0.15.3/httplib.h \
    && echo "a3347656c71c81c3fe510fdb1ff229d7db52eb7df04d3342d340eba0b6ad50ea  /app/cpp-auditor/include/httplib.h" \
        | sha256sum -c -

RUN cmake -S /app/cpp-auditor -B /app/cpp-auditor/build \
    && cmake --build /app/cpp-auditor/build -j 2
