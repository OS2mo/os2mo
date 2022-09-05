# SPDX-FileCopyrightText: 2021 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from typing import Any

import strawberry
from fastapi import Depends
from mora.graphapi.dataloaders import get_loaders
from mora.graphapi.files import get_filestorage
from mora.graphapi.middleware import StarletteContextExtension
from mora.graphapi.mutators import Mutation
from mora.graphapi.types import CPRType
from strawberry.fastapi import GraphQLRouter
from strawberry.schema.config import StrawberryConfig

from mora.auth.keycloak.models import Token
from mora.auth.keycloak.oidc import auth
from mora.util import CPR


def get_schema() -> strawberry.Schema:
    schema = strawberry.Schema(
        query=Query,
        mutation=Mutation,
        # Automatic camelCasing disabled because under_score style is simply better
        #
        # See: An Eye Tracking Study on camelCase and under_score Identifier Styles
        # Excerpt:
        #   Although, no difference was found between identifier styles with respect
        #   to accuracy, results indicate a significant improvement in time and lower
        #   visual effort with the underscore style.
        #
        # Additionally it preserves the naming of the underlying Python functions.
        config=StrawberryConfig(auto_camel_case=False),
        # https://strawberry.rocks/docs/integrations/pydantic#classes-with-__get_validators__
        scalar_overrides={
            CPR: CPRType,  # type: ignore
        },
        extensions=[
            StarletteContextExtension,
        ],
    )
    return schema


async def get_context(token: Token = Depends(auth)) -> dict[str, Any]:
    loaders = await get_loaders()
    return {**loaders, "token": token, "filestorage": get_filestorage()}
