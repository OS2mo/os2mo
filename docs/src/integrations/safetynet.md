---
title: SafetyNet
---

## Beskrivelse

SafetyNet-rapportmodulet kan uploade data fra OS2mo til
[EG SafetyNet](https://eg.dk/it/eg-safetynet/), som i Safetynet kan anvendes til at
behandle informationer om arbejdsmiljø og HR. Modulet genererer følgende 4 rapporter,
i CSV-format, som via SFTP uploades til SafetyNet. Rapporterne uploades som
udgangspunkt een gang i døgnet, men dette kan justeres efter behov.

1. En rapport over medarbejderne i den administrative lønorganisation. Rapporten
   indeholder følgende felter for hver medarbejder:

     * Medarbejdernummer
     * CPR
     * Fornavn
     * Efternavn
     * Mail|
     * Afdelingskode
     * Startdato
     * Slutdato
     * Leders medarbejdernummer
     * Brugernavn
     * Titel
     * Faggruppe

2. En rapport over organisationsenhederne i den administrative lønorganisation.
   Rapporten indeholder følgende felter for hver organisationsenhed:

     * Afdelingsnavn
     * Afdelingskode
     * Forældreafdelingskode
     * Pnummer

3. En rapport over medarbejderne i MED-organisationen. Rapporten indeholder følgende
   felter for hver medarbejder:

     * CPR
     * Afdelingskode
     * Startdato
     * Slutdato
     * Hverv
     * Hovedorganisation

4. En rapport over organisationsenhederne i den MED-organisation.
   Rapporten indeholder følgende felter for hver organisationsenhed:

     * Afdelingsnavn
     * Afdelingskode
     * Forældreafdelingskode
