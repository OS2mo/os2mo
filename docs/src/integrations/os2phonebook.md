# Telefonbog

Dette program eksporterer JSON som kan indlæses i Telefonbogen, der udstilles på kundens intranet.
Progammet understøtter også at sende JSON dataen til telefonbogen selv.

# Konfiguration

For at anvende eksporten er det nødvendigt at oprette et antal nøgler i
_settings.json_:

- `exporters.os2phonebook_base_url`: URL adressen hvorpå
  telefonbogen kan nåes.
- `exporters.os2phonebook_basic_auth_user`: HTTP Basic Auth brugeren
  til dataindlæsning i telefonbogen.
- `exporters.os2phonebook_basic_auth_pass`: HTTP Basic Auth password
  til dataindlæsning i telefonbogen.

Derudover er det nødvendigt at konfigurere _sql_export_ og
dennes konfiguration.

# Programkomponenter

Programmet er opdelt i tre komponenter, hhv.

- Oprettelse af Actual State SQL database (via exporters/sql_export).
- Opslag i Actual State SQLite, og oprettelse processeret JSON.
- Afsendelse af genereret JSON til telefon bogen.

# Indhold af udtrækket

Udtrækket indeholder:

- Medarbejdere
- Medarbejderes adresser
- Medarbejderes engagementer
- Medarbejderes tilknytninger
- Medarbejderes ledere
- Medarbejderes organisatoriske enheder
- Organisatoriske enheder tilknyttet medarbejdere

## Medarbejdere

Der udtrækkes uuid, navn, adresser (DAR, Telefon, E-mail, EAN, P-nummer,
Url), engagementer (uuid, titel og navn), tilknytninger (uuid, titel og
navn), ledere (uuid, titel og navn) samt organisatoriske enheder der er
tilknyttet medarbejderens engagementer, tilknytninger eller ledere, samt
disses forældre enheder.

Adresser udlades hvis scope er 'SECRET'.

Der medtages ikke medarbejdere som ikke har nogle engagementer,
tilknytninger og lederforhold.

## Organisatoriske enheder

Der udtrækkes udelukkende organisatoriske enheder som kan nåes via
medarbejdere fra det overstående. For organisatoriske enheder udtrækkes,
adresser, engagementer, tilknytninger og ledere med samme data som for
medarbejdere.
