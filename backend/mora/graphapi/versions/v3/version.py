# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from uuid import UUID

import strawberry
from pydantic import Field

from ..latest.mutators import admin_permission_class
from ..latest.mutators import Mutation as LatestMutation
from ..latest.permissions import IsAuthenticatedPermission
from ..latest.types import UUIDReturn
from ..v4.version import GraphQLSchema4
from ..v4.version import GraphQLVersion4
from mora import mapping
from mora.service.facet import ClassRequestHandler
from ramodels.mo._shared import UUIDBase


class ClassCreate(UUIDBase):
    """A MO Class create object."""

    type_: str = Field(
        "class", alias="type", description="The object type"
    )  # type is always "class"
    name: str = Field(description="Mo-class name.")
    user_key: str = Field(description="Extra info or uuid")
    org_uuid: UUID = Field(description="UUID of the related organisation.")
    facet_uuid: UUID = Field(description="UUID of the related facet.")

    scope: str | None = Field(description="Scope of the class.")
    published: str | None = Field(description="Published state of the class object.")
    parent_uuid: UUID | None = Field(description="UUID of the parent class.")
    example: str | None = Field(description="Example usage.")
    owner: UUID | None = Field(description="Owner of class")


@strawberry.experimental.pydantic.input(
    model=ClassCreate,
    all_fields=True,
)
class ClassCreateInput:
    """Input model for creating a mo-class."""


async def create_class(input: ClassCreate) -> UUID:
    req_dict = {"facet": str(input.facet_uuid), "class_model": input}

    handler = await ClassRequestHandler.construct(req_dict, mapping.RequestType.CREATE)
    uuid = await handler.submit()
    return UUID(uuid)


@strawberry.type
class Mutation(LatestMutation):
    # Classes
    # -------
    @strawberry.mutation(
        description="Creates a class.",
        permission_classes=[IsAuthenticatedPermission, admin_permission_class],
    )
    async def class_create(self, input: ClassCreateInput) -> UUIDReturn:
        return UUIDReturn(uuid=await create_class(input.to_pydantic()))


class GraphQLSchema3(GraphQLSchema4):
    """Latest GraphQL Schema, exposed as a version.

    When adding breaking changes, modify this schema to maintain compatibility for the
    version.
    """

    mutation = Mutation


class GraphQLVersion3(GraphQLVersion4):
    """Latest GraphQL version."""

    version = 3
    schema = GraphQLSchema3
