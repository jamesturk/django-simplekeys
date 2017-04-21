Getting Started
===============

Step 1- Configure Settings
--------------------------

* Add ``simplekeys`` to ``INSTALLED_APPS`` as you would any app.
* Be sure to run the ``migrate`` command after adding the app to your project.
* If you want to protect every view in your app you can install :class:`simplekeys.middleware.SimpleKeysMiddleware` in your ``MIDDLEWARE_CLASSES`` setting.
* If you plan on using the provided registration view be sure you've set `DEFAULT_FROM_EMAIL <https://docs.djangoproject.com/en/1.11/ref/settings/#default-from-email>`_.
* Unless otherwise configured simplekeys will use Django's ``CACHE['default']`` to store ephemeral information used for rate-limiting.  Depending on your use case it may
  be desirable to configure Django's cache with this in mind.
* simplekeys doesn't require any other settings, but there are plenty of other things you can configure.  See :ref:`advanced-settings` for details.

Step 2- Configure Default Zones & Tiers
---------------------------------------

Typically this will be done via the Django admin, if you're not using the Django admin it is possible to do this via the shell but that is beyond the scope of this documentation.

For the simplest usage it is sufficient to create a :class:`Tier` and a :class:`Zone` with the slug ``default``.  You should then edit the ``Tier`` to have a :class:`Limit` configuration for the default zone.

For more detail on these concepts, see :ref:`models`.

.. warning::

    If you do not create an association between a ``Tier`` and a ``Zone`` then users will not be able to access any views that you define as being within a given ``Zone``.


Step 3- Protect API Views
-------------------------

Unless you used ``simplekeys.middleware.SimpleKeysMiddleware`` in Step 1, you'll need to let Django know which views require API keys.

This can be done using the :func:`key_required` decorator, it might look like::

    @key_required()
    def simple_api_view(request):
        ...


.. function:: simplekeys.decorators.key_required(zone=None)

    Decorator that specifies that a view should require an API key and will be
    throttled according to the rules of a specified zone.

    If ``zone`` parameter is omitted ``SIMPLEKEYS_DEFAULT_ZONE`` will be used
    (``default`` unless overriden)


Step 4- Add Registration Views (optional)
-----------------------------------------

simplekeys provides two class-based views that can be used together to provide
a simple email-based workflow for obtaining API keys.

You can also create ``Key`` instances via the Django admin or within your own
app, but these views are provided to accomodate a common flow out of the box.

You can use these two views by adding them to your ``urls.py`` like so::

    url(r'^register/$', RegistrationView.as_view()),
    url(r'^confirm/$', ConfirmationView.as_view()),

These two views are designed to work without any parameters but take quite a 
few optional parameters should you wish to customize their behavior.

See :ref:`views` for more details on overiding the defaults.

