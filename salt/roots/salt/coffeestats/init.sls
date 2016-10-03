nginx:
  pkg:
    - installed
  service:
    - running
    - require:
      - service: uwsgi
      - pkg: nginx

postgresql:
  pkg:
    - installed
  service:
    - running
    - require:
      - pkg: postgresql

coffeestats-dependencies:
  pkg.installed:
    - pkgs:
      - libpq-dev
      - python
      - python-dev
      - python-virtualenv
      - virtualenv
      - libffi-dev
      - xvfb
      - iceweasel
      - libyaml-dev
      - libjpeg-dev
      - libpng-dev

/etc/uwsgi/apps-available/coffeestats.ini:
  file.managed:
    - user: root
    - group: root
    - mode: 0644
    - source: salt://coffeestats/coffeestats.uwsgi.ini
    - template: jinja

/etc/uwsgi/apps-enabled/coffeestats.ini:
  file.symlink:
    - target: /etc/uwsgi/apps-available/coffeestats.ini
    - require:
      - file: /etc/uwsgi/apps-available/coffeestats.ini

coffeestats-venv:
  cmd.run:
    - name: virtualenv --python=/usr/bin/python2 /home/vagrant/coffeestats-venv
    - runas: vagrant
    - creates: /home/vagrant/coffeestats-venv
    - require:
      - pkg: coffeestats-dependencies

uninstall-pybcrypt:
  cmd.run:
    - name: /home/vagrant/coffeestats-venv/bin/pip uninstall -y py-bcrypt
    - onlyif: /home/vagrant/coffeestats-venv/bin/pip freeze | grep -q py-bcrypt
    - requires:
      - cmd: coffeestats-venv

coffeestats-requires:
  cmd.run:
    - name: /home/vagrant/coffeestats-venv/bin/pip install -r requirements/local.txt
    - runas: vagrant
    - cwd: /vagrant
    - require:
      - cmd: coffeestats-venv
      - cmd: uninstall-pybcrypt
      - pkg: coffeestats-dependencies
    - watch_in:
      - service: uwsgi

coffeestats-static:
  cmd.run:
    - name: . /home/vagrant/csdev.sh ; /home/vagrant/coffeestats-venv/bin/python manage.py collectstatic --noinput
    - runas: vagrant
    - cwd: /vagrant/coffeestats
    - require:
      - cmd: coffeestats-requires
      - file: /home/vagrant/csdev.sh

uwsgi:
  pkg.installed

uwsgi-plugin-python:
  pkg.installed

uwsgi-coffeestats:
  service.running:
    - name: uwsgi
    - enable: True
    - full_restart: True
    - sig: uwsgi
    - require:
      - pkg: uwsgi
      - pkg: uwsgi-plugin-python
      - file: /etc/uwsgi/apps-enabled/coffeestats.ini
      - cmd: coffeestats-requires
      - cmd: coffeestats-static
    - watch:
      - file: /etc/uwsgi/apps-available/coffeestats.ini
    - watch_in:
      - service: nginx

/home/vagrant/csdev.sh:
  file.managed:
    - user: vagrant
    - group: vagrant
    - mode: 0644
    - template: jinja
    - source: salt://coffeestats/csdev.sh

coffeestats-db:
  postgres_user.present:
    - name: {{ pillar['database']['user'] }}
    - user: postgres
    - password: {{ pillar['database']['password'] }}
    - createdb: True
    - login: True
    - require:
      - service: postgresql
  postgres_database.present:
    - name: {{ pillar['database']['database'] }}
    - user: postgres
    - owner: {{ pillar['database']['user'] }}
    - encoding: UTF8
    - template: template0
    - require:
      - service: postgresql
      - postgres_user: {{ pillar['database']['user'] }}
  cmd.run:
    - name: . /home/vagrant/csdev.sh; /home/vagrant/coffeestats-venv/bin/python manage.py migrate --noinput
    - cwd: /vagrant/coffeestats
    - runas: vagrant
    - require:
      - cmd: coffeestats-requires
      - file: /home/vagrant/csdev.sh
      - postgres_database: coffeestats-db
    - watch_in:
      - service: uwsgi

/etc/nginx/sites-available/default:
  file.managed:
    - user: root
    - group: root
    - mode: 0644
    - template: jinja
    - source: salt://coffeestats/nginx.conf
    - require:
      - file: /etc/uwsgi/apps-enabled/coffeestats.ini
    - watch_in:
      - service: nginx

/home/vagrant/run_tests.sh:
  file.managed:
    - user: vagrant
    - group: vagrant
    - mode: 0755
    - source: salt://coffeestats/run_tests.sh
