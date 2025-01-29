# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import traceback
from collections.abc import AsyncIterator
from collections.abc import Iterable
from collections.abc import Sequence
from contextlib import suppress
from functools import cache
from textwrap import dedent
from typing import Any

from fastapi import APIRouter
from fastapi.encoders import jsonable_encoder
from graphql import ExecutionResult
from graphql.error import GraphQLError
from starlette.responses import PlainTextResponse
from strawberry import Schema
from strawberry.exceptions import StrawberryGraphQLError
from strawberry.extensions import SchemaExtension
from strawberry.printer import print_schema
from strawberry.schema.config import StrawberryConfig
from strawberry.types import ExecutionContext
from strawberry.types.scalar import ScalarDefinition
from strawberry.types.scalar import ScalarWrapper
from strawberry.utils.await_maybe import AsyncIteratorOrIterator
from structlog import get_logger

from mora import config
from mora.db import get_session
from mora.exceptions import HTTPException
from mora.graphapi.middleware import StarletteContextExtension
from mora.graphapi.router import CustomGraphQLRouter
from mora.log import canonical_gql_context

logger = get_logger()


def add_exception_extension(error: GraphQLError) -> StrawberryGraphQLError:
    extensions = {}
    if isinstance(error.original_error, HTTPException):
        extensions["error_context"] = jsonable_encoder(error.original_error.detail)
        # Log errors like http_exception_handler in backend/mora/app.py
        settings = config.get_settings()
        if not settings.is_production():
            logger.info(
                "http_exception",
                stack=error.original_error.stack,
                traceback=error.original_error.traceback,
            )

    return StrawberryGraphQLError(
        extensions=extensions,
        nodes=error.nodes,
        source=error.source,
        positions=error.positions,
        path=error.path,
        original_error=error.original_error,
        message=error.message,
    )


class LogContextExtension(SchemaExtension):
    async def on_operation(self) -> AsyncIterator[None]:
        if self.execution_context.operation_name:
            canonical_gql_context()["name"] = self.execution_context.operation_name
        if self.execution_context.variables:
            canonical_gql_context()["vars"] = self.execution_context.variables
        yield
        if self.execution_context.errors:
            canonical_gql_context()["errors"] = self.execution_context.errors
            canonical_gql_context()["query"] = self.execution_context.query


class ExtendedErrorFormatExtension(SchemaExtension):
    async def on_operation(self) -> AsyncIterator[None]:
        yield
        result = self.execution_context.result
        if result and hasattr(result, "errors") and result.errors is not None:
            result.errors = list(map(add_exception_extension, result.errors))


class RollbackOnError(SchemaExtension):
    async def on_operation(self) -> AsyncIterator[None]:
        yield
        result = self.execution_context.result
        if result and hasattr(result, "errors") and result.errors is not None:
            await get_session().rollback()


class IntrospectionQueryCacheExtension(SchemaExtension):
    cache: dict[tuple[Schema, str | None], ExecutionResult | None] = {}

    def on_execute(self) -> AsyncIteratorOrIterator[None]:  # type: ignore
        """Cache GraphQL introspection query, which otherwise takes 5-10s to execute.

        Based on the "In memory cached execution" example from
        https://strawberry.rocks/docs/guides/custom-extensions.
        """
        execution_context = self.execution_context
        cache_key = (execution_context.schema, execution_context.query)
        if (
            execution_context.operation_name == "IntrospectionQuery"
            and not execution_context.variables
        ):
            with suppress(KeyError):
                execution_context.result = self.cache[cache_key]
        yield
        self.cache.setdefault(cache_key, execution_context.result)


class CustomSchema(Schema):
    def process_errors(
        self,
        errors: list[GraphQLError],
        execution_context: None | ExecutionContext = None,
    ) -> None:
        exceptions = [
            "".join(traceback.format_exception(error.original_error))
            for error in errors
        ]
        canonical_gql_context()["exceptions"] = exceptions
        if not config.get_settings().is_production():
            # Pretty-print exceptions in development
            for exception in exceptions:
                print(exception, end="")


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
        LogContextExtension,
        RollbackOnError,
        ExtendedErrorFormatExtension,
        IntrospectionQueryCacheExtension,
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

    scalar_overrides: dict[object, ScalarWrapper | ScalarDefinition | type] | None = (
        None
    )

    @classmethod
    @cache
    def get(cls) -> CustomSchema:
        """Instantiate Strawberry Schema."""
        return CustomSchema(
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
        return {
            "version": cls.version,
        }

    @classmethod
    def get_router(cls, is_latest: bool) -> APIRouter:
        """Get Strawberry FastAPI router serving this GraphQL API version."""
        router = CustomGraphQLRouter(
            graphql_ide="graphiql",  # TODO: pathfinder seems a lot nicer
            is_latest=is_latest,
            schema=cls.schema.get(),
            context_getter=cls.get_context,
        )

        @router.get("/schema.graphql", response_class=PlainTextResponse)
        async def schema() -> str:
            """Return the GraphQL version's schema definition in SDL format."""
            header = dedent(
                f"""\
                # SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
                # SPDX-License-Identifier: MPL-2.0
                #
                # OS2mo GraphQL API schema definition (v{cls.version}).
                # https://os2mo.eksempel.dk/graphql/v{cls.version}/schema.graphql

                """
            )
            return header + print_schema(cls.schema.get())

        return router
