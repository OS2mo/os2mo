# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from collections.abc import AsyncIterator
from collections.abc import Iterable
from collections.abc import Sequence
from typing import Any

from fastapi import APIRouter
from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder
from graphql.error import GraphQLError
from starlette.responses import PlainTextResponse
from strawberry import Schema
from strawberry.custom_scalar import ScalarDefinition
from strawberry.custom_scalar import ScalarWrapper
from strawberry.exceptions import StrawberryGraphQLError
from strawberry.extensions import SchemaExtension
from strawberry.extensions.tracing import SentryTracingExtension
from strawberry.printer import print_schema
from strawberry.schema.config import StrawberryConfig

from mora.graphapi.middleware import StarletteContextExtension
from mora.graphapi.router import CustomGraphQLRouter


def add_exception_extension(error: GraphQLError) -> StrawberryGraphQLError:
    extensions = {}
    if isinstance(error.original_error, HTTPException):
        extensions["error_context"] = jsonable_encoder(error.original_error.detail)

    return StrawberryGraphQLError(
        extensions=extensions,
        nodes=error.nodes,
        source=error.source,
        positions=error.positions,
        path=error.path,
        original_error=error.original_error,
        message=error.message,
    )


class ExtendedErrorFormatExtension(SchemaExtension):
    async def on_operation(self) -> AsyncIterator[None]:
        yield
        result = self.execution_context.result
        if result and hasattr(result, "errors") and result.errors is not None:
            result.errors = list(map(add_exception_extension, result.errors))


class BaseGraphQLSchema:
    """Base GraphQL Schema wrapper with MO defaults.

    Type definitions are mostly copied from Strawberry. We cannot simply inherit from
    the Strawberry class, as its configuration is passed at init-time, whereas this
    wrapper allows for import-time definitions.
    """

    query: type
    mutation: type

    types: Iterable = ()

    extensions: Sequence[type[SchemaExtension] | SchemaExtension] = [
        StarletteContextExtension,
        SentryTracingExtension,
        ExtendedErrorFormatExtension,
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
    def get_router(cls, is_latest: bool) -> APIRouter:
        """Get Strawberry FastAPI router serving this GraphQL API version."""
        router = CustomGraphQLRouter(
            is_latest=is_latest,
            schema=cls.schema.get(),
            context_getter=cls.get_context,
        )

        @router.get("/schema.graphql", response_class=PlainTextResponse)
        async def schema() -> str:
            """Return the GraphQL version's schema definition in SDL format."""
            return print_schema(cls.schema.get())

        return router
