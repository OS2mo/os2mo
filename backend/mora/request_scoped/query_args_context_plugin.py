# SPDX-FileCopyrightText: 2021- Magenta ApS
# SPDX-License-Identifier: MPL-2.0

from starlette.requests import HTTPConnection, Request
from starlette_context.plugins import Plugin
from typing import Any, Optional, Union


class QueryArgContextPlugin(Plugin):
    key = "query_args"

    async def process_request(
        self, request: Union[Request, HTTPConnection]
    ) -> Optional[Any]:
        return request.query_params
