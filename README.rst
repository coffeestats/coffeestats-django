===========
coffeestats
===========

This is the Django_ port of coffeestats_. The port was started because of the
PHP uglyness.

.. _Django: https://www.djangoproject.com/
.. _coffeestats: https://github.com/coffeestats/coffeestats/

.. image:: https://travis-ci.org/jandd/coffeestats-django.svg?branch=master
   :target: https://travis-ci.org/jandd/coffeestats-django
.. image:: https://coveralls.io/repos/jandd/coffeestats-django/badge.png?branch=master
   :target: https://coveralls.io/r/jandd/coffeestats-django?branch=master


Working Environment
===================

You have several options in setting up your working environment.  We recommend
using Vagrant_ to have a completely isolated working environment.  You can also
use virtualenv_ if you don't want to use a fully virtualized environment.

.. _Vagrant: http://www.vagrantup.com/
.. _virtualenv: http://www.virtualenv.org/


Vagrant
-------

To use Vagrant you can just run::

    $ vagrant up

wait a few minutes (depending on the speed of your network connection and
system performance) and you will have a running coffeestats instance available
at http://localhost:8080/.


Virtualenv Only
---------------

First, make sure you are using virtualenv (http://www.virtualenv.org). Once
that's installed, create your virtualenv::

    $ virtualenv coffeestats

You will also need to ensure that the virtualenv has the project directory
added to the path. Adding the project directory will allow `django-admin.py` to
be able to change settings using the `--settings` flag.

Virtualenv with virtualenvwrapper
------------------------------------

In Linux and Mac OSX, you can install virtualenvwrapper_ which will take care
of managing your virtual environments and adding the project path to the
`site-directory` for you::

    $ mkvirtualenv coffeestats-dev
    $ cd coffeestats && add2virtualenv `pwd`

.. _virtualenvwrapper: http://virtualenvwrapper.readthedocs.org/en/latest/,


Installation of Dependencies
=============================

Depending on where you are installing dependencies:

In development::

    $ pip install -r requirements/local.txt

For production::

    $ pip install -r requirements.txt


Acknowledgements
================

- All of the contributors_ to this project.

.. _contributors: https://github.com/coffeestats/coffeestats-django/blob/master/CONTRIBUTORS.txt
