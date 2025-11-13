# FK-Organisation

Kildekoden kan findes på https://github.com/magenta-aps/os2mo-os2sync-export

Dockerimage er tilgængeligt fra https://hub.docker.com/r/magentaaps/os2mo-os2sync-export
### Indledning

Denne integration gør det muligt at sende data fra OS2MO til [OS2Sync](https://www.os2sync.dk/). OS2Sync er i stand til at sende data videre til FK ORG. Anvend os2sync version 3.0.8 eller derover.

Integrationen er eventdrevet hvilket vil sige at det reagerer på ændringer i OS2MO. Ved ændringer læser den følgende informationer fra OS2MO og sender dem til OS2Sync:


Organisationsenheder:

* Navn
* UUID
* UUID på overenhed
* IT-systemer
* Adresser
* KLE-opmærkninger
* Leder UUID (Optionelt)

IT-brugere

* Navn eller kaldenavn (afhængigt af konfiguration)
* UUID, fx ObjectGUID fra AD - kan overstyres med faste uuid'er
* Brugernavn
* CPR-nummer (Optionelt)
* Adresser (Email, Mobil, Fastnet)
* Engagementer

Der synkroniseres altid kun adreser hvis synlighed er angivet som 'Må vises eksternt'.

### Datamodel i MO
For at kunne skelne oplysninger til forskellige brugere til samme person skal data i MO kobles sammen via it-konti, fx en AD konto. IT-kontoen skal derfor indeholde følgende oplysninger:

- `user_key`: brugernavn
- `external_id`: ID, fx. ObjectGUID
- `engagements`: en liste af uuid'er på relevante engagementer.
- `person`: uuid på personen

Desuden skal relevante addresser kobles til it-kontoen ved feltet `itusers`.



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
I FK-org svarer en bruger til en IT-konto, og når fk-org brugerens uuid matcher det i på it-brugeren vil denne konto være adgangsgivende til de støttesystemer der henter data fra FK-Org. For at sikre konsistente uuid'er opbevares det i en FK-org IT konti (IT-fanen i OS2MO). Denne konto har fk-org uuid'et i feltet `external id` og i feltet `user_key` gemmes ObjectGUID på den IT konto som fk-org uuid'et hører sammen med. Brugerens andet data vil således blive hentet fra den IT-konto som fk-org kontoen hører til.

Når integrationen sender brugere til OS2Sync, sker det efter
nedenstående skema:

| OS2Sync-felt    | Udfyldes med |
| - | - |
| `Uuid`| external_id fra fk-org it-brugeren. |
| `UserId` | user_key fra it-kontoen |
| `Name` | MO-personens fornavn og efternavn (Eller evt. kaldenavn) |
| `Cpr`  | MO-brugerens CPR-nummer, hvis indstillingen `OS2SYNC_XFER_CPR` er sat til `true`.|
| `Email`| Email knyttet til it-kontoen og som tilhører en af de konfigurerede addressetyper
| `Phone`| Telefonnummer knyttet til it-kontoen og som tilhører en af de konfigurerede addressetyper.
| `Landline`| Telefonnummer knyttet til it-kontoen og som tilhører en af de konfigurerede addressetyper.
|`Positions`| Stillingsbetegnelse og organisationsenhed for engagementer knyttet til IT-kontoen.

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
- `OS2SYNC_SYNC_MANAGERS`: Skriv leders uuid til orgunits. Kræver at  der kun er en leder pr. enhed.
- `OS2SYNC_USER_KEY_IT_SYSTEM_NAME`: Henter en brugers user_key fra IT-system. Default er "Active Directory"
- `OS2SYNC_FILTER_USERS_BY_IT_SYSTEM`: Synkroniser kun de brugere der har it-konto i it-systemet defineret i `os2sync_user_key_it_system_name`. Default er "false" så alle brugere synkroniseres.
- `OS2SYNC_UUID_FROM_IT_SYSTEMS`: Prioriteret liste af uuider på IT-systemer hvorfra en bruger/enheds uuid skal hentes. Bruger MOs  uuid hvis denne er tom eller hvis de angivne it-systemer ikke er udfyldt i MO.
- `OS2SYNC_FILTER_HIERARCHY_NAMES`: Liste af navne på organisations hierakier, fk.s. 'Linjeorganisation'. Synkroniserer kun organisaitionsenheder og ansatte der hører til i en af de angivne hierakier.
- `OS2SYNC_USE_NICKNAME`: Anvend kaldenavn i stedet for navn hvis det er sat.
