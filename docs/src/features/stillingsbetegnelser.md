---
title: Håndtering af følsomme stillingsbetegnelser i MO og aftagersystemer
---

# Håndtering af følsomme stillingsbetegnelser i MO og aftagersystemer

Formålet er sikring af at MO kan importere stillingsbetegnelser fra Active Directory uden at videresende følsomme stillingsbetegnelser til offentlige aftagersystemer.

## Stillingsbetegnelser og følsomhed

Det er typisk overenskomstbaserede stillingsbetegnelser lønsystemerne SD-Løn og OPUS, der bliver importeret ind i MO.

Dog vedligeholder de fleste kommuner mere sigende stillingsbetegnelser I Active Directory (AD) - stillingsbetegnelser, som beskriver de ansattes opgaver indholdsmæssigt bedre (fx Specialkonsulent kontra Havneingeniør).

Nogle af disse stillingsbetegnelser kan dog indeholde følsomme oplysninger, om fx flexjob, og de må derfor ikke udstilles i aftagersystemer. Der kan opsættes regler for, hvilke stillingsbetegnelser der indeholder følsomme oplysninger.

## Import af stillingsbetegnelser fra AD til MO

Stillingsbetegnelserne fra AD'et vil blive importeret til MOs database ud fra de regler, der er specificerede, men stillingsbetegnelserne vil ikke blive udstillet i brugergrænsefladen; det er udelukkende lønsystemernes stillingsbetegnelser, der bliver udstillet i MO.

## Eksport af stillingsbetegnelser til aftagersystemer

Integrationerne til de offentlige aftagersystemerne konfigureres således at de følsomme stillingsbetegnelser fra lønsystemet ikke bliver eksporteret - i stedet vil stillingsbetegnelsen fra AD blive eksporteret. Såfremt der ingen stillingsbetegnelse er i AD, bruges lønsystemets stillingsbetegnelse, men kun såfremt at denne ikke er følsom.

På den måde findes alle oplysninger i MO, men i de aftagersystemerne er de følsomme oplysninger fjernet.

Her er en liste over de systemer, der overholder reglen for stillingsbetegnelser:

- [plan2learn](https://rammearkitektur.docs.magenta.dk/os2mo/integrations/plan2learn.html)
- [organisationsdiagrammet](https://rammearkitektur.docs.magenta.dk/os2mo/features/org-chart.html)
- [FK Organisation](https://rammearkitektur.docs.magenta.dk/os2mo/integrations/os2sync.html)
- [SQL-databaser](https://rammearkitektur.docs.magenta.dk/os2mo/integrations/sql_export.html).

## Automatisk (eventbaseret) vedligeholdelse af stillingsbetegnelser

Når en stillingsbetegnelse opdateres eller oprettes i AD'et, vil den blive sendt til MO med det samme.
