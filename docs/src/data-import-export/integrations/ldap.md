---
title: Integration til import og eksport til og fra Active Directory
---

## Indledning

Integrationen er designet til, at synkronisere data til og fra AD. Data kan videresendes fra AD til hvilken som helst
ønsket ekstern komponent, såsom SD og MO, og data kan også videresendes til AD fra hvilken som helst ønsket ekstern
komponent, såsom SD og MO.
Integrationen er bygget således at vi, ved hjælp af AMQP (Advanced Message Query Protocol) beskeder, lytter på ændringer
ske i OS2mo, til hvilken som helst af organisationens medarbejdere. OS2mo er i stand til, at tale med og til AD, SD, og
en lang række andre ønskede integrationer, og kan derfor opfange ændringer ske til medarbejdere, IT-konti, engagementer,
addresser, ledere, tilknytninger og meget mere. Vi rydder derefter op i medarbejderens data, i de attributter og felter
der måtte være ændret på, og sender data videre i en nydelig format, der sikrer ensrettethed, og sørger for at alle,
uanset ønsket komponent, er synkroniseret nøjagtig sådan, at deres data, attributter, felter og andet relevant, følger
en rød tråd, og er gennemgående på tværs af alle integrationer. Dette er med til bl.a. at:

- validere data
- ensrette organisationen
- promovere data hygiejne
- synkronisering af data
- ophøje organisationens data kvalitet
- medarbejdere, konti og brugere er gennemgående
- forfremme workflow
- overskueliggøre organisationen med medarbejderen for øjet

## Konfigurerbar

Integrationen er utrolig fleksibel, og kan konfigureres til, at imødekomme jeres behov og ønsker for synkronisering
mellem AD, og enhver anden ekstern integrationen I skulle ønske med hjælp af OS2mo.

På nuværende tidspunkt oprettes en bruger i AD med et brugernavn og email. Disse kan videreføres til og fra OS2mo, og
til og fra en række andre integrationer.
