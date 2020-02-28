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
