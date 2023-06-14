# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from uuid import UUID

import strawberry
from fastapi.encoders import jsonable_encoder
from pydantic import Field

from ..latest.permissions import gen_create_permission
from ..latest.permissions import IsAuthenticatedPermission
from ..latest.types import UUIDReturn
from ..v6.version import GraphQLVersion as NextGraphQLVersion
from mora.common import get_connector
from ramodels.lora.facet import Facet as LoraFacet
from ramodels.mo._shared import UUIDBase


class FacetCreate(UUIDBase):
    """Model representing a facet creation/update."""

    """Inherets uuid from UUIDBase"""

    user_key: str = Field(description="Facet name.")
    type_: str = Field(
        "facet", alias="type", description="The object type"
    )  # type is always "facet"

    org_uuid: UUID = Field(description="UUID of the related organisation.")
    parent_uuid: UUID | None = Field(description="UUID of the parent facet.")
    published: str | None = Field(description="Published state of the facet object.")


@strawberry.experimental.pydantic.input(
    model=FacetCreate,
    all_fields=True,
)
class FacetCreateInput:
    """Input model for creating a facet."""


async def create_facet(input: FacetCreate) -> UUID:
    input_dict = input.dict(by_alias=True)

    lora_facet = LoraFacet.from_simplified_fields(
        user_key=input_dict["user_key"],
        organisation_uuid=input_dict["org_uuid"],
        uuid=input_dict["uuid"],
    )

    jsonified = jsonable_encoder(
        obj=lora_facet, by_alias=True, exclude={"uuid"}, exclude_none=True
    )

    c = get_connector(virkningfra="-infinity", virkningtil="infinity")
    uuid = await c.facet.create(jsonified, input_dict["uuid"])

    return UUID(uuid)


@strawberry.type
class Mutation(NextGraphQLVersion.schema.mutation):  # type: ignore[name-defined]
    # Classes
    # -------
    @strawberry.mutation(
        description="Creates a facet.",
        permission_classes=[
            IsAuthenticatedPermission,
            gen_create_permission("facet"),
        ],
    )
    async def facet_create(self, input: FacetCreateInput) -> UUIDReturn:
        return UUIDReturn(uuid=await create_facet(input.to_pydantic()))  # type: ignore[call-arg]


class GraphQLSchema(NextGraphQLVersion.schema):  # type: ignore
    """Version 5 of the GraphQL Schema.

    Version 6 introduced a breaking change to the `facet_create` mutator.
    Version 5 ensures that the old functionality is still available.
    """

    mutation = Mutation


class GraphQLVersion(NextGraphQLVersion):
    """GraphQL Version 5."""

    version = 5
    schema = GraphQLSchema
