=======
Om MORa
=======

.. contents:: `Indhold`
   :depth: 2

.. image:: http://lorajenkins.atlas.magenta.dk/buildStatus/icon?job=mora/development
   :alt: Build Status
   :target: http://lorajenkins.atlas.magenta.dk/job/mora/job/development/


Introduktion
------------

MORa er en webapplikation til håndtering af et medarbejder- og
organisationshierarki. Systemet sætter brugerne i stand til at navigere rundt i
eksempelvis organisationshierarkiet, indhente relevante informationer om de
forskellige organisationsenheder samt at redigere de data, der er tilknyttet
de forskellige enheder.

Navnet MORa er en sammentrækning af MO og LoRa og
refererer til hhv. `OS2MO <https://os2.eu/projekt/os2mo>`_ og den
`Lokale Rammearkitektur <https://digitaliser.dk/group/3101080/members>`_.
Nedenstående figur viser et typisk eksempel på en side i systemet brugerflade:

   :width: 800
.. image:: docs/graphics/os2mo-1280.png

Opbygning
---------

Den modulære opbygning af MORa ses på nedenstående figur.

.. image:: docs/graphics/MOmoduler.png
   :width: 800

MORa består af frontend og en middleend og sidstnævnte kommunikerer med en LoRa
backend. De enkelte moduler kan opfattes som elementer i
`MVC-modellen <https://en.wikipedia.org/wiki/
Model%E2%80%93view%E2%80%93controller>`_:

MO (Frontend / View)
~~~~~~~~~~~~~~~~~~~~
MOs frontend er skrevet i Javascript frameworket
`AngularJS <https://angularjs.org/>`_. Frontenden kan opfattes som *View* i
MVC-modellen, og brugerne interagerer med applikationen via denne. Frontenden
kommunikerer indirekte med Lora via MOs middleend.

LoRa (Backend / Model)
~~~~~~~~~~~~~~~~~~~~~~
En `LoRa <https://github.com/magenta-aps/mox>`_ backend, som gemmer alle data
i en PostgreSQL-database. Disse data udstilles og manipuleres via en
RESTful service skrevet i Python. LoRa kan opfattes som *Model* i MVC-modellen.

MO (Middleend / Control)
~~~~~~~~~~~~~~~~~~~~~~~~
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
----------------------------

I princippet er det muligt at foretage videreudvikling af MORa uden at have
en kørende instans af LoRa (idet man blot skriver tests til den udviklede
kode), men i praksis vil det være mest praktisk med en kørende LoRa, som man
kan udvikle op imod. Det anbefales derfor at installere LoRa i eksempelvis en
Linux container som `LXC <https://linuxcontainers.org/>`_ eller lignende, som
kører på udviklingsmaskinen. Nærmere instruktioner vedr. selve installationen
af LoRa kan findes på LoRas GitHub-side, som er linket til ovenfor.

For at installere de nødvendige afhængigheder på en Ubuntu-maskine, køres
følgende kommandoer::

  $ sudo apt install python3 python3-venv

Derudover er følgende systemafhængigheder påkrævet af vores nuværende Python-afhængigheder::

  $ sudo apt install build-essential libssl-dev libffi-dev python3-dev xmlsec1

Efterfølgende klones MORa-projektet fra GitHub::

  $ mkdir /path/to/folder
  $ cd /path/to/folder
  $ git clone https://github.com/magenta-aps/mora


Nyere NodeJS-versioner er ikke includeret i Ubuntu 16.04 (LTS),
derfor bør NodeJS LTS-versionen installeres via et eksternt apt repository.

Installationen af NodeJS kan udføres i følgende trin,

Tilføj nodesource public nøgle::

  $ cd setup/nodesource
  $ sudo apt-key add nodesource.gpg.key


Nodesource apt repository skal tilføjes::

  # Add list file
  $ cd setup/nodesource
  $ sudo cp nodesource-8.x.list /etc/apt/sources.list.d/nodesource-8.x.list

  # Update apt cache
  $ sudo apt-get update

Installer nodejs meta pakken::

  $ sudo apt-get install nodejs


Bekræft at version 8 er installeret::

  $ node -v
  v8.11.1


