Getting Started
===============

Step 1- Configure Settings
--------------------------

* Add ``simplekeys`` to ``INSTALLED_APPS`` as you would any app.
* Be sure to run the ``migrate`` command after adding the app to your project.
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

There are two ways to let Django know which views are protected and assign them
to particular zones:

    * ``simplekeys.middleware.SimpleKeysMiddleware`` allows you to define views by regex, similar to a urlconf.  The downside is that this check has to happen on every request.  
    * You can also use the :func:`key_required` decorator to annotate certain views, this will be more efficient, but requires you to decorate views individually- which may be difficult depending upon your setup.

If you add ``simplekeys.middleware.SimpleKeysMiddleware`` to your installed
middleware, by default it will protect every view.  Unless your app is very
simple (and you don't use the Django admin, etc.) you probably also want to
add the ``SIMPLEKEYS_ZONE_PATHS`` setting.

``SIMPLEKEYS_ZONE_PATHS`` is a list of tuples that looks like::

    SIMPLEKEYS_ZONE_PATHS = [
        ('/api/v1/legislators/geo/', 'geo'),
        ('/api/v1/', 'default'),
    ]

This would place the ``/api/v1/legislators/geo/`` method into the 'geo' zone
and all other ``/api/v1/`` methods into the default zone.  These strings are
matched with ``re.match``- so you can design complex rules as needed.

Alternatively, if you choose to use the :func:`key_required` decorator, 
it might look like::

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

