---
title: Lederhåndtering
---

# Lederhåndtering i MO

Nedenfor findes de automatikker og funktionaliteter, der er udviklet til håndtering af ledere i MO.

## Lederroller og engagementer

En lederrolle i MO er som udgangspunkt koblet til det **engagement** (den ansættelse), der bemyndiger personen til at bestride lederrollen. Ingen bestrider en lederrolle blot i kraft af, hvem de er som person – man er leder, fordi man er blevet ansat til det.

Koblingen betyder bl.a., at:

- Det altid er entydigt, hvilken ansættelse en person er leder i kraft af – også når personen har flere ansættelser.
- Integrationer og eksportværktøjer (fx SafetyNet, organisationsdiagrammet og rapporterne) kan udlede den korrekte leder, når en leder har flere engagementer.
- Loggen gør opmærksom på ledere, hvor koblingen mangler.

## Betjening i brugergrænsefladen

Ved oprettelse og redigering af ledere – både fra medarbejder- og organisationssiden – angives det engagement, der bemyndiger personen til lederrollen:

![image](../graphics/lederhaandtering/lederevaelgengagement.png)

Det er også muligt at markere "Tilknyt ikke et engagement", hvis man ønsker at knytte lederrollen til (CPR-)personen i stedet for til et engagement. Bemærk, at denne mulighed forventes udfaset på et senere tidspunkt.

Ledertabellerne har en Engagementskolonne, så man let kan se, hvilken ansættelse en leder er leder i kraft af, om nogen:

![image](../graphics/lederhaandtering/ledereudstilling.png)

## Primær leder og eksplicit leder

Som udgangspunkt er en medarbejders leder den leder, der er placeret i medarbejderens enhed. Nogle gange er der brug for at være mere præcis: Hvis enheden har flere ledere, kan man markere én af dem som **primær leder**. Og hvis en medarbejder skal referere til én og kun én leder, kan man angive en **eksplicit leder** direkte på medarbejderens engagement.

### Primær leder

#### Markér en leder som primær

1. Gå til enheden, vælg fanen *Ledere*, og klik på *Opret leder* – eller klik på blyanten ud for en eksisterende leder for at redigere.
2. Udfyld *Startdato*.
3. Vælg *Primær* i feltet *Primær*.
4. Klik på *Opret leder* / *Redigér leder*.

![image](../graphics/lederhaandtering/primaerleder_opret.png)

Om en leder er primær, kan ses i kolonnen *Primær* i fanen *Ledere* – både på enheden og på medarbejderen.

![image](../graphics/lederhaandtering/primaerleder_tabel.png)

#### Reglen: én primær leder pr. enhed

- En enhed kan kun have én primær leder ad gangen.
- Den samme person må gerne være primær leder i flere forskellige enheder.
- En vakant lederrolle kan også være primær.

Hvis en anden leder allerede er primær i enheden i en periode, der overlapper den, du har valgt, vises meddelelsen "Enheden har allerede en primær leder i perioden" under feltet sammen med navn og periode på den eksisterende primære leder. Formularen kan ikke gemmes, før konflikten er løst.

#### Skift primær leder

Fordi der kun må være én primær leder ad gangen, skal den gamle markering fjernes, før den nye sættes:

1. Redigér den nuværende primære leder med *Startdato* = den dato, skiftet skal ske, og ryd feltet *Primær* (klik på krydset).
2. Redigér (eller opret) den nye leder med samme *Startdato*, og vælg *Primær*.

Den gamle leder er herefter primær frem til dagen før skiftet, og den nye fra skiftedatoen.

### Eksplicit leder

Som udgangspunkt får et engagement sin eller sine ledere fra den enhed, engagementet er placeret i (og – afhængigt af opsætningen – fra en overliggende enhed, hvis enheden ikke selv har en leder). Med eksplicit leder kan man for det enkelte engagement angive præcis hvilken lederrolle, medarbejderen refererer til. Lederrollen kan ligge hvor som helst i organisationen.

#### Angiv en eksplicit leder

Feltet findes, når man opretter eller redigerer et engagement – fra medarbejdersiden, fra enhedens fane *Engagementer* og i flowet for oprettelse af nye medarbejdere.

