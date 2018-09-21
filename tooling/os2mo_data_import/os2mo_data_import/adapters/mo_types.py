# -- coding: utf-8 --

from os2mo_data_import.adapters.base import MemoryMap

# TODO: Fix the inelegant extension of the Memory map in order to gain metadata storage
class MoBase(MemoryMap):

    storage_map = {}

    def get_metadata(self, identifier):

        if not identifier in self.storage_map:
            raise ValueError("Item does not exist")

        return self.storage_map[identifier]["metadata"]


    def set_metadata(self, identifier, metadata):

        if not identifier in self.storage_map:
            raise ValueError("Item does not exist")

        if not isinstance(metadata, dict):
            raise TypeError("Metadata type must be dict")

        if not "metadata" in self.storage_map[identifier]:
            self.storage_map[identifier] = {
                "metadata": []
            }

        if metadata in  self.storage_map[identifier]["metadata"]:
            return False

        self.storage_map[identifier]["metadata"].append(metadata)

        return True

    def ordered_export(self):

        all_items = {
            item["uuid"] : item["data"]
            for item in self.storage_map.values()
        }

        export_data = []
        ordered_list_for_insertion = []
        waiting_for_import = []

        for item in all_items.items():

            uuid, data = item

            if data["parent"]["uuid"] == self.parent_org:
                ordered_list_for_insertion.append(uuid)
                export_data.append(
                    (uuid, data)
                )
            else:
                waiting_for_import.append(uuid)

        while waiting_for_import:

            for item in all_items.items():

                uuid, data = item

                if data["parent"]["uuid"] in ordered_list_for_insertion:
                    ordered_list_for_insertion.append(uuid)
                    export_data.append(
                        (uuid, data)
                    )
                    waiting_for_import.remove(uuid)

        return export_data

    def add_type_address(self, identifier, value, type_ref, date_from, date_to=None, value_as_uuid=False):

        payload = {
            "value": value,
            "address_type": type_ref,
            "type": "address",
            "validity": {
                "from": date_from,
                "to": date_to
            }
        }

        if value_as_uuid:
            payload["uuid"] = payload.pop("value")

        return self.set_metadata(identifier, payload)


class OrganisationUnit(MoBase):

    def __init__(self, parent_org):
        self.parent_org = parent_org
        self.storage_map = {}

    def add(self, identifier, type_ref, date_from, date_to=None, name=None, parent_ref=None, user_key=None):

        if not parent_ref:
            parent_ref = self.parent_org

        if not name:
            name = identifier

        data = {
            "name": name,
            "parent": {
                "uuid": parent_ref
            },
            "org_unit_type": {
                "uuid": type_ref
            },
            "validity": {
                "from": date_from,
                "to": date_to
            }
        }

        # Add user key to the data payload if passed
        # Default is auto generated UUID
        if user_key:
            data.update({
                "user_key": user_key
            })

        return self.save(identifier=identifier, data=data)


class Employee(MoBase):

    # TODO: add association type
    # TODO: unify meta types

    def __init__(self, parent_org):
        self.parent_org = parent_org
        self.storage_map = {}

    def add(self, identifier, cpr_no, date_from, date_to=None, name=None, user_key=None):

        if not name:
            name = identifier

        data = {
            "name": name,
            "cpr_no": cpr_no,
            "org": {
                "uuid": self.parent_org
            },
            "validity": {
                "from": date_from,
                "to": date_to
            }
        }

        # Add user key to the data payload if passed
        # Default is auto generated UUID
        if user_key:
            data.update({
                "user_key": user_key
            })

        return self.save(identifier=identifier, data=data)

    def add_type_engagement(self, identifier, org_unit_ref, job_function_type,
                            engagement_type, date_from, date_to=None):

        payload = {
            "type": "engagement",
            "org_unit": {
                "uuid": org_unit_ref
            },
            "job_function": {
                "uuid": job_function_type
            },
            "engagement_type": {
                "uuid": engagement_type
            },
            "validity": {
                "from": date_from,
                "to": date_to
            }
        }

        return self.set_metadata(identifier, payload)

    def add_type_role(self, identifier, org_unit_ref, type_ref, date_from, date_to=None):

        payload = {
            "type": "role",
            "org_unit": {
                "uuid": org_unit_ref
            },
            "role_type": {
                "uuid": type_ref
            },
            "validity": {
                "from": date_from,
                "to": date_to
            }
        }

        return self.set_metadata(identifier, payload)

    def add_type_manager(self, identifier, org_unit_ref, manager_type,
                         manager_level, responsabilities, date_from, date_to=None):

        if isinstance(responsabilities, str):
            responsabilities = list(responsabilities)

        responsibility = [
            dict(uuid=reference)
            for reference in responsabilities
        ]

        # TODO: add address type to manager payload
        payload = {
            "type": "manager",
            "org_unit": {
                "uuid": org_unit_ref
            },
            "manager_type": {
                "uuid": manager_type
            },
            "responsibility": responsibility,
            "manager_level": {
                "uuid": manager_level
            },
            "validity": {
                "from": date_from,
                "to": date_to
            }
        }

        return self.set_metadata(identifier, payload)

    def add_type_leave(self, identifier, leave_type_ref, date_from, date_to=None):

        payload = {
            "type": "leave",
            "leave_type": {
                "uuid": leave_type_ref
            },
            "validity": {
                "from": date_from,
                "to": date_to
            }
        }

        return self.set_metadata(identifier, payload)

    def add_type_itsystem(self, identifier, itsystem_ref, date_from, date_to=None):

        payload = {
            "type": "it",
            "itsystem": {
                "uuid": itsystem_ref
            },
            "validity": {
                "from": date_from,
                "to": date_to
            }
        }

        return self.set_metadata(identifier, payload)
