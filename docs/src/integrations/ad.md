---
title: Legacy integration
---

# Integration til Active Directory

## Indledning

Denne integration gør det muligt at læse information fra en lokal AD
installation med henblik på at anvende disse informationer ved import
til MO.

## Opsætning

For at kunne afvikle integrationen kræves en række opsætninger af den
lokale server.

Integrationen går via i alt tre maskiner:

1.  Den lokale server, som afvikler integrationen (typisk MO serveren
    selv).
2.  En remote management server som den lokale server kan kommunikere
    med via Windows Remote Management (WinRM). Denne kommunikation
    autentificeres via Kerberos. Der findes en vejledning til
    [opsætning med kerberos her](https://os2mo.readthedocs.io/en/latest/_static/AD%20-%20OS2MO%20ops%C3%A6tnings%20guide.pdf).
    Alternativt kan der autentificeres med ntlm over https. Denne
    opsætning beskrives herunder.
3.  AD serveren.

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

- Første AD i listen (index 0) anvendes til skrivning (hvis
  skrivning er aktiveret) og til integrationer, som endnu ikke er
  forberedt for flere ad'er.
- Alle AD'er anvendes af ad_sync til opdatering af og skabelse af
  adresser, itsystemer

### Opsætning af ntlm over https

For at kunne autentificere med ntlm over https kræver det at
settingsfilen indeholder brugernavn og password til en systembruger fra
et domæne (modsat lokalt oprettet bruger). Derudover skal det i
settings.json specificeres at metoden skal være 'ntlm'. Se bekrivelsen
af parametre herunder. Brugeren skal desuden have
administratorrettigheder på windowsserveren, samt rettigheder til at
læse og evt. skrive i AD. Dette gælder også feltet der indeholder CPR
numre der kan være indstillet til 'confidential'. I så fald skal
rettigheden gives gennem programmet ldp.

SSL certifikatet skal dannes via en windows server der er konfigureret
som CA server. Det er en forudsætning at det oprettes med: _Intended
purpose: Server Authentication_ Fra WinRM serveren åbnes
"certificate management" hvori der kan anmodes om et nyt certifikat.
Her skal som minimum _Common Name_ udfyldes med serverens
hostnavn. Under det nye certifikats 'Egenskaber' findes dens
'CertificateThumbprint'.

Hvis der allerede er opsat en winrm listener på HTTPS, skal den fjernes
først:

```powershell
winrm remove winrm/config/Listener?Address=*+Transport=HTTPS
```

Hvis ikke det allerede er sat op kan winrm sættes til at bruge https
med:

```powershell
winrm quickconfig -transport:https
```

Konfigurer WinRM til at bruge certifikatet:

```powershell
winrm set winrm/config/Listener?Address=*+Transport=HTTPS@{Hostname="hostname";
CertificateThumbprint="02E4XXXXXXXXXXXXXXXXXXXXXXXXXX"}
```

Derefter skal winrm sættes op til at tillade NTLM, men ikke ukrypteret:

```powershell
winrm set winrm/config/service/auth '@{Negotiate="true"}'
winrm set winrm/config/service '@{AllowUnencrypted="false"}'
```

Der kan også være behov for at åbne en port i firewall med:

```powershell
netsh advfirewall firewall add rule name="WinRM-HTTPS" dir=in
localport=5986 protocol=TCP action=allow
```

Nu skulle der være adgang til winrm med ntlm, krypteret med https, via
port 5986.

### Fælles parametre

- `integrations.ad.winrm_host`: Hostname på remote mangagent server

### For hvert AD angives

- `search_base`: Search base, eksempelvis
  'OU=enheder,DC=kommune,DC=local'

- `cpr_field`: Navnet på feltet i AD som indeholder cpr nummer.

- `cpr_separator`: Angiver en eventuel separator mellem fødselsdato
  og løbenumre i cpr-feltet i AD. Hvis der ikke er en separator,
  angives en tom streng.

- `sam_filter`: Hvis denne værdi er sat, vil kun det være muligt at
  cpr-fremsøge medarbejder som har denne værdi foranstillet i
  SAM-navn. Funktionen muliggør at skelne mellem brugere og
  servicebrugere som har samme cpr-nummer.

- `caseless_samname`: Hvis denne værdi er `true` (Default) vil
  sam_filter ikke se forskel på store og små bogstaver.

- `system_user`: Navnet på den systembruger som har rettighed til at
  læse fra AD.

- `password`: Password til samme systembruger.

- `properties`: Liste over felter som skal læses fra AD. Angives som
  en liste i json-filen.

- `method`: Metode til autentificering - enten ntlm eller kerberos.
  Hvis denne ikke er angivet anvendes kerberos.

- `servers` - domain controllere for denne ad.

- `pseudo_cprs`: Liste af ekstra startværdier for cpr-numre. Bruges til at læse AD brugere med cprnummer
  der starter med et tal der ikke er mellem 01 og 31 - Fiktive/systembrugere)

## Test af opsætningen

Der følger med AD integrationen et lille program, `test_connectivity.py`
som tester om der kan læses fra eller skrives til AD, og dermed at
autentificering er konfigureret korrekt. Programmet afvikles med en af
to parametre:

- `--test-read-settings`
- `--test-write-settings`

**En test af læsning foregår i flere trin:**

- Der testes for om Remote Management serveren kan nås og
  autentificeres med metoden specificeret i settings - enten
  Kerberos (standard) eller med ntlm.
- Der testes om det er muligt af afvikle en triviel kommando på AD
  serveren.
- Der testes for, at en søgning på alle cpr-numre fra 31. november
  returnerer nul resultater.
- Der testes for, at en søging på cpr-numre fra den 30. i alle
  måneder returnerer mindst et resultat. Hvis der ikke returneres
  nogen, er fejlen sandsynligvis en manglende rettighed til at
  læse feltet med cpr-nummer i AD. Dette kan bla. skyldes at
  rettigheder til confidential attributes skal sættes i ldp
  programmet.
- Der testes om de returnerede svar indeholder mindst et eksempel
  på disse tegn: æ, ø, å, @ som en test af at tegnsættet er
  korrekt sat op.

**En test af skrivning foregår efter denne opskrift:**

