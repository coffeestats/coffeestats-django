ARG DEBIAN_RELEASE=bookworm
ARG UV_VERSION=0.9.24

FROM debian:${DEBIAN_RELEASE}-slim AS builder
ARG UV_VERSION

RUN DEBIAN_FRONTEND=noninteractive \
  ; apt-get update \
  && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    gettext \
    libffi-dev \
    libjpeg-dev \
    libpq-dev \
    python3-dev \
    python3-venv \
    zlib1g-dev

COPY pyproject.toml uv.lock /srv/coffeestats/
WORKDIR /srv/coffeestats
RUN --mount=from=ghcr.io/astral-sh/uv:$UV_VERSION,source=/uv,target=/bin/uv \
    uv sync --no-dev --no-python-downloads --locked --compile-bytecode ; rm -rf /root/.cache /tmp/uv-*.lock

FROM debian:${DEBIAN_RELEASE}-slim

RUN DEBIAN_FRONTEND=noninteractive \
  ; apt-get update \
  && apt-get install -y --no-install-recommends \
    gettext \
    libffi8 \
    libjpeg62-turbo \
    libpq5 \
    python3 \
    tini \
    zlib1g \
  && apt-get clean \
  && rm -rf /var/cache/apt/archives /var/lib/apt/lists/* /var/log/apt/* /var/log/dpkg.log

COPY --from=builder /srv/coffeestats/.venv /srv/coffeestats/.venv
COPY docker/start-coffeestats.sh /srv/coffeestats/
COPY coffeestats /app/

VOLUME /app/assets
VOLUME /run/coffeestats

WORKDIR /app

ENTRYPOINT ["tini", "--"]
CMD ["/srv/coffeestats/start-coffeestats.sh"]
