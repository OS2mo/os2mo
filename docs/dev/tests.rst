Testsuiten
==========

Der arbejdes i projektet med fire typer af tests:

1. Backend unit tests
2. Backend integration tests
3. Frontend unit tests
4. Frontend end-to-end tests

---------------------------------------
Backend unit tests og integration tests
---------------------------------------

Backend'en har en testsuite bestående af unit tests og integration tests. Disse
findes i :file:`backend/tests/`.

Hver test case køres op imod en LoRa-instans. Der ryddes mellem hver test case,
så testene effektivt set køres isoleret. LoRa-instansen kopierer eventuelle
data i databasen til en backup-database, og gendanner disse efter test-kørslen.

Efter at udviklingsmiljøet er startet med ``docker-compose up -d``, kan
backend unit tests og integration tests køres med kommandoen:

.. code-block:: bash

   docker-compose exec mo pytest

-------------------
Frontend unit tests
-------------------

Frontend-koden har en række unit tests, der tester Vue-koden på
komponent-niveau. Disse findes i :file:`frontend/tests/unit/`.

En stor del af kompleksiteten i frontend-koden består af koblingerne mellem de
forskellige Vue-komponenter. Disse koblinger bliver også testet i form af Vue
unit tests.

Efter at udviklingsmiljøet er startet med ``docker-compose up -d``, kan
frontend unit tests køres med kommandoen:

.. code-block:: bash

   docker-compose exec frontend yarn test:unit

Der kan produceres en HTML-rapport over `test coverage` ved at give flg.
kommando:

.. code-block:: bash

   docker-compose exec frontend yarn test:unit --coverage --coverageReporters=html

Coverage-rapporten kan så findes i :file:`frontend/coverage/index.html`.

-------------------------
Frontend end-to-end tests
-------------------------

Vores frontend har desuden end-to-end tests, der køres med værktøjet
`TestCafe <https://devexpress.github.io/testcafe/>`_.
Disse tests simulerer museklik, tastetryk, osv. i en "headless browser", og
tjekker, at der sker de ønskede ændringer på skærmen, når de forskellige sider
og popup-vinduer aktiveres.

Vores end-to-end tests kan ikke køre parallelt med backend'ens integration
tests, da de anvender samme LoRa-instans og samme database.
``testcafe``-servicen er derfor defineret i sin egen
:file:`dev-environment/docker-compose-testcafe.yml` for at den ikke starter op,
når man starter andre services op.

Efter at udviklingsmiljøet er startet med ``docker-compose up -d``, kan
TestCafe køres med kommandoen:

.. code-block:: bash

   docker-compose -f dev-environment/docker-compose-testcafe.yml up

(Dette kald skriver en warning om at der er `orphan containers`. Det er
forventeligt, og kan ignoreres. De normale services defineret i
:file:`docker-compose.yml` er fra kaldet til ``docker-compose -f
dev-environment/docker-compose-testcafe.yml`` set som `orphans`.)

Kør e2e tests lokalt
--------------------

Ovenstående Docker-løsning er ikke særlig brugbar, hvis man skal skrive nye
tests eller debugge eksisterende tests.

I stedet kan man installere pakker til at køre e2e tests lokalt på sin 
host maskine. (Forudsat man har NodeJS og Chrome installeret.)

.. code-block:: bash

   cd frontend/e2e-tests
   npm install

Derefter kan tests afvikles direkte i Chrome browser:

.. code-block:: bash

   npm run test


Husk korrekt konfiguration
--------------------------

Vær desuden opmærksom på, at end-to-end testene køres med den MO-konfiguration,
der er defineret i ``tests.util.load_sample_confdb``.
I denne MO-konfiguration er alle "feature flags" slået til, således at
frontend-koden kører med et fuldt MO feature-sæt.
Hvis du tilføjer flere MO feature flags, er det derfor en god ide at tilføje
navnet på dit feature flag til ``tests.util.load_sample_confdb``.
