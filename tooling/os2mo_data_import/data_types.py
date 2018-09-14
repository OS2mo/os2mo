# -- coding: utf-8 --

from uuid import uuid4


def create_uuid():
    """
    Generates a UUID (version 4)
    Helper function

    :return:    UUID
    :rtype:     str
    """

    identifier = uuid4()
    return str(identifier)


def create_period_of_action(from_date, to_date):
    if not from_date:
        from_date = "1900-01-01"

    if not to_date:
        to_date = "infinity"

    return {
        "from": from_date,
        "to": to_date
    }

class MemoryMap:
    """
    In memory store
    """

    parent_org = None
    storage_map = {}

    def set_parent_org(self, parent_org):
        self.parent_org = parent_org

    def get_uuid(self, identifier):
        """
        Get UUID by identifier

        :param identifier:  User defined identifier

        :return:            UUID
        """
        item = self.storage_map[identifier]
        return item["uuid"]

    def get_data(self, identifier):
        """
        Get data by identifier

        :param identifier:  User defined identifier

        :return:            Data set as stored
        """
        item = self.storage_map[identifier]
        return item["data"]

    def get_available(self):
        """
        Show available identifiers/uuids

        :return:
        """
        return {
            key: val["uuid"]
            for key, val in self.storage_map.items()
        }

    def save(self, identifier, data):
        """
        Save data type in memory only

        :param identifier:  User defined identifier
        :param data:        Data payload (Type: dict)
        :return:            Created UUID
        """

        if not isinstance(data, dict):
            raise TypeError("Data must be of type dict")

        import_uuid = create_uuid()

        self.storage_map[identifier] = {
            "uuid": import_uuid,
            "data": data
        }

        return import_uuid

    def db_export(self):
        """
        Export list of tuples containing UUID and data
        Example:

            ("77b49f9b-166e-4c07-8a47-598b99cdee04", { <payload> })

        :return:    Database payload
        :rtype:     tuple
        """

        return [
            (item["uuid"], item["data"])
            for item in self.storage_map.values()
        ]


class Facet(MemoryMap):

    def __init__(self, org_uuid):
        self.org_uuid = org_uuid

    def add(self, type_name, **kwargs):

        data = self.build_payload(
            bvn=type_name,
            parent_org=self.org_uuid
        )

        return self.save(type_name, data)

    def build_payload(self, bvn, parent_org, from_date=None, to_date=None):

        default_type = "organisation"
        default_tilhoerer = "klassifikation"

        # Build payload
        attributter = {
            "facetegenskaber": [
                {
                    "brugervendtnoegle": str(bvn),
                    "virkning": create_period_of_action(from_date, to_date)
                }
            ]
        }

        relationer = {
            "ansvarlig": [
                {
                    "objekttype": default_type,
                    "uuid": parent_org,
                    "virkning": create_period_of_action(from_date, to_date)
                }
            ],
            "facettilhoerer": [
                {
                    "objekttype": default_tilhoerer,
                    "virkning": create_period_of_action(from_date, to_date)
                }
            ]
        }

        tilstande = {
            "facetpubliceret": [
                {
                    "publiceret": "Publiceret",
                    "virkning": create_period_of_action(from_date, to_date)
                }
            ]
        }

        return {
            "attributter": attributter,
            "relationer": relationer,
            "tilstande": tilstande
        }
