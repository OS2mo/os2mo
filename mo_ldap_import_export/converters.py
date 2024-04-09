# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
from __future__ import annotations

import copy
import json
import re
import string
from datetime import datetime
from itertools import compress
from json.decoder import JSONDecodeError
from typing import Any
from uuid import UUID
from uuid import uuid4

import pydantic
from fastramqpi.context import Context
from fastramqpi.ramqp.utils import RequeueMessage
from jinja2 import Environment
from jinja2 import exceptions as jinja_exceptions
from ldap3.utils.ciDict import CaseInsensitiveDict
from ldap3.utils.dn import parse_dn
from more_itertools import one
from ramodels.mo.organisation_unit import OrganisationUnit

from .config import Settings
from .dataloaders import DataLoader
from .environments import environment
from .exceptions import IncorrectMapping
from .exceptions import InvalidNameException
from .exceptions import NotSupportedException
from .exceptions import UUIDNotFoundException
from .ldap import is_uuid
from .ldap_classes import LdapObject
from .logging import logger
from .utils import delete_keys_from_dict
from .utils import exchange_ou_in_dn
from .utils import extract_ou_from_dn
from .utils import import_class


async def find_cpr_field(mapping):
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
        try:
            value = (await template.render_async({"mo_employee": mo_dict})).strip()
        except jinja_exceptions.UndefinedError:
            continue

        if value == search_result:
            cpr_field = ldap_field_name
            logger.info(f"Found CPR field in LDAP: '{cpr_field}'")
            break

    if cpr_field is None:
        logger.warning("CPR field not found")

    return cpr_field


async def find_ldap_it_system(
    settings: Settings, mapping: dict[str, Any], mo_it_system_user_keys: list[str]
) -> str | None:
    """
    Loop over all of MO's IT-systems and determine if one of them contains the AD-DN
    as a user_key
    """
    detection_key = str(uuid4())
    relevant_keys: set[str] = set(mo_it_system_user_keys) & mapping["ldap_to_mo"].keys()

    async def template_contains_unique_field(user_key: str) -> bool:
        """Check if the template found at user-key utilizes the unique id.

        The check is done by templating the unique id using a known string and checking
        whether the known string is in the output.
        """
        # TODO: XXX: Could we simply check the template string??
        template = mapping["ldap_to_mo"][user_key]["user_key"]
        unique_id: str = await template.render_async(
            {"ldap": {settings.ldap_unique_id_field: detection_key}}
        )
        return unique_id == detection_key

    found_itsystems = {
        user_key
        for user_key in relevant_keys
        if await template_contains_unique_field(user_key)
    }
    if len(found_itsystems) == 0:
        logger.warning("LDAP IT-system not found")
        return None
    if len(found_itsystems) > 1:
        logger.error("Multiple LDAP IT-system found!")
        return None
    found_itsystem = one(found_itsystems)
    logger.info(f"Found LDAP IT-system: '{found_itsystem}'")
    return found_itsystem


