# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
#
# SPDX-License-Identifier: MPL-2.0
from __future__ import annotations

import asyncio
import copy
import datetime
import json
import re
import string
from typing import Any
from typing import Dict
from uuid import uuid4

import structlog
from fastramqpi.context import Context
from jinja2 import Environment
from jinja2 import Undefined
from ldap3.utils.ciDict import CaseInsensitiveDict
from ramodels.mo.organisation_unit import OrganisationUnit

from .exceptions import CprNoNotFound
from .exceptions import IncorrectMapping
from .exceptions import NoObjectsReturnedException
from .exceptions import NotSupportedException
from .exceptions import UUIDNotFoundException
from .ldap_classes import LdapObject
from .utils import delete_keys_from_dict
from .utils import import_class


def read_mapping_json(filename: str) -> Any:
    with open(filename, "r") as file:
        data = "\n".join(file.readlines())
        data = re.sub("//[^\n]*", "", data)
        return json.loads(data)


def find_cpr_field(mapping):
    """
    Get the field which contains the CPR number in LDAP
    """
    logger = structlog.get_logger()
    mo_to_ldap = mapping["mo_to_ldap"]
    try:
        employee_mapping = mo_to_ldap["Employee"]
    except KeyError:
        raise IncorrectMapping("Missing 'Employee' in mapping 'mo_to_ldap'")

    # See if we can find a match for this search field/result
    search_result = "123"
    search_field = "cpr_no"

    mo_dict = {search_field: search_result}
    cpr_field = None
    for ldap_field_name, template in employee_mapping.items():
        value = template.render({"mo_employee": mo_dict}).strip()

        if value == search_result:
            cpr_field = ldap_field_name
            logger.info(f"Found CPR field in LDAP: '{cpr_field}'")
            break

    if cpr_field is None:
        raise CprNoNotFound("CPR field not found")

    return cpr_field


