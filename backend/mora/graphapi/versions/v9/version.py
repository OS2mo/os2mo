# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from uuid import UUID

import strawberry
from fastapi.encoders import jsonable_encoder
from strawberry.types import Info

from ..latest.classes import ClassUpdateInput
from ..latest.facets import FacetUpdateInput
from ..latest.itsystem import ITSystemCreateInput
from ..latest.mutators import uuid2response
from ..latest.permissions import gen_update_permission
from ..latest.permissions import IsAuthenticatedPermission
from ..latest.schema import Class
from ..latest.schema import Facet
from ..latest.schema import ITSystem
from ..latest.schema import Response
from ..v10.version import GraphQLVersion as NextGraphQLVersion
from mora.graphapi.shim import execute_graphql  # type: ignore[attr-defined]
from ramodels.mo import ClassRead
from ramodels.mo import FacetRead
from ramodels.mo.details import ITSystemRead


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
            variable_values={"input": jsonable_encoder(input)},
        )
        uuid = response.data["class_update"]["uuid"]
        return uuid2response(uuid, ClassRead)

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

        response = await execute_graphql(
            """
            mutation FacetUpdate($input: FacetUpdateInput!){
                facet_update(input: $input) {
                    uuid
                }
            }
            """,
            graphql_version=NextGraphQLVersion,
            context_value=info.context,
            variable_values={"input": jsonable_encoder(input)},
        )
        uuid = response.data["facet_update"]["uuid"]
        return uuid2response(uuid, FacetRead)

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

        response = await execute_graphql(
            """
            mutation ItSystemUpdate($input: ITSystemCreateInput!){
                itsystem_update(input: $input) {
                    uuid
                }
            }
            """,
            graphql_version=NextGraphQLVersion,
            context_value=info.context,
            variable_values={"input": jsonable_encoder(input)},
        )
        uuid = response.data["itsystem_update"]["uuid"]
        return uuid2response(uuid, ITSystemRead)


class GraphQLSchema(NextGraphQLVersion.schema):  # type: ignore
    """Version 9 of the GraphQL Schema.

    Version 10 introduced a breaking change to the org_unit_terminate mutator, which
    changes the name of its input from `unit` to `input` to align with other mutators.
    Version 9 ensures that the old functionality is still available.
    """

    mutation = Mutation


class GraphQLVersion(NextGraphQLVersion):
    """GraphQL Version 9."""

    version = 9
    schema = GraphQLSchema
