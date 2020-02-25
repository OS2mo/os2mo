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
Ubuntu's<docker-install>`.

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
automatisk OS2MO og `LoRa <https://github.com/magenta-aps/mox>`_ med tilhørende `postgres
<https://hub.docker.com/_/postgres>`_ op. Den sætter desuden også indstillinger
til at forbinde dem. Den starter også en Vue.js udviklingsserver op. Se mere
under :ref:`frontend-udvikling`.

Din host maskines :file:`./backend` bliver også mounted til den tilsvarende
mappe inde i backend containeren. Serveren bliver automatisk genstart ved
kodeændringer.

For at hente og bygge images og starte de fem services, kør:

.. code-block:: bash

   docker-compose up -d --build


``-d`` flaget starter servicene i baggrunden. Du kan se outputtet af dem med
``docker-compose logs <name>`` hvor ``<name>`` er navnet på servicen i
:file:`docker-compose.yml`. ``--build`` flaget bygger den nyeste version af
OS2MO imageet fra den lokale :file:`Dockerfile`.

For at stoppe servicene igen, kør ``docker-compose stop``. Servicene vil blive
stoppet, men datane vil blive bevaret. For helt at fjerne containerne og datane
, kør ``docker-compose down -v``.

Efter servicene er startet op kan du se dem på følgende porte på din
hostmaskine:


http://localhost:5001
  Frontend udviklingsserveren. Denne opdateres ved kodeændringer til frontenden.
  Se :ref:`frontend-udvikling`.

http://localhost:5000
  OS2MO backend og frontend. Denne opdateres *ikke* ved kodeændringer til
  frontenden, men opdatere ved kodeændringer til backenden.

http://localhost:8080
  LoRa


.. _frontend-udvikling:

Frontend udvikling
------------------

Du kan tilgå frontend på port ``5000``. Denne frontend er det produktionsklare
byg fra der sidst blev kørt ``docker-compose build`` eller ``docker-compose up
--build``. Den bliver altså *ikke* opdateret ved kodeændringer under
:file:`frontend/`.

For at udvikle på frontend, har :file:`docker-compose.yml` en service med navnet
`frontend` der kører ``vue-cli-service serve``. Den er bundet til port ``5001``.
Til denne service er :file:`frontend/` mountet ind og servicen sørger for at
opdatere ved kodeændringer i denne.

Forespørgelser til ``/service`` og ``/saml`` bliver proxyed videre til backenden i
`mo` containeren.



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
