# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Middleware for authentification."""

from collections.abc import AsyncIterator
from collections.abc import Awaitable
from collections.abc import Callable
from uuid import UUID

from fastapi import Depends
from fastapi import Request
from sqlalchemy.dialects.postgresql import insert
from starlette_context import context
from starlette_context import request_cycle_context

from mora import depends
from mora.auth.keycloak.models import Token
from mora.auth.keycloak.oidc import token_getter
from mora.db import Actor
from mora.db import AsyncSessionWithLock
from mora.log import canonical_log_context

# This magical UUID was introduced into LoRas source code back in
# December of 2015, it is kept here for backwards compatibility, but should
# be eliminated in the future, by ensuring that Keycloak UUIDs are always set.
# For more information, see the commit messsage of the change introducing this.
LORA_USER_UUID = UUID("05211100-baad-1110-006e-6f2075756964")

# These magical UUIDs were introduced in July of 2025 to distinguish between three
# different situations in which the LORA_USER_UUID would be returned, namely whenever
# a token was unparsable, when a token was missing an UUID, and when the auth middleware
# was not run, but get_authenticated_user was called anyway.
# Introducing these three new UUIDs allows us to distinguish which situation has occured
# and should allow us to easier pinpoint auth issues in the future and ensure a richer
# audit / registration log.
UNABLE_TO_PARSE_TOKEN_UUID = UUID("bad070c1-baad-1110-006e-6f7061727365")
MISSING_UUID_ON_TOKEN_UUID = UUID("face1e55-baad-1110-006d-697373696e67")
NO_AUTH_MIDDLEWARE_UUID = UUID("5ec0fa11-baad-1110-006d-696477617265")


_MIDDLEWARE_KEY = "authenticated_user"


def _is_testing_snapshot_or_restore(request: Request) -> bool:
    return request.url.path.startswith("/testing")


def _is_unit_testing_with_fake_db(session: AsyncSessionWithLock) -> bool:
    return session.under_testing_with_fake_db


def _should_save_actor(
    uuid: UUID | None, name: str | None, request: Request, session: AsyncSessionWithLock
) -> bool:
    return (
        uuid is not None
        and name is not None
        and not _is_testing_snapshot_or_restore(request)
        and not _is_unit_testing_with_fake_db(session)
    )


async def set_authenticated_user(
    request: Request,
    session: depends.Session,
    get_token: Callable[[], Awaitable[Token]] = Depends(token_getter),
) -> AsyncIterator[None]:
    # TODO: refactor this auth method
    # https://redmine.magenta.dk/issues/67592
    try:
        token = await get_token()
        uuid = token.uuid
        name = token.preferred_username
        if _should_save_actor(uuid, name, request, session):
            await session.execute(
                insert(Actor)
                .values(actor=uuid, name=name)
                .on_conflict_do_update(index_elements=["actor"], set_={"name": name})
            )
    except Exception:
        uuid = UNABLE_TO_PARSE_TOKEN_UUID
        name = "Unable to parse token"
    if uuid is None:
        uuid = MISSING_UUID_ON_TOKEN_UUID
        name = "UUID missing on token"

    canonical_log_context()["actor"] = {"uuid": str(uuid), "name": name}

    data = {**context, _MIDDLEWARE_KEY: uuid}
    with request_cycle_context(data):
        yield


def get_authenticated_user() -> UUID:
    """Return UUID of the authenticated user."""
    return context.get(_MIDDLEWARE_KEY) or NO_AUTH_MIDDLEWARE_UUID
