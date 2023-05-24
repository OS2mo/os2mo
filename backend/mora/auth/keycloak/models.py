# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import binascii
from base64 import b64decode
from contextlib import suppress
from uuid import UUID

from os2mo_fastapi_utils.auth.models import Token as BaseToken
from pydantic import Extra
from pydantic import validator


class KeycloakToken(BaseToken):
    @validator("uuid", pre=True)
    def parse_base64_uuid(cls, uuid):
        """Attempt to parse incoming UUID as base64"""
        if uuid is not None:
            with suppress(ValueError, binascii.Error):
                uuid = UUID(bytes_le=b64decode(uuid))
        return uuid

    class Config:
        extra = Extra.ignore


Token = KeycloakToken
