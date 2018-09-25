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


    address = org.Employee.add_type_address(
        identifier="William Riker",
        value="213234234",
        type_ref="AdressePost",
        value_as_uuid=True,
        date_from="1986-01-01",
    )

    print(address)

    all_meta_data = org.Employee.get_optional_data("William Riker")
    for data in all_meta_data:
        print(data)


if __name__ == "__main__":
    example_import()
