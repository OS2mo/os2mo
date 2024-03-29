# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from uuid import UUID

import strawberry
from strawberry.types import Info

from ..latest.permissions import gen_update_permission
from ..latest.permissions import IsAuthenticatedPermission
from ..v10.version import GraphQLVersion as NextGraphQLVersion
from ..v13.schema import Class
from ..v13.schema import Facet
from ..v13.schema import ITSystem
from ..v13.schema import Response
from ..v14.version import ITSystemCreateInput
from ..v15.version import FacetUpdateInput
from ..v16.version import ClassUpdateInput


@strawberry.type
class Mutation(NextGraphQLVersion.schema.mutation):  # type: ignore[name-defined]
    @strawberry.mutation(
        description="Updates a class.",
        permission_classes=[
            IsAuthenticatedPermission,
            gen_update_permission("class"),
        ],
    )
    async def class_update(
        self, info: Info, uuid: UUID, input: ClassUpdateInput
    ) -> Response[Class]:
        input.uuid = uuid  # type: ignore
        return await NextGraphQLVersion.schema.mutation.class_update(
            self=self, info=info, input=input
        )

    @strawberry.mutation(
        description="Updates a facet.",
        permission_classes=[
            IsAuthenticatedPermission,
            gen_update_permission("facet"),
        ],
    )
    async def facet_update(
        self, info: Info, input: FacetUpdateInput, uuid: UUID
    ) -> Response[Facet]:
        input.uuid = uuid  # type: ignore
        return await NextGraphQLVersion.schema.mutation.facet_update(
            self=self, info=info, input=input
        )

    @strawberry.mutation(
        description="Updates an ITSystem.",
        permission_classes=[
            IsAuthenticatedPermission,
            gen_update_permission("itsystem"),
        ],
    )
    async def itsystem_update(
        self, info: Info, input: ITSystemCreateInput, uuid: UUID
    ) -> Response[ITSystem]:
        input.uuid = uuid  # type: ignore
        return await NextGraphQLVersion.schema.mutation.itsystem_update(
            self=self, info=info, input=input
        )


class GraphQLSchema(NextGraphQLVersion.schema):  # type: ignore
    """Version 9 of the GraphQL Schema.

    Version 10 introduced a breaking change to the itsystem, facet and class mutators,
    which removes their uuid argument to align with other mutators.
    Version 9 ensures that the old functionality is still available.
    """

    mutation = Mutation


class GraphQLVersion(NextGraphQLVersion):
    """GraphQL Version 9."""

    version = 9
    schema = GraphQLSchema
