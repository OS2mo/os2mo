---
title: Integrationer
---

# Integrationer

## Integration til SD Løn

#### Indledning

Denne integration gør det muligt at hente og opdatere organisations- og
medarbejderoplysninger fra SD Løn til OS2MO.

#### Opsætning {#SD løn opsætning}

For at kunne afvikle integrationen, kræves loginoplysninger til SD-Løn,
som angives via `settings.json`, desuden anvendes en række felter som
angiver den lokale anvendelse af SD Løn. De påkrævede felter er:

-   `integrations.SD_Lon.institution_identifier`: Institution
    Identifer i SD.
-   `integrations.SD_Lon.sd_user`: Brugernavn (inklusiv foranstillet
    SY) til SD.
-   `integrations.SD_Lon.sd_password`: Password til SD.
-   `integrations.SD_Lon.base_url`: url til SD\'s webinterface.
-   `integrations.SD_Lon.global_from_date`: Virkningsdato for import
    på formen YYYY-MM-DD.
-   `integrations.SD_Lon.import.too_deep`: Liste over SD niveauer som
    anses som afdelingsniveau.
-   `integrations.SD_Lon.monthly_hourly_divide`: Skilleværdi for
    måneds/timelønnede.
-   `integrations.SD_Lon.job_function`: Feltet kan have en af to
    vædier: _EmploymentName_ eller
    _JobPositionIdentifier_, se yderligere nedenfor.

Desuden kan disse ikke-påkrævede felter angives:

-   `integrations.SD_Lon.employment_field`: Angiver et af MOs
    ekstrafelter på engagementer, hvis feltet angives vil
    integrationen skrive værdien af _EmploymentName_ i
    dette felt.
-   `integrations.SD_Lon.skip_employment_types`: En liste over værdier
    af _JobPositionIdentifier_ som ikke skal importeres.
    Hvis et engagement har en type fra listen, vil engagementet bliver
    ignoreret og ikke importeret i MO. Den tilhørende bruger vil dog
    blive oprettet, men vil optræde uden engagementer (med mindre
    personen har andre engagementer i kommunen).
-   `integrations.SD_Lon.no_salary_minimum_id`: Angiver en minimum
    påkrævet job position id for ulønnede medarbejdere. Alle ulønnede
    medarbejder med et id under dette minimum får aldrig deres
    engagement oprettet i MO.
-   `integrations.SD_Lon.fix_departments_root`: Angiver hvilken
    org_unit som skal udgøre rodenhed for importerede
    organisationenheder fra SD. Hvis tom anvendes MO\'s
    rodorganisation.

Hvis `integrations.SD_Lon.job_function` har værdien
_EmploymentName_ vil ansættelsers stillingsbetegnelser
bliver taget fra SDs felt af samme navn, som er et fritekstfelt.
Integrationen vil oprette en klasse for alle forekommende
stillingsbetegnelser. Benyttes i stedet værdien
_JobPositionIdentifier_ vil stillingsbetegelsen blive taget
fra dette felt i SD, som er et klassicieret felt.

Desuden er det nødvendigt at angive adressen på MO og LoRa i
variablerne:

-   `mox.base`
-   `mora.base`

#### Brug af integrationen

De forskellige underprogrammer kan alle tilgåes igennem ét hoved
program, nemlig `sd_cli`, ved kørsel af dette program vises
underprogrammerne, og deres parametre og formål kan udforskes. Kør blot:
`` ` python integrations/SD_Lon/sd_cli.py --help ``\`

#### Detaljer om importen

Udtræk fra SD Løn foregår som udgangspunkt via disse webservices:

-   `GetOrganization20111201`
-   `GetDepartment20111201`
-   `GetPerson20111201`
-   `GetEmployment20111201`

Det er desuden muligt at køre et udtræk som synkroniserer ændringer som
er meldt ind til SD Løn, men endnu ikke har nået sin virkningsdato:

-   `GetEmploymentChanged20111201`
-   `GetPersonChangedAtDate20111201`

Endelig er der også en implementering af løbende synkronisering af
ændringer i SD Løn, til dette anvendes udover de nævne webservices også:

-   `GetEmploymentChangedAtDate20111201`

Hvis der ønskes synkronisering af titler hørende til
`JobPositionIdentifier` anvendes desuden:

-   `GetProfession20080201`

Alle enheder fra SD importeres 1:1 som de er i SD, dog er det muligt at
flytte enheder uden hverken overenhed eller underenheder til en særlig
overenhed kaldet 'Forældreløse enheder'.

Medarbejdere som er ansat på niveauerne, angivet i
konfigurationensnøglen `integrations.SD_Lon.import.too_deep` rykkes op
til det laveste niveau højere end dette, og der oprettes en tilknytning
til den afdeling de befinder sig i i SD Løn.

Det er muligt at levere en ekstern liste med ledere, eller alternativt
at benytte SD Løns JobPositionIdentifier til at vurdere at en
medarbejder skal regnes som leder.

Medarbejdere i statuskode 3 regnes for at være på orlov.

Der importeres ingen adresser på medarbejdere. Disse kan eventuelt
hentes fra ad-integrationen.

Alle personer og ansættelser som kan returneres fra de ovennævnte
webservices importeres, både passive og aktive. Dette skyldes dels et
ønske om et så komplet datasæt som muligt, dels at SDs
vedligeholdsesservices gå ud fra, at alle kendte engagementer er i den
lokale model.

Den importerede startdato for engagementer er desværre ikke i alle
tilfælde korrekt, men repræsenterer for aktive ansættelser den dato hvor
den nuværende ansættelsesstatus indtrådte, da det ikke er muligt at
finde den korrekte oprindelige startdato uden et meget stort antal kald
mod SDs api. For afsluttede ansættelser vil sidste ændrede status være
lig med slutdatoen, i disse tilfælde anvendes i stedet SDs felt
EmploymentDate, som desværre er et fritekstfelt som i pricippet kan være
behæftet med fejl.

Postadresser på enheder hentes fa SD og valideres mod DAR. Hvis adressen
kan entydigt genkendes hos DAR, gemmes den tilhørende DAR-uuid på
enheden i MO.

Email adresser og p-numre importeres fra SD hvis disse findes for
enheden.

Vi importerer UUID'er på enheder fra SD til MO så enheder i MO og SD
har samme UUID.

Medarbejdere har ikke en UUID i SD, så her benyttes cpr som nøgle på
personen og ansættelsesnummeret som nøgle på engagementer. Brugerens
UUID i MO vil enten blive tilfældigt valgt, eller trukket fra eksternt
givet liste som matcher cpr-numre med ønskede UUID\'er i MO. Denne
funktionalitet kan anvendes til at sikre, at brugere ikke skifter UUID
hvis det bliver nødvendigt at genimporere fra SD. TIl hjælp til dette
findes et script (`cpr_uuid.py`) under exports som kan lave en sådan
liste fra en kørende instans af MO.

#### Engagementstyper

Alle medarbejdere som har et ansættelsesnummer udelukkende med tal,
tildeles en af to ansættelsestyper:

-   Medarbejder (månedsløn), hvis ansættelsesnummeret er lavere end
    værdien angivet i nøglen
    `integrations.SD_Lon.monthly_hourly_divide`.
-   Medarbejder (timeløn), hvis ansættelsesnummeret er højere.

Hvis medarbejderen har et ansættelsesnummer, som ikke udelukkende er
tal, vil ansættelsestypen blive bestemt fra personens
`JobPositionIdentifier`, hvor der i MO er oprettet klasser der svarer
til disse værdier. Den tilknyttede tekst til hver klasse kan sættes med
et hjælpeværktøj (beskrevet nedenfor).

#### Primær ansættelse

SD Løn har ikke et koncept om primæransættelse, men da AD integrationen
til MO har behov for at kunne genkende den primære ansættelse til
synkronisering, bestemmes dette ud fra en beregning:

En medarbejders primære ansættelse regnes som den ansættelse som har den
største arbejdstidsprocent, hvis flere har den samme, vælges ansættelsen
med det laveste ansættelsenummer. Hvis en ansættelse er manuelt angivet
til at være primær, vil denne ansættelse altid regnes som primær.

Ansættelser i SDs statuskode 0 kan anses som primære hvis ingen andre
ansættelser er primære (altså, medarbejderen har udelukkende ansættelser
i statuskode 0). Hvis en medarbejder har ansættelser i både status 0 og
status 1, vil en ansættelse i status 1 blive beregnet til primær og
status 0 ansættelsen vil ikke blive betragtet som primær.

Informationen om primæransætelse opretholdes i MOs facet `primary_type`,
som ved import af SD altid populeres med disse fire klasser:

-   Manuelt primær ansættelse: Dette felt angiver at en ansættelse
    manuelt er sat til at være primær
-   Ansat: Angiver en medarbejders beregnede primære ansættelse.
-   Ansat - Ikke i løn: Angiver SD Løns statuskode 0. Hvis ingen andre
    primære ansætelser findes vil denne type regnes som primær.
-   Ikke-primær ansat: Angiver alle andre ansættelser for en
    medarbejder.

Manuelt primær optræder ikke direkte i imports, men kan sættes manuelt
fra MOs GUI. De øvrige primærklasser håndteres af SD integrationen, og
må ikke sættes manuelt.

En medarbejder skifter ikke ansættelsestype selvom vedkommende fratræder
sit engagement. En ansættelses aktuelle status angives i stedet via MOs
start- og slutdato. Er slutdato\'en i fortiden, er vedkommende ikke
længere ansat og vil i MOs gui fremgå i fanen fortid. Er en medarbejers
startdato i fremtiden, er personen endnu ikke tiltrådt, og fremgår i
fanen fremtid. 

#### Håndtering af enheder

SDs API til udlæsning af organisationsenheder er desværre meget
mangelfuldt, og integrationen har derfor en yderst primitiv håndtering
af enheder:

Ved førstegangsimport vil alle aktuelle enheder blive importeret med den
virkningstid som oplyses af kald til `GetDepartment`. Dette er dog ikke
nødvendigvis den egentlige oprettelsesdato for enheden og der vil være
tilfælde hvor startdato er enten for tidlig eller for sen i forhold til
den reele startdato for enheden.

Der findes ikke nogen differentiel service fra SD som oplyser om
ændringer i organisationen, og der sker derfor som udgangspunkt ingen
synkronisering af enhedstræet mellem SD og MO. I de tilfælde hvor der
ansættes en medarbejder i en enhed som enten ikke eksisterer i MO, eller
hvor enhedens virkningstid er kortere end ansættelsens start, vil MO
oprette enheden eller forlænge dens virkningstid så den bliver i stand
til at rumme engagementet.

Da det er meget vanskeligt at hente historisk information om enheder,
vil MO oprette eller rette enheden med udgangspunkt i de data som gælder
for enheden på importdagen. Enheden vil herefter fremgå af MO som om den
altid har haft det navn og den placering den har på importdagen.

Hvis en enhed omdøbes eller flyttes i SD, vil denne ændring ikke fremgå
af MO, med mindre der foretages en manuel synkronisering, dette kan
gøres ved at at afvikle scriptet `fix_departments.py`, hvis kommunen
ønsker det, er det muligt at slå en funktionalitet til som tillader
denne afvikling via en knap i MOs front-end.

Når `fix_departments.py` afvikles på en enhed, vil enheden og dens
forældres navne og hierakiske placering blive hentet fra SD og den nye
tilstand vil blive skrevet til MO med evig virkning både bagud og fremad
i tid. Hvis enhedens niveau er angivet i
`integrations.SD_Lon.import.too_deep` til at være et afdelingsnieau vil
integrationen desuden genberegne placeringen de engagementer som SD har
registreret på enheden som vil blive flyttet opad til det laveste
strukturniveau i undertræet. Denne flytning vil få en registreret
virkningstid som er lig med den dag `fix_departments.py` blev afviklet.

Det skal altså understreges, at MOs historiske information om enhder
**ikke** er retvisende. Det betyder dels, at det ikke er muligt at se
tidligere navne på enheden, men mere bemærkelsesværdigt er det, at det
ikke er muligt at se tidligere placeringer i organisationshierakiet. Det
betyder altså, at enheden potentielt tidligere kan have været placeret
et helt andet sted i organisationen. Hvis en medarbejder har været ansat
i en enhed mens enheden er er blevet flyttet, vil dette ikke fremgå at
medarbejderens fortidsfane, da engagementets tilknytning til enheden
ikke har været ændret. Det er derfor vigtigt at holde sig for øje, at
selvom en medarbejders historik ikke indeholder ændringer i
organisatorisk placering, kan vedkommende godt være flyttet alligevel i
form af eventuelle flytninger af hele enheden.

I tilknytning til SD importen, er der i øjeblikket ved at blive
implementeret en funktionalitet som via SD Løns beskedservice kan
oprette enheder i SD når de oprettes i MO. Med denne service vil den
fremadrettede historik for enheder fra idriftsættelsen af servicen,
blive korrekt.

#### Hjælpeværktøjer

Udover de direkte værktøjer til import og løbende opdateringer, findes
et antal hjælpeværktøjer:

-   `test_sd_connectivity.py`: Et lille værktøj som tester at den
    lokale `settings.json` indeholder de nødvendige nøgler. Desuden
   tester programmet for en række potentielle fejl, eksempevis om
    felterne har gyldige værdier og om det er muligt at kontakte SD
    Løn med de angivne brugeroplysinger.
-   `test_mo_against_sd.py`: Et værktøj som tester udvalgte personers
    engagementer mod SD løn of checker at MO og SD er løn har samme
    opfattelse af om personens engagementer er aktive eller ej.
    Værktøjet kan anvendes på et enkelt person eller på alle personer
    som har ansættelse i en bestemt enhed (alle engagementer for disse
    personer vil blive tjekket også dem i andre enheder). Værktøjet
    anvender opslag til SDs API\'er og kan derfor kun anvendes i
    begrænset omfang, og af samme årsag er der ikke implementeret
    mulighed for at tjekke alle ansatte.
-   `calculate_primary.py`: Et værktøj som er i stand til at
    gennemløbe alle ansættelser i MO og afgøre om der for alle
    medarbejdere til alle tider findes et primærengagement. Værktøjet
    er også i stand til at reparere en (eller alle) ansættelser hvor
    dette ikke skulle være tilfældet. Dette modul importeres desuden
    af koden til løbende opdatering, hvor den bruges til at genberegne
    primæransættelser når der skær ændringer i en medarbejders
    ansættelsesforhold. Værktøjet er udstyret med et
    kommandolinjeinterface, som kan udskrive en liste over brugere
    uden primærengagement (eller med mere end et) samt opdatere
    primære engagementer for en enkelt bruger eller for alle brugere.
-   `sync_job_id.py`: Dette værktøj kan opdatere den tekst som vises i
    forbindelse med ansættelsestyper og stillingsbetegnelser som er
    knyttet til SDs `JobPositionIdentifier`. Efter den initielle
    import vil klassens navn modsvare talværdien i SD, og dette
    værktøj kan efterfølgende anvendes til at enten at synkronisere
    teksten til den aktuelle værdi i SD eller til en valgfri tekst.
-   `fix_departments.py`: En implementering af logikken beskrevet
    under afsnitet [Håndtering af enheder](/data-import-export/integrations.html#handtering-af-enheder). Udover anvendelsen i den
    løbende integrationen, indeholder programmet også et
    kommandolinjeværktøj som kan anvendes til manuelt at fremprovokere
    en synkronisering af en enhed (med tilhørende overenheder) til den
    nuværende tilsand af SD Løn. Hvis værktøjet afvikles på en enhed
    som anses for at være Afdelings-niveau, vil det opdatere alle
    enhedens ansættelser, så engagementerne flyttes til de korrekte
    NY-niveauer (som kan være ændret, hvis afdelingen er flyttet).
-   `sd_fix_organisation.py`: Tidligere forsøg på at håndtere
    opdateringer af enheder. Scriptet findes nu kun som basis for
    evenutelle senere forsøg på at lave et fuldt historisk import af
    enhedstræet.

#### Tjekliste for fuldt import

Overordnet foregår opstart af en ny SD import efter dette mønster:

1.  Kør importværktøjet med fuld historik (dette er standard opførsel).
2.  Kør en indledende ChangedAt for at hente alle kendte fremtidige
    ændringer og intitialisere den lokale database over kørsler.
3.  Kør sd_changed_at.py periodisk (eksempelvis dagligt).
4.  Eventuelt synkronisering af stillingsbetegnelser.
5.  Eventuelt synkronisering fra AD.

## 1. Kør importværktøjet

En indledende import køres ved at oprette en instans af [ImportHelper]()

``` python
importer = ImportHelper(
    create_defaults=True,
    mox_base=MOX_BASE,
    mora_base=MORA_BASE,
    store_integration_data=False,
    seperate_names=True
)
```

Hverken importen eller efterfølgende synkronisering med ChangedAt
anvender integrationsdata, og det er derfor valgfrit om vil anvende
dette.

Importen kan derefter køres med disse trin:

``` python
sd = sd_importer.SdImport(
    importer,
    ad_info=None,
    manager_rows=None
)

