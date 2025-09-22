# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0

import re
import traceback
from collections.abc import AsyncIterator
from typing import Any
from typing import cast

from graphql import GraphQLError
from starlette.requests import Request
from starlette_context import context
from starlette_context import request_cycle_context
from strawberry import Schema
from strawberry.schema import BaseSchema
from strawberry.types import ExecutionContext
from strawberry.types.base import StrawberryObjectDefinition
from strawberry.types.field import StrawberryField

from mora import config
from mora.graphapi.fields import Metadata
from mora.graphapi.version import Version
from mora.log import canonical_gql_context


class CustomSchema(Schema):
    def __init__(self, version: Version, *args: Any, **kwargs: Any) -> None:
        self.version = version
        super().__init__(*args, **kwargs)

    def get_fields(
        self, type_definition: StrawberryObjectDefinition
    ) -> list[StrawberryField]:
        """Filter fields based on GraphQL version.

        https://strawberry.rocks/docs/types/schema
        """

        def is_in_version(field: StrawberryField) -> bool:
            metadata = cast(Metadata, field.metadata)
            if "version" not in metadata:
                return True
            return metadata["version"](self.version)

        return [field for field in type_definition.fields if is_in_version(field)]

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


def get_version(schema: BaseSchema) -> Version:
    """Get Schema version."""
    # Strawberry is not generic in its schema, so callers will have a
    # strawberry.Schema or strawberry.BaseSchema type.
    assert isinstance(schema, CustomSchema)
    return schema.version


_GRAPHQL_VERSION_MIDDLEWARE_KEY = "graphql_version"


async def graphql_version_context(request: Request) -> AsyncIterator[None]:
    """Application dependency to create the `graphql_version` context variable."""
    graphql_match = re.match(r"/graphql/v(\d+)", request.url.path)
    if graphql_match is None:
        version = None
    else:
        version = Version(int(graphql_match.group(1)))

    data = {**context, _GRAPHQL_VERSION_MIDDLEWARE_KEY: version}
    with request_cycle_context(data):
        yield


def get_graphql_version() -> Version | None:
    """Get Schema version, but indirectly through the context.

    Please, let's stop passing things around the stack. Use get_version(schema)
    if you are able -- it also has better typing. This one is useful for deep
    in LoRa/RequestHandler code 🥲👍
    """
    return context[_GRAPHQL_VERSION_MIDDLEWARE_KEY]
