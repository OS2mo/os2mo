# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from typing import Any
from uuid import UUID

import strawberry
from pydantic import BaseModel
from pydantic import Extra
from pydantic import Field
from strawberry.types import Info

from ..latest.models import FacetRead
from ..latest.mutators import uuid2response
from ..latest.permissions import gen_create_permission
from ..latest.permissions import gen_update_permission
from ..latest.permissions import IsAuthenticatedPermission
from ..latest.schema import Facet
from ..latest.schema import Response
from ..v16.version import GraphQLVersion as NextGraphQLVersion
from mora.graphapi.shim import execute_graphql  # type: ignore


class FacetCreateV15(BaseModel):
    """Model representing a facet creation."""

    class Config:
        frozen = True
        extra = Extra.forbid

    user_key: str = Field(description="Facet name.")
    published: str = Field(
        "Publiceret", description="Published state of the facet object."
    )

    def to_latest_dict(self) -> dict[str, Any]:
        return {
            "user_key": self.user_key,
            "published": self.published,
            "validity": {"from": None, "to": None},
        }


class FacetUpdateV15(FacetCreateV15):
    """Model representing a facet update."""

    uuid: UUID = Field(description="UUID of the facet to update.")

    def to_latest_dict(self) -> dict[str, Any]:
        latest_dict = super().to_latest_dict()
        return {"uuid": str(self.uuid), **latest_dict}


@strawberry.experimental.pydantic.input(
    model=FacetCreateV15,
    all_fields=True,
)
class FacetCreateInput:
    """Input model for creating facets."""


@strawberry.experimental.pydantic.input(
    model=FacetUpdateV15,
    all_fields=True,
)
class FacetUpdateInput:
    """Input model for updating facets."""


@strawberry.type
class Mutation(NextGraphQLVersion.schema.mutation):  # type: ignore[name-defined]
    # Facets
    # ------
    @strawberry.mutation(
        description="Creates a facet.",
        permission_classes=[
            IsAuthenticatedPermission,
            gen_create_permission("facet"),
        ],
    )
    async def facet_create(
        self, info: Info, input: FacetCreateInput
    ) -> Response[Facet]:
        input_dict = input.to_pydantic().to_latest_dict()
        response = await execute_graphql(
            """
            mutation FacetCreate($input: FacetCreateInput!){
                facet_create(input: $input) {
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
        uuid = response.data["facet_create"]["uuid"]
        return uuid2response(uuid, FacetRead)

    @strawberry.mutation(
        description="Updates a facet.",
        permission_classes=[
            IsAuthenticatedPermission,
            gen_update_permission("facet"),
        ],
    )
    async def facet_update(
        self, info: Info, input: FacetUpdateInput
    ) -> Response[Facet]:
        input_dict = input.to_pydantic().to_latest_dict()
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
            variable_values={"input": input_dict},
        )
        if response.errors:
            for error in response.errors:
                raise ValueError(error.message)
        uuid = response.data["facet_update"]["uuid"]
        return uuid2response(uuid, FacetRead)


class GraphQLSchema(NextGraphQLVersion.schema):  # type: ignore
    """Version 15 of the GraphQL Schema.

    Version 16 introduced a breaking change to the `facet_create` and
    `facet_update` mutators requiring a `validity` argument to be provided.
    Version 15 ensures that the old functionality is still available.
    """

    mutation = Mutation


class GraphQLVersion(NextGraphQLVersion):
    """GraphQL Version 15."""

    version = 15
    schema = GraphQLSchema
