# -- coding: utf-8 --

from os2mo_data_import import Organisation
# from os2mo_data_import.http_utils import temp_import_all


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

    # Example: add additional facet type
    new_facet = org.Facet.add(identifier="Shipsection", user_key="shipsec")

    # What is returned
    print(new_facet)

    # Example: add klasse with reference to new random type facet
    # Every key/value pair will be added as properties ("klasseegenskaber")
    new_klasse_data = {
        "brugervendtnoegle": "Command bridge",
        "omfang": "TNG",
        "titel": "This is the place where cool officers hang out"
    }

    supersection = org.Klasse.add(
        identifier="Bridge",  # Identifier to recall the item
        facet_type="Shipsection",  # Belongs to facet: Shipsection
        properties=new_klasse_data
    )

    # Creation uuid is returned
    print(supersection)



    # Example: Organisation Unit
    # Required: name, type_ref, date_from, date_to
    org_unit = org.OrganisationUnit.add(
        identifier="Officers",
        type_ref="Bridge",  # This unit is of type: Bridge section
        date_from="1986-01-01",
        date_to=None
    )

    # Tuple containing identifier and data is returned
    print(org_unit)


    # Create "Science Officers"
    # Use parent_ref to make it a sub group of "Officers"
    science_unit = org.OrganisationUnit.add(
        identifier="Science Officers",
        type_ref="Bridge",  # This unit is of type: Bridge section
        parent_ref="Officers",  # Sub unit of/Belongs to Officers unit
        date_from="1986-01-01",
        date_to=None
    )

    print(science_unit)


    # Employee
    new_employee = org.Employee.add(
        identifier="Jean-Luc Picard",
        cpr_no="1112114455",
        date_from="1986-01-01"
    )

    print(new_employee)


    # Another employee
    org.Employee.add(
        identifier="William Riker",
        cpr_no="1212114455",
        date_from="1986-01-01"
    )

    # Show map of employees
    employees_map = org.Employee.export()
    for employee in employees_map:

        print(employee)


    # JOB AND ENGAGEMENT

    # Add job type "Bridge Officer
    bridge_officer_job = dict(
        brugervendtnoegle="Bridge Officer",
        titel="Bridge Officer",
    )

    org.Klasse.add(
        identifier="Bridge Officer",
        facet_type="Stillingsbetegnelse",
        properties=bridge_officer_job
    )

    # Get job function type uuid

    new_job = org.Employee.add_type_engagement(
        identifier="William Riker",
        org_unit_ref="Officers",
        job_function_ref="Bridge Officer",
        engagement_type_ref="Ansat",
        date_from="1986-01-01"
    )

    print(new_job)


    # Addresses
    address = org.Employee.add_type_address(
        identifier="William Riker",
        value="213234234",
        type_ref="AdressePost",
        value_as_uuid=True,
        date_from="1986-01-01",
    )

    print(address)



    # ROLES
    command_role = {
        "brugervendtnoegle": "Command function",
        "titel": "In command of designated unit"
    }

    org.Klasse.add(
        identifier="Command",
        facet_type="Stillingsbetegnelse",
        properties=command_role
    )



    create_role = org.Employee.add_type_role(
        identifier="William Riker",
        org_unit_ref="Officers",
        role_type_ref="Command",
        date_from="1986-01-01"
    )

    print(create_role)


    # LEADERSHIP

    # Manager type
    manager_type_data = {
        "brugervendtnoegle": "Teamleader",
        "titel": "In charge of various teams"
    }

    manager_type = org.Klasse.add(
        identifier="Fee",
        facet_type="Ledertyper",
        properties=manager_type_data
    )

    # Manager level
    priority_level = {
        "brugervendtnoegle": "Priority",
        "titel": "Command Alpha-Gamma-Six"
    }

    # Add responsability levels
    org.Klasse.add(
        identifier="Priority",
        facet_type="Lederniveau",
        properties=priority_level
    )

    # Add responsabilities
    distribute_tasks = {
        "brugervendtnoegle": "Distribute tasks",
        "titel": "Must distribute tasks amongst crewmen"
    }

    comm_officer = {
        "brugervendtnoegle": "Comm Officer",
        "titel": "Must establish and maintain comms"
    }

    # Add responsabilities
    org.Klasse.add(
        identifier="Distribute tasks",
        facet_type="Lederansvar",
        properties=priority_level
    )

    org.Klasse.add(
        identifier="Comm Officer",
        facet_type="Lederansvar",
        properties=priority_level
    )

    management = org.Employee.add_type_manager(
        identifier="William Riker",
        org_unit_ref="Officers",
        manager_type_ref="Priority",
        manager_level_ref="Teamleader",
        address_uuid="F28B0B96-8D1A-4FFF-AB47-FA7E105B1CA8",  # Fake address uuid
        responsabilities=["Distribute tasks", "Comm Officer"],
        date_from="1986-01-01",
    )

    print(management)


    # Leave of absence
    leave_type = {
        "brugervendtnoegle": "RNR",
        "titel": "Rest and Recreation"
    }

    org.Klasse.add(
        identifier="RNR",
        facet_type="Lederansvar",
        properties=leave_type
    )

    period_of_leave = org.Employee.add_type_leave(
        identifier="William Riker",
        leave_type_ref="RNR",
        date_from="1986-10-22",
        date_to="1986-10-29"
    )

    print(period_of_leave)


    # Itsystem
    org.Itsystem.add(
        identifier="Main Computer",
        system_name="Main Computer"
    )

    it_system = org.Employee.add_type_itsystem(
        identifier="William Riker",
        itsystem_ref="Main Computer",
        date_from="1986-01-01"
    )

    print(it_system)


    # Show all employee metadata
    all_meta_data = org.Employee.get_optional_data("William Riker")
    for data in all_meta_data:
        print(data)


if __name__ == "__main__":
    example_import()