- Der testes for om de nødvendige værdier er til stede i
  `settings.json`, det drejer sig om nøglerne:

  - `integrations.ad.write.uuid_field`: AD feltet som rummer MOs
    bruger-UUID
  - `integrations.ad.write.level2orgunit_field`: AD feltet hvor MO
    skriver den primære organisatoriske gruppering (direktørområde,
    forvaltning, etc.) for brugerens primære engagement.
  - `integrations.ad.write.org_unit_field`: Navnet på det felt i
    AD, hvor MO skriver enhedshierakiet for den enhed, hvor
    medarbejderen har sin primære ansættelse.
  - `integrations.ad.write.upn_end`: Endelse for feltet UPN.
  - `integrations.ad.write.level2orgunit_type`: UUID på den klasse
    som beskriver at en enhed er den primære organisatoriske
    gruppering (direktørområde, forvaltning, etc.). Dette kan være en
    enhedstype eller et enhedsniveau.

- Der udrages et antal tilfældige brugere fra AD (mindst 10), og
  disse tjekkes for tilstædeværelsen af de tre AD felter beskrevet i:

  1.  `integrations.ad.write.uuid_field`,
  2.  `integrations.ad.write.level2orgunit_field`
  3.  `integrations.ad.write.org_unit_field`

      Hvis hvert felt findes hos mindst én bruger, godkendes den lokale
      AD opsætning.

- Længden af cpr-numrene hos de tilfældige brugere testes for om de
  har den forventede længde, 10 cifre hvis der ikke anvendes en
  separator, 11 hvis der gør. Det er et krav for at integrationen
  kan køre korrekt, at alle cpr-numre anvender samme (eller ingen)
  separator.

Hvis disse tests går igennem, anses opsætningen for at være klar til AD
skriv integrationen.

### Brug af integrationen

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

```python
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

Nogle steder har man flere konti med samme cprnummer i AD'et. For at
vælge den primære, som opdaterer / opdateres fra MO, kan man anvende et
sæt nøgler i settingsfilen:

- `integrations.ad.discriminator.field` et felt i det pågældende AD,
  som bruges til at afgøre hvorvidt denne konto er den primære
- `integrations.ad.discriminator.values` et sæt strenge, som matches
  imod `integrations.ad.discriminator field`
- `integrations.ad.discriminator.function` kan være 'include' eller
  'exclude'

Man definerer et felt, som indeholder en indikator for om kontoen er den
primære, det kunnne f.x være et felt, man kaldte xBrugertype, som kunne
indeholde "Medarbejder".

Hvis man i dette tilfælde sætter
`integrations.ad.discriminator.function` til `include` vil kontoen
opfattes som primær hvis 'Medarbejder' også findes i
`integrations.ad.discriminator.values`.

Opfattes mere end en konto som primær tages den første, man støder på. I
så fald fungerer `integrations.ad.discriminator.values` som en
prioriteret liste.

Findes nøglen `integrations.ad.discriminator.field`, skal de andre to
nøgler også være der. Findes den ikke, opfattes alle AD-konti som
primære.

### Skrivning til AD

Der udvikles i øjeblikket en udvidelse til AD integrationen som skal
muliggøre at oprette AD brugere og skrive information fra MO til
relevante felter.

Hvis denne funktionalitet skal benyttes, er der brug for yderligere
parametre som skal være sat når programmet afvikles:

- `servers` fra `integrations.ad[0]`: Liste med de DC'ere som
  findes i kommunens AD. Denne liste anvendes til at sikre at
  replikering er færdiggjort før der skrives til en nyoprettet
  bruger.
- `integrations.ad.write.uuid_field`: Navnet på det felt i AD, hvor
  MOs bruger-uuid skrives.
- `integrations.ad.write.level2orgunit_field`: Navnet på det felt i
  AD, hvor MO skriver navnet på den organisatoriske hovedgruppering
  (Magistrat, direktørområde, eller forvalting) hvor medarbejderen
  har sin primære ansættelse.
- `integrations.ad.write.org_unit_field`: Navnet på det felt i AD,
  hvor MO skriver enhedshierakiet for den enhed, hvor medarbejderen
  har sin primære ansættelse.
- `integrations.ad.write.primary_types`: Sorteret lister over
  uuid'er på de ansættelsestyper som markerer en primær ansættelse.
  Jo tidligere et engagement står i listen, jo mere primært anses
  det for at være.
- `integrations.ad.write.level2orgunit_type`: uuid på den enhedstype
  som angiver at enheden er en organisatorisk hovedgruppering og
  derfor skal skrives i feltet angivet i
  `integrations.ad.write.level2orgunit_field`.

## Skabelse af brugernavne

For at kunne oprette brugere i AD, er det nødvendigt at kunne tildele et
SamAccountName til de nye brugere. Til dette formål findes i modulet
`user_names` klassen `CreateUserNames`. Programmet startes ved at
instantiere klassen med en liste over allerede reserverede eller
forbudte navne som parametre, og det er herefter muligt at forespørge AD
om en liste over alle brugenavne som er i brug, og herefter er programet
klar til at lave brugernavne.

```python
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
_integrations.ad_writer.user_names.disallowed.csv_path_

For at læse fra en database sættes følgende settings:

- "integrations.ad_writer.user_names.disallowed.sql_connection_string" - https://docs.sqlalchemy.org/en/14/core/engines.html
- "integrations.ad_writer.user_names.disallowed.sql_table_name"
- "integrations.ad_writer.user_names.disallowed.sql_column_name"

## Håndtering af hierarkisk AD'er ved hjælp af PowerShell-script

Nedenfor beskrives opsætning og funktionalitet.

### Opsætning

ADStruktur.ps1 skal sættes op med flg. indstillinger:

- $SettingOURoot = "OU=Rod,DC=kommune,DC=dk"
  Skal være oprettet i forvejen. Angiver rod-enheden hvor scriptet skal arbejde fra.
- $SettingOUInactiveUsers = "OU=Nye OS2MO brugere,OU=Rod,DC=kommune,DC=dk"
  Skal være oprettet i forvejen. Angiver OU'en, hvor ADSkriv opretter inaktive AD-brugere.
- $SettingAutoritativOrg = "extensionAttribute14"
  Angiver navnet på den AD-brugerattribut, som indeholder brugerens organisatoriske placering ("sti") fra MO.

### Funktionalitet

En normal afvikling af scriptet vil herefter gøre flg.:

