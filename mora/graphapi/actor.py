# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from functools import partial
from uuid import UUID

import strawberry
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from strawberry.dataloader import DataLoader

from mora.access_log import access_log
from mora.auth.middleware import get_authenticated_user
from mora.db import Actor as ActorTable
from mora.graphapi.context import MOInfo
from mora.graphapi.filters import gen_filter_string

from .events import Listener
from .events import Namespace
from .events import listener_resolver
from .events import namespace_resolver
from .paged import CursorType
from .paged import LimitType
from .paged import ObjectsAndCursor
from .paged import paginate
from .paged import to_objects
from .seed_resolver import seed_resolver

ACTOR_NAME_LOADER_KEY = "actor_name_loader"


async def actor_name_resolver(
    session: AsyncSession, keys: list[UUID]
) -> list[str | None]:
    """Load actor names from database.

    Args:
        session: The database session to execute our query on.
        keys: list of actor_uuids to lookup.

    Returns:
        List of actor names found via the lookup.
    """
    query = select(ActorTable).where(ActorTable.uuid.in_(keys))
    rows = (await session.scalars(query)).all()
    results = {r.uuid: r.username for r in rows}
    return [results.get(id) for id in keys]


def get_actor_loaders(session: AsyncSession) -> dict[str, DataLoader]:
    return {
        ACTOR_NAME_LOADER_KEY: DataLoader(load_fn=partial(actor_name_resolver, session))
    }


@strawberry.type(
    description="A user or integration that reads and changes data in OS2mo."
)
class Actor:
    uuid: UUID = strawberry.field(description="UUID of the actor")

    @strawberry.field(description="Username of the actor")
    async def username(self, root: "Actor", info: MOInfo) -> str | None:
        loader: DataLoader = info.context.dataloaders.actor_name_loader
        return await loader.load(root.uuid)

    @strawberry.field(
        description="Appropriate display text for the actor",
        deprecation_reason="Use 'username' instead. Will be removed in a future version of OS2mo.",
    )
    async def display_name(self, root: "Actor", info: MOInfo) -> str | None:
        return await self.username(root, info)

    event_namespaces: list[Namespace] = strawberry.field(
        resolver=to_objects(
            seed_resolver(namespace_resolver, {"owners": lambda root: [root.uuid]})
        ),
        description="Get event namespaces owned by this actor.",
    )

    event_listeners: list[Listener] = strawberry.field(
        resolver=to_objects(
            seed_resolver(listener_resolver, {"owners": lambda root: [root.uuid]})
        ),
        description="Get event listeners owned by this actor.",
    )


@strawberry.input(description="Actor filter.")
class ActorFilter:
    uuids: list[UUID] | None = strawberry.field(
        default=None, description=gen_filter_string("UUID", "uuids")
    )


async def actor_resolver(
    info: MOInfo,
    filter: ActorFilter | None = None,
    limit: LimitType = None,
    cursor: CursorType = None,
) -> ObjectsAndCursor:
    """Resolve actors from the actor data-source.

    The actor table is kept ajour as actors (users and integrations) interact
    with OS2mo, and is the same data-source backing the `actor` / `actor_object`
    fields exposed on access log entries and registrations.
    """
    if filter is None:
        filter = ActorFilter()

    session: AsyncSession = info.context.session

    query = select(ActorTable.uuid)
    if filter.uuids is not None:
        query = query.where(ActorTable.uuid.in_(filter.uuids))
    query = query.order_by(ActorTable.uuid)

    uuids, next_cursor = await paginate(session, query, ActorTable.uuid, limit, cursor)

    access_log(
        session,
        info.context.settings,
        "resolve_actors",
        "Actor",
        {
            "limit": limit,
            "cursor": cursor,
            "uuids": filter.uuids,
        },
        list(uuids),
    )

    return ObjectsAndCursor(
        objects=[Actor(uuid=uuid) for uuid in uuids],
        next_cursor=next_cursor,
    )


@strawberry.type(description="Information about the API client itself")
class Myself:
    actor: Actor = strawberry.field(description="The API client as an actor object")
    email: str | None = strawberry.field(description="Contact email for the API client")
    username: str | None = strawberry.field(
        description="Preferred username for the API client"
    )
    roles: list[str] = strawberry.field(
        description="Set of RBAC roles assigned to the client"
    )


def myself_resolver(info: MOInfo) -> Myself:
    token = info.context.token
    return Myself(
        actor=Actor(uuid=get_authenticated_user()),
        email=token.email,
        username=token.preferred_username,
        roles=sorted(token.realm_access.roles),
    )
