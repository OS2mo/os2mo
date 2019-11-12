Opsætning af udviklingsmiljø
============================

.. tip::

   TL;DR: for at få et udviklingsmiljø, kør:

   .. code-block:: bash

      git clone https://github.com/OS2mo/os2mo.git
      cd os2mo
      docker-compose up mox-cp
      docker-compose up -d --build mo


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
<https://docs.docker.com/install/>`_.

Containeren kræver en forbindelse til en `LoRa instans
<https://github.com/magenta-aps/mox>`_. Den kan sættes via miljøvairablen
``OS2MO_LORA_URL``. Desuden kræves enten en forbindelse til Serviceplatformen
som sættes via miljøvariablerne ``OS2MO_SP_*``. Alternativt kan OS2MO lave en
attrap af Serviceplatformen. Det gøres ved at sætte miljøvariablen
``OS2MO_DUMMY_MODE=True``.

For at starte en OS2MO container med en attrap af Serviceplatform, køres
følgende:

.. code-block:: bash

    docker run -p 5000:5000 -e OS2MO_LORA_URL=http://<LoRa-IP>:8080/ -e OS2MO_DUMMY_MODE=True magentaaps/os2mo:latest

Den henter docker imaget fra Docker Hub og starter en container i forgrunden.
``-p 5000:5000`` `binds port
<https://docs.docker.com/engine/reference/commandline/run/#publish-or-expose-port--p---expose>`_
``5000`` på host maskinen til port ``5000`` i containeren. ``-e`` `sætter den
efterfølgende miljøvariabel
<https://docs.docker.com/engine/reference/commandline/run/#set-environment-variables--e---env---env-file>`_
i containeren.

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
automatisk OS2MO og `LoRa <https://hub.docker.com/r/magentaaps/mox>` med
tilhørende `postgres <https://hub.docker.com/_/postgres>`_ op. Den sætter
desuden også miljøvariablerne til at forbinde dem.

Den mounter også din host maskines :file:`./backend` til den tilsvarende mappe
inde i containeren og automatisk genstarter serveren ved kodeændringer.


For at kopiere :ref:`MOX database filer til
initialisering <mox:db_user_ext_init>` kør:

.. code-block:: bash

   docker-compose up -d --build mox-cp mo-cp

For at hente og bygge images og starte de tre services, kør:

.. code-block:: bash

   docker-compose up -d --build mo


``-d`` flaget starter servicene i baggrunden. Du kan se outputtet af dem med
``docker-compose logs <name>`` hvor ``<name>`` er navnent på scervicen i
:file:`docker-compose.yml`. ``--build`` flaget bygger den nyeste version af
OS2MO imageet fra den lokale :file:`Dockerfile`.

For at stoppe servicene igen, kør ``docker-compose stop``. Servicene vil blive
stoppet, men datane vil blive bevaret. For helt at fjerne containerne og datane
, kør ``docker-compose down``.
