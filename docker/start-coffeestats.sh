#!/bin/sh

set -e

/srv/venv/bin/python3 manage.py migrate
/srv/venv/bin/python3 manage.py runserver 0.0.0.0:8000