1. Indlæse alle AD-brugere i og under rodenheden ($SettingOURoot)
2. For hver af disse AD-brugere tjekkes det, om brugeren allerede findes i en OU, der svarer til brugerens organisatoriske placering i MO (= den sti, der evt. står i $SettingAutoritativOrg.) AD-brugere uden en MO-sti gøres der ikke yderligere ved.

- Hvis AD-brugeren er sat som inaktiv (Enabled = $false) flyttes AD-brugeren til OU'en for inaktive brugere ($SettingOUInactiveUsers.)
- Ellers flyttes AD-brugeren til en OU svarende til MO-stien. Såfremt der mangler OU'er i AD, oprettes disse. Dette sker under roden angivet i $SettingOURoot.

3. Slutteligt fjernes alle tomme OU'er under rodenheden ($SettingOURoot), dog med undtagelse af enheden til inaktive brugere ($SettingOUInactiveUsers.)

Processen i skridt 2.2 kan illustreres således:

Lad os sige at AD-brugeren "bent" har MO-stien "Kommune > Afdeling 1 > Enhed A". I AD'et findes kun "Kommune" under rodenheden. Der vil så blive oprettet OU'er for hhv. "Afdeling 1" og "Enhed A", således at "Kommune" indeholder "Afdeling 1", der igen indeholder "Enhed A". AD-brugeren "bent" vil så blive flyttet til "Enhed A".

For at teste, mv. er det også muligt at afvikle scriptet for en enkelt AD-bruger. Denne AD-bruger kan befinde sig hvorsomhelst i AD'et. Skridt 1 vil så skippes, mens skridt 2, 2.1/2.2 og 3 udføres for den angivne AD-bruger.

### Kilde

https://github.com/OS2mo/ps-services/blob/master/Holstebro/ADStruktur.ps1

## Synkronisering

Der eksisterer (udvikles) to synkroniseringstjenester, en til at
synkronisere felter fra AD til MO, og en til at synkronisere felter fra
MO til AD.

### AD til MO

Synkronisering fra AD til MO foregår via programmet `ad_sync.py`.

Programmet opdaterer alle værdier i MO i henhold til den feltmapning,
som er angivet i _settings.json_. Det er muligt at
synkronisere adresseoplysninger, samt at oprette et IT-system på
brugeren, hvis brugeren findes i AD, men endnu ikke har et tilknyttet
IT-system i MO. Desuden er det muligt at synkronisere et AD-felt til et
felt på brugerens primærengagement (typisk stillingsbetegnelsen).

`ad_sync.py` er ejer over det MO-data, som programmet skriver til.

Hvis `ad_sync.py` er sat op til udlæse fra flere AD-servere: Husk at
efterfølgende AD kan overskrive. Derfor: Anvend ikke samme klasser,
itsystemer eller extensionfelter i flere af de specificerede AD'er

Et eksempel på en feltmapning angives herunder:

```json
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
angives en synlighed, som kan antage værdierne _PUBLIC_,
_INTERNAL_, _SECRET_ eller _null_,
hvilket angiver at synligheden i MO sættes til hhv. offentlig, intern,
hemmelig, eller ikke angivet. UUID'erne identificerer de adresseklasser
i MO, som AD-felterne skal mappes til.

Hvis der findes flere adresser i MO med samme type og synlighed, vil
programmet opdatere den først fundne MO-adresse, og afslutte de andre
matchende MO-adresser.

Hvis der for en given bruger er felter i feltmapningen, som ikke findes
i AD, vil disse felter blive sprunget over, men de øvrige felter vil
stadig blive synkroniseret.

Selve synkroniseringen foregår ved at programmet først udtrækker
samtlige medarbejdere fra MO, der itereres hen over denne liste, og
information fra AD'et slås op med cpr-nummer som nøgle. Hvis brugeren
findes i AD, udlæses alle parametre angivet i
_integrations.ad.properties_ og de af dem, som figurerer i
feltmapningen, synkroniseres til MO.

Integrationen vil som udgangspunkt ikke synkronisere fra et eventuelt
skole AD, med mindre nøglen _integrations.ad.skip_school_ad_to_mo_
sættes til _false_.

Da AD ikke understøtter gyldighedstider, antages alle informationer
uddraget fra AD at gælde fra 'i dag' og til evig tid. Den eneste
undtagelse til dette er ved afslutning af deaktiverede AD brugere.

Deaktiverede AD brugere kan håndteres på forskellige måder. Som
udgangspunkt synkroniseres de på præcis samme vis som almindelige
brugere, med mindre nøglen _ad_mo_sync_terminate_disabled_
er sat til _True_. Hvis dette er tilfælde ophører den
automatiske synkronisering, og deaktiverede brugere får i stedet deres
AD data 'afsluttet'. Ved afslutning forstås at brugerens AD
synkroniserede adresser og it-systemer flyttes til fortiden, såfremt de
har en åben slutdato.

Hvis nøglen _ad_mo_sync_terminate_disabled_ ikke er
fintmasket nok, f.eks. fordi deaktiverede brugere dækker over både
brugere som er under oprettelse og brugere som er under nedlæggelse, kan
et være nødvendigt at tage stilling til om en given deaktiveret bruger
skal nedlægges eller synkroniseres på baggrund af AD dataene fra den
enkelte bruger.

Dette understøttes vha.
_ad_mo_sync_terminate_disabled_filters_ nøglen. Denne nøgle
indeholder en liste af jinja templates. Disse templates kan returnere en
sand værdi for at terminere brugeren, eller en falsk værdi for at
synkronisere brugeren. Kun hvis samtlige filtre returnere sand vil
brugeren blive termineret, hvis blot ét af filtrene returnerer falsk vil
brugeren i stedet blive synkroniseret. Resultaterne for evaluering af
filtrene sammenholdes altså med en 'AND' operation.

Værdierne der vurderes som sande er "yes", "true", "1" og "1.0".

**Eksempel 1:**

> Vi ønsker kun at terminere brugere, hvis MO UUID starter med 8 nuller,

    f.eks.: '00000000-e4fe-47af-8ff6-187bca92f3f9'.

> For at opnå dette kan vi lave følgende konfiguration:

> ```json
>
> ```

    {
        "ad_mo_sync_terminate_disabled_filters": [
            "{{ uuid.startswith('00000000') }}"
        ]
    }
    ```

**Eksempel 2:**

> Vi holder i vores AD et extensionAttribute felt til livtidstilstanden

    af brugerne. Lad os antage at der er tale om feltet
    *extensionAttribute3*, der kan holde værdierne:

