---
title: Tools
---

Tools indeholder scripts primært beregnet til at køre natlige jobs og
restore af data efter fejlede jobs.

- job-runner.sh - excutable beregnet til at blive kaldt fra crontab
  uden parametre
- clear_mox_tables.py - beregnet til at tømme os2mo's tabeller ved
  nyindlæsning
- cron-restore.sh - beregnet til at restore OS2MO til før den kørsel,
  som backuppen er taget efter
- moxklas.sh - beregnet til at oprette klasser i LORA - udenom OS2MO
  ved specialle behov
- prefixed_settings.sh - beregnet til at eksportere settings fra en
  JSON-fil og ind i current shell environment
- renew-keytab.sh - beregnet til at oprette/genskabe keytabs
- update-dipex.sh - beregnet til at opdatere dette git-repo med ny
  kode, requirements etc

## job-runner.sh

!!! important
Det er nødvendigt at ændre gruppeejerskab, så det er alignet
med den gruppe, der kører docker, Denne gruppe skal eje både hele
os2mo-data-import-and-export og det directory hvor konfigurationsfiler
ligger I praksis betyder det for os at vi ændrer ejerskabet på det
dertil indrettede CRON-dicrectory i systembrugerens hjemmemappe.

### Afvikling af cron-jobs

Job runner scriptet er ment til at blive kaldt fra crontab på kundens
maskiner Dets arbejde er:

- at læse konfigurationen fra settings/settings.json, som er et
  symbolsk link til settings-filen for systemet.
- at køre de prædefinerede dele af nattens cronjob forudsat at de er
  slået til i konfigurationen
- at lave en backup af databasen og andre filer, der skal i spil for
  at få systemet tilbage til en veldefineret tilstand

### Læsning af konfiguration

Konfigurationen kan se således ud:

```json
{
  "crontab.SVC_USER": "USER@KOMMUNE.NET",
  "crontab.SVC_KEYTAB": "/path/keytab-file",
  "crontab.CRON_BACKUP": "/path/backup-dir",
  "crontab.CRON_LOG_FILE": "/path/cron-log-file",
  "crontab.RUN_MOX_DB_CLEAR": false,
  "crontab.RUN_CHECK_AD_CONNECTIVITY": false,
  "crontab.RUN_BALLERUP_APOS": false,
  "crontab.RUN_BALLERUP_UDVALG": false,
  "crontab.RUN_QUERIES_BALLERUP": false,
  "crontab.RUN_SD_CHANGED_AT": false,
  "crontab.RUN_SD_FIX_DEPARTMENTS": false,
  "crontab.RUN_SD_DB_OVERVIEW": false,
  "crontab.RUN_AD_SYNC": false,
  "crontab.RUN_MOX_STS_ORGSYNC": false,
  "crontab.RUN_MOX_ROLLE": false,
  "crontab.RUN_CPR_UUID": false,
  "crontab.BACKUP_SAVE_DAYS": "60",
  "crontab.MOX_ROLLE_COMPOSE_YML": "",
  "crontab.SNAPSHOT_LORA": "/path/db-snapshot.sql"
}
```

En konfiguration som ovenstående kører ingen jobs, laver en backup i
`/path/backup-dir` og sletter gamle backupper, når de er mere end `60`
dage gamle. Det bruger AD-kontoen `USER@KOMMUNE.NET` når den skal
connecte til AD og logger ind med `/path/keytab-file`, når det behøves
og logger progress til `/path/cron-log-file`.

For at enable importen fra SD sættes `crontab.RUN_SD_CHANGED_AT` til
`true`.

For at enable exporten til STS Organisation, sættes
`crontab.RUN_MOX_STS_ORGSYNC` til `true`.

For at enable exporten to Rollekataloget, sættes `crontab.RUN_MOX_ROLLE`
til `true` og `crontab.MOX_ROLLE_COMPOSE_YML` udfyldes med stien til den
gældende docker-compose.yml file for Rollekatalogseksporten.

Ideen er at dette script kan kaldes fra cron, finder sin egen
konfiguration, kører programmerne, hvorefter det laver en backup af
`/path/db-snapshot.sql` og andre filer, der er nødvendige for at komme
tilbage til en veldefineret tilstand.

Der kan være mere konfiguration nødvendig for de enkelte jobs - se disse
for detaljer

