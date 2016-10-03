#!/bin/sh
# test run and report for coffeestats

set -e

. $HOME/coffeestats-venv/bin/activate
. $HOME/csdev.sh

export DJANGO_SETTINGS_MODULE=${DJANGO_SETTINGS_MODULE%%local}test
cd /vagrant/coffeestats
xvfb-run -s '-screen 0 1280x1024x16' coverage run --branch manage.py test -v 3 $@
coverage html
flake8
