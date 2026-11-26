# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Middleware for authentification."""

from uuid import UUID

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from starlette_context import context

from mora import depends
from mora.auth.keycloak.models import Token
from mora.auth.keycloak.oidc import fetch_token
from mora.db import Actor
from mora.db import AsyncSessionWithLock
from mora.log import canonical_log_context

_MIDDLEWARE_KEY = "authenticated_user"


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


async def set_authenticated_user(session: AsyncSessionWithLock, token: Token) -> None:
    """Record the actor making the request as the author of its changes."""
    actor = await _save_actor(session, token)
    canonical_log_context()["actor"] = {
        "uuid": str(actor),
        "name": token.preferred_username,
    }
    context[_MIDDLEWARE_KEY] = actor


async def authenticate(
    session: depends.Session, token: Token = Depends(fetch_token)
) -> None:
    """FastAPI dependency for routers where every request must be authenticated."""
    await set_authenticated_user(session, token)


def get_authenticated_user() -> UUID:
    """Return the UUID of the authenticated actor."""
    return context[_MIDDLEWARE_KEY]
