# OS2Rollekatalog

## Indledning

Dette program udfylder OS2Rollekataloget med organisation og
medarbejdere fra OS2MO. Kræver opsætning af AD i settings, og der
skrives kun brugere til OS2Rollekataloget der findes både i OS2MO og i
AD.

Eksporten sender alle informationerne i ét payload som overskriver det
der ligger i rollekataloget i forvejen.

## Konfiguration

For at anvende eksporten er det nødvendigt at oprette et antal nøgler i
_settings.json_:

- `exporters.os2rollekatalog.rollekatalog.url`: URL adressen til
  rollekatalogets organisations api, fx.
  <https://os2mo.rollekatalog.dk/api/organisation/v3

- `exporters.os2rollekatalog.rollekatalog.api_token`: API token til
  autentificering med rollekataloget

- `exporters.os2rollekatalog.main_root_org_unit`: UUID på
  rod-enheden i OS2MO. Bliver også rod i rollekatalog medmindre
  andet er sat i _rollekatalog_root_uuid_

- `exporters.os2rollekatalog.ou_filter`: _true_ eller _false_.
  Filtrer enheder og engagementer der ikke hører under
  main_root_org_unit fra. Default er _false_.

- `exporters.os2rollekatalog.rollekatalog_root_uuid`: Optionelt. Hvis rod-uuid'en i rollekataloget allerede eksisterer kan den sættes ind her. Rod-enheden fra OS2MO vil så få overskrevet sit UUID med denne.

- `exporters.os2rollekatalog.sync_titles`: _true_ eller _false_.
  Synkroniserer stillingsbetegnelser til rollekatalogets `titles` api. Kræver specifik adgang til et separat endepunkt i rollekatalogets API. Vedligeholder oversigten over samtlige stillingsbetegnelser samt sender engagementers stillingsbeteglelses uuid med så de kan knyttes sammen. Er denne slået fra sendes stillingsbetegnelser kun som tekst-felt. Default er _false_.

- `exporters.os2rollekatalog.use_nickname`: _true_ eller _false_.
  Anvender brugeres kaldenavn i stedet for navn hvis det er udfyldt i OS2MO. Default er _false_.

## Eksporteret data

Payloaded til OS2Rollekatalog er opdelt i Enheder og Medarbejdere og
indeholder følgende data:

### Medarbejdere

- UUID
- Navn
- Kaldenavn (optionelt). Hvis Kaldenavn er sat i MO, vil det stå i stedet for navn i rollekataloget.
- Email
- AD brugernavn
- Engagementer (Stillingsbetegnelse og Enheds uuid. Optionelt: uuid for stillingsbetegnelse-klassen.)

**_Desuden er der mulighed for synkronisering mellem fremtidige og nutidige brugere_**

Der gives en advarsel i loggen ved mere end én email adresse på en
bruger.

### Organisatoriske enheder

- UUID
- Navn
- Email
- Overenhed
- Leder
- KLE - Kommunernes Landsforenings Emnesystematik
  - Indsigt
  - Udførende

Der tillades kun én leder pr. Organisatorisk enhed.
