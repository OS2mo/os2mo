---
title: OPUS Løn
---

# Integration til OPUS Løn

## Indledning

Denne integration gør det muligt at hente og opdatere organisations- og
medarbejderoplysninger fra XML dumps fra OPUS Løn til OS2MO

## Opsætning

Der er tre muligheder for læsning af opusfiler.

- Lokalt: Opusfilerne kopieres direkte til serverne. Stien
  specificeres i settings.json som
  `integrations.opus.import.xml_path`. Som regel er den
  `/opt/customer/`.

- Windows share: Filerne kan læses fra et windows share med SMB
  protokollen. Denne anvendes hvis `integrations.opus.smb_host` er udfyldt
  i settings.json.

  > Bemærk den skal udfyldes som `IP/sti`. Kræver desuden
  > en bruger med rettighed til at læse filerne og credentials sættes i
  > settings.json som `integrations.opus.smb_user` og
  > `integrations.opus.smb_password`.

- Google cloud storage: Filerne kan
  læses direkte fra google cloud storage. Dette kræver en service konto
  der er sat op på serveren med rettigheder til at læse filerne. Derudover
  er det kun `integrations.opus.gcloud_bucket_name` der skal udfyldes i
  settings.json med det navn som storage enheden har i google cloud.

Fælles for dem alle gælder at de enkelte dumps forventes at være
navngivet systematisk som: `ZLPE<dat0 + tid>_delta.xml`

Eksempelvis `ZLPE20190902224224_delta.xml`.

## Nuværende implementeringslogik for import fra Opus:

- Data indlæses i form at et xml-dump.
- Hvis data indeholder information om enhedstyper, oprettes disse
  enhedstyper som klasser, hvis ikke, får alle enheder typen
  `Enhed`.
- SE-, CVR-, EAN-, p-numre og telefon indlæses på enheder, hvis
  disse oplysninger er tilgængelige.
- Hvis data indeholder postadresser på enheder eller medarejdere,
  slås disse adresser op på DAR, og hvis det er muligt at få en
  entydigt match, gemmes DAR-uuid'en på enheden eller personen.
  Adresser med adressebeskyttelse importeres ikke.
- Telefon og email importeres for medarbejdere, hvis de findes i
  data.
- Ansættelsestyper og titler oprettes som klasser og sættes på de
  tilhørende engagementer. Ansættelsestypen læses fra feltet
  `workContractText`, hvis dette eksisterer, hvis ikke får
  medarbejderen typen `Ansat`.
- Information om ledere importeres direkte fra data, de to
  informationer `superiorLevel` og `subordinateLevel` konkateneres
  til et lederniveau.
- Information om roller importeres direkte fra data.

## IT-Systemer

En import fra OPUS vil oprette IT-systemet 'Opus' i MO. Alle
medarbejdere som har en værdi i feltet `userId` vil få skrevet deres
OPUS brugernavn på dette IT-system.

## AD-Integration

OPUS Importen understøtter at anvende komponenten
[Integration til Active Directory]() til at berige objekterne fra OPUS
med information fra Active Directory. I øjebliket er det muligt at
importere felterne `ObjectGuid` og `SamAccountName`.

Hvis AD integrationen er aktiv, vil importeren oprette IT-systemet
'Active Directory' og oprette alle brugere der findes i AD med
brugernavnet fundet i `SamAccountName`. Brugere med en AD konto vil
blive oprettet med deres AD `ObjectGuid` som UUID på deres brugerobjekt,
med mindre de er angivet i en cpr-mapning.

## cpr-mapning

For at kunne lave en frisk import uden at få nye UUID'er på
medarbejderne, er det muligt at give importen adgang til et csv-udtræk
som parrer cpr-numre med UUID'er. Disse UUID'er vil altid få forrang
og garanterer derfor at en medarbejder får netop denne UUID, hvis
vedkommendes cpr-nummer er i csv-udtrækket. Udtrækket kan produceres fra
en kørende instans af MO ved hjælp ved værktøkjet `cpr_uuid.py`, som
findes under `exports`.

## Primær ansættelse

I XML dumps fra Opus findes ikke et koncept om primæransættelse, men da
AD integrationen til MO har behov for at kunne genkende den primære
ansættelse til synkronisering, bestemmes dette ud fra en beregning:

Den mest afgørende komponent af beregningen foregår på baggrund af
ansættelestypen, hvor en liste af uuid'er i `settings.json` bestemmer
hvilke ansættelstyper der anses for at være mest primære. Hvis flere
engagementer har den samme ansættelsestype, vælges ansættelsen med det
laveste ansættelsenummer. Hvis en ansættelse er manuelt angivet til at
være primær, vil denne ansættelse altid regnes som primær.

Informationen om primæransætelse opretholdes i MOs facet `primary_type`,
som ved import fra Opus XML altid populeres med disse tre klasser:

