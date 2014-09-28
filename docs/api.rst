.. index:: API
.. index:: REST

.. _rest-api-v1_0:

********************
REST API version 1.0
********************

Coffeestats provides a small REST API to be used by third party applications.
The API is described with some example `curl`_ calls below.

.. _curl: http://curl.haxx.se/


Base URI
========

The API is hosted at /api/v1/ and provides several resources that are described
in detail :ref:`below <section-resources>`.

.. code-block:: sh

   curl https://coffeestats.org/api/v1/$Resource

.. index:: authentication

.. _rest authentication:

Authentication
==============

The username and the user's on-the-run token are used for API call
authentication. You can see both used as GET parameters for the bookmarkable
on-the-run link on you `profile page <https://coffeestats.org/profile/>`_.

.. code-block:: sh

   curl -X POST -d "u=user&t=yourtokenhere" https://coffeestats.org/api/v1/$Resource

This is an incomplete example. See :ref:`below <section-resources>` for
detailed resource descriptions.


.. index:: resources

.. _section-resources:

Resources
=========

random-users
------------

.. index:: random-users

.. http:post:: /api/v1/random-users

   Query a set of random users

   :form u: user name
   :form t: on-the-run token
   :form count: optional number of users
   :resheader Content-Type: :mimetype:`text/json`
   :statuscode 200: all is ok, body contains a list of users
   :statuscode 403: authentication required

**curl example**

.. code-block:: sh

   curl -X POST -d "u=user&t=yourtokenhere" https://coffeestats.org/api/v1/random-users |python -mjson.tool
   [
     {
       "coffees": "42",
       "location": "baz",
       "mate": "0",
       "name": "foobar",
       "profile": "https://coffeestats.org/profile?u=foobar",
       "username": "foobar"
     },
     ...
   ]

add-drink
---------

.. index:: add-drink

.. http:post:: /api/v1/add-drink

   Submit the consumption of a drink (mate or coffee)

   :form u: user name
   :form t: on-the-run token
   :form beverage: ``mate`` or ``coffee``
   :form time: timestamp in a format with ISO 8601 date and time i.e. 2014-02-24 19:46:30
   :resheader Content-Type: :mimetype:`text/json`

**curl example**

.. code-block:: sh

   curl -X POST -d "u=user&t=yourtokenhere&beverage=mate&time=2014-02-24 19:46:30" https://coffeestats.org/api/v1/add-drink |python -mjson.tool
   {
     "success": true
   }
