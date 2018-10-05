# -- coding: utf-8 --

import os2mo_data_import.defaults as defaults


class BaseMap(object):
    """
    Simple key value pair (in memory) storage.
    The key is a user defined keyword however the value can be
    any type of object, thus the responsibility to extract the data
    lies at the end of the "handler".

    Example:
        {
            "Magenta": {
                "data": < data_object >
                "optional_data": < data_object >
                "misc": ...
            }
        }

    :param storage_map:
            Dictionary for "crude" storage (dict)

    """

    def __init__(self):
        self.storage_map = {}

    def get(self, identifier):
        """
        Retrieve value/data by identifier.

        :param identifier:
            User defined identifier (str)

        :return:
            Returns the data/content

        """

        return self.storage_map[identifier]

    def save(self, identifier, data):
        """
        Save key/value pair to the storage_map

        :param identifier:
            User defined identifier (str)

        :param data:
            User defined data object.

        :return:
            Returns the data/content
        """

        self.storage_map[identifier] = data

        return data

    def check_if_exists(self, identifier):
        """
        Check for the existance of an identifier
        (For debugging purposes)

        :param identifier:
            User defined identifier (str)

        :return:
            Status of whether the identifier exists in the map (bool)

        """

        if identifier not in self.storage_map:
            return False

        return True

    def export(self):
        """
        Export data as a list of tuples containing
        the identifier/data (key/value) pairs.

        :return:
            Data exported as a list of tuples for external handlers

        """

        return [
            (identifier, data)
            for identifier, data in self.storage_map.items()
        ]