1. Søg lederen frem i feltet *Eksplicit leder*. Søgningen finder kun personer, der findes på engagementets startdato.
2. Vælg den rigtige rolle i feltet *Lederrolle*. Listen viser de lederroller, personen har på engagementets startdato, med enhed og ledertype – så det er tydeligt, hvilken rolle der vælges, hvis personen er leder flere steder. Vælger man en anden person, nulstilles feltet *Lederrolle*.
3. Gem engagementet.

![image](../graphics/lederhaandtering/eksplicitleder_engagement.png)

Bemærk, at engagementet knyttes til **lederrollen** og ikke til personen. Bliver lederrollen vakant, vises den som vakant på engagementet, og besættes samme lederrolle af en ny person, følger engagementet automatisk med. Man kan dog ikke vælge en vakant lederrolle som ny eksplicit leder, da rollen findes via den person, der besætter den.

#### Fjern en eksplicit leder

Redigér engagementet, og ryd felterne *Eksplicit leder* og *Lederrolle*. Engagementet bruger så igen lederen af sin enhed.

#### Sådan vises det

I kolonnen *Leder* under fanen *Engagementer* vises den eksplicitte leder alene, efterfulgt af et lille ikon (en person med et flueben). Holder man musen over ikonet, står der "Eksplicit leder". Er den eksplicitte lederrolle vakant, vises "Vakant" efterfulgt af lederrollens enhed i parentes, med et link til enhedens fane *Ledere*. Engagementer uden eksplicit leder viser som hidtil enhedens leder(e).

![image](../graphics/lederhaandtering/eksplicitleder_tabel.png)

#### Når den eksplicitte lederrolle ophører

MO afslutter ikke koblingen automatisk, når den valgte lederrolle ophører. Så længe rollen ikke er aktiv, viser kolonnen *Leder* enhedens leder(e) i stedet. Redigerer man engagementet med en startdato, hvor rollen ikke er aktiv, vises en advarsel om, at engagementets eksplicitte lederrolle ikke er aktiv på startdatoen. Koblingen bevares, medmindre man fjerner den eller vælger en ny lederrolle.

### Opsætning og teknik

Feltet *Primær* på ledere slås til af Magenta efter aftale. Eksplicit leder er tilgængelig i engagementsformularerne uden særlig opsætning.

I GraphQL-API'et findes primær-markeringen i feltet `primary` på ledere (med tilsvarende `primary`-filter), og den eksplicitte leder i feltet `explicit_manager` på engagementer (med tilsvarende filter). Bemærk, at `managers`-feltet på engagementer ikke tager højde for `explicit_manager` – integrationer, der skal respektere eksplicit leder, skal læse feltet særskilt.

## Automatikker

Det er muligt at oprette ledere manuelt i MO, og når det er gjort, kan en række arbejdsgange automatiseres.

*Bemærk, at det udelukkende er SD-kommuner, der har behov for følgende arbejdsgange, idet LOS/OPUS-kommuner selv
opmærker ledere i lønsystemet.*

