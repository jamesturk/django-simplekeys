django-simplekeys
=================

django-simplekeys is a Django reusable app that provides a simple way to add
API keys to an existing Django project, regardless of API framework.

Features
--------

* `Token bucket <https://en.wikipedia.org/wiki/Token_bucket>`_ rate limiting, for limiting requests/second with optional bursting behavior.
* Quota-based rate limiting (e.g. requests/day)
* Ability to configure different usage tiers, to give different users different rates/quotas.
* Ability to configure different 'zones' so that different API methods can have different limits.  (e.g. some particularly computationally expensive queries can have a much lower limit than cheap GET queries)
* Provided views for very simple email-based API key registration.

Usage
-----

1) Add ``simplekeys`` to ``INSTALLED_APPS`` as you would any app.

2) If you wish to protect every view you can install ``simplekeys.middleware.SimpleKeysMiddleware`` in your ``MIDDLEWARE_CLASSES`` setting.

  Alternatively, If you wish to only protect certain views, do so by decorating those views with the ``simplekeys.middleware.require_apikey`` decorator.

3) In the Django admin, create at least one ``Zone``.

4) In the Django admin, create at least one ``Tier``, and add limits for the ``Zone`` you defined earlier.

5) If you wish to use the provided key registration views, TODO

.. warning::

    If you do not create an association between a ``Tier`` and a ``Zone`` then users will not be able to access any views that you define as being within a given ``Zone``.

Concepts
--------

Tier
    simplekeys has the concept of different keys having different usage limits.

    For example: you could define a silver tier and a gold tier, where gold
    tier keys have higher rate limits due to being trusted users.

    Each API key is associated with a single tier.

    If you only want to have one tier, it is recommended you call it ``default``.

Zone
    simplekeys allows you to define different API zones.  This is intended to
    allow you to specify different rate limits for different API methods.

    Each tier can have different limitations defined on different zones.
    If a tier doesn't have any association with a zone it will not be allowed
    to access it, giving you fine grained control over which keys can access
    which endpoints.

    If all of your API methods will have the same rate limits, you can just
    use a single zone.  Default settings assume you call this ``default``.

Key
    API Keys are associated with a tier and assigned to a user by email address.

    Keys have no association with ``django.contrib.auth``, to avoid a dependency
    that isn't always wanted.

    Should you want to associate them it is possible create Keys automatically
    by adding a ``post_save`` signal to the ``User`` model or you can create keys
    your custom registration view.



Further Reading
---------------

.. toctree::
   :maxdepth: 2

   advanced


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
