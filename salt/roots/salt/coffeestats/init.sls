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

libpq-dev:
  pkg.installed

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

python-virtualenv:
  pkg.installed

python-dev:
  pkg.installed

/home/vagrant/coffeestats-venv:
  file.directory:
    - user: vagrant
    - group: vagrant
    - requires:
      - coffeestats-venv
      - coffeestats-requires

coffeestats-venv:
  cmd.run:
    - name: virtualenv /home/vagrant/coffeestats-venv
    - user: vagrant
    - group: vagrant
    - creates: /home/vagrant/coffeestats-venv
    - requires-in: /home/vagrant/coffeestats-venv

coffeestats-requires:
  cmd.run:
    - name: /home/vagrant/coffeestats-venv/bin/pip install -r requirements/local.txt
    - user: vagrant
    - group: vagrant
    - cwd: /vagrant
    - require:
      - file: /home/vagrant/coffeestats-venv
      - pkg: python-dev
      - pkg: libpq-dev
    - watch_in:
      - service: uwsgi

coffeestats-static:
  cmd.run:
    - name: . /home/vagrant/csdev.sh ; /home/vagrant/coffeestats-venv/bin/python manage.py collectstatic --noinput
    - user: vagrant
    - group: vagrant
    - cwd: /vagrant/coffeestats

uwsgi-coffeestats:
  pkg.installed:
    - names:
      - uwsgi
      - uwsgi-plugin-python
  service.running:
    - name: uwsgi
    - enable: True
    - reload: True
    - sig: uwsgi
    - require:
      - pkg: uwsgi
      - pkg: uwsgi-plugin-python
      - file: /etc/uwsgi/apps-enabled/coffeestats.ini
      - file: /home/vagrant/coffeestats-venv
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
    - name: . /home/vagrant/csdev.sh; /home/vagrant/coffeestats-venv/bin/python manage.py syncdb --migrate --noinput
    - cwd: /vagrant/coffeestats
    - user: vagrant
    - group: vagrant
    - require:
      - cmd: coffeestats-requires
      - file: /home/vagrant/csdev.sh
      - file: /home/vagrant/coffeestats-venv
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
      - service: uwsgi