class LdapConverter:
    def __init__(self, context: Context):

        self.logger = structlog.get_logger()

        self.context = context
        self.user_context = context["user_context"]
        self.settings = self.user_context["settings"]
        self.raw_mapping = self.user_context["mapping"]
        self.dataloader = self.user_context["dataloader"]

        # Note: If new address types or IT systems are added to MO, this class needs
        # to be re-initialized
        self.address_type_info = self.dataloader.load_mo_address_types()
        self.it_system_info = self.dataloader.load_mo_it_systems()

        self.org_unit_info = self.dataloader.load_mo_org_units()
        self.org_unit_type_info = self.dataloader.load_mo_org_unit_types()
        self.org_unit_level_info = self.dataloader.load_mo_org_unit_levels()

        self.engagement_type_info = self.dataloader.load_mo_engagement_types()
        self.job_function_info = self.dataloader.load_mo_job_functions()

        self.mo_address_types = [a["name"] for a in self.address_type_info.values()]
        self.mo_it_systems = [a["name"] for a in self.it_system_info.values()]

        self.overview = self.dataloader.load_ldap_overview()
        self.username_generator = self.user_context["username_generator"]

        self.org_unit_path_string_separator = "->"

        # Set this to an empty string if we do not need to know which org units
        # were imported by this program. For now this is useful to know because
        # we do not import details such as the org-unit level and the type.
        self.imported_org_unit_tag = "IMPORTED FROM LDAP: "

        self.default_org_unit_type_uuid = self.get_org_unit_type_uuid(
            self.settings.default_org_unit_type
        )
        self.default_org_unit_level_uuid = self.get_org_unit_level_uuid(
            self.settings.default_org_unit_level
        )

        mapping = delete_keys_from_dict(
            copy.deepcopy(self.raw_mapping), ["objectClass"]
        )

        environment = Environment(undefined=Undefined)
        environment.filters["splitfirst"] = LdapConverter.filter_splitfirst
        environment.filters["splitlast"] = LdapConverter.filter_splitlast
        environment.filters["mo_datestring"] = LdapConverter.filter_mo_datestring
        environment.filters["strip_non_digits"] = LdapConverter.filter_strip_non_digits
        self.mapping = self._populate_mapping_with_templates(
            mapping,
            environment,
        )

        self.check_mapping()
        self.cpr_field = find_cpr_field(self.mapping)

    def find_object_class(self, json_key, conversion):
        mapping = self.raw_mapping[conversion]
        if json_key not in mapping.keys():
            raise IncorrectMapping(f"{json_key} not found in {conversion} json dict")
        else:
            return mapping[json_key]["objectClass"]

    def find_ldap_object_class(self, json_key):
        return self.find_object_class(json_key, "mo_to_ldap")

    def find_mo_object_class(self, json_key):
        return self.find_object_class(json_key, "ldap_to_mo")

    def import_mo_object_class(self, json_key):
        return import_class(self.find_mo_object_class(json_key))

    def get_ldap_attributes(self, json_key):
        return list(self.mapping["mo_to_ldap"][json_key].keys())

    def get_mo_attributes(self, json_key):
        return list(self.mapping["ldap_to_mo"][json_key].keys())

    def check_attributes(self, detected_attributes, accepted_attributes):
        for attribute in detected_attributes:
            if attribute not in accepted_attributes:
                raise IncorrectMapping(
                    (
                        f"attribute '{attribute}' not allowed."
                        f" Allowed attributes are {accepted_attributes}"
                    )
                )

    def get_json_keys(self, conversion):
        try:
            return list(self.mapping[conversion].keys())
        except KeyError:
            raise IncorrectMapping(f"Missing key: '{conversion}'")

    def get_ldap_to_mo_json_keys(self):
        return self.get_json_keys("ldap_to_mo")

    def get_mo_to_ldap_json_keys(self):
        return self.get_json_keys("mo_to_ldap")

    def get_accepted_json_keys(self) -> list[str]:
        accepted_json_keys = (
            ["Employee", "Engagement"] + self.mo_address_types + self.mo_it_systems
        )

        return accepted_json_keys

    def cross_check_keys(self):
        mo_to_ldap_json_keys = self.get_mo_to_ldap_json_keys()
        ldap_to_mo_json_keys = self.get_ldap_to_mo_json_keys()

        # Check that all mo_to_ldap keys are also in ldap_to_mo
        for json_key in mo_to_ldap_json_keys:
            if json_key not in ldap_to_mo_json_keys:
                raise IncorrectMapping(f"Missing key in 'ldap_to_mo': '{json_key}'")

        # Check that all ldap_to_mo keys are also in mo_to_ldap
        for json_key in ldap_to_mo_json_keys:
            if json_key not in mo_to_ldap_json_keys:
                raise IncorrectMapping(f"Missing key in 'mo_to_ldap': '{json_key}'")

    def check_key_validity(self):
        mo_to_ldap_json_keys = self.get_mo_to_ldap_json_keys()
        ldap_to_mo_json_keys = self.get_ldap_to_mo_json_keys()

        json_keys = list(set(mo_to_ldap_json_keys + ldap_to_mo_json_keys))
        accepted_json_keys = self.get_accepted_json_keys()

        self.logger.info(f"[json check] Accepted keys: {accepted_json_keys}")
        self.logger.info(f"[json check] Detected keys: {json_keys}")

        for key in json_keys:
            if key not in accepted_json_keys:
                raise IncorrectMapping(
                    (
                        f"'{key}' is not a valid key. "
                        f"Accepted keys are {accepted_json_keys}"
                    )
                )
        self.logger.info("[json check] Keys OK")

    def check_for_objectClass(self):
        for conversion in ["mo_to_ldap", "ldap_to_mo"]:
            for json_key in self.get_json_keys(conversion):
                if "objectClass" not in list(
                    self.raw_mapping[conversion][json_key].keys()
                ):
                    raise IncorrectMapping(
                        (
                            "'objectClass' key not present in"
                            f" ['{conversion}']['{json_key}'] json dict"
                        )
                    )

    def get_required_attributes(self, mo_class):
        if "required" in mo_class.schema().keys():
            required_attributes = mo_class.schema()["required"]
        else:
            required_attributes = []

        return required_attributes

    def check_mo_attributes(self):

        ldap_to_mo_json_keys = self.get_ldap_to_mo_json_keys()
        for json_key in ldap_to_mo_json_keys:
            self.logger.info(f"[json check] checking ldap_to_mo[{json_key}]")

            mo_class = self.import_mo_object_class(json_key)

            accepted_attributes = list(mo_class.schema()["properties"].keys())
            detected_attributes = self.get_mo_attributes(json_key)
            self.check_attributes(detected_attributes, accepted_attributes)
            required_attributes = self.get_required_attributes(mo_class)

            # Person uuid is always set automatically and should not be in the template
            if "person" in required_attributes:
                required_attributes.remove("person")
            for attribute in required_attributes:
                if attribute not in detected_attributes:
                    raise IncorrectMapping(
                        (
                            f"attribute '{attribute}' is mandatory. "
                            f"The following attributes are mandatory: "
                            f"{required_attributes}"
                        )
                    )

    def check_ldap_attributes(self):
        mo_to_ldap_json_keys = self.get_mo_to_ldap_json_keys()

        cpr_field = find_cpr_field(self.mapping)
        for json_key in mo_to_ldap_json_keys:
            self.logger.info(f"[json check] checking mo_to_ldap['{json_key}']")

            object_class = self.find_ldap_object_class(json_key)

            accepted_attributes = self.overview[object_class]["attributes"]
            detected_attributes = self.get_ldap_attributes(json_key)
            self.check_attributes(detected_attributes, accepted_attributes)

            detected_single_value_attributes = [
                a for a in detected_attributes if self.dataloader.single_value[a]
            ]

            # Check that the CPR field is present. Otherwise we do not know who an
            # Address/Employee/... belongs to.
            if cpr_field not in detected_attributes:
                raise IncorrectMapping(
                    f"'{cpr_field}' attribute not present in mo_to_ldap['{json_key}']"
                )

            # Check single value fields which map to MO address/it-user/... objects.
            # We like fields which map to these MO objects to be multi-value fields,
            # to avoid data being overwritten if two objects of the same type are
            # added in MO
            if json_key in self.mo_address_types:
                fields_to_check = ["mo_address.value"]
            elif json_key in self.mo_it_systems:
                fields_to_check = ["mo_it_user.user_key"]
            elif json_key == "Engagement":
                fields_to_check = [
                    "mo_engagement.user_key",
                    "mo_engagement.org_unit.uuid",
                    "mo_engagement.engagement_type.uuid",
                    "mo_engagement.job_function.uuid",
                ]
            else:
                fields_to_check = []

            for attribute in detected_single_value_attributes:
                template = self.raw_mapping["mo_to_ldap"][json_key][attribute]
                for field_to_check in fields_to_check:
                    if field_to_check in template:
                        self.logger.warning(
                            (
                                f"[json check] {object_class}['{attribute}'] LDAP "
                                "attribute cannot contain multiple values. "
                                "Values in LDAP will be overwritten if "
                                f"multiple objects of the '{json_key}' type are "
                                "added in MO."
                            )
                        )

            # Make sure that all attributes are single-value or multi-value. Not a mix.
            if len(fields_to_check) > 1:
                matching_attributes = []
                for field_to_check in fields_to_check:
                    for attribute in detected_attributes:
                        template = self.raw_mapping["mo_to_ldap"][json_key][attribute]
                        if field_to_check in template:
                            matching_attributes.append(attribute)
                            break

                if len(matching_attributes) != len(fields_to_check):
                    raise IncorrectMapping(
                        (
                            "Could not find all attributes belonging to "
                            f"{fields_to_check}. Only found the following "
                            f"attributes: {matching_attributes}."
                        )
                    )

                matching_single_value_attributes = [
                    a
                    for a in matching_attributes
                    if a in detected_single_value_attributes
                ]
                matching_multi_value_attributes = [
                    a
                    for a in matching_attributes
                    if a not in detected_single_value_attributes
                ]

                if len(matching_single_value_attributes) not in [
                    0,
                    len(fields_to_check),
                ]:
                    raise IncorrectMapping(
                        (
                            f"LDAP Attributes mapping to '{json_key}' are a mix "
                            "of multi- and single-value. The following attributes are "
                            f"single-value: {matching_single_value_attributes} "
                            "while the following are multi-value attributes: "
                            f"{matching_multi_value_attributes}"
                        )
                    )

    def check_dar_scope(self):
        self.logger.info("[json check] checking DAR scope")
        ldap_to_mo_json_keys = self.get_ldap_to_mo_json_keys()

        for json_key in ldap_to_mo_json_keys:
            mo_class = self.find_mo_object_class(json_key)
            if ".Address" in mo_class:
                uuid = self.get_object_uuid_from_name(self.address_type_info, json_key)
                if self.address_type_info[uuid]["scope"] == "DAR":
                    raise IncorrectMapping(
                        f"'{json_key}' maps to an address with scope = 'DAR'"
                    )

    def check_ldap_to_mo_references(self):

        # https://ff1959.wordpress.com/2012/03/04/characters-that-are-permitted-in-
        # attribute-names-descriptors/
        # The only characters that are permitted in attribute names are ALPHA, DIGIT,
        # and HYPHEN (‘-’). Underscores ‘_’ are not permitted.
        valid_chars = string.ascii_letters + string.digits + "-"
        invalid_chars = "".join([s for s in string.punctuation if s not in valid_chars])
        invalid_chars_regex = r"[%s\s]\s*" % invalid_chars

        raw_mapping = self.raw_mapping["ldap_to_mo"]
        for json_key in self.get_ldap_to_mo_json_keys():
            object_class = self.find_ldap_object_class(json_key)
            accepted_attributes = sorted(set(self.overview[object_class]["attributes"]))
            for key, value in raw_mapping[json_key].items():
                if "ldap." in value:
                    ldap_refs = value.split("ldap.")[1:]

                    for ldap_ref in ldap_refs:
                        ldap_attribute = re.split(invalid_chars_regex, ldap_ref)[0]

                        if ldap_attribute not in accepted_attributes:
                            accepted_attributes_string = "\n".join(accepted_attributes)
                            raise IncorrectMapping(
                                (
                                    f"Non existing attribute detected in "
                                    f"ldap_to_mo['{json_key}']['{key}']: "
                                    f"'ldap.{ldap_ref}...'. "
                                    f"'{ldap_attribute}' attribute not found in LDAP. "
                                    f"Accepted attributes for '{object_class}' are:\n"
                                    f"{accepted_attributes_string}"
                                )
                            )

    def check_mapping(self):
        self.logger.info("[json check] Checking json file")

        # Check that all mo_to_ldap keys are also in ldap_to_mo
        # Check that all ldap_to_mo keys are also in mo_to_ldap
        self.cross_check_keys()

        # Check to make sure that all keys are valid
        self.check_key_validity()

        # Check that the 'objectClass' key is always present
        self.check_for_objectClass()

        # check that the MO address attributes match the specified class
        self.check_mo_attributes()

        # check that the LDAP attributes match what is available in LDAP
        self.check_ldap_attributes()

        # Check that keys which map to ramodels.mo.details.address.Address have scope
        # Which is NOT equal to 'DAR'. DAR fields can still be present in MO. They can
        # just not be synchronized by this app.

        # DAR adresses are not accepted for two reasons:
        #   - DAR does not exist in greenland
        #   - The DAR UUID is not present in LDAP. And LDAP cannot guarantee that an
        #     address is in the same format as DAR expects it to be.
        self.check_dar_scope()

        # Check that fields referred to in ldap_to_mo actually exist in LDAP
        self.check_ldap_to_mo_references()

        self.logger.info("[json check] Attributes OK")

    @staticmethod
    def filter_splitfirst(text):
        """
        Splits a string at the first space, returning two elements
        This is convenient for splitting a name into a givenName and a surname
        and works for names with no spaces (surname will then be empty)
        """
        if text is not None:
            text = str(text)
            if text != "":
                s = text.split(" ", 1)
                return s if len(s) > 1 else (s + [""])
        return ["", ""]

    @staticmethod
    def nonejoin(*args):
        """
        Joins items together if they are not None or emtpy lists
        """
        items_to_join = [a for a in args if a]
        return ", ".join(items_to_join)

    def get_object_name_from_uuid(self, info_dict: dict, uuid: str, name_key="name"):
        return info_dict[str(uuid)][name_key]

    def get_object_uuid_from_name(self, info_dict: dict, name: str, name_key="name"):
        names = [info[name_key] for info in info_dict.values()]
        if name not in names:
            raise UUIDNotFoundException(f"'{name}' not found in '{info_dict}'")
        elif len(set(names)) != len(names):
            raise UUIDNotFoundException(
                f"Duplicate values with key='{name_key}' found in {info_dict}"
            )

        for info in info_dict.values():
            if info[name_key] == name:
                return info["uuid"]

    def get_address_type_uuid(self, address_type: str):
        return self.get_object_uuid_from_name(self.address_type_info, address_type)

    def get_it_system_uuid(self, it_system: str):
        return self.get_object_uuid_from_name(self.it_system_info, it_system)

    def get_job_function_uuid(self, job_function: str):
        return self.get_object_uuid_from_name(self.job_function_info, job_function)

    def get_engagement_type_uuid(self, engagement_type: str):
        return self.get_object_uuid_from_name(
            self.engagement_type_info, engagement_type
        )

    def get_org_unit_type_uuid(self, org_unit_type: str):
        return self.get_object_uuid_from_name(self.org_unit_type_info, org_unit_type)

    def get_org_unit_level_uuid(self, org_unit_level: str):
        return self.get_object_uuid_from_name(self.org_unit_level_info, org_unit_level)

    def get_it_system_name(self, uuid: str):
        return self.get_object_name_from_uuid(self.it_system_info, uuid)

    def get_engagement_type_name(self, uuid: str):
        return self.get_object_name_from_uuid(self.engagement_type_info, uuid)

    def get_job_function_name(self, uuid: str):
        return self.get_object_name_from_uuid(self.job_function_info, uuid)

    def create_org_unit(self, org_unit_path_string: str):
        """
        Create the parent org. in the hierarchy (if it does not exist),
        then create the next one and keep doing that
        until we've reached the final child.
        """

        org_unit_path = org_unit_path_string.split(self.org_unit_path_string_separator)

        for nesting_level in range(len(org_unit_path)):
            partial_path = org_unit_path[: nesting_level + 1]
            partial_path_string = self.org_unit_path_string_separator.join(partial_path)

            try:
                self.get_org_unit_uuid_from_path(partial_path_string)
            except UUIDNotFoundException:
                self.logger.info(f"Importing {partial_path_string}")

                if nesting_level == 0:
                    parent_uuid = None
                    parent = None
                else:
                    parent_path = org_unit_path[:nesting_level]
                    parent_path_string = self.org_unit_path_string_separator.join(
                        parent_path
                    )
                    parent_uuid = self.get_org_unit_uuid_from_path(parent_path_string)
                    parent = {"uuid": str(parent_uuid), "name": parent_path[-1]}

                uuid = uuid4()
                name = partial_path[-1]

                org_unit = OrganisationUnit.from_simplified_fields(
                    user_key=str(uuid4()),
                    name=self.imported_org_unit_tag + name,
                    org_unit_type_uuid=self.default_org_unit_type_uuid,
                    org_unit_level_uuid=self.default_org_unit_level_uuid,
                    from_date=datetime.datetime.now().strftime("%Y-%m-%dT00:00:00"),
                    parent_uuid=parent_uuid,
                    uuid=uuid,
                )

                asyncio.gather(self.dataloader.upload_mo_objects([org_unit]))
                self.org_unit_info[str(uuid)] = {
                    "uuid": str(uuid),
                    "name": name,
                    "parent": parent,
                }

    def get_org_unit_uuid_from_path(self, org_unit_path_string: str):
        clean_org_unit_path_string = org_unit_path_string.replace(
            self.imported_org_unit_tag, ""
        )
        for info in self.org_unit_info.values():
            path_string = self.get_org_unit_path_string(info["uuid"])
            if path_string == clean_org_unit_path_string:
                return info["uuid"]
        raise UUIDNotFoundException(
            f"'{org_unit_path_string}' not found in self.org_unit_info"
        )

    def get_org_unit_path_string(self, uuid: str):
        org_unit_info = self.org_unit_info[str(uuid)]
        object_name = org_unit_info["name"]
        parent = org_unit_info["parent"]

        path_string = object_name
        while parent:
            parent_object_name = parent["name"]
            path_string = (
                parent_object_name + self.org_unit_path_string_separator + path_string
            )
            parent = self.org_unit_info[str(parent["uuid"])]["parent"]

        return path_string.replace(self.imported_org_unit_tag, "")

    def get_or_create_org_unit_uuid(self, org_unit_path_string: str):
        try:
            return self.get_org_unit_uuid_from_path(org_unit_path_string)
        except UUIDNotFoundException:
            self.logger.info(
                (f"Could not find '{org_unit_path_string}'. " "Creating organisation.")
            )
            self.create_org_unit(org_unit_path_string)
            return self.get_org_unit_uuid_from_path(org_unit_path_string)

    @staticmethod
    def str_to_dict(text):
        """
        Converts a string to a dictionary
        """
        return json.loads(text.replace("'", '"'))

    @staticmethod
    def filter_mo_datestring(datetime_object):
        """
        Converts a datetime object to a date string which is accepted by MO.

        Notes
        -------
        MO only accepts date objects dated at midnight.
        """
        return datetime_object.strftime("%Y-%m-%dT00:00:00")

    @staticmethod
    def filter_strip_non_digits(input_string):
        if type(input_string) is not str:
            return None
        return "".join(c for c in input_string if c in string.digits)

    @staticmethod
    def filter_splitlast(text):
        """
        Splits a string at the last space, returning two elements
        This is convenient for splitting a name into a givenName and a surname
        and works for names with no spaces (givenname will then be empty)
        """
        if text is not None:
            text = str(text)
            if text != "":
                text = str(text)
                s = text.split(" ")
                return [" ".join(s[:-1]), s[-1]]
        return ["", ""]

    def _populate_mapping_with_templates(
        self, mapping: Dict[str, Any], environment: Environment
    ):
        for key, value in mapping.items():
            if type(value) == str:
                mapping[key] = environment.from_string(value)
                mapping[key].globals.update(
                    {
                        "now": datetime.datetime.utcnow,
                        "nonejoin": self.nonejoin,
                        "get_address_type_uuid": self.get_address_type_uuid,
                        "get_it_system_uuid": self.get_it_system_uuid,
                        "get_or_create_org_unit_uuid": self.get_or_create_org_unit_uuid,
                        "get_job_function_uuid": self.get_job_function_uuid,
                        "get_engagement_type_uuid": self.get_engagement_type_uuid,
                        "uuid4": uuid4,
                        "get_org_unit_path_string": self.get_org_unit_path_string,
                        "get_engagement_type_name": self.get_engagement_type_name,
                        "get_job_function_name": self.get_job_function_name,
                    }
                )

            elif type(value) == dict:
                mapping[key] = self._populate_mapping_with_templates(value, environment)
        return mapping

    def to_ldap(self, mo_object_dict: dict, json_key: str, dn=None) -> LdapObject:
        """
        mo_object_dict : dict
            dict with mo objects to convert. for example:
                {'mo_employee': Employee,
                 'mo_address': Address}

            Where Employee and Address are imported from ramodels.

        json_key : str
            Key to look for in the mapping dict. For example:
                - Employee
                - mail_address_attributes
        """
        ldap_object = {}
        try:
            mapping = self.mapping["mo_to_ldap"]
        except KeyError:
            raise IncorrectMapping("Missing mapping 'mo_to_ldap'")
        try:
            object_mapping = mapping[json_key]
        except KeyError:
            raise IncorrectMapping(f"Missing '{json_key}' in mapping 'mo_to_ldap'")

        if "mo_employee" not in mo_object_dict.keys():
            raise NotSupportedException(
                "Only cpr-indexed objects are supported by to_ldap"
            )

        for ldap_field_name, template in object_mapping.items():
            rendered_item = template.render(mo_object_dict)
            if rendered_item:
                ldap_object[ldap_field_name] = rendered_item

        if not dn:
            mo_employee_object = mo_object_dict["mo_employee"]
            cpr_no = mo_employee_object.cpr_no

            try:
                dn = self.dataloader.load_ldap_cpr_object(cpr_no, json_key).dn
            except NoObjectsReturnedException:
                dn = self.username_generator.generate_dn(mo_employee_object)

        ldap_object["dn"] = dn

        return LdapObject(**ldap_object)

    def get_number_of_entries(self, ldap_object: LdapObject):
        """
        Returns the number of data entries in an LDAP object. It is possible for a
        single LDAP field to contain multiple values. This function determines
        if that is the case.
        """
        n = []
        for key, value in ldap_object.dict().items():
            if type(value) is list:
                n.append(len(value))
            else:
                n.append(1)

        number_of_entries_in_this_ldap_object = max(n)
        return number_of_entries_in_this_ldap_object

    def from_ldap(
        self, ldap_object: LdapObject, json_key: str, employee_uuid=None
    ) -> Any:
        """
        uuid : UUID
            Uuid of the employee whom this object belongs to. If None: Generates a new
            uuid
        """

        # This is how many MO objects we need to return - a MO object can have only
        # One value per field. Not multiple. LDAP objects however, can have multiple
        # values per field.
        number_of_entries = self.get_number_of_entries(ldap_object)

        converted_objects = []
        for entry in range(number_of_entries):

            ldap_dict = CaseInsensitiveDict(
                {
                    key: value[min(entry, len(value) - 1)]
                    if type(value) == list and len(value) > 0
                    else value
                    for key, value in ldap_object.dict().items()
                }
            )
            mo_dict = {}
            try:
                mapping = self.mapping["ldap_to_mo"]
            except KeyError:
                raise IncorrectMapping("Missing mapping 'ldap_to_mo'")
            try:
                object_mapping = mapping[json_key]
            except KeyError:
                raise IncorrectMapping(f"Missing '{json_key}' in mapping 'ldap_to_mo'")
            for mo_field_name, template in object_mapping.items():

                value = template.render({"ldap": ldap_dict}).strip()

                # TODO: Is it possible to render a dictionary directly?
                #       Instead of converting from a string
                if "{" in value and ":" in value and "}" in value:
                    value = self.str_to_dict(value)

                if value:
                    mo_dict[mo_field_name] = value

            mo_class: Any = self.import_mo_object_class(json_key)

            if not employee_uuid:
                cpr = mo_dict.get("cpr_no")
                if cpr:
                    dataloader = self.context["user_context"]["dataloader"]
                    employee_uuid = dataloader.find_mo_employee_uuid_sync(cpr)

            if employee_uuid:
                if "person" in mo_class.schema()["properties"].keys():
                    mo_dict["person"] = {"uuid": employee_uuid}
                else:
                    mo_dict["uuid"] = employee_uuid

            required_attributes = self.get_required_attributes(mo_class)

            # If all required attributes are present:
            if all(a in mo_dict for a in required_attributes):
                converted_objects.append(mo_class(**mo_dict))

        return converted_objects
