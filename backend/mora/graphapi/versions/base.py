# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from collections.abc import Iterable
from collections.abc import Sequence
from functools import cache
from textwrap import dedent

from fastapi import APIRouter
from starlette.responses import PlainTextResponse
from strawberry.extensions import SchemaExtension
from strawberry.printer import print_schema
from strawberry.schema.config import StrawberryConfig
from strawberry.types.scalar import ScalarDefinition
from strawberry.types.scalar import ScalarWrapper

from mora.graphapi.custom_router import CustomGraphQLRouter
from mora.graphapi.custom_schema import CustomSchema
from mora.graphapi.middleware import StarletteContextExtension
from mora.graphapi.router import get_context
from mora.graphapi.schema import ExtendedErrorFormatExtension
from mora.graphapi.schema import IntrospectionQueryCacheExtension
from mora.graphapi.schema import LogContextExtension
from mora.graphapi.schema import RollbackOnError


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
    def get_router(cls) -> APIRouter:
        """Get Strawberry FastAPI router serving this GraphQL API version."""
        router = CustomGraphQLRouter(
            graphql_ide="graphiql",  # TODO: pathfinder seems a lot nicer
            schema=cls.schema.get(),
            context_getter=get_context,
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
