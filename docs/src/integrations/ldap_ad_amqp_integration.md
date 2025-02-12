---
title: Eventbaseret integration
---

# Integration til eventbaseret AD import og eksport

### Overordnet beskrivelse

Integrationen importerer og eksporterer oplysninger mellem OS2mo (MO) og Active Directory (AD), når ændringerne
indtræffer på udvalgte objekter (engagementer, adresser, mv., se nedenfor).

Nye brugere vil blive oprettet automatisk i det ene eller det andet system. Typisk er OS2mo autoritativ for AD’et.

Herudover lyttes der til ændringer på eksisterende objekter i både MO og AD, og systemerne opdateres med det samme, når
ændringer indtræffer.

Følgende objekter kan synkroniseres den ene eller den anden vej, men det er også muligt at tilføje flere objekter til
synkroniseringen:

- Ansatte
- Ansattes adresser
- IT-konti
- Ansattes ansættelser (engagementer)
- Organisationsenheders adresser

Hvert objekt har en række attributter, der også vil blive opdateret, såfremt det er specificeret. Et engagement kan
således fx få opdateret sin start- og slutdato, ansættelsestypen og stillingsbetegnelsen.

Man specificerer ligeledes selv, hvilket system der skal være autoritativt for hvilke attributter: Måske er man
interesseret i, at Active Directory er autoritativ for stillingsbetegnelser, mens MO er autoritativ for oprettelse af
brugere samt ansættelsestypen, se mapningstabellen nedenfor.

### Mapning mellem MO og AD

En mapning mellem felter i MO og AD kan se ud som følger. Eksemplet giver også et billede af, hvilke attributter der
typisk synkroniseres:

| MO object class | MO attribute | MO-to-AD | AD-to-MO | AD attribute(s)              |
| --------------- | ------------ | -------- | -------- | ---------------------------- |
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

### Generering af AD-brugernavne

Når en bruger bliver oprettet i MO, sendes brugerobjektet til AD, og et brugernavn bliver genereret (kan modificeres
afhængigt af, hvilke navnepolitikker der findes), hvis brugeren ikke i forvejen findes i AD’et. Det er CPR-nummeret, der
bruges som nøgle. Det er også muligt at bruge ADs “objectGUID” attribut som nøgle.

Brugernavnsgenereringen følger nogle regler, som er konfigureret i en json-fil, fx

```json
{
  "username_generator": {
    "objectClass": "UserNameGenerator",
    "combinations_to_try": ["F123L", "F12LL", "F1LLL", "FLLLL", "FLLLLX"],
    "char_replacement": {
      "ø": "oe",
      "æ": "ae",
      "å": "aa",
      "Ø": "oe",
      "Æ": "ae",
      "Å": "aa"
    },
    "forbidden_usernames": ["hater", "lazer"]
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

Brugernavnsgeneratoren kan desuden konsultere en såkaldt forbudtliste, som indeholder brugernavne, der ikke må
genereres. Det kan være fordi de kan betragtes som anstødelige, eller fordi de findes i forvejen i AD’et eller andre
systemer, hvor der ikke må forekomme dubletter.

Se yderligere teknisk dokumentation [her](https://github.com/magenta-aps/os2mo-ldap-import-export).
