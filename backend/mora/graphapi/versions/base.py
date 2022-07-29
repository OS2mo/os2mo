# SPDX-FileCopyrightText: 2021 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from datetime import date
from typing import Any
from typing import Dict
from typing import Optional
from typing import Sequence
from typing import Type
from typing import Union

from fastapi import APIRouter
from strawberry import Schema
from strawberry.custom_scalar import ScalarDefinition
from strawberry.custom_scalar import ScalarWrapper
from strawberry.extensions import Extension
from strawberry.fastapi import GraphQLRouter
from strawberry.schema.config import StrawberryConfig

from mora.graphapi.middleware import StarletteContextExtension


class BaseGraphQLSchema:
    """TODO."""

    query: Type
    mutation: Optional[Type] = None

    # Automatic camelCasing disabled because under_score style is simply better
    #
    # See: An Eye Tracking Study on camelCase and under_score Identifier Styles
    # Excerpt:
    #   Although, no difference was found between identifier styles with respect
    #   to accuracy, results indicate a significant improvement in time and lower
    #   visual effort with the underscore style.
    #
    # Additionally, it preserves the naming of the underlying Python functions.
    config: Optional[StrawberryConfig] = StrawberryConfig(auto_camel_case=False)

    scalar_overrides: Optional[
        Dict[object, Union[ScalarWrapper, ScalarDefinition]]
    ] = None

    extensions: Sequence[Union[Type[Extension], Extension]] = [
        StarletteContextExtension,
    ]

    @classmethod
    def get(cls) -> Schema:
        """TODO."""
        return Schema(
            query=cls.query,
            mutation=cls.mutation,
            config=cls.config,
            scalar_overrides=cls.scalar_overrides,
            extensions=cls.extensions,
        )


class BaseGraphQLVersion:
    """TODO."""

    version: int
    deprecation_date: Optional[date] = None
    schema: BaseGraphQLSchema

    @classmethod
    async def get_context(cls) -> dict[str, Any]:
        """TODO."""
        return {}

    @classmethod
    def get_router(cls, **kwargs: Any) -> APIRouter:
        """TODO."""
        params = dict(
            schema=cls.schema.get(),
            path=f"/v{cls.version}",
            context_getter=cls.get_context,
        )
        params.update(kwargs)
        return GraphQLRouter(**params)
