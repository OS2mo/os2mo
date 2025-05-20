# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import json
from json.decoder import JSONDecodeError
from typing import Any

import pydantic
import structlog
from fastramqpi.ramqp.utils import RequeueMessage
from more_itertools import one

from .config import LDAP2MOMapping
from .config import Settings
from .config import get_required_attributes
from .dataloaders import DataLoader
from .environments import construct_environment
from .exceptions import IncorrectMapping
from .exceptions import SkipObject
from .ldap_classes import LdapObject
from .models import MOBase
from .models import Termination
from .utils import is_list
from .utils import mo_today

logger = structlog.stdlib.get_logger()


class LdapConverter:
    def __init__(self, settings: Settings, dataloader: DataLoader) -> None:
        self.environment = construct_environment(settings, dataloader)

    @staticmethod
    def str_to_dict(text):
        """
        Converts a string to a dictionary
        """
        return json.loads(text.replace("'", '"').replace("Undefined", "null"))

    async def render_template(
        self, field_name: str, template_str: str, context: dict[str, Any]
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

    async def from_ldap(
        self,
        ldap_object: LdapObject,
        mapping: LDAP2MOMapping,
        template_context: dict[str, Any],
    ) -> MOBase | Termination:
        def convert_value(value: Any) -> Any:
            if not is_list(value):
                return value
            if not value:
                return value
            # We can only handle single element lists
            too_long = RequeueMessage("Unable to handle list attributes")
            return one(value, too_long=too_long)

        ldap_dict = {
            key: convert_value(value) for key, value in ldap_object.dict().items()
        }
        context = {"ldap": ldap_dict, **template_context}

        mo_class = mapping.as_mo_class()

        # Handle termination
        if mapping.terminate:
            terminate_template = mapping.terminate
            terminate = await self.render_template(
                "_terminate_", terminate_template, context
            )
            if terminate:
                # Pydantic validator ensures that uuid is set here
                assert hasattr(mapping, "uuid")
                uuid_template = mapping.uuid
                assert uuid_template is not None

                uuid = await self.render_template("uuid", uuid_template, context)
                # Asked to terminate, but uuid template did not return an uuid, i.e.
                # there was no object to actually terminate, so we just skip it.
                if not uuid:
                    message = "Unable to terminate without UUID"
                    logger.info(message)
                    raise SkipObject(message)
                return Termination(mo_class=mo_class, at=terminate, uuid=uuid)

        # TODO: asyncio.gather this for future dataloader bulking
        mo_dict = {
            mo_field_name: await self.render_template(
                mo_field_name, template_str, context
            )
            for mo_field_name, template_str in mapping.get_fields().items()
        }

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
                "Missing values in LDAP to synchronize",
                mo_dict=mo_dict,
                mo_class=mo_class,
                missing_attributes=missing_attributes,
            )
            raise RequeueMessage("Missing values in LDAP to synchronize")

        try:
            return mo_class(**mo_dict)
        except pydantic.ValidationError:
            logger.info("Exception during object parsing", exc_info=True)
            raise
