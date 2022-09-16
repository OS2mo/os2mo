---
title: CSV Exporters
---

# Exporters

This set of code allows to export the content of MO into a fixed set of
csv-files containing various sub-sets of the content of MO.

## Installation

The code contains a general exporter as well as code specific to various
municipalities, the municipality-specfic code should only be run, if you
are running MO from the corresponding municipality, since these
exporters expects data specific to theses places.

The general code can be run directly from the folder with no
installation required.

## Requirements

The modules depend on mora_helper wich can be installed from the Helpers
directory from the root of this repo: 

``` bash
sudo pip3 install -e os2mo_helpers
```

## Configuration

If MO is set up to use authentication, the exporter needs a valid
service SAML token. This is read from the environment variable
SAML_TOKEN.

## Exported data

The general exporter will produce the following data-files:

-   alle_lederfunktioner_os2mo.csv
-   alle-medarbejdere-stilling-email_os2mo.csv
-   org_incl-medarbejdere.csv
-   adm-org-incl-start-og-stopdata-og-enhedstyper-os2mo.csv
-   tilknytninger.csv

Please note that these exports contain the same personal details as MO
itself, and thus it is important to secure appropriate handling of the
exported files.

## Command line options

general_export.py accepts two command line parameters:

- \--root: uuid for the root org to export. If this parameter is not
given, the deepest available tree will be assumed.

- \--threaded-speedup: If set to True, the program will start a full
multithreaded read of all employees in MO. On most systems this will be
significantly faster, but will result in a higher server load and a
longer delay before the first export is finished.

- \--hostname: Hostname for the MO instance. Defaults to localhost.

## Deployment

In order to run the exporter on a continuous basis (eg a nightly run) a
cron job should be set up and SAML_TOKEN should be given a valid value.

To set up the cron job, find the uuid of the wanted root-unit and run
this command from cron:

``` bash
python3 general_export.py \--hostname=localhost \--root=\<uuid\>
```

unless the deployment is for one of the specific municipalities with a
specific set of export code.
