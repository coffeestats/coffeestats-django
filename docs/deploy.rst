**********
Deployment
**********

Salt states
===========

The live deployment for https://coffeestats.org/ is done using `Salt states`_.
The setup is similar to the setup described in
`salt/roots/salt/coffeestats <https://github.com/coffeestats/coffeestats-django/tree/master/salt/roots/salt/coffeestats>`_.

.. _Salt states: http://docs.saltstack.com/en/latest/ref/states/index.html

Manual deployment
=================

You have to setup a WSGI capable web server. We recommend to use `uwsgi`_ and
`nginx`_. You should use `virtualenv`_ to isolate the application code and its
dependencies from the rest of your system.

.. _uwsgi: http://uwsgi-docs.readthedocs.org/en/latest/
.. _nginx: http://nginx.org/
.. _virtualenv: https://virtualenv.pypa.io/en/latest/

Requirements
------------

The following preconditions have to be fulfilled for a manual deployment:

* `Python`_ 2.7.x
* `PostgreSQL`_ >= 9.1
* a WSGI capable web server

.. _Python: https://www.python.org/
.. _PostgreSQL: http://www.postgresql.org/


Database setup
--------------

We use Django's ORM and you can simply setup your database using:

.. code-block:: sh

   python manage.py syncdb --migrate