> - _"Ny bruger"_: Som skal synkroniseres
> - _"På orlov"_: Som skal synkroniseres
> - _"Under sletning"_: Som skal termineres

> Vi ønsker altså at termineringsadfærden skal afledes af feltets værdi

    i AD.

> For at opnå dette kan vi lave følgende konfiguration:

> ```json
>
> ```

    {
        "ad_mo_sync_terminate_disabled_filters": [
            "{{ ad_object['extenionAttribute3'] == 'Under sletning' }}"
        ]
    }
    ```

Såfremt nogle brugere hverken ønskes terminerede eller synkroniserede
kan de filtreres fra vha. _ad_mo_sync_pre_filters_ nøglen.
Denne nøgle indeholder en liste af jinja templates. Disse templates kan
returnere en sand værdi for at beholde brugeren, eller en falsk værdi
for filtrere brugeren fra. Kun hvis samtlige filtre returnerer sand vil
brugeren blive beholdt, hvis blot ét af filtrene returnerer falsk vil
brugeren i stedet blive filtreret fra. Resultaterne for evaluering af
filtrene sammenholdes altså med en 'AND' operation.

> **Eksempel 1:**

> I det forrige Eksempel 2 så vi på en situation hvor et AD felt

    benyttes til at afgøre om hvorvidt brugere skulle termineres eller
    synkroniseres.

> Lad os antage at vi stadig har konfigurationen herfra i vores

    settings.json fil, men nu ønsker slet ikke at synkronisere
    *"På orlov"* brugerne overhovedet.

> For at opnå dette kan vi lave følgende konfiguration:

> ```json
>
> ```

    {
        "ad_mo_sync_terminate_disabled_filters": [
            "{{ ad_object['extenionAttribute3'] == 'Under sletning' }}"
        ],
        "ad_mo_sync_pre_filters": [
            "{{ ad_object['extenionAttribute3'] != 'På orlov' }}"
        ]
    }
    ```

Foruden terminering af MO kontos hvor AD brugeren er deaktiveret, kan MO
kontos hvor en tilsvarende AD bruger ikke kan findes, også termineres
automatisk. Denne funktionalitet aktiveres ved at sætte med nøglen
_ad_mo_sync_terminate_missing_ til _True_.

Disse brugere med manglende AD konti kan desuden begrænses således at
der kun termineres brugere der tidligere har været oprettet i AD. Dette
sker ved at tjekke om brugerens MO konti har et AD it-system svarende
til konfigurationen i `it_systems - samAccountName`. Denne adfærd kan
slås fra ved at sætte nøglen:
_ad_mo_sync_terminate_missing_require_itsystem_ til
_False_, hvorefter **SAMTLIGE MO** brugere uden en tilhørende AD
konti vil blive termineret. Dette vil typisk betyde at et stort antal
historiske brugere vil få termineret deres adresser og itsystemer.

Slutteligt skal det nævnes, at implemeneringen af synkroniseringen
understøtter muligheden for at opnå en betydelig hastighedsforbering ved
at tillade direkte adgang til LoRa, denne funktion aktiveres med nøglen
_integrations.ad.ad_mo_sync_direct_lora_speedup_ og
reducerer kørselstiden betragteligt. Hvis der er få ændringer vil
afviklingstiden komme ned på nogle få minutter.

### MO til AD

Synkronisering fra MO til AD foregår således:

- der itereres hen over alle AD-brugere
- hver enkelt AD-bruger slås op i MO via feltet angivet i nøglen
  _integrations.ad.write.uuid_field_
- data om den tilsvarende MO-bruger synkroniseres til AD i henhold til
  konfigurationen (se nedenfor)

AD-integrationen stiller et antal MO-værdier til rådighed, som det er
muligt at synkronisere til felter på AD-brugere. Flere MO-værdier kan
tilføjes, efterhånden som integrationen udvikles. Her er en liste over
de MO-værdier, integrationen stiller til rådighed i dag:

#### Mo-værdier

| Feltnavn            | Beskrivelse af indhold                                                                                                                                                                             |
| ------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `uuid`              | Brugerens UUID i MO.                                                                                                                                                                               |
| `employment_number` | Lønsystemets ansættelsesnummer for medarbejderens primære engagement.                                                                                                                              |
| `title`             | Stillingsbetegnelsen for brugerens primære engagement.                                                                                                                                             |
| `start_date`        | Startdato for aktuelle engagement i MO.                                                                                                                                                            |
| `end_date`          | Slutdato for aktuelle engagement i MO. Hvis en ansættelse ikke har nogen kendt slutdato, angives 9999-12-31. For at få skrevet afsluttede engagementers slutdato anvendes jobbet _ad_fix_enddate_. |
| `name`              | Brugerens navn, opdelt i fornavn og efternavn. Fornavn kan fx tilgås via `mo_values['name'][0]`, og efternavn via `mo_values['name'][1]`.                                                          |
| `full_name`         | Brugerens fulde navn, dvs. fornavn og efternavn samlet i et felt.                                                                                                                                  |
| `nickname`          | Brugerens kaldenavn, opdelt i fornavn og efternavn. Fornavn kan fx tilgås via `mo_values['nickname'][0]`, og efternavn via `mo_values['nickname'][1]`.                                             |
| `full_nickname`     | Brugerens fulde kaldenavn, dvs. fornavn og efternavn samlet i eet felt.                                                                                                                            |
| `cpr`               | Brugerens CPR-nummer.                                                                                                                                                                              |
| `unit`              | Navn på enheden for brugerens primære engagement.                                                                                                                                                  |
| `unit_uuid`         | UUID på enheden for brugerens primære engagement.                                                                                                                                                  |
| `unit_user_key`     | Brugervendt nøgle for enheden for brugerens primære engagement. Dette vil typisk være lønsystemets korte navn for enheden.                                                                         |
| `unit_public_email` | Email på brugerens primære enhed med synligheden `offentlig`.                                                                                                                                      |
| `unit_secure_email` | Email på brugerens primære enhed med synligheden `hemmelig`. Hvis enheden kun har email-adresser uden angivet synlighed, vil den blive angivet her.                                                |
| `unit_postal_code`  | Postnummer for brugerens primære enhed.                                                                                                                                                            |
| `unit_city`         | By for brugerens primære enhed.                                                                                                                                                                    |
| `unit_streetname`   | Gadenavn for brugerens primære enhed.                                                                                                                                                              |
| `location`          | Fuld organisatorisk sti til brugerens primære enhed.                                                                                                                                               |
| `level2orgunit`     | Den organisatoriske hovedgruppering (magistrat, direktørområde, eller forvaltning) som brugerens primære engagement hører under.                                                                   |
| `manager_name`      | Navn på leder for brugerens primære engagement.                                                                                                                                                    |
| `manager_cpr`       | CPR-nummer på leder for brugerens primære engagement.                                                                                                                                              |
| `manager_sam`       | `SamAccountName` for leder for brugerens primære engagement.                                                                                                                                       |
| `manager_mail`      | Email på lederen for brugerens primære engagement.                                                                                                                                                 |
| `itsystems`         | Et dictionary fra it-systems UUID til itsystemer. I python-termer: {"opus_uuid": {"username": "brugernavn", "from_date": "1930-01-01"}}                                                            |

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

