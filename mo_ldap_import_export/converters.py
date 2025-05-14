# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import json
from json.decoder import JSONDecodeError
from typing import Any

import pydantic
import structlog
from fastramqpi.ramqp.utils import RequeueMessage
from ldap3.utils.ciDict import CaseInsensitiveDict
from more_itertools import one

from .config import LDAP2MOMapping
from .config import Settings
from .config import get_required_attributes
from .dataloaders import DataLoader
from .exceptions import IncorrectMapping
from .ldap_classes import LdapObject
from .models import MOBase
from .models import Termination
from .utils import is_list
from .utils import mo_today

logger = structlog.stdlib.get_logger()


class LdapConverter:
    def __init__(self, settings: Settings, dataloader: DataLoader) -> None:
        self.settings = settings
        self.dataloader = dataloader
        from .environments import construct_environment

        self.environment = construct_environment(self.settings, self.dataloader)

    @staticmethod
    def str_to_dict(text):
        """
        Converts a string to a dictionary
        """
        return json.loads(text.replace("'", '"').replace("Undefined", "null"))

    def get_number_of_entries(self, ldap_object: LdapObject) -> int:
        """Returns the maximum cardinality of data fields within an LdapObject.

        If a given data field has multiple values it will be a list within the
        ldap_object, we wish to find the length of the longest list.

        Non list data fields will be interpreted as having length 1.

        Args:
            ldap_object: The object to find the maximum cardinality within.

        Returns:
            The maximum cardinality contained within ldap_object.
            Will always return atleast 1 as the ldap_object always contains a DN.
        """

        def ldap_field2cardinality(value: Any) -> int:
            if isinstance(value, list):
                return len(value)
            return 1

        values = ldap_object.dict().values()
        cardinality_values = map(ldap_field2cardinality, values)
        return max(cardinality_values)

    async def from_ldap(
        self,
        ldap_object: LdapObject,
        mapping: LDAP2MOMapping,
        template_context: dict[str, Any],
    ) -> list[MOBase | Termination]:
        # This is how many MO objects we need to return - a MO object can have only
        # One value per field. Not multiple. LDAP objects however, can have multiple
        # values per field.
        number_of_entries = self.get_number_of_entries(ldap_object)
        if number_of_entries != 1:  # pragma: no cover
            raise RequeueMessage("Unable to handle list attributes")

        converted_objects: list[MOBase | Termination] = []
        ldap_dict: CaseInsensitiveDict = CaseInsensitiveDict(
            {
                key: (one(value) if is_list(value) and len(value) > 0 else value)
                for key, value in ldap_object.dict().items()
            }
        )
        context = {
            "ldap": ldap_dict,
            **template_context,
        }

        async def render_template(
            field_name: str, template_str: str, context: dict[str, Any]
        ) -> Any:
            template = self.environment.from_string(template_str)
            value = (await template.render_async(context)).strip()

            # Sloppy mapping can lead to the following rendered strings:
            # - {{ldap.mail or None}} renders as "None"
            # - {{ldap.mail}} renders as "[]" if ldap.mail is empty
            #
            # Mapping with {{ldap.mail or ''}} solves both, but let's check
            # for "none" or "[]" strings anyway to be more robust.
            if value.lower() == "none" or value == "[]":
                value = ""

            # TODO: Is it possible to render a dictionary directly?
            #       Instead of converting from a string
            if "{" in value and ":" in value and "}" in value:
                try:
                    value = self.str_to_dict(value)
                except JSONDecodeError as error:
                    error_string = f"Could not convert {value} in '{field_name}' to dict (context={context!r})"
                    raise IncorrectMapping(error_string) from error
            return value

        # TODO: asyncio.gather this for future dataloader bulking
        mo_class = mapping.as_mo_class()
        mo_dict = {
            mo_field_name: await render_template(mo_field_name, template_str, context)
            for mo_field_name, template_str in mapping.get_fields().items()
        }
        if mo_dict.get("_terminate_"):
            # TODO: Convert this to pydantic check
            assert "uuid" in mo_dict, "UUID must be set if _terminate_ is set"
            # Asked to terminate, but uuid template did not return an uuid, i.e.
            # there was no object to actually terminate, so we just skip it.
            if not mo_dict["uuid"]:
                logger.info("Requested termination with no UUID, skipping")
                return []
            converted_objects.append(
                Termination(
                    mo_class=mo_class,
                    at=mo_dict["_terminate_"],
                    uuid=mo_dict["uuid"],
                )
            )
            return converted_objects

        required_attributes = get_required_attributes(mo_class)

        # Load our validity default, if it is not set
        if "validity" in required_attributes:
            assert "validity" not in mo_dict, "validity disallowed in ldap2mo mappings"
            mo_dict["validity"] = {
                "from": mo_today(),
                "to": None,
            }

        # If any required attributes are missing
        missing_attributes = required_attributes - set(mo_dict.keys())
        # TODO: Restructure this so rejection happens during parsing?
        if missing_attributes:  # pragma: no cover
            logger.info(
                "Missing attributes in dict to model conversion",
                mo_dict=mo_dict,
                mo_class=mo_class,
                missing_attributes=missing_attributes,
            )
            raise ValueError("Missing attributes in dict to model conversion")

        # Remove empty values
        mo_dict = {key: value for key, value in mo_dict.items() if value}
        # If any required attributes are missing
        missing_attributes = required_attributes - set(mo_dict.keys())
        if missing_attributes:  # pragma: no cover
            logger.info(
                "Missing values in LDAP to synchronize, skipping",
                mo_dict=mo_dict,
                mo_class=mo_class,
                missing_attributes=missing_attributes,
            )
            return []

        try:
            converted_objects.append(mo_class(**mo_dict))
        except pydantic.ValidationError:
            logger.info("Exception during object parsing", exc_info=True)

        return converted_objects
