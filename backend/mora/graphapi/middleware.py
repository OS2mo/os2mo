# SPDX-FileCopyrightText: 2021- Magenta ApS
# SPDX-License-Identifier: MPL-2.0
from typing import Any
from typing import Optional
from typing import Union

from starlette.requests import HTTPConnection
from starlette.requests import Request
from starlette_context.plugins import Plugin
from starlette_context import context
from strawberry.extensions import Extension


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
    def on_request_start(self):
        context["is_graphql"] = True


def is_graphql() -> bool:
    """Determine if we are currently evaluating a GraphQL query."""
    return context.get("is_graphql", False)
