# SPDX-FileCopyrightText: 2021 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
from enum import Enum

from pydantic import BaseModel
from pydantic import EmailStr
from pydantic import Extra
from typing import Set
from uuid import UUID

from mora.mapping import ADMIN
from mora.mapping import OWNER


class Roles(str, Enum):
    admin = ADMIN
    owner = OWNER


class RealmAccess(BaseModel):
    roles: Set[Roles] = set()


class Token(BaseModel):
    email: EmailStr
    preferred_username: str
    realm_access: RealmAccess = RealmAccess(roles=set())
    uuid: UUID

    class Config:
        extra = Extra.ignore
