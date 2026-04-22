# OS2Rollekatalog

## Indledning

Denne integration synkroniserer organisationsdata fra OS2mo til
[OS2Rollekatalog](https://www.os2.eu/os2rollekatalog). Integrationen er
eventdrevet og reagerer på ændringer i OS2mo (medarbejdere, IT-konti,
adresser, engagementer, organisationsenheder, ledere og KLE). Ændringer
opsamles i en lokal cache og sendes samlet til Rollekatalog med et
konfigurerbart interval.

## Datamodel i MO

For at en medarbejder kan synkroniseres, skal personen have mindst ét
gyldigt engagement under den konfigurerede rodenhed, samt to IT-konti
i OS2mo:

- **AD**: Indeholder SAMAccountName (brugernavnet) i `user_key` og
  ObjectGUID i `external_id`.
- **FK Organisation**: Indeholder AD-kontoens ObjectGUID i `user_key`
  (som kobler de to konti sammen) og FK-UUID'et i `external_id`. Det er
  FK-UUID'et der sendes som `extUuid` til Rollekatalog.

Desuden anvendes specifikke adressetyper til e-mail (standard
`EmailEmployee`) og MitID (standard `MitIDEmployee`).

## Medarbejdere

Følgende data sendes til Rollekatalog for hver medarbejder:

| Felt           | Beskrivelse                                                           |
|----------------|-----------------------------------------------------------------------|
| `extUuid`      | Ekstern UUID fra FK Organisation IT-kontoen                           |
| `nemloginUuid` | MitID-UUID (valgfrit)                                                 |
| `userId`       | SAMAccountName fra AD IT-kontoen                                      |
| `name`         | Navn eller kaldenavn (afhængigt af konfiguration)                     |
| `email`        | E-mailadresse fra den konfigurerede adressetype                       |
| `positions`    | Engagementer med stillingsbetegnelse, enheds-UUID og evt. titel-UUID  |

En medarbejder synkroniseres ikke, hvis personen mangler en AD-konto,
mangler en tilsvarende FK Organisation-konto, eller ikke har gyldige
engagementer under rodenheden. Hvis en tidligere synkroniseret
medarbejder falder ud af scope, fjernes brugeren fra Rollekatalog.

## Organisationsenheder

Følgende data sendes til Rollekatalog for hver organisationsenhed:

| Felt                | Beskrivelse                                        |
|---------------------|----------------------------------------------------|
| `uuid`              | Enhedens UUID                                      |
| `name`              | Enhedens navn                                      |
| `parentOrgUnitUuid` | UUID på overenheden                                |
| `manager`           | Leder (UUID og SAMAccountName) — maks. én pr. enhed |
| `klePerforming`     | KLE-opmærkninger, udførende                        |
| `kleInterest`       | KLE-opmærkninger, indsigt                          |

Enheder uden for det konfigurerede organisationstræ synkroniseres ikke.
Et enhedsniveau kan konfigureres som ekskluderet, hvilket frafiltrerer
enheder på det niveau samt alle deres underenheder. Enheder der fjernes
i OS2mo eller falder ud af scope, fjernes også fra Rollekatalog.

## Stillingsbetegnelser

Når `SYNC_TITLES` er slået til, synkroniseres alle klasser fra facetten
`engagement_job_function` til Rollekatalog som særskilte
stillingsbetegnelses-objekter. Engagementer får da også et titel-UUID
med, så de kobles til den rigtige stillingsbetegnelse. Er synkroniseringen
slået fra, sendes stillingsbetegnelser kun som tekstfelt på engagementet.

## Opsætning og konfiguration

Integrationen køres i Docker. Se `docker-compose.yml` i repositoriet for
et eksempel på udviklingsopsætning.

Påkrævede miljøvariable:

- `ROLLEKATALOG_URL`: Base URL til Rollekatalogets API
- `API_KEY`: API-nøgle til autentificering med Rollekatalog
- `ROOT_ORG_UNIT`: UUID på rodenheden i OS2mo. Kun denne enhed og dens
  underenheder synkroniseres.
- `AD_ITSYSTEM_USER_KEY`: Brugervendt nøgle på AD IT-systemet i OS2mo
- `FK_ITSYSTEM_USER_KEY`: Brugervendt nøgle på FK Organisation
  IT-systemet i OS2mo
- `FASTRAMQPI__DATABASE__*`: Forbindelsesoplysninger til den lokale
  PostgreSQL-database (host, user, password, name)

Valgfrie miljøvariable:

- `SYNC_ENABLED`: Aktiverer skrivning til Rollekatalog. Default `false`,
  så integrationen kan opbygge sin cache inden første skrivning.
- `INTERVAL`: Interval i sekunder mellem batchskrivninger til
  Rollekatalog. Default `900` (15 minutter).
- `EXTERNAL_ROOTS`: Liste af UUID'er på eksterne pseudorødder. Disse
  placeres under rodenheden i Rollekatalog.
- `EXCLUDE_ORG_UNIT_LEVEL`: UUID på et enhedsniveau der skal udelukkes
  fra synkroniseringen.
- `PREFER_NICKNAME`: Brug kaldenavn i stedet for navn, hvis det er
  udfyldt. Default `false`.
- `SYNC_TITLES`: Synkroniser stillingsbetegnelser som særskilte objekter.
  Default `false`.
- `EMPLOYEE_EMAIL_USER_KEY`: Brugervendt nøgle på adressetypen for
  medarbejder-e-mail. Default `EmailEmployee`.
- `MIT_ID_USER_KEY`: Brugervendt nøgle på adressetypen for MitID.
  Default `MitIDEmployee`.
- `HTTPX_TIMEOUT`: Timeout i sekunder ved API-kald til Rollekatalog.
  Default `30`.

## Fejlfinding

Integrationen udstiller en række HTTP-endepunkter til inspektion og
manuel styring af synkroniseringen:

| Metode | Endepunkt                           | Beskrivelse                                                     |
|--------|-------------------------------------|-----------------------------------------------------------------|
| GET    | `/titles`                           | Viser stillingsbetegnelser der ville blive synkroniseret        |
| GET    | `/cache/stikprøve/person?count=N`   | Tilfældig stikprøve af medarbejdere fra cachen                  |
| GET    | `/cache/stikprøve/org_unit?count=N` | Tilfældig stikprøve af organisationsenheder fra cachen          |
| GET    | `/cache/person/{uuid}`              | Viser en medarbejder som den ligger i cachen                    |
| GET    | `/cache/org_unit/{uuid}`            | Viser en organisationsenhed som den ligger i cachen             |
| GET    | `/debug/person/{uuid}`              | Simulerer synkronisering af en medarbejder (viser evt. fejl)    |
| GET    | `/debug/org_unit/{uuid}`            | Simulerer synkronisering af en enhed (viser evt. fejl)          |
| POST   | `/sync/person/{uuid}`               | Udløser synkronisering af en specifik medarbejder               |
| POST   | `/sync/org_unit/{uuid}`             | Udløser synkronisering af en specifik organisationsenhed        |
| POST   | `/trigger/all`                      | Udløser fuld genindlæsning af alle objekter fra OS2mo           |

`/debug/*`-endepunkterne er særligt nyttige til at undersøge hvorfor en
medarbejder eller enhed ikke bliver synkroniseret — hvis objektet ikke
kan synkroniseres, returneres en fejlbesked med årsagen.

## Idriftsættelse

Ved førstegangsopsætning anbefales følgende fremgangsmåde:

1. Start integrationen med `SYNC_ENABLED=false`, så den lokale cache
   opbygges uden at skrive til Rollekatalog.
2. Udløs en fuld genindlæsning fra OS2mo ved at kalde `POST /trigger/all`
   på integrationen.
3. Verificer data i cachen via fejlfindings-endepunkterne beskrevet
   ovenfor.
4. Sæt `SYNC_ENABLED=true`, og genstart integrationen.
