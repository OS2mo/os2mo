---
title: KLE
---

# KLE i MO

## Formål

KLE står for [Kommunernes Landsforenings Emnesystematik](https://www.kl.dk/okonomi-og-administration/digitalisering-og-teknologi/arbejdsgange-forretningsviden-og-informationshaandtering/kl-emnesystematik-kle/) og er en taksonomi, der bruges til at opmærke enkeltsager med kommunale opgaver.

I MO bruges KLE-numre til at opmærke organisationsenheder og bliver sendt til FK Organisation mhp. adgangsstyring.

Det er således muligt at vedligeholde KLE-numre i OS2mo samt eksportere dem til andre systemer.

1. **[Importere KLE-numre i MO vha. regneark](#importere-kle-numre-i-mo-vha-regneark)**
2. **[Vedligeholde KLE-numre i MO](#vedligeholde-kle-numre-i-mo)**
3. **[Eksportere KLE-numre fra MO](#eksportere-kle-numre-fra-mo)**

## Importere KLE-numre i MO vha. regneark

Man kan sagtens oprette KLE-numre i selve MO, men det er oftest nemmere at gøre det i et regnark først og foretage en engangsindlæsning af det i MO.

Ønsker man at opmærke med KLE-numre direkte i MO, se [Vedligeholde KLE-numre i MO](##vedligeholde-KLE-numre-i-MO)

### Udtræk af organisationen

Der laves et udtræk af den administrative organisation fra MO, og det sendes det til jer. Det foregår i [dette regneark](../static/kle.xlsx).

Regnearket indeholder også alle KLE-numre fra [KLE-Online](https://www.kle-online.dk/).

De to datasæt findes i regnearket i under fanerne:

- Org
- KLE

Under de næste tre faner findes de tre såkaldte KLE-aspekter, som I skal opmærke jeres organisation med:

**Ansvarlig**

I det første ark, 'Ansvarlig', er kolonnerne A-D befolket med 'Niveau', 'EmneNr', 'EmneTitel' og 'EnhedNavn'.

Idéen er, at I vælger en enhed i kolonne D og matcher den med ét KLE-nummer fra kolonne C.

Der er her tale om en en-til-en relation, fordi kun en enhed skal kunne være ansvarlig for ét KLE-nummer.

Hvis det er en hjælp, kan I herinde også filtrere på niveauer (1, 2 og 3).

**Indsigt & Udførende**

I de to næste ark, 'Indsigt' og 'Udførende', er kolonnerne A-B befolket med 'EnhedNavn' og 'KLE'.

Idéen er, at I vælger enheder i kolonne A - gerne den samme flere gange, såfremt den skal have indsigt i eller være udførende for flere KLE-numre.

Der er her tale om en mange-til-mange relation.

Når I har udfyldt det, returnerer I det, så vi kan indlæse det i MO. Når det er gjort, er jeres enheder KLE-opmærket.

---

Pas på! Vi skal kunne indlæse arket programmatisk, når det er udfyldt og returneret, så hvis I er kommet til at taste noget ekstra ind eller slettet noget, vil indlæsningen fejle.

Der er tale om en engangsopgave, så når regnearket er fyldt ud og læst ind, behøver I ikke det mere og kan blot vedligeholde opmærkningen i OS2mo:

## Vedligeholde KLE-numre i MO

Se [her](https://rammearkitektur.docs.magenta.dk/os2mo/home/manual.html#fanebladet-kle-opmrkninger).

## Eksportere KLE-numre fra MO

KLE-numre kan pt. eksporteres til:

- [FK Organisation](https://rammearkitektur.docs.magenta.dk/os2mo/data-import-export/exporters/os2sync.html)
- [Rollekataloget](https://rammearkitektur.docs.magenta.dk/os2mo/data-import-export/exporters/os2rollekatalog.html)
