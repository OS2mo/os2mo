# -- coding: utf-8 --

from os2mo_data_import.adapters.base import MemoryMap

# TODO: Fix the inelegant extension of the Memory map in order to gain metadata storage
class MoBase(MemoryMap):

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

        self.storage_map[identifier]["metadata"].append(metadata)


class OrganisationUnit(MoBase):

    def __init__(self, parent_org):
        self.parent_org = parent_org

    def add(self, name, type_ref, date_from, date_to=None):

        data = {
            "name": name,
            "parent": {
                "uuid": self.parent_org
            },
            "org_unit_type": {
                "uuid": type_ref
            },
            "validity": {
                "from": date_from,
                "to": date_to
            }
        }

        return self.save(identifier=name, data=data)

    def add_address_type(self, identifier, address_data):

        if not "address_type" in address_data:
            raise RuntimeError("No address type present")


        return self.set_metadata(identifier, address_data)


class Employee(MoBase):

    def __init__(self, parent_org):
        self.parent_org = parent_org

    def add(self, name, cpr_no, date_from, date_to=None, user_key=None):

        data = {
            "name": name,
            "cpr_no": cpr_no,
            "org": {
                "uuid": self.parent_org
            },
        }

        # Add user key to the data payload if passed
        # Default is auto generated UUID
        if user_key:
            data.update({
                "user_key": user_key
            })

        return self.save(identifier=name, data=data)
