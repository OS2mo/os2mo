# -- coding: utf-8 --

from os2mo_data_import.adapters import Organisation
import os2mo_data_import.http_utils as importutil

def example_import():

    # Init org
    org = Organisation("Enterprise", "Starship Enterprise")

    # Show all default facet and klasse values
    all_facet = org.Facet.get_map()
    print(all_facet)

    all_klasse = org.Klasse.get_map()
    print(all_klasse)

    # Example: show uuid for address_type "Telefon" (phone number)
    phone_no = org.Klasse.get_uuid("Telefon")
    print(phone_no)

    # Example: show data for address_type "Telefon" (phone number)
    # This is the post data payload for the web api import
    phone_data = org.Klasse.get_data("Telefon")
    print(phone_data)

    # Example: add additional facet type
    new_facet = org.Facet.add("Shipsection")

    # UUID is returned
    print(new_facet)

    # It is now possible to reference the new type
    section_type = org.Facet.get_uuid("Shipsection")
    print("Shipsection has uuid: %s" % section_type)

    # Example: add klasse with reference to new random type facet
    # Every key/value pair will be added as properties ("klasseegenskaber")
    new_klasse_data = {
        "brugervendtnoegle": "Command bridge",
        "titel": "This is the place where cool officers hang out"
    }

    supersection = org.Klasse.add(
        identifier="Bridge",  # Identifier to recall the item
        facet_ref=section_type,  # Belongs to facet: Shipsection
        properties=new_klasse_data
    )

    # Creation uuid is returned
    print("Bridge type has uuid: %s" % supersection)

    # or uuid can be retrieved
    bridge_section_uuid = org.Klasse.get_uuid("Bridge")
    print("Bridge type has uuid: %s" % bridge_section_uuid)


    # Example: Organisation Unit
    # Required: name, type_ref, date_from, date_to
    org_unit = org.OrganisationUnit.add(
        name="Officers",
        type_ref=bridge_section_uuid,  # This unit is of type: Bridge section
        date_from="1986-01-01",
        date_to=None
    )

    # UUID is returned
    print(org_unit)

    # The UUID of the new unit can be retrieved:
    officers_unit = org.OrganisationUnit.get_uuid("Officers")
    print("Officers unit has uuid: %s" % officers_unit)

    # Employee
    new_employee = org.Employee.add(
        name="Jean-Luc Picard",
        cpr_no="1122331133",
        date_from="1986-01-01"
    )

    print("New employee: %s" % new_employee)


    # Another employee
    org.Employee.add(
        name="William Riker",
        cpr_no="1122331133",
        date_from="1986-01-01"
    )

    # Show map of employees
    employees_map = org.Employee.get_map()
    print(employees_map)

if __name__ == "__main__":
    example_import()
