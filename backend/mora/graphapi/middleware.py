#!/usr/bin/env python3
# --------------------------------------------------------------------------------------
# SPDX-FileCopyrightText: 2021 - 2022 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
# --------------------------------------------------------------------------------------
"""Starlette plugins to create context variables that can be used in the service app."""
# --------------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------------
from typing import Any
from typing import Optional
from typing import Union

from starlette.requests import HTTPConnection
from starlette.requests import Request
from starlette_context import context
from starlette_context.plugins import Plugin
from strawberry.extensions import Extension

# --------------------------------------------------------------------------------------
# Middleware
# --------------------------------------------------------------------------------------


class GraphQLContextPlugin(Plugin):
    """Starlette Plugin to create the `is_graphql` context variable.

    The variable is used to control the details level for various entities deep within
    the application without having to pass a details level variable throughout the
    entire callstack.

    The variable is `False` by default as to keep everything unaffected by default,
    and is only switched to `True` when a GraphQL query is being executed. This changed
    is trigger by the Starberry GraphQL extension: StarletteContextExtension.

    After all reading code is implemented using GraphQL / shimming this plugin and the
    corresponding extension can be eliminated.
    """

    key = "is_graphql"

    async def process_request(
        self, request: Union[Request, HTTPConnection]
    ) -> Optional[Any]:
        return False


class StarletteContextExtension(Extension):
    def on_request_start(self) -> None:
        context["is_graphql"] = True


def is_graphql() -> bool:
    """Determine if we are currently evaluating a GraphQL query."""
    return context.get("is_graphql", False)


class GraphQLIsShimPlugin(Plugin):
    """Starlette Plugin to create the `is_graphql_shim` context variable.

    The variable is used to toggle GraphQL authentication within the
    GraphQL shim.

    The variable is `False` by default as to keep everything unaffected by default,
    and is only switched to `True` when query is being executed via the GraphQL
    shim.

    After all reading code is implemented using GraphQL / shimming this plugin and the
    corresponding extension can be eliminated.
    """

    key = "is_graphql_shim"

    async def process_request(
        self, request: Union[Request, HTTPConnection]
    ) -> Optional[Any]:
        return False


def set_is_shim() -> None:
    context["is_graphql_shim"] = True


def is_graphql_shim() -> bool:
    """Determine if we are currently in the GraphQL shim.

    Returns:
        bool: True if GraphQL shim. False if not.
    """
    return context.get("is_graphql_shim", False)


class GraphQLArgsPlugin(Plugin):
    """Starlette plugin to create the `graphql_args` context variable.

    The variable is used to store `from_date` and `to_date` and send them
    to the LoRa connector.

    It sucks, and I apologise. We do it like this because we cannot write
    to the internal Strawberry context and fetch it again at a meaningful step
    in the execution.
    """

    key: str = "graphql_args"

    async def process_request(
        self, request: Union[Request, HTTPConnection]
    ) -> Optional[Any]:
        return dict()


def set_graphql_args(args_dict: dict[str, Any]) -> None:
    """Set GraphQL args directly in the Starlette context."""
    context["graphql_args"] = args_dict


def get_graphql_args() -> dict[str, Any]:
    return context.get("graphql_args", dict())
