Advanced Usage
==============

Understanding Tiers & Zones
---------------------------

Some of the real power of simplekeys comes from using multiple zones and tiers.

    * Zones allow you to give different levels of access & rate limits to different API methods.
    * Tiers allow you to give different types of users different access across zones.
    * Limits connect these two, each Tier defines appropriate rate limits and quotas for Zones it has access to.

As noted in the introduction, be sure each tier has an association with each
zone unless you intend to prevent a given tier from accessing that zone at all.

.. _models:

Models
------

.. py:module:: simplekeys.models

.. py:class:: Tier

    .. py:attribute:: slug

        internal name of the Tier (e.g. ``default``)

    .. py:attribute:: name

        human-readable name of the Tier (e.g. ``Default API Users``)

    simplekeys has the concept of different keys having different usage
    limits, this is done with Tiers.

    For example: you could define a silver tier and a gold tier, where gold
    tier keys have higher rate limits due to being trusted users.

    Each API key is associated with a single tier.

    If you only want to have one tier, it is recommended you call it
    ``default``.

.. py:class:: Zone

    .. py:attribute:: slug

        internal name of the Zone (e.g. ``default``)

    .. py:attribute:: name

        human-readable name of the Zone (e.g. ``Default API Methods``)

    simplekeys allows you to define different API zones.  This is intended to
    allow you to specify different rate limits for different API methods.

    Each tier can have different limitations defined on different zones.
    If a tier doesn't have any association with a zone it will not be allowed
    to access it, giving you fine grained control over which keys can access
    which endpoints.

    If all of your API methods will have the same rate limits, you can just
    use a single zone.  Default settings assume you call this ``default``.

.. py:class:: Limit

    .. py:attribute:: tier

        ForeignKey relationship to a :class:`Tier`

    .. py:attribute:: zone

        ForeignKey relationship to a :class:`Zone`

    .. py:attribute:: quota_requests

        How many requests to allow overall each day/month (according to ``quota_period``).

        This is independent of the ``requests_per_second`` and ``burst_size``,
        and sets a hard quota that the user cannot exceed in the given period.

    .. py:attribute:: quota_period

        Specifies if ``quota_requests`` is a daily or a monthly limitation.

        This relies upon whatever ``SIMPLEKEYS_RATE_LIMIT_BACKEND`` you're using
        storing data long enough.  If you're using the default cache-based backend
        you may want to configure ``SIMPLEKEYS_CACHE_TIMEOUT`` to be longer than a month
        if you're using a monthly quota.

    .. py:attribute:: requests_per_second

        Limits how quickly a user can access the API, regardless of their quota.

        It is possible for the user to briefly exceed this rate up to their ``burst_size``
        after which they'll be throttled back to this rate until they back off
        for a sufficient period of time.

        For specifics on this behavior you can read about 
        `token bucket <https://en.wikipedia.org/wiki/Token_bucket>`_
        rate-limiting.

    .. py:attribute:: burst_size

        The maximum number of requests allowed in a burst situation.  This should
        be configured to be somewhat higher than ``requests_per_second``.

