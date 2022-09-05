# SPDX-FileCopyrightText: 2022 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0

from typing import Any

from fastapi import Depends

from mora.auth.keycloak.models import Token
from mora.auth.keycloak.oidc import auth
from mora.util import CPR
from .dataloaders import get_loaders
from .files import get_filestorage
from .mutators import Mutation
from .query import Query
from ..base import BaseGraphQLSchema
from ..base import BaseGraphQLVersion


class LatestGraphQLSchema(BaseGraphQLSchema):
    """Latest GraphQL Schema."""

    query = Query
    mutation = Mutation

    scalar_overrides = {
        CPR: CPRType,  # type: ignore
    }


class LatestGraphQLVersion(BaseGraphQLVersion):
    """Latest GraphQL API version.

    The latest version is never explicitly versioned or exposed directly. Clients should
    always refer and pin themselves to a specific version, which is available as the
    latest `vX` version package, inheriting from this class without modifications.
    When a new breaking change must be introduced to the GraphQL schema, the change is
    made in `latest` and the `vX` package is changed to be an adapter which maintains
    backwards-compatibility. A new `vX+1` package is created to expose latest.
    """

    schema = LatestGraphQLSchema

    @classmethod
    async def get_context(
        cls, token: Token = Depends(auth), **kwargs: Any
    ) -> dict[str, Any]:
        return {
            **await super().get_context(**kwargs),
            **await get_loaders(),
            "token": token,
            "filestorage": get_filestorage(),
        }
