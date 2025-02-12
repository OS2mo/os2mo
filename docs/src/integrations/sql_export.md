# Actual State SQL database

## Indledning

Denne eksport laver et dags-dato udtræk af MO og afleverer det i en SQL
database.

For at opnå den nødvendige afviklingshastighed, tilgår eksporten data
direkte fra LoRa hvor det er muligt at lave bulk udtræk, baseret på den
kendte datamodel for OS2MO behandles de udtrukne data så SQL eksporten
får et udseende som svarer til det man finder i MO.

Tabellerne er for den praktiske anvendeligheds skyld ikke 100%
normaliserede, der vil således for alle klasser altid være både en
reference til primærnøglen for klassen plus en tekstrepræsentation, så
det er muligt at aflæse tabellen uden at skulle foretage et join mod
tabellen `klasser` for alle opslag.

Implementerigen er foretaget ved hjælp af værktøjet SQLAlchemy, som
sikrer at det er muligt at aflevere data til en lang række forskellige
databasesystemer, det er desuden muligt at køre hele eksporten mod en
flad SQLite fil som muliggør eksportering helt uden en kørende
databaseserver.

## Konfiguration

For at anvende eksporten er det nødvendigt at oprette et antal nøgler i
_settings.json_:

- `exporters.actual_state.manager_responsibility_class`: UUID på det
  lederansvar, som angiver at en leder kan nedarve sin lederrolle
  til enheder dybere i organisationen.
- `exporters.actual_state.type`: Typen af database, i øjeblikket
  understøttes _SQLite_, _Mysql_,
  _MS-SQL_, samt _MS-SQL-ODBC_. flere kan
  tilføjes efter behov. _MS-SQL_-driveren er på vej ud
  og er erstattet af _MS-SQL-ODBC_ i nyere
  installationer.
- `exporters.actual_state_historic.type`: Som ovenfor, men for
  historisk eksport.
- `exporters.actual_state.user`: Brugernavn for sql bruger.
- `exporters.actual_state_historic.user`: Som ovenfor, men for
  historisk eksport.
- `exporters.actual_state.password`: Password til sql bruger.
- `exporters.actual_state_historic.password`: Som ovenfor, men for
  historisk eksport.
- `exporters.actual_state.db_name`: Navn på databasen for actual
  state eksport.
- `exporters.actual_state_historic.db_name`: Navnet på databasen for
  historisk eksport.
- `exporters.actual_state.host`: Hostnavn på SQL-serveren.
- `exporters.actual_state_historic.host`: Som ovenfor, men for
  historisk eksport.

For typen _SQLite_ kan user, password og host være tomme
felter.

## Eksport af historik

MO/LoRa er en historisk database hvor de fleste objekter kan have
forskellige værdier på forskellige tidspunkt, såkaldte virkningstider.
SQL-eksporten vil som udgangspunkt eksportere de aktuelt gyldige
værdier, men det er også muligt at foretage en komplet eksport af alle
gyldigheder.

## Kommandolinjeværktøj

**En eksport kan startes fra kommandolinjen med følgende parametre:**

- `--resolve-dar`: Hvis denne parameter er sat, vil eksporten
  forsøge at slå MOs DAR uuid'er op, så adressen også eksporteres
  i klar tekst. Hvis datasættet indeholder mange forskellige
  adresser, vil det betyde en betydelig forøgelse af kørselstiden.
- `--historic`: Hvis denne parameter er sat, vil der blive
  foretaget en fuld eksport af både fortidige, nutidige og
  fremtidige rækker. Dette vil betyde, at en række beregnede
  parametre ikke vil komme med i datasættet.
- `--force-sqlite`: Denne parameter vil betyde at
  `exporters.actual_state.type` i `settings.json` vil blive
  ignoreret, og en _SQLite_-fil vil blive eksporteret.
- `--use-pickle`: Ingen opslag vil blive foretaget i LoRa,
  udtrækket vil baseres på cache-filer fra sidste gennemløb, mest
  anvendeligt til udvikling.

## Modellering

Langt hovedparten af de data som eksporteres kan betragtes som rene
rådata, der er dog nogle få undtagelser, hvor værdierne er fremkommet
algoritmisk, disse værdier beregnes kun ved dags-dato eksport, ved fuld
eksport af historiske værdier, er felterne tomme:

- `enheder.organisatorisk_sti`: Angiver den organisatoriske sti for
  en enhed beregnet ved at gå baglæns gennem enhedstræet og tilføje
  et \\-tegn mellem hver enhed. Eksempel: _Basildon Kommune\\Kunst &
  Kultur\\Musiktilbud\\Øvelokaler_.
