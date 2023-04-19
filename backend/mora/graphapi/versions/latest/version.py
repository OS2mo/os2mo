# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from collections.abc import Awaitable
from collections.abc import Callable
from typing import Any

import strawberry
from fastapi import Depends
from pydantic import PositiveInt

from ..base import BaseGraphQLSchema
from ..base import BaseGraphQLVersion
from .dataloaders import get_loaders
from .files import get_filestorage
from .mutators import Mutation
from .query import Query
from .types import CPRType
from mora.auth.keycloak.models import Token
from mora.auth.keycloak.oidc import token_getter
from mora.db import get_sessionmaker
from mora.util import CPR
from oio_rest.config import get_settings as lora_get_settings
from oio_rest.db import _get_dbname


class LatestGraphQLSchema(BaseGraphQLSchema):
    """Latest GraphQL Schema."""

    query = Query
    mutation = Mutation

    scalar_overrides = {
        CPR: CPRType,
        PositiveInt: strawberry.scalar(int),
    }


class LatestGraphQLVersion(BaseGraphQLVersion):
    """Latest GraphQL API version.

    The latest version is never explicitly versioned or exposed directly. Clients should
    always refer and pin themselves to a specific version, which is available as the
    latest `vN` version package, inheriting from this class without modifications.
    When a new breaking change must be introduced to the GraphQL schema, the change is
    made in `latest` and the `vN` package is changed to be an adapter which maintains
    backwards-compatibility. A new `vN+1` package is created to expose latest.

    As an example, see the merge request for the first breaking change:
    https://git.magenta.dk/rammearkitektur/os2mo/-/merge_requests/1184
    """

    schema = LatestGraphQLSchema

    @classmethod
    async def get_context(
        cls, get_token: Callable[[], Awaitable[Token]] = Depends(token_getter)
    ) -> dict[str, Any]:
        lora_settings = lora_get_settings()
        sessionmaker = get_sessionmaker(
            user=lora_settings.db_user,
            password=lora_settings.db_password,
            host=lora_settings.db_host,
            name=_get_dbname(),
        )
        return {
            **await super().get_context(),
            **await get_loaders(),
            "get_token": get_token,
            "filestorage": get_filestorage(),
            "sessionmaker": sessionmaker,
        }
