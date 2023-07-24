# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from collections.abc import AsyncIterator

from fastapi import Request
from starlette_context import context
from starlette_context import request_cycle_context


_MIDDLEWARE_KEY = "query_args"


async def query_args_context(request: Request) -> AsyncIterator[None]:
    data = {**context, _MIDDLEWARE_KEY: request.query_params}
    with request_cycle_context(data):
        yield
