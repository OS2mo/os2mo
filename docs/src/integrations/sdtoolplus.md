---
title: SDTOOL+
---

## Beskrivelse

SDTool+ udvider SD-integrationen med muligheden for automatisk at ajourføre
organisationstræet i OS2mo, så det svarer til det aktuelle organisationstræ i
SD Løn. Da SDs API kun indeholder muligheden for at hente seneste ændringer på
personer og disses engagementer, er opretholdelsen af organisationsstrukturen
et mere omstændeligt problem, men SDTool+ håndterer dette ved at anvende benytte
de muligheder SDs API tilbyder for at hente organisationsstrukturinformationer
fra forskellige kilder og stykke resultaterne sammen til et fuldt
organisationstræ.

Det er også muligt at konfigurere SDTool+ til at synkronisere
postadresser og P-numre fra organisationsenhederne i SD til OS2mo.

### Synkronisering af organisationstræet

SDTool+ køres via et automatisk job (fx en gang dagligt), og vil ved hver
kørsel gøre følgende:

1. Udlæse alle organisationsenheder fra SD og bygge det tilhørende
   organisationstræ.
2. Udlæse alle organisationsenheder i OS2mo og bygge det tilhørende
   organisationstræ.
3. Sammenligne SD-organisationstræet og OS2mo-organisationstræet og generere en
   liste af operationer, som skal udføres på OS2mo-træet. Operationerne kan
   være af typen "Tilføj", som tilføjer nye enheder fra SD, eller
   "Opdatér", som flytter enheder til en ny forældrenhed og/eller omdøber
   enheder.
4. Sikre, at engagementer flyttes til de korrekte enheder ved
   opdateringsoperationer, såfremt dette er nødvendigt (den såkaldte
   "apply-NY-logic").
5. (Valgfri feature) Udsende emails til relevante medarbejdere såfremt SDTool+
   forsøger at udføre en "ulovlig" operation. Ved en ulovlig operation forstås
   flytning af en enhed, som stadig indeholder aktive eller fremtidigt aktive
   engagementer, til enheden "Udgåede afdelinger" (navnene på disse enheder kan
   variere).

#### Opmærksomhedspunkter

- De fleste anvendere af SDTool+ har fået konfigureret et filter som det, der
  er nævnt afsnittet [Konfiguration](#konfiguration) nedenfor,
  hvilket kan resultere i følgende opførsel i SDTool+: Lad
  os forestille os, at der er opsat i filter, som frasorterer operationer, der
  skal udføres på enheder, hvis navn begynder med "%", da man ikke ønsker, at
  sådanne enheder skal figurere i OS2mo. Antag dernæst, at
  enheden "Sundhed" i SD omdøbes til "% Sundhed". Denne ændring vil ikke slå
  igennem i OS2mo (selv om man sandsynlig ville ønske dette), da operationen
  filtreres pga., at det nye navn begynder med "%". Det er dog mulig at
  konfigurere SDTool+ til _alligevel_ at omdøbe enheden, så den i OS2mo kommer
  til at hedde "% Sundhed", idet omdøbningsoperationer kan tillades på trods af
  det konfigurerede filter for enheder, som begynder med "%". Resultats bliver
  således, at
  1. Enhedens navn i OS2mo stemmer overens med det, som enheden (nu) hedder i
     SD.
  2. Man har en uønsket "%"-enhed stående i OS2mo, hvilket ikke er en fejl i
     SDTool+, men snarere en konsekvens af, at enheden i SD er ændret fra en
     almindelig enhed til en "%"-enhed. Problemet kan dog let løses ved blot
     manuelt at afslutte "% Sundhed" i OS2mo (hvilket sandsynligvis er det,
     man alligevel ønsker).

#### SDTool+'s brug af SDs API (for teknikere)

SDTool+ anvender i forbindelse med punkt 1) i ovenstående beskrivelse følgende
endepunkter fra SDs API:

1. Det grundlæggende organisatonstræ bygges via SDs endpoint
   `GetOrganization20111201`, som udstiller alle enheder i træet, der har et
   afdelingsniveau som blad (leaf node) i
   [træstrukturen](<https://en.wikipedia.org/wiki/Tree_(data_structure)>).
2. Dernæst tilføjes de resterende enheder (NY-niveauer, som ikke har
   et afdelingsniveau under sig længere ned i træet) ved at kigge på
   forskellen mellem ovenstående respons fra `GetOrganization20111201` og
   responset fra `GetDepartment20111201` (som indeholder _alle_ enheder,
   men ikke informationer om deres forældreneheder) og responsene fra en
   række kald til `GetDepartmentParent20190701` returnerer forlældreenheden
   for en given enhed.

### Synkronisering af adresser

SDTool+'s postadresse og P-nummer synkronisering er en valgfri feature i
applikationen. Hvis featuren er aktiveret, kan man (fx dagligt) køre et job,
som for organisationsenheder:

1. Udlæser alle P-numre og postadresser fra SD.
2. Udlæser alle P-numre og postadresser fra OS2mo.
3. Sammenligner ovenstående informationer for hver enhed og opdaterer enhederne
   i OS2mo de steder, hvor ændringer er nødvendige.

Følgende skal bemærkes mht. synkroniseringen af organisationsenhedernes
postadresser:

I OS2mo er adresser gemt som UUID'er (eksempelvis som værdien
de228324-97df-4893-b140-f863da6c0cf3), som er unikke værdier, der stammer fra
[Dansk Adresseregister](https://danmarksadresser.dk/) (DAR) - dvs. adresserne i
OS2mo er "vasket", og de er gemt så præcist, som det kan lade sig gøre. Når den
fysiske adresse skal vises i OS2mo's frontend, så sender OS2mo adresse-UUID'et
til DAR og får den fysiske adresse tilbage (fx "Paradisæblevej 13, 8000 Aarhus C
"), og det er denne adresse, der ses i frontenden.

Når man fra SD henter data om en enhed og dennes postadresse, så kommer den ikke
tilbage som et DAR UUID og ofte heller ikke som den tilsvarende fysiske adresse,
der står i DAR. Et tænkt eksempel: lad os forestille os, at man i SD
henter enheden "Administration", som har adressen "Paradisæblevej 13 - 15,
8000 Aarhus C". Men denne adresse kan ikke (nødvendigvis) findes i DAR, da den
i DAR er delt ud på tre forskellige adresser (og dermed tre unikke UUID'er)
nemlig adresserne "Paradisæblevej 13, 8000 Aarhus C", "Paradisæblevej 14,
8000 Aarhus C" og "Paradisæblevej 15, 8000 Aarhus C". Sådanne forskelle gør, at
SDTool+ har svært ved at sammenligne adresserne i SD og MO, hvorfor adresserne
på enhederne i SD skal opdateres til at være gyldige DAR-adresser, inden
featuren til synkronisering af postadresser aktivers i SDTool+.

## Konfiguration

Applikationen konfigureres via miljøvariable i Docker containeren for
SDTool+. Der er en del konfigurationsmuligheder (mest relevant for teknikere),
som er beskrevet via kommentarer i koden i applikationens
[konfigurationsmodul](https://github.com/magenta-aps/os2mo-sdtool-plus/blob/master/sdtoolplus/config.py).

Bemærk specielt mulighederne for

1. at få frafiltreret enheder fra SD, som man ikke
   ønsker synkroniseret til OS2mo - fx enheder, som begynder med "Ø\_"
   eller "%" eller lignende.
2. at konfigurere SDTool+ til kun at sammenligne
   et givet undertræ i OS2mo med organisationstræet i SD.

## Kildekode

Kildekoden til SDTool+ kan finde på GitHub:
[https://github.com/magenta-aps/os2mo-sdtool-plus](https://github.com/magenta-aps/os2mo-sdtool-plus)