- Manuelt primær ansættelse: Dette felt angiver at en ansættelse
  manuelt er sat til at være primær
- Ansat: Angiver en medarbejders beregnede primære ansættelse.
- Ikke-primær ansat: Angiver alle andre ansættelser for en
  medarbejder.

Manuelt primær optræder ikke direkte i imports, men kan sættes manuelt
fra MOs GUI. De øvrige primærklasser håndteres af Opus integrationen, og
må ikke sættes manuelt.

En medarbejder skifter ikke ansættelsestype selvom vedkommende fratræder
sit engagement. En ansættelses aktuelle status angives i stedet via MOs
start- og slutdato. Er slutdato'en i fortiden, er vedkommende ikke
længere ansat og vil i MOs gui fremgå i fanen fortid. Er en medarbejers
startdato i fremtiden, er personen endnu ikke tiltrådt, og fremgår i
fanen fremtid.

## Anvendelse af integrationen

For at anvende integrationen kræves udover de nævnte xml-dumps, at der
oprettes en gyldig konfiguration i `settings.json`. De påkrævede nøgler
er:

- `mox.base`: Adressen på LoRa.

- `mora.base`: Adressen på MO.

- `integrations.opus.import.run_db`: Stien til den database som
  gemmer information om kørsler af integrationen. Hvis integrationen
  skal køre som mere end et engangsimport har denne fil en vigtig
  betydning.

- `municipality.name`: Navnet på kommunen.

- `crontab.SAML_TOKEN`: saml token til forbindelse til OS2MO

- `integrations.opus.skip_employees`: **Optionelt.**

  > Kan sættes til _true_ for kun at læse
  > organisationsenheder fra opus-filerne.

Til at hjælpe med afviklingen af importen, findes en hjælpefunktion i
`opus_helpers.py` som afvikler selve importen og initialiserer databasen
i `opus.import.run_db` korrekt. Dette modul forventer at finde en
cpr-mapning og vil fejle hvis ikke filen `settings/cpr_uuid_map.csv`
eksisterer.

### Førstegangsimport (initialindlæsning)

Hvis den nuværende import er den første, findes der i reglen ikke nogen
mapning, og der må så oprettes en tom fil i dens sted
(`settings/cpr_uuid_map.csv`)

før kaldet af initialindlæsning skal SAML_TOKEN være defineret i
environment. Det kan man få igennem at source (dotte)
tools/prefixed_settings.sh når man, som det sig hør og bør, er placeret
i roden af directoriet os2mo-data-import-and-export.

Ligeledes må databasen, som er defineret i `opus.import.run_db` ikke
findes og lora-databasen skal være tom.

## Løbende opdatering af Opus data i MO

Der er skrevet et program som foretager løbende opdateringer til MO
efterhåden som der sker ændringer i Opus data. Dette foregår ved, at
integrationen hver gang den afvikles, kigger efter det ældste xml-dump
som endnu ikke er importeret og importerer alle ændringer i dette som er
nyere end den seneste importering. Et objekt regnes som opdateret hvis
parameteren `lastChanged` på objektet er nyere end tidspunktet for det
senest importerede xml-dump. Alle andre objekter ignoreres.

Hvis et objekt er nyt, foretages en sammenligning af de enkelte felter,
og de som er ændret, opdateres i MO med virkning fra `lastChanged`
datoen. En undtagelse for dette er engagementer, som vil blive oprettet
med virkning fra `entryDate` datoen, og altså således kan oprettes med
virkning i fortiden.

Også opdateringsmodulet forventer at finde en cpr-mapning, som vil blive
anvendt til at knytte bestemte UUID'er på bestemte personer, hvis disse
har været importeret tidligere. Denne funktionalitet er nyttig, hvis man
får brug for at re-importere alle Opus-data, og vælger at arbejde sig
igennem gamle dumps for at importere historik. I daglig brug vil
mapningen ikke have nogen betydning, da oprettede brugere her altid vil
være nye.

## Opdatering af enkelte brugere

Skulle det af den ene eller den anden grund ske, at en bruger ikke er
importeret korrekt, er det muligt at efterimportere denne bruger.
Funktionen er endnu ret ny og det tilrådes derfor altid at tage en
backup af databasen før den benyttes. Funktionen fungerer ved at hente
historiske data fra gamle xml-dumps, og det er derfor en forudsætning,
at disse dumps stadig er til rådighed. For at synkronisere en enkelt
medarbejder anvedes disse kommandolinjeparametre:

- `--update-single-user`: Ansættelsesnummer på den relevante
  medarbejder
- `days`: Antal dage bagud integrationen skal søge.

### Nuværende begrænsninger omkring re-import

- IT-systemer tilknyttes kun i forbindelse med oprettelsen af en
  medarbejder, de tildeles uendelig virkning og nedlægges aldrig.
