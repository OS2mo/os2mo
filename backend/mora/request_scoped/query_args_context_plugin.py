# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from typing import Any

from starlette.requests import HTTPConnection
from starlette.requests import Request
from starlette_context.plugins import Plugin


class QueryArgContextPlugin(Plugin):
    key = "query_args"

    async def process_request(self, request: Request | HTTPConnection) -> Any | None:
        return request.query_params