### Mountpoints

Tilvejebringelse (og afslutning) af mountpoints styres af et script,
cronhook.sh, som kaldes før og efter job-runner.sh. Dette script
afvilker scripts i cronhook.pre.d og cronhook.post.d, hvis de er slået
til i settings Sripts her afvikles i alfabetisk orden, og de bør hver
især brokke sig over de settings de mangler

For at mounte opus-filer ind fra et windows share anvendes følgende
settings:

- cronhook.mount_opus_on: true/ false
- cronhook.mount_opus_share - en windows unc-sti
- cronhook.mount_opus_mountpoint - det mounpoint hvor sharet mountet
- cronhook.mount_opus_username - brugernavn til sharet
- cronhook.mount_opus_password - password til sharet

For at unmounte efter kørslen sættes denne setting, men lad være med
det. Det besværliggør fejlfinding, hvis ikke der hele tiden er kontakt
til filerne

- cronhook.unmount_opus_on: true/false

Husk at mountpoints på windows ofte indeholder `$`-tegnet. Et sådan skal
i settings escapes som `\$`

### Kørsel af jobs

job-runner.sh er ikke et smart program. Det er til gengæld simpelt.
Job-afviklingen foregår i 3 afdelinger: _imports_, _exports_ og _reports_.

- For alle jobs i imports og exports gælder at et fejlet job stopper
  afviklingen af de resterende jobs i den pågældfende afdeling
- Hvis imports går galt, afvikles hverken exports eller reports
- Hvis imports går godt forsøges både exports or reports afviklet

I ovenstående konfiguration kan man slå jobs til med alle de
tilgængeglige `crontab.RUN_*`, som dækker over:

- `RUN_MOX_DB_CLEAR` - Tøm OS2mo's database
- `RUN_CHECK_AD_CONNECTIVITY` - Check at der er di korrekte rettigheder
  i AD
- `RUN_SD_FIX_DEPARTMENTS` - Kør SD-fix-departments
- `RUN_SD_CHANGED_AT` - Kør SD-changed-at - deltaimport af ændringer fra
  SD
- `RUN_SD_UPDATE_PRIMARY` - Kør Primærberegning af SD-employees
- `RUN_BALLERUP_APOS` - Indlæs til OS2MO fra APOS (Ballerups version)
- `RUN_OPUS_DIFF_IMPORT` - Kør Opus diff import - deltaimport af
  øndringer fra OPUS
- `RUN_AD_SYNC` - Kør en AD-synkronisering
- `RUN_BALLERUP_APOS` - total-indlæsning af APOS i Ballerup
- `RUN_BALLERUP_UDVALG` - udvalgshierarkiet i Ballerups OS2MO
- `RUN_MOX_ROLLE` - overførslen til rollekataloget
- `RUN_MOX_STS_ORGSYNC` - Overførslen til STS Organisation
- `RUN_QUERIES_BALLERUP` - Ballerups exports / forespørgsler
- `RUN_EXPORT_EMUS` - Kør Eksport til EMUS
- `RUN_CPR_UUID` - Lav en cachefile med CPR/UUID-sammenhænge - gøres
  typisk før en genindlæsning/restore
- `RUN_EXPORTS_TEST` - Kør ingenting, men viser at job-runner har været
  i gang
- `RUN_SD_DB_OVERVIEW` - Kør overbliksrapport over SD-indlæsningens
  progress (datoer)
- `RUN_OPUS_DB_OVERVIEW` - Kør overbliksrapport over OPUS-indlæsningens
  progress (datoer)
- `RUN_AD_GROUP_INTO_MO` - Importer en gruppe af eksterne ansatte som
  ikke findes i lønsystemet

### Pakning og lagring af Backup

Filer til backup er angivet i 3 afdelinger (bash-arrays):

- `BACK_UP_BEFORE_JOBS` - fil lagres i backup inden kørslen af de
  enablede jobs afvikles
- `BACK_UP_AFTER_JOBS` - fil lagres i backup efter at kørslen af de
  enablede jobs er afviklet
- `BACK_UP_AND_TRUNCATE` - fil lagres i backup efter at kørslen af de
  enablede jobs er afviklet, hvorefter fil trunkeres til størrelse 0.
  Dette er praktisk til logfiler, som nu pakkes sammen med det
  datagrundlag, der skal til for at gentage kørslen.

