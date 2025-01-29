# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from collections.abc import AsyncIterator

from fastapi import Request
from mora.log import canonical_log_context
from starlette_context import context
from starlette_context import request_cycle_context

_MIDDLEWARE_KEY = "query_args"


async def query_args_context(request: Request) -> AsyncIterator[None]:
    data = {**context, _MIDDLEWARE_KEY: request.query_params}
    if request.query_params:
        canonical_log_context()[_MIDDLEWARE_KEY] = dict(request.query_params)
    canonical_log_context()["path"] = request.url.path
    canonical_log_context()["method"] = request.method
    with request_cycle_context(data):
        yield
