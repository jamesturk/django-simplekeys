Changelog
=========

0.6.0
-----
    * drop Django 1.x & Python 2 support
    * use newer Django cache features to improve performance

0.5.3
-----
**2018-12-19**
    * reactivating an active key doesn't show unhelpful error message anymore

0.5.2
-----
**2018-10-29**
    * add missing migration

0.5.1
-----
**2018-05-18**
    * added abillity to search keys to admin

0.5.0
-----
**2017-12-12**
    * exportkeys management command
    * usagereport management command

0.4.2
-----
**2017-05-22**

    * error message tweak
    * addition of SIMPLEKEYS_ERROR_NOTE

0.4.0
-----
**2017-05-22**

    * refactored decorator and middleware to be independent
    * added SIMPLEKEYS_ZONE_PATHS for middleware

0.3.0
-----
**2017-04-21**

    * made organization optional & added optional website & usage fields to Key
      (requires migration!)


0.2.0
-----
**2017-04-18**

    * documented & cleaned up API and made more consistent with Django

0.1.0
-----
    * initial prototype with MVP functionality for `Open States <https://openstates.org>`_.
