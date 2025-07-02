# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from textwrap import dedent
from uuid import UUID

import strawberry
from strawberry.types import Info

from mora.auth.keycloak.models import Token
from mora.auth.keycloak.oidc import LEGACY_AUTH_UUID
from mora.auth.keycloak.oidc import NO_AUTH_UUID
from mora.auth.middleware import LORA_USER_UUID

from .events import Listener
from .events import Namespace
from .events import listener_resolver
from .events import namespace_resolver
from .permissions import IsAuthenticatedPermission
from .permissions import gen_read_permission
from .seed_resolver import seed_resolver

BEFORE_ACTOR_UUID = UUID("42c432e8-9c4a-11e6-9f62-873cf34a735f")


@strawberry.interface(
    description=dedent(
        """\
    Interface type for all actors, implementing all shared behavior.
    """
    )
)
class Actor:
    uuid: UUID = strawberry.field(description="UUID of the actor")

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
    * Without being able to determine who made it.
    """
    )
)
class SpecialActor(Actor):
    details: str = strawberry.field(description="Generic text description")


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


def actor_uuid_to_actor(actor_uuid: UUID) -> Actor:
    """Translate an actor UUID to its corresponding Actor object.

    Args:
        actor_uuid: UUID of the actor to lookup.

    Returns:
        An Actor subclass specific to the type of actor_uuid provided.
    """
    well_known_uuids = {
        NO_AUTH_UUID: "The change was made when auth was disabled",
        LEGACY_AUTH_UUID: "The change was made through the legacy auth system",
        BEFORE_ACTOR_UUID: "The change was made before actors were registered",
        LORA_USER_UUID: "The change was made by an unknown actor",
    }
    # Check if the UUID is one of our magic UUIDs
    if actor_uuid in well_known_uuids:
        # TODO: Remove this no cover when using actor_uuid_to_actor in auditlog
        return SpecialActor(  # pragma: no cover
            uuid=actor_uuid, details=well_known_uuids[actor_uuid]
        )

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
    # The fallback here is identical to the one in `get_authenticated_user`
    # ensuring that we always have an actor UUID.
    uuid = token.uuid or LORA_USER_UUID
    return Myself(
        actor=actor_uuid_to_actor(uuid),
        email=token.email,
        username=token.preferred_username,
        roles=sorted(token.realm_access.roles),
    )
