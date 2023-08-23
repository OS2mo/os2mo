# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import strawberry

from ..latest.address import terminate_addr
from ..latest.inputs import AddressTerminateInput
from ..latest.mutators import uuid2response
from ..latest.permissions import gen_terminate_permission
from ..latest.permissions import IsAuthenticatedPermission
from ..latest.schema import Address
from ..latest.schema import Response
from ..v8.version import GraphQLVersion as NextGraphQLVersion
from ramodels.mo.details import AddressRead


@strawberry.type
class Mutation(NextGraphQLVersion.schema.mutation):  # type: ignore[name-defined]
    # Addresses
    # -------
    @strawberry.mutation(
        description="Terminates an address.",
        permission_classes=[
            IsAuthenticatedPermission,
            gen_terminate_permission("address"),
        ],
    )
    async def address_terminate(self, at: AddressTerminateInput) -> Response[Address]:
        return uuid2response(await terminate_addr(at.to_pydantic()), AddressRead)


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
