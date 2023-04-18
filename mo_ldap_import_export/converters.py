# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
#
# SPDX-License-Identifier: MPL-2.0
from __future__ import annotations

import asyncio
import datetime
import json
import re
import string
from json.decoder import JSONDecodeError
from typing import Any
from typing import Dict
from uuid import UUID
from uuid import uuid4

import pandas as pd
from fastramqpi.context import Context
from jinja2 import Environment
from jinja2 import Undefined
from ldap3.utils.ciDict import CaseInsensitiveDict
from ramodels.mo.organisation_unit import OrganisationUnit

from .exceptions import IncorrectMapping
from .exceptions import InvalidNameException
from .exceptions import NotSupportedException
from .exceptions import UUIDNotFoundException
from .ldap_classes import LdapObject
from .logging import logger
from .utils import delete_keys_from_dict
from .utils import import_class


def read_mapping_json(filename: str) -> Any:
    with open(filename, "r") as file:
        data = "\n".join(file.readlines())
        data = re.sub(r"/\*.*\*/", "", data, flags=re.DOTALL)  # Block comments
        data = re.sub(r"//[^\n]*", "", data)  # Line comments
        data = re.sub(
            r",(\s*[}\]])", "\\1", data
        )  # remove trailing commas after the last element in a list or dict
        return json.loads(data)


def find_cpr_field(mapping):
    """
    Get the field which contains the CPR number in LDAP
    """

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
        logger.warning("CPR field not found")

    return cpr_field


def find_ldap_it_system(mapping, mo_it_system_user_keys):
    """
    Loop over all of MO's IT-systems and determine if one of them contains the AD-DN
    as a user_key
    """
    ldap_it_system = None
    for mo_it_system_user_key in mo_it_system_user_keys:
        if mo_it_system_user_key in mapping["ldap_to_mo"]:
            template = mapping["ldap_to_mo"][mo_it_system_user_key]["user_key"]
            dn = template.render({"ldap": {"distinguishedName": "CN=foo"}})
            if dn == "CN=foo":
                ldap_it_system = mo_it_system_user_key
                logger.info(f"Found LDAP IT-system: '{ldap_it_system}'")
                break

    if ldap_it_system is None:
        logger.warning("LDAP IT-system not found")

    return ldap_it_system


