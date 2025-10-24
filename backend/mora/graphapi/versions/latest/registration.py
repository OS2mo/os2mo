# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from datetime import datetime
from textwrap import dedent
from typing import TypeVar
from uuid import UUID

import strawberry

from .actor import Actor
from .actor import actor_uuid_to_actor

MOObject = TypeVar("MOObject")


@strawberry.type(
    description=dedent(
        """\
    Bitemporal container.

    Mostly useful for auditing purposes seeing when data-changes were made and by whom.

    Note:
    Will eventually contain a full temporal axis per bitemporal container.

    **Warning**:
    This entry should **not** be used to implement event-driven integrations.
    Such integration should rather utilize the AMQP-based event-system.
    """
    )
)
class Registration:
    registration_id: int = strawberry.field(
        description=dedent(
            """\
        Internal registration ID for the registration.
        """
        ),
        deprecation_reason=dedent(
            """\
            May be removed in the future once the bitemporal scheme is finished.
            """
        ),
    )

    start: datetime = strawberry.field(
        description=dedent(
            """\
        Start of the bitemporal interval.

        Examples:
        * `"1970-01-01T00:00:00.000000+00:00"`
        * `"2019-12-18T12:55:15.348614+00:00"`
        """
        )
    )
    end: datetime | None = strawberry.field(
        description=dedent(
            """\
        End of the bitemporal interval.

        `null` indicates the open interval, aka. infinity.

        Examples:
        * `"1970-01-01T00:00:00.000000+00:00"`
        * `"2019-12-18T12:55:15.348614+00:00"`
        * `null`
        """
        )
    )

    actor: UUID = strawberry.field(
        description=dedent(
            """\
        UUID of the actor (integration or user) who changed the data.

        Note:
        Currently mostly returns `"42c432e8-9c4a-11e6-9f62-873cf34a735f"`.
        Will eventually contain for the UUID of the integration or user who mutated data, based on the JWT token.
        """
        )
    )

    @strawberry.field(
        description=dedent(
            """\
            Object for the actor (integration or user) who changed the data.
            """
        )
    )
    async def actor_object(self, root: "Registration", info: strawberry.Info) -> Actor:
        return await actor_uuid_to_actor(root.actor, info=info)

    # Name of the entity model
    model: str = strawberry.field(
        description=dedent(
            """\
        Model of the modified entity.

        Examples:
        * `"class"`
        * `"employee"`
        * `"org_unit"`
        """
        )
    )

    # UUID of the modified entity
    uuid: UUID = strawberry.field(
        description=dedent(
            """\
        UUID of the modified entity.
        """
        )
    )

    note: str | None = strawberry.field(
        description="Note associated with the registration."
    )
