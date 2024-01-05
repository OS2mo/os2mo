# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from textwrap import dedent
from typing import Annotated
from typing import TypeVar
from uuid import UUID

import strawberry
from strawberry.types import Info

from ..latest.filters import gen_filter_table
from ..latest.filters import RegistrationFilter
from ..latest.registration import Registration
from ..latest.registration import registration_resolver
from .resolvers import CursorType
from .resolvers import FromDateFilterType
from .resolvers import LimitType
from .resolvers import PagedResolver
from .resolvers import ToDateFilterType
from .resolvers import UUIDsFilterType

MOObject = TypeVar("MOObject")


ActorUUIDsFilterType = Annotated[
    list[UUID] | None,
    strawberry.argument(
        description=dedent(
            """\
        Filter registrations by their changing actor.

        Can be used to select all changes made by a particular user or integration.
        """
        )
        + gen_filter_table("actors")
    ),
]
ModelFilterType = Annotated[
    list[str] | None,
    strawberry.argument(
        description=dedent(
            """\
        Filter registrations by their model type.

        Can be used to select all changes of a type.
        """
        )
        + gen_filter_table("models")
    ),
]


class RegistrationResolver(PagedResolver):
    # TODO: Implement using a dataloader
    async def resolve(  # type: ignore[override]
        self,
        info: Info,
        limit: LimitType = None,
        cursor: CursorType = None,
        uuids: UUIDsFilterType = None,
        actors: ActorUUIDsFilterType = None,
        models: ModelFilterType = None,
        start: FromDateFilterType = None,
        end: ToDateFilterType = None,
    ) -> list[Registration]:
        filter = RegistrationFilter(
            uuids=uuids,
            actors=actors,
            models=models,
            start=start,
            end=end,
        )
        return await registration_resolver(
            info=info,
            filter=filter,
            limit=limit,
            cursor=cursor,
        )
