OS2MO data import
=================

A small higher level utility for os2mo data import.

The utility provides functionality to create organisation units
and employees and to create all of the types to which these can be assigned.

Additonally the utility can be used to insert data objects
into a running instance of os2mo.


Installing
----------

Install the os2mo_data_import package as follows: ::

  # Checkout the mora source repository
  git clone https://github.com/magenta-aps/mora

  # Navigate to the local copy of the repository
  cd /path/to/mora

  # Install package with pip
  pip install tooling/os2mo_data_import


Getting started
---------------
The main entry point (for most use cases) is the Organisation class,
which functions as a wrapper for all the sub classes. ::

  # Imports
  from os2mo_data_import import Organisation

  # Init Organisation
  Magenta = Organisation(
      name="Magenta Aps",
      user_key="Magenta",
      municipality_code=101,
      create_defaults=True
  )

The parameter "create_defaults" toggles automatic generation of default
types for Facet and Klasse.

:Reference:
  os2mo_data_import/defaults.py

To view the default types, a list of all items can be exported: ::

  # Show all default facet types
  all_facet_types = Magenta.Facet.export()
  print(all_facet_types)

  # Show all default klasse types
  all_klasse_types = Magenta.Klasse.export()
  print(all_klasse_types)


Organisation Units
""""""""""""""""""
Before organisation units can be created,
a type for the unit must be added: ::

  # Add klasse with reference to facet "Enhedstype"
  Magenta.Klasse.add(
      identifier="Hovedenhed",  # User defined identifier
      facet_type_ref="Enhedstype",  # Belongs to facet: Enhedstype
      user_key="D1ED90C5-643A-4C12-8889-6B4174EF4467",  # User key for internal reference
      title="Hovedenhed"  # This is the displayed value
  )


Now an organisation unit can be added with "org_unit_type_ref" referencing
the user defined identifier of the newly created unit type by name: ::

  # Add organisation unit: Magenta - OrganisationUnit.add()
  # Belongs to unit type: "Hovedenhed"

  Magenta.OrganisationUnit.add(
      identifier="Magenta",
      name="Magenta Aps",
      org_unit_type_ref="Hovedenhed",  # Reference to the unit type
      date_from="1986-01-01"
  )

Organisation unit "Magenta" is a root unit in this example.
To add children/sub units, "Magenta" must be referenced as parent: ::

  # Klasse type for sub units
  Magenta.Klasse.add(
        identifier="Afdeling",
        facet_type_ref="Enhedstype",
        user_key="91154D1E-E7CA-439B-B910-D4622FD3FD21",
        title="Afdeling"
    )

  # This is a sub unit of Magenta
  # and of type: Afdeling
  Magenta.OrganisationUnit.add(
        identifier="Pilestræde",
        org_unit_type_ref="Afdeling",  # This unit is of type: Afdeling
        parent_ref="Magenta",  # Sub unit of/Belongs to Magenta
        date_from="1986-01-01"
    )


Optional data can be attached to an organisation unit.
In the following example: ::

    # Address types added to organisation unit Magenta

    # Residential address
    Magenta.OrganisationUnit.add_type_address(
        owner_ref="Magenta",
        uuid="0a3f50c4-379f-32b8-e044-0003ba298018",
        address_type_ref="AdressePost",
        date_from="1986-01-01",
    )

    # EAN number
    Magenta.OrganisationUnit.add_type_address(
        owner_ref="Magenta",
        value="00112233",
        address_type_ref="EAN",
        date_from="1986-01-01",
    )

    # Phone number
    Magenta.OrganisationUnit.add_type_address(
        owner_ref="Magenta",
        value="11223344",
        address_type_ref="Telefon",
        date_from="1986-01-01",
    )

Employees
"""""""""
Employees are not directly attached to an organisation unit,
but can have a job function which is linked to a unit.

Create employees first: ::

  # Create employees
  Magenta.Employee.add(
        identifier="Susanne Chæf",
        cpr_no="0101862233"
    )

  Magenta.Employee.add(
        identifier="Odin Perskov",
        cpr_no="0102862234"
    )

Job function
""""""""""""
Add the job function types: ::

  # Job: CEO ("Direktør")
  Magenta.Klasse.add(
      identifier="Direktør",
      facet_type_ref="Stillingsbetegnelse",
      user_key="Direktør",
      title="Direktør"
  )

  # Job: Projectmanager ("Projektleder")
  Magenta.Klasse.add(
      identifier="Projektleder",
      facet_type_ref="Stillingsbetegnelse",
      user_key="Projektleder",
      title="Projektleder"
  )

Add job functions to the newly created employees
with the "add_type_engagement" method: ::

  # Susanne Chæf is CEO
  Magenta.Employee.add_type_engagement(
      owner_ref="Susanne Chæf",
      org_unit_ref="Magenta",
      job_function_ref="Direktør",
      engagement_type_ref="Ansat",
      date_from="1986-01-01"
  )

  # Odin Perskov is projectmanager
  Magenta.Employee.add_type_engagement(
      owner_ref="Odin Perskov",
      org_unit_ref="Pilestræde",
      job_function_ref="Projektleder",
      engagement_type_ref="Ansat",
      date_from="1986-02-01"
  )


Association
"""""""""""
In this example the employee "Odin Perskov" is an external consultant,
and to reflect this an association type can be assigned: ::

  # Create the association type
  Magenta.Klasse.add(
      identifier="Ekstern Konsulent",
      facet_type_ref="Tilknytningstype",
      user_key="Ekstern Konsulent",
      title="Ekstern Konsulent"
  )

  # Add the consultant association to "Odin Perskov":
  Magenta.Employee.add_type_association(
      owner_ref="Odin Perskov",
      org_unit_ref="Pilestræde",
      job_function_ref="Projektleder",
      association_type_ref="Ekstern Konsulent",
      address_uuid="0a3f50c4-379f-32b8-e044-0003ba298018",
      date_from="1986-10-01"
  )

