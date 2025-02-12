---
title: "Request For Comments: Specifikation af serviceinterface for
  LogHændelse"
---

# Request For Comments: Specifikation af serviceinterface for LogHændelse

## Introduktion

LoRas log-tjeneste er ikke en OIO-standard og er heller ikke som
Tilstand, Indsats og Aktivitet lavet på baggrund af et forslag om en
sådan. Log-tjenesten er specificeret af Magenta på bestilling fra
Naturstyrelsen. Dette dokument er den funktionelle specifikation, der lå
til grund for den nuværende implementation.

## Overordnet sammendrag

Tjenesten LogHændelse bruges til at implementere en benyttelseslog for
rammearkitekturservices som Organisation, Klassifikation, Sag, Dokument,
Tilstand, Aktivitet og Indsats - i det hele taget alle
rammearkitektur-services, som følger OIO- og MOX-protokollerne og
udsender standardiserede notifikationer om tilgang til databaserne over
AMQP.

Tjenesten kan også bruges af services uden for rammearkitekturen; den
eneste betingelse er, at de skal sende log-oplysningerne i et
standardiseret format, specifikt som AMQP-beskeder til en nærmere
angivet kø eller exhange.

Logningen foregår ved, at logservicen lytter på den AMQP-exchange eller
-kø, hvortil notifikationerne fra de tjenester, der skal logges, bliver
sendt.

Hvert objekt i tjenesten LogHændelse indeholder samtlige oplysninger,
der skal logges i forbindelse med benyttelsen af tjenesterne.

Det drejer sig først og fremmest om

- _service-ID_ (kan være tjenestens navn - er det ikke entydigt nok,
  kan det være UUID eller brugervendt nøgle for det IT-System, der
  repræsenterer servicen).
- _klasse_ - den type objekt, som hændelsen gælder.
- _tidspunkt_ for den hændelse, der logges.
- _operation_, der udføres - for rammearkitekturen søg, læs, ret, slet
  eller passivér.
- _objekttype_ - altså navnet på den type, for hvilken hændelsen
  logges.
- _objekt_, for hvilket logningen foretages. Dette kan sammen med
  objekttypen og tjenestens navn eller ID entydigt bruges til at
  identificere og fremfinde det objekt, som logningen gælder.
- _bruger_ - den bruger, der foretog den handling, der logges.
- _brugerrolle_ - den brugerrolle, som brugeren har benyttet for at få
  adgang til at udføre den pågældende handling.
- _returkode_ - svarkoden fra servicen, altså f.eks. 200, 404, 403, 500.
- _returtekst_ - fejlmeddelelse fra serveren i tilfælde af, at noget
  gik galt.
- _note_ - såfremt notefelterne på eventuelle nye registreringer eller
  virkningsperioder er udfyldt, kan disse kopieres til notefeltet på
  LogHændelsen. Det vil selvfølgelig være helt op til de services, der
  bruger LogHændelse, hvad der skal stå i dette notefelt.

## Autentificering

Log-servicen kunne i princippet genbruge SAML-tokens fra de oprindelige
hændelser og oprette loghændelserne på vegne af denne bruger.

Logning må imidlertid opfattes som et særskilt ansvarsområde, og det vil
derfor være passende, om denne funktion varetages af en bruger med en
særlig rolle, som vi kunne kalde Logningsansvarlig.

Autentificering foregår altså ved, at der for hver af de services, der
har adgang til at bruge LogHændelse, oprettes en bruger, der har rollen
Logningsansvarlig for netop denne hændelse. Når en tjeneste ønsker at
logge en hændelse, skal den danne et SAML-token for dens Logansvarlige
bruger og medsende som autentikering.

Når LogHændelse modtager log-beskeden vil den først validere, at det
indkommende token er gyldigt, at det er udstedt for IdP'en for den
service, der logges for, og at den bruger, der autentikeres, faktisk er
Logningsansvarlig.

Et interessant aspekt af denne protokol er, at LogHændelse-tjenesten ved
logning ikke autentikerer en af sine egne bruger, men en af
klienttjenestens. Dette volder dog ingen vanskeligheder og kræver ikke
en fælles brugerdatabase; det kræver kun, at den pågældende IdPs
offentlige nøgle registreres på LogHændelse-tjenesten sammen med en
identifikation af servicen.

Af hensyn til performance og fleksibilitet vil det være en stor fordel,
om brugerrollerne medtages i de SAML-tokens, der genereres, så
log-tjenesten ikke behøver at "kalde tilbage" for at verificere, at
brugeren har den rigtige rolle.

## Attributter

En LogHændelse har følgende attributter:

- service
- klasse
- tidspunkt (bemærk, dette kan være tidligere end virkning og
  registrering for log-objektet)
- operation
- objekttype
- returkode
- returtekst
- note

## Tilstande

Umiddelbart kan det antages, at en LogHændelse skabes én gang, hvorefter
den aldrig ændres. Objektet har derfor måske ikke brug for tilstande.

Omvendt kan der måske være brug for at slette hændelser, der ved en
fejltagelse er logget for f.eks. en forkert service, eller for at ændre
et notefelt, hvis der ved en fejltagelse er kommet fortrolige data med
ud.

Vi har derfor én tilstand:

- Gyldighed - en angivelse af, om LogHændelsen er blevet ændret, siden
  den blev registreret. Værdimængden er "Ikke rettet" (default) og
  "Rettet".

## Relationer

En LogHændelse har relationer til ganske få andre objekter.

Dybest set repræsenterer en LogHændelse en registrering af en _handling_
udført af en _bruger_, der har fået lov eller er blevet afvist i forhold
til en _brugerrolle_.

_Handlingen_ er én af de operationer, der er beskrevet under de
generelle egenskaber for OIO-standardernes objekter. Den implementeres
ikke som en objektreference, men som et tekstfelt, hvis værdimængde i
praksis er begrænset til en simpel enumeration af de mulige operationer.
Der foretages ingen validering af dette, eftersom det også skal være
muligt at logge hændelser for services, der ikke er en del af
OIO-systemet. Handlingen kunne med andre ord have været en reference til
Klasse, men implemtenteres i stedet som tekstfeltet _operation_.

_Brugeren_ er en reference til Bruger-objektet i Organisation.

_Brugerrollen_ er en reference til Klassifikation. I nogle tilfælde kan
brugerens adgangsrettigheder være beskrevet af roller, der er oprettet
ad hoc på IdP'en og ikke er mappet i klassifikation, og i sådanne
tilfælde kan rollen angives ved en URN på formen
"rolle:oprindelse:rollenavn". Hvis rollerne senere oprettes i
Klassifikation, skal URN'en kunne bruges til at slå rollen op dér.

LogHændelse har dermed følgende til-én-relationer:

- _objekt_ - det objekt, som logningen gælder. UUID eller URN.
- _bruger_ - den bruger, der har udført den handling, der logges. UUID
  eller URN. Reference til typen Bruger i Organisation.
- _brugerrolle_ - den rolle, som er brugt til at give brugeren adgang
  (eller ej). Reference til Klassifikation. Såfremt brugerrollerne er
  ad hoc og ikke oprettet i Klassifikation, hvilket p.t. er tilfældet
  på referencedata.dk, kan angives en URN.

## Operationer

Log-servicen vil tilbyde de samme operationer som de øvrige
LoRa-services. Det kan dog overvejes, om rettighedsstyringen skal
begrænse skriveoperationerne, så det kun er de operationer, der giver
mening for denne tjeneste, der skal tillades.
