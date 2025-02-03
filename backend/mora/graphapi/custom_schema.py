# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import traceback

from graphql import GraphQLError
from strawberry import Schema
from strawberry.types import ExecutionContext

from mora import config
from mora.log import canonical_gql_context


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