Herefter installeres følgende afhængighed::

  $ curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | sudo apt-key add -
  $ echo "deb https://dl.yarnpkg.com/debian/ stable main" | sudo tee /etc/apt/sources.list.d/yarn.list

  $ sudo apt-get update && sudo apt-get install yarn


Man kan nu på sædvanligvis manuelt installere det virtuelle miljø, som Python
skal køre i og de nødvendige Python-moduler (med "pip install -r requirements.txt"),
men det nemmeste er blot at anvende scriptet
``flask.sh``. Første gang, skal front-enden bygges::

  $ cd /path/to/folder/mora/backend
  $ ./flask.sh build

Hvorefter følgende kommando kan køres::

  $ ./flask.sh run

Dette vil automatisk oprette et vituelt Python-miljø, installere de
nødvendige Python-afhængigheder og starte applikationen (lyttende på
port 5000). Applikationen kan således tilgås på *http://localhost:5000*.
Bemærk dog, at der først skal uploades data til LoRa - til dette formål
kan man med fordel anvende ``flask.sh``.

Generel brug af kommandolinieværktøjet
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Scriptet ``flask.sh`` kan bruges til en række forskellige operationer. De
mulige funktioner ses ved blot at køre scriptet fra kommandolinjen
uden argumenter::

  $ /path/to/folder/mora/backend/flask.sh

hvilket vil resultere i flg. output::

  Usage: /path/to/folder/mora/backend/flask.sh [OPTIONS] COMMAND [ARGS]...

    Management utility for MORA.

  Options:
    --version  Show the flask version
    --help     Show this message and exit.

  Commands:
    auth
    build          Build the frontend application.
    develop        Run for development.
    fixroots       Import the sample fixtures into LoRA.
    get
    import         Import an Excel spreadsheet into LoRa
    load-fixtures  Import the sample fixtures into LoRA.
    python
    run            Runs a development server.
    sheet-convert  Convert a spreadsheet to another format.
    shell          Runs a shell in the app context.
    test
    update

En liste af mulige funktioner ses under *Commands*. Hvis man fx vil importere
et regneark med data til en kørende LoRa-instans, kan dette gøre således
(for passende værdier af sti til regneark)::

  $ ./flask.sh import spreadsheets /sti/til/regneark.xlsx

Ønsker man dokumentation for syntaksen af en given kommando, skriver man fx::

  $ ./flask.sh import

Som vil angive, hvad den korrekte syntaks er::

  Usage: flask.sh import [OPTIONS] SPREADSHEET [URL]

  Error: Missing argument "spreadsheet".

For yderligere detaljer om brugen af ``flask.sh`` henvises til
kildekoden og den indbyggede hjælp.

Konfiguration
~~~~~~~~~~~~~

Indstillinger gemmes i ``setup/mora.json``. Den vigtiste er
``LORA_URL``; denne kan også sættes som en miljøvariabel::

  MORA_LORA_URL=http://localhost:5000 ./flask.sh run


Testsuiten
-----------
Der arbejdes i proktet med tre typer af tests:

1. Unit tests
2. Integration tests
3. End-to-end tests

En del af integrationstestene er sat op til at køre på en sådan måde, at der
startes en LoRa-instans før de enkelte test cases kører. Hver test case
køres derefter op imod LoRa-instansen, idet der ryddes op i LoRa mellem hver
test case, så testene effektivt set køres isoleret. For at anvende denne test
feature kræver det følgende afhængigheder::

  $ sudo apt install libxmlsec1-dev libxmlsec1-openssl postgresql-contrib

Testsuiten kan køres med kommandoen::

  $ ./flask.sh test

End-to-end tests
----------------

Vores end-to-end tests køres typisk som en del af testsuiten. For at
køre den direkte mod en udviklingsmaskine anvendes eksempelvis::

  cd frontend
  BASE_URL=http://localhost:5000/ yarn testcafe --speed 0.5 firefox e2e-tests

Dokumentation
-------------

Det er muligt at autogenerere dokumentation ud fra doc-strings i kildekoden.
Til dette anvendes `Sphinx <http://www.sphinx-doc.org/en/stable/index.html>`_.
Kør nedenstående kommando for at autogenerere dokumentationen::

  $ ./docs/make html

Dokumentation kan nu findes ved at åbne filen
``/sti/til/mora/docs/out/index.html``.