Udover ovenstående felter er `sync_timestamp` til rådighed. Hvis denne
sættes i feltmapningen vil ad_writer udfylde feltet med tidsstemplet for
hvornår en bruger sidst blev synkroniseret fra MO.

Synkroniseringen til AD foretages i henhold til en lokal feltmapning, som eksempelvis kan se ud som dette:

```json
"integrations.ad_writer.mo_to_ad_fields": {
    "unit_postal_code": "postalCode",
    "unit_city": "l",
    "unit_user_key": "department",
    "unit_streetname": "streetAddress",
    "unit_public_email": "extensionAttribute3",
    "title": "Title",
    "unit": "extensionAttribute2"
}
```

Formatet for `mo_to_ad_fields` er: MO-felt -> AD-felt. Altså mappes _unit_public_email_
fra MO til _extensionAttribute3_ i AD i ovenstående eksempel.

Som et alternativ til den ovennævnte direkte 1-til-1 feltmapning (_mo_to_ad_fields_) er
der også mulighed for en mere fleksibel felt-mapning vha. såkaldte _Jinja_-skabeloner.
Dette giver yderligere muligheder for at tilpasse formatteringen af de enkelte værdier,
der skrives i AD. Se eventuelt [her](https://jinja.palletsprojects.com/en/2.11.x/templates/)
(linket er på engelsk.).

Standard-opsætningen af AD-integrationen indeholder flg. Jinja-templates:

```json
"integrations.ad_writer.template_to_ad_fields": {
    "Name": "{{ mo_values['name'][0] }} {{ mo_values['name'][1] }} - {{ user_sam }}",
    "Displayname": "{{ mo_values['name'][0] }} {{ mo_values['name'][1] }}",
    "Givenname": "{{ mo_values['name'][0] }}",
    "Surname": "{{ mo_values['name'][1] }}",
    "EmployeeNumber": "{{ mo_values['employment_number'] }}",
    "extensionAttribute7": "{{ mo_values['itsystems'].get('123e4567-e89b-12d3-a456-426614174000', {}).get('username') }}",
}
```

De felter, der er tilgængelige i `mo_values` , er beskrevet her: [MO-værdier](#mo-vrdier).
Desuden kan felter + faktiske værdier (for en given bruger) ses ved at køre følgende kommando:

```bash
python -m integrations.ad_integration.ad_writer --mo-values MO_BRUGER_UUID_HER --ignore-occupied-names
```

Med denne standard-opsætning oprettes der brugere i AD på denne form:

<figcaption>Eksempel</figcaption>

| AD-felt        | Indhold                                |
| -------------- | -------------------------------------- |
| Name           | “Fornavn Efternavn - Sam_account_name” |
| Displayname    | "Fornavn Efternavn"                    |
| Givenname      | "Fornavn"                              |
| Surname        | "Efternavn"                            |
| EmployeeNumber | "A1234"                                |

Standard-opsætningen kan udvides eller erstattes. Eksempelvis kan opsætningen udvides til også
at udfylde postnummer, afdeling, gadenavn og en _extension attribute_ således:

```json
"integrations.ad_writer.template_to_ad_fields": {
    "# standard-felter": "",
    "Name": "{{ mo_values['name'][0] }} {{ mo_values['name'][1] }} - {{ user_sam }}",
    "Displayname": "{{ mo_values['name'][0] }} {{ mo_values['name'][1] }}",
    "GivenName": "{{ mo_values['name'][0] }}",
    "SurName": "{{ mo_values['name'][1] }}",
    "EmployeeNumber": "{{ mo_values['employment_number'] }}",

    "# yderligere felter": "",
    "postalCode": "{{ mo_values['unit_postal_code'] }}",
    "department": "{{ mo_values['unit_user_key'] }}",
    "streetName": "{{ mo_values['unit_streetname'].split(' ')[0] }}",
    "extensionAttribute3": "{{ mo_values['unit_public_email']|default('all@afdeling.dk') }}",
    "extensionAttribute4": "{{ sync_timestamp }}"
}
```

Det er værd at bemærke, at begge konfigurationsmuligheder (_mo_to_ad_fields_ og
_template_to_ad_fields_) benytter Jinja-skabeloner som grundlag for deres virkemåde.
Det er altså ækvivalent at skrive henholdsvis:

```json
"integrations.ad_writer.mo_to_ad_fields": {
    "unit_postal_code": "postalCode",
}
```

og:

```json
"integrations.ad_writer.template_to_ad_fields": {     "
    postalCode": "{{ mo_values['unit_postal_code'] }}",
}
```

Da førstnævnte konfiguration konverteres til sidstnævnte internt i programmet.

Når man skriver Jinja-templates i _template_to_ad_fields_ er data om MO-brugeren
tilgængelige i objektet `mo_values`(som vist i eksemplerne ovenfor). Samtidig er
data om AD-brugeren (før skrivning) ligeledes tilgængelige i objektet `ad_values`.
Når koden _opretter_ en ny AD-bruger, er `ad_values` tilgængeligt for Jinja-templates,
men er et tomt objekt. Dette kan fx anvendes til kun at synkronisere data fra MO til
AD, såfremt der ikke allerede står noget i det pågældende AD-felt:

```json
"integrations.ad_writer.template_to_ad_fields": {
    "titel": "{{ ad_values.get('titel') or mo_values['title'] }}",
}
```

I ovenstående eksempel vil værdien i AD-feltet _titel_ kun blive udfyldt med MO's
tilsvarende _title_ hvis AD-brugeren ikke allerede har en titel. Og det har
AD-brugeren ikke, såfremt programmet netop er i færd med at oprette selvsamme
AD-bruger.

## Afvikling af PowerShell templates

Det er muligt at angive PowerShell kode hvor visse værdier angives med abstrakte
refrencer til MO, som så på runtime vil bive udfyldt med de tilhørende værdier for
det person det drejer sig om. For øjeblikket understøttes disse variable:

- `%OS2MO_AD_BRUGERNAVN%`
- `%OS2MO_BRUGER_FORNAVN%`
- `%OS2MO_BRUGER_EFTERNAVN%`
- `%OS2MO_BRUGER_CPR%`
- `%OS2MO_LEDER_EMAIL%`
- `%OS2MO_LEDER_NAVN%`
- `%OS2MO_BRUGER_ENHED%`
- `%OS2MO_BRUGER_ENHED_UUID%`

Hvis et script indeholder andre nøgler på formen _%OS2MO\_ ... %_ vil der returneres en
fejlmeddelelse (exception hvis det afvikles som en integration), med mindre disse
variable er udkommenteret.

Integrationen forventer at scripts befinder sig i mappen _scripts_ i en undermappe til
integrationen selv, og alle scripts skal have en _ps_template_ som filendelse. Den
tekniske platform for afvikling af scripts er den samme som for den øvrige AD
integration; scriptet sendes til remote management serveren, som afvikler scriptet.
Bemærk at scripts i denne kategori ikke nødvendigvis behøver have direkte kontakt med
AD, men vil kunne anvends til alle formål hvor der er behov for at afvikle PowerShell
med værdier fra MO.

## Opsætning for lokal brug af integrationen

Flere af værktøjerne i AD integrationen er udstyret med et kommandolinjeinterface,
som kan anvendes til lokale tests. For at anvende dette er skal tre ting være på
plads i det lokale miljø:

1.  En lokal bruger med passende opsætning af kerberos til at kunne tilgå remote
    management serveren.
2.  Den nødvendige konfiguration skal angives i `settings.json`.
3.  Et lokalt pythonmiljø med passende afhængigheder.

Angående punkt 1 skal dette opsættes af den lokale IT organisation, hvis man har
fulgt denne dokumentation så langt som til dette punkt, er der en god sandsynlighed
for at man befinder sig i et miljø, hvor dette allerede er på plads.

Punkt 2 gøres ved at oprette filen`settings.json`under mappen `settings` Et eksempel
på sådan en fil kunne se sådan ud:

```json
{
  "mox.base": "http://localhost:8080",
  "mora.base": "http://localhost:5000",
  "municipality.name": "Kommune Kommune",
  "municipality.code": 999,
  "integrations.SD_Lon.import.too_deep": ["Afdelings-niveau"],
  "integrations.SD_Lon.global_from_date": "2019-10-31",
  "integrations.SD_Lon.sd_user": "SDUSER",
  "integrations.SD_Lon.sd_password": "SDPASSWORD",
  "integrations.SD_Lon.institution_identifier": "AA",
  "integrations.SD_Lon.import.run_db": "/home/mo/os2mo-data-import-and-export/settings/change_at_runs.db",
  "address.visibility.secret": "53e9bbec-dd7b-42bd-b7ee-acfbaf8ac28a",
  "address.visibility.internal": "3fe99cdd-4ab3-4bd1-97ad-2cfb757f3cac",
  "address.visibility.public": "c5ddc7d6-1cd2-46b0-96de-5bfd88db8d9b",
  "integrations.ad.winrm_host": "rm_mangement_hostname",
  "integrations.ad.search_base": "OU=KK,DC=kommune,DC=dk",
  "integrations.ad.system_user": "serviceuser",
  "integrations.ad.password": "sericeuser_password",
  "integrations.ad.cpr_field": "ad_cpr_field",
  "integrations.ad.write.servers": ["DC1", "DC2", "DC3", "DC4", "DC5"],
  "integrations.ad.write.level2orgunit_type": "cdd1305d-ee6a-45ec-9652-44b2b720395f",
  "integrations.ad.write.primary_types": [
    "62e175e9-9173-4885-994b-9815a712bf42",
    "829ad880-c0b7-4f9e-8ef7-c682fb356077",
    "35c5804e-a9f8-496e-aa1d-4433cc38eb02"
  ],
  "integrations.ad_writer.mo_to_ad_fields": {
    "unit_user_key": "department",
    "level2orgunit": "company",
    "title": "Title",
    "unit": "extensionAttribute2"
  },
  "integrations.ad.write.uuid_field": "sts_field",
  "integrations.ad.write.level2orgunit_field": "extensionAttribute1",
  "integrations.ad.write.org_unit_field": "extensionAttribute2",
  "integrations.ad.properties": [
    "manager",
    "ObjectGuid",
    "SamAccountName",
    "mail",
    "mobile",
    "pager",
    "givenName",
    "l",
    "sn",
    "st",
    "cn",
    "company",
    "title",
    "postalCode",
    "physicalDeliveryOfficeName",
    "extensionAttribute1",
    "extensionAttribute2",
    "ad_cpr_field"
  ],
  "integrations.ad.ad_mo_sync_mapping": {
    "user_addresses": {
      "telephoneNumber": ["51d4dbaa-cb59-4db0-b9b8-031001ae107d", "PUBLIC"],
      "pager": ["956712cd-5cde-4acc-ad0a-7d97c08a95ee", "SECRET"],
      "mail": ["c8a49f1b-fb39-4ce3-bdd0-b3b907262db3", null],
      "physicalDeliveryOfficeName": [
        "7ca6dfb1-5cc7-428c-b15f-a27056b90ae5",
        null
      ],
      "mobile": ["43153f5d-e2d3-439f-b608-1afbae91ddf6", "PUBLIC"]
    },
    "it_systems": {
      "samAccountName": "fb2ac325-a1c4-4632-a254-3a7e2184eea7"
    }
  }
}
```

Hvor betydniningen af de enkelte felter er angivet højere oppe i dokumentationen.
Felter som omhandler skolemdomænet er foreløbig sat via miljøvariable og er ikke
inkluderet her, da ingen af skriveintegrationerne på dette tidspunkt undestøtter dette.

Det skal nu oprettes et lokalt afviklingsmiljø. Dette gøres ved at klone git
projektet i en lokal mappe og oprette et lokal python miljø:

```bash
git clone https://github.com/OS2mo/os2mo-data-import-and-export
cd os2mo-data-import-and-export
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install os2mo_data_import/
pip install pywinrm[kerberos]
```

For at bekræfte at alt er på plads, findes et værktøj til at teste kommunikationen:

```bash
cd integrations/ad_integration
python test_connectivity.py
```

Hvis dette returnerer med ordet 'success' er integrationen klar til brug.

## Anvendelse af kommondolinjeværktøjer

Følgende funktionaliteter har deres eget kommandolinjeværktøj som gør det muligt at
anvende dem uden at rette direkte i Python koden:

- `ad_writer.py`
- `ad_life_cycle.py`
- `execute_ad_script.py`
- `user_names.py`

For user names kræves der dog en del forudsætninger som gør at kommandolinjeværktøjet
ikke i praksis har brugbar funktionalitet endnu.

### ad_writer.py

Dette værktøj har følgende muligheder:

```
usage: ad_writer.py [-h]
    [--create-user-with-manager MO_uuid |
    --create-user MO_uuid |
    --sync-user MO_uuid |
    --delete-user User_SAM |
    --read-ad-information User_SAM |
    --add-manager-to-user Manager_SAM User_SAM]
```

**De forskellige muligheder gennemgås her en ad gangen:**

- --create-user-with-manager MO uuid
  Eksempel:

  ```bash
  python ad_writer-py --create-user-with-manager 4931ddb6-5084-45d6-9fb2-52ff33998005
  ```

  Denne kommando vil oprette en ny AD bruger ved hjælp af de informationer der er
  findes om brugeren i MO. De relevante felter i AD vil blive udfyld i henhold til
  den lokale feltmapning, og der vil blive oprettet et link til AD kontoen for
  lederen af medarbejderens primære ansættelse. Hvis det ikke er muligt at finde
  en leder, vil integrationen standse med en _ManagerNotUniqueFromCprException_.

- --create-user MO_uuid
  Eksempel:

  ```bash
  python ad_writer-py --create-user 4931ddb6-5084-45d6-9fb2-52ff33998005
  ```

  Som ovenfor men i dette tilfælde oprettes der ikke et link til lederens AD konto.

- --sync-user MO_uuid
  Eksempel:

  ```bash
  python ad_writer-py --sync-user 4931ddb6-5084-45d6-9fb2-52ff33998005
  ```

  Synkroniser oplysninger fra MO til en allerede eksisterende AD konto.

- --delete-user User_SAM
  Eksempel:

  ```bash
  python ad_writer-py --delete-user MGORE
  ```

  Slet den pågældende AD bruger. Denne funktion anvendes hovedsageligt til tests,
  da et driftmiljø typisk vil have en mere kompliceret procedure for sletning af
  brugere.

- --read-ad-information User_SAM
  Eksempel:

  ```bash
  python ad_writer-py --read-ad-information MGORE
  ```

  Returnerer de AD oplysninger fra AD som integrationen i øjeblikket er konfigureret
  til at læse. Det er altså en delmængde af disse oplysninger som vil blive
  skrevet til MO af synkroniseringsværktøjet. Funktionen er primært nyttig til
  udvikling og fejlfinding.

- --add-manager-to-user Manager_SAM User_SAM
  Eksempel:
  ```bash
  python ad_writer-py --add-manager-to-user DMILL MGORE
  ```
  Udfylder brugerens `manager` felt med et link til AD kontoen der hører til
  ManagerSAM.

### ad_fix_enddate.py

Hvis ad_writer skal skrive `end_date` kan dette job være nødvendigt at sætte op også
fordi ad_writer ikke læser engagementer i MO i fortiden. Dette job tjekker alle
engagementer i AD som har slutdatoen 9999-12-31 i AD og tjekker deres slutdato i MO.
Hvis engagementet allerede er afsluttet i MO opdateres det i AD.

For at sætte det som en del af job-runneren sættes:

- `crontab.RUN_AD_ENDDATE_FIXER`: Sættes til _true_ for at køre det som en del af de daglige jobs.
- `integrations.ad_writer.fixup_enddate_field`: Det felt i AD som slutdatoen skrives i.
- `integrations.ad.write.uuid_field`: Feltet i AD som indeholder brugeres MO uuid.

### ad_life_cycle.py

Dette værktøj kan afhængig af de valgte parametre oprette eller deaktivere
AD-konti på brugere som henholdsvis findes i MO men ikke i AD, eller findes
i AD, men ikke har aktive engagementer i MO.

```bash
ad_life_cycle.py [-h/--help]
    [--create-ad-accounts] [--disable-ad-accounts]
    [--dry-run] [--use-cached-mo]
```

Betydningen af disse parametre angives herunder, det er muligt at afvilke begge
synkroniseringer i samme kørsel ved at angive begge parametre.

- `--create-ad-accounts`

  Opret AD brugere til MO brugere som ikke i forvejen findes i AD efter de
  regler som er angivet i settings-nøglerne:

  - `integrations.ad.write.create_user_trees`
  - `integrations.ad.lifecycle.create_filters`

  Se mere om disse herunder.

- `--disable-ad-accounts`

  Sæt status til Disabled for AD konti hvor den tilhøende MO bruge ikke længere
  har et aktivt engagement og som opfylder reglerne angivet i settings-nøglen:

  - `integrations.ad.lifecycle.disable_filters`

  Se mere om denne herunder.

- `--dry-run`

  Programmet vil ikke forsøge at opdatere sit billede af MO, en vil anvende
  den aktuelt cache'de værdi. Dette kan være nyttigt til udvikling, eller
  hvis flere integrationer køres umidelbart efter hinanden.

- `--use-cached-mo`

  Programmet vil ikke genopfriske LoraCache, men blot benytte den aktuelle
  LoraCache der findes på disken.

Derudover kan programmet konfigureres med nøgler i`settings.json`specifikt:

- `integrations.ad.write.create_user_trees`

  Her angives en liste over et eller flere UUID'er på organisationsenheder i
  MO. Hvis en medarbejder optræder i en af disse enheder (samt deres
  underenheder, underenhedernes underenheder, osv.) vil`ad_life_cycle`oprette
  en AD-konto for medarbejderen (såfremt de ikke allerede har en.)

  Hvis man eksempelvis har et organisationstræ i MO, der ser således ud:

  ```
  Enhed A (uuid: aaaa)
    - Enhed A1 (uuid: aaaa1111)
  Enhed B (uuid:bbbb)
    - Enhed B1 (uuid: bbbb1111)
  ```

  og man ønsker, at`ad_life_cycle`kun må oprette AD-konti for MO-brugere i
  enhederne A, A1, og B1, kan man angive:

  ```json
  {
    "integrations.ad.write.create_user_trees": ["aaaa", "bbbb1111"]
  }
  ```

  Der vil ikke blive oprettet AD-konti for MO-brugere i enhed B med denne
  opsætning.

- `integrations.ad.lifecycle.create_filters`

  Se dokumentation herunder for`integrations.ad.lifecycle.disable_filters`.
  Denne nøgle gør det samme, blot som filter for oprettelse istedet for
  som filter for deaktivering.

- `integrations.ad.lifecycle.disable_filters`

  Liste af jinja templates der evalueres på MO brugere, deres engagementer og
  deres tilhørende AD konti. Disse templates kan returnere en sand værdi for
  at beholde brugeren eller en falsk værdi for at sortere brugeren fra.

  Værdierne der vurderes som sande er "yes", "true", "1" og "1.0".
  De findes i `string_to_bool` metoden i `exporters/utils/jinja_filter.py`.

  Eksempel 1:
  Vi ønsker kun at deaktivere brugere, hvis AD konto har et givent prefix (`X`)
  i deres SAM Account Name. For at opnå dette kan vi lave følgende konfiguration:

  ```json
  {
    "integrations.ad.lifecycle.disable_filters": [
      "{{ ad_object['SamAccountName'].startswith('X') }}"
    ]
  }
  ```

  Hermed vil disable-ad-accounts kun deaktivere brugere med X som prefix.

  Eksempel 2:

  Vi ønsker ikke at oprette brugere i AD, såfremt de har en given
  stillingsbetegnelse (_Bruger_) på deres primære engagement i MO.
  For at opnå dette kan vi lave følgende konfiguration:

  ```json
  {
      "integrations.ad.lifecycle.create_filters": [
          "{{ employee.get('primary_engagement', {})
                      .get('job_function', {})
                      .get('title', '') != 'Bruger' }}"            ]        }
  ```

  Hermed vil create-ad-accounts oprette AD konti for alle brugere, undtagen
  dem som har den givne stillingsbetegnelse.

Det er værd at bemærke at brugerne som laves med ad*life_cycle som udgangspunkt
\_ikke* oprettes med relaterede data, de vil altså fremstå f.eks. uden adresser.
Deres relaterede data kan tilførsel vha. `mo_to_ad_sync`programmet`.

Settings kan overskrives hvis der skal gælde andre regler under oprettelsen af nye
brugere end der ellers gør under synkroniseringen. Dette gøres ved at sætte felterne
ind i `ad_lifecycle_injected_settings`. De skal skrives som en dictionary med formen
"sti.til.setting": "værdi". Bemærk at stien her ikke svarer til stien i
settings.json, men i den dictionary som AD læser ud af settings. Fx.

```json
{
  "ad_lifecycle_injected_settings": {
    "primary_write.mo_to_ad_fields.Title": "title"
  }
}
```

Dette vil tilføje "title" til settings svarende til:

`settings["primary_write"]["mo_to_ad_fields"]["Title"] = "title".`

Man kan se resultatet af at tilføre de ekstra settings ved at køre:

```bash
python -m integrations.ad_integration.read_ad_conf_settings --inject
```

#### execute_ad_script.py

Dette værktøj har følgende muligheder:

```
usage: execute_ad_script.py [-h]
                            [--validate-script Script name |
            --execute-script Script name user_uuid]
```

**De forskellige muligheder gennemgås her en ad gangen:**

- `--validate-script Script_name`

  Eksempel:

  ```bash
  python ad_writer-py --validate-script send_email
  ```

  Denne kommando vil lede efter en skabelon i `scripts/send_email.ps_template` og
  validere at skabelonen kun indeholder gyldige nøgleværdier. Hvis dette er
  tilfældet returneres sætningen "Script is valid" og ellers returneres en
  fejlbesked som beskriver hvilke ugyldige nøgler der er fundet i skabelonen.

- `--execute-script Script name user_uuid`

  Eksempel:

  ```bash
  python execute_ad_script.py --execute-script send_email 4931ddb6-5084-45d6-9fb2-52ff33998005
  ```

  Denne kommando vil finde en skabelon i`scripts/send_email.ps_template`og først
  validere og derefter afvikle de med værdier taget fra brugen med uuid som angivet.

## Import af AD OU til MO

Som en ekstra funktionalitet, er det muligt at anvende AD integrationens
læsefaciliteter til at indlæse en bestemt OU fra AD'et til MO. Dette vil
eksempelvis kunne anvendes hvis AD'et er autoritativ for eksterne konsulenter i
kommunen og man ønsker, at disse personer skal fremgå af MOs frontend på trods af at
de ikke importeres fra lønsystemet. Integrationen vil oprette ansættelsestypen
'Ekstern' og vil oprette alle brugere fra et på forhånd angivet OU som ansatte i MO.
Det er en forudsætning, at disse brugere ikke har andre ansættelser i MO i forvejen.
Hvis brugere fjernes fra OU'et vil de blive fjernet fra MO ved næste kørsel af
integrationen.

I den nuværende udgave af integrationen, genkendes OU'et med eksterne
brugere på, at dets navn indeholder ordene 'Ekstern Konsulenter', dette vil på sigt
blive erstattet med konfiguration.

For at programmet kan afvikles, er det nødvendigt at sætte konfigurationsværdien
`integrations.ad.import_ou.mo_unit_uuid` som angiver UUID'en på den enhed brugerne
fra AD skal synkroniseres til. Hvis enheden ikke eksisterer i forvejen vil den blive
oprettet ved første kørsel, så for en kommune som starter op med brug af denne
integration, kan der blot angives et tilfældigt UUID.

Programmet hedder `import_ad_group_into_mo.py` og kan anvendes med et antal
kommandolinjeparametre:

- `--create-or-update`: Opretter og opdaterer bruger fra AD til MO.

- `--cleanup-removed-users`: Fjerne MO brugere som ikke længere er
  konsulenter i AD.

- `--full-sync`: Kører begge de to ovenstående operationer.
