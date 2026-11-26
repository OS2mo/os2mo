# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Middleware for authentification."""

from collections.abc import AsyncIterator
from collections.abc import Awaitable
from collections.abc import Callable
from uuid import UUID

from fastapi import Depends
from fastapi import Request
from sqlalchemy import select
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
NO_AUTH_MIDDLEWARE_UUID = UUID("5ec0fa11-baad-1110-006d-696477617265")


_MIDDLEWARE_KEY = "authenticated_user"


def _is_testing_snapshot_or_restore(request: Request) -> bool:
    return request.url.path.startswith("/testing")


def _is_unit_testing_with_fake_db(session: AsyncSessionWithLock) -> bool:
    return session.under_testing_with_fake_db


def _should_save_actor(request: Request, session: AsyncSessionWithLock) -> bool:
    return not (
        _is_testing_snapshot_or_restore(request)
        or _is_unit_testing_with_fake_db(session)
    )


async def _save_actor(session: AsyncSessionWithLock, token: Token) -> UUID:
    """Keep the actor table ajour with the actor making the request.

    Actors are identified by their username.

    Returns:
        The UUID of the actor.
    """
    # It's very common for an actor (integration) to make a lot of requests
    # simultaneously. Writing to the actor's row, even if nothing changed,
    # locks it until the request's transaction ends, making the requests "queue
    # up", eventually exhausting the connection pool. Reading doesn't take any
    # locks, so we only write if the table isn't already up to date.
    actor = await session.scalar(
        select(Actor).where(Actor.username == token.preferred_username)
    )
    if actor is not None:
        return actor.uuid

    result = await session.execute(
        insert(Actor)
        .values(username=token.preferred_username)
        .on_conflict_do_update(
            index_elements=["username"],
            set_={"username": token.preferred_username},
        )
        .returning(Actor.uuid)
    )
    return result.scalar_one()


async def set_authenticated_user(
    request: Request,
    session: depends.Session,
    get_token: Callable[[], Awaitable[Token]] = Depends(token_getter),
) -> AsyncIterator[None]:
    # TODO: refactor this auth method
    # https://redmine.magenta.dk/issues/67592
    actor: UUID | None = None
    try:
        token = await get_token()
    except Exception:
        actor = UNABLE_TO_PARSE_TOKEN_UUID
        name = "Unable to parse token"
    else:
        name = token.preferred_username
        if _should_save_actor(request, session):
            actor = await _save_actor(session, token)

    canonical_log_context()["actor"] = {"uuid": str(actor), "name": name}

    data = {**context, _MIDDLEWARE_KEY: actor}
    with request_cycle_context(data):
        yield


def get_authenticated_user() -> UUID:
    """Return the UUID of the authenticated actor."""
    return context.get(_MIDDLEWARE_KEY) or NO_AUTH_MIDDLEWARE_UUID
