django-simplekeys
=================

django-simplekeys is a reusable Django app that provides a simple way to add
API keys to an existing Django project, regardless of API framework.

Features
--------

* `Token bucket <https://en.wikipedia.org/wiki/Token_bucket>`_ rate limiting, for limiting requests/second with optional bursting behavior.
* Quota-based rate limiting (e.g. requests/day)
* Ability to configure different usage tiers, to give different users different rates/quotas.
* Ability to configure different 'zones' so that different API methods can have different limits.  (e.g. some particularly computationally expensive queries can have a much lower limit than cheap GET queries)
* Provided views for very simple email-based API key registration.


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

   intro
   advanced


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
