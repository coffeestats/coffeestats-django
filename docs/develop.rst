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

We recommend using Docker to have a completely isolated working environment.
You can also use Poetry to run an isolated Python virtual environment. We also
include a docker compose setup that takes care of starting a database and a
container with the application and its dependencies.

If you are not familiar with Django you should start with the `Django
tutorial`_.

.. _Django tutorial: https://docs.djangoproject.com/en/1.6/intro/tutorial01/


.. _directory structure:

Directory structure
===================

:file:`.`
   base directory with .gitignore, CONTRIBUTORS.txt, LICENSE.txt,
   README.txt

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

            :file:`common`
               common styling like fonts, colors, icons and mediaqueries

            :file:`components`
               `Sass`_ components / pageareas which will be imported and compiled in the caffeine.scss

            :file:`fonts`
               font files

         :file:`images`
            icons and other image files

         :file:`js`
            JavaScript libraries and a common scripts.js (app specific JavaScript code is kept in
            :file:`static/<appname>/js` subdirectories of the corresponding apps)

      :file:`templates`
         directory containing the HTML and email text templates

   :file:`docs`
      directory containing the `Sphinx`_ documentation source


.. _Selenium: http://www.seleniumhq.org/
.. _Sphinx: http://sphinx-doc.org/
.. _pip: https://pip.pypa.io/en/latest/
.. _Sass: http://sass-lang.com/


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

SASS files which look like this: _filename.scss are for imports in other sass files. Sass won't generate own css files of them.
