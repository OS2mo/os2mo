---
title: Export til FK-ORG via OS2Sync
---

### Indledning

Denne integration gør det muligt at sende data fra OS2MO til
[OS2Sync](https://www.os2sync.dk/). OS2Sync er i stand til at sende data videre til FK ORG, såfremt det er installeret og konfigureret.
Integrationen læser flg. oplysninger i OS2MO, og sender dem til OS2Sync:

OS2MO | Oplysninger
|- | -
| Organisationsenheder | <ul><li>UUID</li><li>Parent UUID</li><li>Navn</li><li>IT-systemer</li><li>Adresser</li><li>KLE-opmærkninger</li><li>Leder UUID (Optionelt)</li></ul> |
| Ansatte| <ul><li>UUID</li><li>UserId</li><li>Navn (eller kaldenavn - se under os2sync.templates)</li><li>CPR-nummer (Optionelt)</li><li>Adresser (Email, Mobil, Fastnet)</li><li>Engagementer</li></ul>                              |

Der synkroniseres altid kun adreser hvis synlighed er angivet som 'Må vises eksternt'.

### Organisationsenheder
Når integrationen sender organisationsenheders adresser til OS2Sync, sker det efter nedenstående skema. Såfremt en adresseoplysning på
enheden matcher på "Scope" og evt. "Brugervendt nøgle", sendes
oplysningen til feltet angivet i "OS2Sync-felt":

| Scope     | Brugervendt nøgle  | OS2Sync-felt       |
| --------- | ------------------ | ------------------ |
| `EMAIL`   | (vilkårlig)        | `Email`            |
| `EAN`     | (vilkårlig)        | `Ean`              |
| `PHONE`   | (vilkårlig)        | `PhoneNumber`      |
| `DAR`     | (vilkårlig)        | `Post`             |
| `PNUMBER` | (vilkårlig)        | `Location`         |
| `TEXT`    | `ContactOpenHours` | `ContactOpenHours` |
| `TEXT`    | `DtrId`            | `DtrId`            |



### Brugere
I FK-org kan en person have en bruger pr. AD-konto, og når fk-org brugerens uuid matcher ObjectGUID i AD vil denne AD-konto være adgangsgivende til de støttesystemer der henter data fra FK-Org. For at sikre konsistente uuid'er og brugernavne kan både organisationsenheder og brugere konfigureres til at bruge uuid'et fra IT konti (IT-fanen i OS2MO). Brugerens UserId vil ligeledes blive hentet fra en "Active Directory" it-konto hvis en sådan findes.

Når integrationen sender brugere til OS2Sync, sker det efter
nedenstående skema:

| OS2Sync-felt    | Udfyldes med |
| - | - |
| `Uuid`| MO-brugerens UUID, med mindre det er overskrevet af et it-system. |
| `UserId` | MO-brugerens UUID, med mindre det er overskrevet af et it-system. Default er at læse fra it-konti tilknyttet "Active Directory" it-systemet. |
| `Name` | MO-brugerens fornavn og efternavn |
| `Cpr`  | MO-brugerens CPR-nummer, hvis indstillingen `os2sync.xfer_cpr` er sat til `true`.|

### Flere brugere pr person

Hvis der er skal sendes flere brugere pr. person til fk-org skal hvert it-system være knyttet til et engagement. Det gør det muligt for integrationen at finde både uuid og brugernavn til hver bruger, samt kun at sende det relevante engagement til fk-org. Desuden kan adresser også knyttes til engagementer, så hver fk-org konto får den korrekte email-addresse sendt med.

### Opsætning og konfiguration

For at kunne afvikle integrationen kræves en række opsætninger af den
lokale server.

Opsætningen kan læses fra `settings.json` eller som miljøvariable med `os2sync_`-prefix.

### fælles parametre

- `crontab.RUN_OS2SYNC`: Bestemmer om jobbet skal køres i cron
  (true/false)
- `mora.base`: Beskriver OS2MO's adresse
- `municipality.cvr` : Kommunens CVR-nummer
- `log_level`: Loglevel, fx. INFO eller DEBUG. Default er WARNING

Autentificering sker vha. af en keycloak client som skal bruge følgende miljøvariable:

- `CLIENT_ID`
- `CLIENT_SECRET`
- `AUTH_SERVER`


### os2syncs parametre
Påkrævede:
- `os2sync.api_url`: Adresse på os2sync-containeres API, default er
  " http://localhost:8081/api"
- `os2sync.top_unit_uuid`: UUID på den top-level organisation, der
  skal overføres

Valgfri:
- `os2sync.ca_verify_os2mo`: Angiver om OS2mo serverens certifikat
  skal checkes. Default er "true"
- `os2sync.ca_verify_os2sync`: Angiver om Os2Sync containerens
  certifikat skal checkes. Default er "true"
- `os2sync.hash_cache`: Sti til en cache-fil som sørger for at kun ændringer overføres.
- `os2sync.phone_scope_classes`: Prioriteret rækkefølge af adresssetype klasser at vælge telefonnummer fra. Hvis ingen rækkefølge er sat vælges et tilfældig telefonnummer fra OS2MO.
- `os2sync.landline_scope_classes`: Prioriteret rækkefølge af adresssetype klasser at vælge fastnet telefonnummer fra. Hvis denne ikke er udfyldt vil der ikke blive sendt noget fastnet nummer til os2sync.
- `os2sync.email_scope_classes`: Prioriteret rækkefølge af adresssetype klasser at vælge email-adresser fra. Hvis ingen rækkefølge er sat vælges en tilfældig email-adresse fra OS2MO.

- `os2sync.xfer_cpr`: Bestemmer om cpr-nummer skal overføres, default er "false"
- `os2sync.use_lc_db`: Bestemmer om kørslen skal hente data fra sqlite-filen dannet ud fra loracache af jobbet exports_lc_for_jobs_db. Default er 'false'.
- `os2sync.ignored.unit_levels`: liste af unit-level-klasser, der
  skal ignoreres i overførslen
- `os2sync.ignored.unit_types`: liste af unit-type-klasser, der skal
  ignoreres i overførslen
- `os2sync.autowash`: Automatisk oprydning i organisationsenheder i fk-org der ikke findes i OS2MO. Default er 'false'.
- `os2sync.sync_managers`: Skriv leders uuid til orgunits. Kræver at
  der kun er en leder pr. enhed.
- `os2sync.templates`: Giver mulighed for at styre formatteringen af
  data vha. Jinja-templates.
- `os2sync.user_key_it_system_name`: Henter en brugers user_key fra
  IT-system. Default er "Active Directory"
- `os2sync.filter_users_by_it_system`: Synkroniser kun de brugere der har it-konto i it-systemet defineret i `os2sync_user_key_it_system_name`. Default er "false" så alle brugere synkroniseres.
- `os2sync.uuid_from_it_systems`: Prioriteret liste af uuider på
  IT-systemer hvorfra en bruger/enheds uuid skal hentes. Bruger MOs
  uuid hvis denne er tom eller hvis de angivne it-systemer ikke er
  udfyldt i MO.
- `os2sync.filter_hierarchy_names`: Liste af navne på organisations hierakier, fk.s. 'Linjeorganisation'. Synkroniserer kun organisaitionsenheder og ansatte der hører til i en af de angivne hierakier.


### `os2sync.templates`

Denne indstilling kan bruges til at styre, hvordan felter sendes til
OS2Sync. Indstillingen består af en eller flere feltnøgler, og en
tilhørende
[Jinja-template](https://jinja.palletsprojects.com/en/2.11.x/templates/).

På nuværende tidspunkt kender programmet feltnøglerne `person.name` og
`person.user_id`, der bruges til at kontrollere, hvordan hhv.
personnavne og bruger-id'er formatteres, når de sendes til OS2Sync.

Et eksempel på brug:

```json
{
  "os2sync.templates": {
    "person.name": "{% if nickname -%}{{ nickname }}{%- else %}{{ name }}{%- endif %}"
  }
}
```

Denne opsætning betyder, at vi først tjekker om der er et kaldenavn
(`nickname`) registreret på personen i MO. Hvis der er, så anvendes
dette, når der skrives et personnavn til OS2Sync. Hvis ikke, så anvendes det almindelige navn, der er registreret på personen (`name`.)

Et eksempel på brug af `person.user_id`:

```json
{
  "os2sync.templates": {
    "person.user_id": "{{ user_key }}"
  }
}
```

Hvis OS2Sync-integrationen sættes op med denne opsætning, skriver den
MO-brugerens BVN (brugervendte nøgle) i OS2Sync-feltet `UserId`,
medmindre MO-brugeren også har et registreret IT-system af typen "AD".
I så fald anvendes det AD-brugernavn, der er registreret på IT-systemet.
