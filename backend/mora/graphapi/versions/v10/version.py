# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import strawberry
from pydantic import Field

from ..latest.manager import create_manager
from ..latest.models import ManagerCreate
from ..latest.mutators import uuid2response
from ..latest.permissions import gen_create_permission
from ..latest.permissions import IsAuthenticatedPermission
from ..latest.schema import Manager
from ..latest.schema import Response
from ..v11.version import GraphQLVersion as NextGraphQLVersion
from ramodels.mo.details import ManagerRead


class ManagerCreateV10(ManagerCreate):
    type_: str = Field("manager", alias="type", description="The object type.")

    def to_handler_dict(self) -> dict:
        result = super().to_handler_dict()
        result["type"] = self.type_
        return result


@strawberry.experimental.pydantic.input(
    model=ManagerCreateV10,
    all_fields=True,
)
class ManagerCreateInput:
    """Input model for creating a manager."""


@strawberry.type
class Mutation(NextGraphQLVersion.schema.mutation):  # type: ignore[name-defined]
    @strawberry.mutation(
        description="Creates a manager relation.",
        permission_classes=[
            IsAuthenticatedPermission,
            gen_create_permission("manager"),
        ],
    )
    async def manager_create(self, input: ManagerCreateInput) -> Response[Manager]:
        return uuid2response(await create_manager(input.to_pydantic()), ManagerRead)


class GraphQLSchema(NextGraphQLVersion.schema):  # type: ignore
    """Version 10 of the GraphQL Schema.

    Version 11 introduced a breaking change to the `manager_create` mutator.
    Version 10 ensures that the old functionality is still available.
    """

    mutation = Mutation


class GraphQLVersion(NextGraphQLVersion):
    """GraphQL Version 10."""

    version = 10
    schema = GraphQLSchema
