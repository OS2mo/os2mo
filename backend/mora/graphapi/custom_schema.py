# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import traceback
from typing import Any

from graphql import GraphQLError
from strawberry import Schema
from strawberry.schema import BaseSchema
from strawberry.types import ExecutionContext

from mora import config
from mora.graphapi.version import Version
from mora.log import canonical_gql_context


class CustomSchema(Schema):
    def __init__(self, version: Version, *args: Any, **kwargs: Any) -> None:
        self.version = version
        super().__init__(*args, **kwargs)

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
