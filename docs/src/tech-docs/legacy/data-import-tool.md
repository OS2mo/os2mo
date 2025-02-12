---
title: OS2MO data import tool
---

A small higher level utility for os2mo data import.

The utility provides functionality to create organisation units and
employees and to create all of the types to which these can be assigned.

Additonally the utility can be used to insert data objects into a
running instance of os2mo.

## Installing

Install the os2mo_data_import package as follows:

```bash
# Checkout the mora source repository
https://github.com/OS2mo/os2mo-data-import-and-export

# Navigate to the local copy of the repository
cd /path/to/os2mo-data-import-and-export

# Install package with pip
pip install -e os2mo_data_import
```

## Getting started

The main entry point (for most use cases) is the Organisation class,
which functions as a wrapper for all the sub classes.

```python
# Imports
from os2mo_data_import import ImportHelper

# Init helper
os2mo = ImportHelper(create_defaults=True, store_integration_data=True)

# Add organisation
os2mo.add_organisation(
    identifier="Magenta Aps",
    user_key="Magenta",
    municipality_code=101
)
```

### Organisation Units

Before organisation units can be created, a type for the unit must be
added:

```python
# Add klasse with reference to facet "org_unit_type"
os2mo.add_klasse(
    identifier="Hovedenhed",
    facet_type_ref="org_unit_type",
    user_key="D1ED90C5-643A-4C12-8889-6B4174EF4467",
    title="Hovedenhed"  # This is the displayed value
)
```

Now an organisation unit can be added with "org_unit_type_ref"
referencing the user defined identifier of the newly created unit type
by name:

```python
# Root unit: Magenta
# Belongs to unit type: "Hovedenhed"
os2mo.add_organisation_unit(
    identifier="Magenta",
    name="Magenta Aps",
    type_ref="Hovedenhed",  # Reference to the unit type
    date_from="1986-01-01"
)
```

Organisation unit "Magenta" is a root unit in this example. To add
children/sub units, "Magenta" must be referenced as parent:

```python
# Add unit type "Afdeling"
os2mo.add_klasse(
    identifier="Afdeling",
    facet_type_ref="org_unit_type",
    user_key="91154D1E-E7CA-439B-B910-D4622FD3FD21",
    title="Afdeling"
)

# Add sub unit "Pilestræde"
os2mo.add_organisation_unit(
    identifier="Pilestræde",
    type_ref="Afdeling",  # This unit is of type: Afdeling
    parent_ref="Magenta",  # Sub unit of/Belongs to Magenta
    date_from="1986-01-01"
)
```

Optional data or "details" can be associated with an organisation
unit.

!!! note

    At least 2 "Klasse" objects must be created, an object for the primary
    phone number and an object for the primary mailing address (residence).

    The validation in the (os2mo) frontend application requires:

    The user_key on the the primary phone number object must be specified as
    "PhoneUnit"

    The user_key on the primary mail address object must be specified as
    "AddressMailUnit"

    Hence either the "identifier" or the "user_key" must be set to:

    -   PhoneUnit
    -   AddressMailUnit

    (The "user_key" is derived from the value of the "identifier if not
    explicitly set)

    See the example below:

```python
# Add klasse type "AdressePost"
# Which belongs to facet type "org_unit_address_type"

# user_key is not explicitly set, identifier must be "AddressMailUnit"
os2mo.add_klasse(
    identifier="AddressMailUnit",
    facet_type_ref="org_unit_address_type",
    title="Adresse",
    scope="DAR",
    example="<UUID>"
)

# Add klasse type "Telefon"
# Which belongs to facet type "org_unit_address_type"

# user_key is set to "PhoneUnit", hence the identifier can be anything
os2mo.add_klasse(
    identifier="Telefon",
    facet_type_ref="org_unit_address_type",
    user_key="PhoneUnit",
    title="Tlf",
    scope="PHONE",
    example="20304060"
)

# Add "AdressePost" detail to the unit "Magenta"
os2mo.add_address_type(
    organisation_unit="Magenta",
    value="0a3f50c4-379f-32b8-e044-0003ba298018",
    type_ref="AdressePost",
    date_from="1986-01-01"
)

# Add "Telefon" detail to the unit "Magenta"
os2mo.add_address_type(
    organisation_unit="Magenta",
    value="11223344",
    type_ref="Telefon",
    date_from="1986-01-01",
)
```

### Employees

Employees are not directly attached to an organisation unit, but can
have a job function which is linked to a unit.

Create employees first:

```python
os2mo.add_employee(
    identifier="Susanne Chæf",
    cpr_no="0101862233"
)

os2mo.add_employee(
    identifier="Odin Perskov",
    cpr_no="0102862234"
)
```

### Job function

Add the job function types:

```python
# Job: CEO ("Direktør")
os2mo.add_klasse(
    identifier="Direktør",
    facet_type_ref="engagement_type",
    user_key="Direktør",
    title="Direktør"
)

# Job: Projectmanager ("Projektleder")
os2mo.add_klasse(
    identifier="Projektleder",
    facet_type_ref="engagement_type",
    user_key="Projektleder",
    title="Projektleder"
)
```

Add job functions to the newly created employees with the
"add_type_engagement" method:

```python
# Susanne Chæf is CEO
os2mo.add_engagement(
    employee="Susanne Chæf",
    organisation_unit="Magenta",
    job_function_ref="Direktør",
    engagement_type_ref="Ansat",
    date_from="1986-01-01"
)

# Odin Perskov is projectmanager
os2mo.add_engagement(
    employee="Odin Perskov",
    organisation_unit="Pilestræde",
    job_function_ref="Projektleder",
    engagement_type_ref="Ansat",
    date_from="1986-02-01"
)
```

