Version 0.11.0 (in development)
===============================

New features
------------
* #24547: Edit behaviour for employee name and cpr number
* #24400: Better documentation of command line interface.
* #24750: Added functionality for listing and retrieving generated export files from external directory.

Internal changes
----------------

* TBD

API changes
-----------

* TBD

Bug fixes
---------

* #24150: When terminating an employee, mark any manager roles it
  possesses as vacant rather than terminating them.

Known bugs
----------

* #24134: Sorting doesn't work after performing an update.

Version 0.10.1-post1, 2018-10-12
================================

Bug fixes
---------

* A missing check for Node packages broke the `mox
  <http://github.com/magenta-aps/mox/>` test suite.

Known bugs
----------

* #24134: Sorting doesn't work after performing an update.


Version 0.10.1, 2018-10-08
==========================

New features
------------

* #22849: Updated SAML implementation, with support for signed requests,
  single sign-on and single logout.
* #22381: Replace 'Enhedsnummer' with a description of the location of the organisational unit.
* #23558: Added the possibility to create managers without employees through the ou endpoint, thus allowing for vacant manager positions.
* #24014: Since we now model IT systems using an
  ``organisationfunktion``, we can now represent the account name.
* #22849: Added handling for user permissions, giving a fitting error if a user attempts an action without the correct permissions.
* #23976: Employees with their associated relations can now be created with one API call. All requests are now validated before being submitted to LoRa, to prevent half-writes.
* #24134: Columns in the UI can now be sorted.
* #24135: Dropdowns are now alphabetically sorted.
* #24068: Clicking the OS2-icon in the top left corner now takes you to the landing page.
* #23793: Support has been added for P-nummer as address type.
* #23781: Managers now have a separate set of address types.

Internal changes
----------------

* #23559: REST API now uses and enforces ISO 8601 dates in all cases
  except history display. All ``from`` or ``to`` dates must either
  lack a timestamp or correspond to midnight, Central European time.
* #23559: The ``terminate`` endpoints for employees as well as units
  now read the date from the ``to`` field rather than ``from``.
* #24198: We now model IT systems using ``organisationfunktion``
  rather than a direct relation.
* #23558: The employee is now optional on managers.

API changes
-----------

* #24200: Move all writing and editing APIs from ``/service/ou`` and
  ``/service/e/`` to a shared endpoint ``/service/details``. This
  primarily means that writing operations no longer require knowledge of the
  user, allowing e.g. vacant managers.

Bug fixes
---------

* #24067: Fixed being able to edit root organisational units
* #23559: Display end dates *inclusively*, so that the year ends 31
  December rather than 1 January.

Known bugs
----------

* #24134: Sorting doesn't work after performing an update.

Version 0.9.0, 2018-09-07
=========================

New features
------------

* #23778: Support for IT-systems on units
  
Internal changes
----------------

* #23992: Updated API documentation and README
* #23993: Reorganisation of source code layout
* #23994: Refactoring of frontend code

Bug fixes
---------

* #24012: Fixed hotkey support
* #24013: Fixed rename unit dialog not being populated correctly
