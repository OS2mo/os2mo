# -- coding: utf-8 --

import json
from uuid import uuid4
from requests import Session
from os2mo_data_import import Organisation
from os2mo_data_import import adapters
from os2mo_data_import import http_utils


class ImportUtility(Session):

    def __init__(self, organisation_object, dry_run=True):

        if not isinstance(organisation_object, Organisation):
            raise TypeError("Object is not of type Organisation")

        self.dry_run = dry_run
        self.Org = organisation_object

        # Inserted uuid maps
        self.inserted_facet = {}
        self.inserted_klasse = {}

    def create_uuid(self):
        uuid = uuid4()
        return str(uuid)

    def dummy_validity(self):
        return {
            "from": "1900-01-01",
            "to": "infinity"
        }

    def jsonify(self, data_as_dict):
        output = json.dumps(data_as_dict, indent=2)
        print(output)

    def import_organisation(self):
        """
        TODO: add actual import functionality
        """

        # Organisation
        org_export = self.Org.export()
        org_data = adapters.build_organisation_payload(org_export)

        self.uuid = self.create_uuid()

        return self.jsonify(org_data)

    def import_facet(self):
        """
        TODO: add actual import functionality
        """
        all_items = self.Org.Facet.export()

        for item in all_items:

            identifier, data = item

            if "validity" not in data:
                data["validity"] = self.dummy_validity()

            payload = adapters.build_facet_payload(data, self.uuid)

            self.inserted_facet[identifier] = self.create_uuid()

            # self.jsonify(payload)

    def import_klasse(self):
        """
        TODO: add actual import functionality
        """

        all_items = self.Org.Klasse.export()

        for item in all_items:
            identifier, data = item

            facet_type_ref = data["facet_type_ref"]
            facet_data = data["data"]

            if "validity" not in facet_data:
                facet_data["validity"] = self.dummy_validity()

            facet_uuid = self.inserted_facet.get(facet_type_ref)

            payload = adapters.build_klasse_payload(
                klasse=facet_data,
                facet_ref=facet_uuid,
                parent_org=self.uuid
            )

            self.inserted_klasse[identifier] = self.create_uuid()

            # self.jsonify(payload)

    def import_org_unit(self):
        """
        TODO: add actual import functionality
        """

        all_units = self.Org.OrganisationUnit.export()

        for unit in all_units:
            identifier, content = unit

            data = content["data"]

            # TODO: missing functionality to append optional data
            optional_data = content["optional_data"]

            payload = self.build_mo_payload(data)
            self.jsonify(payload)

    def import_employee(self):
        """
        TODO: add actual import functionality
        """

        all_employees = self.Org.Employee.export()

        for employee in all_employees:
            identifier, content = employee

            data = content["data"]

            # TODO: missing functionality to append optional data
            optional_data = content["optional_data"]

            payload = self.build_mo_payload(data)
            self.jsonify(payload)

    def build_mo_payload(self, list_of_tuples):

        payload = {}

        regular_set = [
            "type",
            "name",
            "cpr_no",
            "validity"
        ]

        for key, val in list_of_tuples:

            if key in regular_set:
                payload[key] = val

            if key == "parent":
                # TODO: Missing mapping, using org uuid instead
                payload[key] = {
                    "uuid": self.uuid
                }

            if key == "org_unit_type":
                org_unit_type = self.inserted_klasse.get(val)

                if not org_unit_type:
                    print(key, val)
                    print(self.inserted_klasse)
                    raise RuntimeError("Type not found")

                payload[key] = {
                    "uuid": org_unit_type
                }

            if "parent" not in payload:
                payload["org"] = {
                    "uuid": self.uuid
                }

        return payload

    def import_all(self):

        self.import_organisation()
        self.import_facet()
        self.import_klasse()
        self.import_org_unit()
        self.import_employee()

        return

