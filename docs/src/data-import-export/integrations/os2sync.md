---
title: Integration til OS2Sync
---

### Indledning

Denne integration gør det muligt at sende data fra OS2MO til
[OS2Sync](https://www.os2sync.dk/). OS2Sync er i stand til at sende data
videre til FK ORG, såfremt det er installeret og konfigureret.
Integrationen læser flg. oplysninger i OS2MO, og sender dem til OS2Sync:

| OS2MO                 | Oplysninger                                                                                                                                           |
| --------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| Ansatte               | <ul<liUUID</li<liUserId</li<liNavn</li<liCPR-nummer</li<liAdresser</li<liEngagementer</li</ul                                           |
| Organisationsenheder  | <ul<liUUID</li<liParent UUID</li<liNavn</li<liIT-systemer</li<liAdresser</li<liKLE-opmærkninger</li<liLeder UUID (Optionelt)</li</ul  |

Når integrationen sender *ansatte* til OS2Sync, sker det efter
nedenstående skema:

| OS2Sync-felt     |   Udfyldes med                                                                                                                                                     |
| ---------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `Uuid`           | MO-brugerens UUID                                                                                                                                                  |
| `UserId`         | MO-brugerens UUID, medmindre der er registreret et IT-system af typen "AD" på MO-brugeren. I så fald bruges det AD-brugernavn, der er registreret på IT-systemet.  |
| `Person` `Name`  | MO-brugerens fornavn og efternavn                                                                                                                                  |
| `Person` `Cpr`   | MO-brugerens CPR-nummer, medmindre indstillingen `os2sync.xfer_cpr` er sat til `False`.                                                                            |

Når integrationen sender *organisationsenheders adresser* til OS2Sync,
sker det efter nedenstående skema. Såfremt en adresseoplysning på
enheden matcher på "Scope" og evt. "Brugervendt nøgle", sendes
oplysningen til feltet angivet i "OS2Sync-felt":

| Scope     | Brugervendt nøgle     | OS2Sync-felt         |
| --------- | --------------------- | -------------------- |
| `EMAIL`   |  (vilkårlig)          | `Email`              |
| `EAN`     |  (vilkårlig)          | `Ean`                |
| `PHONE`   |  (vilkårlig)          | `PhoneNumber`        |
| `DAR`     |  (vilkårlig)          | `Post`               |
| `PNUMBER` |  (vilkårlig)          | `Location`           |
| `TEXT`    |  `ContactOpenHours`   | `ContactOpenHours`   |
| `TEXT`    |  `DtrId`              | `DtrId`              |

### Opsætning

For at kunne afvikle integrationen kræves en række opsætninger af den
lokale server.

Opsætningen i `settings.json`

### fælles parametre

-   `crontab.RUN_OS2SYNC`: Bestemmer om jobbet skal køres i cron
    (true/false)
-   `crontab.SAML_TOKEN`: api token for service-adgang til OS2MO
-   `mora.base`: Beskriver OS2MO's adresse
-   `municipality.cvr` : Kommunens CVR-nummer

### os2syncs parametre

-   `os2sync.log_file`: logfil, typisk '/opt/dipex/os2sync.log'
-   `os2sync.log_level`: Loglevel, numerisk efter pythons
    logging-modul, typisk 10, som betyder at alt kommer ud
-   `os2sync.ca_verify_os2mo`: Angiver om OS2mo serverens certifikat
    skal checkes, typisk true
-   `os2sync.ca_verify_os2sync`: Angiver om Os2Sync containerens
    certifikat skal checkes, typisk true
-   `os2sync.hash_cache`: Cache som sørger for at kun ændringer
    overføres
-   `os2sync.phone_scope_classes`: Begrænsning af hvilke
    telefon-klasser, der kan komme op, anvendes typisk til at
    frasortere hemmelige telefonnumre
-   `os2sync.email_scope_classes`: Begrænsning af hvilke
    email-klasser, der kan komme op, anvendes typisk til at frasortere
    hemmelige email-addresser
-   `os2sync.api_url`: Adresse på os2sync-containeres API, typisk
    http://localhost:8081/api
-   `os2sync.top_unit_uuid`: UUID på den top-level organisation, der
    skal overføres
-   `os2sync.xfer_cpr`: Bestemmer om cpr-nummer skal overføres, typisk
    true
-   `os2sync.use_lc_db`: Bestemmer om kørslen skal anvende lora-cache
    for hastighed
-   `os2sync.ignored.unit_levels`: liste af unit-level-klasser, der
    skal ignoreres i overførslen
-   `os2sync.ignored.unit_types`: liste af unit-type-klasser, der skal
    ignoreres i overførslen
-   `os2sync.autowash`: sletning uden filter. Normalt slettes kun
    afdelinger i os2sync, som er forsvundet fra OS2MO. Med autowash
    slettes alt i os2syncs version af den administrative org, som ikke
    vil blive overført fra os2mo.
-   `os2sync.sync_managers`: Skriv leders uuid til orgunits. Kræver at
    der kun er en leder pr. enhed.
-   `os2sync.templates`: Giver mulighed for at styre formatteringen af
    data vha. Jinja-templates.
-   `os2sync_user_key_it_system_name`: Henter en brugers user_key fra
    IT-system. Default er "Active Directory"
-   `os2sync_uuid_from_it_systems`: Prioriteret liste af uuider på
    IT-systemer hvorfra en bruger/enheds uuid skal hentes. Bruger MOs
    uuid hvis denne er tom eller hvis de angivne it-systemer ikke er
    udfyldt i MO.

### `os2sync.templates`

Denne indstilling kan bruges til at styre, hvordan felter sendes til
OS2Sync. Indstillingen består af en eller flere feltnøgler, og en
tilhørende
[Jinja-template](https://jinja.palletsprojects.com/en/2.11.x/templates/).

På nuværende tidspunkt kender programmet feltnøglerne `person.name` og
`person.user_id`, der bruges til at kontrollere, hvordan hhv.
personnavne og bruger-id'er formatteres, når de sendes til OS2Sync.

Et eksempel på brug:

``` json
{
    "os2sync.templates": {
        "person.name": "{% if nickname -%}{{ nickname }}{%- else %}{{ name }}{%- endif %}"
    }
}
```

Denne opsætning betyder, at vi først tjekker om der er et kaldenavn
(`nickname`) registreret på personen i MO. Hvis der er, så anvendes
dette, når der skrives et personnavn til OS2Sync. Hvis ikke, så anvendes
det almindelige navn, der er registreret på personen (`name`.)

Et eksempel på brug af `person.user_id`:

``` json
{
    "os2sync.templates": {
        "person.user_id": "{{ user_key }}"
    }
}
```

Hvis OS2Sync-integrationen sættes op med denne opsætning, skriver den
MO-brugerens BVN (brugervendte nøgle) i OS2Sync-feltet `UserId`,
medmindre MO-brugeren også har et registreret IT-system af typen "AD".
I så fald anvendes det AD-brugernavn, der er registreret på IT-systemet.
