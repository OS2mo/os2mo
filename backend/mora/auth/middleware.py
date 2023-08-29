# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Middleware for authentification."""
from collections.abc import AsyncIterator
from collections.abc import Awaitable
from collections.abc import Callable
from uuid import UUID

from fastapi import Depends
from fastapi import Header
from starlette_context import context
from starlette_context import request_cycle_context

from mora.auth.keycloak.models import Token
from mora.auth.keycloak.oidc import token_getter

# This magical UUID was introduced into LoRas source code back in
# December of 2015, it is kept here for backwards compatibility, but should
# be eliminated in the future, by ensuring that Keycloak UUIDs are always set.
# For more information, see the commit messsage of the change introducing this.
LORA_USER_UUID = UUID("42c432e8-9c4a-11e6-9f62-873cf34a735f")


_MIDDLEWARE_KEY = "authenticated_user"
_AUTHORIZATION_MIDDLEWARE_KEY = "authorization_header"


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
    data = {**context, _MIDDLEWARE_KEY: user_uuid}
    with request_cycle_context(data):
        yield


def get_authenticated_user() -> UUID:
    """Return UUID of the authenticated user."""
    return context.get(_MIDDLEWARE_KEY) or LORA_USER_UUID


async def set_authorization_header(
    authorization: str | None = Header(None),
) -> AsyncIterator[None]:
    data = {**context, _AUTHORIZATION_MIDDLEWARE_KEY: authorization}
    with request_cycle_context(data):
        yield


def get_authorization_header() -> str | None:
    """Return the authorization header value."""
    return context.get(_AUTHORIZATION_MIDDLEWARE_KEY)
