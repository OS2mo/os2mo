# -- coding: utf-8 --

from uuid import uuid4


class Utility:

    def create_uuid(self):
        """
        Generates a UUID (version 4)
        Helper function

        :return:    UUID
        :rtype:     str
        """

        identifier = uuid4()
        return str(identifier)


class MemoryMap(Utility):
    """
    MemoryMap
    """

    def __init__(self):
        self.storage_map = {}

    def get(self, identifier):
        """

        :param identifier:
        :return:
        """

        return self.storage_map[identifier]

    def save(self, identifier, data):
        """

        :param identifier:
        :param data:
        :return:
        """

        self.storage_map[identifier] = data

        return identifier

    def check_if_exists(self, identifier):
        """
        Check for the existance of an identifier
        (For debugging purposes)

        :param identifier:  User defined identifier (Type: str)
        :return:            bool
        """

        if identifier not in self.storage_map:
            return None

        return True

    def export(self):
        """

        :return:
        """

        return [
            (identifier, data)
            for identifier, data in self.storage_map.items()
        ]


class Facet(MemoryMap):
    """
    Facet
    """

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
        super().__init__()

    def add(self, identifier, user_key=None):
        """

        :param identifier:
        :param user_key:
        :return:
        """

        data = {
            "brugervendtnoegle": (user_key or identifier)
        }

        return self.save(identifier, data)

    def create_defaults(self):
        """

        :return:
        """

        for facet_type in self.defaul_types:
            self.add(facet_type)

        return self.export()


class Klasse(MemoryMap):
    """
    Klasse
    """

    default_types = {
        "Enhed": {
            "facet_type_ref": "Enhedstype",
            "data": {
                "brugervendtnoegle": "Enhed",
                "beskrivelse": "Dette er en organisationsenhed",
                "titel": "Enhed"
            }
        },
        "AdressePost": {
            "facet_type_ref": "Adressetype",
            "data": {
                "brugervendtnoegle": "AdressePost",
                "eksempel": "<UUID>",
                "omfang": "DAR",
                "titel": "Adresse"
            }
        },
        "Email": {
            "facet_type_ref": "Adressetype",
            "data": {
                "brugervendtnoegle": "Email",
                "eksempel": "test@example.com",
                "omfang": "EMAIL",
                "titel": "Emailadresse"
            }
        },
        "Telefon": {
            "facet_type_ref": "Adressetype",
            "data": {
                "brugervendtnoegle": "Telefon",
                "eksempel": "20304060",
                "omfang": "PHONE",
                "titel": "Telefonnummer"
            }
        },
        "Webadresse": {
            "facet_type_ref": "Adressetype",
            "data": {
                "brugervendtnoegle": "Webadresse",
                "eksempel": "http://www.magenta.dk",
                "omfang": "WWW",
                "titel": "Webadresse"
            }
        },
        "EAN": {
            "facet_type_ref": "Adressetype",
            "data": {
                "brugervendtnoegle": "EAN",
                "eksempel": "00112233",
                "omfang": "EAN",
                "titel": "EAN nr."
            }
        },
        "PNUMBER": {
            "facet_type_ref": "Adressetype",
            "data": {
                "brugervendtnoegle": "PNUMBER",
                "eksempel": "00112233",
                "omfang": "PNUMBER",
                "titel": "P-nr."
            }
        },
        "TEXT": {
            "facet_type_ref": "Adressetype",
            "data": {
                "brugervendtnoegle": "TEXT",
                "eksempel": "Fritekst",
                "omfang": "TEXT",
                "titel": "Fritekst"
            }
        },
        "Ansat": {
            "facet_type_ref": "Engagementstype",
            "data": {
                "brugervendtnoegle": "Ansat",
                "titel": "Ansat"
            }
        },
        "Leder": {
            "facet_type_ref": "Ledertyper",
            "data": {
                "brugervendtnoegle": "Leder",
                "titel": "Leder"
            }
        },
        "Lederansvar": {
            "facet_type_ref": "Lederansvar",
            "data": {
                "brugervendtnoegle": "Lederansvar",
                "titel": "Ansvar for organisationsenheden"
            }
        },
        "Lederniveau": {
            "facet_type_ref": "Lederniveau",
            "data": {
                "brugervendtnoegle": "Lederniveau",
                "titel": "Niveau 90",
            }
        }
    }

    def __init__(self):
        super().__init__()

    def add(self, identifier, facet_type_ref, **properties):
        """

        :param identifier:
        :param facet_type:
        :param properties:
        :return:
        """

        data = {
            "facet_type_ref": facet_type_ref,
            "data": properties
        }

        return self.save(identifier, data)

    def create_defaults(self):
        """

        :return:
        """

        for identifier, data in self.default_types.items():
            self.save(identifier, data)

        return self.export()


