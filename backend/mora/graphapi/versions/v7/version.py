# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import strawberry
from fastapi.encoders import jsonable_encoder
from strawberry.types import Info

from ..latest.inputs import AddressTerminateInput
from ..latest.mutators import uuid2response
from ..latest.permissions import gen_terminate_permission
from ..latest.permissions import IsAuthenticatedPermission
from ..latest.schema import Address
from ..latest.schema import Response
from ..v8.version import GraphQLVersion as NextGraphQLVersion
from mora.graphapi.shim import execute_graphql  # type: ignore[attr-defined]
from ramodels.mo.details import AddressRead


@strawberry.type
class Mutation(NextGraphQLVersion.schema.mutation):  # type: ignore[name-defined]
    @strawberry.mutation(
        description="Terminates an address.",
        permission_classes=[
            IsAuthenticatedPermission,
            gen_terminate_permission("address"),
        ],
    )
    async def address_terminate(
        self, info: Info, at: AddressTerminateInput
    ) -> Response[Address]:
        input = at
        input_dict = jsonable_encoder(input.to_pydantic().dict(by_alias=True))  # type: ignore
        input_dict = {k: v for k, v in input_dict.items() if v}
        response = await execute_graphql(
            """
            mutation AddressTerminate($input: AddressTerminateInput!){
                address_terminate(input: $input) {
                    uuid
                }
            }
            """,
            graphql_version=NextGraphQLVersion,
            context_value=info.context,
            variable_values={"input": input_dict},
        )
        uuid = response.data["address_terminate"]["uuid"]
        if response.errors:
            for error in response.errors:
                raise ValueError(error.message)
        return uuid2response(uuid, AddressRead)


class GraphQLSchema(NextGraphQLVersion.schema):  # type: ignore
    """Version 7 of the GraphQL Schema.

    Version 8 introduced a breaking change to the address_terminate mutator, which
    changes the name of its input from `at` to `input` to align with other mutators.
    Version 7 ensures that the old functionality is still available.
    """

    mutation = Mutation


class GraphQLVersion(NextGraphQLVersion):
    """GraphQL Version 7."""

    version = 7
    schema = GraphQLSchema
