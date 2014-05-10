Tests
=====

Coffeestats comes with a full suite of unit and functional tests. The unit
tests are available in each app's tests module. To run the test suite you need
the test dependencies installed (both :file:`requirements/test.txt` and
:file:`requirements/local.txt` include the list of necessary Python modules).

When all test requirements are met you can run all tests using:

.. code-block:: sh

   cd coffeestats
   coverage run --branch manage.py test

You can get a coverage report with:

.. code-block:: sh

   coverage report -m

.. note::
   The functional tests in the :file:`coffeestats/functional_tests` directory
   need a Firefox and a graphical display. If you want to run the tests in a
   headless environment you can use xvfb. This approach is also used on Travis
   CI


Continous Integration
---------------------

The coffeestats test suite is run on `Travis CI`_ after every push to the
master branch of the main github repository, code coverage is reported to the
`Coveralls`_ service after successful builds.

.. _Travis CI: https://travis-ci.org/coffeestats/coffeestats-django
.. _Coveralls: https://coveralls.io/r/coffeestats/coffeestats-django