sd.create_ou_tree(
    create_orphan_container=False,
    sub_tree=None,
    super_unit=None
)
sd.create_employees()

importer.import_all()
```

Hvor der i dette tilfælde ikke angives ledere eller en AD integration.
Disse to punkter diskuteres under punkterne [Ledere i SD Løn](/data-import-export/integrations.html#ledere-i-sd-lon) og [AD
Integration til SD Import]().

Parametren _sub_tree_ kan angives med en uuid og det vil så
fald kun blive undertræet med den pågældende uuid i SD som vil blive
importeret. Det er i øjeblikket et krav, at dette træ er på rod-niveau i
SD.

Importen vil nu blive afviklet og nogle timer senere vil MO være
populeret med værdierne fra SD Løn som de ser ud dags dato.

## 2. Kør en indledende ChangedAt

I SD Løn importeres i udgangspunktet kun nuværende og forhenværende
medarbejdere og engagementer, fremtidige ændringer skal hentes i en
seperat process. Denne process håndteres af programmet
[sd_changed_at.py]{.title-ref} (som også anvendes til efterfølgende
daglige synkroniseringer). Programmet tager i øjeblikket desværre ikke
mod parametre fra kommandolinjen, men har brug for at blive rettet
direkte i koden, hvor parametren [init]{.title-ref} i
[\_\_main\_\_]{.title-ref} delen af programmet skal sættes til
[True]{.title-ref}.

Programet kan nu afvikles direkte fra kommandolinjen

python3 sd_changed_at.py

Herefter vil alle kendte fremtidige virkninger blive indlæst til MO.
Desuden vil der blive oprettet en sqlite database med en oversigt over
kørsler af changed_at (se [ChangedAt.db]()) .

## 3. Kør sd_changed_at.py periodisk

Daglige indlæsninger foregår som nævnt også med programmet
[sd_changed_at.py]{.title-ref}, hvilket foregår ved at sætte
[init]{.title-ref} til [False]{.title-ref} og køre programmet uden
yderligere parametre. Programmet vil så spørge [ChangedAt.db]() om
hvorår der sidst blev synkroniseret, og vil herefter synkronisere
yderligere en dag frem i tiden.

## 4. Eventuelt synkroisering af stillingsbetegnelser

Hvis nøglen \* `integrations.SD_Lon.job_function` er valgt til
[JobPositionIdentifier]{.title-ref}, vil alle stillingsbetegnelser nu
være talværdier fra SD Løns klassificerede stillinger, for at få læsbare
stillinger skal disse synkroniseres ved hjælp af værktøjet
`sync_job_id.py` (se ovenfor).

## 5. Eventuelt synkronisering fra AD

Hvis det ønskes at synkronisere adresser fra AD, skal scriptet
`ad_sync.py` afvikles, settings til dette er beskrevet i afsnittet
[Integration til Active Directory]()

#### Ledere {#Ledere i SD Løn}

SD Løn indeholder som udgangspunkt ikke information om, hvorvidt en
ansat er leder. Det er derfor ikke muligt importere informaion om ledere
direke fra dataudtrækket. Der er dog implementeret to metoder til at
angive lederinformation:

> 1.  Inddirekte via [JobPositionIdentifier]{.title-ref}
>
>     Det er muligt at angive et antal værdier for
>     [JobPositionIdentifier]{.title-ref} som anses for at være ledere.
>     Disse er i øjeblikket hårdkodet til værdierne 1030, 1040 og
>
>     1050\. Hvis intet andet angives vil disse medarbejdere anses for
>     at være ledere i de afdelinger de er ansat i.
>
> 2.  Via eksternt leveret fil.
>
>     Integrationen understøtter at blive leveret en liste af ledere som
>     kan importeres fra en anden kilde. Denne liste angives med
>     parametren `manager_rows` ved opstart af importeren. Formatet for
>     denne anivelse er
>
>     ``` python
>     manager_rows = [
>
>     {'cpr': leders_cpr_nummer,
>      'ansvar': 'Lederansvar'
>      'afdeling': sd_enhedskode
>     }
>     ...
>     ]
>     ```
>
>     Hvor lederansvar er en fritekststreng, alle unikke værdier vil
>     blive oprettet under facetten `responsibility` i Klassifikation.
>     Det er i den nuværende udgave ikke muligt at importere mere end et
>     lederansvar pr leder.

#### AD Integration til SD import {#AD Integration til SD import}

SD Importen understøtter at anvende komponenten [Integration til Active
Directory]() til at berige objekterne fra SD Løn med information fra
Active Directory. I de fleste tilfælde drejer dette sig som minimum om
felterne `ObjectGuid` og `SamAccountName` men det er også muligt at
hente eksempelvis telefonnumre eller stillingsbetegnelser.

Feltet `ObjectGuid` vil i MO blive anvendt til UUID for det tilhørende
medarbejderobjekt, hvis ikke UUID\'en allerede er givet fra en ekstern
kilde. `SamAccountName` vil blive tilføjet som et brugernavn til IT
systemet Active Direkctory for den pågældende bruger.

#### run_db.sqlite {#ChangedAt.db}

For at holde rede på hvornår MO sidst er opdateret fra SD Løn, findes en
SQLite database som indeholder to rækker for hver færdiggjort kørsel.
Adressen på denne database er angivet i settings med nøglen
`integrations.SD_Lon.import.run_db`.

Programmet `db_overview.py` er i stand til at læse denne database.

Ved starten af alle changedAt kørsler, skrives en linje med status
`Running` og efter hver kørsel skrives en linje med status
`Update finished`. En changedAt kørsel kan ikke startes hvis den nyeste
linje har status `Running`, da dette enten betyder at integrationen
allerede kører, eller at den seste kørsel fejlede.

### Integration til OPUS Løn

#### Indledning

Denne integration gør det muligt at hente og opdatere organisations- og
medarbejderoplysninger fra XML dumps fra OPUS Løn til OS2MO

#### Opsætning

Der er tre muligheder for læsning af opusfiler.

-   Lokalt: Opusfilerne kopieres direkte til serverne. Stien
    specificeres i settings.json som
    `integrations.opus.import.xml_path`. Som regel er den
    `/opt/customer/`.

\* Windows share. Filerne kan læses fra et windows share med SMB
protokollen. Denne anvendes hvis `integrations.opus.smb_host` er udfyldt
i settings.json. Bemærk den skal udfyldes som `IP/sti`. Kræver desuden
en bruger med rettighed til at læse filerne og credentials sættes i
settings.json som `integrations.opus.smb_user` og
`integrations.opus.smb_password`. \* Google cloud storage: Filerne kan
læses direkte fra google cloud storage. Dette kræver en service konto
der er sat op på serveren med rettigheder til at læse filerne. Derudover
er det kun `integrations.opus.gcloud_bucket_name` der skal udfyldes i
settings.json med det navn som storage enheden har i google cloud.

Fælles for dem alle gælder at de enkelte dumps forventes at være
navngivet systematisk som: `ZLPE<dat0 + tid>_delta.xml`

Eksempelvis `ZLPE20190902224224_delta.xml`.

#### Nuværende implementeringslogik for import fra Opus:

> -   Data indlæses i form at et xml-dump.
> -   Hvis data indeholder information om enhedstyper, oprettes disse
>     enhedstyper som klasser, hvis ikke, får alle enheder typen
>     `Enhed`.
> -   SE-, CVR-, EAN-, p-numre og telefon indlæses på enheder, hvis
>     disse oplysninger er tilgængelige.
> -   Hvis data indeholder postadresser på enheder eller medarejdere,
>     slås disse adresser op på DAR, og hvis det er muligt at få en
>     entydigt match, gemmes DAR-uuid\'en på enheden eller personen.
>     Adresser med adressebeskyttelse importeres ikke.
> -   Telefon og email importeres for medarbejdere, hvis de findes i
>     data.
> -   Ansættelsestyper og titler oprettes som klasser og sættes på de
>     tilhørende engagementer. Ansættelsestypen læses fra feltet
>     `workContractText`, hvis dette eksisterer, hvis ikke får
>     medarbejderen typen `Ansat`.
> -   Information om ledere importeres direkte fra data, de to
>     informationer `superiorLevel` og `subordinateLevel` konkateneres
>     til et lederniveau.
> -   Information om roller importeres direkte fra data.

#### IT-Systemer

En import fra OPUS vil oprette IT-systemet \'Opus\' i MO. Alle
medarbejdere som har en værdi i feltet `userId` vil få skrevet deres
OPUS brugernavn på dette IT-system.

#### AD-Integration

OPUS Importen understøtter at anvende komponenten [Integration til
Active Directory]() til at berige objekterne fra OPUS med information
fra Active Directory. I øjebliket er det muligt at importere felterne
`ObjectGuid` og `SamAccountName`.

Hvis AD integrationen er aktiv, vil importeren oprette IT-systemet
\'Active Directory\' og oprette alle brugere der findes i AD med
brugernavnet fundet i `SamAccountName`. Brugere med en AD konto vil
blive oprettet med deres AD `ObjectGuid` som UUID på deres brugerobjekt,
med mindre de er angivet i en cpr-mapning.

#### cpr-mapning

For at kunne lave en frisk import uden at få nye UUID\'er på
medarbejderne, er det muligt at give importen adgang til et csv-udtræk
som parrer cpr-numre med UUID\'er. Disse UUID\'er vil altid få forrang
og garanterer derfor at en medarbejder får netop denne UUID, hvis
vedkommendes cpr-nummer er i csv-udtrækket. Udtrækket kan produceres fra
en kørende instans af MO ved hjælp ved værktøkjet `cpr_uuid.py`, som
findes under `exports`.

#### Primær ansættelse

I XML dumps fra Opus findes ikke et koncept om primæransættelse, men da
AD integrationen til MO har behov for at kunne genkende den primære
ansættelse til synkronisering, bestemmes dette ud fra en beregning:

Den mest afgørende komponent af beregningen foregår på baggrund af
ansættelestypen, hvor en liste af uuid\'er i `settings.json` bestemmer
hvilke ansættelstyper der anses for at være mest primære. Hvis flere
engagementer har den samme ansættelsestype, vælges ansættelsen med det
laveste ansættelsenummer. Hvis en ansættelse er manuelt angivet til at
være primær, vil denne ansættelse altid regnes som primær.

Informationen om primæransætelse opretholdes i MOs facet `primary_type`,
som ved import fra Opus XML altid populeres med disse tre klasser:

> -   Manuelt primær ansættelse: Dette felt angiver at en ansættelse
>     manuelt er sat til at være primær
> -   Ansat: Angiver en medarbejders beregnede primære ansættelse.
> -   Ikke-primær ansat: Angiver alle andre ansættelser for en
>     medarbejder.

Manuelt primær optræder ikke direkte i imports, men kan sættes manuelt
fra MOs GUI. De øvrige primærklasser håndteres af Opus integrationen, og
må ikke sættes manuelt.

En medarbejder skifter ikke ansættelsestype selvom vedkommende fratræder
sit engagement. En ansættelses aktuelle status angives i stedet via MOs
start- og slutdato. Er slutdato\'en i fortiden, er vedkommende ikke
længere ansat og vil i MOs gui fremgå i fanen fortid. Er en medarbejers
startdato i fremtiden, er personen endnu ikke tiltrådt, og fremgår i
fanen fremtid.

#### Anvendelse af integrationen

For at anvende integrationen kræves udover de nævnte xml-dumps, at der
oprettes en gyldig konfiguration i `settings.json`. De påkrævede nøgler
er:

> -   `mox.base`: Adressen på LoRa.
>
> -   `mora.base`: Adressen på MO.
>
> -   `integrations.opus.import.run_db`: Stien til den database som
>     gemmer information om kørsler af integrationen. Hvis integrationen
>     skal køre som mere end et engangsimport har denne fil en vigtig
>     betydning.
>
> -   `municipality.name`: Navnet på kommunen.
>
> -   `crontab.SAML_TOKEN`: saml token til forbindelse til OS2MO
>
> -   
>
>     `integrations.opus.skip_employees`: Optionelt.
>
>     :   Kan sættes til [true]{.title-ref} for kun at læse
>         organisationsenheder fra opus-filerne.

Til at hjælpe med afviklingen af importen, findes en hjælpefunktion i
`opus_helpers.py` som afvikler selve importen og initialiserer databasen
i `opus.import.run_db` korrekt. Dette modul forventer at finde en
cpr-mapning og vil fejle hvis ikke filen `settings/cpr_uuid_map.csv`
eksisterer.

## Førstegangsimport (initialindlæsning)

Hvis den nuværende import er den første, findes der i reglen ikke nogen
mapning, og der må så oprettes en tom fil i dens sted
(`settings/cpr_uuid_map.csv`)

før kaldet af initialindlæsning skal SAML_TOKEN være defineret i
environment. Det kan man få igennem at source (dotte)
tools/prefixed_settings.sh når man, som det sig hør og bør, er placeret
i roden af directoriet os2mo-data-import-and-export.

Ligeledes må databasen, som er defineret i `opus.import.run_db` ikke
findes og lora-databasen skal være tom.

#### Løbende opdatering af Opus data i MO

Der er skrevet et program som foretager løbende opdateringer til MO
efterhåden som der sker ændringer i Opus data. Dette foregår ved, at
integrationen hver gang den afvikles, kigger efter det ældste xml-dump
som endnu ikke er importeret og importerer alle ændringer i dette som er
nyere end den seneste importering. Et objekt regnes som opdateret hvis
parameteren `lastChanged` på objektet er nyere end tidspunktet for det
senest importerede xml-dump. Alle andre objekter ignoreres.

Hvis et objekt er nyt, foretages en sammenligning af de enkelte felter,
og de som er ændret, opdateres i MO med virkning fra `lastChanged`
datoen. En undtagelse for dette er engagementer, som vil blive oprettet
med virkning fra `entryDate` datoen, og altså således kan oprettes med
virkning i fortiden.

Også opdateringsmodulet forventer at finde en cpr-mapning, som vil blive
anvendt til at knytte bestemte UUID\'er på bestemte personer, hvis disse
har været importeret tidligere. Denne funktionalitet er nyttig, hvis man
får brug for at re-importere alle Opus-data, og vælger at arbejde sig
igennem gamle dumps for at importere historik. I daglig brug vil
mapningen ikke have nogen betydning, da oprettede brugere her altid vil
være nye.

#### Opdatering af enkelte brugere

Skulle det af den ene eller den anden grund ske, at en bruger ikke er
importeret korrekt, er det muligt at efterimportere denne bruger.
Funktionen er endnu ret ny og det tilrådes derfor altid at tage en
backup af databasen før den benyttes. Funktionen fungerer ved at hente
historiske data fra gamle xml-dumps, og det er derfor en forudsætning,
at disse dumps stadig er til rådighed. For at synkronisere en enkelt
medarbejder anvedes disse kommandolinjeparametre:

-   `--update-single-user`: Ansættelsesnummer på den relevante
    medarbejder
-   `days`: Antal dage bagud integrationen skal søge.

## Nuværende begrænsninger omkring re-import

> -   IT-systemer tilknyttes kun i forbindelse med oprettelsen af en
>     medarbejder, de tildeles uendelig virkning og nedlægges aldrig.
> -   Ændringer i roller håndteres kun ved ændringer i slutdatoer, det
>     antages at startdatoer ikke ændres.
> -   Tomme ændringer på en leder opdages ikke, så der opstår en ekstra
>     række på lederobjekter hvis en leder ændres. Den resulterende
>     tilstand er korrekt, men indeholder en kunstig skæringsdato i sin
>     historik.
> -   Der oprettes ikke automatisk nye engagementstyper, alle
>     engagementer forventes at have en type som blev oprettet ved
>     førstegangsimporten.
> -   Der oprettes ikke automatisk nye lederniveauer, alle ledere
>     forventes at have et niveau som eksisterede ved
>     førstegangsimporten.

#### run_db.sqlite

For at holde rede på hvornår MO sidst er opdateret fra Opus, findes en
SQLite database som indeholder to rækker for hver færdiggjort kørsel.
Adressen på denne database er angivet i `settings.json` under nøglen
`opus.import.run_db`.

Programmet `db_overview.py` er i stand til at læse denne database og
giver et outut som dette:

    id: 1, dump date: 2019-09-02 22:41:28, status: Running since 2019-11-19 08:32:30.575527
    id: 2, dump date: 2019-09-02 22:41:28, status: Import ended: 2019-11-19 08:55:32.455146
    id: 3, dump date: 2019-09-03 22:40:12, status: Running diff update since 2019-11-19 10:18:35.859294
    id: 4, dump date: 2019-09-03 22:40:12, status: Diff update ended: 2019-11-19 10:19:15.806079
    id: 5, dump date: 2019-09-04 22:40:12, status: Running diff update since 2019-11-19 10:19:16.006959
    id: 6, dump date: 2019-09-04 22:40:12, status: Diff update ended: 2019-11-19 10:19:48.980694
    id: 7, dump date: 2019-09-05 22:40:12, status: Running diff update since 2019-11-19 10:19:49.187977
    id: 8, dump date: 2019-09-05 22:40:12, status: Diff update ended: 2019-11-19 10:20:23.547771
    id: 9, dump date: 2019-09-06 22:40:13, status: Running diff update since 2019-11-19 10:20:23.745032
    id: 10, dump date: 2019-09-06 22:40:13, status: Diff update ended: 2019-11-19 10:20:54.931163
    id: 11, dump date: 2019-09-09 22:40:12, status: Running diff update since 2019-11-19 10:20:55.123478
    id: 12, dump date: 2019-09-09 22:40:12, status: Diff update ended: 2019-11-19 10:21:35.481189
    id: 13, dump date: 2019-09-10 22:40:12, status: Running diff update since 2019-11-19 10:21:35.682252
    id: 14, dump date: 2019-09-10 22:40:12, status: Diff update ended: 2019-11-19 10:22:12.298526
    id: 15, dump date: 2019-09-11 22:41:48, status: Running diff update since 2019-11-19 10:22:12.496829
    id: 16, dump date: 2019-09-11 22:41:48, status: Diff update ended: 2019-11-19 10:22:45.317372
    id: 17, dump date: 2019-09-12 22:40:12, status: Running diff update since 2019-11-19 10:22:45.517679
    id: 18, dump date: 2019-09-12 22:40:12, status: Diff update ended: 2019-11-19 10:23:20.548220
    id: 19, dump date: 2019-09-13 22:40:14, status: Running diff update since 2019-11-19 10:23:20.744435
    id: 20, dump date: 2019-09-13 22:40:14, status: Diff update ended: 2019-11-19 10:23:51.416625
    id: 21, dump date: 2019-09-16 22:40:12, status: Running diff update since 2019-11-19 10:23:51.610555
    id: 22, dump date: 2019-09-16 22:40:12, status: Diff update ended: 2019-11-19 10:24:44.799932
    id: 23, dump date: 2019-09-17 22:40:12, status: Running diff update since 2019-11-19 10:24:45.000445
    id: 24, dump date: 2019-09-17 22:40:12, status: Diff update ended: 2019-11-19 10:25:25.651491
    (True, 'Status ok')

Ved starten af alle opus_diff_import kørsler, skrives en linje med
status `Running` og efter hver kørsel skrives en linje med status
`Diff update ended`. En kørsel kan ikke startes hvis den nyeste linje
har status `Running`, da dette enten betyder at integrationen allerede
kører, eller at den seneste kørsel fejlede.

#### Filtrering af organisationsenheder

Den valgfrie nøgle `integrations.opus.units.filter_ids` kan sættes for
at filtrere udvalgte organisationenheder og deres tilhørende
underliggende organisationsenheder fra, før selve importen kører.

Nølgen skal være en liste indeholdende OPUS ID\'er for de
organisationsenheder, som ønskes filtreret fra. OPUS ID findes i OPUS
filen `<orgUnit id="350" client="813" lastChanged="2020-09-16">`

### Integration til Active Directory {#Integration til Active Directory}

#### Indledning

Denne integration gør det muligt at læse information fra en lokal AD
installation med henblik på at anvende disse informationer ved import
til MO.

#### Opsætning

For at kunne afvikle integrationen kræves en række opsætninger af den
lokale server.

Integrationen går via i alt tre maskiner:

> 1.  Den lokale server, som afvikler integrationen (typisk MO serveren
>     selv).
> 2.  En remote management server som den lokale server kan kommunikere
>     med via Windows Remote Management (WinRM). Denne kommunikation
>     autentificeres via Kerberos. Der findes en vejledning til
>     opsætning med kerberos her:
>     <https://os2mo.readthedocs.io/en/latest/_static/AD%20-%20OS2MO%20ops%C3%A6tnings%20guide.pdf>
>     Alternativt kan der autentificeres med ntlm over https. Denne
>     opsætning beskrives herunder.
> 3.  AD serveren.

Når integrationen er i drift, genererer den PowerShell kommandoer som
sendes til remote management serveren som afvikler dem mod AD serveren.
Denne omvej hænger sammen med, at MO afvikles fra et Linux miljø,
hvorimod PowerShell kommunikation med AD bedst afvikles fra et Windows
miljø.

For at kunne afvikle integrationen kræves der udover den nævnte
opsætning af enten Kerberos eller ntlm, at AD er sat op med cpr-numre på
medarbejdere samt en servicebruger som har rettigheder til at læse dette
felt. Desuden skal et antal variable være sat i `settings.json`

Det er muligt at anvende flere AD til udlæsning af adresser og
itsystemer til OS2MO Således er `integrations.ad` i `settings.json` et
array med følgende indbyggede betydning:

> -   Første AD i listen (index 0) anvendes til skrivning (hvis
>     skrivning er aktiveret) og til integrationer, som endnu ikke er
>     forberedt for flere ad\'er.
> -   Alle AD\'er anvendes af ad_sync til opdatering af og skabelse af
>     adresser, itsystemer

## Opsætning af ntlm over https

For at kunne autentificere med ntlm over https kræver det at
settingsfilen indeholder brugernavn og password til en systembruger fra
et domæne (modsat lokalt oprettet bruger). Derudover skal det i
settings.json specificeres at metoden skal være \'ntlm\'. Se bekrivelsen
af parametre herunder. Brugeren skal desuden have
administratorrettigheder på windowsserveren, samt rettigheder til at
læse og evt. skrive i AD. Dette gælder også feltet der indeholder CPR
numre der kan være indstillet til \'confidential\'. I så fald skal
rettigheden gives gennem programmet ldp.

SSL certifikatet skal dannes via en windows server der er konfigureret
som CA server. Det er en forudsætning at det oprettes med: [Intended
purpose: Server Authentication]{.title-ref} Fra WinRM serveren åbnes
\"certificate management\" hvori der kan anmodes om et nyt certifikat.
Her skal som minimum [Common Name]{.title-ref} udfyldes med serverens
hostnavn. Under det nye certifikats \'Egenskaber\' findes dens
\'CertificateThumbprint\'.

Hvis der allerede er opsat en winrm listener på HTTPS, skal den fjernes
først:

[winrm remove
winrm/config/Listener?Address=\*+Transport=HTTPS]{.title-ref}

Hvis ikke det allerede er sat op kan winrm sættes til at bruge https
med:

[winrm quickconfig -transport:https]{.title-ref}

Konfigurer WinRM til at bruge certifikatet:

[winrm set winrm/config/Listener?Address=\*+Transport=HTTPS
\@{Hostname=\"hostname\";
CertificateThumbprint=\"02E4XXXXXXXXXXXXXXXXXXXXXXXXXX\"}]{.title-ref}

Derefter skal winrm sættes op til at tillade NTLM, men ikke ukrypteret:

``` powershell
winrm set winrm/config/service/auth '@{Negotiate="true"}'
winrm set winrm/config/service '@{AllowUnencrypted="false"}'
```

Der kan også være behov for at åbne en port i firewall med:

[netsh advfirewall firewall add rule name=\"WinRM-HTTPS\" dir=in
localport=5986 protocol=TCP action=allow]{.title-ref}

Nu skulle der være adgang til winrm med ntlm, krypteret med https, via
port 5986.

## Fælles parametre

> -   `integrations.ad.winrm_host`: Hostname på remote mangagent server

## For hvert ad angives

> -   `search_base`: Search base, eksempelvis
>     \'OU=enheder,DC=kommune,DC=local\'
>
> -   `cpr_field`: Navnet på feltet i AD som indeholder cpr nummer.
>
> -   `cpr_separator`: Angiver en eventuel separator mellem fødselsdato
>     og løbenumre i cpr-feltet i AD. Hvis der ikke er en separator,
>     angives en tom streng.
>
> -   `sam_filter`: Hvis denne værdi er sat, vil kun det være muligt at
>     cpr-fremsøge medarbejder som har denne værdi foranstillet i
>     SAM-navn. Funktionen muliggør at skelne mellem brugere og
>     servicebrugere som har samme cpr-nummer.
>
> -   `caseless_samname`: Hvis denne værdi er `true` (Default) vil
>     sam_filter ikke se forskel på store og små bogstaver.
>
> -   `system_user`: Navnet på den systembruger som har rettighed til at
>     læse fra AD.
>
> -   `password`: Password til samme systembruger.
>
> -   `properties`: Liste over felter som skal læses fra AD. Angives som
>     en liste i json-filen.
>
> -   `method`: Metode til autentificering - enten ntlm eller kerberos.
>     Hvis denne ikke er angivet anvendes kerberos.
>
> -   `servers` - domain controllere for denne ad.
>
> -   
>
>     `pseudo_cprs`: Liste af ekstra startværdier for cpr-numre. Bruges til at læse AD brugere med cprnummer
>
>     :   der starter med et tal der ikke er mellem 01 og 31 -
>         Fiktive/systembrugere)

## Test af opsætningen

Der følger med AD integrationen et lille program, `test_connectivity.py`
som tester om der kan læses fra eller skrives til AD, og dermed at
autentificering er konfigureret korrekt. Programmet afvikles med en af
to parametre:

> -   `--test-read-settings`
> -   `--test-write-settings`

En test af læsning foregår i flere trin:

:   -   Der testes for om Remote Management serveren kan nås og
        autentificeres med metoden specificeret i settings - enten
        Kerberos (standard) eller med ntlm.
    -   Der testes om det er muligt af afvikle en triviel kommando på AD
        serveren.
    -   Der testes for, at en søgning på alle cpr-numre fra 31. november
        returnerer nul resultater.
    -   Der testes for, at en søging på cpr-numre fra den 30. i alle
        måneder returnerer mindst et resultat. Hvis der ikke returneres
        nogen, er fejlen sandsynligvis en manglende rettighed til at
        læse feltet med cpr-nummer i AD. Dette kan bla. skyldes at
        rettigheder til confidential attributes skal sættes i ldp
        programmet.
    -   Der testes om de returnerede svar indeholder mindst et eksempel
        på disse tegn: æ, ø, å, @ som en test af at tegnsættet er
        korrekt sat op.

En test af skrivning foregår efter denne opskrift:

> -   Der testes for om de nødvendige værdier er til stede i
>     `settings.json`, det drejer sig om nøglerne:
>
>     -   `integrations.ad.write.uuid_field`: AD feltet som rummer MOs
>         bruger-UUID
>
>     \* `integrations.ad.write.level2orgunit_field`: AD feltet hvor MO
>     skriver den primære organisatoriske gruppering (direktørområde,
>     forvaltning, etc.) for brugerens primære engagement.
>
>     \* `integrations.ad.write.org_unit_field`: Navnet på det felt i
>     AD, hvor MO skriver enhedshierakiet for den enhed, hvor
>     medarbejderen har sin primære ansættelse.
>
>     -   `integrations.ad.write.upn_end`: Endelse for feltet UPN.
>
>     \* `integrations.ad.write.level2orgunit_type`: UUID på den klasse
>     som beskriver at en enhed er den primære organisatoriske
>     gruppering (direktørområde, forvaltning, etc.). Dette kan være en
>     enhedstype eller et enhedsniveau.
>
> -   Der udrages et antal tilfældige brugere fra AD (mindst 10), og
>     disse tjekkes for tilstædeværelsen af de tre AD felter beskrevet i
>     `integrations.ad.write.uuid_field`,
>     `integrations.ad.write.level2orgunit_field` og
>     `integrations.ad.write.org_unit_field`. Hvis hvert felt findes hos
>     mindst en bruger, godkendes den lokale AD opsætning.
>
> -   Længden af cpr-numrene hos de tilfældige brugere testes for om de
>     har den forventede længde, 10 cifre hvis der ikke anvendes en
>     separator, 11 hvis der gør. Det er et krav for at integrationen
>     kan køre korrekt, at alle cpr-numre anvender samme (eller ingen)
>     separator.

Hvis disse tests går igennem, anses opsætningen for at være klar til AD
skriv integrationen.

#### Brug af integrationen

Integrationen anvendes ved at slå brugere op via cpr nummer. Det er
muligt at slå op på enten et specifikt cpr-nummer, på en søgning med
wild card, eller man kan lave et opslag på alle brugere, som derved
caches i integrationen hvorefter opsalg på enkelte cpr-numre vil ske
næsten instantant. Den indledende cache skabes i praksis ved at
itererere over alle cpr-numre ved hjælp af kald til 01\*, 02\* etc.

Ved anvendelse af både administrativt AD og skole AD vil brugere først
blive slået op i skole AD og dernæst i administrativt AD, hvis
medarbejderen findes begge steder vil det således blive elementet fra
det administrative AD som vil ende med at blive returneret.

``` python
import ad_reader

