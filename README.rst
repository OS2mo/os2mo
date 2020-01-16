============
Om OS2MO 2.0
============

.. contents:: `Indhold`
   :depth: 2

.. image:: https://lorajenkins.magenta.dk/buildStatus/icon?job=mora/development
   :alt: Build Status
   :target: https://lorajenkins.magenta.dk/job/mora/job/development/


Introduktion
============

MORa er en webapplikation til håndtering af et medarbejder- og
organisationshierarki. Systemet sætter brugerne i stand til at navigere rundt i
eksempelvis organisationshierarkiet, indhente relevante informationer om de
forskellige organisationsenheder samt at redigere de data, der er tilknyttet
de forskellige enheder.

Navnet MORa er en sammentrækning af MO og LoRa og
refererer til hhv. `OS2MO <https://os2.eu/projekt/os2mo>`_ og den
`Lokale Rammearkitektur <https://digitaliser.dk/group/3101080/members>`_.
Nedenstående figur viser et typisk eksempel på en side i systemet brugerflade:

.. image:: ./graphics/os2mo-1280.png
   :width: 100%

MO manual
=========
Denne manual introducerer til centrale begreber og funktionaliteter i OS2mo.


`MO manual <https://github.com/OS2mo/os2mo/blob/development/docs/static/MO manual.pdf>`_

MOs systemlandskab og eksisterende og kommende integrationer
============================================================

`MOs systemlandskab <https://github.com/OS2mo/os2mo/blob/development/docs/graphics/OS2mo_landskabet.png>`_

Opbygning
=========

Den modulære opbygning af MORa ses på nedenstående figur.

.. image:: ./graphics/MOmoduler.png
   :width: 100%

MORa består af frontend og en middleend og sidstnævnte kommunikerer med en LoRa
backend. De enkelte moduler kan opfattes som elementer i
`MVC-modellen <https://en.wikipedia.org/wiki/
Model%E2%80%93view%E2%80%93controller>`_:

--------------------
MO (Frontend / View)
--------------------
MOs frontend er skrevet i Javascript frameworket
`Vue.js`_. Frontenden kan opfattes som *View* i
MVC-modellen, og brugerne interagerer med applikationen via denne. Frontenden
kommunikerer indirekte med Lora via MOs middleend.

----------------------
LoRa (Backend / Model)
----------------------
En `LoRa <https://github.com/magenta-aps/mox>`_ backend, som gemmer alle data
i en PostgreSQL-database. Disse data udstilles og manipuleres via en
RESTful service skrevet i Python. LoRa kan opfattes som *Model* i MVC-modellen.
LoRa anvender OIO-standarderne for sag, dokument, organisation og klassifikation

MO betjener sig af udvidelser af datamodellen i LoRa. Før Lora kan anvendes sammen
med MO skal disse tilretninger afspejles i databasen.

--------------------------------------
MO-tilretninger af datamodellen i LoRa
--------------------------------------

For at få datamodellen i LoRa til at afspejle datamodellen i MO skal LoRAs
konfiguration justeres så den anvender en anden databaseopsætning. MOs model
findes i LoRa repositoriet under ``oio_rest/oio_rest/db_extensions/mo-01.json``.
LoRa kan konfigureres med følgende for at bruge MOs datamodeludviddelse:

.. code-block:: toml

   [db_extensions]
   path = "oio_rest/oio_rest/db_extensions/mo-01.json"

Dette skal sættes som en del af konfigurationen af LoRA inden
databasen initialiseres. Derudover skal det være
sat under kørslen.

Uden denne indstilling vil eksempelvis kaldenavn og primære
engagementer ikke kunne lagres.

------------------------
MO (Middleend / Control)
------------------------
MOs middleend fungerer som en bro mellem frontenden og backenden, og den har
til opgave at oversætte de data, der sendes mellem frontenden og backenden til
passende JSON formater, når der udføres læse- og skriveoperationer fra og
til LoRa (se flere detaljer nedenfor).

Når der læses fra LoRa, leverer denne data i et JSON-format, som
frontenden ikke umiddelbart kan tolke, hvorfor middleenden oversætter disse
til det JSON-format, som frontenden forventer. Tilsvarende sender frontenden
ved skriveoperationer JSON i et format, som skal oversættes af middleenden til
det JSON-format, som kræves af LoRa's REST API. Middlend kan opfattes som *Control* i MVC-modellen.



Opsætning af udviklingsmiljø
============================

.. tip::

   TL;DR: for at få et udviklingsmiljø, kør:

   .. code-block:: bash

      git clone git@git.magenta.dk:rammearkitektur/os2mo.git # Or https://github.com/OS2mo/os2mo.git
      cd os2mo
      docker-compose up -d --build


------
Docker
------

Repositoriet inderholder en :file:`Dockerfile`. Det er den anbefalede måde at
installere OS2MO i produktion og som udvikler.

Alle releases bliver sendt til  Docker Hub på `magentaaps/os2mo
<https://hub.docker.com/r/magentaaps/os2mo>`_ under tagget ``latest``. Tagget
``dev-latest`` indeholder det seneste byg af ``development`` branchen.

For at køre OS2MO i docker, skal du have en kørende docker instans. For
installationen af denne, referere vi til `den officielle dokumentation
<https://docs.docker.com/install/>`_. Alternativt er her :ref:`en kort guide til
Ubuntu s<docker-install>`.

Containeren kræver en forbindelse til en `LoRa instans
<https://github.com/magenta-aps/mox>`_. Den kan sættes via :ref:`indstillingen
<settings>` ``[lora] url``. Desuden kræves enten en forbindelse til
Serviceplatformen som indstilles under ``[service_platformen]``. Alternativt kan
OS2MO lave en attrap af Serviceplatformen. Det gøres ved at sætte indstillingen
``dummy_mode = true``.