class Itsystem(MemoryMap):
    """
    Itsystem
    """

    def __init__(self):
        super().__init__()

    def add(self, identifier, user_key=None, system_name=None):
        """

        :param identifier:
        :param user_key:
        :param system_name:
        :return:
        """

        data = {
            "user_key": (user_key or identifier),
            "system_name": (system_name or identifier),
        }

        return self.save(identifier, data)


class MoMemoryMap(MemoryMap):
    """
    MoMemoryMap
    """

    def add_type_address(self, owner_ref, address_type_ref,
                         date_from, date_to=None, value=None, uuid=None):
        """

        :param owner_ref:
        :param address_type_ref:
        :param date_from:
        :param date_to:
        :param value:
        :param uuid:
        :return:
        """

        if not value and not uuid:
            raise ValueError("Missing parameter (either value or uuid")

        validity = {
            "from": date_from,
            "to": date_to
        }

        address_data = [
            ("type", "address"),
            ("address_type", address_type_ref),
            ("validity", validity)
        ]

        # Do NOT append uuid if value is passed
        if value:
            item = ("value", value)
        else:
            item = ("uuid", uuid)

        address_data.append(item)

        return self.add_optional_data(owner_ref, address_data)

    def get_optional_data(self, owner_ref):
        """

        :param owner_ref:
        :return:
        """
        return self.storage_map[owner_ref]["optional_data"]

    def add_optional_data(self, owner_ref, data):
        """

        :param owner_ref:
        :param data:
        :return:
        """

        optional_data = self.storage_map[owner_ref]["optional_data"]

        if data in optional_data:
            raise AssertionError("Optional data exists")

        optional_data.append(data)

        return (owner_ref, data)


class OrganisationUnit(MoMemoryMap):
    """
    OrganisationUnit
    """

    def __init__(self):
        super().__init__()

    def add(self, identifier, date_from, date_to=None, name=None,
            user_key=None, org_unit_type_ref=None, parent_ref=None, uuid=None):
        """

        :param identifier:
        :param name:
        :param date_from:
        :param date_to:
        :param user_key:
        :param org_unit_type_ref:
        :param parent_ref:
        :param uuid:
        :return:
        """

        if identifier in self.storage_map:
            raise AssertionError("Organisation unit already exists")

        name = (name or identifier)

        validity = {
            "from": date_from,
            "to": date_to
        }

        organisation_unit_data = [
            ("name", name),
            ("parent", parent_ref),
            ("org_unit_type", org_unit_type_ref),
            ("validity", validity)
        ]

        # Import user_key if passed
        if user_key:
            item = ("user_key", user_key)
            organisation_unit_data.append(item)

        # Import uuid if passed
        if uuid:
            uuid = str(uuid)
            item = ("uuid", uuid)
            organisation_unit_data.append(item)

        data = {
            "parent_ref": parent_ref,
            "data": organisation_unit_data,
            "optional_data": []
        }

        return self.save(identifier, data)


