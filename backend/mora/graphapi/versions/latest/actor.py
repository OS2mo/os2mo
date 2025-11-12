# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from contextlib import suppress
from enum import Enum
from functools import partial
from textwrap import dedent
from uuid import UUID

import strawberry
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from strawberry.dataloader import DataLoader
from strawberry.types import Info

from mora.auth.keycloak.models import Token
from mora.auth.keycloak.oidc import LEGACY_AUTH_UUID
from mora.auth.keycloak.oidc import NO_AUTH_UUID
from mora.auth.middleware import LORA_USER_UUID
from mora.auth.middleware import MISSING_UUID_ON_TOKEN_UUID
from mora.auth.middleware import NO_AUTH_MIDDLEWARE_UUID
from mora.auth.middleware import UNABLE_TO_PARSE_TOKEN_UUID
from mora.db import Actor as ActorTable

from .events import Listener
from .events import Namespace
from .events import listener_resolver
from .events import namespace_resolver
from .permissions import IsAuthenticatedPermission
from .permissions import gen_read_permission
from .seed_resolver import seed_resolver

BEFORE_ACTOR_UUID = UUID("42c432e8-9c4a-11e6-9f62-873cf34a735f")
ACTOR_NAME_LOADER_KEY = "actor_name_loader"


@strawberry.enum
class HardcodedActor(Enum):
    NO_AUTH = strawberry.enum_value(
        NO_AUTH_UUID,
        description="The change was made when auth was disabled",
    )
    LEGACY_AUTH = strawberry.enum_value(
        LEGACY_AUTH_UUID,
        description="The change was made through the legacy auth system",
    )
    BEFORE_ACTOR = strawberry.enum_value(
        BEFORE_ACTOR_UUID,
        description="The change was made before actors were registered",
    )
    LORA_USER = strawberry.enum_value(
        LORA_USER_UUID,
        description=dedent("""\
            The change was made by an unknown actor.

            This could either by due to:

            * an invalid or unparsable token
            * a token missing an UUID
            * by-passing the authentication middleware

            or similar.
        """),
        deprecation_reason=dedent("""\
            Deprecated as of version 43.4.0 in favor of:

            * UNABLE_TO_PARSE_TOKEN: for invalid or unparsable tokens
            * MISSING_UUID_ON_TOKEN: for tokens missing an UUID
            * NO_AUTH_MIDDLEWARE_UUID: for by-passing the authentication middleware
        """),
    )
    UNABLE_TO_PARSE_TOKEN = strawberry.enum_value(
        UNABLE_TO_PARSE_TOKEN_UUID,
        description="The change was made by an invalid or unparsable token",
    )
    MISSING_UUID_ON_TOKEN = strawberry.enum_value(
        MISSING_UUID_ON_TOKEN_UUID,
        description="The change was made by a token missing an UUID",
    )
    NO_AUTH_MIDDLEWARE = strawberry.enum_value(
        NO_AUTH_MIDDLEWARE_UUID,
        description="The change was made by-passing the authentication middleware",
    )


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
    query = select(ActorTable).where(ActorTable.actor.in_(keys))
    rows = (await session.scalars(query)).all()
    results = {r.actor: r.name for r in rows}
    return [results.get(id) for id in keys]


def get_actor_loaders(session: AsyncSession) -> dict[str, DataLoader]:
    return {
        ACTOR_NAME_LOADER_KEY: DataLoader(load_fn=partial(actor_name_resolver, session))
    }


@strawberry.interface(
    description=dedent(
        """\
    Interface type for all actors, implementing all shared behavior.
    """
    )
)
class Actor:
    uuid: UUID = strawberry.field(description="UUID of the actor")

    @strawberry.field(
        description="Appropriate display text for any actor (regardless of type)"
    )
    async def display_name(self, root: "Actor", info: Info) -> str | None:
        loader: DataLoader = info.context[ACTOR_NAME_LOADER_KEY]
        return await loader.load(root.uuid)

    event_namespaces: list[Namespace] = strawberry.field(
        resolver=seed_resolver(
            namespace_resolver, {"owners": lambda root: [root.uuid]}
        ),
        description="Get event namespaces owned by this actor.",
        permission_classes=[
            IsAuthenticatedPermission,
            gen_read_permission("event_namespace"),
        ],
    )

    event_listeners: list[Listener] = strawberry.field(
        resolver=seed_resolver(listener_resolver, {"owners": lambda root: [root.uuid]}),
        description="Get event listeners owned by this actor.",
        permission_classes=[
            IsAuthenticatedPermission,
            gen_read_permission("event_listener"),
        ],
    )


@strawberry.type(
    description=dedent(
        """\
    The SpecialActor type is used for special magic-number UUIDs.

    It is returned, if a change was made;
    * While auth was disabled.
    * Using the legacy auth system.
    * Before registrations got actors registered.
    or similar
    """
    )
)
class SpecialActor(Actor):
    @strawberry.field(description="Enum key for the specific case of the special actor")
    async def key(self, root: "SpecialActor") -> HardcodedActor:
        return HardcodedActor(root.uuid)


@strawberry.type(
    description=dedent(
        """\
    The UnknownActor type is a fallback actor type for when lookup fails.

    It is returned when all attempts at actor translations have failed.
    """
    )
)
class UnknownActor(Actor):
    error: str = strawberry.field(description="Descriptive error message")


def actor_uuid_to_actor(actor_uuid: UUID | None) -> Actor:
    """Translate an actor UUID to its corresponding Actor object.

    Args:
        actor_uuid: UUID of the actor to lookup.

    Returns:
        An Actor subclass specific to the type of actor_uuid provided.
    """
    # Special case for missing actors, should ideally never happen
    if actor_uuid is None:
        return UnknownActor(  # pragma: no cover
            uuid=UUID("ffffffff-ffff-ffff-ffff-ffffffffffff"),
            error="No token provided.",
        )

    # Check if the UUID is one of our magic UUIDs
    # TODO: Use `actor_uuid in HardcodedActor:` in Python3.12+
    with suppress(ValueError):
        # Attempt to construct the HardcodedActor with our UUID
        # This fails with a ValueError if the actor_uuid is not in our enum.
        HardcodedActor(actor_uuid)
        return SpecialActor(uuid=actor_uuid)

    # TODO: Add PersonActor type and resolve it here
    #       Be sure to check whether the user has permission to resolve people
    # TODO: Add IntegrationActor type and resolve it here
    #       Be sure to check whether the user has permission to resolve integrations

    # Fail to translate, let the user know
    return UnknownActor(
        uuid=actor_uuid,
        error=dedent(
            """\
            The actor could not be translated.

            Note: Person actor translation has not been implemented yet.
            Note: Integration actor translation has not been implemented yet.
            """
        ),
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


async def myself_resolver(info: Info) -> Myself:
    token: Token = await info.context["get_token"]()
    return Myself(
        actor=actor_uuid_to_actor(token.uuid),
        email=token.email,
        username=token.preferred_username,
        roles=sorted(token.realm_access.roles),
    )
