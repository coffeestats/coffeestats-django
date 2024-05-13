FROM python:3.9-bullseye

ENV \
  PYTHONUNBUFFERED=1 \
  PYTHONFAULTHANDLER=1 \
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100

EXPOSE 8000

RUN DEBIAN_FRONTEND=noninteractive \
  ; apt-get update \
  && apt-get install -y --no-install-recommends \
    build-essential \
    chromium \
    chromium-driver \
    curl \
    gettext \
    git \
    libffi-dev \
    libjpeg-dev \
    libpq-dev \
    python3-dev \
    python3-pip \
    python3-venv \
    zlib1g-dev

ENV PATH=/root/.local/bin:$PATH

RUN python3 -m pip install --user pipx \
 && python3 -m pipx ensurepath \
 && pipx install "poetry==1.8.2"

VOLUME /srv/coffeestats
WORKDIR /srv/coffeestats
COPY pyproject.toml poetry.lock /srv/coffeestats/

RUN poetry export --with=dev > requirements.txt \
 && python3 -m venv /srv/venv \
 && /srv/venv/bin/python3 -m pip install -r requirements.txt

COPY docker/start-coffeestats.sh /srv/

ENTRYPOINT "/srv/start-coffeestats.sh"