class Employee(MoMemoryMap):
    """
    Employee
    """

    # TODO: add association type
    # TODO: unify meta types

    def __init__(self):
        super().__init__()

    def add(self, identifier, cpr_no, name=None, user_key=None, uuid=None):
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

        if identifier in self.storage_map:
            raise AssertionError("Employee already exists")

        name = (name or identifier)

        employee_data = [
            ("name", name),
            ("cpr_no", cpr_no),
            ("org", None),
        ]

        if user_key:
            item = ("user_key", user_key)
            employee_data.append(item)

        if uuid:
            uuid = str(uuid)
            item = ("uuid", uuid)
            employee_data.append(item)

        data = {
            "data": employee_data,
            "optional_data": []
        }

        return self.save(identifier, data)

    def add_type_engagement(self, owner_ref, org_unit_ref, job_function_ref,
                            engagement_type_ref, date_from, date_to=None):
        """

        :param owner_ref:
        :param org_unit_ref:
        :param job_function_ref:
        :param engagement_type_ref:
        :param date_from:
        :param date_to:
        :return:
        """

        validity = {
            "from": date_from,
            "to": date_to
        }

        engagement_data = [
            ("type", "engagement"),
            ("org_unit", org_unit_ref),
            ("job_function", job_function_ref),
            ("engagement_type", engagement_type_ref),
            ("validity", validity)
        ]

        return self.add_optional_data(owner_ref, engagement_data)

    def add_type_association(self, owner_ref, org_unit_ref,
                             job_function_ref, association_type_ref,
                             date_from, date_to=None, address_uuid=None):
        """

        :param owner_ref:
        :param org_unit_ref:
        :param job_function_ref:
        :param association_type_ref:
        :param date_from:
        :param date_to:
        :param address_uuid:
        :return:
        """

        validity = {
            "from": date_from,
            "to": date_to
        }

        association_data = [
            ("type", "association"),
            ("org_unit", org_unit_ref),
            ("job_function", job_function_ref),
            ("association_type", association_type_ref),
            ("validity", validity)
        ]

        if address_uuid:
            item = ("address_uuid", address_uuid)
            association_data.append(item)

        return self.add_optional_data(owner_ref, association_data)

    def add_type_role(self, owner_ref, org_unit_ref, role_type_ref,
                      date_from, date_to=None):
        """

        :param owner_ref:
        :param org_unit_ref:
        :param role_type_ref:
        :param date_from:
        :param date_to:
        :return:
        """

        validity = {
            "from": date_from,
            "to": date_to
        }

        role_data = [
            ("type", "role"),
            ("org_unit", org_unit_ref),
            ("role_type", role_type_ref),
            ("validity", validity)
        ]

        return self.add_optional_data(owner_ref, role_data)

    def add_type_manager(self, owner_ref, org_unit_ref, manager_type_ref, manager_level_ref,
                         address_uuid, responsibility_list, date_from, date_to=None):
        """

        :param owner_ref:
        :param org_unit_ref:
        :param manager_type_ref:
        :param manager_level_ref:
        :param address_uuid:
        :param responsibility_list:
        :param date_from:
        :param date_to:
        :return:
        """

        if isinstance(responsibility_list, str):
            responsibility_list = list(responsibility_list)

        validity = {
            "from": date_from,
            "to": date_to
        }

        manager_data = [
            ("type", "manager"),
            ("org_unit", org_unit_ref),
            ("manager_type", manager_type_ref),
            ("manager_level", manager_level_ref),
            ("responsibility", responsibility_list),
            ("validity", validity)
        ]

        if address_uuid:
            item = ("address_uuid", address_uuid)
            manager_data.append(item)

        return self.add_optional_data(owner_ref, manager_data)

    def add_type_leave(self, owner_ref, leave_type_ref, date_from, date_to=None):
        """

        :param owner_ref:
        :param leave_type_ref:
        :param date_from:
        :param date_to:
        :return:
        """

        validity = {
            "from": date_from,
            "to": date_to
        }

        leave_data = [
            ("type", "leave"),
            ("leave_type", leave_type_ref),
            ("validity", validity)
        ]

        return self.add_optional_data(owner_ref, leave_data)

    def add_type_itsystem(self, owner_ref, itsystem_ref,
                          date_from, date_to=None):
        """

        :param owner_ref:
        :param itsystem_ref:
        :param date_from:
        :param date_to:
        :return:
        """

        validity = {
            "from": date_from,
            "to": date_to
        }

        it_data = [
            ("type", "it"),
            ("itsystem", itsystem_ref),
            ("validity", validity)
        ]

        return self.add_optional_data(owner_ref, it_data)


class Organisation(Utility):
    """
    Organisation
    """

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

        # Exposed classes
        self.Facet = Facet()
        self.Klasse = Klasse()
        self.Itsystem = Itsystem()
        self.OrganisationUnit = OrganisationUnit()
        self.Employee = Employee()

        if create_defaults:
            self.Facet.create_defaults()
            self.Klasse.create_defaults()

    def export(self):
        """

        :return:
        """
        return {
            "uuid": self.uuid,
            "name": self.name,
            "user_key": self.user_key,
            "municipality_code": self.municipality_code,
            "validity": self.validity
        }

