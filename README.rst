============
Om OS2mo 2.0
============

`OS2mo <https://os2.eu/projekt/os2mo>`_ er en webapplikation til håndtering af et medarbejder- og
organisationshierarki. Systemet sætter brugerne i stand til at navigere rundt i
eksempelvis organisationshierarkiet, indhente relevante informationer om de
forskellige organisationsenheder samt at redigere de data, der er tilknyttet
de forskellige enheder.

Dokumentation
=============

Dokumentationen for OS2mo kan findes på `Read The Docs <https://os2mo.readthedocs.io/>`_.

Dokumentation kan også bygges manuelt.
Til dette anvendes `Sphinx <http://www.sphinx-doc.org/en/stable/index.html>`_.
Kør nedenstående kommando for at autogenerere dokumentationen::

  $ ./docs/make html

Dokumentation kan nu findes ved at åbne filen
``/sti/til/mora/docs/out/index.html``.

Licens og Copyright
===================

Copyright (c) 2017-2019, Magenta ApS.

Dette værk er frigivet under `Mozilla Public License, version 2.0
<https://www.mozilla.org/en-US/MPL/>`_, som gengivet i ``LICENSE``. Dette er et
OS2 projekt. Ophavsretten tilhører de individuelle bidragydere.

Der findes en version af core-koden, og den er placeret her:
`https://github.com/OS2mo <https://github.com/OS2mo>`_.

Værket anvender følgende Open Source software-komponenter:

* `Flask <https://www.palletsprojects.com/p/flask/>`_, BSD License
* `Flask-Session <https://github.com/fengsp/flask-session>`_, BSD License
* `lxml <http://lxml.de/>`_, BSD License
* `python-dateutil <https://dateutil.readthedocs.io>`_, BSD License, Apache Software License
* `python3-saml <https://github.com/onelogin/python3-saml>`_, MIT License
* `requests <http://python-requests.org>`_, Apache Software License
* `vue.js <https://vuejs.org/>`_, MIT License