In the following example an address is assigned to employee "Odin Perskov".
For residential addresses, valid UUID's are used to reference an address
from the "Danish registry of addresses" (DAR): ::

  Magenta.Employee.add_type_address(
      owner_ref="Odin Perskov",
      uuid="0a3f50a0-ef5a-32b8-e044-0003ba298018",  # Must be a valid DAR UUID
      address_type_ref="AdressePost",
      date_from="1986-11-01",
  )


Roles
"""""
To add a role type: ::

  # A role as contact for external projects
  Magenta.Klasse.add(
      identifier="Kontaktperson for eksterne projekter",
      facet_type_ref="Rolletype",
      title="Kontaktperson for eksterne projekter"
  )

  # Role assigned to "Odin Perskov"
  Magenta.Employee.add_type_role(
        owner_ref="Odin Perskov",
        org_unit_ref="Magenta",
        role_type_ref="Kontaktperson for eksterne projekter",
        date_from="1986-12-01"
    )

It systems
""""""""""
Generic IT systems can be created and assigned to employees with a specified "user_key",
which functions as a reference to a username, pin code etc.: ::

  # Create IT system: Database
  Magenta.Itsystem.add(
      identifier="Database",
      system_name="Database"
  )

  # Assign access to the database
  # with username "odpe@db"
  Magenta.Employee.add_type_itsystem(
      owner_ref="Odin Perskov",
      user_key="odpe@db",
      itsystem_ref="Database",
      date_from="1987-10-01"
  )

Manager type, level and responsibilities
""""""""""""""""""""""""""""""""""""""""
In order to assign employees as managers to an organisation unit,
the following types must be created:

 - manager type
 - manager level
 - A type for each responsibility

Create manager type: ::

  Magenta.Klasse.add(
      identifier="Direktør",
      facet_type_ref="Ledertyper",
      user_key="Direktør",
      title="Virksomhedens direktør"
  )

Create manager level: ::

  Magenta.Klasse.add(
      identifier="Højeste niveau",
      facet_type_ref="Lederniveau",
      user_key="Højeste niveau",
      title="Højeste niveau"
  )

Create several responsibilities: ::

  Magenta.Klasse.add(
      identifier="Tage beslutninger",
      facet_type_ref="Lederansvar",
      user_key="Tage beslutninger",
      title="Tage beslutninger"
  )

  Magenta.Klasse.add(
      identifier="Motivere medarbejdere",
      facet_type_ref="Lederansvar",
      user_key="Motivere medarbejdere",
      title="Motivere medarbejdere"
  )

  Magenta.Klasse.add(
      identifier="Betale løn",
      facet_type_ref="Lederansvar",
      user_key="Betale løn",
      title="Betale løn"
  )

Assign the manager position of Magenta to "Sussanne Chæf": ::

  Magenta.Employee.add_type_manager(
      owner_ref="Susanne Chæf",
      org_unit_ref="Magenta",
      manager_type_ref="Direktør",
      manager_level_ref="Højeste niveau",
      responsibility_list=["Tage beslutninger", "Motivere medarbejdere", "Betale løn"],
      date_from="1986-12-01",
  )

Example
"""""""
If a "real" os2mo application is available,
a practial example is provided with contains similar import data
as the given examples above.

Feel free to run the "example.py" included in the repository:

Example: $MORA_REPO/tooling/os2mo_data_import/example.py

Run example: ::

  cd os2mo_data_import
  python example.py


Reference
---------
For more information on the os2mo project,
please refer to the official documentation.

Read the docs: https://mora.readthedocs.io/en/master/


Known Issues
------------
Current it is not possible to assign "Leave" (e.g. various types of leave of absence).

This issue is related to the validation of type assignments.

A fix for this will be provided shortly.


TODO
""""
 * Adapters must be reworked
