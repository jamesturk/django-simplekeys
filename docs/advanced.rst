Advanced Usage
==============

Multiple Tiers
--------------

Adding multiple tiers requires going into the Django admin and creating
new tiers with the limits you desire.  As noted in the introduction, be sure
each tier has an association with each zone unless you intend to prevent
a given tier from accessing that zone at all.

simplekeys makes no assumptions about how you want to associate users with
tiers.  The default key registration view accepts an optional ``tier``
parameter that allows you to pass a tier slug (defaults to ``default``).


Multiple Zones
--------------

Most APIs can get by with a single zone, but perhaps you have some methods that are computationally expensive and so you need a lower rate limit to prevent your server from being overwhelmed.

The default middleware will group all views into the ``SIMPLEKEYS_DEFAULT_ZONE``, but with the decorator it is possible to override this zone.

By passing the zone's slug to the ``zone`` argument of ``simplekeys.middleware.require_apikey`` the view in question will be authorized using the ``zone`` argument.


API Key Registration
--------------------

The provided views create unregistered API keys and then email the user a link
that will let them verify their email address and thus enable their key.

Should you wish to vary that flow at all, perhaps auto-assigning users keys
or not requiring email registration, it is recommended you do so by
programatically creating Key objects.


Rate Limiting Backends
----------------------

Keeping track of how many times a key is used requires some semi-permanent storage that is relatively cheap to access.

Since Django's existing cache framework provides easy access to such data stores, that is the default backend.

There is also a memory backend, which stores the rate-limiting data locally, this is not intended for production use and should only be used if you know what you're doing.

In both of these cases, the rate-limiting data is somewhat ephemeral, a process restarting or a cache getting cleared will allow users to make more calls than you might otherwise have expected.  If this does not meet your needs it may be necessary to explore other options, or you may be able to simply write a custom backend that writes to your storage of choice.

If you write a rate limiting backend that you think others might find useful, please consider contributing back to the project.


Configuration
-------------

``SIMPLEKEYS_DEFAULT_ZONE``
    If you use the ``SimpleKeysMiddleware`` or ``require_apikey`` without
    a ``zone`` parameter, simplekeys will consider your view part of this
    zone.

    Default: ``default``

``SIMPLEKEYS_HEADER``
    HTTP header that ``simplekeys.middleware.SimpleKeysMiddleware`` and
    ``simplekeys.middleware.require_apikey`` will check for presence of 
    API key.

    Default: ``HTTP_X_API_KEY``

``SIMPLEKEYS_QUERY_PARAM``
    HTTP query parameter that ``simplekeys.middleware.SimpleKeysMiddleware``
    and ``simplekeys.middleware.require_apikey`` will check for presence of
    API key.  (This check occurs after ``SIMPLEKEYS_HEADER`` check.)

    Default: ``apikey``

``SIMPLEKEYS_RATE_LIMIT_BACKEND``
    String representing full import path to a rate limit backend.

    Default: ``simplekeys.backends.CacheBackend``

``SIMPLEKEYS_CACHE``
    ``settings.CACHE`` entry to use for ``simplekeys.backends.CacheBackend``

    Default: ``default``

``SIMPLEKEYS_CACHE_TIMEOUT``
    Timeout for entries created by ``simplekeys.backends.CacheBackend``

    Default: ``25*60*60`` (25 hours)
