---
title: Administrationsmodulet
---

# Administrationsmodulet

Adminstrationsmodulet er delt i to:

- **IT-systemer**. Man kan oprette, ændre og nedlægge *IT-systemer og -roller* i MO, hvilket gør, at man også kan oprette *IT-brugere* i MO: "Som administrator ønsker jeg at oprette en medarbejder som bruger i system X og tildele hende en specifik rolle i det system (fx Admin)".

- **Klassifikationer**. Man kan oprette, ændre og nedlægge *klasser* i MO, hvilket betyder, at man fx kan oprette *Stillingsbetegnelser* i MO: "Som administrator ønsker jeg at oprette stillingsbetegnelsen 'Ekstern konsulent', så jeg kan tildele den til medarbejdere".

De to moduler gennemgås nedenfor og kan tilgås i MO via venstremenuens punkt, **Administration**:

![image](../graphics/administrationsmodulet/adminmenu.png)

## IT-systemer

Formålet med dette modul er at tillade administrator at vedligeholde IT-systemer og -roller. Dette er en forudsætning for at kunne tildele IT-adgange i MO.

### Brugergrænsefladen

Når man er inde i IT-systemer i MO, præsenteres man for dette billede:

![image](../graphics/administrationsmodulet/itsystemerforside.png)

#### Oprettelse af IT-systemer & -roller

Oprettelsen af IT-systemer og -roller foretages i to skridt:

- først IT-systemet
- derpå de tilknyttede IT-roller

Der vælges "Opret IT-system" til højre i ovenstående billede, hvorpå denne formular kommer frem:

![image](../graphics/administrationsmodulet/opretitsystem.png)

Her angives datoer, navn og brugervendt nøgle, og oprettelsen sker ved tryk på knappen "Opret IT-system".

Når det er gjort, klikkes "Administrér roller":

![image](../graphics/administrationsmodulet/administrerroller.png)

Hvorpå man kan oprette og tilknytte it-roller til det IT-system, man lige har lavet:

![image](../graphics/administrationsmodulet/opretitrolle.png)

Nu er IT-systemer og dets IT-roller klar til at blive anvendt i MO, så man kan oprette IT-brugere:

![image](../graphics/administrationsmodulet/opretitbrugermedrolle.png)

#### Ændring og sletning af IT-system og -rolle

Ved bruge af hhv. blyant- og slette-ikonet til højre for et IT-system, kan man ændre og afslutte det:

![image](../graphics/administrationsmodulet/changedeleteitsystem.png)

### Datostyring af IT-systemer og -roller

Som det fremgår af ovenstående, er det muligt at datostyre sine IT-systemer og -roller, så man fx kan oprette dem med fremtidig virkning.

## Klassifikationsmodulet

Formålet med dette modul er at tillade administrator at vedligeholde *Klasser*.

### Definition

**Facetter & Klasser**

Det, der normalt går under navnet *metadata*, kaldes *klasser* i [OIO-standarden](https://arkitektur.digst.dk/specifikationer/organisation/oio-specifikation-af-model-organisation), og derfor benyttes den samme term i MO.

En *klasse* beskriver et objekt i MO (en person, en ansættelse, en organisationsenhed, en ledertype, en orlovstype, etc.) og hører altid hierarkisk under en såkaldt *facet*.

Eksempel 1:

- **Orlovstype** (facet)
    - Barselsorlov (klasse)
    - Forældreorlov (klasse)
    - Sygeorlov (klasse)

Eksempel 2:

- **Ledertype** (facet)
    - Beredskabschef (klasse)
    - Centerchef (klasse)
    - Direktør (klasse)
    - Institutionsleder (klasse)
    - Områdeleder (klasse)
    - Sekretariatschef (klasse)

### Brugergrænsefladen

Når man er inde i Klassifikationsmodulet i MO, præsenteres man for dette billede:

![image](../graphics/administrationsmodulet/klassifikationerforside.png)

#### Oprettelse af klasser

Der vælges "Opret klasse" til højre i ovenstående billede, hvorpå denne formular kommer frem:

![image](../graphics/administrationsmodulet/klassifikationeropretklasse.png)

Herefter vælges, hvilken facet klassen skal høre under, et datointerval angives, og klassen navngives. Denne navngivning skal duplikeres i feltet "Brugervendt nøgle (bvn) *", og der kan trykkes på knappen "Opret klasse":

![image](../graphics/administrationsmodulet/klassifikationerudfyldogopret.png)

Når det er gjort, dukker den nye klasse, 'Mekaniker', op to steder:

I listen af klasser i Klassifikationsmodulet, så en administrator kan vedligeholde den:

![image](../graphics/administrationsmodulet/oprettetklasse.png)

Og i dropdowns inde i MO, så en MO-forvalter kan benytte den til at hæfte en stillingsbetegnelse på en ansat:

![image](../graphics/administrationsmodulet/oprettetklasseidropdown.png)

Bemærk, at der ved oprettelse af **Adressetyper** ligeledes skal angives et *scope*, så validering af input bliver muligt. Det kan fx være, at man vil oprette muligheden for at registrere privattelefon i MO, hvorfor *scope* 'PHONE' skal vælges:

![image](../graphics/administrationsmodulet/adminaddressscope.png)

#### Ændring af klasser

Den facet, man ønsker at ændre klasser til, vælges:

![image](../graphics/administrationsmodulet/klassifikationervalgaffacet.png)

Man klikker på blyant-ikonet til højre for den klasse, man ønsker at ændre, og foretager den ønskede ændring:

![image](../graphics/administrationsmodulet/klassifikationerresultat.png)

#### Sletning af klasser

Den korrekte facet vælges, og man trykker på krydset ud for den klasse, der skal slettes:

![image](../graphics/administrationsmodulet/sletklasse.png)

Herefter angives klassens slutdato:

![image](../graphics/administrationsmodulet/afslutklasse.png)

### Datostyring af klasser

Klasser kan datostyres på samme måde som fx engagementer, enheder og tilknytninger, så man fx kan oprette dem med fremtidig virkning.

Datostyring af klasser giver større fleksibilitet, højere datakvalitet og mere præcise data i MO, men det betyder også, at administratorer skal være opmærksomme på gyldighedsintervallerne: En klasses gyldighedsperiode skal dække gyldighedsperioden på de objekter, den beskriver.

**Eksempel**: En stillingsbetegnelse, 'Projektleder', er gyldig fra 01-01-2027 til 31-12-2027. Du opretter et engagement (en ansættelse) til en medarbejder, der starter 01-01-2026. Hvis du forsøger at give engagementet klassen "Projektleder", vil systemet ikke tillade det, fordi engagementet refererer til noget, der 'ikke findes' i den pågældende tidsperiode.

**Vær desuden opmærksom på**, at hvis lønsystemet er autoritativt for en klasse, og man ændrer den i MO, er der risiko for, at den bliver ændret tilbage, næste gang der synkroniseres data fra lønsystemet.