1. **Automatisk flytning af en leders engagement**: Når en leder opmærkes manuelt i MO, flyttes lederens engagement automatisk til den enhed, lederen er oprettet i. Se afsnittet om [Opret Leder i MO](#opret-leder-i-mo).
2. **Automatisk afslutning af ledere i MO**: Når en leders sidste engagement ophører, bliver vedkommendes lederrolle automatisk afsluttet eller sat vakant. Se afsnittet om [Automatisk afslutning af ledere i MO](#automatisk-afslutning-af-ledere-i-mo).
3. **Opret leder i SD**: Lederen oprettes i en leder-enhed i SD-Løn, og MO indplacerer automatisk lederen korrekt ved indlæsningen. Se afsnittet om [Indplacer leder i leder-enhed i SD-Løn](#opret-leder-i-sd).

## Opret leder i MO (automatisk løft af lederens engagement)

Det er muligt at aktivere en komponent i MO, som sikrer, at en leders engagement altid er placeret i samme enhed som den enhed, hvor lederrollen findes ("elevate managers"). Mekanismen er hændelsesbaseret: Den udføres med det samme, når lederobjekter ændres i MO.

Mekanismen illustreres af eksemplet på nedenstående figur:

![image](../graphics/lederhaandtering/engagementsflytning.png)

1. En medarbejder har et engagement, som er placeret i enheden "IT-support".
2. En MO-bruger opmærker manuelt medarbejderen til at være leder i enheden "IT og Digitalisering".
3. Komponenten flytter herefter automatisk medarbejderens engagement fra "IT-support" til "IT og Digitalisering".

Funktionen virker også, når lederen har flere engagementer: Det er engagementet, der er koblet til lederrollen (jf. afsnittet Lederroller og engagementer ovenfor), der flyttes.

Derudover gælder (kan tilpasses efter behov):

- Øvrige eksisterende ledere på enheden afsluttes automatisk.

## Automatisk afslutning af ledere i MO

Lederroller afsluttes automatisk, når det ansættelsesgrundlag, de hviler på, ophører:

- Er lederrollen koblet til et engagement, afsluttes - lederrollen (eller sættes som vakant), når dette engagement ophører. Får engagementet tildelt en slutdato i fremtiden, afsluttes lederrollen pr. samme dato.
- Er lederrollen ikke koblet til et engagement (knyttet til personen), afsluttes rollen, når personens *sidste* aktive engagement ophører, i tilfælde af, at vedkommende har flere engagementer.

> **Bemærk:** Integrationen kan konfigureres således at lederroller ikke afsluttes, men i stedet sættes vakante pr. den dato, hvor lederens engagement ophører. Ved vakance påsættes den korrekte slutdato/vakantdato automatisk.

Automatikken kører på MOs eventsystem og lytter direkte på lederhændelser, hvilket betyder, at den reagerer med det samme. Den anvender fuld tidslinjelogik, så også ugyldige lederperioder (fx perioder, hvor lederen ikke havde noget aktivt engagement) genskrives korrekt.

For teknikere: Der findes et /trigger/all-endpoint, så samtlige ledere kan synkroniseres/genberegnes på én gang, fx efter en konfigurationsændring.

Hermed:

+ automatiseres ophør / vakance af lederrollen
+ reduceres mængden af manuelt vedligehold
+ minimeres risiko for fejl i lederdata
+ effektiviseres tidsforbruget

## Opret leder i SD  (Leder-kasser)

Når en leder er indplaceret i en til formålet oprettet leder-enhed i SD-Løn, bliver denne enhed og lederen indlæst i MO.

Automatitkken i MO gør derefter følgende:

1. Flytter lederen fra leder-enheden til den enhed, lederen skal være leder af.
2. Tilføjer evt. manglende ledertype-oplysninger om lederen (om der fx er tale om en Direktør eller en    Kommunaldirektør).
3. Afslutter ledere, der ikke længere har noget engagement i den enhed, de er ledere i.

### Detaljeret beskrivelse

Dette afsnit beskriver hvordan logikken opfører sig, når den eksekveres:

1. Det tjekkes om alle aktuelle ledere fortsat har engagementer i de organisationsenheder, de er indplaceret i. Hvis det ikke er tilfældet, sættes dags dato som slutdato på lederen.
2. For alle organisationsenheder, hvis navn ender med `_leder` og som *ikke* er præfikset med `Ø_`:

![_leder org-unit](../graphics/lederhaandtering/_leder.png)

- Hentes alle ansatte som har en tilknytning til `_leder`-enheden:

![Tilknytninger](../graphics/lederhaandtering/tilknytning.png)

- Tjekkes, at hver ansatte har et aktivt engagement i overenheden. Hvis mere end én medarbejder har en tilknytning til `_leder`-enheden, vælges den ansættelse, der har den seneste startdato: Denne person bliver sat som leder i overenheden.

- Mappes hvert enhedsniveau til et leder-level:

  ![Manager level](../graphics/lederhaandtering/manager_level.png)

- Gøres lederen *også* til leder af overenhedens overenhed, hvis overenheden har `_led-adm`i sit navn.

  ![led-adm](../graphics/lederhaandtering/_led-adm.png)

  I eksemplet ovenfor, hvor lederen bliver leder af to enheder, identificeres leder-level fra den øverste enhed,
  altså fra Borgmesterens Afdeling.

Når en leder er blevet valgt ud fra de ovenstående kriterier, vil alle tilknytninger i `_leder`-enheden termineres, så kun én tilknytning resterer.

### Teknik

Integrationen konfigureres via miljøvariable i integrationens container (bl.a. rodenhed, standard-ledertype, standard-lederansvar samt mapning fra enhedsniveauer til lederniveauer). Konfigurationen foretages af Magenta i forbindelse med idriftsættelse.
