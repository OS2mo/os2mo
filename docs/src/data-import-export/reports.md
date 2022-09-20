---
title: Shared Reports
---

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
