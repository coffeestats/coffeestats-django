******************
Code documentation
******************

Caffeine app
============

:py:mod:`caffeine.admin`
------------------------

.. automodule:: caffeine.admin
   :members: UserCreationForm, UserChangeForm, CaffeineUserAdmin

:py:mod:`caffeine.authbackend`
------------------------------

.. automodule:: caffeine.authbackend
   :members: LegacyCoffeestatsAuth

:py:mod:`caffeine.forms`
------------------------

.. automodule:: caffeine.forms
   :members: CoffeestatsRegistrationForm, SettingsForm, SelectTimeZoneForm,
             SubmitCaffeineForm

:py:mod:`caffeine.middleware`
-----------------------------

.. automodule:: caffeine.middleware
   :members: EnforceTimezoneMiddleware

:py:mod:`caffeine.models`
-------------------------

.. automodule:: caffeine.models
   :members: CaffeineUserManager, User, CaffeineManager, Caffeine,
             ActionManager, Action

:py:mod:`caffeine.templatetags.caffeine`
----------------------------------------

.. autofunction:: caffeine.templatetags.caffeine.publicurl

.. autofunction:: caffeine.templatetags.caffeine.ontherunurl

.. autofunction:: caffeine.templatetags.caffeine.messagetags

:py:mod:`caffeine.views`
------------------------

.. todo::
   document caffeine.views (there are import errors in django-registration)


Caffeine API v1 app
===================

.. automodule:: caffeine_api_v1.views
   :members:

Core app
========

.. automodule:: core.utils
   :members:
