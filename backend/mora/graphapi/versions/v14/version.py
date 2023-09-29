# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from datetime import datetime
from typing import Any

import strawberry
from pydantic import Extra
from pydantic import Field
from pydantic import parse_obj_as
from strawberry.types import Info

from ..latest.inputs import ITSystemCreateInput as LatestITSystemCreateInput
from ..latest.inputs import ITSystemUpdateInput as LatestITSystemUpdateInput
from ..latest.models import ITSystemCreate as LatestITSystemCreate
from ..latest.models import ITSystemUpdate as LatestITSystemUpdate
from ..latest.permissions import gen_create_permission
from ..latest.permissions import gen_read_permission
from ..latest.permissions import gen_update_permission
from ..latest.permissions import IsAuthenticatedPermission
from ..latest.query import to_paged_response
from ..latest.resolvers import Resolver
from ..latest.schema import ITSystem
from ..latest.schema import Paged
from ..latest.schema import Response
from ..v15.version import GraphQLVersion as NextGraphQLVersion
from ramodels.mo._shared import UUIDBase
from ramodels.mo.details import ITSystemRead


class ITSystemCreateV14(UUIDBase):
    """Model representing an itsystem creation."""

    class Config:
        frozen = True
        allow_population_by_field_name = True
        extra = Extra.forbid

    user_key: str
    name: str
    from_date: datetime | None = Field(
        None, alias="from", description="Start date of the validity."
    )
    to_date: datetime | None = Field(
        None, alias="to", description="End date of the validity, if applicable."
    )

    def to_new_create_input(self) -> LatestITSystemCreateInput:
        return LatestITSystemCreateInput.from_pydantic(
            parse_obj_as(LatestITSystemCreate, self.to_latest_dict())
        )

    def to_new_update_input(self) -> LatestITSystemUpdateInput:
        return LatestITSystemUpdateInput.from_pydantic(
            parse_obj_as(LatestITSystemUpdate, self.to_latest_dict())
        )

    def to_latest_dict(self) -> dict[str, Any]:
        return {
            "uuid": str(self.uuid),
            "user_key": self.user_key,
            "name": self.name,
            "validity": {
                "from": self.from_date.isoformat() if self.from_date else None,
                "to": self.to_date.isoformat() if self.to_date else None,
            },
        }


@strawberry.experimental.pydantic.input(
    model=ITSystemCreateV14,
    all_fields=True,
)
class ITSystemCreateInput:
    """input model for creating ITSystems."""


class ITSystemResolver(Resolver):
    def __init__(self) -> None:
        super().__init__(ITSystemRead)


@strawberry.type(description="Entrypoint for all read-operations")
class Query(NextGraphQLVersion.schema.query):  # type: ignore[name-defined]
    # ITSystems
    # ---------
    itsystems: Paged[Response[ITSystem]] = strawberry.field(
        resolver=to_paged_response(ITSystemResolver()),
        description="Get it-systems.",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("itsystem")],
    )


@strawberry.type
class Mutation(NextGraphQLVersion.schema.mutation):  # type: ignore[name-defined]
    # ITSystems
    # ---------
    @strawberry.mutation(
        description="Creates an ITSystem.",
        permission_classes=[
            IsAuthenticatedPermission,
            gen_create_permission("itsystem"),
        ],
    )
    async def itsystem_create(
        self, info: Info, input: ITSystemCreateInput
    ) -> Response[ITSystem]:
        new_input = input.to_pydantic().to_new_create_input()
        return await NextGraphQLVersion.schema.mutation.itsystem_create(
            self=self, info=info, input=new_input
        )

    @strawberry.mutation(
        description="Updates an ITSystem.",
        permission_classes=[
            IsAuthenticatedPermission,
            gen_update_permission("itsystem"),
        ],
    )
    async def itsystem_update(
        self, info: Info, input: ITSystemCreateInput
    ) -> Response[ITSystem]:
        new_input = input.to_pydantic().to_new_update_input()
        return await NextGraphQLVersion.schema.mutation.itsystem_update(
            self=self, info=info, input=new_input
        )


class GraphQLSchema(NextGraphQLVersion.schema):  # type: ignore
    """Version 14 of the GraphQL Schema.

    Version 15 introduced a breaking change to the `itsystem_update` input type and
    to the `itsystems` query input filter type, additionally both the `itsystem_create`
    and `itsystem_update` not require a `validity` argument to be provided.
    Version 14 ensures that the old functionality is still available.
    """

    query = Query
    mutation = Mutation


class GraphQLVersion(NextGraphQLVersion):
    """GraphQL Version 14."""

    version = 14
    schema = GraphQLSchema
