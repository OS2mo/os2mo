# -- coding: utf-8 --

import json
from uuid import uuid4
from requests import Session
from os2mo_data_import.data_types import Organisation
from os2mo_data_import import adapters


class ImportUtility(Session):

    def __init__(self, organisation_object, dry_run=True):

        if not isinstance(organisation_object, Organisation):
            raise TypeError("Object is not of type Organisation")

        # Init base class
        super().__init__()

        # Meta
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

        self.uuid = self.insert_mox_data(
            resource="organisation/organisation",
            data=org_data
        )

        return self.uuid

    def insert_mox_data(self, resource, data):

        base = "http://localhost:8080"
        service = "{base}/{resource}".format(
            base=base,
            resource=resource
        )

        response = self.post(url=service, json=data)

        r = response.json()

        if not "uuid" in r:
            print(response.text)

        return r["uuid"]

    def insert_mora_data(self, resource, data):

        base = "http://localhost:5000"
        service = "{base}/{resource}".format(
            base=base,
            resource=resource
        )

        response = self.post(url=service, json=data)

        if response.status_code != 200:
            print("======== FAILED ========")
            print(data)
            print(response.text)

        return response.json()

    def import_klassifikation(self):

        user_key = (
            self.Org.user_key or self.Org.name
        )

        identifier = user_key
        bvn = "Organisation {name}".format(name=user_key)
        description = "Belongs to {name}".format(name=user_key)

        klassifikation = {
            "brugervendtnoegle": bvn,
            "beskrivelse": description,
            "kaldenavn": identifier,
            "validity": self.Org.validity
        }

        klassifikation_data = adapters.build_klassifikation_payload(
            klassifikation=klassifikation,
            organisation_uuid=self.uuid
        )

        self.klassifikation_uuid = self.insert_mox_data(
            resource="klassifikation/klassifikation",
            data=klassifikation_data
        )

        return self.klassifikation_uuid

    def import_facet(self):
        """
        TODO: add actual import functionality
        """
        all_items = self.Org.Facet.export()

        for item in all_items:

            identifier, data = item

            if "validity" not in data:
                data["validity"] = self.dummy_validity()

            payload = adapters.build_facet_payload(
                facet=data,
                klassifikation_uuid=self.klassifikation_uuid,
                organisation_uuid=self.uuid
            )

            facet_uuid = self.insert_mox_data(
                resource="klassifikation/facet",
                data=payload
            )

            self.inserted_facet[identifier] = facet_uuid

        return self.inserted_facet

    def import_klasse(self):
        """
        TODO: add actual import functionality
        """

        all_items = self.Org.Klasse.export()

        for item in all_items:
            identifier, data = item

            facet_type_ref = data["facet_type_ref"]
            klasse_data = data["data"]

            print("KLASSE DATA ++++++")
            print(klasse_data)

            if "validity" not in klasse_data:
                klasse_data["validity"] = self.dummy_validity()

            facet_uuid = self.inserted_facet.get(facet_type_ref)

            payload = adapters.build_klasse_payload(
                klasse=klasse_data,
                facet_uuid=facet_uuid,
                organisation_uuid=self.uuid
            )

            self.inserted_klasse[identifier] = self.insert_mox_data(
                resource="klassifikation/klasse",
                data=payload
            )

        return self.inserted_klasse

    def import_itsystem(self):
        all_items = self.Org.Itsystem.export()

        for item in all_items:
            identifier, data = item

            payload = adapters.build_it

    def import_org_units(self):
        """
        TODO: add actual import functionality
        """

        all_units = self.Org.OrganisationUnit.export()

        self.inserted_org_unit = {}

        for unit in all_units:
            identifier, content = unit

            parent_ref = content["parent_ref"]

            if parent_ref:
                parent_data = self.Org.OrganisationUnit.get(parent_ref)
                self._insert_org_unit(parent_ref, parent_data["data"])

            self._insert_org_unit(identifier, content["data"])

        return self.inserted_org_unit

    def _insert_org_unit(self, identifier, data):

        if identifier in self.inserted_org_unit:
            return False

        payload = self.build_mo_payload(data)

        store = self.insert_mora_data(resource="service/ou/create", data=payload)

        self.inserted_org_unit[identifier] = store

        return True

    def get_facet_types(self):

        if hasattr(self, "facet_types"):
            return

        self.facet_types = {}

        resource = "service/o/{uuid}/f/{type}/".format(
            uuid=self.uuid,
            type="address_type"
        )

        service = "{base}/{resource}".format(
            base="http://localhost:5000",
            resource=resource
        )

        response = self.get(service)

        if response.status_code != 200:
            print(response.text)
            raise RuntimeError(response.text)

        data = response.json()

        if "items" not in data["data"]:
            return False

        print("Facet types")
        for item in data["data"]["items"]:
            uuid = item["uuid"]
            print(uuid)
            self.facet_types[uuid] = item

        return True

    def _insert_optional(self, uuid, data):

        process_optional = [
            self.build_mo_payload(item)
            for item in data
        ]

        resource = "service/e/{uuid}/create".format(uuid=uuid)

        opt_yes = self.insert_mora_data(resource=resource, data=process_optional)

        print(opt_yes)

        return True

    def _insert_employee(self, identifier, content):

        if identifier in self.inserted_org_unit:
            return False

        data = content["data"]
        optional_data = content["optional_data"]

        payload = self.build_mo_payload(data)

        store = self.insert_mora_data(resource="service/e/create", data=payload)

        self.inserted_employees[identifier] = store

        self._insert_optional(store, optional_data)
        return True

    def import_employees(self):
        """
        TODO: add actual import functionality
        """

        self.inserted_employees = {}

        all_employees = self.Org.Employee.export()

        for employee in all_employees:
            identifier, content = employee

            uuid = self._insert_employee(identifier, content)

        return self.inserted_employees


    def build_mo_payload(self, list_of_tuples):

        payload = {}

        regular_set = [
            "type",
            "name",
            "cpr_no",
            "validity",
            "uuid",
            "value"
        ]

        reference_types = [
            "role_type",
            "leave_type",
            "it_type",
            "job_function",
            "engagement_type"
        ]

        if not hasattr(self, "facet_types"):
            self.get_facet_types()

        for key, val in list_of_tuples:

            if key == "itsystem":
                self.inserted_itsystem.get(val)
                payload[key] = {
                    "uuid": self.uuid
                }

            if key == "org":
                payload[key] = {
                    "uuid": self.uuid
                }

            if key in regular_set:
                payload[key] = val

            if key in reference_types:
                uuid = self.inserted_klasse.get(val)

                payload[key] = {
                    "uuid": str(uuid)
                }

            if key == "org_unit":
                uuid = self.inserted_org_unit.get(val)
                payload[key] = {
                    "uuid": str(uuid)
                }

            if key == "address_type":
                uuid = self.inserted_klasse.get(val)

                address_type = self.facet_types.get(uuid)

                print(address_type)

                payload[key] = address_type


            if key == "parent":

                if val:
                    parent_uuid = self.inserted_org_unit.get(val)
                else:
                    parent_uuid = self.uuid

                payload[key] = {
                    "uuid": str(parent_uuid)
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

        store = self.import_organisation()
        print(store)

        store = self.import_klassifikation()
        print(store)

        store = self.import_facet()
        print(store)

        store = self.import_klasse()
        print(store)

        store = self.import_itsystem()
        print(store)

        store = self.import_org_units()
        print(store)

        store = self.import_employees()
        print(store)

        return

