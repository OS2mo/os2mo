# FK-Organisation

Kildekoden kan findes på https://github.com/magenta-aps/os2mo-os2sync-export

Dockerimage er tilgængeligt fra https://hub.docker.com/r/magentaaps/os2mo-os2sync-export

### Indledning

Denne integration gør det muligt at sende data fra OS2MO til [OS2Sync](https://www.os2sync.dk/). OS2Sync er i stand til at sende data videre til FK ORG. Anvend os2sync version 3.0.8 eller derover.

Integrationen er eventdrevet hvilket vil sige at det reagerer på ændringer i OS2MO. Ved ændringer læser den følgende informationer fra OS2MO og sender dem til OS2Sync:

Organisationsenheder:

- Navn
- UUID
- UUID på overenhed
- IT-systemer
- Adresser
- KLE-opmærkninger
- Leder UUID (Optionelt)

Ansatte:

- Navn (eller kaldenavn - se under [os2sync_templates](#os2sync_templates))
- UUID
- UserId
- CPR-nummer (Optionelt)
- Adresser (Email, Mobil, Fastnet)
- Engagementer

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

I FK-org kan en person have en bruger pr. AD-konto, og når fk-org brugerens uuid matcher ObjectGUID i AD vil denne AD-konto være adgangsgivende til de støttesystemer der henter data fra FK-Org. For at sikre konsistente uuid'er og brugernavne kan både organisationsenheder og brugere konfigureres til at bruge uuid'et fra IT konti (IT-fanen i OS2MO). Brugerens UserId vil ligeledes blive hentet fra en "Active Directory" it-konto hvis en sådan findes, ellers bruges UUID'et fra OS2MO.

Når integrationen sender brugere til OS2Sync, sker det efter
nedenstående skema:

| OS2Sync-felt | Udfyldes med                                                                                                                                 |
| ------------ | -------------------------------------------------------------------------------------------------------------------------------------------- |
| `Uuid`       | MO-brugerens UUID, med mindre det er overskrevet af et it-system.                                                                            |
| `UserId`     | MO-brugerens UUID, med mindre det er overskrevet af et it-system. Default er at læse fra it-konti tilknyttet "Active Directory" it-systemet. |
| `Name`       | MO-brugerens fornavn og efternavn                                                                                                            |
| `Cpr`        | MO-brugerens CPR-nummer, hvis indstillingen `OS2SYNC_XFER_CPR` er sat til `true`.                                                            |

### Flere brugere pr person

Hvis der er skal sendes flere brugere pr. person til fk-org skal hvert it-system være knyttet til et engagement. Det gør det muligt for integrationen at finde både uuid og brugernavn til hver bruger, samt kun at sende det relevante engagement til fk-org. Desuden kan adresser også knyttes til engagementer, så hver fk-org konto får den korrekte email-addresse sendt med.

### Opsætning og konfiguration

Integrationen køres i docker - se docker-compose.yml for et eksempel på opsætning til udviklingsbrug.

Påkrævede:

- `OS2SYNC_API_URL`: Adresse på os2sync-containeres API, fx. "http://os2sync:5000/api"
- `OS2SYNC_TOP_UNIT_UUID`: UUID på den øverste enhed i os2mo organisation, der skal overføres til fk-org.
- `AMQP__URL`: Forbindelsesparametre til beskedkøen, fx. "amqp://guest:guest@msg_broker:5672/"
- `MO_URL`: Beskriver OS2MO's adresse, fx. " http://mo"
- `MUNICIPALITY` : Kommunens CVR-nummer

Autentificering sker vha. af en keycloak client som skal bruge følgende miljøvariable:

- `CLIENT_ID`
- `CLIENT_SECRET`
- `AUTH_SERVER`: fx "http://keycloak:8080/auth"

Valgfri:

- `LOG_LEVEL`: Loglevel, fx. WARNING eller DEBUG. Default er INFO
- `OS2SYNC_CA_VERIFY_OS2MO`: Angiver om OS2mo serverens certifikat skal checkes. Default er "true"
- `OS2SYNC_CA_VERIFY_OS2SYNC`: Angiver om Os2Sync containerens certifikat skal checkes. Default er "true"
- `OS2SYNC_PHONE_SCOPE_CLASSES`: Prioriteret rækkefølge af adresssetype klasser at vælge telefonnummer fra. Hvis ingen rækkefølge er sat vælges et tilfældig telefonnummer fra OS2MO.
- `OS2SYNC_LANDLINE_SCOPE_CLASSES`: Prioriteret rækkefølge af adresssetype klasser at vælge fastnet telefonnummer fra. Hvis denne ikke er udfyldt vil der ikke blive sendt noget fastnet nummer til os2sync.
- `OS2SYNC_EMAIL_SCOPE_CLASSES`: Prioriteret rækkefølge af adresssetype klasser at vælge email-adresser fra. Hvis ingen rækkefølge er sat vælges en tilfældig email-adresse fra OS2MO.
- `OS2SYNC_XFER_CPR`: Bestemmer om cpr-nummer skal overføres, default er "false"
- `OS2SYNC_IGNORED.UNIT_LEVELS`: liste af unit-level-klasser, der skal ignoreres i overførslen
- `OS2SYNC_IGNORED.UNIT_TYPES`: liste af unit-type-klasser, der skal ignoreres i overførslen
- `OS2SYNC_AUTOWASH`: Automatisk oprydning i organisationsenheder i fk-org der ikke findes i OS2MO. Default er 'false'.
- `OS2SYNC_SYNC_MANAGERS`: Skriv leders uuid til orgunits. Kræver at der kun er en leder pr. enhed.
- `OS2SYNC_TEMPLATES`: Giver mulighed for at styre formatteringen af data vha. Jinja-templates. Se afsnittet om [os2sync_tempaltes](#os2sync_templates)
- `OS2SYNC_USER_KEY_IT_SYSTEM_NAME`: Henter en brugers user_key fra IT-system. Default er "Active Directory"
- `OS2SYNC_FILTER_USERS_BY_IT_SYSTEM`: Synkroniser kun de brugere der har it-konto i it-systemet defineret i `os2sync_user_key_it_system_name`. Default er "false" så alle brugere synkroniseres.
- `OS2SYNC_UUID_FROM_IT_SYSTEMS`: Prioriteret liste af uuider på IT-systemer hvorfra en bruger/enheds uuid skal hentes. Bruger MOs uuid hvis denne er tom eller hvis de angivne it-systemer ikke er udfyldt i MO.
- `OS2SYNC_FILTER_HIERARCHY_NAMES`: Liste af navne på organisations hierakier, fk.s. 'Linjeorganisation'. Synkroniserer kun organisaitionsenheder og ansatte der hører til i en af de angivne hierakier.

### os2sync_templates

Denne indstilling kan bruges til at styre, hvordan felter sendes til
OS2Sync. Indstillingen består af en eller flere feltnøgler, og en
tilhørende
[Jinja-template](https://jinja.palletsprojects.com/en/2.11.x/templates/).

På nuværende tidspunkt kender programmet feltnøglerne `person.name` og
`person.user_id`, der bruges til at kontrollere, hvordan hhv.
personnavne og bruger-id'er formatteres, når de sendes til OS2SYNC\_

Et eksempel på brug:

```bash
  OS2SYNC_TEMPLATES='{"person.name": "{% if nickname -%}{{ nickname }}{%- else %}{{ name }}{%- endif %}"}'

```

Denne opsætning betyder, at vi først tjekker om der er et kaldenavn (`nickname`) registreret på personen i MO. Hvis der er, så anvendes dette, når der skrives et personnavn til OS2SYNC\_ Hvis ikke, så anvendes det almindelige navn, der er registreret på personen (`name`.)

Et eksempel på brug af `person.user_id`:

```bash
OS2SYNC_TEMPLATES='{"person.user_id": "{{ user_key }}"}}'
```

Hvis OS2Sync-integrationen sættes op med denne opsætning, skriver den MO-brugerens BVN (brugervendte nøgle) i OS2Sync-feltet `UserId`, medmindre MO-brugeren også har et registreret IT-system af typen "AD". I så fald anvendes det AD-brugernavn, der er registreret på IT-systemet.
