# SPDX-FileCopyrightText: 2021- Magenta ApS
# SPDX-License-Identifier: MPL-2.0
from typing import Any
from typing import Optional
from typing import Union

from starlette.requests import HTTPConnection
from starlette.requests import Request
from starlette_context.plugins import Plugin


class QueryArgContextPlugin(Plugin):
    key = "query_args"

    async def process_request(
        self, request: Union[Request, HTTPConnection]
    ) -> Optional[Any]:
        return request.query_params
