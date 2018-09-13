Version 0.10.0 (In development)
===============================

New features
------------

* #22849: Implemented support for signed SAML AuthN Requests.

Internal changes
----------------

* #23559: REST API now uses and enforces ISO 8601 dates in all cases
  except history display. All ``from`` or ``to`` dates must either
  lack a timestamp or correspond to midnight, Central European time.

Bug fixes
---------

* #23559: Display end dates *inclusively*, so that the year ends 31
  December rather than 1 January.

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
