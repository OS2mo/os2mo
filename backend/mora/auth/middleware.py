# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Middleware for authentification."""

from collections.abc import AsyncIterator
from collections.abc import Awaitable
from collections.abc import Callable
from uuid import UUID

from fastapi import Depends
from sqlalchemy.dialects.postgresql import insert
from starlette_context import context
from starlette_context import request_cycle_context

from mora import depends
from mora.auth.keycloak.models import Token
from mora.auth.keycloak.oidc import token_getter
from mora.db import Actor
from mora.log import canonical_log_context

# This magical UUID was introduced into LoRas source code back in
# December of 2015, it is kept here for backwards compatibility, but should
# be eliminated in the future, by ensuring that Keycloak UUIDs are always set.
# For more information, see the commit messsage of the change introducing this.
LORA_USER_UUID = UUID("05211100-baad-1110-006e-6F2075756964")


_MIDDLEWARE_KEY = "authenticated_user"


async def fetch_authenticated_user(
    session: depends.Session,
    get_token: Callable[[], Awaitable[Token]] = Depends(token_getter),
) -> UUID | None:
    try:
        token = await get_token()
        canonical_log_context()["actor"] = {
            "uuid": str(token.uuid),
            "name": token.preferred_username,
        }
    except Exception:
        return None

    # Ensure the actor is known and saved
    await session.execute(
        insert(Actor)
        .values(actor=token.uuid, name=token.preferred_username)
        .on_conflict_do_nothing()
    )

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
