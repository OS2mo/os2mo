# SPDX-FileCopyrightText: 2021 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Starlette plugins to create context variables that can be used in the service app."""
from typing import Any

from starlette.requests import HTTPConnection
from starlette.requests import Request
from starlette_context import context
from starlette_context.plugins import Plugin
from strawberry.extensions import Extension

from ramodels.mo import OpenValidity


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

    async def process_request(self, request: Request | HTTPConnection) -> Any | None:
        return 0


class StarletteContextExtension(Extension):
    def on_request_start(self) -> None:
        # clear query arguments bypassing the stack
        context["query_args"] = {}
        # Store reference counter, instead of simple boolean, to ensure we do not set
        # is_graphql=False as soon as the first nested schema execution exits.
        context["is_graphql"] = context.get("is_graphql", 0) + 1

    def on_request_end(self) -> None:
        context["is_graphql"] = context.get("is_graphql", 0) - 1


def is_graphql() -> bool:
    """Determine if we are currently evaluating a GraphQL query."""
    return context.get("is_graphql", 0) > 0


class GraphQLDatesPlugin(Plugin):
    """Starlette plugin to create the `graphql_args` context variable.

    The variable is used to store `from_date` and `to_date` and send them
    to the LoRa connector.

    When we regain control of our connectors and dataloaders, this
    should be deleted immediately and with extreme prejudice.
    """

    key: str = "graphql_dates"

    async def process_request(self, request: Request | HTTPConnection) -> Any | None:
        return None


def set_graphql_dates(dates: OpenValidity) -> None:
    """Set GraphQL args directly in the Starlette context."""
    context["graphql_dates"] = dates


def get_graphql_dates() -> OpenValidity | None:
    return context.get("graphql_dates")