### Association

In this example the employee "Odin Perskov" is an external consultant,
and to reflect this an association type can be assigned:

```python
os2mo.add_klasse(
    identifier="Ekstern Konsulent",
    facet_type_ref="association_type",
    user_key="F997F306-71DF-477C-AD42-E753F9C21B42",
    title="Ekstern Konsulent"
)

# Add the consultant association to "Odin Perskov":
os2mo.add_association(
    employee="Odin Perskov",
    organisation_unit="Pilestræde",
    job_function_ref="Projektleder",
    association_type_ref="Ekstern Konsulent",
    address_uuid="0a3f50c4-379f-32b8-e044-0003ba298018",
    date_from="1986-10-01"
)
```

In the following example an address is assigned to employee "Odin
Perskov". For residential addresses, valid UUID's are used to
reference an address from the "Danish registry of addresses" (DAR):

```python
# Add address type "AdressePostEmployee"
os2mo.add_klasse(
    identifier="AdressePostEmployee",
    facet_type_ref="employee_address_type",
    user_key="2F29C717-5D78-4AA9-BDAE-7CDB3A378018",
    title="Adresse",
    scope="DAR",
    example="<UUID>"
)

# Detail AdressePostEmployee assigned to "Odin Perskov"
os2mo.add_address_type(
    employee="Odin Perskov",
    value="0a3f50a0-ef5a-32b8-e044-0003ba298018",
    type_ref="AdressePostEmployee",
    date_from="1986-11-01",
)
```

### Roles

To add a role type:

```python
# A role as contact for external projects
os2mo.add_klasse(
    identifier="Nøgleansvarlig",
    facet_type_ref="role_type",
    user_key="0E078F23-A5B4-4FB4-909B-60E49295C5E9",
    title="Nøgleansvarlig"
)

# Role assigned to "Odin Perskov"
os2mo.add_role(
    employee="Odin Perskov",
    organisation_unit="Pilestræde",
    role_type_ref="Nøgleansvarlig",
    date_from="1986-12-01"
)
```

### It systems

Generic IT systems can be created and assigned to employees with a
specified "user_key", which functions as a reference to a username,
pin code etc.:

```python
# Create IT system: Database
  os2mo.new_itsystem(
      identifier="Database",
      system_name="Database"
  )

  # Assign access to the database
  # with username "odpe@db"
  os2mo.join_itsystem(
      employee="Odin Perskov",
      user_key="odpe@db",
      itsystem_ref="Database",
      date_from="1987-10-01"
  )
```

### Manager type, level and responsibilities

In order to assign employees as managers to an organisation unit, the
following types must be created:

- manager type
- manager level
- A type for each responsibility

Create manager type:

```python
os2mo.add_klasse(
    identifier="Leder",
    facet_type_ref="manager_type",
    user_key="55BD7A09-86C3-4E15-AF5D-EAD20EB12F81",
    title="Virksomhedens direktør"
)
```

Create manager level:

```python
os2mo.add_klasse(
    identifier="Højeste niveau",
    facet_type_ref="manager_level",
    user_key="6EAA7DA7-212D-4FD0-A068-BA3F932FDB10",
    title="Højeste niveau"
)
```

Create several responsibilities:

```python
os2mo.add_klasse(
    identifier="Tage beslutninger",
    facet_type_ref="responsibility",
    user_key="A9ABDCCB-EC83-468F-AB7D-175B95E94956",
    title="Tage beslutninger"
)

os2mo.add_klasse(
    identifier="Motivere medarbejdere",
    facet_type_ref="responsibility",
    user_key="DC475AF8-21C9-4112-94AE-E9FB13FE8D14",
    title="Motivere medarbejdere"
)

os2mo.add_klasse(
    identifier="Betale løn",
    facet_type_ref="responsibility",
    user_key="0A929060-3392-4C07-8F4E-EF5F9B6AFDE2",
    title="Betale løn"
)
```

Assign the manager position of Magenta to "Susanne Chæf":

```python
os2mo.add_manager(
    employee="Susanne Chæf",
    organisation_unit="Magenta",
    manager_type_ref="Leder",
    manager_level_ref="Højeste niveau",
    responsibility_list=["Tage beslutninger", "Motivere medarbejdere", "Betale løn"],
    date_from="1987-12-01",
)
```

## Preservation of UUIDs

If the system to be imported into MO contains UUIDs that should be
preserved in MO, it is possible to import the UUIDs for employees,
organisational units, classes and classifications. This is achieved by
adding an extra uuid argument when creating the object, eg:

```python
os2mo.add_klasse(
    identifier="Betale løn",
    facet_type_ref="responsibility",
    uuid="195da2b6-e648-4bdc-add1-e22654996997",
    user_key="0A929060-3392-4C07-8F4E-EF5F9B6AFDE2",
    title="Betale løn"
)
```

## Continuous integration

It is possible to run the importer in a mode where the internal
identifiers will be stored in the special field 'integration_data' in
LoRa. This identifier will be recognized upon the next import and the
object will be re-imported in contrast to being created again. In effect
this will turn the importer into a one-way integration of the imported
system.

## Example

If a "real" os2mo application is available, a practial example is
provided with contains similar import data as the given examples above.

Feel free to run the "import_example.py" included in the repository:

Example:

```bash
$os2mo-data-import-and-export/os2mo_data_import/import_example.py
```

Run example:

```bash
cd os2mo_data_import
python import_example.py
```

## Known Issues

Currently it is not possible to assign "Leave" (e.g. various types of
leave of absence).

This issue is related to the validation of type assignments.
