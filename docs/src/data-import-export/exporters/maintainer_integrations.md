---
title: Automatik til Vedligeholdelse
---

# Håndtering af Arbejdsprocesser gennem Automatisering

Nedenfor præsenteres de automatikker, der er udviklet, til at hjælpe med at promovere arbejdsgange.

## Stillingsbetegnelser

Hvis organisationens har medarbejderdata, der indeholder stillingsbetegnelser af følsom natur, kan det være en
udfodring at eksporterer eller importerer organisations data. Det kan fx være, at I importerer jeres medarbejder data
fra AD, hvor stillingsbetegnelserne ikke er synlige, eller at de kan gemmes væk. Måske er jeres stillingsbetegnelses
koder importeret fra SD løn, og kan indeholde sensitiv information, som i ikke ønsker fremstillet, idet i ser OS2MO
værende autoritativ for jeres organisation.

### Eventbaseret vedligeholdelse af stillingsbetegnelser

Applikationen har til formål at håndtere stillingsbetegnelser og eventuelle stillingsbetegnelses koder, som vi
overskriver, inden jeres organisationsdata bliver eksporteret til andre integrationer. Arbejdsgangen fremmes derfor, ved
at mindske jeres behov for manuelle rettelser i medarbejderdata.

Der bliver lyttet på ændringer samt oprettelser af nye engagementer, hvor engagementets indhold bliver hevet ud, og
stillingsbetegnelsen bliver, ud fra forretnings-specifikke ønsker, skrevet til et nyt felt. Den nye felt, som indeholder
titlen på stillingsbetegnelsen, bliver nu brugt som felt eller attribut, når der skal eksporteres data til andre
integrationer såsom `plan2learn`, `orgviewer`, `os2sync`, `sqleksport` eller andet som skulle ønskes.

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
