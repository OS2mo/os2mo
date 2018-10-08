# -- coding: utf-8 --

from uuid import uuid4
from requests import Session
from urllib.parse import urljoin
from os2mo_data_import import adapters
from os2mo_data_import import Organisation

# Default settings
MOX_BASE = "http://localhost:8080"
MORA_BASE = "http://localhost:5000"


class ImportUtility(object):

    def __init__(self, dry_run=True, mox_base=MOX_BASE, mora_base=MORA_BASE):
        # Service endpoints
        self.mox_base = mox_base
        self.mora_base = mora_base

        # Session
        self.dry_run = dry_run
        self.session = Session()

    def insert_mox_data(self, resource, data):

        service = urljoin(self.mox_base, resource)

        if self.dry_run:
            response_data = {
                "uuid": str(
                    uuid4()
                )
            }
        else:
            response = self.session.post(url=service, json=data)
            response_data = response.json()

        return response_data["uuid"]

    def insert_mora_data(self, resource, data):

        service = urljoin(self.mora_base, resource)

        if self.dry_run:
            response_data = str(
                uuid4()
            )
        else:
            response = self.session.post(url=service, json=data)
            response_data = response.json()

        return response_data

    def get_facet_types(self):

        if hasattr(self, "facet_types"):
            return

        self.facet_types = {}

        resource = "service/o/{uuid}/f/{type}/".format(
            uuid=self.uuid,
            type="address_type"
        )

        service = urljoin(self.mora_base, resource)


        if self.dry_run:
            for value in self.inserted_klasse.values():
                print("#######", value)
                self.facet_types[value] = {
                    "uuid": value
                }

                print(
                    self.facet_types
                )
        else:
            response = self.session.get(service)

            if response.status_code != 200:
                print(response.text)
                raise RuntimeError(response.text)

            response_data = response.json()

            if "items" not in response_data["data"]:
                return False

            print("Facet types")
            for item in response_data["data"]["items"]:
                uuid = item["uuid"]
                self.facet_types[uuid] = item

        return True

    def import_organisation(self):
        """
        Import Organisation into datastore
        """

        # Organisation
        export_data = self.Org.export()

        self.validity = export_data["validity"]

        org_data = adapters.organisation_payload(
            organisation=export_data["data"],
            municipality_code=export_data["municipality_code"],
            validity=self.validity
        )

        if "uuid" in export_data:
            # TODO: Import uuid if passed
            pass

        self.uuid = self.insert_mox_data(
            resource="organisation/organisation",
            data=org_data
        )

        return self.uuid

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
            "kaldenavn": identifier
        }

        klassifikation_data = adapters.klassifikation_payload(
            klassifikation=klassifikation,
            organisation_uuid=self.uuid,
            validity=self.Org.validity
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

            payload = adapters.facet_payload(
                facet=data,
                klassifikation_uuid=self.klassifikation_uuid,
                organisation_uuid=self.uuid,
                validity=self.validity
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

            facet_uuid = self.inserted_facet.get(facet_type_ref)

            payload = adapters.klasse_payload(
                klasse=klasse_data,
                facet_uuid=facet_uuid,
                organisation_uuid=self.uuid,
                validity=self.validity
            )

            print(payload)

            self.inserted_klasse[identifier] = self.insert_mox_data(
                resource="klassifikation/klasse",
                data=payload
            )

        return self.inserted_klasse

    def import_itsystem(self):
        all_items = self.Org.Itsystem.export()

        self.inserted_itsystem = {}

        for item in all_items:
            identifier, data = item

            payload = adapters.itsystem_payload(
                itsystem=data,
                organisation_uuid=self.uuid,
                validity=self.validity
            )

            store = self.insert_mox_data(
                resource="organisation/itsystem",
                data=payload
            )

            self.inserted_itsystem[identifier] = store

        return self.inserted_itsystem

    def import_org_units(self):
        """
        TODO: add actual import functionality
        """

        all_units = self.Org.OrganisationUnit.export()

        for unit in all_units:
            identifier, content = unit

            parent_ref = content["parent_ref"]

            if parent_ref:
                parent_data = self.Org.OrganisationUnit.get(parent_ref)
                store = self._insert_org_unit(parent_ref, parent_data["data"])

                if store:
                    self._insert_optional_org_unit(store, parent_data["optional_data"])


            store_pr = self._insert_org_unit(identifier, content["data"])

            if store_pr:
                self._insert_optional_org_unit(store_pr, content["optional_data"])

        return self.inserted_org_unit

    def _insert_org_unit(self, identifier, data):

        if identifier in self.inserted_org_unit:
            return False

        payload = self.build_mo_payload(data)

        store = self.insert_mora_data(resource="service/ou/create", data=payload)
        print("STORING ORG UNIT: %s" % store)
        if not store:
            print(store)
            raise RuntimeError("COULD NOT STORE ORG UNIT")


        self.inserted_org_unit[identifier] = store

        return self.inserted_org_unit[identifier]

    def _insert_optional_org_unit(self, uuid, data):

        if not uuid:
            raise RuntimeError("UUID IS MISSING")

        process_optional = [
            self.build_mo_payload(item)
            for item in data
        ]

        resource = "service/ou/{uuid}/create".format(uuid=uuid)

        opt_yes = self.insert_mora_data(resource=resource, data=process_optional)

        return opt_yes



    def _insert_optional(self, uuid, data):

        process_optional = [
            self.build_mo_payload(item)
            for item in data
        ]

        for i in process_optional:
            print(i)

        resource = "service/e/{uuid}/create".format(uuid=uuid)

        opt_yes = self.insert_mora_data(resource=resource, data=process_optional)

        print(opt_yes)

        return True

    def _insert_employee(self, identifier, content):

        if identifier in self.inserted_employees:
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
            "engagement_type",
            "manager_type",
            "manager_level",
            "association_type"
        ]

        # Get facet types
        self.get_facet_types()

        # Prep for adapter
        build_value = None

        for key, val in list_of_tuples:

            if key in regular_set:
                build_value = val

            if key in reference_types:
                uuid = self.inserted_klasse.get(val)

                build_value = {
                    "uuid": str(uuid)
                }

            if key == "itsystem":
                uuid = self.inserted_itsystem.get(val)
                build_value = {
                    "uuid": uuid
                }

            if key == "org":
                build_value = {
                    "uuid": self.uuid
                }

            if key == "org_unit":
                uuid = self.inserted_org_unit.get(val)
                build_value = {
                    "uuid": str(uuid)
                }

            if key == "address_type":
                uuid = self.inserted_klasse.get(val)

                address_type = self.facet_types.get(uuid)

                print("!!!!!!!")
                print(address_type)

                build_value = address_type

            if key == "address":
                type_uuid = self.inserted_klasse.get("AdressePost")

                address_type = self.facet_types.get(type_uuid)

                build_value = {
                    "uuid": str(val),
                    "address_type": address_type
                }

            if key == "parent":
                print("GETTING PARENT: %s" % val)
                parent_uuid = self.inserted_org_unit.get(val)
                print("PARENT HAS UUID: %s" % parent_uuid)

                if not parent_uuid:
                    parent_uuid = self.uuid

                build_value = {
                    "uuid": str(parent_uuid)
                }

            if key == "org_unit_type":
                org_unit_type = self.inserted_klasse.get(val)

                if not org_unit_type:
                    print(key, val)
                    print(self.inserted_klasse)
                    raise RuntimeError("Type not found")

                build_value = {
                    "uuid": org_unit_type
                }

            if key == "responsibility":
                responsibility_list = []

                for responsibility in val:

                    uuid = self.inserted_klasse.get(responsibility)

                    reference = {
                        "uuid": uuid
                    }

                    responsibility_list.append(reference)

                build_value = responsibility_list

            if not build_value:
                print(key, val)
                raise ValueError("Unable to create build value")


            payload[key] = build_value

        return payload


    def import_all(self, org):

        self.Org = org

        # Inserted uuid maps
        self.inserted_facet = {}
        self.inserted_klasse = {}
        self.inserted_org_unit = {}
        self.inserted_employees = {}

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
