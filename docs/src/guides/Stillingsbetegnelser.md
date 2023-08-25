---
title: Håndtering af følsomme stillingsbetegnelser i MO og aftagersystemer
---

# Formål

Formålet er sikring af at MO kan importere stillingsbetegnelser fra Active Directory uden ikke videresende følsomme stillingsbetegnelser til offentlige aftagersystemer.

## Stillingsbetegnelser og følsomhed

Overenskomstbaserede stillingsbetegnelser bliver importeret i MO fra lønsystemerne, typisk SD-Løn og OPUS.

De fleste kommuner vedligeholder dog stillingsbetegnelser som beskriver de ansattes stillinger indholdsmæssigt bedre end lønsystemernes i Active Directory (fx Specialkonsulent kontra Havneingeniør).

Nogle af disse kan indeholde følsomme oplysninger, fx flexjob, og de må ikke udstilles i aftagersystemer. Der kan opsættes regler for, hvilke stillingsbetegnelser der indeholder følsomme oplsyninger.

## Import af stillingsbetegnelser fra AD til MO

Stillingsbetegnelserne fra Active Directory vil blive importeret til MOs database ud fra de regler, der er specificerede, men stillingsbetegnelserne vil ikke blive udstillet i brugergrænsefladen; det er lønsystemernes stillingsbetegnelser, der bliver udstillet i MO.

## Automatisk (eventbaseret) vedligeholdelse af stillingsbetegnelser

Når en stillingsbetegnelse opdateres eller oprettes i AD'et, vil den blive sendt til MO med det samme.

## Eksport af stillingsbetegnelser til aftagersystemer

Integrationerne til de offentlige aftagersystemerne konfigureres således at de følsomme stillingsbetegnelser fra AD'et ikke bliver eksporteret - i stedet vil lønsystemets stillingsbetegnelse blive eksporteret.

På den måde findes alle oplysninger i MO, men i de aftagersystemerne er de følsomme oplysninger fjernet.

Her er en liste over de systemer, der overholder reglen for stillingsbetegnelser:

- [plan2learn](https://rammearkitektur.docs.magenta.dk/os2mo/data-import-export/exporters/plan2learn.html),
- [organisationsdiagrammet](https://rammearkitektur.docs.magenta.dk/os2mo/data-import-export/exporters/org-chart.html),
- [FK Organisation](https://rammearkitektur.docs.magenta.dk/os2mo/data-import-export/exporters/os2sync.html)
- [SQL-databaser](https://rammearkitektur.docs.magenta.dk/os2mo/data-import-export/exporters/sql_export.html).
