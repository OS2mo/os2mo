# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0

from more_itertools import one
from strawberry.exceptions import StrawberryGraphQLError

from mora.graphapi.shim import ExecutionResult


def handle_gql_error(response: ExecutionResult) -> None:
    """Handle and reraise GraphQL errors.

    Args:
        response (ExecutionResult): The GraphQL response to extract errors from.

    Raises:
        error.original_error: The original error, if any.
        ValueError: If no original error is present.
    """

    def to_exception(error: StrawberryGraphQLError) -> Exception:
        if error.original_error:
            return error.original_error
        return error

    if response.errors:
        exceptions = list(map(to_exception, response.errors))
        if len(exceptions) == 1:
            raise one(exceptions)
        raise ExceptionGroup("GraphQL Errors", exceptions)  # noqa: F821