class LdapConverter:
    def __init__(self, context: Context):
        self.context = context
        self.user_context = context["user_context"]
        self.settings = self.user_context["settings"]
        self.raw_mapping = self.user_context["mapping"]
        self.dataloader = self.user_context["dataloader"]
        self.org_unit_path_string_separator = (
            self.settings.org_unit_path_string_separator
        )
        self.load_info_dicts()
        self.overview = self.dataloader.load_ldap_overview()
        self.username_generator = self.user_context["username_generator"]

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
            self.raw_mapping,
            ["objectClass", "__import_to_mo__", "__export_to_ldap__"],
        )

        environment = Environment(undefined=Undefined)
        environment.filters["splitfirst"] = LdapConverter.filter_splitfirst
        environment.filters["splitlast"] = LdapConverter.filter_splitlast
        environment.filters["mo_datestring"] = LdapConverter.filter_mo_datestring
        environment.filters["parse_datetime"] = LdapConverter.filter_parse_datetime
        environment.filters["strip_non_digits"] = LdapConverter.filter_strip_non_digits
        self.mapping = self._populate_mapping_with_templates(
            mapping,
            environment,
        )

        self.check_mapping()
        self.cpr_field = find_cpr_field(self.mapping)
        self.ldap_it_system = find_ldap_it_system(self.mapping, self.mo_it_systems)

    def load_info_dicts(self):
        # Note: If new address types or IT systems are added to MO, these dicts need
        # to be re-initialized
        logger.info("[info dict loader] Loading info dicts")
        self.address_type_info = self.dataloader.load_mo_address_types()
        self.it_system_info = self.dataloader.load_mo_it_systems()

        self.org_unit_info = self.dataloader.load_mo_org_units()
        self.org_unit_type_info = self.dataloader.load_mo_org_unit_types()
        self.org_unit_level_info = self.dataloader.load_mo_org_unit_levels()

        self.engagement_type_info = self.dataloader.load_mo_engagement_types()
        self.job_function_info = self.dataloader.load_mo_job_functions()

        self.primary_type_info = self.dataloader.load_mo_primary_types()

        self.mo_address_types = [a["user_key"] for a in self.address_type_info.values()]
        self.mo_it_systems = [a["user_key"] for a in self.it_system_info.values()]

        self.all_info_dicts = {
            f: getattr(self, f)
            for f in dir(self)
            if f.endswith("_info") and type(getattr(self, f)) is dict
        }

        self.check_info_dicts()
        logger.info("[info dict loader] Info dicts loaded successfully")

    def __import_to_mo__(self, json_key):
        """
        Returns True, when we need to import this json key. Otherwise False
        """
        return self.raw_mapping["ldap_to_mo"][json_key]["__import_to_mo__"]

    def __export_to_ldap__(self, json_key):
        """
        Returns True, when we need to export this json key. Otherwise False
        """
        return self.raw_mapping["mo_to_ldap"][json_key]["__export_to_ldap__"]

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
            if (
                attribute not in accepted_attributes
                and not attribute.startswith("extensionAttribute")
                and not attribute.startswith("__")
            ):
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

        logger.info(f"[json check] Accepted keys: {accepted_json_keys}")
        logger.info(f"[json check] Detected keys: {json_keys}")

        for key in json_keys:
            if key not in accepted_json_keys:
                raise IncorrectMapping(
                    (
                        f"'{key}' is not a valid key. "
                        f"Accepted keys are {accepted_json_keys}"
                    )
                )
        logger.info("[json check] Keys OK")

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
            logger.info(f"[json check] checking ldap_to_mo[{json_key}]")

            mo_class = self.import_mo_object_class(json_key)

            accepted_attributes = list(mo_class.schema()["properties"].keys())
            detected_attributes = self.get_mo_attributes(json_key)
            self.check_attributes(detected_attributes, accepted_attributes)
            required_attributes = self.get_required_attributes(mo_class).copy()

            if json_key == "Engagement":
                # We require a primary attribute. If primary is not desired you can set
                # it to {{ NONE }} in the json dict
                required_attributes.append("primary")

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

        for json_key in mo_to_ldap_json_keys:
            logger.info(f"[json check] checking mo_to_ldap['{json_key}']")

            object_class = self.find_ldap_object_class(json_key)

            accepted_attributes = self.overview[object_class]["attributes"].keys()
            detected_attributes = self.get_ldap_attributes(json_key)

            self.check_attributes(detected_attributes, accepted_attributes)

            detected_single_value_attributes = [
                a for a in detected_attributes if self.dataloader.single_value[a]
            ]

            # Check single value fields which map to MO address/it-user/... objects.
            # We like fields which map to these MO objects to be multi-value fields,
            # to avoid data being overwritten if two objects of the same type are
            # added in MO
            def filter_fields_to_check(fields_to_check):
                """
                A field only needs to be checked if we use information from LDAP in
                the 'ldap_to_mo' mapping. If we do not, we also do not need to make
                sure that we are writing information to LDAP for this field.
                """
                fields_with_ldap_reference = []
                for field in fields_to_check:
                    mo_field = field.split(".")[1]
                    if "ldap." in self.raw_mapping["ldap_to_mo"][json_key][mo_field]:
                        fields_with_ldap_reference.append(field)

                return fields_with_ldap_reference

            if json_key in self.mo_address_types:
                fields_to_check = filter_fields_to_check(["mo_employee_address.value"])
            elif json_key in self.mo_it_systems:
                fields_to_check = filter_fields_to_check(
                    ["mo_employee_it_user.user_key"]
                )
            elif json_key == "Engagement":
                fields_to_check = filter_fields_to_check(
                    [
                        "mo_employee_engagement.user_key",
                        "mo_employee_engagement.org_unit.uuid",
                        "mo_employee_engagement.engagement_type.uuid",
                        "mo_employee_engagement.job_function.uuid",
                    ]
                )
            else:
                fields_to_check = []

            for attribute in detected_single_value_attributes:
                template = self.raw_mapping["mo_to_ldap"][json_key][attribute]
                for field_to_check in fields_to_check:
                    if field_to_check in template:
                        logger.warning(
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
        logger.info("[json check] checking DAR scope")
        ldap_to_mo_json_keys = self.get_ldap_to_mo_json_keys()

        for json_key in ldap_to_mo_json_keys:
            mo_class = self.find_mo_object_class(json_key)
            if ".Address" in mo_class:
                uuid = self.get_object_uuid_from_user_key(
                    self.address_type_info, json_key
                )
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
            accepted_attributes = sorted(
                self.overview[object_class]["attributes"].keys()
            )
            for key, value in raw_mapping[json_key].items():
                if type(value) is not str:
                    continue
                if "ldap." in value:
                    ldap_refs = value.split("ldap.")[1:]

                    for ldap_ref in ldap_refs:
                        ldap_attribute = re.split(invalid_chars_regex, ldap_ref)[0]

                        if (
                            ldap_attribute not in accepted_attributes
                            and not ldap_attribute.startswith("extensionAttribute")
                        ):
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

    def check_uuid_refs_in_mo_objects(self):
        raw_mapping = self.raw_mapping["ldap_to_mo"]
        for json_key in self.get_ldap_to_mo_json_keys():
            object_class = self.import_mo_object_class(json_key)
            mapping_dict = raw_mapping[json_key]
            schema = object_class.schema()
            if "required" in schema:
                required_attributes = object_class.schema()["required"]
            else:
                required_attributes = []

            # If we are dealing with an object that links to a person/org_unit
            if "person" in schema["properties"]:
                # either person or org_unit needs to be in the dict
                if "person" not in mapping_dict and "org_unit" not in mapping_dict:
                    raise IncorrectMapping(
                        (
                            "Either 'person' or 'org_unit' key needs to be present in "
                            f"ldap_to_mo['{json_key}']"
                        )
                    )
                if "person" in mapping_dict and "org_unit" in mapping_dict:
                    if not (
                        "person" in required_attributes
                        and "org_unit" in required_attributes
                    ):
                        raise IncorrectMapping(
                            (
                                "Either 'person' or 'org_unit' key needs to be present "
                                f"in ldap_to_mo['{json_key}']. Not both"
                            )
                        )
                uuid_key = "person" if "person" in mapping_dict else "org_unit"

                # And the corresponding item needs to be a dict with an uuid key
                if "dict(uuid=" not in mapping_dict[uuid_key].replace(" ", ""):
                    raise IncorrectMapping(
                        (
                            f"ldap_to_mo['{json_key}']['{uuid_key}'] needs to be a "
                            f"dict with 'uuid' as one of it's keys"
                        )
                    )

            # Otherwise: We are dealing with the org_unit/person itself.
            else:
                # A field called 'uuid' needs to be present
                if "uuid" not in mapping_dict:
                    raise IncorrectMapping(
                        f"ldap_to_mo['{json_key}'] needs to contain a key called 'uuid'"
                    )

                # And it needs to contain a reference to the employee_uuid global
                if "employee_uuid" not in mapping_dict["uuid"]:
                    raise IncorrectMapping(
                        (
                            f"ldap_to_mo['{json_key}']['uuid'] needs to contain a "
                            "reference to 'employee_uuid'"
                        )
                    )

    def check_get_uuid_functions(self):

        # List of all 'get_uuid' functions. For example "get_address_type_uuid("
        get_uuid_function_strings = [
            f + "(" for f in dir(self) if f.startswith("get_") and f.endswith("_uuid")
        ]

        # List all user keys from the different info-dicts
        all_user_keys = []
        for info_dict in self.all_info_dicts.values():
            user_keys = [v["user_key"] for v in info_dict.values()]
            all_user_keys.extend(user_keys)

        # Check ldap_to_mo mapping only. in mo_to_ldap mapping we do not need 'get_uuid'
        # functions because we can just extract the uuid from a mo object directly.
        for json_key in self.get_json_keys("ldap_to_mo"):
            for mo_attribute, template in self.raw_mapping["ldap_to_mo"][
                json_key
            ].items():

                if type(template) is not str:
                    continue
                for get_uuid_function_string in get_uuid_function_strings:

                    # If we are using a 'get_uuid' function in this template:
                    if get_uuid_function_string in template:
                        argument = template.split(get_uuid_function_string)[1].split(
                            ")"
                        )[0]

                        # And if the argument is a hard-coded string:
                        if argument.startswith("'") and argument.endswith("'"):
                            logger.info(f"[json check] Checking {template}")

                            # Check if the argument is a valid user_key
                            user_key = argument.replace("'", "")
                            if user_key not in all_user_keys:
                                raise IncorrectMapping(
                                    (
                                        f"'{user_key}' not found in any info dict. "
                                        "Please check "
                                        f"ldap_to_mo['{json_key}']['{mo_attribute}']"
                                        f"={template}"
                                    )
                                )

    def check_import_and_export_flags(self):
        """
        Checks that '__import_to_mo__' and '__export_to_ldap__' keys are present in
        the json dict
        """

        expected_key_dict = {
            "ldap_to_mo": "__import_to_mo__",
            "mo_to_ldap": "__export_to_ldap__",
        }

        for conversion in ["ldap_to_mo", "mo_to_ldap"]:
            ie_key = expected_key_dict[conversion]

            for json_key in self.get_json_keys(conversion):
                if ie_key not in self.raw_mapping[conversion][json_key]:
                    raise IncorrectMapping(
                        f"Missing '{ie_key}' key in {conversion}['{json_key}']"
                    )
                if type(self.raw_mapping[conversion][json_key][ie_key]) is not bool:
                    raise IncorrectMapping(
                        f"{conversion}['{json_key}']['{ie_key}'] is not a boolean"
                    )

    def check_cpr_field_or_it_system(self):
        """
        Check that we have either a cpr-field OR an it-system which maps to an LDAP DN
        """

        cpr_field = find_cpr_field(self.mapping)
        ldap_it_system = find_ldap_it_system(self.mapping, self.mo_it_systems)
        if not cpr_field and not ldap_it_system:
            raise IncorrectMapping(
                "Neither a cpr-field or an ldap it-system could be found"
            )

    def check_mapping(self):
        logger.info("[json check] Checking json file")

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

        # Check that MO objects have a uuid field
        self.check_uuid_refs_in_mo_objects()

        # Check that get_..._uuid functions have valid input strings
        self.check_get_uuid_functions()

        # Check for import and export flags
        self.check_import_and_export_flags()

        # Check to see if there is an existing link between LDAP and MO
        self.check_cpr_field_or_it_system()

        logger.info("[json check] Attributes OK")

    def check_info_dict_for_duplicates(self, info_dict):
        """
        Check that we do not see the same name twice in one info dict
        """
        name_key = "user_key"
        names = [info[name_key] for info in info_dict.values()]
        if len(set(names)) != len(names):
            raise InvalidNameException(
                f"Duplicate values found in info_dict['{name_key}'] = {sorted(names)}"
            )

    def check_org_unit_info_dict(self):
        """
        Check if the org unit separator is not in any of the org unit names
        """
        separator = self.org_unit_path_string_separator
        for org_unit_name in [info["name"] for info in self.org_unit_info.values()]:
            if separator in org_unit_name:
                raise InvalidNameException(
                    f"Found {separator} in '{org_unit_name}'. This is not allowed."
                )

    def check_info_dicts(self):
        logger.info("[info dict check] Checking info dicts")
        for info_dict_name, info_dict in self.all_info_dicts.items():
            if info_dict_name != "org_unit_info":
                self.check_info_dict_for_duplicates(info_dict)

        self.check_org_unit_info_dict()

    @staticmethod
    def nonejoin(*args):
        """
        Joins items together if they are not None or emtpy lists
        """
        items_to_join = [a for a in args if a]
        return ", ".join(items_to_join)

    def get_object_user_key_from_uuid(self, info_dict: dict, uuid: str):
        return info_dict[str(uuid)]["user_key"]

    @staticmethod
    def name_normalizer(name):
        return name.lower().replace("-", " ")

    def get_object_uuid_from_user_key(self, info_dict: dict, user_key: str):
        name_key = "user_key"
        if not user_key:
            raise UUIDNotFoundException("object type name is empty")

        normalized_name = self.name_normalizer(user_key)

        candidates = {
            info[name_key]: info["uuid"]
            for info in info_dict.values()
            if self.name_normalizer(info[name_key]) == normalized_name
        }
        if len(candidates) > 0:
            if user_key in candidates:
                return candidates[user_key]
            return list(candidates.values())[0]
        else:
            raise UUIDNotFoundException(f"'{user_key}' not found in '{info_dict}'")

    def get_address_type_uuid(self, address_type: str):
        return self.get_object_uuid_from_user_key(self.address_type_info, address_type)

    def get_it_system_uuid(self, it_system: str):
        return self.get_object_uuid_from_user_key(self.it_system_info, it_system)

    def get_job_function_uuid(self, job_function: str):
        return self.get_object_uuid_from_user_key(self.job_function_info, job_function)

    def get_primary_type_uuid(self, primary: str):
        return self.get_object_uuid_from_user_key(self.primary_type_info, primary)

    def get_engagement_type_uuid(self, engagement_type: str):
        return self.get_object_uuid_from_user_key(
            self.engagement_type_info, engagement_type
        )

    def get_org_unit_type_uuid(self, org_unit_type: str):
        return self.get_object_uuid_from_user_key(
            self.org_unit_type_info, org_unit_type
        )

    def get_org_unit_level_uuid(self, org_unit_level: str):
        return self.get_object_uuid_from_user_key(
            self.org_unit_level_info, org_unit_level
        )

    def get_address_type_user_key(self, uuid: str):
        return self.get_object_user_key_from_uuid(self.address_type_info, uuid)

    def get_it_system_user_key(self, uuid: str):
        return self.get_object_user_key_from_uuid(self.it_system_info, uuid)

    def get_engagement_type_user_key(self, uuid: str):
        return self.get_object_user_key_from_uuid(self.engagement_type_info, uuid)

    def get_job_function_user_key(self, uuid: str):
        return self.get_object_user_key_from_uuid(self.job_function_info, uuid)

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
                logger.info(f"Importing {partial_path_string}")

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

                # Note: 1902 seems to be the earliest accepted year by OS2mo
                # We pick 1960 because MO's dummy data also starts all organizations
                # in 1960...
                # We just want a very early date here, to avoid that imported employee
                # engagements start before the org-unit existed.
                from_date = datetime.datetime(1960, 1, 1).strftime("%Y-%m-%dT00:00:00")
                org_unit = OrganisationUnit.from_simplified_fields(
                    user_key=str(uuid4()),
                    name=self.imported_org_unit_tag + name,
                    org_unit_type_uuid=self.default_org_unit_type_uuid,
                    org_unit_level_uuid=self.default_org_unit_level_uuid,
                    from_date=from_date,
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
        if not org_unit_path_string:
            raise UUIDNotFoundException("Organization unit string is empty")
        try:
            return self.get_org_unit_uuid_from_path(org_unit_path_string)
        except UUIDNotFoundException:
            logger.info(
                (f"Could not find '{org_unit_path_string}'. " "Creating organisation.")
            )
            self.create_org_unit(org_unit_path_string)
            return self.get_org_unit_uuid_from_path(org_unit_path_string)

    @staticmethod
    def str_to_dict(text):
        """
        Converts a string to a dictionary
        """
        return json.loads(text.replace("'", '"').replace("Undefined", "null"))

    @staticmethod
    def filter_parse_datetime(datestring):
        if not datestring or datestring.lower() == "none":
            return None
        try:
            return pd.to_datetime(datestring, dayfirst=False)
        except pd.errors.OutOfBoundsDatetime:
            year = int(datestring.split("-")[0])
            if year > 2000:
                return pd.Timestamp.max
            else:
                return pd.Timestamp.min

    @staticmethod
    def filter_mo_datestring(datetime_object):
        """
        Converts a datetime object to a date string which is accepted by MO.

        Notes
        -------
        MO only accepts date objects dated at midnight.
        """
        if not datetime_object:
            return None
        return datetime_object.strftime("%Y-%m-%dT00:00:00")

    @staticmethod
    def filter_strip_non_digits(input_string):
        if type(input_string) is not str:
            return None
        return "".join(c for c in input_string if c in string.digits)

    @staticmethod
    def filter_splitfirst(text, separator=" "):
        """
        Splits a string at the first space, returning two elements
        This is convenient for splitting a name into a givenName and a surname
        and works for names with no spaces (surname will then be empty)
        """
        if text is not None:
            text = str(text)
            if text != "":
                s = text.split(separator, 1)
                return s if len(s) > 1 else (s + [""])
        return ["", ""]

    @staticmethod
    def filter_splitlast(text, separator=" "):
        """
        Splits a string at the last space, returning two elements
        This is convenient for splitting a name into a givenName and a surname
        and works for names with no spaces (givenname will then be empty)
        """
        if text is not None:
            text = str(text)
            if text != "":
                text = str(text)
                s = text.split(separator)
                return [separator.join(s[:-1]), s[-1]]
        return ["", ""]

    def _populate_mapping_with_templates(
        self, mapping: Dict[str, Any], environment: Environment
    ):
        globals_dict = {
            "now": datetime.datetime.utcnow,
            "nonejoin": self.nonejoin,
            "get_address_type_uuid": self.get_address_type_uuid,
            "get_it_system_uuid": self.get_it_system_uuid,
            "get_or_create_org_unit_uuid": self.get_or_create_org_unit_uuid,
            "get_job_function_uuid": self.get_job_function_uuid,
            "get_primary_type_uuid": self.get_primary_type_uuid,
            "get_engagement_type_uuid": self.get_engagement_type_uuid,
            "uuid4": uuid4,
            "get_org_unit_path_string": self.get_org_unit_path_string,
            "get_engagement_type_user_key": self.get_engagement_type_user_key,
            "get_job_function_user_key": self.get_job_function_user_key,
        }
        for key, value in mapping.items():
            if type(value) == str:
                mapping[key] = environment.from_string(value)
                mapping[key].globals.update(globals_dict)

            elif type(value) == dict:
                mapping[key] = self._populate_mapping_with_templates(value, environment)
        return mapping

    def to_ldap(self, mo_object_dict: dict, json_key: str, dn: str) -> LdapObject:
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
        self, ldap_object: LdapObject, json_key: str, employee_uuid: UUID
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
            context = {"ldap": ldap_dict, "employee_uuid": str(employee_uuid)}
            try:
                mapping = self.mapping["ldap_to_mo"]
            except KeyError:
                raise IncorrectMapping("Missing mapping 'ldap_to_mo'")
            try:
                object_mapping = mapping[json_key]
            except KeyError:
                raise IncorrectMapping(f"Missing '{json_key}' in mapping 'ldap_to_mo'")
            for mo_field_name, template in object_mapping.items():
                try:
                    value = template.render(context).strip()

                    # Sloppy mapping can lead to the following rendered strings:
                    # - {{ldap.mail or None}} renders as "None"
                    # - {{ldap.mail}} renders as "[]" if ldap.mail is empty
                    #
                    # Mapping with {{ldap.mail or NONE}} solves both, but let's check
                    # for "none" or "[]" strings anyway to be more robust.
                    if value.lower() == "none" or value == "[]":
                        value = ""
                except UUIDNotFoundException:
                    continue
                # TODO: Is it possible to render a dictionary directly?
                #       Instead of converting from a string
                if "{" in value and ":" in value and "}" in value:
                    try:
                        value = self.str_to_dict(value)
                    except JSONDecodeError:
                        raise IncorrectMapping(
                            (
                                f"Could not convert {value} in "
                                f"{json_key}['{mo_field_name}'] to dict"
                            )
                        )

                if value:
                    mo_dict[mo_field_name] = value

            mo_class: Any = self.import_mo_object_class(json_key)
            required_attributes = self.get_required_attributes(mo_class)

            # If all required attributes are present:
            if all(a in mo_dict for a in required_attributes):
                converted_objects.append(mo_class(**mo_dict))
            else:
                logger.info(
                    (
                        f"Could not convert {mo_dict}. "
                        f"The following attributes are required: {required_attributes}"
                    )
                )

        return converted_objects
