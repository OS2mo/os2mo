# SPDX-FileCopyrightText: 2021 Magenta ApS
# SPDX-License-Identifier: MPL-2.0

from pydantic import BaseModel
from pydantic import EmailStr
from pydantic import Extra
from pydantic import root_validator
from typing import Any
from typing import Dict
from typing import Optional
from typing import Set
from uuid import UUID

from mora import config

settings = config.get_settings()


class RealmAccess(BaseModel):
    roles: Set[str] = set()


class KeycloakToken(BaseModel):
    azp: str
    email: Optional[EmailStr]
    preferred_username: Optional[str]
    realm_access: RealmAccess = RealmAccess(roles=set())
    uuid: Optional[UUID]

    @root_validator
    def uuid_attribute_required_for_mo_client(
        cls, values: Dict[str, Any]
    ) -> Dict[str, Any]:
        if (
            settings.keycloak_rbac_enabled and
            values.get("azp") == settings.keycloak_mo_client and
            values.get("uuid") is None
        ):
            raise ValueError(
                'The uuid user attribute is missing in the token'
            )
        return values

    class Config:
        extra = Extra.ignore

# TODO: Remove the stuff below, once a proper auth solution is in place,
#  that works for local DIPEX development.
#  https://redmine.magenta-aps.dk/issues/44020


class NoAuthToken(BaseModel):
    pass


Token = KeycloakToken
if not settings.os2mo_auth:
    Token = NoAuthToken
