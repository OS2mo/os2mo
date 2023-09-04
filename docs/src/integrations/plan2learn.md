---
title: Eksport til plan2learn
---

## Indledning

Denne eksport script bygger datafiler som via sftp kan sendes til
plan2learn.

Koden består af to dele *plan2learn.py* som foretager
eksporteringen fra MO til 5 csv-filer, samt *ship_files.py*,
som via ftpes afleverer filerne til Play2Learn. Forbindelsesoplysninger
på ftp-serveren angives i *settings.json* via tre nøgler:

-   *exporters.plan2learn.host*
-   *exporters.plan2learn.user*
-   *exporters.plan2learn.password*

Værktøjet har mulighed for at anvende to forskellige backends til at
hente data: de kan hentes fra MO, eller direkte fra LoRa via
LoRa-cache-mekanisme som også anvendes i andre eksportmoduler.
LoRa-cache udgaven er langt den hurtigste og MO backenden er
hovedsageligt bibeholdt for at kunne foretage en sammenligning mellem de
to backends med henblik på fejlfinding.

## Implementeringsstrategi

Der udarbejdes i alt 5 csv udtræk:

-   *bruger.csv*: Udtræk af alle nuværende og kendte fremtidigt
    aktive brugere i kommunen.
-   *organisation.csv*: Udtræk af alle organisationsenheder og deres
    relation til hinanden.
-   *engagement.csv*: Udtræk over alle nuværende og kendte
    fremtidige engagementer.
-   *stillingskode.csv*: Udtræk over alle aktive
    stillingsbetegnelser.
-   *leder.csv*: Udtræk over alle ledere i kommunen.

## Brugerudtrækket

I dette udtræk eksporteres disse felter:

-   *BrugerId*: Brugerens uuid i MO
-   *CPR*: Brugerens cpr-nummer
-   *Navn*: Brugerens fulde navn, ikke opdelt i fornavn og efteranvn
-   *E-mail*: Hvis brugeren har en email i MO, angives den her.
-   *Mobil*: Hvis brugeren har en mobiltelefon i MO, angives den
    her.
-   *Stilling*: Stillingsbetegnelse for brugerens primærengagement.
    Hvis dette engagement har en stillingsbetegnelse skrevet i feltet
    extension_2 anvendes dette, og ellers anvendes
    stillingsbetegnelsen fra engagementet.

E-mail og mobiltelefon genkenes via bestemte klasse under adressetype,
disse klasse er for nuværende hårdkodet direkte i python filen, men vil
på sigt blive flyttet til *settings.json*.

Kun personer med ansættelsestype Timeløn eller Månedsløn inkluderes i
udtrækket. Disse typer genkendes via en liste med de to uuid'er på
typerne, for nuværende er listen hårdkoden direkte i python filen, men
vil på sigt blive flyttet til *settings.json*.

## Organisation

I dette udtræk eksporteres disse felter:

-   *AfdelingsID*: Afdelingens uuid i MO.
-   *Afdelingsnavn*: Afdelingens navn.
-   *Parentid*: uuid på enhedens forældreenhed.
-   *Gade*: Gadenavn
-   *Postnr*: Postnummer
-   *By*: Bynavn

Kun enheder på strukturniveau eksporteres. Dette foregår på den måde, at
hvis enheden har et enhedsniveau (*org_unit_level*) som
figurerer i nøglen *integrations.SD_Lon.import.too_deep* i
*settings.json* vil enheden blive ignoreret.

Enheder som ikke har en gyldig adresse i MO, vil få angivet en tom
streng for Gade, Postnr og By.

Rodenheden for organisationen vil have en tom streng som Parentid.

## Engagement

I dette udtræk eksporteres disse felter:

-   *BrugerId*: Brugerens uuid i MO. Nøgle til *Bruger*
    -udtrækket.
-   *AfdelingsId*: Afdelingens uuid i MO. Nøgle til
    *Organisation* -udtrækket.
-   *AktivStatus*: Sættes til 1 for aktive engagementer, 0 for
    fremtidige.
-   *StillingskodeId*: uuid til engagements titel, som gemmes som en
    klasse under facetten *engagement_job_function* i MO.
    Nøgle til stillingskode.
-   *Primær*: 1 hvis engagementet er primært, ellers 0.
-   *Engagementstype*: Angiver om stillingen er måneds eller
    timelønnet.
-   *StartdatoEngagement*: Startdato hvis engagementet endnu ikke er
    startet

Kun bestemte typer engagementer eksporteres, dette vil normalt være
timelønnede og månedslønnede. Disse genkendes via nøglen
*exporters.plan2learn.allowed_engagement_types* i
*settings.json*, som angiver en liste over uuid'er på de
engagementstyper som skal eksporeres.

Engagmenter som tidligere har været aktive, men som nu er afsluttede,
eksporteres ikke. Kendte fremtidige engagementer eksporteres med
AktivStatus 0.

## Stillingskode

I dette udtræk eksporteres disse felter:

-   *StillingskodeID*: uuid på den klasse i MO som holder
    stillingsbetegnelsne, nøgle til *Engagement*
    -udtrækket
-   *AktivStatus*: Angiver om stillingskoden anvendes. Der
    eksporteres kun akive stillingskoder, så værdien er altid 1.
-   *Stillingskode*: Læsbar tekstrepræsentation af stillingskoden (i
    modsæting til uuid'en).
-   *Stillingskode#*: I øjeblikket en Kopi af
    *StillingskodeID*.

## Leder

I dette udtræk eksporteres disse felter:

-   *BrugerId*: Brugerens uuid i MO. Nøgle til *Bruger*
    -udtrækket.
-   *AfdelingsID*: Afdelingens uuid i MO. Nøgle til
    *Organisation* -udtrækket.
-   *AktivStatus*: Kun aktive ledere eksporteres, væriden er altid
    1.
-   *Titel*: Lederens ansvarsområder.
