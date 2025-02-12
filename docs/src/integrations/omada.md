# Omada

## Indledning

Integrationen henter brugerdata fra Omada og indlæser dem i OS2mo. Integrationen beriger allerede eksisterende brugere i OS2mo og opretter også helt nye brugere, der er manuelt oprettet i Omada.

Integrationen understøtter at samme bruger kan have flere AD-konti og flere engagementer (ansættelser) samt at disse kan bindes sammen.

## Forudsætninger

For at integrationen kan aktiveres, skal følgende være på plads:

1. Et view udstilles i Omada med alle relevante data.
2. Brugertyperne opmærkes.
3. Der laves en servicekonto til Magenta, som har læserettigheder til viewet.
4. Der tilvejebringes en testinstans til Omada.
5. Autentificering foregår via OIDC eller HTTP Basic Auth.
6. En nøgle, der kan identificere en bruger unikt i hhv. Omada og OS2mo, tilvejebringes.
7. Det identificeres hvordan der kan skelnes mellem nyoprettede og allerede eksisterende brugere. Det skal dog først verificeres om det er nødvendigt i det lokale setup.

## Omada view

Data fra Omada bliver indlæst i OS2mo via et view. Nedenstående data vil blive synkroniseret.

Alle **brugere** har en VALIDFROM/VALIDTO, der bliver importeret ind i MO på hvert synkroniseret objekt. Vikarer har disse felter for **personerne**:

- Fornavne
- Efternavn
- CPRnr.

Samt felter for **engagementerne**:

- Stillingsbetegnelse - Passer præcist med de jobtitler, der allerede eksisterer i MO. Hvis ikke sættes en standard-jobtitel.
- Organisationskode - Det kan være AD GUID, hvis disse er opsat som IT-konti på enhederne. Kan også være enhedsnummeret (bvn - brugervendt nøgle).
- Synlighed - Sæt en adresse til 'hemmelig', 'må vises internt' eller 'må vises eksternt'.

Derudover bliver **adresser** synkroniseret for fx felter:

- E-mail
- Direkte telefonnummer
- Mobiltelefonnummer

Og **IT-konti** for følgende felter:

- ObjectGuid fra Active Directory
- AD-login / SamAccountName

## Skelnen mellem eksisterende og manuelt oprettede medarbejdere

Manuelt oprettede brugere bliver kun oprettet, hvis de har en identitetskode. Allerede eksisterende brugere vil have en anden identitetskode, så det er muligt at skelne.

## Manglende historik på slettede brugere

Når en bruger slettes i Omada (og ikke længere er med i viewet), vil brugerens engagement også blive slettet i MO, og der vil altså ikke fremgå nogen historik på engagementet i MOs GUI (fortidsfanen) - Det er en konsekvens af, at Omada ikke opererer med bitemportalitet ligesom MO. Man vil dog altid kunne finde historikken i MOs database om nødvendigt.

## Datahåndtering i MO GUI

I OS2mo vil ObjectGuid og ad-login (SamAccountName) blive skrevet under fanen it-system på brugeren, og adresser vil blive placeret under adressefanen.

Der vil være relationer mellem _engagementer_ og _adresser_ samt _it-konti_ og _engagementer_. Det vil sørge for at en bruger med flere engagementer og flere it-konti kan få tildelt differentierede rettigheder i fx FK Organisation.

_Bemærk at objectguid og ad-login (SamAccountName) vil fremgå af hver sin række i OS2mo’s GUI under fanen it-system._

## Adgangsstyring & autentificering

For at kunne tilgå viewet, skal OS2mo have en servicekonto, som har læserettigheder til viewet.
Den foretrukne autentificeringsmetode mod API'et er via OIDC.

## Frekvens

Omada er ikke event-baseret, så det er OS2mo der skal spørge Omada om ændringer. Os2mo kan gøre det med et interval, der er nærmere specificeret af kunden, fx hvert kvarter eller hvert minut.
