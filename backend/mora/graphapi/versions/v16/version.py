# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from typing import Any
from uuid import UUID

import strawberry
from pydantic import Extra
from pydantic import Field
from strawberry.types import Info

from ..latest.models import ClassRead
from ..latest.models import UUIDBase
from ..latest.mutators import uuid2response
from ..latest.permissions import gen_create_permission
from ..latest.permissions import gen_update_permission
from ..latest.permissions import IsAuthenticatedPermission
from ..latest.response import Response
from ..latest.schema import Class
from ..v17.version import GraphQLVersion as NextGraphQLVersion
from mora.graphapi.shim import execute_graphql  # type: ignore


class ClassCreateV16(UUIDBase):
    """Model representing a Class creation."""

    class Config:
        frozen = True
        extra = Extra.forbid

    name: str = Field(description="Class name")
    user_key: str = Field(description="Extra info or uuid")
    facet_uuid: UUID = Field(description="UUID of the related facet.")
    published: str = Field(
        "Publiceret", description="Published state of the class object"
    )

    scope: str | None = Field(description="Scope of the class.")
    parent_uuid: UUID | None = Field(description="UUID of the parent class.")
    example: str | None = Field(description="Example usage.")
    owner: UUID | None = Field(description="Owner of class")

    def to_latest_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "user_key": self.user_key,
            "facet_uuid": str(self.facet_uuid),
            "published": self.published,
            "scope": self.scope,
            "parent_uuid": str(self.parent_uuid) if self.parent_uuid else None,
            "example": self.example,
            "owner": str(self.owner) if self.owner else None,
            "validity": {"from": None, "to": None},
        }


class ClassUpdateV16(ClassCreateV16):
    """Model representing a class update."""

    uuid: UUID = Field(description="UUID of the class to update.")

    def to_latest_dict(self) -> dict[str, Any]:
        latest_dict = super().to_latest_dict()
        return {"uuid": str(self.uuid), **latest_dict}


@strawberry.experimental.pydantic.input(
    model=ClassCreateV16,
    all_fields=True,
)
class ClassCreateInput:
    """Input model for creating classes."""


@strawberry.experimental.pydantic.input(
    model=ClassUpdateV16,
    all_fields=True,
)
class ClassUpdateInput:
    """Input model for updating classes."""


@strawberry.type
class Mutation(NextGraphQLVersion.schema.mutation):  # type: ignore[name-defined]
    @strawberry.mutation(
        description="Creates a class.",
        permission_classes=[
            IsAuthenticatedPermission,
            gen_create_permission("class"),
        ],
    )
    async def class_create(
        self, info: Info, input: ClassCreateInput
    ) -> Response[Class]:
        input_dict = input.to_pydantic().to_latest_dict()
        response = await execute_graphql(
            """
            mutation ClassCreate($input: ClassCreateInput!){
                class_create(input: $input) {
                    uuid
                }
            }
            """,
            graphql_version=NextGraphQLVersion,
            context_value=info.context,
            variable_values={"input": input_dict},
        )
        if response.errors:
            for error in response.errors:
                raise ValueError(error.message)
        uuid = response.data["class_create"]["uuid"]
        return uuid2response(uuid, ClassRead)

    @strawberry.mutation(
        description="Updates a class.",
        permission_classes=[
            IsAuthenticatedPermission,
            gen_update_permission("class"),
        ],
    )
    async def class_update(
        self, info: Info, input: ClassUpdateInput
    ) -> Response[Class]:
        input_dict = input.to_pydantic().to_latest_dict()
        response = await execute_graphql(
            """
            mutation ClassUpdate($input: ClassUpdateInput!){
                class_update(input: $input) {
                    uuid
                }
            }
            """,
            graphql_version=NextGraphQLVersion,
            context_value=info.context,
            variable_values={"input": input_dict},
        )
        if response.errors:
            for error in response.errors:
                raise ValueError(error.message)
        uuid = response.data["class_update"]["uuid"]
        return uuid2response(uuid, ClassRead)


class GraphQLSchema(NextGraphQLVersion.schema):  # type: ignore
    """Version 16 of the GraphQL Schema.

    Version 17 introduced a breaking change to the `class_create` and
    `class_update` mutators requiring a `validity` argument to be provided.
    Version 16 ensures that the old functionality is still available.
    """

    mutation = Mutation


class GraphQLVersion(NextGraphQLVersion):
    """GraphQL Version 16."""

    version = 16
    schema = GraphQLSchema