ad_reader = ad_reader.ADParameterReader()

# Læs alle medarbejdere ind fra AD.
ad_reader.cache_all()

# De enkelte opslag går nu direkte til cache og returnerer med det samme
user = ad_reader.read_user(cpr=cpr, cache_only=True)
```

Objektet `user` vil nu indeholde de felter der er angivet i
`settings.json` med nøglen `integrations.ad.properties`.

## Valg af primær konto ved flere konti pr. cprnummer

Nogle steder har man flere konti med samme cprnummer i AD\'et. For at
vælge den primære, som opdaterer / opdateres fra MO, kan man anvende et
sæt nøgler i settingsfilen:

-   `integrations.ad.discriminator.field` et felt i det pågældende AD,
    som bruges til at afgøre hvorvidt denne konto er den primære
-   `integrations.ad.discriminator.values` et sæt strenge, som matches
    imod `integrations.ad.discriminator field`
-   `integrations.ad.discriminator.function` kan være \'include\' eller
    \'exclude\'

Man definerer et felt, som indeholder en indikator for om kontoen er den
primære, det kunnne f.x være et felt, man kaldte xBrugertype, som kunne
indeholde \"Medarbejder\".

Hvis man i dette tilfælde sætter
`integrations.ad.discriminator.function` til `include` vil kontoen
opfattes som primær hvis \'Medarbejder\' også findes i
`integrations.ad.discriminator.values`

Opfattes mere end en konto som primær tages den første, man støder på -I
så tilfælde fungerer `integrations.ad.discriminator.values` som en
prioriteret liste

Findes nøglen `integrations.ad.discriminator.field`, skal de andre to
nøgler også være der. Findes den ikke, opfattes alle AD-konti som
primære.

#### Skrivning til AD

Der udvikles i øjeblikket en udvidelse til AD integrationen som skal
muliggøre at oprette AD brugere og skrive information fra MO til
relevante felter.

Hvis denne funktionalitet skal benyttes, er der brug for yderligere
parametre som skal være sat når programmet afvikles:

> -   `servers` fra `integrations.ad[0]`: Liste med de DC\'ere som
>     findes i kommunens AD. Denne liste anvendes til at sikre at
>     replikering er færdiggjort før der skrives til en nyoprettet
>     bruger.
> -   `integrations.ad.write.uuid_field`: Navnet på det felt i AD, hvor
>     MOs bruger-uuid skrives.
> -   `integrations.ad.write.level2orgunit_field`: Navnet på det felt i
>     AD, hvor MO skriver navnet på den organisatoriske hovedgruppering
>     (Magistrat, direktørområde, eller forvalting) hvor medarbejderen
>     har sin primære ansættelse.
> -   `integrations.ad.write.org_unit_field`: Navnet på det felt i AD,
>     hvor MO skriver enhedshierakiet for den enhed, hvor medarbejderen
>     har sin primære ansættelse.
> -   `integrations.ad.write.primary_types`: Sorteret lister over
>     uuid\'er på de ansættelsestyper som markerer en primær ansættelse.
>     Jo tidligere et engagement står i listen, jo mere primært anses
>     det for at være.
> -   `integrations.ad.write.level2orgunit_type`: uuid på den enhedstype
>     som angiver at enheden er en organisatorisk hovedgruppering og
>     derfor skal skrives i feltet angivet i
>     `integrations.ad.write.level2orgunit_field`.

## Skabelse af brugernavne

For at kunne oprette brugere i AD, er det nødvendigt at kunne tildele et
SamAccountName til de nye brugere. Til dette formål findes i modulet
`user_names` klassen `CreateUserNames`. Programmet startes ved at
instantiere klassen med en liste over allerede reserverede eller
forbudte navne som parametre, og det er herefter muligt at forespørge AD
om en liste over alle brugenavne som er i brug, og herefter er programet
klar til at lave brugernavne.

``` python
from user_names import CreateUserName

