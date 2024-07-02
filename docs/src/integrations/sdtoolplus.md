---
title: SDTOOL+
---

## Beskrivelse

SDs API indeholder muligheden for at hente seneste ændringer på personer og
disses engagementer. Det er også muligt at hente informationer om
organisationsenhedernes træstruktur, men ikke i form af de seneste ændringer,
hvilket gør det svært at vedligeholde organisationsenhedstrukturen fra SD i
OS2mo. SDTool+ løser dette problem, idet det udvider SD-integrationen med muligheden
for automatisk at ajourføre organisationstræet i OS2mo, så det svarer til
organisationstræet i SD Løn. Det erstatter dermed den såkaldte "SDTool-knap" i
OS2mo's brugerflade, som vil blive udfaset inden længe.

SDTool+ køres via et automatisk job (fx en gang dagligt), og vil ved hver
kørsel gøre følgende:

1. Udlæse alle organisationsenheder fra SD og bygge det tilhørende
   organisationstræ.
    1. Det grundlæggende organisatonstræ bygges via SDs endpoint
       `GetOrganization20111201`, som udstiller alle enheder i træet, der har et
       afdelingsniveau som blad (leaf node) i
       [træstrukturen](https://en.wikipedia.org/wiki/Tree_(data_structure)).
    2. Dernæst tilføjes de resterende enheder (NY-niveauer, som ikke har
       et afdelingsniveau under sig længere ned i træet) ved at kigge på
       forskellen mellem ovenstående respons fra `GetOrganization20111201` og
       responset fra `GetDepartment20111201` (som indeholder _alle_ enheder,
       men ikke informationer om deres forældreneheder) og responsene fra en
       række kald til `GetDepartmentParent20190701` returnerer forlældreenheden
       for en given enhed.
2. Udlæse alle organisationsenheder i OS2mo og bygge det tilhørende
   organisationstræ.
3. Sammenligne SD-organisationstræet og OS2mo-organisationstræet og generere en
   liste af operationer, som skal udføres på OS2mo-træet. Operationerne kan
   være af typen "Tilføj", som tilføjer nye enheder fra SD, eller
   "Opdatér", som flytter enheder til en ny forældrenhed og/eller omdøber
   enheder.
     1. Der er mulighed for at få frafiltreret enheder fra SD, som man ikke
        ønsker synkroniseret til OS2mo - fx enheder, som begynder med "Ø_"
        eller "%" eller lignende.
     2. Der er også mulighed for at konfigurere SDTool+ til kun at sammenligne
        et givet undertræ i OS2mo med organisationstræet i SD.
4. Sikre, at der ved opdateringsoperationer, hvor en enhed potentielt kan have fået en ny
   forældrenhed), laves et kald til SD-integrationen (SD-changed-at), som
   sikrer, at engagementer flyttes op i et nyt relevant NY-niveau, såfremt
   dette skulle være nødvendigt pga. den potentielt nye forældreenhed (denne
   funktionalitet kaldes "apply-NY-logic" og er ikke relevant for alle kunder).
5. (Valgfri feature) Udsende emails til relevante medarbejdere såfremt SDTool+
   forsøger at udføre en "ulovlig" operation. Ved en ulovlig operation forstås
   flytning af en enhed, som stadig indeholder aktive eller fremtidigt aktive
   engagementer, til enheden "Udgåede afdelinger" (navn kan variere fra
   kunde til kunde).

SDTOOL+ bygger ovenpå den Docker-baserede SD-integration, og er derfor afhængig af at denne kører.

SDTOOL+ er en FastAPI web-applikation, der udstiller et API via HTTP. Den antages at køre i samme Docker-netværk som resten af OS2mo-installationen (selve OS2mo og evt. andre integrationer.)

## Opsætning

SDTOOL+ kræver en række oplysninger for at kunne køre. Disse indstillinger gives vha. miljøvariable.

### Klient-oplysninger til OS2mo:

- `mora_base`: (Valgfri) URL, der angiver adressen på OS2mo. Default-værdi er `http://mo:5000`.
- `client_id`: (Valgfrit) klient-ID, der anvendes når SDTOOL+ kommunikerer med OS2mo. Default-værdi er `integration_sdtool_plus`.
- `client_secret`: (Obligatorisk) klient-hemmelighed, der anvendes når SDTOOL+ kommunikerer med OS2mo.
- `auth_realm`: (Valgfri) "realm", der anvendes når SDTOOL+ kommunikerer med OS2mo. Default-værdi er `mo`.
- `auth_server`: (Valgfri) URL, der angiver adressen på den anvendte Keycloak-installation. Default-værdi er `http://keycloak:8080/auth`.