Pakning af backup foregår i to afdelinger:

- _pre_backup_ - her pakkes alle filer i `BACK_UP_BEFORE_JOBS` sammen i en
  tidsstemplet tarfil
- _post_backup_ - her pakkes filerne i `BACK_UP_AFTER_JOBS` og
  `BACK_UP_AND_TRUNCATE` ned i tarfilen, som gzippes og filerne i
  `BACK_UP_AND_TRUNCATE` trunkeres.

Lagringen af backup foregår i servicebrugerens hjemmedirectory, se
`crontab.CRON_BACKUP` i konfigurationseksemplet ovenfor.

### Afvikling af et enkelt job udenom cron

Det kan, for eksempel under udvikling eller test, være nødvendigt at
starte et program manuelt. Den mulighed har man også med job-runner
scriptet. Man giver simpelhen navnet på den indre funktion med i kaldet.

Herefter læses konfiguration på normal vis, men der tages nu ikke hensyn
til om jobbet er slået til i konfigurationen eller ej, det køres

Følgende interne funktioner kan kaldes:

- imports_test_ad_connectivity
- imports_sd_fix_departments
- imports_sd_changed_at
- imports_opus_diff_import
- imports_sd_update_primary
- imports_ad_sync
- imports_ballerup_apos
- imports_ballerup_udvalg
- exports_mox_rollekatalog
- exports_mox_stsorgsync
- exports_os2mo_phonebook
- exports_cpr_uuid
- exports_viborg_emus
- reports_sd_db_overview
- reports_opus_db_overview
- exports_queries_ballerup
- exports_test
- imports
- exports
- reports

Vil man for eksempel afvikle mox_stsorgsync, anvender man kaldet:

```bash
tools/jon-runner.sh exports_mox_stsorgsync
```

#### dotning / (sourcing) af job-runner.sh