.. py:class:: Key

    Keys are the tokens given to users to access the API.

    .. py:attribute:: key

        The actual key used for access, by default these are randomly generated UUIDs.

    .. py:attribute:: status

            * 'u' - Unactivated, requests will not be allowed, but validation will be. (If you're using the default views keys are created in this state and updated once the user confirms their email address.)
            * 'a' - Activated, requests will be allowed
            * 's' - Suspended, requests will not be allowed, neither will activation.

    .. py:attribute:: tier

        ForeignKey relationship to :class:`Tier` indicating which Tier this key has access to.

    .. py:attribute:: email

        Email address associated with the key.

    .. py:attribute:: name

        Name of individual associated with the key.

    .. py:attribute:: organization

        (Optional) organization associated with the key.

    .. py:attribute:: website

        (Optional) website associated with the key.

    .. py:attribute:: usage

        (Optional) Description of intended usage of the API key.

.. _views:

Class-based Views
-----------------

.. py:module:: simplekeys.views

.. py:class:: RegistrationView

    Presents user with a simple form they can fill out to obtain a key.

    Upon successful submission of the form a non-active key is created for the
    user, and an email is sent with a link that the user must click to verify
    their email address.

    Optional Arguments:

    template_name
        Name of template to use for registration form.

        This template should render the ``form`` context variable
        and provide a ``<form method="POST" action=".">`` to send the form
        contents back to the view for processing.

        Default: ``simplekeys/register.html``

    email_subject
        Subject of email sent to user.

        Default: ``API Key Registration``

    email_message_template
        Name of template to use for plain text email.

        This template is provided the newly-created ``Key`` instance as well
        as the fully-qualified ``confirmation_url`` based on the optional
        parameter described below.

        Default: ``simplekeys/confirmation_email.txt``

    from_email
        Email address from which to send.

        Default: ``DEFAULT_FROM_EMAIL``

    tier
        :ref:`tier` that will be used for permissions/rate limiting for this
        view.

        Default: ``default``

    redirect
        URL, view name, or model to redirect to after registration is complete.

        See `django's redirect shortcut <https://docs.djangoproject.com/en/1.11/topics/http/shortcuts/#redirect>`_ for options.

    confirmation_url
        URL to include in email, should match URL of :class:`ConfirmationView`

        If URL is a relative URL, will be appended to the current
        `Site` <https://docs.djangoproject.com/en/1.11/ref/contrib/sites/>`_

        Default: ``/confirm/``


.. py:class:: ConfirmationView

    After filling out the registration form the user is emailed a link to confirm
    their email address.  The user must visit this link to finish the process and
    activate their API key.

    This view is quite simple, when accessed via GET it will render
    ``confirmation_template_name`` and then when accessed via a successful POST
    will show ``confirmed_template_name``.

    If an attempt is made to access this view with invalid activation data
    this view returns an ``HttpResponseBadRequest`` 400 error.

    Optional Arguments:

    confirmation_template_name
        This template should render the ``form`` context variable
        and provide a ``<form method="POST" action=".">`` to send the form
        contents back to the view for processing.

        All fields on the form render as hidden, you can simply ask the user
        to press submit to proceed.

        Default: ``simplekeys/confirmation.html``

    confirmed_template
        Default: ``simplekeys/confirmed.html``

        This template is shown after the key is sucessfully activated.

        It is passed the newly activated ``Key`` instance, be sure to let the
        user know what their API key is!

.. _advanced-settings:

Advanced Settings
-----------------

``SIMPLEKEYS_DEFAULT_ZONE``
    If you use the :func:`key_required` without a ``zone`` parameter, 
    simplekeys will consider your view part of this zone.

    Default: ``default``

``SIMPLEKEYS_ZONE_PATHS``
    Used in conjunction with :class:`SimpleKeysMiddleware` to associate
    request paths with zones.

    Default: ``[('.*', 'default')]``

``SIMPLEKEYS_HEADER``
    HTTP header that :class:`SimpleKeysMiddleware` and :func:`key_required`
    will check for presence of API key.

    Default: ``HTTP_X_API_KEY``

``SIMPLEKEYS_QUERY_PARAM``
    HTTP query parameter that :class:`SimpleKeysMiddleware` and
    :func:`key_required` will check for presence of API key.
    (This check occurs after ``SIMPLEKEYS_HEADER`` check.)

    Default: ``apikey``

``SIMPLEKEYS_RATE_LIMIT_BACKEND``
    String representing full import path to a rate limit backend.

    Default: :class:`simplekeys.backends.CacheBackend`

``SIMPLEKEYS_CACHE``
    ``settings.CACHE`` entry to use for :class:`simplekeys.backends.CacheBackend`

    Default: ``default``

``SIMPLEKEYS_CACHE_TIMEOUT``
    Timeout for entries created by :class:`simplekeys.backends.CacheBackend`

    Default: ``25*60*60`` (25 hours)


Custom Rate Limiting Backends
-----------------------------

Keeping track of how many times a key is used requires some semi-permanent
storage that is relatively cheap to access.

Since Django's existing cache framework provides easy access to such data
stores, that is the default backend.

There is also a memory backend, which stores the rate-limiting data locally,
this is not intended for production use and should only be used if you know
what you're doing.

In both of these cases, the rate-limiting data is somewhat ephemeral, a
process restarting or a cache getting cleared will allow users to make more
calls than you might otherwise have expected.  If this does not meet your
needs it may be necessary to explore other options, or you may be able to
simply write a custom backend that writes to your storage of choice.

If you write a rate limiting backend that you think others might find useful,
please consider contributing back to the project.
