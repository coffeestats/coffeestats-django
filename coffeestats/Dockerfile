FROM python:3.6-alpine

ENV \
  PYTHONUNBUFFERED=1 \
  PYTHONFAULTHANDLER=1 \
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100 \
  PIPENV_HIDE_EMOJIS=true \
  PIPENV_COLORBLIND=true \
  PIPENV_NOSPIN=true \
  PIPENV_DOTENV_LOCATION=config/.env \
  TEST_CHROMEDRIVER=/usr/bin/chromedriver

EXPOSE 8000

RUN apk --no-cache add \
  bash \
  build-base \
  curl \
  gcc \
  gettext \
  git \
  libffi-dev \
  linux-headers \
  musl-dev \
  zlib-dev \
  postgresql-dev \
  jpeg-dev \
  chromium \
  chromium-chromedriver

RUN pip install pipenv

VOLUME /srv/coffeestats
WORKDIR /srv/coffeestats
COPY Pipfile Pipfile.lock /srv/coffeestats/

RUN pipenv install --system --deploy --ignore-pipfile --dev

COPY docker/start-coffeestats.sh /srv/

ENTRYPOINT "/srv/start-coffeestats.sh"
