Development
===========

To start development on coffeestats you have several options for getting a
working environment. Everything starts with a git clone::

  git clone https://github.com/jandd/coffeestats-django.git

We recommend using Vagrant_ to have a completely isolated working environment.
You can also use virtualenv_ if you don't want the overhead of a full virtual
machine.

.. _Vagrant: http://www.vagrantup.com/
.. _virtualenv: http://www.virtualenv.org/


Vagrant
-------

To use Vagrant you can just run::

   $ vagrant up

from within your git working copy. Just wait a few minutes (depending on the
speed of your network connection and system performance) and you will have a
running coffeestats instance available at http://localhost:8080/.

You can then just work with the files in your working copy. If you want to
perform service restarts or any other system administration in your coffeestats
virtual machine you can use::

   $ vagrant ssh


Virtualenv Only
---------------

First, make sure you are using virtualenv (http://www.virtualenv.org). Once
that's installed, create your virtualenv::

    $ virtualenv coffeestats
    $ cd coffeestats && add2virtualenv `pwd`

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

To work with the virtual environment later use::

    $ workon coffeestats-dev

.. _virtualenvwrapper: http://virtualenvwrapper.readthedocs.org/en/latest/,


Installation of dependencies
----------------------------

Development dependencies are defined in :file:`requirements/local.txt`. Use the
following command to install the dependencies in your currently activated
environment::

    $ pip install -r requirements/local.txt
