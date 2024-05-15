Tests
=====

Coffeestats comes with a full suite of unit and functional tests. The unit
tests are available in each app's tests module.

When all test requirements are met you can run all tests using:

.. code-block:: sh

   cd coffeestats
   poetry run coverage run --branch manage.py test

You can get a coverage report with:

.. code-block:: sh

   poetry run coverage report -m

.. note::
   The functional tests in the :file:`coffeestats/functional_tests` directory
   need Chromium and a graphical display. If you want to run the tests in a
   headless environment you can use xvfb.
