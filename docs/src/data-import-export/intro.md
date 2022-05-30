---
title: OS2MO Data Import
---

Magentas officielle repo til integrationer og eksportfunktioner til
OS2MO.

For spørgsmål til koden eller brug af den, er man velkommen til at
kontakte Magenta ApS <info@magenta.dk\>

# Usage

Start en OS2mo stak vha. *docker-compose*, se detaljer her: https://os2mo.readthedocs.io/en/1.16.1/dev/environment/docker.html?#docker-compose

Når dette er sket, kan DIPEX udviklingsmiljøet startes med:

``` bash 
docker-compose up -d --build
```

Når kommandoen er kørt færdig, kan man hoppe ind i containeren med:

``` bash
docker-compose exec dipex /bin/bash
```

Dette giver en terminal i containeren, hvorfra diverse programmer kan køres. 

Et fælles entrypoint til programmerne findes ved at køre:

``` bash
python3 metacli.py
```

Forbindelsen imod OS2mo, kan testes med programmet *check_connectivity*: 

``` bash
python3 metacli.py check_connectivity --mora-base http://mo
```
