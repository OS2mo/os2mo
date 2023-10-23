---
title: SDTOOL+
---

SDTOOL+ udvider SD-integrationen med muligheden for automatisk at ajourføre organisationstræet i OS2MO, så det svarer til organisationstræet i SD Løn. Det erstatter dermed den såkaldte "SDTool-knap" i OS2MO's brugerflade.

SDTOOL+ bygger ovenpå den Docker-baserede SD-integration, og er derfor afhængig af at denne kører.

SDTOOL+ er en FastAPI web-applikation, der udstiller et API via HTTP. Den antages at køre i samme Docker-netværk som resten af OS2MO-installationen (selve OS2MO og evt. andre integrationer.)

## Opsætning

SDTOOL+ kræver en række oplysninger for at kunne køre. Disse indstillinger gives vha. miljøvariable.

### Klient-oplysninger til OS2MO:

- `mora_base`: (Valgfri) URL, der angiver adressen på OS2MO. Default-værdi er `http://mo:5000`.
- `client_id`: (Valgfrit) klient-ID, der anvendes når SDTOOL+ kommunikerer med OS2MO. Default-værdi er `dipex`.
- `client_secret`: (Obligatorisk) klient-hemmelighed, der anvendes når SDTOOL+ kommunikerer med OS2MO.
- `auth_realm`: (Valgfri) "realm", der anvendes når SDTOOL+ kommunikerer med OS2MO. Default-værdi er `mo`.
- `auth_server`: (Valgfri) URL, der angiver adressen på den anvendte Keycloak-installation. Default-værdi er `http://keycloak:8080/auth`.

### Klient-oplysninger til SD-Løn:

- `sd_username`: (Obligatorisk) brugernavn til den SD-servicebruger, der anvendes ved opslag i SD-Løn.
- `sd_password`: (Obligatorisk) password på den SD-servicebruger, der anvendes ved opslag i SD-Løn.
- `sd_institution_identifier`: (Obligatorisk) institutions-ID, der anvendes ved opslag i SD-Løn.

### Klient-oplysninger til SD-integrationen:

- `sd_lon_base_url`: (Valgfri) URL på SD-integrationen, som SDTOOL+ kommunikerer med. Default-værdi er `http://sdtool_plus:8000`.

### Styring af SDTOOL+ enhedsoprettelse:

- `org_unit_type`: (Valgfrit) navn på den organisationenheds-type (`org_unit_type`), som SDTOOL+ skal anvende, når det opretter nye enheder i OS2MO. Default-værdi: `Enhed`.

### Logging, fejlrapportering, mv.:

- `log_level`: (Valgfrit) niveau for logging - default-værdi er `DEBUG`.
- `sentry_dsn`: (Valgfrit) DSN på Sentry, der anvendes til indsamling af fejlrapporter.

## Anvendelse

SDTOOL+ virker ved at det henter oplysninger om organisationstræets udseende i SD-Løn, og derefter bringer organisationstræet i OS2MO i overensstemmelse med SD-træet, ved at udføre de relevante oprettelser og ændringer i OS2MO's GraphQL-API.

SDTOOl+ anvender flg. dele af SD-Løns API:

- `GetOrganization20111201`
- `GetDepartment20111201`

SD-Løn ønsker ikke, at der laves for mange API-kald til disse dele af deres API, og derfor er SDTOOL+ indrettet på at blive aktiveret een gang dagligt, via et cronjob. Dette kan ske ved:

- `curl http://<SDTOOL+-url>/trigger`

Denne forespørgsel henter SD-organisationstræet, og ajourfører OS2MO-organisationstræet ud fra dette. SDTOOL+ svarer på forespørgslen med en liste af de ændringer, der er blevet udført i OS2MO-organisationstræet.

For hver organisationsenhed, som oprettes eller ændres i OS2MO ved denne kørsel, kalder SDTOOL+ endvidere `/trigger/fix-departments/{org_unit_uuid}` i SD-integrationen. Dette sikrer, at medarbejdere i OS2MO flyttes til den rette organisationsenhed (enten den ændrede enhed, eller en af dens overliggende enheder.)

SDTOOL+ kan detektere en enheds-sletning i SD, men effektuerer ikke denne sletning i OS2MO's organisationstræ, da sletning af enheder i SD anses for at være umulige, eller ihvertfald højest usædvanlige.

SDTOOL+ kan desuden udføre en "tør" kørsel således:

- `curl http://<SDTOOL+-url>/trigger`

Denne forespørgsel svarer med en liste af de ændringer, som _ville blive_ udført i OS2MO's organisationstræ.

SDTOOL+ kommunikerer med OS2MO's GraphQL-API, og forventer i skrivende stund GraphQL API-version 7.

## Monitorering og alarmer

SDTOOL+ skriver log-output til `stdout`, og defaulter til log-niveau `DEBUG`.

SDTOOL+ kan konfigureres til at indsende fejlrapporter til Sentry, således at "unhandled exceptions" i applikations-koden bliver opsamlet og sendt til Sentry.

SDTOOL+ vedligeholder et Prometheus `gauge` ved navn `dipex_last_success_timestamp`, som nulstilles ved hver ny kørsel af logikken i `/trigger`. Derved bliver det muligt at spore evt. manglende eller fejlende kørsler, ved at måle tiden siden den sidste succesfulde kørsel, og sammenligne med det forventede (typisk 1 succesfuld kørsel per døgn.)
