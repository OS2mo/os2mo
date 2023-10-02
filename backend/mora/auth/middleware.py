# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Middleware for authentification."""
from collections.abc import AsyncIterator
from collections.abc import Awaitable
from collections.abc import Callable
from uuid import UUID

from fastapi import Depends
from fastapi import Request
from starlette_context import context
from starlette_context import request_cycle_context

from mora.auth.keycloak.models import Token
from mora.auth.keycloak.oidc import token_getter

# This magical UUID was introduced into LoRas source code back in
# December of 2015, it is kept here for backwards compatibility, but should
# be eliminated in the future, by ensuring that Keycloak UUIDs are always set.
# For more information, see the commit messsage of the change introducing this.
LORA_USER_UUID = UUID("05211100-baad-1110-006e-6F2075756964")


_AUTHENTICATED_USER_MIDDLEWARE_KEY = "authenticated_user"
_AUTHENTICATED_USER_HEADER = "X-Authenticated-User"



async def fetch_authenticated_user(
    get_token: Callable[[], Awaitable[Token]] = Depends(token_getter)
) -> UUID | None:
    try:
        token = await get_token()
    except Exception:
        return None
    return token.uuid


async def set_authenticated_user(
    user_uuid: UUID | None = Depends(fetch_authenticated_user),
) -> AsyncIterator[None]:
    data = {**context, _AUTHENTICATED_USER_MIDDLEWARE_KEY: user_uuid}
    with request_cycle_context(data):
        yield


async def set_authenticated_user_from_header(request: Request) -> AsyncIterator[None]:
    user_uuid = request.headers.get(_AUTHENTICATED_USER_HEADER)
    data = {**context}
    if user_uuid:
        data[_AUTHENTICATED_USER_MIDDLEWARE_KEY] = UUID(user_uuid)
    with request_cycle_context(data):
        yield


def get_authenticated_user() -> UUID:
    """Return UUID of the authenticated user."""
    return context.get(_AUTHENTICATED_USER_MIDDLEWARE_KEY) or LORA_USER_UUID
