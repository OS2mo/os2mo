---
title: Indsigt
---

# Få indsigt i de data, der findes i MOs mave

Insights er et modul, der giver muligheden for selv at sammensætte data fra MO og udskrive dem i en csv-fil, der kan åbnes i et regnearksformat (Calc LibreOffice; Excel; Google Sheets).

Formålene med modulet er mange og afhænger af, hvilke data der sammenstilles.

Et eksempel er generering af et udtræk bestående af enheder, lederfunktioner og engagementer, så man kan se, hvem der er chef for hvem og hvor.

## Brugergrænsefladen

Når man klikker på Indsigt i venstremenuen:

![image](../graphics/insights/ventremenu.png)

 bliver man præsenteret for dette billede:

![image](../graphics/insights/insightsforside.png)

Man skriver den enhed, man vil have data på, i søgefeltet:

![image](../graphics/insights/soegning.png)

Når en organisationsenhed er fremsøgt, kan man ved slideren vælge, om de underliggende enheder skal inkluderes i forespørgslen eller ej:

![image](../graphics/insights/slider.png)

Herefter vælges hvilke andre data, man er interesseret i.

Det sker ved valg af "Emne":

![image](../graphics/insights/insightsemne.png)

Herefter kan der tilføjes eller fjernes data under "Felter" fra det Emne, der er valgt:

![image](../graphics/insights/insightsfelter.png)

Hvis man ønsker, at csv-filen skal indeholde flere Emner, trykkes der på "+"-knappen:

![image](../graphics/insights/insightsplus.png)

hvorpå det bliver muligt at tilføje flere data. Ønsker man at fjerne et emne, trykkes der på "-"-knappen:

![image](../graphics/insights/insightsminus.png)

Herefter trykkes "Søg", hvorpå genereringen af filen igangsættes. Hvor lang tid det tager at generere filen, afhænger af, hvor mange data der er valgt. MO beregner automatisk, hvor lang tid der er tilbage af en forespørgsel:

![image](../graphics/insights/beregning.png)

Bemærk, at hvis man klikker bort fra Indsigt, afbrydes forespørgslen. Hvis du vil arbejde videre i MO, mens du venter, kan du åbne MO i en anden browser.

Når "Download som csv"-knappen aktiveres (bliver blå), kan der trykkes på den, og csv-filen bliver hentet ned på din computer:

![image](../graphics/insights/insightsdownload.png)

Kald din fil, hvad du vil. Hvis feltet efterlades tomt, bliver den navngivet "insights":

![image](../graphics/insights/insightsfilnavn.png)


En eksempelfil med oplysninger om engagementer i én enhed kan se sådan ud:

![image](../graphics/insights/insightseksempelcsv.png)

Hvis man ønsker helt at fjerne data fra søgningen, trykkes "Ryd":

![image](../graphics/insights/insightssoegogryd.png)
