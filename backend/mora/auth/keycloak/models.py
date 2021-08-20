# SPDX-FileCopyrightText: 2021 Magenta ApS
# SPDX-License-Identifier: MPL-2.0

from pydantic import BaseModel
from pydantic import MissingError
from pydantic import ValidationError
from pydantic import EmailStr
from pydantic import Extra
from pydantic import root_validator
from pydantic.error_wrappers import ErrorWrapper
from typing import Any
from typing import Dict
from typing import Optional
from typing import Set
from uuid import UUID

from mora import config

settings = config.get_settings()


class RealmAccess(BaseModel):
    roles: Set[str] = set()


class Token(BaseModel):
    azp: str
    email: Optional[EmailStr]
    preferred_username: Optional[str]
    realm_access: RealmAccess = RealmAccess(roles=set())
    uuid: UUID = None

    @root_validator
    def uuid_attribute_required_for_mo_client(
        cls, values: Dict[str, Any]
    ) -> Dict[str, Any]:
        if values.get("azp") == settings.keycloak_mo_client:
            if values["uuid"] is None:
                raise ValidationError(
                    errors=[ErrorWrapper(MissingError(), loc='uuid')],
                    model=Token
                )
        return values

    class Config:
        extra = Extra.ignore