- Ændringer i roller håndteres kun ved ændringer i slutdatoer, det
  antages at startdatoer ikke ændres.
- Tomme ændringer på en leder opdages ikke, så der opstår en ekstra
  række på lederobjekter hvis en leder ændres. Den resulterende
  tilstand er korrekt, men indeholder en kunstig skæringsdato i sin
  historik.
- Der oprettes ikke automatisk nye engagementstyper, alle
  engagementer forventes at have en type som blev oprettet ved
  førstegangsimporten.
- Der oprettes ikke automatisk nye lederniveauer, alle ledere
  forventes at have et niveau som eksisterede ved
  førstegangsimporten.

## run_db.sqlite

For at holde rede på hvornår MO sidst er opdateret fra Opus, findes en
SQLite database som indeholder to rækker for hver færdiggjort kørsel.
Adressen på denne database er angivet i `settings.json` under nøglen
`opus.import.run_db`.

Programmet `db_overview.py` er i stand til at læse denne database og
giver et outut som dette:

```log
id: 1, dump date: 2019-09-02 22:41:28, status: Running since 2019-11-19 08:32:30.575527
id: 2, dump date: 2019-09-02 22:41:28, status: Import ended: 2019-11-19 08:55:32.455146
id: 3, dump date: 2019-09-03 22:40:12, status: Running diff update since 2019-11-19 10:18:35.859294
id: 4, dump date: 2019-09-03 22:40:12, status: Diff update ended: 2019-11-19 10:19:15.806079
id: 5, dump date: 2019-09-04 22:40:12, status: Running diff update since 2019-11-19 10:19:16.006959
id: 6, dump date: 2019-09-04 22:40:12, status: Diff update ended: 2019-11-19 10:19:48.980694
id: 7, dump date: 2019-09-05 22:40:12, status: Running diff update since 2019-11-19 10:19:49.187977
id: 8, dump date: 2019-09-05 22:40:12, status: Diff update ended: 2019-11-19 10:20:23.547771
id: 9, dump date: 2019-09-06 22:40:13, status: Running diff update since 2019-11-19 10:20:23.745032
id: 10, dump date: 2019-09-06 22:40:13, status: Diff update ended: 2019-11-19 10:20:54.931163
id: 11, dump date: 2019-09-09 22:40:12, status: Running diff update since 2019-11-19 10:20:55.123478
id: 12, dump date: 2019-09-09 22:40:12, status: Diff update ended: 2019-11-19 10:21:35.481189
id: 13, dump date: 2019-09-10 22:40:12, status: Running diff update since 2019-11-19 10:21:35.682252
id: 14, dump date: 2019-09-10 22:40:12, status: Diff update ended: 2019-11-19 10:22:12.298526
id: 15, dump date: 2019-09-11 22:41:48, status: Running diff update since 2019-11-19 10:22:12.496829
id: 16, dump date: 2019-09-11 22:41:48, status: Diff update ended: 2019-11-19 10:22:45.317372
id: 17, dump date: 2019-09-12 22:40:12, status: Running diff update since 2019-11-19 10:22:45.517679
id: 18, dump date: 2019-09-12 22:40:12, status: Diff update ended: 2019-11-19 10:23:20.548220
id: 19, dump date: 2019-09-13 22:40:14, status: Running diff update since 2019-11-19 10:23:20.744435
id: 20, dump date: 2019-09-13 22:40:14, status: Diff update ended: 2019-11-19 10:23:51.416625
id: 21, dump date: 2019-09-16 22:40:12, status: Running diff update since 2019-11-19 10:23:51.610555
id: 22, dump date: 2019-09-16 22:40:12, status: Diff update ended: 2019-11-19 10:24:44.799932
id: 23, dump date: 2019-09-17 22:40:12, status: Running diff update since 2019-11-19 10:24:45.000445
id: 24, dump date: 2019-09-17 22:40:12, status: Diff update ended: 2019-11-19 10:25:25.651491
(True, 'Status ok')
```

Ved starten af alle opus_diff_import kørsler, skrives en linje med
status `Running` og efter hver kørsel skrives en linje med status
`Diff update ended`. En kørsel kan ikke startes hvis den nyeste linje
har status `Running`, da dette enten betyder at integrationen allerede
kører, eller at den seneste kørsel fejlede.

## Filtrering af organisationsenheder

Den valgfrie nøgle `integrations.opus.units.filter_ids` kan sættes for
at filtrere udvalgte organisationenheder og deres tilhørende
underliggende organisationsenheder fra, før selve importen kører.

Nølgen skal være en liste indeholdende OPUS ID'er for de
organisationsenheder, som ønskes filtreret fra. OPUS ID findes i OPUS
filen `<orgUnit id="350" client="813" lastChanged="2020-09-16">`
