---
title: Rapporter i OS2MO
---

Det er muligt at få genereret rapporter fx hver nat, så de indeholder friske data, når man møder på arbjdet om morgenen.

Rapporterne findes i topmenuen:

![image](../graphics/reportsinUI.png)

De rapporter, der findes i dag, er beskrevet nedenfor. Ønskes andre sammenstillinger af data i en rapport, kontakt venligst Magenta på support@magenta.dk.

# Eksisterende rapporter
- **Alle medarbejdere**.
    - UUID
    - Navn på person
    - Stilling
    - CPR-Nummer
    - AD-email
    - AD-telefonnummer
    - Enhed

[Eksempel](../Reports/OS2mo%20Ansatte.xlsx)

- **Alle tilknytninger**.
    - Org-enhedens UUID
    - Org-enhedens navn
    - Overordnet UUID
    - Navn på person
    - Personens UUID
    - CPR-Nummer

[Eksempel](../Reports/OS2mo%20alle%20tilknytninger.xlsx)

- **Medarbejdere, indplacering og start- og stopdatoer**
    - Org-enhedens UUID
    - Org-enhedens navn
    - Enhedstype Titel
    - Enhedstypens UUID
    - Gyldig fra
    - Gyldig til

[Eksempel](../Reports/OS2mos%20administrative%20organisation%20inkl.%20start-%20og-%20stopdato%20samt%20enhedstyper.xlsx)

- **Den administrative organisation**
    - Organistionsenhed
    - Navn på medarbejder
    - Brugernavn
    - Telefon
    - E-mail
    - Adresse

[Eksempel](../Reports/OS2mos%20organisation%20inkl.%20medarbejdere.xlsx)

- **Alle ledere**
    - Enhed
    - Navn
    - Ansvar
    - Telefon
    - E-mail

[Eksempel](../Reports/OS2mo%20Alle%20lederfunktioner.xlsx)

- **Medarbejdertelefonbog**
    - Navn
    - Telefon
    - Mobiltelefon
    - Enhed
    - Stillingsbetegnelse

[Eksempel](../Reports/OS2mo%20Medarbejdertelefonbog.xlsx)

- **Stilling og kontaktinformation**
    - CPR
    - Ansættelse gyldig fra
    - Ansættelse gyldig til
    - Fornavn
    - Efternavn
    - Person UUID
    - Brugernavn
    - Org-enhed
    - Org-enhed UUID
    - E-mail
    - Telefon
    - Stillingsbetegnelse
    - Engagement UUID

[Eksempel](../Reports/OS2MO%20Alles%20%20stilling%2Bemail.xlsx)

Andre rapporter kan ligeledes genereres, fx. rapport over MED-organisationens repræsentanter.

# Technical info
Shared reports introduces a collection of reports that can be used by
customers regardless of their individual setup. They utilise standard
MO-data and return
[pandas DataFrames](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.html),
which can then be exported to a variety of file formats and served in
`/forespoergsler`.

## Quick Start

The `main()` method in `/reports/shared_reports.py` will generate all
available reports. It utilises settings from `settings.json`,
specifically `mora.base` as the hostname, `reports.org_name` as the name
of the organisation for which to generate reports,
`reports.pay_org_name` as the name of the organisation from which to
generate payroll reports, and `mora.folder.query_export` as the output
directory.

!!! example
    In `settings.json`, the following settings should be available:

    ``` json
    {
        "mora.base": "http://localhost:5000",
        "mora.folder.query_export": "/opt/reports/"
        "reports.org_name": "Testkommune"
    }
    ```

    Note that `reports.pay_org_name` is *not* set in these settings. In
    this case, it will default to the organisation name. However, a few
    customers have a specific payroll organisation, so we need to be able to
    use the setting if necessary.

    Then, to generate all reports in CSV-format, simply call

    ``` bash
    python /reports/shared_reports.py
    ```

If only a subset of reports and/or different output formats are
required, the API can be used directly – refer to the following
section. In the future, a Click CLI will be made available.
