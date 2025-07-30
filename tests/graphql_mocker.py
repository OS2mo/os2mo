# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Respx helpers for mocking GraphQL endpoints."""

import json
from contextlib import suppress
from typing import Any

from fastapi.encoders import jsonable_encoder
from httpx import Response
from respx import MockRouter
from respx import Route

from mo_ldap_import_export.main import GRAPHQL_VERSION


class GraphQLRoute(Route):
    @property
    def result(self):
        return self.return_value.json()["data"]

    @result.setter
    def result(self, value) -> None:
        # TODO: Support errors
        self.return_value = Response(200, json={"data": jsonable_encoder(value)})

    @property
    def request_json(self) -> list[dict[str, Any]]:
        return [json.loads(x.request.content) for x in self.calls]

    @property
    def request_query(self) -> list[dict[str, Any]]:
        return [x["query"] for x in self.request_json]

    @property
    def request_variables(self) -> list[dict[str, Any]]:
        return [x["variables"] for x in self.request_json]


class GraphQLMocker:
    def __init__(self, respx_mock: MockRouter) -> None:
        self.respx_mock = respx_mock

    def query(
        self,
        query_name: str,
        *,
        name: str | None = None,
        **lookups: Any,
    ) -> GraphQLRoute:
        # TODO: Match more strictly on query name
        url = f"/graphql/v{GRAPHQL_VERSION}"
        route = GraphQLRoute(
            method="POST", url=url, content__contains=query_name, **lookups
        )
        self.respx_mock.add(route, name=name)
        # Attempt to move the FastRAMQPI MO passthrough mock behind our new mock
        # This is necessary as respx simply uses the first match it finds and our
        # route above is added to the back of the queue.
        with suppress(KeyError):
            self.respx_mock.add(self.respx_mock.pop(name="mo"), name="mo")
        return route
