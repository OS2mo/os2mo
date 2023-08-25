---
title: Automatik til Vedligeholdelse
---

# Håndtering af arbejdsprocesser gennem Automatisering

Nedenfor præsenteres de automatikker, der er udviklet til at hjælpe med at promovere arbejdsgange.

## Stillingsbetegnelser

Hvis organisationens har medarbejderdata, der indeholder stillingsbetegnelser af følsom natur, kan det være en
udfodring at eksporterer eller importerer organisations data. Det kan fx være, at I importerer jeres medarbejder data
fra AD, hvor stillingsbetegnelserne ikke er synlige, eller at de kan gemmes væk. Måske er jeres stillingsbetegnelses
koder importeret fra SD løn, og kan indeholde sensitiv information, som i ikke ønsker fremstillet, idet i ser OS2MO
værende autoritativ for jeres organisation.

### Automatisk og eventbaseret vedligeholdelse af stillingsbetegnelser

Applikationen har til formål at håndtere stillingsbetegnelser og eventuelle stillingsbetegnelses koder.
Derved mindskes behovet for manuelle rettelser i medarbejderdata.

"Applikationen 'lytter' på ændringer til stillingsbetegnelser, der kommer fra AD'et, samt på oprettelser af nye
engagementer (ansættelser), som indeholder stillingsbetegnelser. Stillingsbetegnelsen kan herefter eksporteres til andre
it-systemer, såsom
[plan2learn](https://rammearkitektur.docs.magenta.dk/os2mo/data-import-export/exporters/plan2learn.html),
[organisationsdiagrammet](https://rammearkitektur.docs.magenta.dk/os2mo/data-import-export/exporters/org-chart.html),
[FK Organisation](https://rammearkitektur.docs.magenta.dk/os2mo/data-import-export/exporters/os2sync.html) og
[SQL-databaser](https://rammearkitektur.docs.magenta.dk/os2mo/data-import-export/exporters/sql_export.html).

### Filtreringer

Applikationen er konfigurerbar, og kan tilpasses til organisations behov og ønsker. Medarbejderens stillingsbetegnelse
kan rettes og konfigureres fx ud fra

* addresse type
    * fx email, telefon, henvendelsessted, EAN-nummer, addresser m.m.
* addresse typens scope
    * fx arbejdsmail, privatmail, arbejdstelefon, privattelefon, lokation m.m
* stillingsbetegnelses koder
    * fx stillings koder og titler
* primær ansættelse
    * fx engagementets primære status
