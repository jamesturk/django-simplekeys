Getting Started
===============

Requirements
------------

* simplekeys currently supports Django 1.8 through Django 1.11. Future versions will drop support for Django <= 1.10.
* simplekeys is tested against Python 2.7, Python 3.5, and Python 3.6.

Usage
-----

Step 1- Configure Settings
**************************

* Add ``simplekeys`` to ``INSTALLED_APPS`` as you would any app.
* If you want to protect every view in your app you can install ``simplekeys.middleware.SimpleKeysMiddleware`` in your ``MIDDLEWARE_CLASSES`` setting.
* If you plan on using the provided registration view be sure you've set `DEFAULT_FROM_EMAIL <https://docs.djangoproject.com/en/1.11/ref/settings/#default-from-email>`_.
* Unless otherwise configured simplekeys will use Django's ``CACHE['default']`` to store ephemeral information used for rate-limiting.  Depending on your use case it may
  be desirable to configure Django's cache with this in mind.
* simplekeys doesn't require any other settings, but there are plenty of other things you can configure.  See :ref:`advanced-settings` for details.

Step 2- Configure Default Zones & Tiers
***************************************

Typically this will be done via the Django admin, if you're not using the Django admin it is possible to do this via the shell but that is beyond the scope of this documentation.

Tiers
    simplekeys has the concept of different keys having different usage limits.

    For example: you could define a silver tier and a gold tier, where gold
    tier keys have higher rate limits due to being trusted users.

    Each API key is associated with a single tier.

    If you only want to have one tier, it is recommended you call it ``default``.

Zones
    simplekeys allows you to define different API zones.  This is intended to
    allow you to specify different rate limits for different API methods.

    Each tier can have different limitations defined on different zones.
    If a tier doesn't have any association with a zone it will not be allowed
    to access it, giving you fine grained control over which keys can access
    which endpoints.

    If all of your API methods will have the same rate limits, you can just
    use a single zone.  Default settings assume you call this ``default``.

.. warning::

    If you do not create an association between a ``Tier`` and a ``Zone`` then users will not be able to access any views that you define as being within a given ``Zone``.


Step 3- Protect Views
*********************

Unless you used ``simplekeys.middleware.SimpleKeysMiddleware`` in Step 1, you'll need to let Django know which views require API keys.

This can be done using the ``key_required`` decorator:

.. function:: simplekeys.decorators.key_required(zone=None)

    Decorator that specifies that a view should require an API key and will be
    throttled according to the rules of a specified zone.

    If ``zone`` parameter is omitted ``SIMPLEKEYS_DEFAULT_ZONE`` will be used
    (``default`` unless overriden)


Step 4- Add Registration Views (optional)
*****************************************

simplekeys provides two class-based views that can be used together to provide
a simple email-based workflow for obtaining API keys.

You can also create ``Key`` instances via the Django admin or within your own
app, but these views are provided to accomodate a common flow out of the box.

.. class:: simplekeys.views.RegistrationView

    Presents user with a simple form they can fill out to obtain a key.

    Upon successful submission of the form a non-active key is created for the
    user, and an email is sent with a link that the user must click to verify
    their email address.

    Variables:

    template_name
        Name of template to use for registration form.
        Default: "simplekeys/register.html"

    email_subject
        Subject of email sent to user.

        Default: "API Key Registration"

    email_message_template
        Name of template to use

        Default: "simplekeys/confirmation_email.txt"

    from_email = settings.DEFAULT_FROM_EMAIL
    tier = 'default'
    redirect = '/'
    confirmation_url = '/confirm/'
