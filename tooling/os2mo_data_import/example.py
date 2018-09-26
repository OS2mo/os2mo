# -- coding: utf-8 --

from os2mo_data_import import Organisation
from os2mo_data_import.data_import import import_handler


def example_import():
    """
    This example requires that the os2mo_data_import library is installed!

    Install into venv or python path:

        pip install -e /path/to/os2mo_data_import

    Run the example:

        python /path/to/os2mo_data_import/example.py

    !! Unittest is missing !!

    """

    # Init org

    org = Organisation("Enterprise", "Starship Enterprise")
    print(org)

    # Show all default facet and klasse values
    all_facet = org.Facet.export()
    print(all_facet)

    all_klasse = org.Klasse.export()
    print(all_klasse)

    # Example: add klasse with reference to new random type facet
    # Every key/value pair will be added as properties ("klasseegenskaber")
    org.Klasse.add(
        identifier="Command bridge",  # Identifier to recall the item
        facet_type_ref="Enhedstype",  # Belongs to facet: Enhedstype
        brugervendtnoegle="Command bridge",
        omfang="TNG",
        titel="This is the place where cool officers hang out"
    )

    # Example: Organisation Unit
    # Required: name, org_unit_type_ref, date_from, date_to
    org.OrganisationUnit.add(
        identifier="Officers",
        org_unit_type_ref="Command bridge",  # This unit is of type: Bridge section
        date_from="1986-01-01",
        date_to=None
    )

    # Create "Science Officers"
    # Use parent_ref to make it a sub group of "Officers"
    org.OrganisationUnit.add(
        identifier="Science Officers",
        org_unit_type_ref="Command bridge",  # This unit is of type: Bridge section
        parent_ref="Officers",  # Sub unit of/Belongs to Officers unit
        date_from="1986-01-01",
        date_to=None
    )


    # Employee

    new_employee = org.Employee.add(
        identifier="Jean-Luc Picard",
        cpr_no="1112114455",
        date_from="1986-01-01"
    )

    # Another employee
    org.Employee.add(
        identifier="William Riker",
        cpr_no="1212114455",
        date_from="1986-01-01"
    )


    # JOB AND ENGAGEMENT

    # Add job type "Bridge Officer
    org.Klasse.add(
        identifier="Bridge Officer",
        facet_type_ref="Stillingsbetegnelse",
        brugervendtnoegle="Bridge Officer",
        titel="Bridge Officer"
    )

    # Get job function type uuid
    org.Employee.add_type_engagement(
        owner_ref="William Riker",
        org_unit_ref="Officers",
        job_function_ref="Bridge Officer",
        engagement_type_ref="Ansat",
        date_from="1986-01-01"
    )


    # Addresses

    org.Employee.add_type_address(
        owner_ref="William Riker",
        uuid="213234234",
        address_type_ref="AdressePost",
        date_from="1986-01-01",
    )


    # ROLES

    org.Klasse.add(
        identifier="Command",
        facet_type_ref="Stillingsbetegnelse",
        brugervendtnoegle="Command function",
        titel="In command of designated unit"
    )

    org.Employee.add_type_role(
        owner_ref="William Riker",
        org_unit_ref="Officers",
        role_type_ref="Command",
        date_from="1986-01-01"
    )


    # LEADERSHIP

    # Manager type
    org.Klasse.add(
        identifier="Teamleader",
        facet_type_ref="Ledertyper",
        brugervendtnoegle="Teamleader",
        titel="In charge of various teams"
    )

    # Manager level
    org.Klasse.add(
        identifier="Priority",
        facet_type_ref="Lederniveau",
        brugervendtnoegle="Priority",
        titel="Command Alpha-Gamma-Six"
    )

    # Add responsabilities
    org.Klasse.add(
        identifier="Distribute tasks",
        facet_type_ref="Lederansvar",
        brugervendtnoegle="Distribute tasks",
        titel="Must distribute tasks amongst crewmen"
    )

    org.Klasse.add(
        identifier="Comm Officer",
        facet_type_ref="Lederansvar",
        brugervendtnoegle="Comm Officer",
        titel="Must establish and maintain comms"
    )

    org.Employee.add_type_manager(
        owner_ref="William Riker",
        org_unit_ref="Officers",
        manager_type_ref="Priority",
        manager_level_ref="Teamleader",
        address_uuid="F28B0B96-8D1A-4FFF-AB47-FA7E105B1CA8",  # Fake address uuid
        responsibility_list=["Distribute tasks", "Comm Officer"],
        date_from="1986-01-01",
    )


    # Leave of absence

    org.Klasse.add(
        identifier="RNR",
        facet_type_ref="Lederansvar",
        brugervendtnoegle="RNR",
        titel="Rest and Recreation"
    )

    org.Employee.add_type_leave(
        owner_ref="William Riker",
        leave_type_ref="RNR",
        date_from="1986-10-22",
        date_to="1986-10-29"
    )

    # Itsystem

    org.Itsystem.add(
        identifier="Main Computer",
        system_name="Main Computer"
    )

    org.Employee.add_type_itsystem(
        owner_ref="William Riker",
        itsystem_ref="Main Computer",
        date_from="1986-01-01"
    )

    # # Show all employee metadata
    employee = org.Employee.get("William Riker")

    data = employee["data"]
    optional_data = employee["optional_data"]

    print("Employee data:")
    for item in data:
        print(item)

    print("Employee optional data:")
    for item in optional_data:
        print(item)


    # TODO: MAKE THIS WORK!
    from os2mo_data_import.utility import ImportUtility

    os2mo = ImportUtility(org, dry_run=True)
    os2mo.import_all()


if __name__ == "__main__":
    example_import()
