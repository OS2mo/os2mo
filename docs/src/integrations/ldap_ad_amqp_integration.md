---
title: Eventbaseret integration
---

# Tovejs, eventbaseret integration mellem MO og Active Directory

## Overordnet beskrivelse

Integrationen importerer og eksporterer oplysninger mellem MO og Active Directory (AD) via LDAP(S), når ændringerne
indtræffer på udvalgte objekter (engagementer, adresser, mv., se nedenfor).

Nye brugere vil blive oprettet automatisk i det ene eller det andet system. Typisk er MO autoritativ for AD’et.

Herudover lyttes der til ændringer på eksisterende objekter i både MO og AD, og systemerne opdateres med det samme, når
ændringer indtræffer.

Hvert objekt har en række attributter, der også vil blive opdateret, såfremt det er specificeret. Et engagement kan
således fx få opdateret sin start- og slutdato, ansættelsestypen og stillingsbetegnelsen.

Man specificerer ligeledes selv, hvilket system der skal være autoritativt for hvilke attributter: Måske er man
interesseret i, at Active Directory er autoritativ for stillingsbetegnelser, mens MO er autoritativ for oprettelse af
brugere samt ansættelsestypen, se mapningstabellen nedenfor.

## Overordnet arkitektur

Integrationen fungerer som en **eventdrevet agent**, der lytter efter hændelser fra begge systemer og sikrer, at data holdes konsistente på tværs.

```
┌──────┐  GraphQL / HTTP  ┌─────────────────────────┐  LDAP(S)  ┌─────────────────────────┐
│  MO  │ ◄──────────────► │  mo_ldap_import_export  │ ◄───────► │ Active Directory / LDAP │
└──────┘                  └─────────────────────────┘           └─────────────────────────┘
```

Applikationen afvikles som en Docker-container og eksponerer et HTTP-API.

---

## Dataflow

### MO → LDAP

1. En ændring sker i MO (f.eks. ny medarbejder, opdateret adresse).
2. MO udsender en hændelse via sit event-system.
3. Integrationen modtager hændelsen, beregner den ønskede tilstand i LDAP ud fra den konfigurerede felttilknytning og opdaterer LDAP-objektet.

### LDAP → MO

1. En ændring sker i LDAP/Active Directory.
2. Integrationen detekterer ændringen via LDAP-polling.
3. Integrationen beregner den ønskede tilstand i MO ud fra den konfigurerede felttilknytning og opdaterer de relevante objekter i MO.

---

### Generering af AD-brugernavne

Når en bruger bliver oprettet i MO, sendes brugerobjektet til AD, og et brugernavn bliver genereret (kan modificeres
afhængigt af, hvilke navnepolitikker der findes), hvis brugeren ikke i forvejen findes i AD’et. Det er CPR-nummeret, der
bruges som nøgle. Det er også muligt at bruge ADs “objectGUID” attribut som nøgle.

Brugernavnsgenereringen følger nogle regler, som er konfigureret i en json-fil, fx

```json
{
  "username_generator": {
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

Brugernavnsgeneratoren kan desuden konsultere en såkaldt forbudtliste, som indeholder brugernavne, der ikke må
genereres. Det kan være fordi de kan betragtes som anstødelige, eller fordi de findes i forvejen i AD’et eller andre
systemer, hvor der ikke må forekomme dubletter.

## Links

- Repository: https://github.com/OS2mo/os2mo-ldap-import-export
- Magenta ApS: https://magenta.dk/