Disse indstillinger laves i en TOML fil der bindes til ``/user-settings.toml`` i
containeren.

For at starte en OS2MO container køres følgende:

.. code-block:: bash

    docker run -p 5000:5000 -v /path/to/user-settings.toml:/user-settings.toml magentaaps/os2mo:latest

Den henter docker imaget fra Docker Hub og starter en container i forgrunden.
``-p 5000:5000`` `binds port
<https://docs.docker.com/engine/reference/commandline/run/#publish-or-expose-port--p---expose>`_
``5000`` på host maskinen til port ``5000`` i containeren. ``-v`` `binder
<https://docs.docker.com/engine/reference/commandline/run/#mount-volume--v---read-only>`_
``/path/to/user-settings.toml`` på host maskinen til ``/user-settings.toml``
inde i containeren.

Hvis serveren starter rigtigt op skulle du kunne tilgå den på fra din host
maskine på ``http://localhost:5000``.


Brugerrettigheder
-----------------

:file:`Dockerfile` laver en ``mora`` brugerkonto der kører applikationen.
Brugerkonto ejer alle filer lavet af applikationen. Brugerkontoen har ``UID`` og
``GID`` på 72020.

Hvis du vil kører under en anden ``UID/GID``, kan du specificere det med
``--user=uid:gid`` `flaget
<https://docs.docker.com/engine/reference/run/#user>`_ til ``docker run`` eller
`i docker-compose
<https://docs.docker.com/compose/compose-file/#domainname-hostname-ipc-mac_address-privileged-read_only-shm_size-stdin_open-tty-user-working_dir>`_.

--------------
Docker-compose
--------------

Du kan bruge ``docker-compose`` til at starte OS2MO, LoRa og relaterede services
op.

En :file:`docker-compose.yml` til udvikling er inkluderet. Den starter
automatisk OS2MO og `LoRa`_ med
tilhørende `postgres <https://hub.docker.com/_/postgres>`_ op. Den sætter
desuden også miljøvariablerne til at forbinde dem.

Den mounter også din host maskines :file:`./backend` til den tilsvarende mappe
inde i containeren og automatisk genstarter serveren ved kodeændringer.

For at hente og bygge images og starte de tre services, kør:

.. code-block:: bash

   docker-compose up -d --build


``-d`` flaget starter servicene i baggrunden. Du kan se outputtet af dem med
``docker-compose logs <name>`` hvor ``<name>`` er navnent på scervicen i
:file:`docker-compose.yml`. ``--build`` flaget bygger den nyeste version af
OS2MO imageet fra den lokale :file:`Dockerfile`.

For at stoppe servicene igen, kør ``docker-compose stop``. Servicene vil blive
stoppet, men datane vil blive bevaret. For helt at fjerne containerne og datane
, kør ``docker-compose down -v``.


.. _docker-install:

-----------------------------
Docker installation på Ubuntu
-----------------------------

`Den officielle dokumentation til Docker <https://docs.docker.com/install/>`__
indeholder udførlig dokumentation for installering på all platforme. Den kan dog
være svær at navigere. Derfor er her en kort guide til at installere nyeste
version af Docker og docker-compose på Ubuntu:

.. code-block:: bash

   sudo apt-get update

   curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -

   sudo add-apt-repository \
   "deb [arch=amd64] https://download.docker.com/linux/ubuntu \
   $(lsb_release -cs) \
   stable"

   sudo apt-get update
   sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose


Testsuiten
==========

Der arbejdes i projektet med tre typer af tests:

1. Unit tests
2. Integration tests
3. End-to-end tests

------------------------
Unit og Integration test
------------------------

Hver test case køres op imod en LoRa-instans, der ryddes mellem hver test case
så testene effektivt set køres isoleret. LoRa instansen kopierer eventuelle data
i databasen til en backup lokation og gendanner disse efter testkørslen.

Efter udviklingsmiljøet er startet med ``docker-compose up -d`` kan
testsuiten køres med kommandoen:

.. code-block:: bash

   docker-compose exec mo pytest

----------------
End-to-end tests
----------------

Vores end-to-end tests køres ikke som en del af testsuiten. De kan ikke køre
parallelt med integrationsstestene da de anvender samme LoRa instans og samme
database. ``testcafe`` servicen er defineret i sin egen
:file:`dev-environment/docker-compose-testcafe.yml` for at den ikke starter op
når man starter andre services op.

Efter udviklingsmiljøet er startet med ``docker-compose up -d`` kan testcafe
køres med kommandoen:

.. code-block:: bash

   docker-compose -f dev-environment/docker-compose-testcafe.yml up

Dette kald skriver en warning om at der er orphan containers. Det er
forventeligt og kan ignoreres. De normale services defineret i
:file:`docker-compose.yml` er fra kaldet til ``docker-compose -f
dev-environment/docker-compose-testcafe.yml`` set som orphans.

Dokumentation
=============

Det er muligt at autogenerere dokumentation ud fra doc-strings i kildekoden.
Til dette anvendes `Sphinx <http://www.sphinx-doc.org/en/stable/index.html>`_.
Kør nedenstående kommando for at autogenerere dokumentationen::

  $ ./docs/make html

Dokumentation kan nu findes ved at åbne filen
``/sti/til/mora/docs/out/index.html``.

Kodestandarder
==============

Der anvendes overalt i python-koden styleguiden `PEP 8 <https://www.python.org/dev/peps/pep-0008/>`_.

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
