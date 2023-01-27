# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from collections.abc import Iterable
from collections.abc import Sequence
from typing import Any

from fastapi import APIRouter
from strawberry import Schema
from strawberry.custom_scalar import ScalarDefinition
from strawberry.custom_scalar import ScalarWrapper
from strawberry.extensions import Extension
from strawberry.schema.config import StrawberryConfig

from mora.graphapi.middleware import StarletteContextExtension
from mora.graphapi.router import CustomGraphQLRouter


class BaseGraphQLSchema:
    """Base GraphQL Schema wrapper with MO defaults.

    Type definitions are mostly copied from Strawberry. We cannot simply inherit from
    the Strawberry class, as its configuration is passed at init-time, whereas this
    wrapper allows for import-time definitions.
    """

    query: type
    mutation: type | None = None

    types: Iterable = ()

    extensions: Sequence[type[Extension] | Extension] = [
        StarletteContextExtension,
    ]

    # Automatic camelCasing disabled because under_score style is simply better
    #
    # See: An Eye Tracking Study on camelCase and under_score Identifier Styles
    # Excerpt:
    #   Although, no difference was found between identifier styles with respect
    #   to accuracy, results indicate a significant improvement in time and lower
    #   visual effort with the underscore style.
    #
    # Additionally, it preserves the naming of the underlying Python functions.
    config: StrawberryConfig | None = StrawberryConfig(auto_camel_case=False)

    scalar_overrides: dict[
        object, ScalarWrapper | ScalarDefinition | type
    ] | None = None

    @classmethod
    def get(cls) -> Schema:
        """Instantiate Strawberry Schema."""
        return Schema(
            query=cls.query,
            mutation=cls.mutation,
            types=cls.types,
            extensions=cls.extensions,
            config=cls.config,
            scalar_overrides=cls.scalar_overrides,
        )


class BaseGraphQLVersion:
    """Base container for a versioned GraphQL API."""

    version: int
    schema: type[BaseGraphQLSchema]

    @classmethod
    async def get_context(cls) -> dict[str, Any]:
        """Strawberry context getter."""
        return {}

    @classmethod
    def get_router(cls, **kwargs: Any) -> APIRouter:
        """Get Strawberry FastAPI router serving this GraphQL API version."""
        params = dict(
            schema=cls.schema.get(),
            path=f"/v{cls.version}",
            context_getter=cls.get_context,
        )
        params.update(kwargs)  # allows overriding values
        return CustomGraphQLRouter(**params)  # type: ignore