### Klient-oplysninger til SD-Løn:

- `sd_username`: (Obligatorisk) brugernavn til den SD-servicebruger, der anvendes ved opslag i SD-Løn.
- `sd_password`: (Obligatorisk) password på den SD-servicebruger, der anvendes ved opslag i SD-Løn.
- `sd_institution_identifier`: (Obligatorisk) institutions-ID, der anvendes ved opslag i SD-Løn.

### Klient-oplysninger til SD-integrationen:

- `sd_lon_base_url`: (Valgfri) URL på SD-integrationen, som SDTOOL+ kommunikerer med. Default-værdi er `http://sdtool_plus:8000`.

### Styring af SDTOOL+ enhedsoprettelse:

- `org_unit_type`: (Valgfrit) navn på den organisationenheds-type (`org_unit_type`), som SDTOOL+ skal anvende, når det opretter nye enheder i OS2mo. Default-værdi: `Enhed`.

### Logging, fejlrapportering, mv.:

- `log_level`: (Valgfrit) niveau for logging - default-værdi er `INFO`.
- `sentry_dsn`: (Valgfrit) DSN på Sentry, der anvendes til indsamling af fejlrapporter.

## Anvendelse

SDTOOL+ virker ved at det henter oplysninger om organisationstræets udseende i SD-Løn, og derefter bringer organisationstræet i OS2mo i overensstemmelse med SD-træet, ved at udføre de relevante oprettelser og ændringer i OS2mo's GraphQL-API.

SDTOOl+ anvender flg. dele af SD-Løns API:

- `GetOrganization20111201`
- `GetDepartment20111201`

SD-Løn ønsker, at der ikke laves for mange API-kald til disse dele af deres API, og derfor er SDTOOL+ indrettet på at blive aktiveret een gang dagligt, via et cronjob. Dette kan ske ved:

- `curl -X POST http://<SDTOOL+-url>/trigger`

Denne forespørgsel henter SD-organisationstræet, og ajourfører OS2mo-organisationstræet ud fra dette. SDTOOL+ svarer på forespørgslen med en liste af de ændringer, der er blevet udført i OS2mo-organisationstræet.

For hver organisationsenhed, som oprettes eller ændres i OS2mo ved denne kørsel, kalder SDTOOL+ endvidere `/trigger/fix-departments/{org_unit_uuid}` i SD-integrationen. Dette sikrer, at medarbejdere i OS2mo flyttes til den rette organisationsenhed (enten den ændrede enhed, eller en af dens overliggende enheder.)

SDTOOL+ kan detektere en enheds-sletning i SD, men effektuerer ikke denne sletning i OS2mo's organisationstræ, da sletning af enheder i SD anses for at være umulige, eller ihvertfald højest usædvanlige, idet den gængse SD-praksis er at flytte nedlagte enheder ned under en enhed kaldet "Lukkede afdelinger" eller lignende.

SDTOOL+ kan desuden udføre en "tør" kørsel således:

- `curl -X POST http://<SDTOOL+-url>/trigger/dry`

Denne forespørgsel svarer med en liste af de ændringer, som _ville blive_ udført i OS2mo's organisationstræ.

SDTOOL+ kommunikerer med OS2mo's GraphQL-API, og forventer i skrivende stund GraphQL API-version 7.

## Monitorering og alarmer

SDTOOL+ skriver log-output til `stdout`, og defaulter til log-niveau `DEBUG`.

SDTOOL+ kan konfigureres til at indsende fejlrapporter til Sentry, således at "unhandled exceptions" i applikations-koden bliver opsamlet og sendt til Sentry.

SDTOOL+ vedligeholder et Prometheus `gauge` ved navn `dipex_last_success_timestamp`, som nulstilles ved hver ny kørsel af logikken i `/trigger`. Derved bliver det muligt at spore evt. manglende eller fejlende kørsler, ved at måle tiden siden den sidste succesfulde kørsel, og sammenligne med det forventede (typisk 1 succesfuld kørsel per døgn.)
