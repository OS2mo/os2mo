---
title: XFlow
---

# OS2mo-integration til XFlow

Denne integration faciliterer overførslen af oplysninger om medarbejdere fra OS2mo
til fagsystemet XFlow. Formålet er, at de relevante medarbejdere automatisk er
til stede i XFlow, så de kan indgå i XFlows arbejdsgange, uden at oplysningerne
skal vedligeholdes manuelt to steder. Integrationen genererer jævnligt (fx dagligt)
et antal rapporter i OS2mo, som kan anvendes til at vedligeholde de relevante
medarbejderinformationer i XFlow.

## Hvilke oplysninger overføres

For hver medarbejder, overføres følgende oplysninger:

- Fornavn
- Efternavn
- E-mail
- CPR-nummer
- Organisation
- Nærmeste leders CPR-nummer

## Hvilke medarbejdere kommer med

Integrationen medtager ikke alle medarbejdere i OS2mo. Der bliver filtreret på
to måder:

- **Stillingsbetegnelse (jobfunktion).** Kun medarbejdere med bestemte
  stillingsbetegnelser kommer med.
- **Organisatorisk placering.** Kun medarbejdere, der hører til under en af de
  godkendte rodenheder (de øverste enheder, der er valgt til formålet), kommer
  med. Medarbejdere uden for disse dele af organisationen bliver ikke overført.

En medarbejder kommer altså kun med, hvis vedkommende både har en relevant
stillingsbetegnelse og er placeret under en godkendt rodenhed i OS2mo.

## Hvordan findes den nærmeste leder

For hver medarbejder finder integrationen den nærmeste relevante leder. Søgningen
starter i medarbejderens egen enhed og bevæger sig opad i organisationen, indtil
en passende leder findes.

En leder regnes kun for relevant, hvis vedkommende er fast tilknyttet (har et
månedslønnet engagement), har den rigtige ledertype, og har
det rigtige ansvar (fx personaleansvar). Hvis medarbejderen selv er leder i sin
egen enhed, springes denne over, og der ledes videre opad efter en leder på et højere
niveau. Hvis der ikke findes en relevant leder, overføres medarbejderen uden en nærmeste
leder.

## Rapporter til XFlow

Oplysningerne samles i en rapport (en datafil) pr. rodenhed. Hver rapport
indeholder de medarbejdere, der hører til under den pågældende rodenhed. Når
rapporten er dannet, gøres den tilgængelig i OS2mo, hvorfra den kan anvendes af
XFlow.

## Sammenlægning af flere rodenheder i én rapport

I nogle tilfælde ønsker man, at medarbejderne fra flere rodenheder skal samles i
den samme rapport. Integrationen kan konfigureres til at håndtere dette scenarie.

Det er muligt at angive (via en konfiguration), at en eller flere rodenheder skal lægges
sammen med en anden rodenheds rapport. Når det er sat op, vil medarbejderne fra de
sammenlagte
enheder optræde i rapporten for den valgte rodenhed. Den enkelte medarbejders
egen organisation bevares i oplysningerne, så det fortsat fremgår, hvilken enhed
medarbejderen reelt hører til. Flere rodenheder kan lægges sammen i den samme
rapport.

## Opsætning

Integrationen styres af nogle indstillinger, som konfigureres ved idriftsættelsen:

- Hvilke stillingsbetegnelser der skal medtages.
- Hvilke rodenheder der er godkendte.
- Eventuelt hvilke rodenheder der skal lægges sammen i en anden rodenheds
  rapport.
- Eventuelt hvilke lederstillinger der skal anses som ledere under en bestemt
  rodenhed, hvis dette skal afvige fra standardopsætningen.

Indstillingerne afgør, hvilke medarbejdere der kommer med, hvordan de fordeles
på rapporter, og hvem der findes som nærmeste leder.
