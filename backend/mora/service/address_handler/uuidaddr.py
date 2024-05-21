# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import re
import uuid

from . import base
from ... import exceptions
from ..validation.validator import forceable


class UUIDAddressHandler(base.AddressHandler):
    scope = "UUID"
    prefix = "urn:magenta.dk:uuid:"

    @staticmethod
    @forceable
    async def validate_value(value):
        """Make sure *value* is a valid UUID.

        This is a bit trickier than it sounds, because we want all UUIDs to
        look alike. This means we must check that:
        * there are hyphens,
        * there is no URN prefix, and
        * there are no curly braces.
        """
        if not re.match(
            r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", value
        ):
            exceptions.ErrorCodes.V_INVALID_ADDRESS_UUID(value=value)

        try:
            uuid.UUID(value)
        except ValueError:
            exceptions.ErrorCodes.V_INVALID_ADDRESS_UUID(value=value)
