#!/usr/bin/env python3
# --------------------------------------------------------------------------------------
# SPDX-FileCopyrightText: 2021 - 2022 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
# --------------------------------------------------------------------------------------
"""GraphQL executer with the necessary context variables.

Used for shimming the service API.
"""
# --------------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------------
from typing import Any

from strawberry.types import ExecutionResult

# --------------------------------------------------------------------------------------
# Code
# --------------------------------------------------------------------------------------


async def execute_graphql(*args: Any, **kwargs: Any) -> ExecutionResult:
    from mora.graphapi.main import get_schema
    from mora.graphapi.dataloaders import get_loaders
    from mora.graphapi.middleware import set_is_shim

    set_is_shim()

    loaders = await get_loaders()
    if "context_value" not in kwargs:
        kwargs["context_value"] = loaders

    return await get_schema().execute(*args, **kwargs)
