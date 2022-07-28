# SPDX-FileCopyrightText: 2021 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from typing import Any

import strawberry
from strawberry.fastapi import GraphQLRouter
from strawberry.schema.config import StrawberryConfig

from mora.util import CPR
from .dataloaders import get_loaders
from .mutation import Mutation
from .query import Query
from .types import CPRType
from ...middleware import StarletteContextExtension
from ...version import GraphQLVersion


async def get_context() -> dict[str, Any]:
    loaders = await get_loaders()
    return {**loaders}


def get_version(enable_graphiql: bool, **kwargs: Any) -> GraphQLVersion:
    router = GraphQLRouter(
        get_schema(), context_getter=get_context, graphiql=enable_graphiql
    )

    version = GraphQLVersion(
        version=3,
        router=router,
        deprecation_date=None,
    )

    return version


def get_schema() -> strawberry.Schema:  # TODO!
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