class ExtendedMap(BaseMap):
    """
    Extends the BaseMap with methods to add optional data

    Example:
        {
            "Magenta": {
                "data": < data_object >
                "optional_data": < data_object >
                "misc": ...
            }
        }

    """

    def get_data(self, owner_ref):
        """
        Retrieve content from the "data" dict key

        :param owner_ref:
            Reference to the user defined identifier

        :return:
            Returns contents of the "data" dict key

        """
        return self.storage_map[owner_ref]["data"]

    def get_opt(self, owner_ref):
        """
        Retrieve content from the "optional_data" dict key

        :param owner_ref:
            Reference to the user defined identifier

        :return:
            Returns contents of the "optional_data" dict key

        """
        return self.storage_map[owner_ref]["optional_data"]

    def save_opt(self, owner_ref, data):
        """
        Update existing data object with optional content.

        :param owner_ref:
            Reference to the user defined identifier

        :param data:
            Optional user defined content

        :return:
            Returns the data content which was passed

        """

        # Identifier must already exist in the storage_map
        if not self.check_if_exists(owner_ref):
            raise ValueError(
                "There is not matching reference in the storage map"
            )

        optional_data = self.get_opt(owner_ref)

        if data in optional_data:
            raise AssertionError("Optional data already exists")

        optional_data.append(data)

        return data

    def add_type_address(self, owner_ref, address_type_ref,
                         date_from, date_to=None, value=None, uuid=None):
        """
        Address type data (optional data)

        For further information,
        please see the official mora documentation on address types:

        https://mora.readthedocs.io/en/development/api/address.html

        :param owner_ref:
            Reference to the user defined identifier

        :param address_type_ref:
            User defined reference of the facet to which the address type belongs

        :param date_from:
            Start date as string: "1900-01-01" (str)

        :param date_to:
            End date as string: "1900-01-01" (str)

        :param value:
            String value, e.g. "00112233" (str)

        :param uuid:
            UUID as string, e.g. "2F4DBD6E-5940-4081-8729-120650904FAE"
            This is used ONLY for valid DAR address objects

            # Official website: http://dawa.aws.dk/dok/api#adresse

        :return:
            List of tuples, example:
            This is abstract content exported for external handler.

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

        return self.save_opt(owner_ref, address_data)


class Facet(BaseMap):
    """
    Facet type - parent of klasse type
    In the current state of the os2mo application
    no other types than default values should be needed.

    """
    def __init__(self):
        super().__init__()

    def add(self, identifier, user_key=None):
        """
        Add new facet to the storage map.
        In the context of the os2mo application,
        a new object does only require a unique user_key.

        :param identifier:
            User defined identifier

        :param user_key:
            Optional user_key (if the key should differ from the identifier)
            If the user_key is not set, it conforms to the passed identifier

        :return:
            Returns data as dict, example:

            {
                "user_key": "Tilknytningstype"
            }

        """

        data = {
            "user_key": (user_key or identifier)
        }

        return self.save(identifier, data)

    def create_defaults(self, default=defaults.facet_types):
        """
        Default values are created if not passed,
        please see os2mo_data_import.defaults for more information.

        :return:
           Returns data as a list of tuples.

        """

        for facet_type in default:
            self.add(facet_type)

        return self.export()


class Klasse(BaseMap):
    """
    The Klasse class provides functionality for collecting
    user defined klasse meta objects for import.

    In the current state of the os2mo application
    the following two klasse objects must be created:

        {
            "user_key": "Telefon",
            "example": "20304060",
            "scope": "PHONE",
            "title": "Tlf"
        }

        {
            "user_key": "AdressePost",
            "example": "<UUID>",
            "scope": "DAR",
            "title": "Adresse"
        }

    The frontend application expects these two klasse objects to exist.
    These provide functionality for 2 required input fields.

    Note:
        The required objects are included in the list of defaults
        and are automatically created when running create_defaults().

    TODO:
        Add validation for the required types.
        Additionally check for all common types which are not created.

        The defaults should be additive and only created if the user
        has not created the required types.

    """

    default_types = {}

    def __init__(self):
        super().__init__()

    def add(self, identifier, facet_type_ref, **properties):
        """
        Add new facet to the storage map.
        In the context of the os2mo application,
        a new object does only require a unique user_key.

        :param identifier:
            User defined identifier

        :param facet_type_ref:
            User defined identifier

        :param properties:
            Optional user_key (if the key should differ from the identifier)
            If the user_key is not set, it conforms to the passed identifier

        :return:
            Returns data as dict.

        """

        data = {
            "facet_type_ref": facet_type_ref,
            "data": properties
        }

        return self.save(identifier, data)

    def create_defaults(self, default=defaults.klasse_types):
        """
        Default values are created if not passed,
        please see os2mo_data_import.defaults for more information.

        :return:
           Returns data as a list of tuples.

        """

        for identifier, facet_ref, data in default:
            self.add(identifier, facet_ref, **data)

        return self.export()


class Itsystem(BaseMap):
    """
    The Itsystem class provides functionality for collecting
    user defined itsystems for import.

    Employees can have a relation to an itsystem.

    TODO:
        Prepare for upcoming changes to "Itsystem" which will allow
        to attach a username tied to the system
        (which differs from user_key)

    """

    def __init__(self):
        super().__init__()

    def add(self, identifier, user_key=None, system_name=None):
        """
        Add new itsystem to the storage map.
        In the context of the os2mo application,
        a new object does only require a unique user_key.

        :param identifier:
            User defined identifier

        :param user_key:
            The user_key (str) functions similar to "title".
            It is displayed in the frontend application
            as the name of the it system.

        :param system_name:
            Name of the it system (str)
            (However this is currently not used)

        :return:
            Returns data as a dictionary.

        """

        data = {
            "user_key": (user_key or identifier),
            "system_name": (system_name or identifier),
        }

        return self.save(identifier, data)


class OrganisationUnit(ExtendedMap):
    """
    The Organisation Unit class provides functionality for collecting
    user defined organisation units for import.

    """

    def __init__(self):
        super().__init__()

    def add(self, identifier, date_from, date_to=None, name=None,
            user_key=None, org_unit_type_ref=None, parent_ref=None, uuid=None):
        """
        Add new organisation unit to the storage map.

        :param identifier:
            User defined identifier (str)

        :param name:
            Name of the organisation unit which should be displayed (str)

        :param date_from:
            Start date e.g. "1900-01-01" (str)

        :param date_to:
            End date, e.g. "1900-01-01" (str)

        :param user_key:
            Either user defined or imported key from source (str)
            (For internal history)

        :param org_unit_type_ref:
            Named reference to the type (klasse) of organisation (str)
            E.g. "Enhed", "Section", "Department" etc.

        :param parent_ref:
            Reference to the "name" (Not its UUID) of the parent organisation (str)

        :param uuid:
            Imported UUID from the source (str)
            (Optional: uuid is either imported or created on insert)

        :return:
            Returns data as a list of tuples

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


