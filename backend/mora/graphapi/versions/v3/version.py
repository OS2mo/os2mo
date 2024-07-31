# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from uuid import UUID

import strawberry
from pydantic.v1 import Field

from ..latest.permissions import gen_create_permission
from ..latest.permissions import IsAuthenticatedPermission
from ..v4.version import GraphQLVersion as NextGraphQLVersion
from ..v5.version import UUIDReturn
from mora import mapping
from mora.graphapi.gmodels.mo._shared import UUIDBase
from mora.service.facet import ClassRequestHandler


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
class Mutation(NextGraphQLVersion.schema.mutation):  # type: ignore[name-defined]
    # Classes
    # -------
    @strawberry.mutation(
        description="Creates a class.",
        permission_classes=[
            IsAuthenticatedPermission,
            gen_create_permission("class"),
        ],
    )
    async def class_create(self, input: ClassCreateInput) -> UUIDReturn:
        return UUIDReturn(uuid=await create_class(input.to_pydantic()))  # type: ignore[call-arg]


class GraphQLSchema(NextGraphQLVersion.schema):  # type: ignore
    """Version 3 of the GraphQL Schema.

    Version 4 introduced a breaking change to the `class_create` mutator.
    Version 3 ensures that the old functionality is still available.
    """

    mutation = Mutation


class GraphQLVersion(NextGraphQLVersion):
    """GraphQL Version 3."""

    version = 3
    schema = GraphQLSchema