name_creator = CreateUserNames(occupied_names=set())
name_creator.populate_occupied_names()

name = ['Karina', 'Munk', 'Jensen']
print(name_creator.create_username(name))

name = ['Anders', 'Kristian', 'Jens', 'Peter', 'Andersen']
print(name_creator.create_username(name))

name = ['Olê', 'Østergård', 'Høst', 'Ærøe']
print(name_creator.create_username(name))
```

For at undgå at genbruge brugernavne læses alle eksisterende brugernavne
fra AD. Derudover er det muligt at tilføje lister af brugernavne man
ikke vil have oprettet, fx. fordi tidligere brugere har anvendt det
navn. Listen kan hentes fra en csv fil eller fra en database ved at
tilføje variable til settings.json.

For at læse fra en csv fil sættes stien til filen i
[integrations.ad_writer.user_names.disallowed.csv_path]{.title-ref}.

For at læse fra en database sættes følgende settings: \*
\"integrations.ad_writer.user_names.disallowed.sql_connection_string\" -
<https://docs.sqlalchemy.org/en/14/core/engines.html> \*
\"integrations.ad_writer.user_names.disallowed.sql_table_name\" \*
\"integrations.ad_writer.user_names.disallowed.sql_column_name\"

## Synkronisering

Der eksisterer (udvikles) to synkroniseringstjenester, en til at
synkronisere felter fra AD til MO, og en til at synkronisere felter fra
MO til AD.

##### AD til MO

Synkronisering fra AD til MO foregår via programmet `ad_sync.py`.

Programmet opdaterer alle værdier i MO i henhold til den feltmapning,
som er angivet i [settings.json]{.title-ref}. Det er muligt at
synkronisere adresseoplysninger, samt at oprette et IT-system på
brugeren, hvis brugeren findes i AD, men endnu ikke har et tilknyttet
IT-system i MO. Desuden er det muligt at synkronisere et AD-felt til et
felt på brugerens primærengagement (typisk stillingsbetegnelsen).

`ad_sync.py` er ejer over det MO-data, som programmet skriver til.

Hvis `ad_sync.py` er sat op til udlæse fra flere AD-servere: Husk at
efterfølgende AD kan overskrive. Derfor: Anvend ikke samme klasser,
itsystemer eller extensionfelter i flere af de specificerede AD\'er

Et eksempel på en feltmapning angives herunder:

``` json
"ad_mo_sync_mapping": {
    "user_attrs": {
        "samAccountName": "user_key"
    },
    "user_addresses": {
        "telephoneNumber": ["a6dbb837-5fca-4f05-b369-8476a35e0a95", "INTERNAL"],
        "pager": ["d9cd7a04-a992-4b31-9534-f375eba2f1f4 ", "PUBLIC"],
        "EmailAddress": ["fbd70da1-ad2e-4373-bb4f-2a431b308bf1", null],
        "mobile": ["6e7131a0-de91-4346-8607-9da1b576fc2a ", "PUBLIC"]
    },
    "it_systems": {
        "samAccountName": "d2998fa8-9d0f-4a2c-b80e-c754c72ef094"
    },
    "engagements": {
        "Title": "extension_2"
    }
}
```

I `user_attrs` kan AD-felter på brugere mappes til tilsvarende felter i
MO. I eksemplet er AD-feltet `samAccountName` således mappet til
MO-feltet `user_key`.

I `user_addresses` kan AD-felter mappes til MO-adresseoplysninger. Her
angives en synlighed, som kan antage værdierne [PUBLIC]{.title-ref},
[INTERNAL]{.title-ref}, [SECRET]{.title-ref} eller [null]{.title-ref},
hvilket angiver at synligheden i MO sættes til hhv. offentlig, intern,
hemmelig, eller ikke angivet. UUID\'erne identificerer de adresseklasser
i MO, som AD-felterne skal mappes til.

Hvis der findes flere adresser i MO med samme type og synlighed, vil
programmet opdatere den først fundne MO-adresse, og afslutte de andre
matchende MO-adresser.

Hvis der for en given bruger er felter i feltmapningen, som ikke findes
i AD, vil disse felter blive sprunget over, men de øvrige felter vil
stadig blive synkroniseret.

Selve synkroniseringen foregår ved at programmet først udtrækker
samtlige medarbejdere fra MO, der itereres hen over denne liste, og
information fra AD\'et slås op med cpr-nummer som nøgle. Hvis brugeren
findes i AD, udlæses alle parametre angivet i
[integrations.ad.properties]{.title-ref} og de af dem, som figurerer i
feltmapningen, synkroniseres til MO.

Integrationen vil som udgangspunkt ikke synkronisere fra et eventuelt
skole AD, med mindre nøglen
[integrations.ad.skip_school_ad_to_mo]{.title-ref} sættes til
[false]{.title-ref}.

Da AD ikke understøtter gyldighedstider, antages alle informationer
uddraget fra AD at gælde fra \'i dag\' og til evig tid. Den eneste
undtagelse til dette er ved afslutning af deaktiverede AD brugere.

Deaktiverede AD brugere kan håndteres på forskellige måder. Som
udgangspunkt synkroniseres de på præcis samme vis som almindelige
brugere, med mindre nøglen [ad_mo_sync_terminate_disabled]{.title-ref}
er sat til [True]{.title-ref}. Hvis dette er tilfælde ophører den
automatiske synkronisering, og deaktiverede brugere får i stedet deres
AD data \'afsluttet\'. Ved afslutning forstås at brugerens AD
synkroniserede adresser og it-systemer flyttes til fortiden, såfremt de
har en åben slutdato.

Hvis nøglen [ad_mo_sync_terminate_disabled]{.title-ref} ikke er
fintmasket nok, f.eks. fordi deaktiverede brugere dækker over både
brugere som er under oprettelse og brugere som er under nedlæggelse, kan
et være nødvendigt at tage stilling til om en given deaktiveret bruger
skal nedlægges eller synkroniseres på baggrund af AD dataene fra den
enkelte bruger.

Dette understøttes vha.
[ad_mo_sync_terminate_disabled_filters]{.title-ref} nøglen. Denne nøgle
indeholder en liste af jinja templates. Disse templates kan returnere en
sand værdi for at terminere brugeren, eller en falsk værdi for at
synkronisere brugeren. Kun hvis samtlige filtre returnere sand vil
brugeren blive termineret, hvis blot ét af filtrene returnerer falsk vil
brugeren i stedet blive synkroniseret. Resultaterne for evaluering af
filtrene sammenholdes altså med en \'AND\' operation.

Værdierne der vurderes som sande er \"yes\", \"true\", \"1\" og \"1.0\".

> Eksempel 1:
>
> Vi ønsker kun at terminere brugere, hvis MO UUID starter med 8 nuller,
> f.eks.: \'00000000-e4fe-47af-8ff6-187bca92f3f9\'.
>
> For at opnå dette kan vi lave følgende konfiguration:
>
> ``` json
> {
>     "ad_mo_sync_terminate_disabled_filters": [
>         "{{ uuid.startswith('00000000') }}"
>     ]
> }
> ```
>
> Eksempel 2:
>
> Vi holder i vores AD et extensionAttribute felt til livtidstilstanden
> af brugerne. Lad os antage at der er tale om feltet
> [extensionAttribute3]{.title-ref}, der kan holde værdierne:
>
> -   \`\"Ny bruger\"\`: Som skal synkroniseres
> -   \`\"På orlov\"\`: Som skal synkroniseres
> -   \`\"Under sletning\"\`: Som skal termineres
>
> Vi ønsker altså at termineringsadfærden skal afledes af feltets værdi
> i AD.
>
> For at opnå dette kan vi lave følgende konfiguration:
>
> ``` json
> {
>     "ad_mo_sync_terminate_disabled_filters": [
>         "{{ ad_object['extenionAttribute3'] == 'Under sletning' }}"
>     ]
> }
> ```

Såfremt nogle brugere hverken ønskes terminerede eller synkroniserede
kan de filtreres fra vha. [ad_mo_sync_pre_filters]{.title-ref} nøglen.
Denne nøgle indeholder en liste af jinja templates. Disse templates kan
returnere en sand værdi for at beholde brugeren, eller en falsk værdi
for filtrere brugeren fra. Kun hvis samtlige filtre returnerer sand vil
brugeren blive beholdt, hvis blot ét af filtrene returnerer falsk vil
brugeren i stedet blive filtreret fra. Resultaterne for evaluering af
filtrene sammenholdes altså med en \'AND\' operation.

> Eksempel 1:
>
> I det forrige Eksempel 2 så vi på en situation hvor et AD felt
> benyttes til at afgøre om hvorvidt brugere skulle termineres eller
> synkroniseres.
>
> Lad os antage at vi stadig har konfigurationen herfra i vores
> settings.json fil, men nu ønsker slet ikke at synkronisere [\"På
> orlov\"]{.title-ref} brugerne overhovedet.
>
> For at opnå dette kan vi lave følgende konfiguration:
>
> ``` json
> {
>     "ad_mo_sync_terminate_disabled_filters": [
>         "{{ ad_object['extenionAttribute3'] == 'Under sletning' }}"
>     ],
>     "ad_mo_sync_pre_filters": [
>         "{{ ad_object['extenionAttribute3'] != 'På orlov' }}"
>     ]
> }
> ```

Foruden terminering af MO kontos hvor AD brugeren er deaktiveret, kan MO
kontos hvor en tilsvarende AD bruger ikke kan findes, også termineres
automatisk. Denne funktionalitet aktiveres ved at sætte med nøglen
[ad_mo_sync_terminate_missing]{.title-ref} til [True]{.title-ref}.

Disse brugere med manglende AD konti kan desuden begrænses således at
der kun termineres brugere der tidligere har været oprettet i AD. Dette
sker ved at tjekke om brugerens MO konti har et AD it-system svarende
til konfigurationen i `it_systems -> samAccountName`. Denne adfærd kan
slås fra ved at sætte nøglen:
[ad_mo_sync_terminate_missing_require_itsystem]{.title-ref} til
[False]{.title-ref}, hvorefter SAMTLIGE MO brugere uden en tilhørende AD
konti vil blive termineret. Dette vil typisk betyde at et stort antal
historiske brugere vil få termineret deres adresser og itsystemer.

Slutteligt skal det nævnes, at implemeneringen af synkroniseringen
understøtter muligheden for at opnå en betydelig hastighedsforbering ved
at tillade direkte adgang til LoRa, denne funktion aktiveres med nøglen
[integrations.ad.ad_mo_sync_direct_lora_speedup]{.title-ref} og
reducerer kørselstiden betragteligt. Hvis der er få ændringer vil
afviklingstiden komme ned på nogle få minutter.

##### MO til AD

Synkronisering fra MO til AD foregår således:

-   der itereres hen over alle AD-brugere
-   hver enkelt AD-bruger slås op i MO via feltet angivet i nøglen
    [integrations.ad.write.uuid_field]{.title-ref}
-   data om den tilsvarende MO-bruger synkroniseres til AD i henhold til
    konfigurationen (se nedenfor)

AD-integrationen stiller et antal MO-værdier til rådighed, som det er
muligt at synkronisere til felter på AD-brugere. Flere MO-værdier kan
tilføjes, efterhånden som integrationen udvikles. Her er en liste over
de MO-værdier, integrationen stiller til rådighed i dag:

::: {#MO-værdier}
  ----------------------------------------------------------------------------------
  Feltnavn              Beskrivelse af indhold
  --------------------- ------------------------------------------------------------
  `uuid`                Brugerens UUID i MO.

  `employment_number`   Lønsystemets ansættelsesnummer for medarbejderens primære
                        engagement.

  `title`               Stillingsbetegnelsen for brugerens primære engagement.

  `start_date`          Startdato for aktuelle engagement i MO.

  `end_date`            Slutdato for aktuelle engagement i MO. Hvis en ansættelse
                        ikke har nogen kendt slutdato, angives 9999-12-31. For at få
                        skrevet afsluttede engagementers slutdato anvendes jobbet
                        [ad_fix_enddate]{.title-ref}.

  `name`                Brugerens navn, opdelt i fornavn og efternavn. Fornavn kan
                        fx tilgås via `mo_values['name'][0]`, og efternavn via
                        `mo_values['name'][1]`.

  `full_name`           Brugerens fulde navn, dvs. fornavn og efternavn samlet i et
                        felt.

  `nickname`            Brugerens kaldenavn, opdelt i fornavn og efternavn. Fornavn
                        kan fx tilgås via `mo_values['nickname'][0]`, og efternavn
                        via `mo_values['nickname'][1]`.

  `full_nickname`       Brugerens fulde kaldenavn, dvs. fornavn og efternavn samlet
                        i eet felt.

  `cpr`                 Brugerens CPR-nummer.

  `unit`                Navn på enheden for brugerens primære engagement.

  `unit_uuid`           UUID på enheden for brugerens primære engagement.

  `unit_user_key`       Brugervendt nøgle for enheden for brugerens primære
                        engagement. Dette vil typisk være lønsystemets korte navn
                        for enheden.

  `unit_public_email`   Email på brugerens primære enhed med synligheden
                        `offentlig`.

  `unit_secure_email`   Email på brugerens primære enhed med synligheden `hemmelig`.
                        Hvis enheden kun har email-adresser uden angivet synlighed,
                        vil den blive angivet her.

  `unit_postal_code`    Postnummer for brugerens primære enhed.

  `unit_city`           By for brugerens primære enhed.

  `unit_streetname`     Gadenavn for brugerens primære enhed.

  `location`            Fuld organisatorisk sti til brugerens primære enhed.

  `level2orgunit`       Den organisatoriske hovedgruppering (magistrat,
                        direktørområde, eller forvaltning) som brugerens primære
                        engagement hører under.

  `manager_name`        Navn på leder for brugerens primære engagement.

  `manager_cpr`         CPR-nummer på leder for brugerens primære engagement.

  `manager_sam`         `SamAccountName` for leder for brugerens primære engagement.

  `manager_mail`        Email på lederen for brugerens primære engagement.

  `itsystems`           Et dictionary fra it-systems UUID til itsystemer. I
                        python-termer: {\"opus_uuid\": {\"username\":
                        \"brugernavn\", \"from_date\": \"1930-01-01\"}}
  ----------------------------------------------------------------------------------

  : MO-værdier
:::

MO-felterne `level2orgunit` og `location` synkroniseres altid til
felterne angivet i konfigurationsnøglerne
`integrations.ad.write.level2orgunit_type` og
`integrations.ad.write.org_unit_field`, og skal derfor ikke specificeres
yderligere i feltmapningen.

MO-felterne `manager_name`, `manager_cpr`, `manager_sam` og
`manager_mail` får indhold ud fra brugerens primære engagement. Derfor
har disse felter kun et indhold fra den dato, hvor brugerens engagement
i enheden begynder. Hvis der køres en synkronisering til et AD inden
denne dato, vil felterne være tomme, da engagementet ikke er begyndt
endnu.

Udover ovenstående felter er
`` sync_timestamp` til rådighed. Hvis denne sættes i feltmapningen vil ad_writer udfylde feltet med tidsstemplet for hvornår en bruger sidst blev synkroniseret fra MO.  Synkroniseringen til AD foretages i henhold til en lokal feltmapning, som eksempelvis kan se ud som dette:  .. code-block:: json    "integrations.ad_writer.mo_to_ad_fields": {     "unit_postal_code": "postalCode",     "unit_city": "l",     "unit_user_key": "department",     "unit_streetname": "streetAddress",     "unit_public_email": "extensionAttribute3",     "title": "Title",     "unit": "extensionAttribute2"   }  Formatet for ``mo_to_ad_fields`` er: MO-felt -> AD-felt. Altså mappes `unit_public_email` fra MO til `extensionAttribute3` i AD i ovenstående eksempel.  MO til AD - tilpasning vha. Jinja-templates +++++++++++++++++++++++++++++++++++++++++++  Som et alternativ til den ovennævnte direkte 1-til-1 feltmapning (`mo_to_ad_fields`) er der også mulighed for en mere fleksibel felt-mapning vha. såkaldte `Jinja`-skabeloner. Dette giver yderligere muligheder for at tilpasse formatteringen af de enkelte værdier, der skrives i AD. Se eventuelt her: https://jinja.palletsprojects.com/en/2.11.x/templates/ (linket er på engelsk.)  Standard-opsætningen af AD-integrationen indeholder flg. Jinja-templates:  .. code-block:: json    "integrations.ad_writer.template_to_ad_fields": {     "Name": "{{ mo_values['name'][0] }} {{ mo_values['name'][1] }} - {{ user_sam }}",     "Displayname": "{{ mo_values['name'][0] }} {{ mo_values['name'][1] }}",     "Givenname": "{{ mo_values['name'][0] }}",     "Surname": "{{ mo_values['name'][1] }}",     "EmployeeNumber": "{{ mo_values['employment_number'] }}",     "extensionAttribute7": "{{ mo_values['itsystems'].get('123e4567-e89b-12d3-a456-426614174000', {}).get('username') }}",   }  De felter, der er tilgængelige i ``mo_values`` , er beskrevet her: :ref:`MO-værdier`. Desuden kan felter + faktiske værdier (for en given bruger) ses ved at køre følgende kommando:  .. code-block:: bash    python -m integrations.ad_integration.ad_writer --mo-values MO_BRUGER_UUID_HER --ignore-occupied-names  Med denne standard-opsætning oprettes der brugere i AD på denne form:  .. list-table:: Eksempel    :header-rows: 1     * - AD-felt      - Indhold    * - `Name`      - "Fornavn Efternavn - Sam_account_name"    * - `Displayname`      - "Fornavn Efternavn"    * - `GivenName`      - "Fornavn"    * - `SurName`      - "Efternavn"    * - `EmployeeNumber`      - "A1234"  Standard-opsætningen kan udvides eller erstattes. Eksempelvis kan opsætningen udvides til også at udfylde postnummer, afdeling, gadenavn og en `extension attribute` således:  .. code-block:: json    "integrations.ad_writer.template_to_ad_fields": {     "# standard-felter": "",     "Name": "{{ mo_values['name'][0] }} {{ mo_values['name'][1] }} - {{ user_sam }}",     "Displayname": "{{ mo_values['name'][0] }} {{ mo_values['name'][1] }}",     "GivenName": "{{ mo_values['name'][0] }}",     "SurName": "{{ mo_values['name'][1] }}",     "EmployeeNumber": "{{ mo_values['employment_number'] }}",      "# yderligere felter": "",     "postalCode": "{{ mo_values['unit_postal_code'] }}",     "department": "{{ mo_values['unit_user_key'] }}",     "streetName": "{{ mo_values['unit_streetname'].split(' ')[0] }}",     "extensionAttribute3": "{{ mo_values['unit_public_email']|default('all@afdeling.dk') }}",     "extensionAttribute4": "{{ sync_timestamp }}"   }  Det er værd at bemærke, at begge konfigurationsmuligheder (`mo_to_ad_fields` og `template_to_ad_fields`) benytter Jinja-skabeloner som grundlag for deres virkemåde. Det er altså ækvivalent at skrive henholdsvis:  .. code-block:: json    "integrations.ad_writer.mo_to_ad_fields": {     "unit_postal_code": "postalCode",   }  og:  .. code-block:: json    "integrations.ad_writer.template_to_ad_fields": {     "postalCode": "{{ mo_values['unit_postal_code'] }}",   }  Da førstnævnte konfiguration konverteres til sidstnævnte internt i programmet.  Når man skriver Jinja-templates i `template_to_ad_fields` er data om MO-brugeren tilgængelige i objektet ``mo_values`(som vist i eksemplerne ovenfor). Samtidig er data om AD-brugeren (før skrivning) ligeledes tilgængelige i objektet`ad_values`. Når koden *opretter* en ny AD-bruger, er`ad_values`` tilgængeligt for Jinja-templates, men er et tomt objekt. Dette kan fx anvendes til kun at synkronisere data fra MO til AD, såfremt der ikke allerede står noget i det pågældende AD-felt:  .. code-block:: json    "integrations.ad_writer.template_to_ad_fields": {     "titel": "{{ ad_values.get('titel') or mo_values['title'] }}",   }  I ovenstående eksempel vil værdien i AD-feltet `titel` kun blive udfyldt med MO's tilsvarende `title` hvis AD-brugeren ikke allerede har en titel. Og det har AD-brugeren ikke, såfremt programmet netop er i færd med at oprette selvsamme AD-bruger.   Afvikling af PowerShell templates ---------------------------------  Det er muligt at angive PowerShell kode hvor visse værdier angives med abstrakte refrencer til MO, som så på runtime vil bive udfyldt med de tilhørende værdier for det person det drejer sig om.  for øjeblikket understøttes disse variable:   * ``%OS2MO_AD_BRUGERNAVN%`*`%OS2MO_BRUGER_FORNAVN%`*`%OS2MO_BRUGER_EFTERNAVN%`*`%OS2MO_BRUGER_CPR%`*`%OS2MO_LEDER_EMAIL%`*`%OS2MO_LEDER_NAVN%`*`%OS2MO_BRUGER_ENHED%`*`%OS2MO_BRUGER_ENHED_UUID%`` Hvis et script indeholder andre nøgler på formen %OS2MO_ ... % vil der returneres en fejlmeddelelse (exception hvis det afvikles som en integration), med mindre disse variable er udkommenteret.  Integrationen forventer at scripts befinder sig i mappen `scripts` i en undermappe til integrationen selv, og alle scripts skal have en `ps_template` som filendelse. Den tekniske platform for afvikling af scripts er den samme som for den øvrige AD integration; scriptet sendes til remote management serveren, som afvikler scriptet. Bemærk at scripts i denne kategori ikke nødvendigvis behøver have direkte kontakt med AD, men vil kunne anvends til alle formål hvor der er behov for at afvikle PowerShell med værdier fra MO.   Opsætning for lokal brug af integrationen -----------------------------------------  Flere af værktøjerne i AD integrationen er udstyret med et kommandolinjeinterface, som kan anvendes til lokale tests. For at anvende dette er skal tre ting være på plads i det lokale miljø:   1. En lokal bruger med passende opsætning af kerberos til at kunne tilgå remote     management serveren.  2. Den nødvendige konfiguration skal angives i ``settings.json`.  3. Et lokalt pythonmiljø med passende afhængigheder  Angående punkt 1 skal dette opsættes af den lokale IT organisation, hvis man har fulgt denne dokumentation så langt som til dette punkt, er der en god sandsynlighed for at man befinder sig i et miljø, hvor dette allerede er på plads.  Punkt 2 gøres ved at oprette filen`settings.json`under mappen`settings`Et eksempel på sådan en fil kunne se sådan ud:  .. code-block:: json     {        "mox.base": "http://localhost:8080",        "mora.base": "http://localhost:5000",        "municipality.name": "Kommune Kommune",        "municipality.code": 999,        "integrations.SD_Lon.import.too_deep": ["Afdelings-niveau"],        "integrations.SD_Lon.global_from_date": "2019-10-31",        "integrations.SD_Lon.sd_user": "SDUSER",        "integrations.SD_Lon.sd_password": "SDPASSWORD",        "integrations.SD_Lon.institution_identifier": "AA",        "integrations.SD_Lon.import.run_db": "/home/mo/os2mo-data-import-and-export/settings/change_at_runs.db",        "address.visibility.secret": "53e9bbec-dd7b-42bd-b7ee-acfbaf8ac28a",        "address.visibility.internal": "3fe99cdd-4ab3-4bd1-97ad-2cfb757f3cac",        "address.visibility.public": "c5ddc7d6-1cd2-46b0-96de-5bfd88db8d9b",        "integrations.ad.winrm_host": "rm_mangement_hostname",        "integrations.ad.search_base": "OU=KK,DC=kommune,DC=dk",        "integrations.ad.system_user": "serviceuser",        "integrations.ad.password": "sericeuser_password",        "integrations.ad.cpr_field": "ad_cpr_field",        "integrations.ad.write.servers": [      "DC1",      "DC2",      "DC3",      "DC4",      "DC5"        ],        "integrations.ad.write.level2orgunit_type": "cdd1305d-ee6a-45ec-9652-44b2b720395f",        "integrations.ad.write.primary_types": [      "62e175e9-9173-4885-994b-9815a712bf42",      "829ad880-c0b7-4f9e-8ef7-c682fb356077",      "35c5804e-a9f8-496e-aa1d-4433cc38eb02"        ],        "integrations.ad_writer.mo_to_ad_fields": {      "unit_user_key": "department",      "level2orgunit": "company",      "title": "Title",      "unit": "extensionAttribute2"        },        "integrations.ad.write.uuid_field": "sts_field",        "integrations.ad.write.level2orgunit_field": "extensionAttribute1",        "integrations.ad.write.org_unit_field": "extensionAttribute2",        "integrations.ad.properties": [      "manager",      "ObjectGuid",      "SamAccountName",      "mail",      "mobile",      "pager",      "givenName",      "l",      "sn",      "st",      "cn",      "company",      "title",      "postalCode",      "physicalDeliveryOfficeName",      "extensionAttribute1",      "extensionAttribute2",      "ad_cpr_field"        ],        "integrations.ad.ad_mo_sync_mapping": {      "user_addresses": {          "telephoneNumber": ["51d4dbaa-cb59-4db0-b9b8-031001ae107d", "PUBLIC"],          "pager": ["956712cd-5cde-4acc-ad0a-7d97c08a95ee", "SECRET"],          "mail": ["c8a49f1b-fb39-4ce3-bdd0-b3b907262db3", null],          "physicalDeliveryOfficeName": ["7ca6dfb1-5cc7-428c-b15f-a27056b90ae5", null],          "mobile": ["43153f5d-e2d3-439f-b608-1afbae91ddf6", "PUBLIC"]      },      "it_systems": {          "samAccountName": "fb2ac325-a1c4-4632-a254-3a7e2184eea7"      }        }    }   Hvor betydniningen af de enkelte felter er angivet højere oppe i dokumentationen. Felter som omhandler skolemdomænet er foreløbig sat via miljøvariable og er ikke inkluderet her, da ingen af skriveintegrationerne på dette tidspunkt undestøtter dette.  Det skal nu oprettes et lokalt afviklingsmiljø. Dette gøres ved at klone git projektet i en lokal mappe og oprette et lokal python miljø:  ::     git clone https://github.com/OS2mo/os2mo-data-import-and-export    cd os2mo-data-import-and-export    python3 -m venv venv    source venv/bin/activate    pip install --upgrade pip    pip install os2mo_data_import/    pip install pywinrm[kerberos]   For at bekræfte at alt er på plads, findes et værktøj til at teste kommunikationen:  ::     cd integrations/ad_integration    python test_connectivity.py  Hvis dette returnerer med ordet 'success' er integrationen klar til brug.   Anvendelse af kommondolinjeværktøjer ------------------------------------  Følgende funktionaliteter har deres eget kommandolinjeværktøj som gør det muligt at anvende dem uden at rette direkte i Python koden:   *`ad_writer.py`*`ad_life_cycle.py`*`execute_ad_script.py`*`user_names.py`` For user names kræves der dog en del forudsætninger som gør at kommandolinjeværktøjet ikke praksis har brugbar funktionalitet endnu.  ad_writer.py ++++++++++++  Dette værktøj har følgende muligheder:  ::     usage: ad_writer.py [-h]                     [--create-user-with-manager MO_uuid |         --create-user MO_uuid |         --sync-user MO_uuid | --delete-user User_SAM |         --read-ad-information User_SAM |         --add-manager-to-user Manager_SAM User_SAM]  De forskellige muligheder gennemgås her en ad gangen:  * --create-user-with-manager MO uuid     Eksempel: python ad_writer-py --create-user-with-manager 4931ddb6-5084-45d6-9fb2-52ff33998005     Denne kommando vil oprette en ny AD bruger ved hjælp af de informationer der er    findes om brugeren i MO. De relevante felter i AD vil blive udfyld i henhold til    den lokale feltmapning, og der vil blive oprettet et link til AD kontoen for    lederen af medarbejderens primære ansættelse. Hvis det ikke er muligt at finde    en leder, vil integrationen standse med en `ManagerNotUniqueFromCprException`.   * --create-user MO_uuid     Eksempel: python ad_writer-py --create-user 4931ddb6-5084-45d6-9fb2-52ff33998005     Som ovenfor men i dette tilfælde oprettes der ikke et link til lederens AD konto.   * --sync-user MO_uuid     Eksempel: python ad_writer-py --sync-user 4931ddb6-5084-45d6-9fb2-52ff33998005     Synkroniser oplysninger fra MO til en allerede eksisterende AD konto.   * --delete-user User_SAM     Eksempel: python ad_writer-py --delete-user MGORE     Slet den pågældende AD bruger. Denne funktion anvendes hovedsageligt til tests,    da et driftmiljø typisk vil have en mere kompliceret procedure for sletning af    brugere.   * --read-ad-information User_SAM     Eksempel: python ad_writer-py --read-ad-information MGORE     Returnere de AD oplysninger fra AD som integrationen i øjeblikket er konfigureret    til at læse. Det er altså en delmængde af disse oplysninger som vil blive    skrevet til MO af synkroniseringsværktøjet. Funktionen er primært nyttig til    udvikling og fejlfinding.   * --add-manager-to-user Manager_SAM User_SAM     Eksempel: python ad_writer-py --add-manager-to-user DMILL MGORE     Udfylder brugerens ``manager`` felt med et link til AD kontoen der hører til    ManagerSAM.   ad_fix_enddate.py +++++++++++++++++ Hvis ad_writer skal skrive `end_date` kan dette job være nødvendigt at sætte op også fordi ad_writer ikke læser engagementer i MO i fortiden. Dette job tjekker alle engagementer i AD som har slutdatoen 9999-12-31 i AD og tjekker deres slutdato i MO. Hvis engagementet allerede  er afsluttet i MO opdateres det i AD.  For at sætte det som en del af job-runneren sættes:  * ``crontab.RUN_AD_ENDDATE_FIXER`` : Sættes til `true` for at køre det som en del af de daglige jobs. * ``integrations.ad_writer.fixup_enddate_field`: Det felt i AD som slutdatoen skrives i. *`integrations.ad.write.uuid_field`: Feltet i AD som indeholder brugeres MO uuid.      ad_life_cycle.py ++++++++++++++++  Dette værktøj kan afhængig af de valgte parametre oprette eller deaktivere AD-konti på brugere som henholdsvis findes i MO men ikke i AD, eller findes i AD, men ikke har aktive engagementer i MO.  ::    usage: ad_life_cycle.py [-h/--help]                            [--create-ad-accounts] [--disable-ad-accounts]                            [--dry-run] [--use-cached-mo]  Betydningen af disse parametre angives herunder, det er muligt at afvilke begge synkroniseringer i samme kørsel ved at angive begge parametre.   *`\--create-ad-accounts`Opret AD brugere til MO brugere som ikke i forvejen findes i AD efter de    regler som er angivet i settings-nøglerne:     *`integrations.ad.write.create_user_trees`og    *`integrations.ad.lifecycle.create_filters`Se mere om disse herunder.   *`\--disable-ad-accounts`Sæt status til Disabled for AD konti hvor den tilhøende MO bruge ikke længere    har et aktivt engagement og som opfylder reglerne angivet i settings-nøglen:     *`integrations.ad.lifecycle.disable_filters`Se mere om denne herunder.   *`\--dry-run`Programmet vil ikke forsøge at opdatere sit billede af MO, en vil anvende    den aktuelt cache'de værdi. Dette kan være nyttigt til udvikling, eller    hvis flere integrationer køres umidelbart efter hinanden.   *`\--use-cached-mo`Programmet vil ikke genopfriske LoraCache, men blot benytte den aktuelle    LoraCache der findes på disken.  Derudover kan programmet konfigureres med nøgler i`settings.json`specifikt:   *`integrations.ad.write.create_user_trees`Her angives en liste over et eller flere UUID'er på organisationsenheder i    MO. Hvis en medarbejder optræder i en af disse enheder (samt deres    underenheder, underenhedernes underenheder, osv.) vil`ad_life_cycle`oprette en AD-konto for medarbejderen (såfremt de ikke allerede har en.)     Hvis man eksempelvis har et organisationstræ i MO, der ser således ud:     .. code-block::        Enhed A (uuid: aaaa)         - Enhed A1 (uuid: aaaa1111)       Enhed B (uuid: bbbb)         - Enhed B1 (uuid: bbbb1111)     og man ønsker, at`ad_life_cycle`kun må oprette AD-konti for MO-brugere i    enhederne A, A1, og B1, kan man angive:     .. code-block:: json        {         "integrations.ad.write.create_user_trees": [           "aaaa", "bbbb1111"         ]       }     Der vil ikke blive oprettet AD-konti for MO-brugere i enhed B med denne    opsætning.   *`integrations.ad.lifecycle.create_filters`Se dokumentation herunder for`integrations.ad.lifecycle.disable_filters`.    Denne nøgle gør det samme, blot som filter for oprettelse istedet for    som filter for deaktivering.   *`integrations.ad.lifecycle.disable_filters`Liste af jinja templates der evalueres på MO brugere, deres engagementer og    deres tilhørende AD konti. Disse templates kan returnere en sand værdi for    at beholde brugeren eller en falsk værdi for at sortere brugeren fra.     Værdierne der vurderes som sande er "yes", "true", "1" og "1.0".    De findes i`string_to_bool`metoden i`exporters/utils/jinja_filter.py`.     Eksempel 1:     Vi ønsker kun at deaktivere brugere, hvis AD konto har et givent prefix (`X`` )    i deres SAM Account Name. For at opnå dette kan vi lave følgende konfiguration:     .. code-block:: json         {            "integrations.ad.lifecycle.disable_filters": [                "{{ ad_object['SamAccountName'].startswith('X') }}"            ]        }     Hermed vil disable-ad-accounts kun deaktivere brugere med X som prefix.     Eksempel 2:     Vi ønsker ikke at oprette brugere i AD, såfremt de har en given    stillingsbetegnelse (`Bruger`) på deres primære engagement i MO.    For at opnå dette kan vi lave følgende konfiguration:     .. code-block:: json         {            "integrations.ad.lifecycle.create_filters": [                "{{ employee.get('primary_engagement', {}).get('job_function', {}).get('title', '') != 'Bruger' }}"            ]        }     Hermed vil create-ad-accounts oprette AD konti for alle brugere, undtagen    dem som har den givne stillingsbetegnelse.   Det er værd at bemærke at brugerne som laves med ad_life_cycle som udgangspunkt *ikke* oprettes med relaterede data, de vil altså fremstå f.eks. uden adresser. Deres relaterede data kan tilførsel vha. ``mo_to_ad_sync`programmet.  Settings kan overskrives hvis der skal gælde andre regler under oprettelsen af nye brugere end der ellers gør under synkroniseringen.  Dette gøres ved at sætte felterne ind i`ad_lifecycle_injected_settings`. De skal skrives som en dictionary med formen "sti.til.setting": "værdi". Bemærk at stien her ikke svarer til stien i settings.json, men i den dictionary som AD læser ud af settings.    Fx.      .. code-block:: json      {       "ad_lifecycle_injected_settings": {           "primary_write.mo_to_ad_fields.Title": "title"           }         }  Dette vil tilføje "title" til settings svarende til settings["primary_write"]["mo_to_ad_fields"]["Title"] = "title". Man kan se resultatet af at tilføre de ekstra settings ved at køre:`python
-m integrations.ad_integration.read_ad_conf_settings
\--inject`execute_ad_script.py ++++++++++++++++++++  Dette værktøj har følgende muligheder:  ::     usage: execute_ad_script.py [-h]                                [--validate-script Script name |              --execute-script Script name user_uuid]  De forskellige muligheder gennemgås her en ad gangen:  * --validate-script Script_name     Eksempel: python ad_writer-py --validate-script send_email     Denne kommando vil lede efter en skabelon i`scripts/send_email.ps_template`og    validere at skabelonen kun indeholder gyldige nøgleværdier. Hvis dette er    tilfældet returneres sætningen "Script is valid" og ellers returneres en    fejlbesked som beskriver hvilke ugyldige nøgler der er fundet i skabelonen.   * --execute-script Script name user_uuid    Eksempel: python execute_ad_script.py --execute-script send_email 4931ddb6-5084-45d6-9fb2-52ff33998005     Denne kommando vil finde en skabelon i`scripts/send_email.ps_template`og først    validere og derefter afvikle de med værdier taget fra brugen med uuid som angivet.   Import af AD OU til MO ======================  Som en ekstra funktionalitet, er det muligt at anvende AD integrationens læsefaciliteter til at indlæse en bestemt OU fra AD'et til MO. Dette vil eksempelvis kunne anvendes hvis AD'et er autoritativ for eksterne konsulenter i kommunen og man ønsker, at disse personer skal fremgå af MOs frontend på trods af at de ikke importeres fra lønsystemet. Integrationen vil oprette ansættelsestypen 'Ekstern' og vil oprette alle brugere fra et på forhånd angivet OU som ansatte i MO. Det er en forudsætning, at disse brugere ikke har andre ansættelser i MO i forvejen. Hvis brugere fjernes fra OU'et vil de blive fjernet fra MO ved næste kørsel af integrationen.  I den nuværende udgave af integrationen, genkendes OU'et med eksterne brugere på, at dets navn indeholder ordene 'Ekstern Konsulenter', dette vil på sigt blive erstattet med konfiguration.  For at programmet kan afvikles, er det nødvendigt at sætte konfigurationsværdien`integrations.ad.import_ou.mo_unit_uuid`som angiver UUID'en på den enhed brugerne fra AD skal synkroniseres til. Hvis enheden ikke eksisterer i forvejen vil den blive oprettet ved første kørsel, så for en kommune som starter op med brug af denne integration, kan der blot angives et tilfældigt UUID.  Programmet hedder`import_ad_group_into_mo.py\`\`
og kan anvendes med et antal kommandolinjeparametre:

> -   \--create-or-update: Opretter og opdaterer bruger fra AD til MO.
> -   \--cleanup-removed-users: Fjerne MO brugere som ikke længere er
>     konsulenter i AD.
> -   \--full-sync: Kører begge de to ovenstående operationer.

### Integration til OS2Sync

#### Indledning

Denne integration gør det muligt at sende data fra OS2MO til
[OS2Sync](https://www.os2sync.dk/). OS2Sync er i stand til at sende data
videre til FK ORG, såfremt det er installeret og konfigureret.
Integrationen læser flg. oplysninger i OS2MO, og sender dem til OS2Sync:

+----------------------------------+----------------------------------+
| OS2MO                            | Oplysninger                      |
+==================================+==================================+
| Ansatte                          | -   UUID                         |
|                                  | -   UserId                       |
|                                  | -   Navn                         |
|                                  | -   CPR-nummer                   |
|                                  | -   Adresser                     |
|                                  | -   Engagementer                 |
+----------------------------------+----------------------------------+
| \-\-\-\-\-\                      | \-\-\-\-\-\-\-\                  |
| -\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-- | -\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-- |
+----------------------------------+----------------------------------+
| Organisationsenheder             | -   UUID                         |
|                                  | -   Parent UUID                  |
|                                  | -   Navn                         |
|                                  | -   IT-systemer                  |
|                                  | -   Adresser                     |
|                                  | -   KLE-opmærkninger             |
|                                  | -   Leder UUID (Optionelt)       |
+----------------------------------+----------------------------------+

Når integrationen sender *ansatte* til OS2Sync, sker det efter
nedenstående skema:

  OS2Sync-felt      Udfyldes med
  ----------------- ---------------------------------------------------------------------------------------------------------------------------------------------------------------------
  `Uuid`            MO-brugerens UUID
  `UserId`          MO-brugerens UUID, medmindre der er registreret et IT-system af typen \"AD\" på MO-brugeren. I så fald bruges det AD-brugernavn, der er registreret på IT-systemet.
  `Person` `Name`   MO-brugerens fornavn og efternavn
  `Person` `Cpr`    MO-brugerens CPR-nummer, medmindre indstillingen `os2sync.xfer_cpr` er sat til `False`.

Når integrationen sender *organisationsenheders adresser* til OS2Sync,
sker det efter nedenstående skema. Såfremt en adresseoplysning på
enheden matcher på \"Scope\" og evt. \"Brugervendt nøgle\", sendes
oplysningen til feltet angivet i \"OS2Sync-felt\":

  Scope       Brugervendt nøgle    OS2Sync-felt
  ----------- -------------------- --------------------
  `EMAIL`     (vilkårlig)          `Email`
  `EAN`       (vilkårlig)          `Ean`
  `PHONE`     (vilkårlig)          `PhoneNumber`
  `DAR`       (vilkårlig)          `Post`
  `PNUMBER`   (vilkårlig)          `Location`
  `TEXT`      `ContactOpenHours`   `ContactOpenHours`
  `TEXT`      `DtrId`              `DtrId`

#### Opsætning

For at kunne afvikle integrationen kræves en række opsætninger af den
lokale server.

Opsætningen i `settings.json`

## fælles parametre

-   `crontab.RUN_OS2SYNC`: Bestemmer om jobbet skal køres i cron
    (true/false)
-   `crontab.SAML_TOKEN`: api token for service-adgang til OS2MO
-   `mora.base`: Beskriver OS2MO\'s adresse
-   `municipality.cvr` : Kommunens CVR-nummer

## os2syncs parametre

> -   `os2sync.log_file`: logfil, typisk \'/opt/dipex/os2sync.log\'
> -   `os2sync.log_level`: Loglevel, numerisk efter pythons
>     logging-modul, typisk 10, som betyder at alt kommer ud
> -   `os2sync.ca_verify_os2mo`: Angiver om OS2mo serverens certifikat
>     skal checkes, typisk true
> -   `os2sync.ca_verify_os2sync`: Angiver om Os2Sync containerens
>     certifikat skal checkes, typisk true
> -   `os2sync.hash_cache`: Cache som sørger for at kun ændringer
>     overføres
> -   `os2sync.phone_scope_classes`: Begrænsning af hvilke
>     telefon-klasser, der kan komme op, anvendes typisk til at
>     frasortere hemmelige telefonnumre
> -   `os2sync.email_scope_classes`: Begrænsning af hvilke
>     email-klasser, der kan komme op, anvendes typisk til at frasortere
>     hemmelige email-addresser
> -   `os2sync.api_url`: Adresse på os2sync-containeres API, typisk
>     <http://localhost:8081/api>
> -   `os2sync.top_unit_uuid`: UUID på den top-level organisation, der
>     skal overføres
> -   `os2sync.xfer_cpr`: Bestemmer om cpr-nummer skal overføres, typisk
>     true
> -   `os2sync.use_lc_db`: Bestemmer om kørslen skal anvende lora-cache
>     for hastighed
> -   `os2sync.ignored.unit_levels`: liste af unit-level-klasser, der
>     skal ignoreres i overførslen
> -   `os2sync.ignored.unit_types`: liste af unit-type-klasser, der skal
>     ignoreres i overførslen
> -   `os2sync.autowash`: sletning uden filter. Normalt slettes kun
>     afdelinger i os2sync, som er forsvundet fra OS2MO. Med autowash
>     slettes alt i os2syncs version af den administrative org, som ikke
>     vil blive overført fra os2mo.
> -   `os2sync.sync_managers`: Skriv leders uuid til orgunits. Kræver at
>     der kun er en leder pr. enhed.
> -   `os2sync.templates`: Giver mulighed for at styre formatteringen af
>     data vha. Jinja-templates.
> -   `os2sync_user_key_it_system_name`: Henter en brugers user_key fra
>     IT-system. Default er \"Active Directory\"
> -   `os2sync_uuid_from_it_systems`: Prioriteret liste af uuider på
>     IT-systemer hvorfra en bruger/enheds uuid skal hentes. Bruger MOs
>     uuid hvis denne er tom eller hvis de angivne it-systemer ikke er
>     udfyldt i MO.

## `os2sync.templates`

Denne indstilling kan bruges til at styre, hvordan felter sendes til
OS2Sync. Indstillingen består af en eller flere feltnøgler, og en
tilhørende
[Jinja-template](https://jinja.palletsprojects.com/en/2.11.x/templates/).

På nuværende tidspunkt kender programmet feltnøglerne `person.name` og
`person.user_id`, der bruges til at kontrollere, hvordan hhv.
personnavne og bruger-id\'er formatteres, når de sendes til OS2Sync.

Et eksempel på brug:

``` json
{
    "os2sync.templates": {
        "person.name": "{% if nickname -%}{{ nickname }}{%- else %}{{ name }}{%- endif %}"
    }
}
```

Denne opsætning betyder, at vi først tjekker om der er et kaldenavn
(`nickname`) registreret på personen i MO. Hvis der er, så anvendes
dette, når der skrives et personnavn til OS2Sync. Hvis ikke, så anvendes
det almindelige navn, der er registreret på personen (`name`.)

Et eksempel på brug af `person.user_id`:

``` json
{
    "os2sync.templates": {
        "person.user_id": "{{ user_key }}"
    }
}
```

Hvis OS2Sync-integrationen sættes op med denne opsætning, skriver den
MO-brugerens BVN (brugervendte nøgle) i OS2Sync-feltet `UserId`,
medmindre MO-brugeren også har et registreret IT-system af typen \"AD\".
I så fald anvendes det AD-brugernavn, der er registreret på IT-systemet.

### Integration for Aarhus LOS

#### Introduction

This integration makes it possible to fetch and import organisation and
person data from Aarhus LOS. It is built specifically for Aarhus
Kommune, as the data format is a custom format defined by them. The
format is based on OPUS, but has been subject to further processing, and
as such the original OPUS importer is incompatible

The importer connects to an external FTP provided by Aarhus Kommune, to
fetch delta files.

The importer utilizes a single piece of state in the form of a file,
containing the date of the last import run. Essentially a minimal
implementation of the run-db found in other importers

#### Setup

The integration requires minimal configuration outside of the common
default values found in the settings file:

-   `integrations.aarhus_los.ftp_url`: The url for the Aarhus Kommune
    FTP. Contains a default for the current FTP url.
-   `integrations.aarhus_los.ftp_user`: The FTP username
-   `integrations.aarhus_los.ftp_pass`: The FTP password
-   `integrations.aarhus_los.state_file`: A location for a file
    containing state across different imports.

#### Usage

The importer can be run with the following command:

`` ` python integrations/aarhus/los_import.py ``\`

The command currently takes no parameters.

The command will:

-   Perform an initial import, of all preset classes and organisation
    objects if it determines it hasn\'t taken place yet
-   Ensure a state file exists, containing the date of the last import.
-   Connect to the AAK FTP and perform the necessary import of all
    \'klasse\', \'it system\', org unit and person objects, to bring the
    system up to date.
-   Write a timestamp of a completed import into the state file

The command is designed to be idempotent, and can theoretically be run
as often as is deemed necessary.

#### Functionality

## Seed data

If no import has yet taken place, initial seed data is loaded by the
importer. This data is coded in the file
[integrations/aarhus/initial.py]{.title-ref}.

The initial data sets up:

-   a MO organisation (Aarhus Kommune)
-   a set of MO address types for use when importing organisational
    units and employees
-   a set of MO facet classes for recording the hierarchy of
    organisational units
-   an IT system (\"AZ\")

The organisational unit address types are:

-   Postadresse
-   LOS ID
-   CVR nummer
-   EAN nummer
-   P-nummer
-   WWW (URL)
-   Ekspeditionstid
-   Telefontid
-   Telefon
-   Fax
-   Email
-   Magkort
-   Alternativt navn

The employee address types are:

-   Phone
-   Email
-   Lokale

To store the hierarchy of an organisational unit, the following MO
classes are created in the facet \`org_unit_hierarchy\`:

-   [Linjeorganisation]{.title-ref}
-   [Sikkerhedsorganisation]{.title-ref}

Finally, the following facets are created, containing one placeholder
class each:

  Facet                            Placeholder class value
  -------------------------------- ---------------------------------
  [role_type]{.title-ref}          [Rolletype]{.title-ref}
  [association_type]{.title-ref}   [Tilknytningsrolle]{.title-ref}
  [leave_type]{.title-ref}         [Orlovsrolle]{.title-ref}

  : Miscellaneous facets and classes

## Loading additional classes into MO

The MO facet [org_unit_type]{.title-ref} is used to store the
organisational unit type. See
`Organisational unit type`{.interpreted-text role="ref"} for more on how
the facet [org_unit_type]{.title-ref} is used. By reading the CSV file
[STAM_UUID_Enhedstype.csv]{.title-ref}, the importer can add additional
classes to [org_unit_type]{.title-ref}. The importer reads the CSV file
this way:

  MO class field           CSV field                      Data type   Content
  ------------------------ ------------------------------ ----------- ---------------------------------------------
  [uuid]{.title-ref}       [EnhedstypeUUID]{.title-ref}   UUID        The unique ID of the facet class value
  [user_key]{.title-ref}   [Enhedstype]{.title-ref}       String      The user key (BVN) of the facet class value
  [title]{.title-ref}      [Enhedstype]{.title-ref}       String      The title of the facet class value

  : [org_unit_type]{.title-ref} classes

The MO facet [engagement_type]{.title-ref} is used to store the
different engagement types. By reading the CSV file
[STAM_UUID_Engagementstype.csv]{.title-ref}, the importer can add
additional classes to [engagement_type]{.title-ref}. The importer reads
the CSV file this way:

  MO class field           CSV field                           Data type   Content
  ------------------------ ----------------------------------- ----------- ---------------------------------------------
  [uuid]{.title-ref}       [EngagementstypeUUID]{.title-ref}   UUID        The unique ID of the facet class value
  [user_key]{.title-ref}   [Engagementstype]{.title-ref}       String      The user key (BVN) of the facet class value
  [title]{.title-ref}      [Engagementstype]{.title-ref}       String      The title of the facet class value

  : [engagement_type]{.title-ref} classes

The MO facet [engagement_job_function]{.title-ref} is used to store the
different job function types. By reading the CSV file
[STAM_UUID_Stillingsbetegnelse.csv]{.title-ref}, the importer can add
additional classes to [engagement_job_function]{.title-ref}. The
importer reads the CSV file this way:

  MO class field           CSV field                           Data type   Content
  ------------------------ ----------------------------------- ----------- ---------------------------------------------
  [uuid]{.title-ref}       [StillingBetUUID]{.title-ref}       UUID        The unique ID of the facet class value
  [user_key]{.title-ref}   [Stillingsbetegnelse]{.title-ref}   String      The user key (BVN) of the facet class value
  [title]{.title-ref}      [Stillingsbetegnelse]{.title-ref}   String      The title of the facet class value

  : [engagement_job_function]{.title-ref} classes

Additional IT systems can be added in the file
[STAM_UUID_ITSystem.csv]{.title-ref}. When the importer reads this file,
it creates MO IT systems this way:

  MO IT system field       CSV field                    Data type   Content
  ------------------------ ---------------------------- ----------- -------------------------------------
  [uuid]{.title-ref}       [ITSystemUUID]{.title-ref}   UUID        The unique ID of the IT system
  [name]{.title-ref}       [Name]{.title-ref}           String      The name of the IT system
  [user_key]{.title-ref}   [Userkey]{.title-ref}        String      The user key (BVN) of the IT system

  : IT systems

## Organisational units

The integration can create and update MO organisational units based on
the contents of [Org_inital\*.csv]{.title-ref},
[Org_nye\*.csv]{.title-ref} and [Org_ret\*.csv]{.title-ref}.

The organisational units are created in MO according to this schema:

::: {#Organisational unit type}
  MO field                           CSV field                         Data type        Content
  ---------------------------------- --------------------------------- ---------------- ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
  [uuid]{.title-ref}                 [OrgUUID]{.title-ref}             UUID             The unique ID of the organisational unit
  [user_key]{.title-ref}             [BrugervendtNøgle]{.title-ref}    String           The user-facing key of the organisational unit
  [name]{.title-ref}                 [OrgEnhedsNavn]{.title-ref}       String           The name of the organisational unit
  [parent]{.title-ref}               [ParentUUID]{.title-ref}          UUID             Determines the parent of the organisational unit, and thus its place in the organisational hierarchy.
  [org_unit_type]{.title-ref}        [OrgEnhedsTypeUUID]{.title-ref}   UUID, optional   Identifies the type of the organisational unit. If given, this is stored in the MO facet [org_unit_type]{.title-ref}.
  [org_unit_hierarchy]{.title-ref}   [Med-i-Linjeorg]{.title-ref}      Boolean          If True, the organisational unit will be marked as being part of the hierarchy \"Linjeorganisation\". This is stored in the MO facet [org_unit_hierarchy]{.title-ref}.

  : Organisational units
:::

Additionally, the [Org\_\*.csv]{.title-ref} files can contain
information which will be imported into MO as addresses of the given
organisational unit. The following CSV fields will be recorded as
addresses in MO:

  MO address type                 CSV field                     Data type   Content
  ------------------------------- ----------------------------- ----------- ------------------------------------------------------------------------------------------------------------------------------------------------
  [LOSID]{.title-ref}             [LOSID]{.title-ref}           String      The LOS ID of the organisational unit
  [CVRUnit]{.title-ref}           [CVR]{.title-ref}             String      The CVR number of the organisational unit
  [EANUnit]{.title-ref}           [EAN]{.title-ref}             String      The EAN number of the organisational unit
  [PNumber]{.title-ref}           [P-Nr]{.title-ref}            String      The P-number of the organisational unit
  [SENumber]{.title-ref}          [SE-Nr]{.title-ref}           String      The SE-number of the organisational unit
  [intdebit]{.title-ref}          [IntDebitor-Nr]{.title-ref}   String      The SE-number of the organisational unit
  [UnitMagID]{.title-ref}         [MagID]{.title-ref}           String      The \"Magkort\" of the organisational unit
  [AddressMailUnit]{.title-ref}   [PostAdresse]{.title-ref}     DAR UUID    The postal address of the organisational unit. The textual address will be looked up in DAR and its DAR UUID will be stored as its MO address.

  : Organisational unit addresses

Finally, the [Org\_\*.csv]{.title-ref} files contain the fields
[StartDato]{.title-ref} and [SlutDato]{.title-ref}. These are used by
the importer to determine the [validity]{.title-ref} of the
organisational units and addresses created. Each [validity]{.title-ref}
consists of [from]{.title-ref} and [to]{.title-ref} dates in MO.

If multiple lines in the CSV files refer to the same organisational unit
UUID, and have identical properties from one line to the next (e.g. the
same name or the same LOS ID), the importer does not create multiple MO
objects, but rather merges the MO objects into one object, whose start
date will be the earliest [StartDato]{.title-ref} and whose end date
will be the latest [SlutDato]{.title-ref}.
