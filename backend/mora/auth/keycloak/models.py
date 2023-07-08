# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import binascii
from base64 import b64decode
from contextlib import suppress
from typing import Any
from uuid import UUID

from pydantic import BaseModel
from pydantic import EmailStr
from pydantic import Extra
from pydantic import validator


class RealmAccess(BaseModel):
    roles: set[str] = set()


class Token(BaseModel):
    azp: str
    email: EmailStr | None
    preferred_username: str | None
    realm_access: RealmAccess = RealmAccess(roles=set())
    uuid: UUID | None

    @validator("uuid", pre=True)
    def parse_base64_uuid(cls, uuid: Any) -> UUID | None:
        """Attempt to parse incoming UUID as base64"""
        if uuid is not None:
            with suppress(TypeError, ValueError, binascii.Error):
                uuid = UUID(bytes_le=b64decode(uuid))
        return uuid

    class Config:
        extra = Extra.ignore
