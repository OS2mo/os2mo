# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from functools import partial
from uuid import UUID

import strawberry
from more_itertools import only
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from strawberry.dataloader import DataLoader
from strawberry.types import Info
from strawberry import Private

from mora.auth.keycloak.oidc import LEGACY_AUTH_UUID
from mora.auth.keycloak.oidc import NO_AUTH_UUID
from mora.auth.middleware import LORA_USER_UUID
from mora.db import Actor as ActorTable
from mora.graphapi.gmodels.mo.employee import EmployeeRead

from .filters import EmployeeFilter, ITUserFilter
from .resolvers import employee_resolver, it_user_resolver
from .response import Response
from .schema import Employee

BEFORE_ACTOR_UUID = UUID("42c432e8-9c4a-11e6-9f62-873cf34a735f")
ACTOR_NAME_LOADER_KEY = "actor_name_loader"


async def database_load_actor_names(
    session: AsyncSession, keys: list[UUID]
) -> list[str | None]:
    """Load Actors from database.

    Args:
        session: The database session to execute our query on.
        keys: list of actor_uuids to lookup.

    Returns:
        List of actor names found via the lookup, None if an actor could not be found.
    """
    query = select(ActorTable).where(ActorTable.actor.in_(keys))
    rows = (await session.scalars(query)).all()
    results = {r.actor: r for r in rows}
    return [results.get(id) for id in keys]


def get_actor_loaders(session: AsyncSession) -> dict[str, DataLoader]:
    return {
        ACTOR_NAME_LOADER_KEY: DataLoader(
            load_fn=partial(database_load_actor_names, session)
        )
    }


@strawberry.interface
class Actor:
    uuid: UUID


@strawberry.type
class IntegrationActor(Actor):
    name: str


@strawberry.type
class PersonActor(Actor):
    person_uuid: Private[UUID]

    @strawberry.field
    async def person(self, root: "PersonActor") -> Response[Employee]:
        return Response[EmployeeRead](uuid=root.person_uuid)  # type: ignore

    @strawberry.field
    async def username(self, root: "PersonActor", info: Info) -> str | None:
        loader: DataLoader = info.context[ACTOR_NAME_LOADER_KEY]
        return await loader.load(root.uuid)


@strawberry.type
class SpecialActor(Actor):
    details: str


async def actor_uuid_to_actor(actor_uuid: UUID, info: Info) -> Actor:
    well_known_uuids = {
        LORA_USER_UUID: "The change was made by an unknown actor",
        NO_AUTH_UUID: "The change was made when auth was disabled",
        LEGACY_AUTH_UUID: "The change was made through the legacy auth system",
        BEFORE_ACTOR_UUID: "The change was made before actors were registered",
    }
    # Check if the UUID is one of our magic UUIDs
    if actor_uuid in well_known_uuids:
        return SpecialActor(uuid=actor_uuid, details=well_known_uuids[actor_uuid])

    # Check if the UUID is an employee
    result = only(
        await employee_resolver(info=info, filter=EmployeeFilter(uuids=[actor_uuid]))
    )
    if result:
        return PersonActor(uuid=actor_uuid, person_uuid=actor_uuid)

    # Check if the UUID is an it-user
    # TODO: Is value stored in uuid or external_id?
    # TODO: What if there are multiple matches?
    # TODO: What if person is not set on the IT-account?
    result = only(
        await it_user_resolver(info=info, filter=ITUserFilter(uuids=[actor_uuid]))
    )
    if result:
        return PersonActor(uuid=actor_uuid, person_uuid=result.employee_uuid)

    # Check if the UUID is an known integration
    loader: DataLoader = info.context[ACTOR_NAME_LOADER_KEY]
    result = await loader.load(actor_uuid)
    if result:
        return IntegrationActor(uuid=actor_uuid, name=result)

    # Fail to translate, let the user know
    return SpecialActor(uuid=actor_uuid, details="The actor could not be translated")
