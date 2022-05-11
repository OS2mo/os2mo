#!/usr/bin/env python3
# --------------------------------------------------------------------------------------
# SPDX-FileCopyrightText: 2021 - 2022 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
# --------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------------
from more_itertools import one

from mora.graphapi.shim import ExecutionResult

# --------------------------------------------------------------------------------------
# Code
# --------------------------------------------------------------------------------------


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
