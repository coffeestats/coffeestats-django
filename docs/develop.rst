***********
Development
***********

Getting the coffeestats source
==============================

To start development on coffeestats you have several options for getting a
working environment. Everything starts with a git clone::

  git clone https://github.com/coffeestats/coffeestats-django.git


Development environment setup
=============================

We recommend using Vagrant_ to have a completely isolated working environment.
You can also use virtualenv_ if you don't want the overhead of a full virtual
machine.

.. _Vagrant: http://www.vagrantup.com/
.. _virtualenv: https://virtualenv.pypa.io/en/latest/

If you do not use Vagrant you are on your own when it comes to database setup
and definition of environment variables.

Vagrant
-------

To use Vagrant you can just run:

.. code-block:: sh

   vagrant up

from within your git working copy. Just wait a few minutes (depending on the
speed of your network connection and system performance) and you will have a
running coffeestats instance available at http://localhost:8080/.

You can then just work with the files in your working copy. If you want to
perform service restarts or any other system administration in your coffeestats
virtual machine you can use:

.. code-block:: sh

   vagrant ssh

A fresh Vagrant VM has everything setup and all dependendencies installed in
a virtualenv in :file:`~vagrant/coffeestats-venv/`. If you need to update the
dependencies you can use:

.. code-block:: sh

   sudo salt-call state.highstate

The Salt invocation will take care of restarting `uwsgi`_ and `nginx`_ if
needed.

.. _uwsgi: http://uwsgi-docs.readthedocs.org/en/latest/
.. _nginx: http://nginx.org/

Virtualenv
----------

If you want to avoid the overhead of a virtual machine you can also use
virtualenv_ to setup your development environment.

.. _virtualenv: https://virtualenv.pypa.io/en/latest/

You will need a PostgreSQL database and have to take care of setting the
necessary environment variables for the Django settings yourself. Look at the
Salt state descriptions to get an idea what has to be done.

Virtualenv Only
^^^^^^^^^^^^^^^

First, make sure you are using virtualenv_. Once that's installed, create your
virtualenv:

.. code-block:: sh

   virtualenv ~/coffeestats-venv
   cd coffeestats && add2virtualenv `pwd`

Use the following command to work with the virtual environment later:

.. code-block:: sh

   . ~/coffeestats-venv/bin/activate

Virtualenv with virtualenvwrapper
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

In Linux and Mac OSX, you can install virtualenvwrapper_ which will take care
of managing your virtual environments and adding the project path to the
`site-directory` for you:

.. code-block:: sh

   mkvirtualenv coffeestats-dev
   cd coffeestats && add2virtualenv `pwd`

To work with the virtual environment later use:

.. code-block:: sh

   workon coffeestats-dev

.. _virtualenvwrapper: http://virtualenvwrapper.readthedocs.org/en/latest/


Installation of dependencies
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you use a virtual environment you have to install the necessary
dependencies. You need Python and PostgreSQL development headers installed
before the installation of the development dependencies will work. On Debian
based systems you can use apt to install both:

.. code-block:: sh

   sudo apt-get update
   sudo apt-get install libpq-dev python-dev

Development dependencies are defined in :file:`requirements/local.txt`. Use the
following command to install the dependencies in your currently activated
environment:

.. code-block:: sh

   pip install -r requirements/local.txt


Development session
===================

If you are using Vagrant as recommended you can start a development session by
opening a terminal and an editor session inside of your coffeestats clone. In
the terminal session you run:

.. code-block:: sh

   vagrant up
   # ... wait for the VM to start
   vagrant ssh
   # ... should now be logged in to your vagrant VM
   . csdev.sh
   . coffeestats-venv/bin/activate
   cd /vagrant/coffeestats

If you are not familiar with Django you should start with the `Django
tutorial`_.

.. _Django tutorial: https://docs.djangoproject.com/en/1.6/intro/tutorial01/


.. _directory structure:

Directory structure
===================

:file:`.`
   base directory with .gitignore, .travis.yml, CONTRIBUTORS.txt, LICENSE.txt,
   README.txt, Vagrantfile

   :file:`coffeestats`
      base directory for the project code and other project files

      :file:`assets`
         directory for static files to be served by a web server. This directory is
         populated by :command:`manage.py collectstatic`

      :file:`caffeine`
         directory containing the caffeine app. This app contains the main model
         classes, code for generating statistics as well as the views used to display
         the web user interface

      :file:`caffeine_api_v1`
         directory containing the :ref:`REST API v1.0 <rest-api-v1_0>` implementation

      :file:`coffeestats`
         directory containing the configuration code for coffeestats like the main
         URL configuration, settings for different environments (local, test,
         production) and the WSGI application entry point

      :file:`core`
         directory containing code to be used by multiple Django apps

      :file:`functional_tests`
         directory containing functional tests based on `Selenium`_

      :file:`static`
         directory containing subdirectories with static assets for coffeestats

         :file:`css`
            `Sass`_ sources as well as generated and hand-written CSS

         :file:`fonts`
            font files

         :file:`images`
            icons and other image files

         :file:`js`
            JavaScript libraries (app specific JavaScript code is kept in
            :file:`static/<appname>/js` subdirectories of the corresponding apps)

      :file:`templates`
         directory containing the HTML and email text templates

   :file:`docs`
      directory containing the `Sphinx`_ documentation source

   :file:`requirements`
      directory containing `pip`_ requirements files

   :file:`salt`
      directory containing the `Salt`_ states and pillars that are used to
      provision the Vagrant VM

.. _Selenium: http://www.seleniumhq.org/
.. _Sphinx: http://sphinx-doc.org/
.. _pip: https://pip.pypa.io/en/latest/
.. _Sass: http://sass-lang.com/
.. _Salt: http://www.saltstack.com/community/


.. index:: Sass

.. _css generation:

CSS generation with Sass
========================

We use `Sass`_ to generate our Cascading Style Sheets (CSS) file. Sass is a CSS
generator feeded by a CSS like language. On Debian systems you can install Sass
by running:

.. code-block:: sh

   sudo apt-get install ruby-sass

On other systems with a Ruby Gems installation you can run:

.. code-block:: sh

   gem install sass

During development you can continuosly run :program:`sass` to generate the
:file:`coffeestats/static/css/caffeine.css`:

.. code-block:: sh

   cd coffeestats/static
   sass --watch css/caffeine.scss:css/caffeine.css

You can also run :program:`sass` before committing your changes on
:file:`coffeestats/static/css/caffeine.scss` manually:

.. code-block:: sh

   cd coffeestats/static
   sass css/caffeine.scss:css/caffeine.css

.. index:: caffeine.scss, caffeine.css

.. warning::

   Please be aware that all changes in :file:`css/caffeine.css` you make
   manually will be overwritten the next time somebody runs Sass. You should
   always modify :file:`css/caffeine.scss` instead.
