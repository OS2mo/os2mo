---
title: SD-Læs
---

# SD-integration



## 1. Introduktion
Denne dokumentation beskriver den nye SD-integration, som synkroniserer data fra SD-Løn
til MO. Integrationen erstatter den tidligere løsning og tilbyder en mere robust og
driftssikker synkronisering af medarbejder- og organisationsdata.

Dokumentet henvender sig til slutbrugere og driftsansvarlige, som arbejder med
medarbejderdata i MO, og som har brug for at forstå, hvordan data flyder fra SD-Løn ind
i MO.

## 2. Overblik over integrationen
SD-integrationen håndterer den automatiske overførsel af organisations- og personaledata
fra SD-Løn til MO. Når en ændring foretages i SD-Løn – f.eks. en ny ansættelse, en
ændring af stillingsbetegnelse eller en organisatorisk omstrukturering – sørger
integrationen for, at ændringen automatisk afspejles i MO.

## 3. Hvad er nyt i den nye integration?
Den nye SD-integration karakteriseres ved

* Event-baseret sync i realtid
* Fuldt sync af hele tidslinjen pr. objekt
* Nemt at synkronisere et enkelt objekt
* Robust – ingen oprydningsscripts nødvendige
* Bedre tests, inkl. integrationstests mod kørende MO
* Anvender nye SD API-features

Den nye integration er designet til at være mere pålidelig, hvilket reducerer den
manuelle indsats for driftsansvarlige markant.

## 4. Dataflow: Fra SD-Løn til MO
Nedenfor beskrives, hvordan data flyder igennem systemet fra en ændring registreres i
SD-Løn, til den er synlig for slutbrugeren i MO.

1. En ændring foretages i SD-Løn (f.eks. ny ansættelse, stillingsændring, organisatorisk flytning).
2. SD-Løn sender en hændelse (event) via AMQP-beskedkøen til SD-integrationen.
3. SD-integrationen modtager hændelsen og henter det fulde XML-payload fra SD-Løns API, som indeholder alle relevante data for det pågældende objekt.
4. Integrationen parser XML-data og omdanner dem til interne Pydantic-datamodeller (tidslinjer).
5. Tidslinjerne fra SDLøn sammenlignes med de eksisterende tidslinjer i MO for at beregne de nødvendige ændringer.
6. De beregnede ændringer skrives til MO via MOs GraphQL-API.
7. Slutbrugeren kan nu se de opdaterede data i MOs brugergrænseflade.

# 5. Tidslinjer og event-processering
Et centralt koncept i den nye integration er tidslinjer. Hvert objekt (f.eks. en
organisationsenhed eller et engagement) repræsenteres som en samling af tidslinjer, hvor
hver tidslinje beskriver en bestemt egenskab over tid.

## 5.1 Egenskaber på tidslinjer
For en organisationsenhed kan tidslinjerne f.eks. være:

* `active`: Om enheden er aktiv i en given periode.
* `name`: Enhedens navn over tid.
* `unit_id`: Enhedens ID.
* `parent`: Enhedens overordnede enhed over tid.

## 5.2 Sammenligning og synkronisering
Når en hændelse modtages, bygger integrationen tidslinjer fra både SDLøn’s XML-data og
MOs nuværende data. De to sæt af tidslinjer sammenlignes interval for interval. På den
måde kan integrationen præcist beregne, hvilke perioder der skal oprettes, opdateres
eller afsluttes i MO.

Denne fremgangsmåde sikrer, at hele historikken for et objekt synkroniseres
korrekt – ikke kun den seneste ændring, men alle ændringer over tid.

## 5.3 Udløsning af events
Events kan både udløses fra SD, men også fra MO selv. Sidstnævnte (konfigurerbare)
feature sikrer, at det ikke ved en fejl er muligt at ødelægge data i MO via manuelle
ændringer. Hvis man fx en en fejl kommer til at ændre slutdatoen for en persons
engagement i MO, så vil denne handling udløse en MO-event, som trigger synkronisering
af engagementet, hvorfor dettes slutdato øjeblikkeligt ændres tilbage til den korrekte
værdi, som angivet i SD.

# 6. Engagementstyper og statuskoder
Som udgangspunkt beregnes engagementtypen i MO ud fra ansættelsesdata i SD.
Default-værdierne er “Månedlønnet, fuldtid”, “Månedslønnet, deltid” og “Timelønnet”.
Alternativt er det muligt at få importeret statuskoderne 1-1 fra SD-Løn:

| Statuskode SD | Tekst i SD | Tekst i MO |
| :---- | :---- | :---- |
| 0 | Ansat, ikke i løn | Ikke i løn |
| 1 | Ansat, i løn | I løn |
| 3 | Midlertidig ude af løn | Orlov |
| 4 | Konflikt | Statuskode 4 (konfigurerbar) |
| 7 | Emigreret eller død | Fratrådt (kan ikke ses i MOs UI) |
| 8 | Fratrådt | Fratrådt (kan ikke ses i MOs UI) |
| 9 | Pensioneret | Fratrådt (kan ikke ses i MOs UI) |

# 7. Adresser
Synkronisering af postadresser, emails og telefonnumre på enheder og personer (samt
P-numre på enheder) faciliteres af SD-integrationen. Synkroniseringen af disse objekter
er konfigurerbare, og det er muligt granuleret af styre, hvilket objekter der skal
sync’es fra SD til MO. Eksempelvis kan man vælge, at personers private emails ikke skal
sync’es, men at deres private telefonnumre skal med.

# 8. Hvad skal du som slutbruger vide?

## 8.1 Data opdateres automatisk
Alle ændringer i SD-Løn synkroniseres automatisk til MO. Du behøver ikke selv at
foretage dig noget for at sikre, at dine data er opdaterede.

## 8.2 Data er tidstro
Da integrationen er event-baseret, vil ændringer typisk være synlige i MO sekunder
efter, de er registreret i SD-Løn.

## 8.3 Historik bevares
Den nye integration synkroniserer hele tidslinjen for et objekt. Det betyder, at du i MO
kan se både nuværende, fremtidige og historiske data ("Nutid", "Fremtid" og "Fortid" i
MO’s brugergrænseflade).
