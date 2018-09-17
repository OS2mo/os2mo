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

        # Use existing uuid when overwriting
        if identifier in self.storage_map:
            import_uuid = self.get_uuid(identifier)
        else:
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

    def __init__(self, parent_org):
        self.parent_org = parent_org
        self.storage_map = {}

    def add(self, identifier):

        data = self.build_payload(
            bvn=identifier,
            parent_org=self.parent_org
        )

        return self.save(identifier, data)

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


class Klasse(MemoryMap):

    def __init__(self, parent_org):
        self.parent_org = parent_org
        self.storage_map = {}

    def add(self, identifier, **kwargs):

        data = self.build_payload(
            user_key=identifier, 
            **kwargs
        )

        return self.save(identifier, data)

    def build_payload(self, user_key, facet_ref,
                      from_date=None, to_date=None, **properties):

        klasse_properties = {
            "brugervendtnoegle": user_key,
            "virkning": create_period_of_action(from_date, to_date)
        }

        if properties:
            klasse_properties.update(properties)

        attributter = {
            "klasseegenskaber": [
                klasse_properties
            ]
        }

        relationer = {
            "ansvarlig": [
                {
                    "objekttype": "organisation",
                    "uuid": self.parent_org,
                    "virkning": create_period_of_action(from_date, to_date)
                }
            ],
            "facet": [
                {
                    "objekttype": "facet",
                    "uuid": facet_ref,
                    "virkning": create_period_of_action(from_date, to_date)
                }
            ]
        }

        tilstande = {
            "klassepubliceret": [
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


class Organisation(MemoryMap):

    def __init__(self):
        self.parent_org = parent_org
        self.storage_map = {}

    def add(self, identifier, org_name=None, municipality_code=999,
            date_from=None, date_to=None):

        if not org_name:
            org_name = identifier

        data = self.build_payload(
            bvn=identifier,
            name=org_name,
            municipality_code=municipality_code,
            date_from=date_from,
            date_to=date_to
        )

        return self.save(identifier, data)

    def build_payload(self, bvn, name, municipality_code=999, date_from=None, date_to=None):
        # Inelegant conversion to string
        municipality_code = str(municipality_code)

        # Create urn value
        urn_municipality_code = "urn:dk:kommune:{}".format(municipality_code)

        attributter = {
            "organisationegenskaber": [
                {
                    "brugervendtnoegle": str(bvn),
                    "organisationsnavn": str(name),
                    "virkning": create_period_of_action(date_from, date_to)
                }
            ]
        }

        relationer = {
            "myndighed": [
                {
                    "urn": urn_municipality_code,
                    "virkning": create_period_of_action(date_from, date_to)
                }
            ]
        }

        tilstande = {
            "organisationgyldighed": [
                {
                    "gyldighed": "Aktiv",
                    "virkning": create_period_of_action(date_from, date_to)
                }
            ]
        }

        return {
            "note": "Automatisk indlæsning",
            "attributter": attributter,
            "relationer": relationer,
            "tilstande": tilstande
        }
