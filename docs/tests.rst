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
