# -- coding: utf-8 --

from uuid import uuid4
from os2mo_data_import import Organisation
from os2mo_data_import import adapters
from os2mo_data_import import http_utils


def import_handler(org):

    if not isinstance(org, Organisation):
        raise TypeError("Object is not of type Organisation")

    org_export = org.export()

    org_data = adapters.build_organisation_payload(**org_export)
    org_uuid = http_utils.insert_mox_data(
        resource="organisation/organisation",
        payload=org_data
    )

    facet_map = {}

    for item in org.Facet.export():
        identifier, data = item

        properties = {
            "parent_org": org_uuid,
            "date_from": "1900-01-01"
        }

        data.update(properties)

        payload = adapters.build_facet_payload(**data)

        uuid = uuid4()
        store = http_utils.import_mox_data(
            identifier=uuid,
            resource="klassifikation/facet",
            payload=payload
        )

        facet_map[identifier] = store["uuid"]


    klasse_map = {}

    for item in org.Klasse.export():
        identifier, data = item

        facet_type = data.pop("facet_type")
        facet_ref = facet_map.get(facet_type)

        properties = {
            "facet_ref": facet_ref,
            "parent_org": org_uuid,
            "date_from": "1900-01-01"
        }

        data.update(properties)

        payload = adapters.build_klasse_payload(**data)

        uuid = uuid4()
        store = http_utils.import_mox_data(
            identifier=uuid,
            resource="klassifikation/klasse",
            payload=payload
        )

        klasse_map[identifier] = store["uuid"]




    all_units = org.OrganisationUnit.export()

    org_unit_map = {}

    while all_units:

        for unit in all_units:

            identifier, data = unit
            parent_ref = data.get("parent_ref")
            print("PARENT %s" % parent_ref)


            if parent_ref and parent_ref not in org_unit_map:
                continue

            parent_uuid = org_unit_map.get(parent_ref)


            name = data.get("name")
            type_ref = data.get("type_ref")
            type_uuid = klasse_map[type_ref]

            date_from, date_to = data.get("validity")


            payload = adapters.build_org_unit_payload(
                name=(name or identifier),
                parent_uuid=(parent_uuid or org_uuid),
                type_uuid=type_uuid,
                date_from=date_from,
                date_to=date_to
            )

            store = http_utils.import_mora_data(
                resource="service/ou/create",
                payload=payload
            )

            # TODO: insert optional data also

            org_unit_map[identifier] = store

            all_units.remove(unit)

    employee_map = {}

    for employee in org.Employee.export():

        identifier, data = employee

        name = data.get("name")
        user_key = data.get("user_key")
        cpr_no = data.get("cpr_no")

        date_from, date_to = data.get("validity")

        payload = adapters.build_employee_payload(
            name=(name or identifier),
            user_key=user_key,
            cpr_no=cpr_no,
            org_ref=org_uuid,
            date_from=date_from,
            date_to=date_to
        )

        store = http_utils.import_mora_data(
            resource="service/e/create",
            payload=payload
        )

        employee_map[identifier] = store


    for emp in employee_map.items():
        print(emp)


