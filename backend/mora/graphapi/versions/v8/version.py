# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import strawberry
from fastapi.encoders import jsonable_encoder
from strawberry.types import Info

from ..latest.inputs import OrganisationUnitTerminateInput
from ..latest.mutators import uuid2response
from ..latest.permissions import gen_terminate_permission
from ..latest.permissions import IsAuthenticatedPermission
from ..latest.schema import OrganisationUnit
from ..latest.schema import Response
from ..v9.version import GraphQLVersion as NextGraphQLVersion
from mora.graphapi.shim import execute_graphql  # type: ignore[attr-defined]
from ramodels.mo.organisation_unit import OrganisationUnitRead


@strawberry.type
class Mutation(NextGraphQLVersion.schema.mutation):  # type: ignore[name-defined]
    @strawberry.mutation(
        description="Terminates an organization unit.",
        permission_classes=[
            IsAuthenticatedPermission,
            gen_terminate_permission("org_unit"),
        ],
    )
    async def org_unit_terminate(
        self, info: Info, unit: OrganisationUnitTerminateInput
    ) -> Response[OrganisationUnit]:
        input = unit
        input_dict = jsonable_encoder(input.to_pydantic().dict(by_alias=True))  # type: ignore
        input_dict = {k: v for k, v in input_dict.items() if v}
        response = await execute_graphql(
            """
            mutation OrgUnitTerminate($input: OrganisationUnitTerminateInput!){
                org_unit_terminate(input: $input) {
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
        uuid = response.data["org_unit_terminate"]["uuid"]
        return uuid2response(uuid, OrganisationUnitRead)


class GraphQLSchema(NextGraphQLVersion.schema):  # type: ignore
    """Version 8 of the GraphQL Schema.

    Version 9 introduced a breaking change to the org_unit_terminate mutator, which
    changes the name of its input from `unit` to `input` to align with other mutators.
    Version 8 ensures that the old functionality is still available.
    """

    mutation = Mutation


class GraphQLVersion(NextGraphQLVersion):
    """GraphQL Version 8."""

    version = 8
    schema = GraphQLSchema
