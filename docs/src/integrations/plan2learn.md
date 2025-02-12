# plan2learn

## Indledning

Denne eksport script bygger datafiler som via sftp kan sendes til
plan2learn.

Koden består af to dele _plan2learn.py_ som foretager
eksporteringen fra MO til 5 csv-filer, samt _ship_files.py_,
som via ftpes afleverer filerne til Play2Learn. Forbindelsesoplysninger
på ftp-serveren angives i _settings.json_ via tre nøgler:

- _exporters.plan2learn.host_
- _exporters.plan2learn.user_
- _exporters.plan2learn.password_

Værktøjet har mulighed for at anvende to forskellige backends til at
hente data: de kan hentes fra MO, eller direkte fra LoRa via
LoRa-cache-mekanisme som også anvendes i andre eksportmoduler.
LoRa-cache udgaven er langt den hurtigste og MO backenden er
hovedsageligt bibeholdt for at kunne foretage en sammenligning mellem de
to backends med henblik på fejlfinding.

## Implementeringsstrategi

Der udarbejdes i alt 5 csv udtræk:

- _bruger.csv_: Udtræk af alle nuværende og kendte fremtidigt
  aktive brugere i kommunen.
- _organisation.csv_: Udtræk af alle organisationsenheder og deres
  relation til hinanden.
- _engagement.csv_: Udtræk over alle nuværende og kendte
  fremtidige engagementer.
- _stillingskode.csv_: Udtræk over alle aktive
  stillingsbetegnelser.
- _leder.csv_: Udtræk over alle ledere i kommunen.

## Brugerudtrækket

I dette udtræk eksporteres disse felter:

- _BrugerId_: Brugerens uuid i MO
- _CPR_: Brugerens cpr-nummer
- _Navn_: Brugerens fulde navn, ikke opdelt i fornavn og efteranvn
- _E-mail_: Hvis brugeren har en email i MO, angives den her.
- _Mobil_: Hvis brugeren har en mobiltelefon i MO, angives den
  her.
- _Stilling_: Stillingsbetegnelse for brugerens primærengagement.
  Hvis dette engagement har en stillingsbetegnelse skrevet i feltet
  extension_2 anvendes dette, og ellers anvendes
  stillingsbetegnelsen fra engagementet.

E-mail og mobiltelefon genkenes via bestemte klasse under adressetype,
disse klasse er for nuværende hårdkodet direkte i python filen, men vil
på sigt blive flyttet til _settings.json_.

Kun personer med ansættelsestype Timeløn eller Månedsløn inkluderes i
udtrækket. Disse typer genkendes via en liste med de to uuid'er på
typerne, for nuværende er listen hårdkoden direkte i python filen, men
vil på sigt blive flyttet til _settings.json_.

## Organisation

I dette udtræk eksporteres disse felter:

- _AfdelingsID_: Afdelingens uuid i MO.
- _Afdelingsnavn_: Afdelingens navn.
- _Parentid_: uuid på enhedens forældreenhed.
- _Gade_: Gadenavn
- _Postnr_: Postnummer
- _By_: Bynavn

Kun enheder på strukturniveau eksporteres. Dette foregår på den måde, at
hvis enheden har et enhedsniveau (_org_unit_level_) som
figurerer i nøglen _integrations.SD_Lon.import.too_deep_ i
_settings.json_ vil enheden blive ignoreret.

Enheder som ikke har en gyldig adresse i MO, vil få angivet en tom
streng for Gade, Postnr og By.

Rodenheden for organisationen vil have en tom streng som Parentid.

## Engagement

I dette udtræk eksporteres disse felter:

- _BrugerId_: Brugerens uuid i MO. Nøgle til _Bruger_
  -udtrækket.
- _AfdelingsId_: Afdelingens uuid i MO. Nøgle til
  _Organisation_ -udtrækket.
- _AktivStatus_: Sættes til 1 for aktive engagementer, 0 for
  fremtidige.
- _StillingskodeId_: uuid til engagements titel, som gemmes som en
  klasse under facetten _engagement_job_function_ i MO.
  Nøgle til stillingskode.
- _Primær_: 1 hvis engagementet er primært, ellers 0.
- _Engagementstype_: Angiver om stillingen er måneds eller
  timelønnet.
- _StartdatoEngagement_: Startdato hvis engagementet endnu ikke er
  startet

Kun bestemte typer engagementer eksporteres, dette vil normalt være
timelønnede og månedslønnede. Disse genkendes via nøglen
_exporters.plan2learn.allowed_engagement_types_ i
_settings.json_, som angiver en liste over uuid'er på de
engagementstyper som skal eksporeres.

Engagmenter som tidligere har været aktive, men som nu er afsluttede,
eksporteres ikke. Kendte fremtidige engagementer eksporteres med
AktivStatus 0.

## Stillingskode

I dette udtræk eksporteres disse felter:

- _StillingskodeID_: uuid på den klasse i MO som holder
  stillingsbetegnelsne, nøgle til _Engagement_
  -udtrækket
- _AktivStatus_: Angiver om stillingskoden anvendes. Der
  eksporteres kun akive stillingskoder, så værdien er altid 1.
- _Stillingskode_: Læsbar tekstrepræsentation af stillingskoden (i
  modsæting til uuid'en).
- _Stillingskode#_: I øjeblikket en Kopi af
  _StillingskodeID_.

## Leder

I dette udtræk eksporteres disse felter:

- _BrugerId_: Brugerens uuid i MO. Nøgle til _Bruger_
  -udtrækket.
- _AfdelingsID_: Afdelingens uuid i MO. Nøgle til
  _Organisation_ -udtrækket.
- _AktivStatus_: Kun aktive ledere eksporteres, væriden er altid
  1.
- _Titel_: Lederens ansvarsområder.