class LdapConverter:
    def __init__(self, context: Context):
        self.context = context
        self.user_context = context["user_context"]
        self.settings = self.user_context["settings"]
        self.raw_mapping = self.user_context["mapping"]
        self.dataloader: DataLoader = self.user_context["dataloader"]
        self.org_unit_path_string_separator: str = (
            self.settings.org_unit_path_string_separator
        )

    async def _init(self):
        await self.load_info_dicts()
        self.overview = self.dataloader.load_ldap_overview()
        self.username_generator = self.user_context["username_generator"]

        self.default_org_unit_type_uuid = self.get_org_unit_type_uuid(
            self.settings.default_org_unit_type
        )
        self.default_org_unit_level_uuid = self.get_org_unit_level_uuid(
            self.settings.default_org_unit_level
        )

        mapping = delete_keys_from_dict(
            self.raw_mapping,
            ["objectClass", "_import_to_mo_", "_export_to_ldap_"],
        )

        self.mapping = self._populate_mapping_with_templates(
            copy.deepcopy(mapping),
            environment,
        )

        await self.check_mapping()
        self.cpr_field = await find_cpr_field(self.mapping)
        self.ldap_it_system = await find_ldap_it_system(
            self.settings, self.mapping, self.mo_it_systems
        )

    async def load_info_dicts(self):
        # Note: If new address types or IT systems are added to MO, these dicts need
        # to be re-initialized
        logger.info("[info dict loader] Loading info dicts")
        self.employee_address_type_info = (
            await self.dataloader.load_mo_employee_address_types()
        )
        self.org_unit_address_type_info = (
            await self.dataloader.load_mo_org_unit_address_types()
        )
        self.it_system_info = await self.dataloader.load_mo_it_systems()
        self.visibility_info = await self.dataloader.load_mo_visibility()

        self.org_unit_info = await self.dataloader.load_mo_org_units()
        self.org_unit_type_info = await self.dataloader.load_mo_org_unit_types()
        self.org_unit_level_info = await self.dataloader.load_mo_org_unit_levels()

        self.engagement_type_info = await self.dataloader.load_mo_engagement_types()
        self.job_function_info = await self.dataloader.load_mo_job_functions()

        mo_employee_address_types = [
            a["user_key"] for a in self.employee_address_type_info.values()
        ]
        mo_org_unit_address_types = [
            a["user_key"] for a in self.org_unit_address_type_info.values()
        ]
        self.mo_address_types = list(
            set(mo_employee_address_types + mo_org_unit_address_types)
        )
        self.mo_it_systems = [a["user_key"] for a in self.it_system_info.values()]

        self.all_info_dicts = {
            f: getattr(self, f)
            for f in dir(self)
            if f.endswith("_info") and isinstance(getattr(self, f), dict)
        }

        self.check_info_dicts()
        logger.info("[info dict loader] Info dicts loaded successfully")

    def _import_to_mo_(self, json_key: str, manual_import: bool):
        """
        Returns True, when we need to import this json key. Otherwise False
        """
        import_flag = self.raw_mapping["ldap_to_mo"][json_key]["_import_to_mo_"]
        import_flag = import_flag.lower()

        match import_flag:
            case "true":
                return True
            case "manual_import_only":
                return manual_import
            case "false":
                return False
            case _:
                raise IncorrectMapping(f"Import flag = '{import_flag}' not recognized")

    def _export_to_ldap_(self, json_key):
        """
        Returns True, when we need to export this json key. Otherwise False
        """
        export_flag = self.raw_mapping["mo_to_ldap"][json_key][
            "_export_to_ldap_"
        ].lower()
        if export_flag == "pause":
            logger.info("_export_to_ldap_ = 'pause'. Requeueing.")
            raise RequeueMessage()
        return export_flag == "true"

    def find_object_class(self, json_key, conversion):
        mapping = self.raw_mapping[conversion]
        if json_key not in mapping.keys():
            raise IncorrectMapping(f"{json_key} not found in {conversion} json dict")
        return mapping[json_key]["objectClass"]

    def find_ldap_object_class(self, json_key):
        return self.find_object_class(json_key, "mo_to_ldap")

    def find_mo_object_class(self, json_key):
        return self.find_object_class(json_key, "ldap_to_mo")

    def import_mo_object_class(self, json_key):
        return import_class(self.find_mo_object_class(json_key))

    def get_ldap_attributes(self, json_key, remove_dn=True):
        ldap_attributes = list(self.mapping["mo_to_ldap"][json_key].keys())
        if "dn" in ldap_attributes and remove_dn:
            # "dn" is the key which all LDAP objects have, not an attribute.
            ldap_attributes.remove("dn")
        return ldap_attributes

    def get_mo_attributes(self, json_key):
        return list(self.mapping["ldap_to_mo"][json_key].keys())

    def check_attributes(self, detected_attributes, accepted_attributes):
        for attribute in detected_attributes:
            if (
                attribute not in accepted_attributes
                and not attribute.startswith("extensionAttribute")
                and not attribute.startswith("__")
                and not attribute == "sAMAccountName"
                and not attribute == "entryUUID"
            ):
                raise IncorrectMapping(
                    f"Attribute '{attribute}' not allowed."
                    f" Allowed attributes are {accepted_attributes}"
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
        accepted_json_keys: list[str] = (
            ["Employee", "Engagement", "Custom"]
            + self.mo_address_types
            + self.mo_it_systems
        )

        return accepted_json_keys

    def check_key_validity(self):
        mo_to_ldap_json_keys = self.get_mo_to_ldap_json_keys()
        ldap_to_mo_json_keys = self.get_ldap_to_mo_json_keys()

        json_keys = set(mo_to_ldap_json_keys + ldap_to_mo_json_keys)
        accepted_json_keys = set(self.get_accepted_json_keys())

        logger.info(f"[json check] Accepted keys: {accepted_json_keys}")
        logger.info(f"[json check] Detected keys: {json_keys}")

        unaccepted_keys = json_keys - accepted_json_keys
        if unaccepted_keys:
            raise IncorrectMapping(
                f"{unaccepted_keys} are not valid keys. "
                f"Accepted keys are {accepted_json_keys}"
            )
        logger.info("[json check] Keys OK")

    def get_required_attributes(self, mo_class):
        if "required" in mo_class.schema().keys():
            return mo_class.schema()["required"]
        return []

    @staticmethod
    def clean_get_current_method_from_template_string(template_string):
        """
        Cleans all calls to the get_current_* methods from a template string
        """
        return re.sub(r"get_current[^)]*\)", "", template_string)

    def check_ldap_attributes(self):
        mo_to_ldap_json_keys = self.get_mo_to_ldap_json_keys()

        for json_key in mo_to_ldap_json_keys:
            logger.info(f"[json check] checking mo_to_ldap['{json_key}']")

            object_class = self.find_ldap_object_class(json_key)

            accepted_attributes = list(self.overview[object_class]["attributes"].keys())
            detected_attributes = self.get_ldap_attributes(json_key, remove_dn=False)

            self.check_attributes(detected_attributes, accepted_attributes + ["dn"])

            detected_single_value_attributes = [
                a
                for a in detected_attributes
                if a == "dn" or self.dataloader.single_value[a]
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
                    template = self.clean_get_current_method_from_template_string(
                        self.raw_mapping["ldap_to_mo"][json_key][mo_field]
                    )
                    if "ldap." in template:
                        fields_with_ldap_reference.append(field)

                return fields_with_ldap_reference

            fields_to_check = []
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

            for attribute in detected_single_value_attributes:
                template = self.raw_mapping["mo_to_ldap"][json_key][attribute]
                for field_to_check in fields_to_check:
                    if field_to_check in template:
                        logger.warning(
                            f"[json check] {object_class}['{attribute}'] LDAP "
                            "attribute cannot contain multiple values. "
                            "Values in LDAP will be overwritten if "
                            f"multiple objects of the '{json_key}' type are "
                            "added in MO."
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
                        "Could not find all attributes belonging to "
                        f"{fields_to_check}. Only found the following "
                        f"attributes: {matching_attributes}."
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
                        f"LDAP Attributes mapping to '{json_key}' are a mix "
                        "of multi- and single-value. The following attributes are "
                        f"single-value: {matching_single_value_attributes} "
                        "while the following are multi-value attributes: "
                        f"{matching_multi_value_attributes}"
                    )

                if json_key == "Engagement":
                    if len(matching_multi_value_attributes) > 0:
                        raise IncorrectMapping(
                            f"LDAP Attributes mapping to 'Engagement' contain one or "
                            f"more multi-value attributes "
                            f"{matching_multi_value_attributes}, which is not allowed"
                        )

    def check_dar_scope(self):
        logger.info("[json check] checking DAR scope")
        ldap_to_mo_json_keys = self.get_ldap_to_mo_json_keys()

        for json_key in ldap_to_mo_json_keys:
            mo_class = self.find_mo_object_class(json_key)
            if ".Address" in mo_class:
                try:
                    info_dict = self.employee_address_type_info
                    uuid = self.get_object_uuid_from_user_key(info_dict, json_key)
                except UUIDNotFoundException:
                    info_dict = self.org_unit_address_type_info
                    uuid = self.get_object_uuid_from_user_key(info_dict, json_key)

                if info_dict[uuid]["scope"] == "DAR":
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
                list(self.overview[object_class]["attributes"].keys()) + ["dn"]
            )
            for value in raw_mapping[json_key].values():
                if not isinstance(value, str):
                    continue
                if "ldap." in value:
                    ldap_refs = value.split("ldap.")[1:]

                    for ldap_ref in ldap_refs:
                        ldap_attribute = re.split(invalid_chars_regex, ldap_ref)[0]
                        self.check_attributes([ldap_attribute], accepted_attributes)

    def check_get_uuid_functions(self):
        # List of all 'get_uuid' functions. For example "get_it_system_uuid("
        get_uuid_function_strings = [
            f + "("
            for f in dir(self)
            if f.startswith("get_") and f.endswith("_uuid") and "create" not in f
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
                if not isinstance(template, str):
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
                                    f"'{user_key}' not found in any info dict. "
                                    "Please check "
                                    f"ldap_to_mo['{json_key}']['{mo_attribute}']"
                                    f"={template}"
                                )

    async def check_cpr_field_or_it_system(self):
        """
        Check that we have either a cpr-field OR an it-system which maps to an LDAP DN
        """

        cpr_field = await find_cpr_field(self.mapping)
        ldap_it_system = await find_ldap_it_system(
            self.settings, self.mapping, self.mo_it_systems
        )
        if not cpr_field and not ldap_it_system:
            raise IncorrectMapping(
                "Neither a cpr-field or an ldap it-system could be found"
            )

    async def check_mapping(self):
        logger.info("[json check] Checking json file")

        # Check to make sure that all keys are valid
        self.check_key_validity()

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

        # Check that get_..._uuid functions have valid input strings
        self.check_get_uuid_functions()

        # Check to see if there is an existing link between LDAP and MO
        await self.check_cpr_field_or_it_system()

        logger.info("[json check] Attributes OK")

    def check_info_dict_for_duplicates(self, info_dict, name_key="user_key"):
        """
        Check that we do not see the same name twice in one info dict
        """
        names = [info[name_key] for info in info_dict.values()]
        if len(set(names)) != len(names):
            duplicates = [name for name in names if names.count(name) > 1]
            raise InvalidNameException(
                f"Duplicate values found in info_dict['{name_key}'] = {sorted(duplicates)}"
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

            for info in info_dict.values():
                if "uuid" not in info:
                    raise IncorrectMapping("'uuid' key not found in info-dict")
                uuid = info["uuid"]
                if not isinstance(uuid, str):
                    raise IncorrectMapping(f"{uuid} is not a string")
                if not is_uuid(uuid):
                    raise IncorrectMapping(f"{uuid} is not an uuid")

        self.check_org_unit_info_dict()

    @staticmethod
    def nonejoin(*args) -> str:
        """
        Joins items together if they are not None or emtpy lists
        """
        items_to_join = [a for a in args if a]
        return ", ".join(items_to_join)

    def nonejoin_orgs(self, *args) -> str:
        """
        Joins orgs together if they are not empty strings
        """
        items_to_join = [a.strip() for a in args if a]
        sep = self.org_unit_path_string_separator
        return sep.join(items_to_join)

    def remove_first_org(self, orgstr):
        """
        Remove first org from orgstr
        """
        _, *rest = orgstr.split(self.org_unit_path_string_separator)
        return self.nonejoin_orgs(*rest)

    async def get_object_item_from_uuid(
        self, info_dict: str, uuid: str, key: str
    ) -> Any:
        try:
            return getattr(self, info_dict)[str(uuid)][key]
        except KeyError:
            await self.load_info_dicts()
            return getattr(self, info_dict)[str(uuid)][key]

    async def get_object_user_key_from_uuid(self, info_dict: str, uuid: str) -> str:
        user_key: str = await self.get_object_item_from_uuid(
            info_dict, uuid, "user_key"
        )
        return user_key

    async def get_object_name_from_uuid(self, info_dict: str, uuid: str) -> str:
        name: str = await self.get_object_item_from_uuid(info_dict, uuid, "name")
        return name

    @staticmethod
    def string_normalizer(name):
        return name.lower().replace("-", " ")

    def get_object_uuid_from_info_dict(
        self, info_dict: dict, key: str, value: str
    ) -> str:
        accepted_values = [d[key] for d in info_dict.values()]
        error_message = f"'{value}' is not among {accepted_values}"
        if not value:
            raise UUIDNotFoundException(error_message)

        normalized_value = self.string_normalizer(value)

        candidates: dict[str, str] = {
            info[key]: info["uuid"]
            for info in info_dict.values()
            if self.string_normalizer(info[key]) == normalized_value
        }
        if len(candidates) > 0:
            if value in candidates:
                return candidates[value]
            return list(candidates.values())[0]
        else:
            raise UUIDNotFoundException(error_message)

    def get_object_uuid_from_user_key(self, info_dict: dict, user_key: str) -> str:
        return self.get_object_uuid_from_info_dict(info_dict, "user_key", user_key)

    def get_object_uuid_from_name(self, info_dict: dict, name: str) -> str:
        return self.get_object_uuid_from_info_dict(info_dict, "name", name)

    def get_employee_address_type_uuid(self, address_type: str) -> str:
        return self.get_object_uuid_from_user_key(
            self.employee_address_type_info, address_type
        )

    def get_org_unit_address_type_uuid(self, address_type: str) -> str:
        return self.get_object_uuid_from_user_key(
            self.org_unit_address_type_info, address_type
        )

    def get_it_system_uuid(self, it_system: str) -> str:
        return self.get_object_uuid_from_user_key(self.it_system_info, it_system)

    def get_visibility_uuid(self, visibility: str) -> str:
        return self.get_object_uuid_from_user_key(self.visibility_info, visibility)

    def get_job_function_uuid(self, job_function: str) -> str:
        return self.get_object_uuid_from_name(self.job_function_info, job_function)

    async def get_or_create_job_function_uuid(
        self,
        job_function: str,
        default: str | None = None,
    ) -> str:
        if not job_function:
            if default is None:
                raise UUIDNotFoundException("job_function is empty")
            else:
                logger.info(
                    "job_function is empty, using provided default",
                    default=default,
                )
                job_function = default
        try:
            return self.get_job_function_uuid(job_function)
        except UUIDNotFoundException:
            uuid = await self.dataloader.create_mo_job_function(job_function)
            self.job_function_info = await self.dataloader.load_mo_job_functions()
            self.check_info_dicts()
            return str(uuid)

    async def get_primary_type_uuid(self, primary: str) -> str:
        result = await self.dataloader.graphql_client.read_class_uuid_by_facet_and_class_user_key(
            "primary_type", primary
        )
        return str(
            one(
                result.objects,
                too_short=UUIDNotFoundException(
                    f"primary_type not found, user_key: {primary}"
                ),
            ).uuid
        )

    def get_engagement_type_uuid(self, engagement_type: str) -> str:
        return self.get_object_uuid_from_name(
            self.engagement_type_info, engagement_type
        )

    async def get_current_engagement_attribute_uuid_dict(
        self,
        attribute: str,
        employee_uuid: UUID,
        engagement_user_key: str,
    ) -> dict[str, str]:
        """
        Returns an uuid-dictionary with the uuid matching the desired attribute

        Parameters
        --------------
        attribute: str
            attribute to look up. For example:
                - org_unit_uuid
                - engagement_type_uuid
                - primary_uuid
        employee_uuid: UUID
            uuid of the employee
        engagement_user_key: str
            user_key of the engagement

        Notes
        --------
        This method requests all engagements for employee with uuid = employee_uuid
        and then filters out all engagements which do not match engagement_user_key.
        If there is exactly one engagement left after this, the uuid of the requested
        attribute is returned.
        """

        if "uuid" not in attribute:
            raise ValueError(
                "attribute must be an uuid-string. For example 'job_function_uuid'"
            )

        logger.info(
            f"Looking for '{attribute}' in existing engagement with "
            f"user_key = '{engagement_user_key}' "
            f"and employee_uuid = '{employee_uuid}'"
        )
        engagement_dicts = await self.dataloader.load_mo_employee_engagement_dicts(
            employee_uuid, engagement_user_key
        )

        if not engagement_dicts:
            raise UUIDNotFoundException(
                f"Employee with uuid = {employee_uuid} has no engagements "
                f"with user_key = '{engagement_user_key}'"
            )
        elif len(engagement_dicts) > 1:
            raise UUIDNotFoundException(
                f"Employee with uuid = {employee_uuid} has multiple engagements "
                f"with user_key = '{engagement_user_key}'"
            )
        else:
            engagement = engagement_dicts[0]
            logger.info(f"Match found in engagement with uuid = {engagement['uuid']}")
            return {"uuid": engagement[attribute]}

    async def get_current_org_unit_uuid_dict(
        self, employee_uuid: UUID, engagement_user_key: str
    ) -> dict:
        """
        Returns an existing 'org-unit' object formatted as a dict
        """
        return await self.get_current_engagement_attribute_uuid_dict(
            "org_unit_uuid", employee_uuid, engagement_user_key
        )

    async def get_current_engagement_type_uuid_dict(
        self, employee_uuid: UUID, engagement_user_key: str
    ) -> dict:
        """
        Returns an existing 'engagement type' object formatted as a dict
        """
        return await self.get_current_engagement_attribute_uuid_dict(
            "engagement_type_uuid", employee_uuid, engagement_user_key
        )

    async def get_current_primary_uuid_dict(
        self, employee_uuid: UUID, engagement_user_key: str
    ) -> dict | None:
        """
        Returns an existing 'primary' object formatted as a dict
        """
        primary_dict = await self.get_current_engagement_attribute_uuid_dict(
            "primary_uuid", employee_uuid, engagement_user_key
        )

        if not primary_dict["uuid"]:
            return None
        return primary_dict

    async def get_employee_dict(self, employee_uuid: UUID) -> dict:
        mo_employee = await self.dataloader.load_mo_employee(employee_uuid)
        return mo_employee.dict()

    async def get_primary_engagement_dict(self, employee_uuid: UUID) -> dict:
        engagements = await self.dataloader.load_mo_employee_engagement_dicts(
            employee_uuid
        )
        # TODO: Make is_primary a GraphQL filter in MO and clean this up
        is_primary_engagement = await self.dataloader.is_primaries(
            [engagement["uuid"] for engagement in engagements]
        )
        primary_engagement = one(compress(engagements, is_primary_engagement))
        return primary_engagement

    async def get_or_create_engagement_type_uuid(self, engagement_type: str) -> str:
        if not engagement_type:
            raise UUIDNotFoundException("engagement_type is empty")
        try:
            return self.get_engagement_type_uuid(engagement_type)
        except UUIDNotFoundException:
            uuid = await self.dataloader.create_mo_engagement_type(engagement_type)
            self.engagement_type_info = await self.dataloader.load_mo_engagement_types()
            self.check_info_dicts()
            return str(uuid)

    def get_org_unit_type_uuid(self, org_unit_type: str) -> str:
        return self.get_object_uuid_from_user_key(
            self.org_unit_type_info, org_unit_type
        )

    def get_org_unit_level_uuid(self, org_unit_level: str) -> str:
        return self.get_object_uuid_from_user_key(
            self.org_unit_level_info, org_unit_level
        )

    async def get_employee_address_type_user_key(self, uuid: str) -> str:
        return await self.get_object_user_key_from_uuid(
            "employee_address_type_info", uuid
        )

    async def get_org_unit_address_type_user_key(self, uuid: str) -> str:
        return await self.get_object_user_key_from_uuid(
            "org_unit_address_type_info", uuid
        )

    async def get_it_system_user_key(self, uuid: str) -> str:
        return await self.get_object_user_key_from_uuid("it_system_info", uuid)

    async def get_engagement_type_name(self, uuid: str) -> str:
        return await self.get_object_name_from_uuid("engagement_type_info", uuid)

    async def get_job_function_name(self, uuid: str) -> str:
        return await self.get_object_name_from_uuid("job_function_info", uuid)

    async def get_org_unit_name(self, uuid: str) -> str:
        return await self.get_object_name_from_uuid("org_unit_info", uuid)

    async def create_org_unit(self, org_unit_path_string: str):
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
                await self.get_org_unit_uuid_from_path(partial_path_string)
            except UUIDNotFoundException:
                logger.info(f"Importing {partial_path_string}")

                if nesting_level == 0:
                    parent_uuid = str(await self.dataloader.load_mo_root_org_uuid())
                else:
                    parent_path = org_unit_path[:nesting_level]
                    parent_path_string = self.org_unit_path_string_separator.join(
                        parent_path
                    )
                    parent_uuid = await self.get_org_unit_uuid_from_path(
                        parent_path_string
                    )

                uuid = uuid4()
                name = partial_path[-1]

                # Note: 1902 seems to be the earliest accepted year by OS2mo
                # We pick 1960 because MO's dummy data also starts all organizations
                # in 1960...
                # We just want a very early date here, to avoid that imported employee
                # engagements start before the org-unit existed.
                from_date = datetime(1960, 1, 1).strftime("%Y-%m-%dT00:00:00")
                org_unit = OrganisationUnit.from_simplified_fields(
                    user_key=str(uuid4()),
                    name=name,
                    org_unit_type_uuid=UUID(self.default_org_unit_type_uuid),
                    org_unit_level_uuid=UUID(self.default_org_unit_level_uuid),
                    from_date=from_date,
                    parent_uuid=UUID(parent_uuid) if parent_uuid else None,
                    uuid=uuid,
                )

                await self.dataloader.upload_mo_objects([org_unit])
                self.org_unit_info[str(uuid)] = {
                    "uuid": str(uuid),
                    "name": name,
                    "parent_uuid": parent_uuid,
                }

    async def get_org_unit_uuid_from_path(self, org_unit_path_string: str):
        for info in self.org_unit_info.values():
            clean_name = info["name"].strip()
            if not org_unit_path_string.strip().endswith(clean_name):
                continue
            path_string = await self.get_org_unit_path_string(info["uuid"])
            if path_string == org_unit_path_string:
                return info["uuid"]
        raise UUIDNotFoundException(
            f"'{org_unit_path_string}' not found in self.org_unit_info"
        )

    async def get_org_unit_path_string(self, uuid: str):
        root_org_uuid: str = str(await self.dataloader.load_mo_root_org_uuid())
        org_unit_info = self.org_unit_info[str(uuid)]
        object_name = org_unit_info["name"].strip()
        parent_uuid: str = org_unit_info["parent_uuid"]

        path_string = object_name
        while parent_uuid and parent_uuid != root_org_uuid:
            parent_object_name = self.org_unit_info[parent_uuid]["name"].strip()
            path_string = (
                parent_object_name + self.org_unit_path_string_separator + path_string
            )
            parent_uuid = self.org_unit_info[parent_uuid]["parent_uuid"]

        return path_string

    def make_dn_from_org_unit_path(self, dn: str, org_unit_path_string: str) -> str:
        """
        Makes a new DN based on an org-unit path string and a DN, where the org unit
        structure is parsed as an OU structure in the DN.

        Example
        --------
        >>> dn = "CN=Earthworm Jim,OU=OS2MO,DC=ad,DC=addev"
        >>> new_dn = make_dn_from_org_unit_path(dn,"foo/bar")
        >>> new_dn
        >>> "CN=Earthworm Jim,OU=bar,OU=foo,DC=ad,DC=addev"
        """
        sep = self.org_unit_path_string_separator
        org_units = org_unit_path_string.split(sep)[::-1]
        new_ou = ",".join([f"OU={org_unit.strip()}" for org_unit in org_units])
        return exchange_ou_in_dn(dn, new_ou)

    def clean_org_unit_path_string(self, org_unit_path_string: str) -> str:
        """
        Cleans leading and trailing whitespace from org units in an org unit path string

        Example
        ----------
        >>> org_unit_path_string = "foo / bar"
        >>> clean_org_unit_path_string(org_unit_path_string)
        >>> "foo/bar"
        """
        sep = self.org_unit_path_string_separator
        return sep.join([s.strip() for s in org_unit_path_string.split(sep)])

    def org_unit_path_string_from_dn(self, dn, number_of_ous_to_ignore=0) -> str:
        """
        Constructs an org-unit path string from a DN.

        If number_of_ous_to_ignore is specified, ignores this many OUs in the path

        Examples
        -----------
        >>> dn = "CN=Jim,OU=Technicians,OU=Users,OU=demo,OU=OS2MO,DC=ad,DC=addev"
        >>> org_unit_path_string_from_dn(dn,2)
        >>> "Users/Technicians
        >>>
        >>> org_unit_path_string_from_dn(dn,1)
        >>> "demo/Users/Technicians
        """
        ou_decomposed = parse_dn(extract_ou_from_dn(dn))[::-1]
        sep = self.org_unit_path_string_separator
        org_unit_list = [ou[1] for ou in ou_decomposed]

        if number_of_ous_to_ignore >= len(org_unit_list):
            logger.info(
                "[Org-unit-path-string-from-dn] DN cannot be mapped to org-unit-path.",
                dn=dn,
                org_unit_list=org_unit_list,
                number_of_ous_to_ignore=number_of_ous_to_ignore,
            )
            return ""
        org_unit_path_string = sep.join(org_unit_list[number_of_ous_to_ignore:])

        logger.info(
            "[Org-unit-path-string-from-dn] Constructed org unit path string from dn.",
            dn=dn,
            org_unit_path_string=org_unit_path_string,
            number_of_ous_to_ignore=number_of_ous_to_ignore,
        )
        return org_unit_path_string

    async def get_or_create_org_unit_uuid(self, org_unit_path_string: str):
        logger.info(
            "[Get-or-create-org-unit-uuid] Finding org-unit uuid.",
            org_unit_path_string=org_unit_path_string,
        )

        if not org_unit_path_string:
            raise UUIDNotFoundException("Organization unit string is empty")

        # Clean leading and trailing whitespace from org unit path string
        org_unit_path_string = self.clean_org_unit_path_string(org_unit_path_string)

        try:
            return await self.get_org_unit_uuid_from_path(org_unit_path_string)
        except UUIDNotFoundException:
            logger.info(
                f"Could not find '{org_unit_path_string}'. " "Creating organisation."
            )
            await self.create_org_unit(org_unit_path_string)
            return await self.get_org_unit_uuid_from_path(org_unit_path_string)

    @staticmethod
    def str_to_dict(text):
        """
        Converts a string to a dictionary
        """
        return json.loads(text.replace("'", '"').replace("Undefined", "null"))

    @staticmethod
    def min(a, b):
        if a is None:
            return b
        if b is None:
            return a
        if a < b:
            return a
        return b

    def _populate_mapping_with_templates(
        self, mapping: dict[str, Any], environment: Environment
    ):
        globals_dict = {
            "now": datetime.utcnow,
            "min": self.min,
            "nonejoin": self.nonejoin,
            "nonejoin_orgs": self.nonejoin_orgs,
            "remove_first_org": self.remove_first_org,
            "get_employee_address_type_uuid": self.get_employee_address_type_uuid,
            "get_org_unit_address_type_uuid": self.get_org_unit_address_type_uuid,
            "get_it_system_uuid": self.get_it_system_uuid,
            "get_or_create_org_unit_uuid": self.get_or_create_org_unit_uuid,
            "org_unit_path_string_from_dn": self.org_unit_path_string_from_dn,
            "get_job_function_uuid": self.get_job_function_uuid,
            "get_visibility_uuid": self.get_visibility_uuid,
            "get_primary_type_uuid": self.get_primary_type_uuid,
            "get_engagement_type_uuid": self.get_engagement_type_uuid,
            "uuid4": uuid4,
            "get_org_unit_path_string": self.get_org_unit_path_string,
            "make_dn_from_org_unit_path": self.make_dn_from_org_unit_path,
            "get_engagement_type_name": self.get_engagement_type_name,
            "get_job_function_name": self.get_job_function_name,
            "get_org_unit_name": self.get_org_unit_name,
            "get_or_create_job_function_uuid": self.get_or_create_job_function_uuid,
            "get_or_create_engagement_type_uuid": (
                self.get_or_create_engagement_type_uuid
            ),
            "get_current_org_unit_uuid_dict": self.get_current_org_unit_uuid_dict,
            "get_current_engagement_type_uuid_dict": (
                self.get_current_engagement_type_uuid_dict
            ),
            "get_current_primary_uuid_dict": self.get_current_primary_uuid_dict,
            "get_primary_engagement_dict": self.get_primary_engagement_dict,
            "get_employee_dict": self.get_employee_dict,
        }
        for key, value in mapping.items():
            if isinstance(value, str):
                mapping[key] = environment.from_string(value)
                mapping[key].globals.update(globals_dict)
            elif isinstance(value, dict):
                mapping[key] = self._populate_mapping_with_templates(value, environment)
        return mapping

    async def to_ldap(self, mo_object_dict: dict, json_key: str, dn: str) -> LdapObject:
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

        # Globals
        mo_object_dict["dn"] = dn

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
            rendered_item = await template.render_async(mo_object_dict)
            if rendered_item:
                ldap_object[ldap_field_name] = rendered_item

        if "dn" not in ldap_object:
            ldap_object["dn"] = dn

        return LdapObject(**ldap_object)

    def get_number_of_entries(self, ldap_object: LdapObject):
        """
        Returns the number of data entries in an LDAP object. It is possible for a
        single LDAP field to contain multiple values. This function determines
        if that is the case.
        """

        def is_list(x: Any) -> bool:
            return isinstance(x, list)

        values = ldap_object.dict().values()
        list_values = filter(is_list, values)
        list_lengths = map(len, list_values)
        return max(list_lengths, default=1)

    async def from_ldap(
        self,
        ldap_object: LdapObject,
        json_key: str,
        employee_uuid: UUID,
        engagement_uuid: UUID | None = None,
    ) -> Any:
        """
        uuid : UUID
            Uuid of the employee whom this object belongs to. If None: Generates a new
            uuid
        engagement_uuid: UUID
            Engagement UUID to use when creating `Address` and `ITUser` instances.
        """

        # This is how many MO objects we need to return - a MO object can have only
        # One value per field. Not multiple. LDAP objects however, can have multiple
        # values per field.
        number_of_entries = self.get_number_of_entries(ldap_object)

        converted_objects = []
        for entry in range(number_of_entries):
            ldap_dict: CaseInsensitiveDict = CaseInsensitiveDict(
                {
                    key: (
                        value[min(entry, len(value) - 1)]
                        if isinstance(value, list) and len(value) > 0
                        else value
                    )
                    for key, value in ldap_object.dict().items()
                }
            )
            context = {
                "ldap": ldap_dict,
                "employee_uuid": str(employee_uuid),
                "engagement_uuid": str(engagement_uuid) if engagement_uuid else None,
            }
            try:
                mapping = self.mapping["ldap_to_mo"]
            except KeyError:
                raise IncorrectMapping("Missing mapping 'ldap_to_mo'")
            try:
                object_mapping = mapping[json_key]
            except KeyError:
                raise IncorrectMapping(f"Missing '{json_key}' in mapping 'ldap_to_mo'")

            async def render_template(template):
                try:
                    value = (await template.render_async(context)).strip()

                    # Sloppy mapping can lead to the following rendered strings:
                    # - {{ldap.mail or None}} renders as "None"
                    # - {{ldap.mail}} renders as "[]" if ldap.mail is empty
                    #
                    # Mapping with {{ldap.mail or NONE}} solves both, but let's check
                    # for "none" or "[]" strings anyway to be more robust.
                    if value.lower() == "none" or value == "[]":
                        value = ""
                except UUIDNotFoundException as e:
                    logger.warning(e)
                    return None
                # TODO: Is it possible to render a dictionary directly?
                #       Instead of converting from a string
                if "{" in value and ":" in value and "}" in value:
                    try:
                        value = self.str_to_dict(value)
                    except JSONDecodeError:
                        raise IncorrectMapping(
                            f"Could not convert {value} in "
                            f"{json_key}['{mo_field_name}'] to dict "
                            f"(context={context!r})"
                        )
                return value

            mo_dict = {}
            for mo_field_name, template in object_mapping.items():
                value = await render_template(template)
                if value:
                    mo_dict[mo_field_name] = value

            mo_class: Any = self.import_mo_object_class(json_key)
            required_attributes = set(self.get_required_attributes(mo_class))

            # If any required attributes are missing
            missing_attributes = required_attributes - set(mo_dict.keys())
            if missing_attributes:
                logger.info(
                    f"Could not convert {mo_dict} to {mo_class}. "
                    f"The following attributes are missing: {missing_attributes}"
                )
                continue

            # If requested to terminate, we generate and return a termination subclass
            # instead of the original class. This is to ensure we can forward the termination date,
            # without having to modify the RAModel.
            if "_terminate_" in mo_dict:

                class Termination(mo_class):
                    terminate_: str

                mo_dict["terminate_"] = mo_dict.pop("_terminate_")
                mo_class = Termination

            try:
                converted_objects.append(mo_class(**mo_dict))
            except pydantic.ValidationError as pve:
                logger.info(pve)

        return converted_objects
