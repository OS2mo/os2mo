---
title: Access Log
---

# Access Log i MO

MO logger både **skrivninger** (hvem har ændret hvad hvornår) og **læsninger** (hvem har læst hvad hvornår).

**Skrivninger** dokumenteres af MOs bitemporale **auditlog**, som både kan tilgås i brugergrænsefladen og via GraphQL-API'et. Se [Audit log i MO](https://rammearkitektur.docs.magenta.dk/os2mo/features/audit-log.html).

**Læsninger** dokumenteres af access-loggen, som beskrives på denne side. Access-loggen kan konsulteres via GraphQL; på sigt er det planen, at den også skal kunne tilgås i brugergrænsefladen.

Samlet set er det muligt på struktureret vis at:

* Se hvilke brugere der har læst eller skrevet data
* Se hvornår data er blevet læst eller skrevet
* Se hvilke data der er blevet læst eller skrevet
* Se hvilke datatyper der er blevet læst eller skrevet

## Skrivninger

Skrivningsloggen tager udgangspunkt i OS2mo's bitemporalitet.

Når et objekt oprettes, ændres eller nedlægges i OS2mo, sker det på databaselaget ved at der tilføjes nye rækker, der beskriver den indkomne ændring.
Disse nye rækker indeholder tidspunktet for hvornår ændringen er foretaget, hvem der har foretaget ændringen, samt en reference til hvordan de nye data ser ud.

Dette betyder altså, at det er muligt at rejse tilbage i tiden og se hvordan de historiske data for et objekt så ud på et tidspunkt i fortiden.

### API

GraphQL-interfacet udstiller bitemporaliteten fra OS2mos database via **registrations**.

Man kan tilgå registreringerne ad to veje: enten via topniveau-feltet **registrations**, hvor man angiver den relevante objekttype og dermed kan hente registreringer på tværs af alle objekter af den type, eller via topniveau-feltet for den pågældende objekttype (fx **classes**) og derfra navigere ned til registreringerne for hvert enkelt objekt.

Det er muligt at få en liste af ændringer med:

- Hvem der har foretaget ændringen
- Hvilken datatype der er forandret
- Hvornår ændringen trådte i kraft, og til hvornår den var aktuel
- UUID'et på den entitet, som er forandret

Man kan endvidere filtrere registreringerne på disse parametre og dermed besvare spørgsmål som:

- Hvilke ændringer har en given bruger eller integration foretaget i data i et givet interval?
- Hvem har ændret entiteten med et givet UUID?
- Hvilke ændringer er der sket i hele OS2mo siden i går?

Denne funktionalitet udgør det underliggende API for [auditloggen i brugergrænsefladen](https://rammearkitektur.docs.magenta.dk/os2mo/features/audit-log.html), så brugere og integrationer tilgår de samme historiske data.

## Læsninger

Når der foretages en læsning i OS2mo, tilføjes nye rækker, som beskriver den indkomne læse-operation. Disse læse-operationers rækker indsættes i samme transaktion som læsningerne selv, således at begge sker atomart (så vidt det er muligt).

Læse-rækkerne indeholder tidspunktet for operationen, ID'et for entiteten, som har foretaget læsningen, samt hvilke(n) datatype(r) der er læst og hvordan.

### API

Der findes et GraphQL top-level endepunkt **accesslog**, som gør det muligt at slå op i alle læse-operationsrækkerne i databasen fra ét centralt sted.

Man kan dermed få en liste af læsninger med:

- Hvem der har foretaget læsningen
- Hvilken datatype der er læst
- Hvornår læsningen blev udført
- UUID på den entitet(er), som er blevet læst

Man kan endvidere filtrere læseloggen på disse parametre og dermed besvare spørgsmål som:

- Hvilke læsninger har en given bruger eller integration foretaget i et givet interval?
- Hvem har læst entiteten med et givet UUID?
- Hvilke læsninger er der sket i hele OS2mo siden i går?

