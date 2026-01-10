#!/bin/sh

set -e

export PYTHONUNBUFFERED=1

/srv/coffeestats/.venv/bin/python3 manage.py collectstatic --noinput
/srv/coffeestats/.venv/bin/python3 manage.py migrate --noinput
/srv/coffeestats/.venv/bin/gunicorn --error-logfile - --capture-output --bind unix:/run/coffeestats/coffeestats.sock --env DJANGO_SETTINGS_MODULE=coffeestats.settings.production coffeestats.wsgi
