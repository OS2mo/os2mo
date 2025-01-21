# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from uuid import UUID

import strawberry
from more_itertools import only
from sqlalchemy import select
from strawberry.types import Info

from mora.auth.keycloak.oidc import LEGACY_AUTH_UUID
from mora.auth.keycloak.oidc import NO_AUTH_UUID
from mora.auth.middleware import LORA_USER_UUID
from mora.db import Actor as ActorTable
from mora.graphapi.gmodels.mo.employee import EmployeeRead

from .filters import EmployeeFilter
from .resolvers import employee_resolver
from .response import Response
from .schema import Employee

BEFORE_ACTOR_UUID = UUID("42c432e8-9c4a-11e6-9f62-873cf34a735f")


async def database_actor_resolver(actor_uuid: UUID, info: Info) -> str | None:
    """Translate an actor_uuid to a name via the actor table."""
    query = select(ActorTable.name).where(ActorTable.actor == actor_uuid)
    session = info.context["session"]
    return await session.scalar(query)


@strawberry.interface
class Actor:
    uuid: UUID


@strawberry.type
class IntegrationActor(Actor):
    name: str


@strawberry.type
class PersonActor(Actor):
    @strawberry.field
    async def person(self, root: "PersonActor") -> Response[Employee]:
        return Response[EmployeeRead](uuid=root.uuid)  # type: ignore

    @strawberry.field
    async def username(self, root: "PersonActor", info: Info) -> str | None:
        return await database_actor_resolver(root.uuid, info=info)


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
        return PersonActor(uuid=actor_uuid)

    # Check if the UUID is an known integration
    result = await database_actor_resolver(actor_uuid, info)
    if result:
        return IntegrationActor(uuid=actor_uuid, name=result)

    # Fail to translate, let the user know
    return SpecialActor(uuid=actor_uuid, details="The actor could not be translated")
