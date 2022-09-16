---
title: Integration for Aarhus LOS
---

## Introduction

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

## Setup

The integration requires minimal configuration outside of the common
default values found in the settings file:

-   `integrations.aarhus_los.ftp_url`: The url for the Aarhus Kommune
    FTP. Contains a default for the current FTP url.
-   `integrations.aarhus_los.ftp_user`: The FTP username
-   `integrations.aarhus_los.ftp_pass`: The FTP password
-   `integrations.aarhus_los.state_file`: A location for a file
    containing state across different imports.

## Usage

The importer can be run with the following command:

``` bash 
python integrations/aarhus/los_import.py 
```

The command currently takes no parameters.

The command will:

-   Perform an initial import, of all preset classes and organisation
    objects if it determines it hasn't taken place yet
-   Ensure a state file exists, containing the date of the last import.
-   Connect to the AAK FTP and perform the necessary import of all
    'klasse', 'it system', org unit and person objects, to bring the
    system up to date.
-   Write a timestamp of a completed import into the state file

The command is designed to be idempotent, and can theoretically be run
as often as is deemed necessary.

## Functionality

### Seed data

If no import has yet taken place, initial seed data is loaded by the
importer. This data is coded in the file
*integrations/aarhus/initial.py*.

The initial data sets up:

-   a MO organisation (Aarhus Kommune)
-   a set of MO address types for use when importing organisational
    units and employees
-   a set of MO facet classes for recording the hierarchy of
    organisational units
-   an IT system ("AZ")

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
classes are created in the facet `org_unit_hierarchy`:

-   *Linjeorganisation*
-   *Sikkerhedsorganisation*

Finally, the following facets are created, containing one placeholder
class each:

<figcaption>Miscellaneous facets and classes</figcaption>

| Facet              |  Placeholder class value |
| ------------------ | ------------------------ |
| *role_type*        | *Rolletype*              |
| *association_type* | *Tilknytningsrolle*      |
| *leave_type*       | *Orlovsrolle*            |


### Loading additional classes into MO

The MO facet *org_unit_type* is used to store the
organisational unit type. See
[Organisational unit type]() for more on how
the facet *org_unit_type* is used. By reading the CSV file
*STAM_UUID_Enhedstype.csv*, the importer can add additional
classes to *org_unit_type*. The importer reads the CSV file
this way:

<figcaption>org_unit_type classes</figcaption>

| MO class field  | CSV field         | Data type | Content                                     |
| --------------- | ----------------- | --------- | ------------------------------------------- |
| *uuid*          | *EnhedstypeUUID*  | UUID      | The unique ID of the facet class value      |
| *user_key*      | *Enhedstype*      | String    | The user key (BVN) of the facet class value |
| *title*         | *Enhedstype*      | String    | The title of the facet class value          |

The MO facet *engagement_type* is used to store the
different engagement types. By reading the CSV file
*STAM_UUID_Engagementstype.csv*, the importer can add
additional classes to *engagement_type*. The importer reads
the CSV file this way:

| MO class field | CSV field              | Data type | Content                                     |
| -------------- | -----------------------| --------- | ------------------------------------------- |
| *uuid*         | *EngagementstypeUUID*  | UUID      | The unique ID of the facet class value      |
| *user_key*     | *Engagementstype*      | String    | The user key (BVN) of the facet class value |
| *title*        | *Engagementstype*      | String    | The title of the facet class value          |

The MO facet *engagement_job_function* is used to store the
different job function types. By reading the CSV file
*STAM_UUID_Stillingsbetegnelse.csv*, the importer can add
additional classes to *engagement_job_function*. The
importer reads the CSV file this way:

<figcaption>engagement_job_function classes</figcaption>

| MO class field  | CSV field             | Data type | Content                                     |
| --------------- | --------------------- |---------- | ------------------------------------------- |
| *uuid*          | *StillingBetUUID*     | UUID      | The unique ID of the facet class value      |
| *user_key*      | *Stillingsbetegnelse* | String    | The user key (BVN) of the facet class value |
| *title*         | *Stillingsbetegnelse* | String    | The title of the facet class value          |

Additional IT systems can be added in the file
*STAM_UUID_ITSystem.csv*. When the importer reads this file,
it creates MO IT systems this way:

<figcaption>IT systems</figcaption>

| MO IT system field  | CSV field       | Data type | Content                             |
| ------------------- | --------------- | --------- | ----------------------------------- |
| *uuid*              | *ITSystemUUID*  | UUID      | The unique ID of the IT system      |
| *name*              | *Name*          | String    | The name of the IT system           |
| *user_key*          | *Userkey*       | String    | The user key (BVN) of the IT system |

### Organisational units

The integration can create and update MO organisational units based on
the contents of *Org_inital\*.csv*,
*Org_nye\*.csv* and *Org_ret\*.csv*.

The organisational units are created in MO according to this schema:

<figcaption>Organisational units</figcaption>

| MO field             | CSV field           | Data type      | Content |
| -------------------- | ------------------- | -------------- | ------- |
| *uuid*               | *OrgUUID*           | UUID           | The unique ID of the organisational unit |
| *user_key*           | *BrugervendtNøgle*  | String         | The user-facing key of the organisational unit |
| *name*               | *OrgEnhedsNavn*     | String         | The name of the organisational unit |
| *parent*             | *ParentUUID*        | UUID           | Determines the parent of the organisational unit, and thus its place in the organisational hierarchy. |
| *org_unit_type*      | *OrgEnhedsTypeUUID* | UUID, optional | Identifies the type of the organisational unit. If given, this is stored in the MO facet *org_unit_type*. |
| *org_unit_hierarchy* | *Med-i-Linjeorg*    | Boolean        | If True, the organisational unit will be marked as being part of the hierarchy "Linjeorganisation". This is stored in the MO facet *org_unit_hierarchy*. |


Additionally, the *Org_\*.csv* files can contain
information which will be imported into MO as addresses of the given
organisational unit. The following CSV fields will be recorded as
addresses in MO:

<figcaption>Organisational unit addresses</figcaption>

| MO address type | CSV field       | Data type | Content                                   |
| --------------- | --------------- | --------- | ----------------------------------------- |
|*LOSID*          | *LOSID*         | String    | The LOS ID of the organisational unit     |
|*CVRUnit*        | *CVR*           | String    | The CVR number of the organisational unit |
|*EANUnit*        | *EAN*           | String    | The EAN number of the organisational unit |
|*PNumber*        | *P-Nr*          | String    | The P-number of the organisational unit   |
|*SENumber*       | *SE-Nr*         | String    | The SE-number of the organisational unit  |
|*intdebit*       | *IntDebitor-Nr* | String    | The SE-number of the organisational unit  |
|*UnitMagID*      | *MagID*         | String    | The "Magkort" of the organisational unit  |
|*AddressMailUnit*| *PostAdresse*   | DAR UUID  | The postal address of the organisational unit. The textual address will be looked up in DAR and its DAR UUID will be stored as its MO address.|

Finally, the *Org_\*.csv* files contain the fields
*StartDato* and *SlutDato*. These are used by
the importer to determine the *validity* of the
organisational units and addresses created. Each *validity*
consists of *from* and *to* dates in MO.

If multiple lines in the CSV files refer to the same organisational unit
UUID, and have identical properties from one line to the next (e.g. the
same name or the same LOS ID), the importer does not create multiple MO
objects, but rather merges the MO objects into one object, whose start
date will be the earliest *StartDato* and whose end date
will be the latest *SlutDato*.
