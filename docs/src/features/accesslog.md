---
title: Access Log
---

# Access Log

Access-loggen kan konsulteres via GraphQL, men på sigt er det planen, at den også skal kunne tilgås i brugergrænsefladen.

Det er muligt på struktureret vis at:

- Se hvilke brugere der har læst eller skrevet data
- Se hvornår data er blevet læst eller skrevet
- Se hvilke data der er blevet læst eller skrevet
- Se hvilke data-typer der er blevet læst eller skrevet

## Skrivninger

Skrivningsloggen tager udgangspunkt i OS2mo's bitemporalitet.

Når et objekt oprettes, ændres eller nedlægges i OS2mo, sker det på databaselaget ved at der tilføjes nye rækker, der beskriver den indkomne ændring.
Disse nye rækker indeholder tidspunktet for hvornår ændringen er foretaget, hvem der har foretaget ændringen, samt en reference til hvordan de nye data ser ud.

Dette betyder altså, at det er muligt at rejse tilbage i tiden og se hvordan de historiske data for et objekt så ud på et tidspunkt i fortiden.

### API

GraphQL-interfacet udstiller bitemporaliteten fra OS2mo's database.

Det er muligt at få en liste af ændringer med:

- Hvem der har foretaget ændringen
- Hvilken datatype der er forandret
- Hvornår ændringen trådte i kraft og til hvornår den var aktuel
- UUID'et på den entitet som er forandret

Man kan endvidere filtrere registreringerne på disse parametre.

Det er muligt at lave forespørgsler såsom:

- Hvilke ændringer har en given bruger eller integration foretaget i data i et givet interval?
- Hvem har ændret entiteten med et givet UUID?
- Hvilke ændringer er der sket i hele OS2mo siden i går?

## Læsninger

Når der foretages en læsning i OS2mo, tilføjes nye rækker som beskriver den indkomne læse-operation. Disse læse-operationers rækker indsættes i samme transaktion som læsningerne selv, således at begge sker atomart (så vidt det er muligt).

Læse-rækkerne indeholder tidspunktet for operationen, ID'et for entiteten, som har foretaget læsningen, samt hvilke(n) datatype(r) der er læst og hvordan.

### API

Der findes et GraphQL top-level endepunkt accesslog, som gør det muligt at slå op i alle læse-operationsrækkerne i databasen fra et centralt sted.

Man kan dermed få en liste af læsninger med:

- Hvem der har foretaget læsningen
- Hvilken datatype der er læst
- Hvornår læsningen blev udført
- UUID på den entitet(er) som er blevet læst

Potentielt også disse (udelades i første version):

- Præcis hvilke felter på en given entitet der er tilgået
- SQL querien der blev udført og dens præcise resultat

Man kan endvidere filtrere læseloggen på disse parametre.

Det skal altså muligt at lave forespørgsler såsom:

- Hvilke læsningen har en given bruger eller integration foretaget i et givent interval?
- Hvem har læst entiteten med et givent UUID?
- Hvilke læsninger er der sket i hele OS2mo siden igår?
