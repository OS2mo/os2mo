# SPDX-FileCopyrightText: 2022 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from collections.abc import Awaitable
from collections.abc import Callable
from typing import Any

from fastapi import Depends

from ..base import BaseGraphQLSchema
from ..base import BaseGraphQLVersion
from .dataloaders import get_loaders
from .files import get_filestorage
from .mutators import Mutation
from .query import Query
from .types import CPRType
from mora.auth.keycloak.models import Token
from mora.auth.keycloak.oidc import token_getter
from mora.util import CPR


class LatestGraphQLSchema(BaseGraphQLSchema):
    """Latest GraphQL Schema."""

    query = Query
    mutation = Mutation

    scalar_overrides = {
        CPR: CPRType,
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
        return {
            **await super().get_context(),
            **await get_loaders(),
            "get_token": get_token,
            "filestorage": get_filestorage(),
        }