- `enheder.fungerende_leder`: I MO er en leder modeleret som en
  organisationfunktion som sammenkæder en person med en enhed. Der
  er ikke noget krav om at alle enheder har en lederfunktion pegende
  på sig, og der vil derfor være enheder som ikke figurerer i
  tabellen `ledere`. For disse enheder er det muligt algoritmisk at
  bestemme en leder ved at gå op i træet indtil der findes en leder
  med passende lederansvar. Dette felt indeholder resultatet af
  denne algoritme.
- `adresser.værdi`: For alle adressetyper, undtaget DAR adresser, er
  dette felt taget direkte fra rådata. For DAR-adresser, er rådata
  en UUID og ikke en tekststreng, i dette tilfælde indeholder dette
  felt resultatet af et opsalg mod DAR, og den egentlige rådata
  (UUID'en) befinder sig i feltet `dar_uuid`.
- `engagementer.primærboolean`: Beregnes ved at iterere hen over
  alle engagementer for en bruger, det engagement som har det
  højeste _scope_ på sin primærklasse vil blive markeret
  som primær, alle andre vil blive markeret som ikke-primært.

## Eksporterede tabeller

Eksporten producerer disse tabeller, indholdet af de enkelte tabeller
gennemgås systematisk i det følgende afsnit.

- `facetter`
- `klasser`
- `brugere`
- `enheder`
- `adresser`
- `engagementer`
- `roller`
- `tilknytninger`
- `orlover`
- `it_systemer`
- `it_forbindelser`
- `ledere`
- `leder_ansvar`
- `KLE`

### facetter

- `uuid`: Facettens uuid, primærnøgle for tabellen.
- `bvn`: Brugervendt nøgle for facetten.

Facetter i MO har ikke nogen titel, og ikke nogen historik.

### klasser

- `uuid`: Klassens uuid, primærnøgle for tabellen.
- `bvn`: Brugervendt nøgle for klassen.
- `titel`: Klassens titel, det er denne tekst som vil fremgå af MOs
  frontend.
- `facet_uuid`: Reference til primærnøglen i tabellen `facetter`.
- `facet_bvn`: Den brugervendte nøgle som knytter sig til klassens
  facet.

Klasser regnes af MO til at have evig virkning og eksporteres derfor
altid med dags-dato værdi, også i et historisk eksport.

### brugere

- `uuid`: Brugerens uuid, primærnøgle for tabellen.
- `fornavn`: Brugerens fornavn.
- `efternavn`: Brugerens efternavn.
- `kaldenavn_fornavn`: Fornavnet på brugerens kaldenavn.
- `kaldenavn_efternavn`: Efternavnet på brugerens kaldenavn.
- `cpr`: Brugerens cpr-nummer.
- `startdato`: Startdato for denne rækkes gyldighed.
- `slutdato`: Slutdato for denne rækkes gyldighed.

### enheder

- `uuid`: Enhedens uuid, primærnøgle for tabellen.
- `navn` Enhedens navn.
- `forældreenhed_uuid`: Reference til primærnøglen for
  forælderenheden.
- `enhedstype_uuid`: Enhedstypen, reference til primærnøglen i
  tabellen
- `enhedstype_titel`: Titel på enhedstypens klasse. `klasser`.
- `enhedsniveau_uuid`: Enhedsniveau, dette felt anvendes normalt kun
  af kommuner, som anvender SD som lønsystem. Reference til
  primærnøglen i tabellen `klasser`.
- `enhedsniveau_titel`: Titel på klassen for enhedsniveau.
- `organisatorisk_sti`: Enhedens organisatoriske placering, se
  afsnit om [Modellering](#modellering).
- `leder_uuid`: Reference til primærnøglen for det lederobjet som er
  leder af enheden. Informationen er teknisk set redundant, da den
  også fremkommer ved et join til tabellen `ledere`, men angives
  også her som en bekemmelighed.
- `fungerende_leder_uuid`: Reference til primærnøglen for nærmeste
  leder af enheden. Hvis enheder har en leder, vil dette være det
  samme som _leder_. Feltet er et afledt felt og findes
  ikke i rådata, se afsnit om [Modellering](#modellering).
- `startdato`: Startdato for denne rækkes gyldighed.
- `slutdato`: Slutdato for denne rækkes gyldighed.

### adresser

Adresser er i MO organisationfunktioner med funktionsnavnet `Adresse`.

- `uuid`: Adressens (org-funk'ens) uuid, primærnøgle for tabellen
- `bruger_uuid`: Reference til primærnøglen i tabellen `brugere`.
  Hvis adressen er på en enhed, vil feltet være blankt.
- `enhed_uuid`: Reference til primærnøglen i tabellen `enheder`.
  Hvis adressen er på en bruger, vil feltet være blankt.
- `værdi`: Selve adressen, hvis adressen er en DAR-adresse, vil
  dette felt indeholde en tekstrepræsentation af adressen.
- `dar_uuid`: DAR-uuid'en som liger bag opslaget som fremgår af
  `værdi_tekst`. Blankt hvis ikke adressen er en DAR-adresse.
- `adressetype_uuid`: Adressetypen, reference til primærnøglen i
  tabellen `klasser`.
- `adressetype_scope`: Adressens overordnede type (omfang),
  eksempelvis Telefon eller P-nummer.
- `adressetype_titel`: Titlen på adressetypens klasse.
- `synlighed_uuid`: Synlighedstype, reference til primærnøglen i
  tabellen `klasser`.
- `synlighed_titel`: Titlen på synlighedstypens klasse.
- `startdato`: Startdato for denne rækkes gyldighed.
- `slutdato`: Slutdato for denne rækkes gyldighed.

### engagementer

Engagementer er i MO organisationfunktioner med funktionsnavnet
`Engagement`.

- `uuid`: Engagementets (org-funk'ens) uuid, primærnøgle for
  tabellen.
- `bruger_uuid`: Reference til primærnøglen i tabellen `brugere`.
- `enhed_uuid`: Reference til primærnøglen i tabellen `enheder`.
- `bvn`: Engagementets brugervendte nøgle. Dette vil i de fleste
  tilfælde være ansættelsesnummeret i lønsystemet.
- `arbejdstidsfraktion`: Angiver den registrerede
  arbejdstidsfraktion for engagementet.
- `engagementstype_uuid`: Engagementstypen, reference til
  primærnøglen i tabellen `klasser`.
- `engagementstype_titel`: Titlen på engagementstypeklassen.
- `primærtype_uuid`: Engagementets primærtype, reference til
  primærnøglen i tabellen `klasser`.
- `primærtype_titel`: Titlen på primærtypetypeklassen.
- `stillingsbetegnelse_uuid`: Engagementets stillingsbetegnelse,
  reference til primærnøglen i tabellen `klasser`.
- `job_function_titel`: Titlen på klassen for stillingsbetegnelse.
- `primær_boolean`: Boolean som angiver om engagementet er brugerens
  primære engagement, se afsnit om beregnede felter
- `udvidelse_1`: Første af 10 fritekstfelter på MOs engagementer
- `udvidelse_10`: Sidste af 10 fritekstfelter på MOs engagementer
- `startdato`: Startdato for denne rækkes gyldighed.
- `slutdato`: Slutdato for denne rækkes gyldighed.

### roller

Roller er i MO organisationfunktioner med funktionsnavnet `Rolle`.

- `uuid`: Rollens (org-funk'ens) uuid, primærnøgle for tabellen.
- `bruger_uuid`: Reference til primærnøglen i tabellen `brugere`.
- `enhed_uuid`: Reference til primærnøglen i tabellen `enheder`.
- `rolletype_uuid`: Rolletypen, reference til primærnøglen i
  tabellen `klasser`.
- `rolletype_titel`: Titlen på klassen for rolletypen.
- `startdato`: Startdato for denne rækkes gyldighed.
- `slutdato`: Slutdato for denne rækkes gyldighed.

### tilknytninger

Tilknytninger er i MO organisationfunktioner med funktionsnavnet
`Tilknytning`.

- `uuid`: Tilknytningens (org-funk'ens) uuid, primærnøgle for
  tabellen.
- `bvn`: Tilknytningens brugervendte nøgle.
- `bruger_uuid`: Reference til primærnøglen i tabellen `brugere`.
- `` enhed_uuid`: Reference til primærnøglen i tabellen ``enheder``.
- `tilknytningstype_uuid`: Tilknytningstypen, reference til
  primærnøglen i tabellen `klasser`.
- `tilknytningstype_text`: Titlen på klassen for tilknytningstypen.
- `startdato`: Startdato for denne rækkes gyldighed.
- `slutdato`: Slutdato for denne rækkes gyldighed.

### orlover

Orlover er i MO organisationfunktioner med funktionsnavnet `Orlov`.

- `uuid`: Orlovens (org-funk'ens) uuid, primærnøgle for tabellen.
- `bvn`: Brugervendt nøgle for orloven.
- `bruger_uuid`: Reference til primærnøglen i tabellen `brugere`.
- `orlovstype_text`: Titlen på klasse for orlovstypen.
- `orlovstype_uuid`: Orlovstypen, reference til primærnøglen i
  tabellen `klasser`.
- `startdato`: Startdato for denne rækkes gyldighed.
- `slutdato`: Slutdato for denne rækkes gyldighed.

### it_systemer

- `uuid`: IT-systemets uuid, primærnøgle for tabellen.
- `navn`: IT-systemets navn.

IT-systmer regnes af MO til at have evig virkning og eksporteres derfor
altid med dags-dato værdi, også i et historisk eksport.

### it_forbindelser

IT-forbindelser er i MO organisationfunktioner med funktionsnavnet
`IT-system`.

IT-forbindeler dækker over en sammenkædningen mellem et IT-system og
enten en enhed eller en bruger. Hvis forbindelsen er til en bruger, vil
sammenkædningen indeholde brugerens brugernavn i det pågældende system.
Hvis forbindelsen er til en enhed, skal den tolkes i betydningen, at
dette IT-system er i anvendelse i den pågældende enhed, i dette tilfælde
vil der normalt ikke være brugernavn på forbindelsen.

- `uuid`: IT-forbindelsens (org-funk'ens) uuid, primærnøgle for
  tabellen.
- `it_system_uuid`: Reference til primærnøglen i tabellen
  `it_systemer`
- `bruger_uuid`: Reference til primærnøglen i tabellen `brugere`.
  Hvis it-forbindelsen er på en enhed, vil feltet være blankt.
- `enhed_uuid`: Reference til primærnøglen i tabellen `enheder`.
- `brugernavn`: Brugerens brugernavn i IT-systemet. Normalt blank
  for forbindelser til enheder.
- `startdato`: Startdato for denne rækkes gyldighed.
- `slutdato`: Slutdato for denne rækkes gyldighed.

### ledere

- `uuid`: Lederrollens (org-funk'ens) uuid, primærnøgle for
  tabellen.
- `bruger_uuid`: Reference til primærnøglen i tabellen `brugere`.
- `enhed_uuid`: Reference til primærnøglen i tabellen `enheder`.
- `ledertype_titel`: Titlen på klassen for ledertypen.
- `ledertype_uuid`: Klassen for ledertypen, reference til
  primærnøglen i tabellen `klasser`.
- `niveautype_titel`: Titlen på klassen for lederniveau.
- `niveautype_uuid`: Klassen for lederniveau, reference til
  primærnøglen i tabellen `klasser`.
- `startdato`: Startdato for denne rækkes gyldighed.
- `slutdato`: Slutdato for denne rækkes gyldighed.

### leder_ansvar

Lederansvar er i MO ikke et selvstændigt objekt, men er modelleret som
en liste af klasser som tilknyttes en lederrolle.

- `id`: Arbitrært løbenummer, denne tabel har ikke har nogen
  naturlig primærnøgle.
- `leder_uuid`: Reference til primærnøglen i tabellen `ledere`.
- `lederansvar_uuid`: Klassen for lederansvar, reference til
  primærnøglen i tabellen `klasser`.
- `lederansvar_titel`: Titlen på klassen for lederansvar.
- `startdato`: Startdato for denne rækkes gyldighed.
- `slutdato`: Slutdato for denne rækkes gyldighed.

### KLE

KLE opmærkning er i MO ikke selvstændige objekter, men er modelleret som
en binding imellem to klasser, nemlig KLE-Aspekt (f.eks. udførende) og
KLE-numre.

- `id`: Arbitrært løbenummer, primærnøgle for tabellen.
- `uuid`: KLE-bindingens uuid.
- `enhed_uuid`: Reference til primærnøglen i tabellen `enheder`.
- `kle_aspekt_uuid`: Klassen for KLE-aspekt, reference til
  primærnøglen i tabellen `klasser`.
- `kle_aspekt_titel`: Titlen på KLE-aspektets klasse.
- `kle_nummer_uuid`: Klassen for KLE-nummer, reference til
  primærnøglen i tabellen `klasser`.
- `kle_nummer_titel`: Titlen på KLE-nummerets klasse.
- `startdato`: Startdato for denne rækkes gyldighed.
- `slutdato`: Slutdato for denne rækkes gyldighed.

## Actual state til cron-jobs

Jobs kører generelt hurtigere, hvis de anvender en actual state
database, end hvis de anvender rest-kald imod os2mo.

Derfor findes muligheden for at slå et job til, som genererer en actual
state database i SQLite-format til brug for cron-jobs.

For at anvende denne eksport er det nødvendigt at oprette enkelt nøgle i
`settings.json`:

- `lc-for-jobs.actual_db_name`: Navnet på filen (eksporten tilsætter
  selv '.db' til navnet)

Databasen vil kun være skrivbar imens den bliver genereret.
