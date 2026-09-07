---
title: Organisationsdiagram
---

# Organisationsdiagram til MO

## Formål

Formålet med organisationsdiagrammet er gøre MOs data tilgængelige for alle i organisationen.

Organisationsdiagrammet kan bruges såvel som opslagsværk som overblik over linjeorganisationen og MED/TR-organisationen.

Organisationsdiagrammet læser data fra MO, dvs. hvis data ændres i MO, afspejles det *med det samme* i organisationsdigrammet.

### Præsentation af data
#### Visning af organisationer
Det er muligt at udstille flere organisationer via forskellige adresser (URL'er). Således kan man fx vælge at udstille sin administrative organisation med ansatte og ledere i ét organisationsdiagram og sin MED/TR-organisation med tillidsrepræsentantskabet i et andet.

#### Visning af enheder i en træstruktur
Enheder vises i en træstruktur, så man tydeligt kan se enhedernes hierarkiske tilhørsforhold.

![image](../graphics/hierarchy.png)

Træstrukturen kan konfigureres til at folde sig ud enten lodret eller vandret.

#### Udfoldning af træstruktur
Der er toggle-knapper for hver enhed, som viser eller skjuler overenheder og underenheder til denne.

#### Visning af detaljer for enhed
Ved klik på en enhed fremkommer en liste af personer, som er er ansatte eller/og tilknyttet enheden, deres leder(e) samt kontaktinformation på enheden.

![image](../graphics/unitdetails.png)

#### Visning af detaljer for person
Ved klik på en person (fra enhedens personliste) fremkommer detaljerede oplysninger om personen - herunder kontaktinformation.

![image](../graphics/employeedetails.png)

#### Visning af tilknytninger og engagementer i samme diagram

Det er muligt at vise såvel engagementer som tilknytninger i ét og samme diagram, fx så både ansatte og MED/TR-repræsentanter fremgår.

I konfigurationen vælges det, om personer skal vises på baggrund af deres engagementer, deres tilknytninger eller begge dele.

#### Kaldenavn
Det er muligt at udstille Kaldenavn i organisationsdiagrammet i stedet for CPR-navn, såfremt Kaldenavn er angivet i MO. Det betyder også, at det er muligt at søge på Kaldenavn. Kaldenavne benyttes typisk, når CPR-navnet ikke ønskes udstillet.

#### Ledere og engagementer
Som standard vises både lederrollen og lederens engagement(er) i diagrammet. Ønsker man kun at vise lederrollen, kan dette vælges i konfigurationen

### Navigation og deling

#### Navigation mellem enheder
Der navigeres mellem enheder ved at folde den visuelle træstruktur ud og klikke eller ‘tabbe’ sig frem til enheder.

#### Deling af trævisning via URL
Som udgangspunkt vises træstrukturen med den rodenhed, der er konfigureret, og dennes underenheder vil være foldet ud. Når man klikker rundt i trævisningen, opdateres URL'en med den enhed, der aktuelt er i fokus.

Man kan dele visningen ved at kopiere websidens URL og sende den til en anden part. Modtageren kan indsætte URL'en i sin egen browser og få åbnet en trævisning, hvor samme enhed er i fokus, og dens underenheder allerede er foldet ud.

Når man åbner en enhed for at vise dens personliste og individuelle personer, opdaterer dette også URL'en. Dette bruges i søgefunktionen til at linke til visning af bestemte personer.

### Søgefunktion
Søgefunktionen vises i toppen af skærmen.

![image](../graphics/searchfunctionalityorgchart.png)

Ved klik på luppen kommer man til søgesiden. Når man indtaster i søgefeltet, får man et søgeresultat med personer eller enheder, der passer til det søgte.

![image](../graphics/searchperson.png)

Vælger man en person eller enhed fra søgeresultatet, forsvinder søgeresultatet for at gøre plads til visning af den specifikke enhed eller person i træstrukturen.

![image](../graphics/searchmagnus.png)

Der kan søges på:

1. Enhedsnavn
2. Personers navn (herunder Kaldenavn, hvis dette er konfigureret)

## Datavisning
### For visning af enheder

For hver organisationsenhed vises:

1. Enhedens navn
2. Antal ansatte eller tilknyttede (for hhv. linje- og MED/TR-organisation)
3. Antal underenheder

Antallet af ansatte/tilknyttede og antallet af underenheder kan hver især slås fra i konfigurationen.

### For visning af enhedsdetaljer
Når man klikker på en enhed, vises følgende informationer om den:

1. Enhedens navn
2. Enhedens kontaktinformation
3. Enhedens leder samt stillingsbetegnelse
4. Enhedens medlemmer (personliste) med navn og stillingsbetegnelse

### For visning af person

1. Navn (fulde navn eller kaldenavn, afhængigt af konfiguration)
2. Ansættelsestype
3. Stillingsbetegnelse
4. Kontaktinformation, fx email, telefon, arbejdsadresse og lokation.

## Filtrering og tilpasning af data

Nedenstående muligheder sættes i konfigurationen af den enkelte udstilling. De påvirker udelukkende, hvad organisationsdiagrammet viser - data i MO ændres ikke.

### Udgangspunkt for diagrammet
Hver udstilling har en konfigureret rodenhed, som træstrukturen foldes ud fra. Enheder uden for rodenhedens del af organisationen vises ikke.

### Filtrering på organisationshierarki
Udstillingen kan afgrænses til de enheder, der er markeret med et eller flere bestemte [organisationshierarkier](https://rammearkitektur.docs.magenta.dk/os2mo/integrations/organisationsopmaerkning.html), fx 'Linjeorganisation' eller 'MED-organisation'. Det er denne mekanisme, der typisk bruges til at udstille den administrative organisation og MED-organisationen i hver sit diagram.

### Fravalg af enheder
Enheder kan skjules i træet på tre måder:

1. Ved at angive enhedernes UUID'er
2. Ved at angive tekststrenge, så enheder, hvis navn indeholder strengen, skjules
3. Ved at angive enhedsniveauer (org_unit_level), så alle enheder på de pågældende niveauer skjules

### Sortering af enheder
Enheder sorteres som udgangspunkt alfabetisk. Udvalgte enheder kan angives ved UUID, så de i stedet altid placeres nederst under deres overenhed.

### Fravalg af enhedens e-mail
Enhedens e-mailadresse kan fjernes fra enhedsdetaljerne, fx hvis en fællespostkasse ikke ønskes udstillet offentligt.

### Fravalg af adressetyper
Udvalgte adressetyper kan skjules ved at angive deres brugervendte nøgler (user keys). Det gælder både for enheder og personer og bruges, når fx en bestemt telefon- eller adressetype ikke skal udstilles.

### Fravalg af engagementstyper
Engagementer af bestemte engagementstyper kan fjernes fra personlisterne, fx så robotkonti eller eksterne konti ikke vises i diagrammet.

### Valg mellem to stillingsbetegnelser
Mange medarbejdere har i praksis to stillingsbetegnelser: en overenskomstmæssig (fx "specialkonsulent") og en titel, der beskriver det faktiske arbejde (fx "projektleder for byudvikling"). Diagrammet kan konfigureres til at vise én af de to.

## Brugeroplevelse
### Tilgængelighed
Løsningen lever op til krav om tilgængelighed og kan derfor udstilles på både intranet og hjemmeside.

### Look and feel
Løsningen kan integrere lokale design, fra farvekoder til logo. Konkret kan der konfigureres et selvstændigt stylesheet (farver, typografi mv.), et logo, et favicon samt en titel.

### Responsivt layout
Løsningen kan anvendes på både små og store skærme.

### Understøttelse af browsere
Løsningen understøtter gængse, opdaterede browsere.

## Øvrig funktionalitet
### Print styles
Organisationsdiagrammet kan printes (ctrl-p). Antal ark afhænger af organisationens størrelse.

### mailto-link i e-mail-adresser
Når der vises persondetaljer, kan email vises i et mailto-link, så det er muligt at sende mails direkte (såfremt man har en mailklient installeret på sit system). Man skal være opmærksom på spamfare ved at oplyse om email på offentligt tilgængelige websites.
​
### CORS-settings på servere
Løsningen skal køre på en server, hvor CORS-setup tillader, at der hentes data via MO API'et.
