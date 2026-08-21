---
title: Eventbaseret integration
---

# Integration til eventbaseret AD import og eksport

## Overordnet beskrivelse

Integrationen importerer og eksporterer oplysninger mellem OS2mo (MO) og Active Directory (AD), når ændringerne indtræffer på udvalgte objekter (engagementer, adresser, mv., se nedenfor).

Nye brugere bliver oprettet automatisk i det ene eller det andet system. Typisk er OS2mo autoritativ for AD'et, men det er også muligt at oprette eksterne brugere med Active Directory som autoritativ kilde – fx ansatte i en privat virksomhed, byrådsmedlemmer og konsulenter. Det løser bl.a. problemstillinger, hvor en medarbejder både har en offentlig og en privat ansættelse, eller både er kommunalt ansat og byrådsmedlem. Forudsætningen herfor er understøttelsen af [multiple it-konti](https://rammearkitektur.docs.magenta.dk/os2mo/features/multipleitkonti.html).

Herudover lyttes der til ændringer på eksisterende objekter i både MO og AD, og systemerne opdateres med det samme, når ændringer indtræffer.

## Hvad kan MO fjernstyre i AD?

MO kan fjernstyre AD'et på følgende områder:
- **Organisationsenheder**
  - Oprettelse, vedligeholdelse og nedlæggelse af enheder (OU'er).
- **Brugerkonti**
  - Oprettelse, vedligeholdelse og nedlæggelse af brugere.
  - Brugernavne (se Generering af AD-brugernavne nedenfor).
  - Understøttelse af multiple brugerkonti pr. person, jf. [multiple it-konti](https://rammearkitektur.docs.magenta.dk/os2mo/features/multipleitkonti.html).
- **Grupper**
  - Sikkerhedsgrupper, postkasser og distributionsgrupper.
  - Tildeling af rettigheder og adgange via grupper.
- **Adgangsstyring**
  - Rettigheder til filer, mapper, systemer og applikationer.
- **Flere Active Directories**
  - Såfremt organisationen opererer med flere Active Directories, kan MO håndtere dem alle.

## Synkroniserede objekter

Følgende objekter kan synkroniseres den ene eller den anden vej, og det er muligt at tilføje flere objekter til synkroniseringen:

- Ansatte
- Ansattes adresser
- IT-konti
- Ansattes ansættelser (engagementer)
- Organisationsenheders adresser

Hvert objekt har en række attributter, der også opdateres, hvis det er specificeret. Et engagement kan fx få opdateret sin start- og slutdato, ansættelsestypen og stillingsbetegnelsen.

Man specificerer selv, hvilket system der skal være autoritativt for hvilke attributter: Måske skal Active Directory være autoritativ for stillingsbetegnelser, mens MO er autoritativ for oprettelse af brugere samt ansættelsestypen, jf. mapningstabellen nedenfor.

## MitID Erhverv UUID

Integrationen kan importere brugeres **MitID Erhverv UUID** fra AD'et og gemme det i MO som en adresse i relation til brugerens AD-it-konto. Herefter kan UUID'et overføres til et andet system og understøtte rettighedsstyring via NemLog-in.

MitID-UUID'et kan indlæses fra det AD-felt, den lokale NSIS IdP er konfigureret til – fx Signaturgruppens løsning. For Signaturgruppens løsning understøttes udlæsning fra `altSecurityIdentities`-attributten (værdien, der starter med NL3UUID).

## binding_type

IT-brugere i MO har feltet `binding_type`, som kan indeholde metadata om, hvorfor en given IT-bruger er oprettet og bundet til eksisterende data. Integrationen anvender feltet til at skelne mellem **eksplicitte og implicitte relationer**, den selv har oprettet. Feltet fungerer i alle henseender ligesom `external_id`-feltet.

## Mapning mellem MO og AD

En mapning mellem felter i MO og AD kan se ud som følger. Eksemplet giver også et billede af, hvilke attributter der
typisk synkroniseres:

| MO object class | MO attribute | MO-to-AD | AD-to-MO | AD attribute(s)              |
|-----------------|--------------|----------|----------|------------------------------|
| Employee        | givenname    | ✓        | %        | givenName                    |
| Employye        | surname      | ✓        | %        | sn                           |
| Employee        | cpr_no       | ✓        | %        | employeeID                   |
| ITUser          | user_key     | %        | ✓        | objectGUID                   |
| Address         | value        | ✓        | ✓        | mail                         |
| Address         | value        | ✓        | %        | streetAddress, l, postalCode |
| Address         | value        | ✓        | %        | postalAddress                |
| Engagement      | job_function | %        | ✓        | title                        |
| Engagement      | user_key     | ✓        | %        | countryCode                  |
| Address         | value        | ✓        | %        | telephoneNumber              |
| ITUser          | user_key     | ✓        | %        | sAMAccountName               |

## Konfigurationssproget (Jinja)

Mapningen udtrykkes i skabeloner (Jinja), og konfigurationssproget indeholder bl.a.:

- **'for each'-understøttelse**, så én regel kan udfoldes over flere objekter – fx flere engagementer på samme person.
- **Hjælpefunktioner** i skabelonerne, bl.a. opslag af den bedste DN, engagements-UUID'er og AD-attributværdier via CPR-nummer.
- **Parallel evaluering** af felt-skabelonerne, hvilket gør synkroniseringen hurtig.

### Generering af AD-brugernavne

Når en bruger bliver oprettet i MO, sendes brugerobjektet til AD, og et brugernavn bliver genereret (kan modificeres
afhængigt af, hvilke navnepolitikker der findes), hvis brugeren ikke i forvejen findes i AD’et. Det er CPR-nummeret, der bruges som nøgle. Det er også muligt at bruge ADs “objectGUID” attribut som nøgle.

Brugernavnsgenereringen følger nogle regler, som er konfigureret i en json-fil, fx

```json
{
  "username_generator": {
    "objectClass": "UserNameGenerator",
    "combinations_to_try": [
      "F123L",
      "F12LL",
      "F1LLL",
      "FLLLL",
      "FLLLLX"
    ],
    "char_replacement": {
      "ø": "oe",
      "æ": "ae",
      "å": "aa",
      "Ø": "oe",
      "Æ": "ae",
      "Å": "aa"
    },
    "forbidden_usernames": [
      "hater",
      "lazer"
    ]
  }
}
```

Sammensætningen af brugernavne følger dette mønster:

- F: Fornavn
- 1: Første efternavn
- 2: Andet efternavn
- 3: Tredje efternavn
- L: Efternavn
- X: Et løbenummer, der tilføjes

Når dette mønster anvendes på en Jens Hansen, vil han derfor få “jhans” som brugernavn i AD’et.

Hvis jhans allerede eksisterer, vil Jens Hansen få “jhans2”.

Brugernavnsgeneratoren kan desuden:

- Konsultere en **forbudtliste** med brugernavne, der ikke må genereres – fordi de kan betragtes som anstødelige, eller fordi de findes i forvejen i AD'et eller andre systemer, hvor der ikke må forekomme dubletter.
- Understøtte **genbrug af et brugernavn, man selv tidligere har haft** – fx når en tidligere medarbejder genansættes.

## Oprydningsværktøjer
Integrationen udstiller endpoints til dataoprydning, som bl.a. kan:

- Rydde op i adressers gyldigheder.
- Slette IT-brugere, der hører til et udfaset IT-system.

Det gør det let at holde datagrundlaget rent, når systemlandskabet ændrer sig.

## Drift, robusthed og fejlsøgning

- Der kan udsendes **refresh-events for et helt undertræ** i AD'et på én gang, fx efter konfigurationsændringer.
- Integrationen medsender **X-Request-ID** til MO, så kald kan spores på tværs af systemerne og korreleres med MOs logs. Det gør fejlsøgning på tværs af systemlandskabet væsentligt lettere.
- Integrationen er sikret mod uendelige redigeringsløkker på objekter med opsplittet gyldighed.

Se yderligere teknisk dokumentation [her](https://github.com/magenta-aps/os2mo-ldap-import-export).
