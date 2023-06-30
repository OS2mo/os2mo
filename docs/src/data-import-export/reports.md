---
title: Rapporter i OS2MO
---

Det er muligt at få genereret rapporter fx hver nat, så de indeholder friske data, når man møder på arbjdet om morgenen.

Rapporterne findes i topmenuen:

![image](../graphics/reportsinUI.png)

De rapporter, der findes i dag, er beskrevet nedenfor. Ønskes andre sammenstillinger af data i en rapport, kontakt venligst Magenta på support@magenta.dk.

# Eksisterende rapporter
- **Alle medarbejdere**. Består af
    - CPR-Nummer
    - Ansættelse gyldig fra
    - Ansættelse gyldig til
    - Fornavn
    - Efternavn
    - Personens UUID
    - Brugernavn
    - Org-enhed
    - Org-enhedens UUID
    - E-mail
    - Telefon
    - Stillingsbetegnelse
    - Engagementets UUID
- **Alle organisationsenheders tilknytninger**. Består af
    - Org-enhedens UUID
    - Org-enhed
    - Overordnet UUID
    - Navn
    - Personens UUID
    - CPR-Nummer
- **Den administrative organisation**
    - Org-enhedens UUID
    - Navn
    - Enhedstypens UUID
    - Gyldig fra
    - Gyldig til
    - Enhedstypens titel
- **Alle ledere**
    - Navn
    - Ansvar
    - Telefon
    - E-mail
- **Adresser tilhørende ledere og medarbejdere**
    - Navn
    - Postadresse
    - Telefon
    - E-mail
    - Hvis der er flere adresser (fx AD-adresser), kan de medtages.
- **MED-organisationen**
    - Liste følger

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
