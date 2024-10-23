# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Respx helpers for mocking GraphQL endpoints."""

from typing import Any

from fastapi.encoders import jsonable_encoder
from httpx import Response
from respx import Route
from respx.types import URLPatternTypes


class GraphQLRoute(Route):
    @property
    def result(self):
        return self.return_value.json()["data"]

    @result.setter
    def result(self, value) -> None:
        # TODO: Support errors
        self.return_value = Response(200, json={"data": jsonable_encoder(value)})


class GraphQLMocker:
    def __init__(self, respx_mock: Any) -> None:
        self.respx_mock = respx_mock

    def query(
        self,
        query_name: str,
        url: URLPatternTypes | None = None,
        *,
        name: str | None = None,
        **lookups: Any,
    ) -> GraphQLRoute:
        # TODO: Match more strictly on query name
        route = GraphQLRoute(
            method="POST", url=url, content__contains=query_name, **lookups
        )
        self.respx_mock.add(route, name=name)
        return route
