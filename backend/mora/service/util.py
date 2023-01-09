# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import json
from operator import itemgetter
from typing import Any

from more_itertools import one

from mora import exceptions
from mora.graphapi.shim import execute_graphql
from mora.graphapi.shim import ExecutionResult


def handle_gql_error(response: ExecutionResult) -> None:
    """Handle and reraise GraphQL errors.

    Args:
        response (ExecutionResult): The GraphQL response to extract errors from.

    Raises:
        error.original_error: The original error, if any.
        ValueError: If no original error is present.
    """
    if response.errors:
        error = one(response.errors)
        if error.original_error:
            raise error.original_error
        raise ValueError(error)


async def get_configuration() -> dict[str, Any]:
    """Read global configuration settings.

    Returns:
        A dictionary of settings.
    """
    query = """
    query ConfiguationQuery {
      configuration {
        key
        jsonified_value
      }
    }
    """
    response = await execute_graphql(query)
    handle_gql_error(response)
    configurations = response.data["configuration"]
    if not configurations:
        exceptions.ErrorCodes.E_UNKNOWN()
    keys = map(
        lambda key: key.removeprefix("confdb_"), map(itemgetter("key"), configurations)
    )
    values = map(json.loads, map(itemgetter("jsonified_value"), configurations))
    return dict(zip(keys, values))
