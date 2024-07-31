# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import strawberry
from pydantic.v1 import Field

from ..latest.it_user import create_ituser
from ..latest.models import ITUserCreate
from ..latest.permissions import gen_create_permission
from ..latest.permissions import IsAuthenticatedPermission
from ..v12.version import GraphQLVersion as NextGraphQLVersion  # type: ignore
from ..v13.mutators import uuid2response
from ..v13.schema import ITUser
from ..v13.schema import Response
from mora.graphapi.gmodels.mo.details import ITUserRead
from mora.graphapi.versions.latest.inputs import all_fields
from mora.graphapi.versions.latest.inputs import ValidityInput


class ITUserCreateV11(ITUserCreate):
    type_: str = Field("it", alias="type", description="The object type.")

    def to_handler_dict(self) -> dict:
        result = super().to_handler_dict()
        result["type"] = self.type_
        return result


@strawberry.experimental.pydantic.input(
    model=ITUserCreateV11, fields=list(all_fields(ITUserCreateV11) - {"validity"})
)
class ITUserCreateInput:
    """input model for creating IT-Users."""

    validity: ValidityInput


@strawberry.type
class Mutation(NextGraphQLVersion.schema.mutation):  # type: ignore[name-defined]
    @strawberry.mutation(
        description="Creates an IT-User.",
        permission_classes=[
            IsAuthenticatedPermission,
            gen_create_permission("ituser"),
        ],
    )
    async def ituser_create(self, input: ITUserCreateInput) -> Response[ITUser]:
        return uuid2response(await create_ituser(input.to_pydantic()), ITUserRead)


class GraphQLSchema(NextGraphQLVersion.schema):  # type: ignore
    """Version 11 of the GraphQL Schema.

    Version 12 introduced a breaking change to the `ituser_create` mutator.
    Version 11 ensures that the old functionality is still available.
    """

    mutation = Mutation


class GraphQLVersion(NextGraphQLVersion):
    """GraphQL Version 11."""

    version = 11
    schema = GraphQLSchema
