# -- coding: utf-8 --

class MoxUtility:

    def create_uuid(self):
        """
        Generates a UUID (version 4)
        Helper function

        :return:    UUID
        :rtype:     str
        """

        identifier = uuid4()
        return str(identifier)

    def validity_range(self, from_date, to_date):

        if not to_date:
            to_date = "infinity"

        return {
            "from": from_date,
            "to": to_date
        }

class MemoryMap(object):

    def __init__(self):
        self.storage_map = {}

    def get(self, identifier):

        data = self.storage_map[identifier]

        if not data:
            raise RuntimeError("No data found")

        return (identifier, data)

    def save(self, identifier, data):
        self.storage_map[identifier] = data

        return self.get(identifier)

    def export(self):
        return [
            data for data in self.storage_map.values()
        ]


class Facet(MemoryMap):

    defaul_types = [
        "Tilknytningstype",
        "Funktionstype",
        "Lederansvar",
        "Lederniveau",
        "Brugertype",
        "Engagementstype",
        "Enhedstype",
        "Ledertyper",
        "Orlovstype",
        "Myndighedstype",
        "Rolletype",
        "Stillingsbetegnelse",
        "Adressetype"
    ]

    def __init__(self):
        self.storage_map = {}

    def add(self, identifier, user_key=None):

        data = {
            "brugervendtnoegle": (user_key or identifier)
        }

        return self.save(identifier, data)

    def create_defaults(self):

        for facet_type in self.defaul_types:
            self.add(facet_type)

        return self.export()


class Klasse(MemoryMap):

    default_types = [
        {
            "brugervendtnoegle": "Enhed",
            "beskrivelse": "Dette er en organisationsenhed",
            "titel": "Enhed",
            "facet_type": "Enhedstype"
        },
        {
            "brugervendtnoegle": "AdressePost",
            "eksempel": "<UUID>",
            "omfang": "DAR",
            "titel": "Adresse",
            "facet_type": "Adressetype"
        },
        {
            "brugervendtnoegle": "Email",
            "eksempel": "test@example.com",
            "omfang": "EMAIL",
            "titel": "Emailadresse",
            "facet_type": "Adressetype",
        },
        {
            "brugervendtnoegle": "Telefon",
            "eksempel": "20304060",
            "omfang": "PHONE",
            "titel": "Telefonnummer",
            "facet_type": "Adressetype",
        },
        {
            "brugervendtnoegle": "Webadresse",
            "eksempel": "http://www.magenta.dk",
            "omfang": "WWW",
            "titel": "Webadresse",
            "facet_type": "Adressetype",
        },
        {
            "brugervendtnoegle": "EAN",
            "eksempel": "00112233",
            "omfang": "EAN",
            "titel": "EAN nr.",
            "facet_type": "Adressetype",
        },
        {
            "brugervendtnoegle": "PNUMBER",
            "eksempel": "00112233",
            "omfang": "PNUMBER",
            "titel": "P-nr.",
            "facet_type": "Adressetype",
        },
        {
            "brugervendtnoegle": "TEXT",
            "eksempel": "Fritekst",
            "omfang": "TEXT",
            "titel": "Fritekst",
            "facet_type": "Adressetype",
        },
        {
            "brugervendtnoegle": "Ansat",
            "facet_type": "Engagementstype"
        },
        {
            "brugervendtnoegle": "Leder",
            "titel": "Leder",
            "facet_type": "Ledertyper",
        },
        {
            "brugervendtnoegle": "Lederansvar",
            "titel": "Ansvar for organisationsenheden",
            "facet_type": "Lederansvar",
        },
        {
            "brugervendtnoegle": "Lederniveau",
            "titel": "Niveau 90",
            "facet_type": "Lederniveau",
        },
    ]

    def __init__(self):
        self.storage_map = {}

    def add(self, identifier, facet_type, **properties):

        data = {
            "brugervendtnoegle": identifier,
            "facet_type": facet_type
        }

        # Merge data with passed properties
        data.update(properties)

        return self.save(identifier, data)

    def create_defaults(self):

        for klasse in self.default_types:
            identifier = klasse.get("brugervendtnoegle")
            facet_type = klasse.pop("facet_type")
            self.add(identifier, facet_type, **klasse)

        return self.export()