Man kan source (. tools/job-runner.sh) for at få sat sit environment op.
Dermed kan man få adgang til at anvende samme backup/restore
funktionalitet, som anvendes af job-runner.sh / cron-restore.sh. Se
tools/opus_import_all.sh for hvordan man angiver filer, der skal backes
op måske trunkeres efterfølgende. Det er vigtigt at du bruger dit eget
suffix - se her også eksemplet i [opus_import_all.sh](#opus_import_allsh)

#### job-status json-logning

i settings findes mulighed for at logge til distribueret log. Det er
værdien `crontab.CRON_LOG_JSON_SINK`, der bestemmer, hvor loggen
skrives. Hvis den er slået til skrives der jsonlines til denne fil med
status på både de store linier og de enkelte jobs. Hvis den ikke er
slået til, gives der en warning i det almindelige logoutput.

I tillæg til denne fil pakker vi de jsonlinier, der vedrører nærværende
kørsel af job-runner, ned i den backup-fil, som vedrører kørslen. Det
sker ved at vi skriver til filen `crontab.CRON_LOG_JSON`, som trunkeres
efter pakning til log og kørsel.

#### job-status metrikker til prometheus

Magenta anvender tidsseriedatabasen Prometheus til at opsamle metrikker
på udstrækningen af de jobs, der afvikles af job-runner.
Konfigurationsværdien `crontab.CRON_LOG_PROM_API` styrer både hvorvidt
denne funktionalitet er slåt til og hvor man kalder api'et, som typisk
vil være igennem en såkaldt push-gateway på localhost.

## clear_mox_tables.py

Dette anvendes typisk kun af `cron-restore` og dér, hvor man hver nat
genindlæser OS2mo fra APOS.

## cron-restore.sh

Tømmer OS2MOS database og indlæser backup i mo og pakker den tilhørende
run-db ud. Run-db er den lille sqlite-database, som fortæller
SD-changed-at/opus_diff_import hvor langt den er kommet in indlæsningen.

Programmet køres som root på følgende måde:

```bash
bash tools/cron-restore.sh backupfil.tar.gz
```

`backupfil.tar.gz` er så en af de daterede filer, der ligger under
sti-til-service-bruger/CRON/backup

Programmet er 17/3 2020 skrevet om til at håndtere os2mo under docker.

## moxklas.sh

Anvendes under implementering til at oprette klasser i Lora. Nogle gange
også efterfølgende. Scriptet er simpelt, men ikke så simpelt at kalde:

For at oprette en Email-addresse-klasse med en predefineret uuid under
facetten employee_address_type udføres:

```bash
uuid=68d3d0ce-9fde-11ea-80b1-63a0ea904cea facet=employee_address_type bvn=test-moxklas titel=test-moxklas scope=EMAIL bash tools/moxklas.sh
```

Man kan provokere et dry-run ved at sætte en parameter efter hele linien

```bash
uuid=68d3d0ce-9fde-11ea-80b1-63a0ea904cea facet=employee_address_type bvn=test-moxklas titel=test-moxklas scope=EMAIL bash tools/moxklas.sh 42
```

Ovenstående sender et payload til lora, som opretter en klasse som
ligner nedenstående

```json
{
  "attributter": {
    "klasseegenskaber": [
      {
        "brugervendtnoegle": "test-moxklas",
        "titel": "test-moxklas",
        "omfang": "EMAIL",
        "virkning": {
          "from": "1930-01-01 12:02:32",
          "to": "infinity"
        }
      }
    ]
  },
  "tilstande": {
    "klassepubliceret": [
      {
        "publiceret": "Publiceret",
        "virkning": {
          "from": "1930-01-01 12:02:32",
          "to": "infinity"
        }
      }
    ]
  },
  "relationer": {
    "ansvarlig": [
      {
        "uuid": "8a2ae31b-422a-4374-b3a8-a2ed4ed23c63",
        "virkning": {
          "from": "1930-01-01 12:02:32",
          "to": "infinity"
        },
        "objekttype": "organisation"
      }
    ],
    "facet": [
      {
        "uuid": "332e8b38-68c3-4457-a5fb-3332216bb7a6",
        "virkning": {
          "from": "1930-01-01 12:02:32",
          "to": "infinity"
        }
      }
    ]
  }
}
```

## opus_import_all.sh

Anvendes under initialindlæsning af opus filer til det mellemliggende
trin, der er imellem den første komplette indlæsning og det tidspunkt,
hvor man bare indlæser filen fra natten før. Programmet forsøger at
indlæse alle opus-filer på en gang, og skulle det fejle markeres
programmet efter et ekstra fejlet gennemløb og backup skal derefter
indlæses.

Programmet kører som root med:

```bash
bash tools/opus_import_all.sh
```

`Opus_import_all.sh` anvender intensivt _settings/settings.json_. Se under
Opus-indlæsning i dokumentationen for at finde ud af hvilke settings,
der skal være defineret for indlæsning fra Opus.

Programmet slutter af med at fortælle hvilken dato, der tilhører hvilken
logfil, så man kan spole tilbage fra før fejlen opstod. 'At spole
tilbage' gøres så med [`tools/cron-restore.sh`](#cron-restoresh)

## prefixed_settings.sh

prefixed_settings sources og anvender to environment-variable, med
følgende defaults:

```bash
export SETTING_PREFIX=${SETTING_PREFIX:=crontab}
export CUSTOMER_SETTINGS=${CUSTOMER_SETTINGS:=/opt/settings/customer-settings.json}
```

Det omsætter værdier fra ovenstående konfigurationsfil, fjerner et
prefix og eksporterer værdierne

Med øverststående konfigurationsfil ville der efter en sourcing af
scriptet eksistere en nøgle SVC_USER i environment med værdien
USER@KOMMUNE.NET

## renew-keytab.sh

Dette interaktive program gør det muligt med lidt trial-and-error, når
man skal have frembragt en brugbar keytab-fil.

## update-dipex.sh

Dette program anvendes for at opdatere repositoriet og afhængigheder

## inspect_config.py

compare _settings_ file with `kommune-anddeby.json` and report what is
missing

## job-runner.d

Job-runner.d er konponenter, der loades af job-runneren Indtil nu loades
funktionen, der afvikler jobs herigennem ligesom nyeste tilføjelse:
tidsmålinger gør.

## terminate_orgfunc.py

Et tool, som terminerer _ALLE_ brugeres adresser og it-forbindelser. Det
er jo ikke særligt smart at køre sådan et, for så skal man oprette dem
allesammen igen. Det er imidlertid nødvendigt, hvis man er Viborg og
tidligere har brugt Skole-AD eller man ændrer feltmapning