class Employee(ExtendedMap):
    """
    The Employee class provides functionality for collecting
    employee objects for import.

    """

    def __init__(self):
        super().__init__()

    def add(self, identifier, cpr_no, name=None, user_key=None, uuid=None):
        """
        Add new employee to the storage map.
        Employee objects have no validity,
        instead the validity is calculated from the CPR number.

        :Note:
            The CPR number does not need to be "valid" but must be formatted correct

        :param identifier:
            User defined identifier (str)

        :param cpr_no:
            10 digit CPR number

        :param name:
            Full name of the employee (str)

        :param user_key:
            Either user defined or imported key from source (str)
            (For internal history)

        :param uuid:
            Imported UUID from the source (str)
            (Optional: uuid is either imported or created on insert)

        :return:
            Returns data as a list of tuples (list)

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
            Refers to the user defined identifier when added (str)

        :param org_unit_ref:
            Refers to the user defined identifier
            of the related organisation unit (str)

        :param job_function_ref:
            Refers to the user defined identifier
            of the klasse object which holds the job function type (str)

        :param engagement_type_ref:
            Refers to the user defined identifier
            of the klasse object which holds the engagement type (str)

        :param date_from:
            Start date e.g. "1900-01-01" (str)

        :param date_to:
            End date e.g. "1900-01-01" (str)

        :return:
            Returns data as a list of tuples (list)

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

        return self.save_opt(owner_ref, engagement_data)

    def add_type_association(self, owner_ref, org_unit_ref,
                             job_function_ref, association_type_ref,
                             date_from, date_to=None, address_uuid=None):
        """

        :param owner_ref:
            Refers to the user defined identifier when added (str)

        :param org_unit_ref:
            Refers to the user defined identifier
            of the related organisation unit (str)

        :param job_function_ref:
            Refers to the user defined identifier
            of the klasse object which holds the job function type (str)

        :param association_type_ref:
            Refers to the user defined identifier
            of the klasse object which holds the association type (str)

        :param date_from:
            Start date e.g. "1900-01-01" (str)

        :param date_to:
            End date e.g. "1900-01-01" (str)

        :param address_uuid:
            UUID of the address object found in "DAR" database.
            (Must be valid or will be rejected at the insert stage)

        :return:
            Returns data as a list of tuples (list)

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
            item = ("address", address_uuid)
            association_data.append(item)

        return self.save_opt(owner_ref, association_data)

    def add_type_role(self, owner_ref, org_unit_ref, role_type_ref,
                      date_from, date_to=None):
        """

        :param owner_ref:
            Refers to the user defined identifier when added (str)

        :param org_unit_ref:
            Refers to the user defined identifier
            of the related organisation unit (str)

        :param role_type_ref:
            Refers to the user defined identifier
            of the klasse object which holds the job function type (str)

        :param date_from:
            Start date e.g. "1900-01-01" (str)

        :param date_to:
            End date e.g. "1900-01-01" (str)

        :return:
            Returns data as a list of tuples (list)

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

        return self.save_opt(owner_ref, role_data)

    def add_type_manager(self, owner_ref, org_unit_ref, manager_type_ref,
                         manager_level_ref, responsibility_list, date_from,
                         date_to=None, address_uuid=None):
        """

        :param owner_ref:
            Refers to the user defined identifier when added (str)

        :param org_unit_ref:
            Refers to the user defined identifier
            of the related organisation unit (str)

        :param manager_type_ref:
            Refers to the user defined identifier
            of the klasse object which holds the manager type (str)

        :param manager_level_ref:
            Refers to the user defined identifier
            of the klasse object which holds the manager level type (str)

        :param address_uuid:
            UUID of the address object found in "DAR" database.
            (Must be valid or will be rejected at the insert stage)

        :param responsibility_list:
            List of references to user defined identifier
            of responsability klasse type (str)

            E.g. ["responsability1", "responsability2", "responsability3"]

        :param date_from:
            Start date e.g. "1900-01-01" (str)

        :param date_to:
            End date e.g. "1900-01-01" (str)

        :return:
            Returns data as a list of tuples (list)

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
            item = ("address", address_uuid)
            manager_data.append(item)

        return self.save_opt(owner_ref, manager_data)

    def add_type_leave(self, owner_ref, leave_type_ref,
                       date_from, date_to=None):
        """

        :param owner_ref:
            Refers to the user defined identifier when added (str)

        :param leave_type_ref:
            Refers to the user defined identifier
            of the klasse object which holds the leave type (str)

        :param date_from:
            Start date e.g. "1900-01-01" (str)

        :param date_to:
            End date e.g. "1900-01-01" (str)

        :return:
            Returns data as a list of tuples (list)

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

        return self.save_opt(owner_ref, leave_data)

    def add_type_itsystem(self, owner_ref, itsystem_ref,
                          date_from, date_to=None):
        """

        :param owner_ref:
            Refers to the user defined identifier when added (str)

        :param itsystem_ref:
            Refers to the user defined identifier
            of the klasse object which holds the leave type (str)

        :param date_from:
            Start date e.g. "1900-01-01" (str)

        :param date_to:
            End date e.g. "1900-01-01" (str)

        :return:
            Returns data as a list of tuples (list)

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

        return self.save_opt(owner_ref, it_data)


class Organisation(object):
    """
    The Organisation class functions as a wrapper for all the sub classes.
    It also provides similar functionalitiy for importing/creating
    the parent organisation.

    Organisation
     \
      - Facet
      - Klasse
      - Itsystem
      - Organisation Unit
      - Employee

    TODO:
        Add functionality to import / inherit UUID's for existing data
        in order to use this utility for additive purposes.

        (Currently only import "from scratch" is supported)

    :param name:
    :param user_key:
    :param municipality_code:
        3-digit municipality code (str)
        In the current context the actual value is not in use.

    :param uuid:
        Imported UUID from the source (str)
        (Optional: uuid is either imported or created on insert)

    :param date_from:
        Start date e.g. "1900-01-01" (str)

    :param date_to:
        End date e.g. "1900-01-01" (str)

    :param create_defaults:
        Create default facet and klasse types (bool)

    """

    def __init__(self, name, user_key=None, municipality_code=999,
                 uuid=None, date_from=None, date_to=None,
                 create_defaults=True):

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