class MoMemoryMap(MemoryMap):

    def add(self, identifier, date_from, date_to=None,
            name=None, type_ref=None, parent_ref=None, user_key=None, **kwargs):
        """

        :param identifier:
        :param type_ref:
        :param date_from:
        :param date_to:
        :param name:
        :param parent_ref:
        :param user_key:
        :param additional:
        :return:
        """

        data = {
            "name": (name or identifier),
            "user_key": user_key,
            "type_ref": type_ref,
            "parent_ref": parent_ref,
            "validity": (date_from, date_to),
            "optional_data": []
        }

        # Merge additional kwargs
        data.update(kwargs)

        return self.save(identifier, data)

    def create_address(self, value, type_ref,
                       date_from, date_to=None, value_as_uuid=False):

        address = {
            "type": "address",
            "value": value,
            "address_ref": type_ref,
            "validity": {
                "from": date_from,
                "to": date_to
            }
        }

        return address

    def add_type_address(self, identifier, **kwargs):

        address = self.create_address(**kwargs)

        return self.add_optional_data(identifier, address)

    def get_optional_data(self, identifier):
        return self.storage_map[identifier]["optional_data"]

    def add_optional_data(self, identifier, data):

        optional_data = self.storage_map[identifier]["optional_data"]

        if data in optional_data:
            print("ALLREADY EXISTS")
            return None

        optional_data.append(data)

        return (identifier, data)


class OrganisationUnit(MoMemoryMap):

    def __init__(self):
        self.storage_map = {}


class Employee(MoMemoryMap):

    # TODO: add association type
    # TODO: unify meta types

    def __init__(self):
        self.storage_map = {}

    def add_type_engagement(self, identifier, org_unit_ref, job_function_ref,
                            engagement_type_ref, date_from, date_to=None):

        data = {
            "type": "engagement",
            "org_unit_ref": org_unit_ref,
            "job_function_ref": job_function_ref,
            "engagement_type_ref": engagement_type_ref,
            "validity": {
                "from": date_from,
                "to": date_to
            }
        }

        return self.add_optional_data(identifier, data)

    def add_type_role(self, identifier, org_unit_ref, role_type_ref, date_from, date_to=None):

        payload = {
            "type": "role",
            "org_unit_ref": org_unit_ref,
            "role_type_ref": role_type_ref,
            "validity": {
                "from": date_from,
                "to": date_to
            }
        }

        return self.add_optional_data(identifier, payload)

    def add_type_manager(self, identifier, org_unit_ref, manager_type_ref, manager_level_ref,
                         address_uuid, responsabilities, date_from, date_to=None):

        if isinstance(responsabilities, str):
            responsabilities = list(responsabilities)

        # TODO: add address type to manager payload
        payload = {
            "type": "manager",
            "org_unit_ref": org_unit_ref,
            "manager_type_ref": manager_type_ref,
            "responsibility": responsabilities,
            "manager_level_ref": manager_level_ref,
            "address_uuid": address_uuid,
            "validity": {
                "from": date_from,
                "to": date_to
            }
        }

        return self.add_optional_data(identifier, payload)

    def add_type_leave(self, identifier, leave_type_ref, date_from, date_to=None):

        payload = {
            "type": "leave",
            "leave_type_ref": leave_type_ref,
            "validity": {
                "from": date_from,
                "to": date_to
            }
        }

        return self.add_optional_data(identifier, payload)

    def add_type_itsystem(self, identifier, itsystem_ref, date_from, date_to=None):

        payload = {
            "type": "it",
            "itsystem_ref": itsystem_ref,
            "validity": {
                "from": date_from,
                "to": date_to
            }
        }

        return self.add_optional_data(identifier, payload)


class Organisation(object):

    def __init__(self, name, user_key=None, municipality_code=999,
                uuid=None, date_from=None, date_to=None, create_defaults=True):

        self.uuid = uuid
        self.name = name
        self.user_key = user_key
        self.municipality_code = municipality_code

        self.validity = {
            "from": (date_from or "1900-01-01"),
            "to": (date_to or "infinity")
        }

        self.Facet = Facet()
        self.Klasse = Klasse()
        self.OrganisationUnit = OrganisationUnit()
        self.Employee = Employee()

        if create_defaults:
            self.Facet.create_defaults()
            self.Klasse.create_defaults()

    def export(self):
        return (self.uuid, self.name, self.user_key, self.municipality_code, self.validity)
