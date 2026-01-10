**********
Deployment
**********

Manual deployment
=================

You have to setup a WSGI capable web server. We recommend to use `uwsgi`_ and
`nginx`_. We use `uv`_ for dependency management and to isolate the application
code and its dependencies from the rest of your system.

.. _uwsgi: https://uwsgi-docs.readthedocs.org/en/latest/
.. _nginx: https://nginx.org/
.. _uv: https://docs.astral.sh/uv/


Containers
----------

We provide a `docker-compose`_ setup in :file:`docker-compose.yml` and a
production ready :file:`coffeestats/Dockerfile` including `gunicorn`_ as WSGI
server. You may use this with Docker or `podman`_ to run coffeestats behind a
reverse proxy. An example using `nginx`_ is included in the docker-compose
example.

.. _docker-compose: https://docs.docker.com/compose/
.. _gunicorn: https://gunicorn.org/
.. _podman: https://podman.io/


Requirements
------------

The following preconditions have to be fulfilled for a manual deployment:

* `Python`_ >= 3.11.x
* `PostgreSQL`_ >= 11
* a WSGI capable web server

.. _Python: https://www.python.org/
.. _PostgreSQL: http://www.postgresql.org/


Database setup
--------------

We use Django's ORM and you can simply setup your database using:

.. code-block:: sh

   python manage.py migrate
